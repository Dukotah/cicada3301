"""Completeness pass: run the two genuinely-untested catalogued NUMERIC keys as
polyalphabetic shifts over the runes, so the write-up can honestly say every
sourceable numeric lead was executed.

  1. 2012 Mayan rotation key  10 2 14 7 19 6 18 12 7 8 17 0 19  (proposed in
     Campaign VI, never run; per-char polyalphabetic rotation, cross-round reuse)
  2. 2012 end-of-puzzle P.S. digit string (armada test9 was a hollow -99 sentinel)

Prime-gap / totient streams already tested (best -6.81, KEY-HINT-RESEARCH.md);
telnet & trailing-space-prime leads have no local source. Same harness/scorer as
keytest.py; expectation is NULL (Mayan period-13 is contradicted by flat
autocorrelation at lags 2-30), run for the record.
"""
import os, sys
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp, ciphers, score as _score
from run_stats import load_pages, english_baseline

N = gp.N; SC = _score.default(); THRESHOLD = -5.2

MAYAN = [10,2,14,7,19,6,18,12,7,8,17,0,19]
PS = ("1041279065891998535982789873959431895640"
      "442510695567564373922695237268242385295908173"
      "9834390370374475764863415203423499357108713631")

def translit(idxs): return gp.indices_to_translit(idxs)

# candidate numeric keystreams (all reduced mod 29)
def candidates():
    yield "mayan", [x % N for x in MAYAN]
    yield "mayan-rev", [x % N for x in MAYAN][::-1]
    yield "ps-digits", [int(c) % N for c in PS]                       # each digit 0-9
    yield "ps-digits-rev", [int(c) % N for c in PS][::-1]
    yield "ps-pairs", [int(PS[i:i+2]) % N for i in range(0, len(PS)-1, 2)]  # 2-digit groups

pages = load_pages(); unsolved = pages[:-2]
corpus = [i for p in unsolved for i in p]
print(f"=== calibration ===  english {SC.score_norm(translit(english_baseline())):.3f}  THRESHOLD {THRESHOLD}")

def decrypt(idxs, key, offset, sign, atbash):
    L = len(idxs)
    stream = [key[(offset + i) % len(key)] for i in range(L)]
    src = ciphers.atbash_indices(idxs) if atbash else idxs
    return ciphers.apply_stream_to_indices(src, stream, sign=sign)

results = []
def run_target(tname, idxs, sweep):
    for kname, key in candidates():
        offs = range(min(len(key), 128)) if sweep else [0]
        for sign in (-1, +1):
            for atbash in (False, True):
                for off in offs:
                    p = decrypt(idxs, key, off, sign, atbash)
                    sc = SC.score_norm(translit(p))
                    results.append((sc, tname, f"{kname} sign{sign:+d}{' atbash' if atbash else ''} off{off}"))

for pi, p in enumerate(unsolved):
    run_target(f"page{pi}(len{len(p)})", p, sweep=(len(p) <= 400))
run_target("CORPUS", corpus, sweep=False)

results.sort(reverse=True)
print("\n=== TOP 15 (score_norm) ===")
for sc, t, m in results[:15]:
    print(f"  {sc:7.3f}  {t:16s}  {m}{'  <-- HIT' if sc > THRESHOLD else ''}")
hits = [r for r in results if r[0] > THRESHOLD]
print(f"\nconfigs: {len(results)}   above THRESHOLD: {len(hits)}")
print("VERDICT:", "BREAK - investigate" if hits else "documented null (Mayan + P.S. digit string, both signs/atbash/offsets, per-page + corpus)")
