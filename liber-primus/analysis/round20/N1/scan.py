#!/usr/bin/env python3
"""N1 scanner. Run every PDF under given roots through pdffonts + pdftotext +
strings|grep, flag any with (a) an embedded runic font subset or (b) a runic
text layer. Report /BaseFont subset tags verbatim.
"""
import os, re, subprocess, sys, json, hashlib

RUNIC_FACE_HINT = re.compile(
    r'runic|junicode|everson|allrune|futhark|babelstone|noto.?sans.?runic|runlitt|gullhornet',
    re.I)


def sha(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()[:12]


def pdffonts(path):
    r = subprocess.run(["pdffonts", path], capture_output=True, text=True, timeout=60)
    return r.stdout, r.stderr


def scan_one(path):
    rec = {"path": path}
    try:
        out, err = pdffonts(path)
    except Exception as e:
        rec["error"] = "pdffonts:%s" % e
        return rec
    fonts = []
    for line in out.splitlines()[2:]:
        if not line.strip():
            continue
        cols = line.split()
        name = cols[0] if cols else ""
        fonts.append(name)
    rec["fonts"] = fonts
    # subset tags
    tags = re.findall(r'([A-Z]{6})\+(\S+)', out)
    rec["subset_tags"] = ["%s+%s" % (t, n) for t, n in tags]
    # runic-faced fonts (subset or not)
    rec["runic_fonts"] = [f for f in fonts if RUNIC_FACE_HINT.search(f)]
    rec["runic_subset_tags"] = [t for t in rec["subset_tags"] if RUNIC_FACE_HINT.search(t)]
    # text layer: count U+16A0..16FF
    try:
        rt = subprocess.run(["pdftotext", "-q", path, "-"], capture_output=True,
                            text=True, timeout=60)
        txt = rt.stdout
        n_runic = sum(1 for c in txt if 0x16A0 <= ord(c) <= 0x16FF)
        rec["n_runic_textlayer"] = n_runic
    except Exception as e:
        rec["n_runic_textlayer"] = -1
    # strings residue for FontFile / embedded runic BaseFont
    try:
        rs = subprocess.run(["bash", "-c",
            "strings %r | grep -iE 'FontFile|BaseFont|allrune|futhark' | head -20" % path],
            capture_output=True, text=True, timeout=60)
        rec["strings_hits"] = [l for l in rs.stdout.splitlines() if l.strip()][:20]
    except Exception:
        rec["strings_hits"] = []
    rec["interesting"] = bool(rec["runic_subset_tags"] or rec["runic_fonts"]
                              or rec["n_runic_textlayer"] > 0)
    return rec


def main():
    roots = sys.argv[1:] or ["."]
    seen_sha = {}
    records = []
    paths = []
    for root in roots:
        for dirpath, _, files in os.walk(root):
            for fn in files:
                if fn.lower().endswith(".pdf"):
                    paths.append(os.path.join(dirpath, fn))
    n_dup = 0
    for p in paths:
        try:
            s = sha(p)
        except Exception:
            s = None
        if s and s in seen_sha:
            n_dup += 1
            continue
        if s:
            seen_sha[s] = p
        rec = scan_one(p)
        rec["sha1_12"] = s
        records.append(rec)
    summary = {
        "n_paths": len(paths),
        "n_distinct": len(records),
        "n_dup": n_dup,
        "interesting": [r for r in records if r.get("interesting")],
        "with_runic_subset": [r for r in records if r.get("runic_subset_tags")],
        "with_text_layer": [r for r in records if r.get("n_runic_textlayer", 0) > 0],
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan_results.json")
    with open(out, "w") as f:
        json.dump({"summary_counts": {
            "n_paths": summary["n_paths"], "n_distinct": summary["n_distinct"],
            "n_dup": summary["n_dup"],
            "n_interesting": len(summary["interesting"]),
            "n_with_runic_subset": len(summary["with_runic_subset"]),
            "n_with_text_layer": len(summary["with_text_layer"]),
        }, "interesting": summary["interesting"], "all": records}, f, indent=1)
    print(json.dumps({
        "n_paths": summary["n_paths"], "n_distinct": summary["n_distinct"],
        "n_dup": summary["n_dup"],
        "n_interesting": len(summary["interesting"]),
        "n_with_runic_subset": len(summary["with_runic_subset"]),
        "runic_subset_tags": sorted({t for r in summary["with_runic_subset"]
                                     for t in r["runic_subset_tags"]}),
        "text_layer_paths": [(r["path"], r["n_runic_textlayer"])
                             for r in summary["with_text_layer"]],
    }, indent=1))


if __name__ == "__main__":
    main()
