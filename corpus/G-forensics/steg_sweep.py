#!/usr/bin/env python3
"""Lane G — steghide sweep over the JPEG artifact classes.

steghide only supports JPEG/BMP/WAV/AU carriers. For any other container the correct
finding is NOT_APPLICABLE (the instrument could not examine the artifact and therefore
contributes no evidence), never NEGATIVE.
"""
import json, os, subprocess, sys, time

G = os.path.dirname(os.path.abspath(__file__))
DEADLINE = time.time() + float(sys.argv[1])
targets = json.load(open(os.path.join(G, "TARGETS.json")))

done = set()
for l in open(os.path.join(G, "RESULTS.jsonl"), encoding="utf-8"):
    try:
        r = json.loads(l)
    except Exception:
        continue
    done.add((r.get("artifact_path"), r.get("tool")))

TOOL = "steghide info -p '' (JPEG/BMP/WAV/AU carriers only)"
ver = ""
try:
    ver = subprocess.run(["steghide", "--version"], capture_output=True, timeout=10).stdout.decode().strip()
except Exception:
    pass

SUPPORTED = (b"\xff\xd8\xff", b"BM", b"RIFF", b".snd")
NOTE_OK = ("steghide with an empty passphrase. Detects a steghide-embedded payload in a "
           "supported carrier. Does NOT detect OutGuess, JSteg, F5, appended data, or any "
           "non-steghide embedding, and cannot recover a payload under an unknown passphrase.")
NOTE_NA = ("NOT_APPLICABLE, not NEGATIVE: steghide does not support this container format, so "
           "it never examined the artifact and contributes no evidence either way.")

out_f = open(os.path.join(G, "RESULTS.jsonl"), "a", encoding="utf-8")
n = na = 0
for t in targets:
    if time.time() > DEADLINE:
        break
    if (t["path"], TOOL) in done:
        continue
    try:
        head = open(t["path"], "rb").read(4)
    except Exception:
        continue
    supported = any(head.startswith(m) for m in SUPPORTED)
    if not supported:
        row = dict(finding="NOT_APPLICABLE", exit_code=None, output_excerpt="", note=NOTE_NA,
                   command="(skipped: unsupported container)")
        na += 1
    else:
        try:
            p = subprocess.run(["steghide", "info", "-p", "", t["path"]],
                               capture_output=True, timeout=30)
            o = (p.stdout or b"").decode("utf-8", "replace")
            e = (p.stderr or b"").decode("utf-8", "replace")
            code = p.returncode
        except Exception as ex:
            o, e, code = "", str(ex), -1
        txt = (o + e)
        if "could not extract any data" in txt or "wrong passphrase" in txt or code != 0:
            finding = "NEGATIVE"
        elif "embedded file" in txt or "capacity" in txt and "embedded" in txt:
            finding = "HIT"
        else:
            finding = "NEGATIVE"
        row = dict(finding=finding, exit_code=code, output_excerpt=txt[:1500], note=NOTE_OK,
                   command="steghide info -p '' %s" % t["path"])
        n += 1
    out_f.write(json.dumps({
        "artifact_path": t["path"], "artifact_sha256": t["sha256"], "artifact_class": t["class"],
        "tool": TOOL, "tool_version": ver, "params": {"passphrase": ""},
        "output_file": None, "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **row}) + "\n")
    out_f.flush()
print("steghide examined", n, "| NOT_APPLICABLE", na)
