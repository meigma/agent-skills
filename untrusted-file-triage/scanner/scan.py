#!/usr/bin/env python3
"""Static triage of one untrusted download.

Runs inside the scanner container: no network, read-only root, the sample at
/sample (read-only), findings to /out/scan.json. It never executes the sample.
Each finding has a severity: block (do not use), review (a human or agent must
judge), or info.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import unicodedata

SAMPLE = "/sample"
OUT = "/out/scan.json"

EXEC_EXT = {
    "exe", "dll", "scr", "com", "pif", "cpl", "sys", "msi", "msp", "msix", "appx",
    "bat", "cmd", "ps1", "psm1", "vbs", "vbe", "js", "jse", "wsf", "wsh", "hta",
    "jar", "reg", "lnk", "url", "scf", "inf", "sh", "elf", "appimage", "app", "dmg", "pkg",
}
VIDEO_EXT = {"mkv", "mp4", "m4v", "avi", "mov", "wmv", "ts", "m2ts", "webm", "flv", "mpg", "mpeg"}
AUDIO_EXT = {"mp3", "flac", "m4a", "aac", "ogg", "opus", "wav"}
IMAGE_EXT = {"jpg", "jpeg", "png", "gif", "webp", "bmp"}
SIDECAR_EXT = {"srt", "ass", "ssa", "sub", "idx", "vtt", "sup", "nfo", "txt", "md", "sfv", "md5", "sha1", "sha256"}
DOC_EXT = {"pdf", "doc", "docx", "xls", "xlsx"}
DISGUISE_EXT = VIDEO_EXT | AUDIO_EXT | IMAGE_EXT | SIDECAR_EXT | DOC_EXT

EXEC_MIME = {
    "application/x-dosexec", "application/x-msdownload", "application/vnd.microsoft.portable-executable",
    "application/x-executable", "application/x-pie-executable", "application/x-sharedlib",
    "application/x-mach-binary", "application/x-msi", "application/x-ms-shortcut",
    "text/x-shellscript", "text/x-msdos-batch", "application/x-bat",
}
ARCHIVE_MIME = {
    "application/zip", "application/x-7z-compressed", "application/x-rar", "application/vnd.rar",
    "application/gzip", "application/x-xz", "application/x-bzip2", "application/x-tar",
    "application/x-iso9660-image", "application/zstd", "application/vnd.ms-cab-compressed",
}
PE_MIME = {"application/x-dosexec", "application/x-msdownload", "application/vnd.microsoft.portable-executable"}

BIDI = {"\u202a", "\u202b", "\u202c", "\u202d", "\u202e", "\u2066", "\u2067", "\u2068", "\u2069"}
DOUBLE_EXT = re.compile(r"\.(" + "|".join(sorted(DISGUISE_EXT)) + r")\.(" + "|".join(sorted(EXEC_EXT)) + r")$", re.I)

CAPA_MAX = 30 * 1024**2
PE_TOOL_MAX = 200 * 1024**2
SCAN_MAX = 1000 * 1024**2
HASH_MEDIA_MAX = 200 * 1024**2
CAPA_HIGHLIGHT = (
    "anti-analysis", "persistence", "communication", "collection", "impact",
    "host-interaction/process/inject", "load-code", "data-manipulation/encryption",
)


def run(cmd, timeout):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, errors="replace")
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"timed out after {timeout}s"
    except FileNotFoundError as e:
        return -2, "", str(e)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(ext, mime):
    if mime in EXEC_MIME or ext in EXEC_EXT:
        return "executable"
    if mime in ARCHIVE_MIME or ext in {"zip", "7z", "rar", "gz", "xz", "bz2", "tar", "iso", "cab", "zst"}:
        return "archive"
    if mime.startswith(("video/", "audio/", "image/")) or ext in VIDEO_EXT | AUDIO_EXT | IMAGE_EXT:
        return "media"
    if ext in SIDECAR_EXT and mime.startswith("text/"):
        return "sidecar"
    return "data"


def finding(severity, check, detail, file=None):
    return {"severity": severity, "check": check, "detail": detail, "file": file}


def probe_video(path):
    rc, out, err = run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration,format_name:stream=codec_type,codec_name", "-of", "json", path], 120)
    if rc != 0:
        return None, err.strip()[:300] or "ffprobe failed"
    data = json.loads(out or "{}")
    fmt = data.get("format", {})
    return {
        "format": fmt.get("format_name"),
        "duration": float(fmt.get("duration") or 0),
        "streams": [f"{s.get('codec_type')}:{s.get('codec_name')}" for s in data.get("streams", [])],
    }, None


def list_archive(path):
    rc, out, err = run(["7z", "l", "-slt", "-pnot-the-password", path], 300)
    entries, encrypted, cur = [], False, {}
    for line in out.splitlines() + [""]:
        if not line.strip():
            if "Path" in cur and cur.get("Folder") != "+":
                entries.append(cur["Path"])
            encrypted |= cur.get("Encrypted") == "+"
            cur = {}
        elif " = " in line:
            k, v = line.split(" = ", 1)
            cur[k] = v
    text = (out + err).lower()
    if "wrong password" in text or "can not open encrypted archive" in text:
        encrypted = True
    entries = [e for e in entries if e != path]
    return {"entries": len(entries), "encrypted": encrypted,
            "executables": [e for e in entries if e.rsplit(".", 1)[-1].lower() in EXEC_EXT][:25],
            "error": None if rc in (0, 1) else (err.strip()[:300] or f"7z exit {rc}")}


def die(path):
    rc, out, _ = run(["diec", "-j", path], 120)
    try:
        data = json.loads(out)
    except ValueError:
        return []
    found = []
    for det in data.get("detects", []):
        for v in det.get("values", []):
            found.append(v.get("string") or f"{v.get('type')}: {v.get('name')}")
    return found


def inno(path):
    rc, out, _ = run(["innoextract", "--list", path], 120)
    if rc != 0:
        return None
    files = [m.group(1) for m in re.finditer(r'^ - "(.+?)"(?! \[temp\])', out, re.M)]
    return {"files": len(files),
            "executables": [f for f in files if f.rsplit(".", 1)[-1].lower() in EXEC_EXT][:25]}


def capa(path):
    rc, out, err = run(["capa", "-j", "-q", path], 300)
    try:
        data = json.loads(out)
    except ValueError:
        return {"error": (err or out).strip().splitlines()[-1][:300] if (err or out).strip() else f"capa exit {rc}"}
    rules = [(name, r.get("meta", {})) for name, r in data.get("rules", {}).items() if not r.get("meta", {}).get("lib")]
    attack = sorted({f"{a.get('tactic')}::{a.get('technique')} [{a.get('id')}]"
                     for _, m in rules for a in m.get("attack", [])})
    highlights = sorted(f"{name} ({m.get('namespace')})" for name, m in rules
                        if (m.get("namespace") or "").startswith(CAPA_HIGHLIGHT))
    return {"rules": len(rules), "attack": attack, "highlights": highlights}


def clamscan(paths):
    if not paths:
        return [], None
    with open("/tmp/clam.list", "w") as f:
        f.write("\n".join(paths))
    rc, out, err = run(["clamscan", "--no-summary", "--infected", "--detect-pua=yes", "--tempdir=/tmp",
                        "--database=/var/lib/clamav", f"--max-filesize={SCAN_MAX}", f"--max-scansize={SCAN_MAX}",
                        "--file-list=/tmp/clam.list"], 7200)
    hits = []
    for line in out.splitlines():
        m = re.match(r"^(.*): (\S+) FOUND$", line)
        if m:
            hits.append({"file": os.path.relpath(m.group(1), SAMPLE), "signature": m.group(2)})
    return hits, (None if rc in (0, 1) else (err.strip()[:300] or f"clamscan exit {rc}"))


def yara(paths):
    hits, errors = [], []
    for p in paths:
        rc, out, err = run(["yara", "-C", "-w", "/opt/yara/core.yarc", p], 600)
        if rc != 0:
            errors.append(f"{os.path.relpath(p, SAMPLE)}: {err.strip()[:200]}")
        for line in out.splitlines():
            rule = line.split(" ", 1)[0]
            if rule:
                hits.append({"file": os.path.relpath(p, SAMPLE), "rule": rule})
    return hits, errors


def tool_versions():
    v = {"bundle": open("/opt/versions.txt").read().strip()}
    _, out, _ = run(["clamscan", "--database=/var/lib/clamav", "--version"], 30)
    v["clamav"] = out.strip()
    _, out, _ = run(["yara", "--version"], 10)
    v["yara"] = out.strip()
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", choices=["media", "software"], required=True)
    ap.add_argument("--name", required=True)
    args = ap.parse_args()

    started = time.time()
    root_is_file = os.path.isfile(SAMPLE)
    paths = [SAMPLE] if root_is_file else [
        os.path.join(d, f) for d, _, fs in os.walk(SAMPLE) for f in sorted(fs)]
    files, findings, scan_list = [], [], []

    for p in paths:
        rel = os.path.basename(args.name) if root_is_file else os.path.relpath(p, SAMPLE)
        name = os.path.basename(rel)
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        size = os.path.getsize(p)
        _, magic, _ = run(["file", "-b", p], 30)
        _, mime, _ = run(["file", "-b", "--mime-type", p], 30)
        magic, mime = magic.strip(), mime.strip()
        cls = classify(ext, mime)
        rec = {"path": rel, "size": size, "ext": ext, "mime": mime, "magic": magic[:160], "class": cls}

        if any(c in BIDI for c in name) or any(unicodedata.category(c) == "Cf" for c in name):
            findings.append(finding("block", "name", "invisible or right-to-left control character in file name", rel))
        if DOUBLE_EXT.search(name):
            findings.append(finding("block", "name", "double extension hides an executable", rel))
        if ext in DISGUISE_EXT and (mime in EXEC_MIME or mime in PE_MIME):
            findings.append(finding("block", "masquerade", f".{ext} file is really {mime}", rel))

        if cls == "executable":
            if args.profile == "media":
                findings.append(finding("block", "policy", "executable in a TV/movie download", rel))
            else:
                findings.append(finding("review", "policy", "executable: static checks cannot prove it safe", rel))
        if cls == "media" and ext in VIDEO_EXT:
            info, err = probe_video(p)
            rec["video"] = info
            if err:
                findings.append(finding("block", "media", f"not a playable video: {err}", rel))
            elif info["duration"] < 60 and size > 100 * 1024**2:
                findings.append(finding("review", "media", f"{size // 1024**2} MB video lasts {info['duration']:.0f}s", rel))
        if cls == "archive":
            rec["archive"] = a = list_archive(p)
            if a["encrypted"]:
                sev = "block" if args.profile == "media" else "review"
                findings.append(finding(sev, "archive", "password-protected archive: its contents cannot be scanned", rel))
            if a["executables"]:
                sev = "block" if args.profile == "media" else "review"
                findings.append(finding(sev, "archive", f"contains executables: {', '.join(a['executables'][:5])}", rel))
        if mime in PE_MIME and size <= PE_TOOL_MAX:
            rec["die"] = die(p)
            rec["inno"] = inno(p)
            if size <= CAPA_MAX:
                rec["capa"] = capa(p)
        if args.profile == "media" and cls == "data" and size > 1024**2:
            findings.append(finding("review", "policy", f"unidentified {mime} file in a TV/movie download", rel))

        if cls != "media" or size <= HASH_MEDIA_MAX:
            rec["sha256"] = sha256(p)
        if cls not in ("media", "sidecar"):
            if size <= SCAN_MAX:
                scan_list.append(p)
            else:
                findings.append(finding("info", "limits", f"{size // 1024**2} MB exceeds the {SCAN_MAX // 1024**2} MB scan limit; not scanned by ClamAV/YARA", rel))
        files.append(rec)

    clam_hits, clam_err = clamscan(scan_list)
    for h in clam_hits:
        pua = h["signature"].startswith("PUA.")
        findings.append(finding("review" if pua else "block", "clamav", h["signature"], h["file"]))
    if clam_err:
        findings.append(finding("review", "clamav", f"scan error: {clam_err}"))
    yara_hits, yara_errs = yara(scan_list)
    for h in yara_hits:
        mal = re.search(r"(^|_)(MAL|APT|RAT|STEALER|RANSOM|CRIME)(_|$)", h["rule"], re.I)
        findings.append(finding("block" if mal else "review", "yara", h["rule"], h["file"]))
    for e in yara_errs:
        findings.append(finding("info", "yara", f"scan error: {e}"))

    json.dump({
        "name": args.name, "profile": args.profile, "files": files, "findings": findings,
        "tools": tool_versions(), "seconds": round(time.time() - started),
    }, open(OUT, "w"), indent=2)
    print(f"scanned {len(files)} files in {round(time.time() - started)}s", file=sys.stderr)


if __name__ == "__main__":
    main()
