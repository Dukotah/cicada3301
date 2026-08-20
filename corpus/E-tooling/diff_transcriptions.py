#!/usr/bin/env python3
"""Segment-level divergence test between OUR canonical transcription and every
rune-bearing file found in vendor/.

Our canon (liber-primus/data/krisyotam_runes.txt) is 13,136 runes in 57
'%'-delimited segments. Third-party files usually carry the WHOLE Liber Primus
(~15,900 runes: LP1 solved pages + LP2), so a raw count/hash mismatch is
expected and meaningless. The real test is:

    does every one of our 57 segments appear VERBATIM, as a contiguous run,
    inside the other file's rune stream?

A segment that does not appear is a genuine transcription divergence.
Output: transcription_diff.json + a human summary on stdout.
"""
import os, sys, json, hashlib, datetime

E = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(E, "..", ".."))
CANON_FILE = os.path.join(REPO, "liber-primus", "data", "krisyotam_runes.txt")

GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
IDX = {r: i for i, r in enumerate(GP)}
# Codepoint aliases seen in the wild: some transcriptions encode GP index 11 (J)
# as U+16C2 RUNIC LETTER E rather than U+16C4 RUNIC LETTER GER. Same glyph slot,
# different codepoint -- an ENCODING variant, not a reading difference.
IDX["ᛂ"] = 11


def runes(text):
    return [IDX[c] for c in text if c in IDX]


def canon_segments():
    raw = open(CANON_FILE, encoding="utf-8").read()
    segs = []
    for part in raw.split("%"):
        r = runes(part)
        if r:
            segs.append(r)
    return segs


def to_str(seq):
    # single-char-per-rune encoding so we can use fast substring search
    return "".join(chr(0xE000 + i) for i in seq)


def main():
    segs = canon_segments()
    total = sum(len(s) for s in segs)
    print(f"canon: {len(segs)} segments, {total} runes, file={CANON_FILE}")

    scan = json.load(open(os.path.join(E, "vendor_scan.json"), encoding="utf-8"))
    seg_strs = [to_str(s) for s in segs]

    results = []
    for repo in scan["repos"]:
        for f in (repo.get("rune_files") or []):
            if f["n_runes_gp29"] < 5000:
                continue
            p = os.path.join(E, "vendor", repo["dir"], f["path"])
            try:
                t = open(p, encoding="utf-8", errors="ignore").read()
            except Exception as e:
                continue
            hay = to_str(runes(t))
            missing = []
            for i, ss in enumerate(seg_strs):
                if ss not in hay:
                    missing.append(i)
            rec = {
                "repo": repo["dir"],
                "path": f["path"],
                "clone_sha": repo.get("clone_sha"),
                "n_runes_in_file": f["n_runes_gp29"],
                "file_sha256": f["file_sha256"],
                "sha256_indices": f["sha256_indices"],
                "canon_segments_total": len(segs),
                "canon_segments_found_verbatim": len(segs) - len(missing),
                "canon_segments_missing": missing,
                "identical_to_canon": f["sha256_indices"] ==
                    hashlib.sha256(",".join(str(x) for s in segs for x in s).encode()).hexdigest(),
            }
            results.append(rec)
            status = "ALL 57 PRESENT" if not missing else f"MISSING {len(missing)}: {missing}"
            print(f"  {repo['dir']:52s} {f['path'][:44]:44s} n={f['n_runes_gp29']:6d}  {status}")

    out = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "canon_file": "liber-primus/data/krisyotam_runes.txt",
        "canon_n_segments": len(segs),
        "canon_n_runes": total,
        "canon_sha256_indices":
            hashlib.sha256(",".join(str(x) for s in segs for x in s).encode()).hexdigest(),
        "comparisons": results,
    }
    json.dump(out, open(os.path.join(E, "transcription_diff.json"), "w", encoding="utf-8"),
              indent=1)
    div = [r for r in results if r["canon_segments_missing"]]
    print(f"\ncompared={len(results)}  divergent={len(div)}")


if __name__ == "__main__":
    main()
