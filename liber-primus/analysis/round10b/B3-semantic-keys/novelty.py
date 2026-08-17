"""Novelty accounting: how much of the B3 expanded key set was ALREADY tested?

Compared as RUNE-INDEX TUPLES, not Latin strings -- the whole claim of this lane is that the
same Latin word maps to several different rune keys and prior sweeps tested exactly one.
"""
import os
import re
import sys

import b3lib
from b3lib import gp

ROOT = b3lib.ROOT


def prior_latin_words():
    words = set()
    # 1. the ~620-keyword skip-aware sweep list
    p = os.path.join(ROOT, "analysis", "campaign18_skip", "armada2", "keywords_skip.py")
    src = open(p, encoding="utf-8").read()
    for m in re.finditer(r'"([A-Z]{2,})"', src):
        words.add(m.group(1))
    # 2. the repo key lists
    for f in ("thematic.txt", "words_expanded.txt"):
        fp = os.path.join(ROOT, "data", "keys", f)
        if os.path.exists(fp):
            for ln in open(fp, encoding="utf-8"):
                w = ln.strip().upper()
                if w.isalpha():
                    words.add(w)
    # 3. armada-20 crib-drag cribs
    p = os.path.join(ROOT, "analysis", "armada20", "cribdrag.py")
    if os.path.exists(p):
        src = open(p, encoding="utf-8").read()
        m = re.search(r"CRIBS\s*=\s*\[(.*?)\]", src, re.S)
        if m:
            for w in re.finditer(r'"([A-Z]+)"', m.group(1)):
                words.add(w.group(1))
    return words


def main():
    prior_words = prior_latin_words()
    prior_tuples = set()
    for w in prior_words:
        try:
            prior_tuples.add(tuple(gp.keyword_to_indices(w)))
        except ValueError:
            pass
    # the recon LP1-H run explicitly hand-typed the C->F form of two words
    for w in ("FIRFUMFERENFE",):
        prior_tuples.add(tuple(gp.keyword_to_indices(w)))

    mine = b3lib.expanded_keys()
    mine_tuples = {t for _, _, t in mine}
    overlap = mine_tuples & prior_tuples
    print(f"prior Latin words harvested        : {len(prior_words)}")
    print(f"prior rune-key tuples (greedy parse): {len(prior_tuples)}")
    print(f"B3 expanded rune-key tuples        : {len(mine_tuples)}")
    print(f"overlap                            : {len(overlap)}")
    print(f"NOVEL FRACTION                     : "
          f"{100.0*(len(mine_tuples)-len(overlap))/len(mine_tuples):.1f}% "
          f"({len(mine_tuples)-len(overlap)}/{len(mine_tuples)})")
    # how much of the novelty is pure orthography (same Latin word, different rune spelling)?
    latin_prior = {w for w in prior_words}
    same_word_new_spelling = 0
    for lat, grp, t in mine:
        if t not in prior_tuples and lat in latin_prior:
            same_word_new_spelling += 1
    print(f"  of which SAME Latin word, NEW rune spelling: {same_word_new_spelling}")
    print(f"  of which new Latin word entirely           : "
          f"{len(mine_tuples)-len(overlap)-same_word_new_spelling}")


if __name__ == "__main__":
    main()
