"""Avenue #1 helper: build canonical per-page rune ground truth from
krisyotam_runes.txt (split on '%'), for diffing against AI-vision re-reads.

Outputs analysis/vision/canonical_pages.json:
  [{page, runes, translit, n_runes}, ...]  (56 entries)
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from lp.gematria import RUNE_TO_IDX, RUNE_TO_TRANS  # noqa: E402

SRC = os.path.join(ROOT, "data", "krisyotam_runes.txt")


def main():
    raw = open(SRC, encoding="utf-8").read()
    pages = raw.split("%")
    out = []
    for i, page in enumerate(pages):
        runes = "".join(c for c in page if c in RUNE_TO_IDX)
        translit = "".join(RUNE_TO_TRANS[c] for c in runes)
        out.append({
            "page": i,
            "runes": runes,
            "translit": translit,
            "n_runes": len(runes),
        })
    dst = os.path.join(HERE, "canonical_pages.json")
    json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total = sum(p["n_runes"] for p in out)
    print(f"wrote {len(out)} pages, {total} runes -> {dst}")
    for p in out[:3]:
        print(f"  p{p['page']:>2}: {p['n_runes']:>4} runes | {p['translit'][:40]}...")
    print("  ...")
    nonempty = [p for p in out if p["n_runes"] > 0]
    print(f"  non-empty pages: {len(nonempty)}/{len(out)}")


if __name__ == "__main__":
    main()
