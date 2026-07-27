"""T3-iso-folly-wisdom KEY-TEST.

Tests the 3368-byte high-entropy blob at extracts/T3.bin as KEY / PAD /
CIPHERTEXT material over the LP2 runes, using the VERIFIED existing rig:
same imports (lp.gematria/ciphers/score, run_stats.load_pages) and the same
calibrated quadgram scorer (score_norm: ~-2.2 English text, -4.0 English
baseline over runes, <-5.2 = noise-floor THRESHOLD).

Battery (mirrors pp49_51/keytest.py, extended):
  - bytes mod 29 -> additive (both signs) / Beaufort / atbash key
  - forward + reversed key
  - per-page offset sweep on SHORT pages (<=200 runes) + whole-corpus offset0
  - XOR-class: byte XOR then mod 29 as an alt keystream derivation
Reports best score and whether ANY config beats the -4.0 English baseline
with readable plaintext. Short-page top hits are variance, not signal.
"""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp, ciphers, score as _score
from run_stats import load_pages, english_baseline

N = gp.N
SC = _score.default()
ENGLISH = -4.0          # English baseline (task-specified pass bar)
THRESHOLD = -5.2        # rig noise-floor threshold

def translit(idxs):
    return gp.indices_to_translit(idxs)

payload = list(open(os.path.join(HERE, "extracts", "T3.bin"), "rb").read())
assert len(payload) == 3368, len(payload)

# --- calibration anchors ---
pages = load_pages()
print("=== calibration (score_norm) ===")
print(f"  english baseline : {SC.score_norm(translit(english_baseline())):.3f}  (PASS BAR {ENGLISH})")
rng = random.Random(3301)
rand_idx = [rng.randrange(N) for _ in range(6000)]
print(f"  random runes     : {SC.score_norm(translit(rand_idx)):.3f}  (noise floor)")
print(f"  THRESHOLD        : {THRESHOLD}\n")

unsolved = pages[:-2]
corpus = [i for p in unsolved for i in p]
print(f"unsolved pages: {len(unsolved)}   total runes: {len(corpus)}\n")

# --- key-stream derivations from the raw bytes ---
def key_streams():
    base = [b % N for b in payload]                 # bytes mod 29
    yield "modN", base
    yield "modN-rev", base[::-1]
    # XOR-class: rolling XOR of adjacent bytes, then mod 29 (alt whitening)
    xr = [(payload[i] ^ payload[i-1]) % N for i in range(len(payload))]
    yield "xor-roll", xr
    yield "xor-roll-rev", xr[::-1]

def decrypt(idxs, key, offset, sign, atbash, beaufort):
    L = len(idxs)
    stream = [key[(offset + i) % len(key)] for i in range(L)]
    src = ciphers.atbash_indices(idxs) if atbash else idxs
    if beaufort:                       # p = k - c
        return [(stream[i] - c) % N for i, c in enumerate(src)]
    return ciphers.apply_stream_to_indices(src, stream, sign=sign)

results = []
def run_target(tname, idxs, sweep_offsets):
    offsets = range(0, len(payload), 7) if sweep_offsets else [0]
    for kname, key in key_streams():
        for sign in (-1, +1):
            for atbash in (False, True):
                for beaufort in (False, True):
                    if beaufort and sign == +1:    # beaufort ignores sign
                        continue
                    for off in offsets:
                        p = decrypt(idxs, key, off, sign, atbash, beaufort)
                        sc = SC.score_norm(translit(p))
                        mode = (f"{kname} sign{sign:+d}"
                                f"{' atbash' if atbash else ''}"
                                f"{' beaufort' if beaufort else ''} off{off}")
                        results.append((sc, tname, mode))

# per-page: sweep offsets only on SHORT pages (<=200), offset0 on the rest
for pi, p in enumerate(unsolved):
    run_target(f"page{pi}(len{len(p)})", p, sweep_offsets=(len(p) <= 200))
# whole corpus, offset0 (additive family doublet-excluded corpus-wide; for record)
run_target("CORPUS", corpus, sweep_offsets=False)

results.sort(reverse=True)
print("=== TOP 25 decryptions (score_norm, higher=more English) ===")
for sc, tname, mode in results[:25]:
    flag = ""
    if sc > ENGLISH:
        flag = "  <== BEATS ENGLISH"
    elif sc > THRESHOLD:
        flag = "  <- above noise threshold"
    print(f"  {sc:7.3f}  {tname:16s}  {mode}{flag}")

best = results[0]
above_eng = [r for r in results if r[0] > ENGLISH]
above_thr = [r for r in results if r[0] > THRESHOLD]
print(f"\nconfigs tried: {len(results)}")
print(f"above ENGLISH({ENGLISH}): {len(above_eng)}   above THRESHOLD({THRESHOLD}): {len(above_thr)}")
print(f"BEST: {best[0]:.3f}  {best[1]}  {best[2]}")

# show plaintext head of best config for a readability eyeball
def best_plain_head():
    sc, tname, mode = best
    return None
print("\nVERDICT:", "INVESTIGATE - beats English baseline" if above_eng
      else "documented null (no config beats the -4.0 English baseline; "
           "top hits are short-page variance at/below noise floor)")
