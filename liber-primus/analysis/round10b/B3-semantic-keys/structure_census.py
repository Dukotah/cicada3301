"""Structural census: do the UNSOLVED LP2 pages carry set-apart HEADER lines the way the
solved pages do?  (Lane brief handle #3.)  Also documents the '&' / '$' ornament grammar.

Run: PYTHONUTF8=1 python3 structure_census.py
"""
import statistics
import sys

import b3lib
from b3lib import gp


def main():
    raws = b3lib.lp2_segments_raw()
    print("SOLVED reference pages (corpus): first physical line")
    for lbl in ("03.jpg", "05.jpg", "14.jpg"):
        _, page = b3lib.solved_page(lbl)
        first = page["runes"].split("\n")[0]
        idx = gp.runes_to_indices(first)
        print(f"  {lbl:<8s} first line = {len(idx):2d} runes -> "
              f"{gp.indices_to_translit(idx)}")
    print("\nLP2 segments: line profile + ornament grammar")
    short = []
    for si, raw in enumerate(raws):
        lines = [l for l in raw.split("\n") if gp.runes_to_indices(l)]
        lens = [len(gp.runes_to_indices(l)) for l in lines]
        if not lens:
            continue
        med = statistics.median(lens)
        marks = "".join(ch for ch in raw if ch in "&$§")
        flag = ""
        if lens[0] < 0.7 * med:
            flag = "SHORT-FIRST-LINE"
            short.append((si, lens[0], gp.indices_to_translit(
                gp.runes_to_indices(lines[0]))))
        print(f"  seg{si:<3d} lines={len(lens):2d} median={med:5.1f} first={lens[0]:3d} "
              f"marks={marks!r:8s} {flag}")
    print("\nsegments with a short first line:", short)
    print("""
READING:
  * The solved keyed pages DO carry a set-apart title line: 03.jpg = 7 runes (WELCOME),
    14.jpg = 5 runes (A KOAN), 05.jpg = 10 runes (SOME WISDOM, plaintext).
  * Across the 55 unsolved LP2 segments exactly ONE has a short first line: seg 15, 9 runes,
    and it is a TRAILER not a header -- it is followed by the '&' then '$' ornament pair, i.e.
    it closes the passage that began on seg 14.  Every other unsolved segment opens with a
    full-width ~22-rune line.
  * LP2 therefore does NOT use a set-apart header line.  Its one readable page (seg 56) shows
    the LP2 convention instead: the title is INLINE and terminated by '.'  ('PARABLE.LIKE THE
    INSTAR TUNNELING TO THE SURFACE...').  That is why T1/T1b crib at every sentence start and
    every ornament boundary rather than at line starts.
  * '&' (18 occurrences) and '$' (9) are the ornament/section marks; '§' (1) closes seg 56.
""")


if __name__ == "__main__":
    main()
