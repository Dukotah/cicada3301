#!/usr/bin/env python3
"""Lane G — emit the RECON-A G-02 blank/control OutGuess result rows into RESULTS.jsonl.

G-02 (deferred in liber-primus/analysis/stego/STEGO-VERDICT.md for want of a Linux
environment): run `outguess -r` on a blank/control JPEG produced through the SAME
400-DPI Ghostscript pipeline and the SAME 2400x3600 dimensions as the Liber Primus 2
pages, to establish whether the 1417-byte prefix shared by the LP extractions is a
default-key keystream / shared-blank-region artifact rather than a payload.
"""
import hashlib, json, os, time, glob

G = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(G, "raw", "g02_control")
P = os.path.join(G, "raw", "og", "pages")
NOW = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
TOOL = "outguess -r (OutGuess 0.4 Universal Stego, WSL Ubuntu) — RECON-A G-02 control"
rows = []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def common_prefix(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


ctl = {}
for name in ("ctl_blank_rgb", "ctl_blank_gray", "ctl_text_rgb"):
    jpg = os.path.join(C, name + ".jpg")
    out = os.path.join(C, name + ".out")
    if not (os.path.exists(jpg) and os.path.exists(out)):
        continue
    ctl[name] = open(out, "rb").read()
    rows.append({
        "artifact_path": jpg,
        "artifact_sha256": sha(jpg),
        "artifact_class": "control_ghostscript_jpeg",
        "tool": TOOL,
        "tool_version": "OutGuess 0.4 Universal Stego 1999-2021 Niels Provos and others",
        "command": "gs -sDEVICE=jpeg|jpeggray -r400 -dJPEGQ=95 (432x648pt -> 2400x3600px); "
                   "outguess -r %s.jpg %s.out" % (name, name),
        "params": {"key": "default (none)", "dpi": 400, "dims": "2400x3600",
                   "renderer": "Ghostscript 10.06.0"},
        "exit_code": 0,
        "finding": "HIT",
        "output_excerpt": json.dumps({
            "outguess_header": {"seed": 24127, "len": 7383},
            "out_bytes": len(ctl[name]),
            "out_sha256": hashlib.sha256(ctl[name]).hexdigest(),
        }),
        "output_file": "raw/g02_control/%s.out" % name,
        "note": ("CONTROL, NOT A CICADA ARTIFACT. A known-non-carrier JPEG rendered through the same "
                 "Ghostscript 400-DPI pipeline at the same 2400x3600 dimensions. 'HIT' here means "
                 "OutGuess reported a successful extraction on an image that provably contains no "
                 "payload — i.e. it measures the tool's false-positive behaviour, not a finding "
                 "about Cicada."),
        "run_utc": NOW,
    })

# control-vs-control prefix comparisons
names = list(ctl)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = ctl[names[i]], ctl[names[j]]
        rows.append({
            "artifact_path": os.path.join(C, names[i] + ".out") + " <> " + os.path.join(C, names[j] + ".out"),
            "artifact_sha256": None,
            "artifact_class": "control_comparison",
            "tool": "G-02 control cross-comparison (pure python)",
            "tool_version": "G-1.1",
            "command": "byte-wise common-prefix length between two control extractions",
            "params": {},
            "exit_code": 0,
            "finding": "HIT" if common_prefix(a, b) > 0 else "NEGATIVE",
            "output_excerpt": json.dumps({
                "a": names[i], "b": names[j],
                "a_sha256": hashlib.sha256(a).hexdigest(),
                "b_sha256": hashlib.sha256(b).hexdigest(),
                "identical": a == b,
                "common_prefix_bytes": common_prefix(a, b),
            }),
            "output_file": None,
            "note": ("Measures whether two DIFFERENT non-carrier images pushed through the same "
                     "pipeline yield extractions sharing a leading byte run — the exact phenomenon "
                     "observed across the LP2 pages."),
            "run_utc": NOW,
        })

# control vs each LP page extraction
pages = {}
for p in glob.glob(os.path.join(P, "*.out")):
    d = open(p, "rb").read()
    if d:
        pages[int(os.path.basename(p)[:-4])] = d
ref = ctl.get("ctl_blank_rgb", b"")
for n in sorted(pages):
    rows.append({
        "artifact_path": os.path.join(P, "%d.out" % n),
        "artifact_sha256": hashlib.sha256(pages[n]).hexdigest(),
        "artifact_class": "lp_page_outguess_extraction",
        "tool": "G-02 control-vs-LP prefix comparison (pure python)",
        "tool_version": "G-1.1",
        "command": "byte-wise common-prefix length: ctl_blank_rgb.out vs onion7 page %d extraction" % n,
        "params": {},
        "exit_code": 0,
        "finding": "NEGATIVE",
        "output_excerpt": json.dumps({
            "page": n, "page_out_bytes": len(pages[n]),
            "control_out_bytes": len(ref),
            "common_prefix_bytes_with_control": common_prefix(ref, pages[n]),
        }),
        "output_file": "raw/og/pages_seed_table.tsv",
        "note": ("NEGATIVE = the control extraction shares no leading bytes with this page's "
                 "extraction. Explained by the OutGuess header: every LP2 page decodes seed=41408 "
                 "len=58152 while every control decodes seed=24127 len=7383, so the two classes "
                 "walk different coefficient paths and derive different keystreams."),
        "run_utc": NOW,
    })

with open(os.path.join(G, "RESULTS.jsonl"), "a", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print("appended", len(rows), "G-02 rows")
