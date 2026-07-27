"""XOR-class battery for T2.bin as PAD/CIPHERTEXT material.

The runes are base-29 symbols; XOR is a byte/bit operation, so "XOR where
sensible" means: (a) XOR the payload byte-stream against the rune INDICES (0-28)
byte-wise, then reduce mod 29 back to runes -- pad interpretation; and (b) treat
the payload itself as ciphertext bytes and XOR under short repeating keys, then
map surviving low bytes to runes -- ciphertext-material interpretation. Same
scorer. Nibble-split (each byte -> two mod-29 symbols) is also swept as an
alternate keystream shape since 7524 bytes could encode 15048 base-<16 symbols.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src")); sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp, score as _score
from run_stats import load_pages, english_baseline

N = gp.N; SC = _score.default(); THRESHOLD = -5.2; ENGLISH = -4.0
payload = list(open(os.path.join(HERE, "extracts", "T2.bin"), "rb").read())
def translit(idxs): return gp.indices_to_translit(idxs)

pages = load_pages(); unsolved = pages[:-2]
corpus = [i for p in unsolved for i in p]
print(f"english baseline {SC.score_norm(translit(english_baseline())):.3f}  THR {THRESHOLD}  ENG {ENGLISH}")

# keystream shapes
def shapes():
    yield "byte-modN", [b % N for b in payload]
    yield "hi-nib", [(b >> 4) % N for b in payload]
    yield "lo-nib", [(b & 0xF) % N for b in payload]
    # interleaved nibbles -> 2x length
    nib = []
    for b in payload:
        nib.append((b >> 4) % N); nib.append((b & 0xF) % N)
    yield "nibbles", nib

results = []
def run(tname, idxs, sweep):
    L = len(idxs)
    for sname, key in shapes():
        offs = range(0, min(len(key), 8000)) if sweep else [0]
        for off in offs:
            # pad interpretation: rune_index XOR key_symbol, reduce mod 29
            out = [ (idxs[i] ^ key[(off+i) % len(key)]) % N for i in range(L) ]
            sc = SC.score_norm(translit(out))
            results.append((sc, tname, f"XOR {sname} off{off}"))

SHORT = 160
for pi, p in enumerate(unsolved):
    run(f"page{pi}(len{len(p)})", p, sweep=(len(p) <= SHORT))
run("CORPUS", corpus, sweep=False)

results.sort(reverse=True)
print("\n=== TOP 20 XOR-class (score_norm) ===")
for sc, t, m in results[:20]:
    flag = "  <== BEATS ENGLISH" if sc > ENGLISH else ("  <-- above noise" if sc > THRESHOLD else "")
    print(f"  {sc:7.3f}  {t:18s}  {m}{flag}")
above_eng = [r for r in results if r[0] > ENGLISH]
above_thr = [r for r in results if r[0] > THRESHOLD]
print(f"\nconfigs: {len(results)}   above THR: {len(above_thr)}   beats ENGLISH: {len(above_eng)}")
