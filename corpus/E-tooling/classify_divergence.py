#!/usr/bin/env python3
"""Classify every canon-segment divergence in a vendored transcription as
OMISSION (segment absent / truncated) vs CONTRADICTION (a different rune at the
same position -- a genuine reading conflict).

Method: anchor the canon segment inside the file's rune stream via the longest
matching block, then run difflib.SequenceMatcher over the aligned window and
emit every opcode with rune context.
"""
import os, sys, json, difflib, datetime

E = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(E, "..", ".."))
CANON_FILE = os.path.join(REPO, "liber-primus", "data", "krisyotam_runes.txt")
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
IDX = {r: i for i, r in enumerate(GP)}
# Codepoint aliases seen in the wild: some transcriptions encode GP index 11 (J)
# as U+16C2 RUNIC LETTER E rather than U+16C4 RUNIC LETTER GER. Same glyph slot,
# different codepoint -- an ENCODING variant, not a reading difference.
IDX["ᛂ"] = 11
TR = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M",
      "L","NG","OE","D","A","AE","Y","IA","EA"]

def runes(t):
    return [IDX[c] for c in t if c in IDX]

def segments():
    raw = open(CANON_FILE, encoding="utf-8").read()
    return [r for r in (runes(p) for p in raw.split("%")) if r]

def show(seq):
    return "".join(GP[i] for i in seq)

def tr(seq):
    return "".join(TR[i] for i in seq)

def classify(seg, hay, ctx=12):
    """Return (verdict, details[]) for one canon segment vs a full rune stream."""
    sm = difflib.SequenceMatcher(None, seg, hay, autojunk=False)
    # longest matching block anchors the alignment
    a, b, size = sm.find_longest_match(0, len(seg), 0, len(hay))
    cover = size / len(seg)
    if size < 20 or cover < 0.25:
        return "OMISSION", {"reason": "segment does not appear in file (longest common run "
                            f"{size}/{len(seg)} runes)", "longest_common_run": size,
                            "coverage": round(cover, 4)}, []
    # window in the file that should hold the whole segment
    start = max(0, b - a - 30)
    end = min(len(hay), b - a + len(seg) + 30)
    win = hay[start:end]
    sm2 = difflib.SequenceMatcher(None, seg, win, autojunk=False)
    ops = [o for o in sm2.get_opcodes() if o[0] != "equal"]
    diffs = []
    for tag, i1, i2, j1, j2 in ops:
        # trim leading/trailing window padding artefacts
        if tag == "insert" and (j1 == 0 or j2 == len(win)):
            continue
        if tag == "delete" and (i1 == 0 or i2 == len(seg)) and (i2 - i1) < 3:
            pass
        d = {
            "op": tag,
            "canon_pos_in_segment": i1,
            "canon_runes": show(seg[i1:i2]),
            "canon_translit": tr(seg[i1:i2]),
            "file_runes": show(win[j1:j2]),
            "file_translit": tr(win[j1:j2]),
            "canon_context": show(seg[max(0,i1-ctx):i1]) + " >" + show(seg[i1:i2]) + "< " + show(seg[i2:i2+ctx]),
            "file_context": show(win[max(0,j1-ctx):j1]) + " >" + show(win[j1:j2]) + "< " + show(win[j2:j2+ctx]),
        }
        diffs.append(d)
    if not diffs:
        return "MATCHES_WITH_ALIGNMENT", {"note": "segment present; earlier miss was a "
                                         "substring-search artefact"}, []
    # truncation: all divergence is one trailing delete running to the segment end
    if len(diffs) == 1 and diffs[0]["op"] == "delete" and ops[0][2] == len(seg):
        return "OMISSION", {"reason": "file truncates the segment (tail absent)",
                            "n_runes_missing": ops[0][2] - ops[0][1]}, diffs
    if len(diffs) == 1 and diffs[0]["op"] == "delete" and ops[0][1] == 0:
        return "OMISSION", {"reason": "file omits the segment head",
                            "n_runes_missing": ops[0][2] - ops[0][1]}, diffs
    has_repl = any(d["op"] == "replace" for d in diffs)
    return ("CONTRADICTION" if has_repl else "INDEL"), {
        "reason": "different rune(s) at the same aligned position" if has_repl
                  else "insertion/deletion of rune(s) inside an otherwise matching segment",
        "n_ops": len(diffs)}, diffs

def main():
    segs = segments()
    scan = json.load(open(os.path.join(E, "vendor_scan.json"), encoding="utf-8"))
    diffj = json.load(open(os.path.join(E, "transcription_diff.json"), encoding="utf-8"))
    out = []
    for c in diffj["comparisons"]:
        if not c["canon_segments_missing"]:
            continue
        p = os.path.join(E, "vendor", c["repo"], c["path"])
        if not os.path.exists(p):
            continue
        hay = runes(open(p, encoding="utf-8", errors="ignore").read())
        rec = {"repo": c["repo"], "path": c["path"], "clone_sha": c["clone_sha"],
               "n_runes_in_file": c["n_runes_in_file"], "findings": []}
        for si in c["canon_segments_missing"]:
            verdict, why, diffs = classify(segs[si], hay)
            rec["findings"].append({"canon_segment": si, "segment_len": len(segs[si]),
                                    "verdict": verdict, "why": why, "diffs": diffs[:8]})
        out.append(rec)
        for f in rec["findings"]:
            print(f"{c['repo'][:40]:40s} {c['path'][-38:]:38s} seg{f['canon_segment']:3d} "
                  f"{f['verdict']}")
    res = {"generated_utc": datetime.datetime.now(datetime.timezone.utc)
               .strftime("%Y-%m-%dT%H:%M:%SZ"),
           "canon_file": "liber-primus/data/krisyotam_runes.txt",
           "canon_sha256_indices": diffj["canon_sha256_indices"],
           "results": out}
    json.dump(res, open(os.path.join(E, "divergence_classified.json"), "w",
              encoding="utf-8"), indent=1, ensure_ascii=False)
    n_contra = sum(1 for r in out for f in r["findings"] if f["verdict"] == "CONTRADICTION")
    n_indel = sum(1 for r in out for f in r["findings"] if f["verdict"] == "INDEL")
    n_omit = sum(1 for r in out for f in r["findings"] if f["verdict"] == "OMISSION")
    print(f"\nCONTRADICTION={n_contra}  INDEL={n_indel}  OMISSION={n_omit}")

if __name__ == "__main__":
    main()
