"""Key-test for T2-2jpg-seed38370-blob: the 7524-byte high-entropy blob extracted
from the 2-jpg OutGuess seed-38370 chain. Entropy 7.978, no magic header, no
compression/base64 structure -- statistically indistinguishable from random. We
test it as KEY / PAD / CIPHERTEXT material over the LP2 runes using the SAME
verified harness + calibrated scorer as pp49_51/keytest.py.

score_norm anchors: english ~ -2.2 (translit) ... english_baseline() = -4.006
here, random runes = noise floor, THRESHOLD -5.2. A real break must clearly beat
the -4.0 English baseline with readable plaintext.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp, ciphers, score as _score
from run_stats import load_pages, english_baseline
import random

N = gp.N               # 29
SC = _score.default()
THRESHOLD = -5.2
ENGLISH = -4.0         # baseline to beat

payload = list(open(os.path.join(HERE, "extracts", "T2.bin"), "rb").read())
print(f"payload bytes: {len(payload)}")

def translit(idxs): return gp.indices_to_translit(idxs)

# --- calibration anchors ---
pages = load_pages()
print("=== calibration (score_norm) ===")
print(f"  english baseline : {SC.score_norm(translit(english_baseline())):.3f}")
rng = random.Random(3301)
rand_idx = [rng.randrange(N) for _ in range(6000)]
print(f"  random runes     : {SC.score_norm(translit(rand_idx)):.3f}")
print(f"  THRESHOLD        : {THRESHOLD}   ENGLISH-to-beat: {ENGLISH}\n")

unsolved = pages[:-2]
corpus = [i for p in unsolved for i in p]
print(f"unsolved pages: {len(unsolved)}   total runes: {len(corpus)}\n")

# ---- key streams derived from payload ----
base = [b % N for b in payload]           # bytes mod 29 -> rune-index keystream
def key_streams():
    yield "modN", base
    yield "modN-rev", base[::-1]

# also XOR-class: XOR raw bytes then map mod 29 -- for CIPHERTEXT-material test we
# instead treat payload bytes themselves as a ciphertext byte->rune not meaningful;
# XOR is applied at byte level below in a separate battery.

def decrypt(idxs, key, offset, sign, atbash, beaufort):
    L = len(idxs)
    stream = [key[(offset + i) % len(key)] for i in range(L)]
    src = ciphers.atbash_indices(idxs) if atbash else idxs
    if beaufort:                       # p = k - c
        return [(stream[i] - c) % N for i, c in enumerate(src)]
    return ciphers.apply_stream_to_indices(src, stream, sign=sign)

results = []
def run_target(tname, idxs, sweep_offsets):
    # cap offset sweep at len(payload) but that's 7524; for short pages sweep a
    # generous window, for long pages just offset 0 (additive is doublet-excluded
    # corpus-wide anyway).
    if sweep_offsets:
        offsets = range(0, len(base))          # full sweep on short pages
    else:
        offsets = [0]
    for kname, key in key_streams():
        for sign in (-1, +1):
            for atbash in (False, True):
                for beaufort in (False, True):
                    if beaufort and sign == +1:   # beaufort ignores sign
                        continue
                    for off in offsets:
                        p = decrypt(idxs, key, off, sign, atbash, beaufort)
                        sc = SC.score_norm(translit(p))
                        mode = (f"{kname} sign{sign:+d}"
                                f"{' atbash' if atbash else ''}"
                                f"{' beaufort' if beaufort else ''} off{off}")
                        results.append((sc, tname, mode))

# per-page: full offset sweep on SHORT pages (<=160 runes -> real short-page set),
# offset0 on long. Whole corpus offset0.
SHORT = 160
for pi, p in enumerate(unsolved):
    run_target(f"page{pi}(len{len(p)})", p, sweep_offsets=(len(p) <= SHORT))
run_target("CORPUS", corpus, sweep_offsets=False)

results.sort(reverse=True)
print("=== TOP 30 (score_norm, higher = more English) ===")
for sc, tname, mode in results[:30]:
    flag = ""
    if sc > ENGLISH:   flag = "  <== BEATS ENGLISH"
    elif sc > THRESHOLD: flag = "  <-- above noise threshold"
    print(f"  {sc:7.3f}  {tname:18s}  {mode}{flag}")

above_eng = [r for r in results if r[0] > ENGLISH]
above_thr = [r for r in results if r[0] > THRESHOLD]
print(f"\nconfigs tried: {len(results)}")
print(f"above THRESHOLD({THRESHOLD}): {len(above_thr)}   beats ENGLISH({ENGLISH}): {len(above_eng)}")

# show plaintext of the single best config for eyeball readability check
best = results[0]
bsc, btn, bmode = best
print(f"\nBEST: {bsc:.3f}  {btn}  {bmode}")
