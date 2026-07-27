"""KEY-TEST: T1-onion3-5x5-rune-outguess payload as KEY/PAD/CIPHERTEXT vs LP2 runes.

Payload = 1498-byte PGP SIGNED MESSAGE (the public "3301" RSA block, GnuPG sig).
Known-public, not novel -- but tested for the record as additive/Beaufort/atbash
key material and XOR-class over the runes.

Reuses the VERIFIED rig: same imports + same calibrated scorer as
analysis/pp49_51/keytest.py  (score_norm: ~-2.2 English, -4.0 baseline, <-5.2 noise).
Key derivations tried:
  raw    - all 1498 bytes mod 29
  print  - printable bytes only mod 29
  b64    - base64-decoded OAEP ciphertext bytes mod 29 (the "compressed RSA" blob)
Each: forward + reversed; additive both signs; Beaufort; atbash-src;
per-page offset sweep on SHORT pages (<=400) + whole-corpus offset0; plus XOR mod 29.
"""
import os, sys, base64, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp, ciphers, score as _score
from run_stats import load_pages, english_baseline

N = gp.N
SC = _score.default()
THRESHOLD = -5.2
ENGLISH_BASELINE = -4.0

raw = open(os.path.join(HERE, "extracts", "T1-onion3-5x5-rune-outguess.bin"), "rb").read()
raw_bytes = list(raw)
print_bytes = [b for b in raw_bytes if 32 <= b < 127]

# derive the base64 OAEP ciphertext blob and decode it
txt = raw.decode("latin-1")
m = re.search(r"Scheme: Crypt::RSA::ES::OAEP\s*\n\s*\n(.*?)\n-----END", txt, re.S)
b64_bytes = []
if m:
    blob = re.sub(r"\s+", "", m.group(1))
    blob += "=" * ((4 - len(blob) % 4) % 4)          # fix base64 padding
    try:
        b64_bytes = list(base64.b64decode(blob))
    except Exception as e:
        print("b64 decode failed:", e)
print(f"payload sizes -> raw:{len(raw_bytes)} print:{len(print_bytes)} b64-cipher:{len(b64_bytes)}")

def translit(idxs):
    return gp.indices_to_translit(idxs)

# --- calibration anchors ---
pages = load_pages()
print("=== calibration (score_norm) ===")
print(f"  english baseline : {SC.score_norm(translit(english_baseline())):.3f}")
import random
rng = random.Random(3301)
rand_idx = [rng.randrange(N) for _ in range(6000)]
print(f"  random runes     : {SC.score_norm(translit(rand_idx)):.3f}  (noise floor)")
print(f"  ENGLISH_BASELINE cmp = {ENGLISH_BASELINE}   THRESHOLD = {THRESHOLD}\n")

unsolved = pages[:-2]
corpus = [i for p in unsolved for i in p]
print(f"unsolved pages: {len(unsolved)}   total runes: {len(corpus)}\n")

def key_streams():
    for kname, pl in [("raw", raw_bytes), ("print", print_bytes), ("b64cipher", b64_bytes)]:
        if not pl:
            continue
        base = [b % N for b in pl]
        yield kname, base
        yield f"{kname}-rev", base[::-1]

def decrypt(idxs, key, offset, sign, atbash, beaufort, xor):
    L = len(idxs)
    stream = [key[(offset + i) % len(key)] for i in range(L)]
    src = ciphers.atbash_indices(idxs) if atbash else idxs
    if xor:                                  # p = (c XOR k) mod 29  (bytewise xor then reduce)
        return [((c ^ stream[i]) % N) for i, c in enumerate(src)]
    if beaufort:                             # p = k - c
        return [(stream[i] - c) % N for i, c in enumerate(src)]
    return ciphers.apply_stream_to_indices(src, stream, sign=sign)

results = []
def run_target(tname, idxs, sweep_offsets):
    for kname, key in key_streams():
        offsets = range(min(len(key), 300)) if sweep_offsets else [0]
        for sign in (-1, +1):
            for atbash in (False, True):
                for mode_flag in ("add", "beaufort", "xor"):
                    beaufort = mode_flag == "beaufort"
                    xor = mode_flag == "xor"
                    if beaufort and sign == +1:      # beaufort ignores sign; dedupe
                        continue
                    if xor and sign == +1:           # xor ignores sign; dedupe
                        continue
                    for off in offsets:
                        p = decrypt(idxs, key, off, sign, atbash, beaufort, xor)
                        sc = SC.score_norm(translit(p))
                        desc = f"{kname} sign{sign:+d}{' atbash' if atbash else ''} {mode_flag} off{off}"
                        results.append((sc, tname, desc))

for pi, p in enumerate(unsolved):
    run_target(f"page{pi}(len{len(p)})", p, sweep_offsets=(len(p) <= 400))
run_target("CORPUS", corpus, sweep_offsets=False)

results.sort(reverse=True)
print("=== TOP 30 (score_norm, higher=more English) ===")
for sc, tname, mode in results[:30]:
    flag = ""
    if sc > ENGLISH_BASELINE:
        flag = "  <== BEATS ENGLISH BASELINE"
    elif sc > THRESHOLD:
        flag = "  <- above noise threshold"
    print(f"  {sc:7.3f}  {tname:18s}  {mode}{flag}")

beat_eng = [r for r in results if r[0] > ENGLISH_BASELINE]
above_thr = [r for r in results if r[0] > THRESHOLD]
print(f"\nconfigs tried: {len(results)}")
print(f"above THRESHOLD({THRESHOLD}): {len(above_thr)}")
print(f"beats ENGLISH_BASELINE({ENGLISH_BASELINE}): {len(beat_eng)}")

if beat_eng:
    best = beat_eng[0]
    print(f"\nBEST: {best[0]:.3f}  {best[1]}  {best[2]}")
    # show plaintext of the single best config for eyeballing
print("\nVERDICT:", "INVESTIGATE" if beat_eng else "documented null")
