---
name: untrusted-file-triage
description: >
  Use when a download from the lab media stack (qBittorrent, SABnzbd, Sonarr,
  Radarr, Gamarr on media01) must be checked before anyone opens, installs, or
  runs it: "is this torrent safe", "scan this repack", "check this download
  for malware", "validate this game before I install it", suspicious files in
  a TV or movie download. Runs a pinned static scanner (ClamAV, YARA-Forge,
  capa, Detect It Easy, ffprobe, 7-Zip, innoextract) in an isolated container
  on media01, traces the files to their torrent, and returns a PASS, REVIEW,
  or BLOCK verdict.
---

# Untrusted file triage

Static triage for downloads on `media01` (the lab media VM on `nas01`). It
never executes the sample. The output is a verdict plus the evidence behind
it; turning that into a decision (and telling the user) is your job.

No scanner proves a file safe. For TV and movies a PASS is strong evidence,
because valid video files are rarely dangerous. For software and game repacks
the best result is **REVIEW with no block findings and a confirmed source**;
the remaining risk is handled by containment (see "Running software").

## Requirements

- The `nas01:` Incus remote (operator client certificate). `incus exec
  nas01:media01 -- true` must work.
- `python3` locally. Optional: `VT_API_KEY` for VirusTotal hash lookups.

## Run it

```bash
~/.agents/skills/untrusted-file-triage/scripts/triage.sh "/data/torrents/games/<release>"
```

- The argument is a file or directory **as seen on media01**, under `/data`:
  the torrent's content path (`/data/torrents/<category>/…`), a Usenet job
  (`/data/usenet/complete/<category>/…`), or an imported library folder
  (`/data/media/{tv,movies,games}/…`). Find content paths with
  `incus exec nas01:media01 -- docker exec qbittorrent curl -s http://127.0.0.1:8080/api/v2/torrents/info`.
- The profile is picked from the path: TV/movie paths get `media` (any
  executable or encrypted archive is a BLOCK), everything else gets
  `software` (executables are REVIEW). Override with `--profile media|software`.
- Exit status: `0` PASS, `10` REVIEW, `20` BLOCK, anything else means triage
  itself failed (read stderr; do not treat it as a verdict).
- The report prints to stdout and is saved, with `scan.json` and
  `provenance.json`, under `~/.local/state/untrusted-file-triage/<time>-<name>/`.
- First run on a new scanner version builds the image on media01 (about two
  minutes). A 4 GB repack scans in about two minutes; video is checked with
  `ffprobe` only and takes seconds.

## What happens

1. Builds `untrusted-triage:<hash>` on media01 from `scanner/` if that exact
   version is missing, and removes older versions.
2. Refreshes ClamAV signatures into the `triage-clamdb` volume when they are
   older than 12 hours. This is the only step with network access.
3. Finds the qBittorrent torrent holding the files: same inode (Sonarr and
   Radarr hardlink imports), else identical names and sizes (Gamarr copies).
   Records the infohash, trackers, and torrent comment.
4. Scans in a container with `--network none`, a read-only root, all
   capabilities dropped, user `nobody`, 3 GiB memory, and the sample mounted
   read-only. Per file: magic type versus extension, name tricks (double
   extensions, right-to-left characters), `ffprobe` for video, archive
   listing and encryption, Detect It Easy and the Inno Setup payload list and
   capa for Windows executables, then ClamAV (with PUA detection) and the
   YARA-Forge core rules over everything that is not media.
5. Renders the verdict locally, adding VirusTotal hash lookups when
   `VT_API_KEY` is set. Hashes only: never upload a sample anywhere.

## Reading the findings

| Finding | Meaning |
| --- | --- |
| `name`, `masquerade` block | A file pretends to be something else. Treat the whole download as hostile. |
| `media` block | A "video" that `ffprobe` cannot read. Fake episodes that are really archives or installers land here. |
| `policy` block (media profile) | An executable, script, shortcut, or encrypted archive inside a TV/movie release. Real releases never contain these. |
| `policy` review (software profile) | Expected for any software. It is the reminder that static checks cannot clear an executable. |
| `clamav` block | A named malware signature. Do not second-guess it. |
| `clamav` review `PUA.*` | Potentially unwanted: keygens, cracks, hack tools. Expected for cracked games; matters only with other signals. |
| `yara` block | A rule naming malware, an APT, a RAT, a stealer, or ransomware. |
| `yara` review | Suspicious-pattern or hack-tool rules. Read the rule name; packers and installers trigger some. |
| `virustotal` | Five or more engines with specific family names is a block. Only generic names (HackTool, Keygen, Riskware, Generic) is a review. Unknown to VirusTotal is normal for fresh repacks. |
| `limits` info | A file over 1000 MB was not scanned by ClamAV or YARA. Repack `.bin` archives are compressed, so scanning them finds little anyway. |

capa lists what an executable can do, not what it does. Installers routinely
show locale/geolocation checks, process memory changes, registry queries,
and shutdown/reboot: that is normal for Inno Setup (FitGirl, DODI). Look for
combinations an installer has no use for: keylogging, screen capture,
credential or browser-data access, persistence plus network communication.

## Confirming the source

For software, the provenance check matters more than any scanner: most
malicious repacks are fakes posted under a known name.

1. Take the infohash from the report.
2. Find the release on the repacker's **official** site only (FitGirl:
   `fitgirl-repacks.site`, whose search is `https://fitgirl-repacks.site/?s=<title>`;
   lookalike domains are common and are themselves malware sources). Pull
   the magnet infohashes from the release page and compare, ignoring case:

   ```bash
   curl -s -A 'Mozilla/5.0' https://fitgirl-repacks.site/<release-slug>/ | grep -o -i 'btih:[0-9a-f]\{40\}' | sort -u
   ```

3. Report a match, a mismatch (treat as BLOCK), or that you could not find
   the release (stays REVIEW).

## After the verdict

- **BLOCK**: tell the user what was found. Recommend removing the torrent
  with its files and blocklisting the release in Sonarr/Radarr/Gamarr
  (Activity → remove → blocklist). Do not delete anything without the user's
  go-ahead.
- **REVIEW**, media profile: explain the specific finding and let the user
  decide.
- **REVIEW**, software profile: if there are no block findings and the source
  is confirmed, it is reasonable to install. Recommend containment below.
- **PASS**: say so, including the profile it was checked against.

## Running software

Install and run software only on `win01` (Windows 11 VM on lab02, see the
lab's Windows VM runbook), never on the operator Mac or media01, and snapshot
it first:

```bash
incus snapshot create nas01:win01 pre-<release>    # before installing
incus snapshot restore nas01:win01 pre-<release>   # if anything looks wrong
incus snapshot delete nas01:win01 pre-<release>    # once satisfied
```

## Rules

- Never execute, open, or extract a sample on media01 or the operator machine,
  and never copy samples to the operator machine. Work through the scanner.
- Never upload samples to VirusTotal or any other service; hash lookups only.
- A failed triage (non 0/10/20 exit) is not a verdict. Fix and rerun.
- Do not loosen the scanner container's isolation flags to make a scan pass.

## Maintenance

Tool versions are pinned in `scanner/Dockerfile` (base image digest, capa,
Detect It Easy, YARA-Forge core rules, each with a SHA-256). Bump a version
and its digest together; the image tag is a hash of `scanner/`, so the next
run rebuilds automatically. ClamAV signatures update themselves.
