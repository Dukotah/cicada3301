#!/usr/bin/env python3
"""ADJUDICATE the henkman/liberprimus page-56 reading conflict against ground truth.

Page LP2 56 ("AN END") is SOLVED: totient keystream, key[i] = (p_i - 1) mod 29
over consecutive primes, decrypt C - K mod 29, F-rune interrupters are nulls
that do not advance the keystream.

Conflict (corpus/B-liber-primus/CONFLICT-henkman-2016.json, page_index 56):
    rune index 19   canon = U+16C9 (X)      henkman = U+16DA (L)

Both readings are decoded with the SAME method and scored.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
spec = importlib.util.spec_from_file_location(
    "rp56", os.path.join(ROOT, "analysis", "reproduce", "reproduce_page_56_an_end.py"))
rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)

CANON_RUNE, HENK_RUNE, POS = "ᛉ", "ᛚ", 19

runes = rp.runes_from_relikd("relikd_p56_an_end.txt")
assert len(runes) == 85
assert runes[POS] == CANON_RUNE, (POS, runes[POS])
henk = runes[:POS] + HENK_RUNE + runes[POS + 1:]

scorer = rp.Quadgram()
stream = [(p - 1) % rp.N for p in rp.sieve_primes(len(runes) + 8)]

EXPECT = ["ANEND", "WITHIN", "THEDEEPWEB", "THEREEXISTS", "APAGE", "HASHES",
          "ITISTHEDUTY", "EUERYPILGRIM", "SEECOUT", "THISPAGE"]

for label, r in (("canon   X (U+16C9)", runes), ("henkman L (U+16DA)", henk)):
    txt, iset = rp.decrypt_with_interrupters(r, stream, scorer, sign=-1)
    up = rp.canon(txt)
    found = [w for w in EXPECT if rp.canon(w) in up]
    print("=" * 74)
    print("reading        : %s   at rune index %d" % (label, POS))
    print("translit ctx   : ...%s..." % rp.to_translit(rp.to_indices(r))[10:30])
    print("nulls found    : %s" % iset)
    print("quadgram/char  : %+.4f" % scorer.score_norm(up))
    print("plaintext      : %s" % up)
    print("crib words     : %d/%d  -> %s" % (len(found), len(EXPECT),
          ("MISSING: " + ", ".join(w for w in EXPECT if w not in found)) if len(found) < len(EXPECT) else "all present"))

# isolate the single affected plaintext character
print("=" * 74)
for label, r in (("canon", runes), ("henkman", henk)):
    txt, _ = rp.decrypt_with_interrupters(r, stream, scorer, sign=-1)
    print("%-8s plaintext[16:26] = %s" % (label, rp.canon(txt)[16:26]))
