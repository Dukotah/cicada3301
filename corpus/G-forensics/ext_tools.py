#!/usr/bin/env python3
"""Lane G — run the external instrument battery (exiftool, binwalk, file, steghide)
over the artifact classes the pre-outage run never reached.

Appends structured rows to RESULTS.jsonl using the lane's established schema.
Bounded by a wall-clock deadline so it cannot be killed mid-write.
"""
import json, os, subprocess, sys, time, hashlib

G = os.path.dirname(os.path.abspath(__file__))
DEADLINE = time.time() + float(sys.argv[1])
KLASS = sys.argv[2] if len(sys.argv) > 2 else None
TOOL = sys.argv[3] if len(sys.argv) > 3 else "exiftool"

targets = json.load(open(os.path.join(G, "TARGETS.json")))
if KLASS:
    targets = [t for t in targets if t["class"] == KLASS]

done = set()
for l in open(os.path.join(G, "RESULTS.jsonl"), encoding="utf-8"):
    try:
        r = json.loads(l)
    except Exception:
        continue
    done.add((r.get("artifact_path"), r.get("tool")))

TOOLDEF = {
    "exiftool": {
        "argv": lambda p: ["exiftool", "-a", "-u", "-g1", "-json", p],
        "version": lambda: run(["exiftool", "-ver"]),
        "note": ("Independent metadata instrument (ExifTool). Would surface EXIF, XMP, IPTC, "
                 "Photoshop IRB, ICC, MakerNotes, PDF/PNG/GIF/ID3 metadata and any non-standard "
                 "APPn/chunk carrying text. Does NOT examine DCT coefficients or appended data."),
        "hit": lambda out: _exif_hit(out),
    },
    "binwalk": {
        "argv": lambda p: ["binwalk", "--signature", p],
        "version": lambda: run(["binwalk", "--version"]),
        "note": ("Signature scan for embedded container headers at any offset. NOTE ON POWER: inside "
                 "compressed/encrypted regions random bytes reproduce short magic sequences by chance, "
                 "so a bare match count is not evidence without header validation."),
        "hit": lambda out: len([l for l in out.splitlines() if l[:1].isdigit()]) > 0,
    },
    "file": {
        "argv": lambda p: ["file", "-b", "--mime", p],
        "version": lambda: run(["file", "--version"]).splitlines()[0] if run(["file", "--version"]) else "",
        "note": "libmagic container identification. Detects only the declared container type.",
        "hit": lambda out: False,
    },
}

INTERESTING = {"Comment", "UserComment", "XMP", "ImageDescription", "Artist", "Copyright",
               "Software", "DocumentName", "Title", "Subject", "Keywords", "Author",
               "Creator", "Producer", "ID3", "Lyrics", "TextualData", "Warning"}


def _exif_hit(out):
    try:
        d = json.loads(out)
    except Exception:
        return False
    for rec in d:
        for grp, v in rec.items():
            if isinstance(v, dict):
                for k in v:
                    if k in INTERESTING:
                        return True
            elif grp in INTERESTING:
                return True
    return False


def run(argv, timeout=25):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        return (p.stdout or b"").decode("utf-8", "replace").strip()
    except Exception:
        return ""


td = TOOLDEF[TOOL]
ver = td["version"]()
out_f = open(os.path.join(G, "RESULTS.jsonl"), "a", encoding="utf-8")
n = 0
for t in targets:
    if time.time() > DEADLINE:
        break
    key = (t["path"], TOOL)
    if key in done:
        continue
    argv = td["argv"](t["path"])
    try:
        p = subprocess.run(argv, capture_output=True, timeout=40)
        out = (p.stdout or b"").decode("utf-8", "replace")
        err = (p.stderr or b"").decode("utf-8", "replace")
        code = p.returncode
    except subprocess.TimeoutExpired:
        out, err, code = "", "timeout", -1
    except FileNotFoundError:
        print("tool missing:", TOOL)
        break
    if code != 0 and not out:
        finding = "ERROR"
    else:
        finding = "HIT" if td["hit"](out) else "NEGATIVE"
    row = {
        "artifact_path": t["path"],
        "artifact_sha256": t["sha256"],
        "artifact_class": t["class"],
        "tool": TOOL,
        "tool_version": ver,
        "command": " ".join(argv),
        "params": {},
        "exit_code": code,
        "finding": finding,
        "output_excerpt": (out or err)[:4000],
        "output_file": None,
        "note": td["note"],
        "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out_f.write(json.dumps(row) + "\n")
    out_f.flush()
    n += 1
print("appended", n, "rows for", TOOL, "class", KLASS)
