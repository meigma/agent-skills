#!/usr/bin/env python3
"""Turn scan.json (+ provenance.json) into a verdict and a Markdown report.

Runs on the operator machine, outside the scanner container. With
VT_API_KEY set it adds VirusTotal hash lookups for executables and archives
(hash lookups only: nothing is ever uploaded).

usage: report.py <scan.json> <provenance.json>
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

SEVERITY = {"block": 2, "review": 1, "info": 0}
GENERIC = re.compile(
    r"hack ?tool|keygen|crack|patch|pua|riskware|not-a-virus|activator|kms|unwanted|grayware|potentially|generic|heur", re.I)


def vt_lookup(sha, key):
    req = urllib.request.Request(f"https://www.virustotal.com/api/v3/files/{sha}", headers={"x-apikey": key})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            attrs = json.load(r)["data"]["attributes"]
    except urllib.error.HTTPError as e:
        return None if e.code == 404 else {"error": f"HTTP {e.code}"}
    stats = attrs.get("last_analysis_stats", {})
    names = sorted({v["result"] for v in attrs.get("last_analysis_results", {}).values()
                    if v.get("category") == "malicious" and v.get("result")})
    return {"malicious": stats.get("malicious", 0), "suspicious": stats.get("suspicious", 0), "names": names}


def add_virustotal(scan):
    key = os.environ.get("VT_API_KEY")
    targets = [f for f in scan["files"] if f.get("sha256") and f["class"] in ("executable", "archive")][:20]
    if not key:
        for f in targets:
            scan["findings"].append({"severity": "info", "check": "virustotal", "file": f["path"],
                                     "detail": f"not looked up (no VT_API_KEY): https://www.virustotal.com/gui/file/{f['sha256']}"})
        return
    delay = float(os.environ.get("VT_RATE_DELAY", "15"))
    for i, f in enumerate(targets):
        if i:
            time.sleep(delay)
        r = vt_lookup(f["sha256"], key)
        f["virustotal"] = r
        if r is None:
            sev, detail = "info", "unknown to VirusTotal"
        elif "error" in r:
            sev, detail = "info", f"lookup failed: {r['error']}"
        else:
            m, specific = r["malicious"], [n for n in r["names"] if not GENERIC.search(n)]
            if m == 0:
                sev = "info"
            elif m >= 5 and specific:
                sev = "block"
            else:
                sev = "review"
            shown = ", ".join((specific or r["names"])[:6])
            detail = f"{m} malicious, {r['suspicious']} suspicious" + (f": {shown}" if shown else "")
        scan["findings"].append({"severity": sev, "check": "virustotal", "file": f["path"], "detail": detail})


def render(scan, prov):
    findings = sorted(scan["findings"], key=lambda f: -SEVERITY[f["severity"]])
    top = max((SEVERITY[f["severity"]] for f in findings), default=0)
    verdict = {2: "BLOCK", 1: "REVIEW", 0: "PASS"}[top]
    classes = {}
    for f in scan["files"]:
        classes[f["class"]] = classes.get(f["class"], 0) + 1
    total = sum(f["size"] for f in scan["files"])

    out = [f"# Triage: {scan['name']}", "",
           f"**Verdict: {verdict}** (profile `{scan['profile']}`, {len(scan['files'])} files, "
           f"{total / 1024**3:.2f} GiB, scanned in {scan['seconds']}s)", "",
           {"BLOCK": "Do not open or run anything from this download. Delete it and blocklist the release.",
            "REVIEW": "Static checks found nothing that proves this is malicious, but something needs judgement. "
                      "Read the findings; run executables only somewhere disposable.",
            "PASS": "No findings. For media this is a strong result; it never proves an executable safe."}[verdict], ""]

    out += ["## Provenance", ""]
    if not prov.get("torrents"):
        out += ["No qBittorrent torrent holds these files (Usenet download, manual copy, or the torrent was removed). "
                "Check the source by hand.", ""]
    else:
        for t in prov["torrents"]:
            out += [f"- **{t['name']}**, infohash `{t['hash']}`, category `{t.get('category') or '-'}` "
                    f"(matched by {t.get('match', 'hardlinked files')})",
                    f"  - comment: {t.get('comment') or '-'}; created by: {t.get('created_by') or '-'}",
                    f"  - trackers: {', '.join(t.get('trackers', [])[:4]) or '-'}"]
        out += ["", "Confirm the infohash against the release's **official** page before trusting an executable.", ""]

    out += ["## Findings", "", "| Severity | Check | File | Detail |", "| --- | --- | --- | --- |"]
    for f in findings:
        out.append(f"| {f['severity']} | {f['check']} | {f.get('file') or '-'} | {f['detail'].replace('|', '/')} |")
    if not findings:
        out.append("| - | - | - | none |")

    out += ["", "## Inventory", "", ", ".join(f"{n} {c}" for c, n in sorted(classes.items())), ""]
    for f in scan["files"]:
        if f["class"] in ("executable", "archive") or f.get("die") or f.get("capa"):
            out.append(f"### `{f['path']}`")
            out.append(f"- {f['size']:,} bytes, {f['mime']}; sha256 `{f.get('sha256', '-')}`")
            if f.get("die"):
                out.append(f"- Detect It Easy: {'; '.join(f['die'])}")
            if f.get("inno"):
                exes = ", ".join(f["inno"]["executables"][:8])
                out.append(f"- Inno Setup payload: {f['inno']['files']} files" + (f"; executables: {exes}" if exes else ""))
            if f.get("archive"):
                a = f["archive"]
                out.append(f"- Archive: {a['entries']} entries, encrypted={a['encrypted']}"
                           + (f"; executables: {', '.join(a['executables'][:8])}" if a["executables"] else ""))
            c = f.get("capa")
            if c and "error" in c:
                out.append(f"- capa: {c['error']}")
            elif c:
                out.append(f"- capa: {c['rules']} capabilities")
                for h in c["highlights"][:12]:
                    out.append(f"  - {h}")
                if c["attack"]:
                    out.append(f"  - ATT&CK: {'; '.join(c['attack'][:10])}")
            out.append("")
    videos = [f for f in scan["files"] if f.get("video")]
    for v in videos[:10]:
        out.append(f"- `{v['path']}`: {v['video']['format']}, {v['video']['duration'] / 60:.0f} min, "
                   f"{', '.join(v['video']['streams'][:6])}")
    out += ["", "## Scanners", "", f"- {scan['tools']['bundle']}", f"- {scan['tools']['clamav']}",
            f"- yara {scan['tools']['yara']}", ""]
    return verdict, "\n".join(out)


def main():
    scan = json.load(open(sys.argv[1]))
    prov = json.load(open(sys.argv[2]))
    add_virustotal(scan)
    verdict, md = render(scan, prov)
    print(md)
    sys.exit({"PASS": 0, "REVIEW": 10, "BLOCK": 20}[verdict])


if __name__ == "__main__":
    main()
