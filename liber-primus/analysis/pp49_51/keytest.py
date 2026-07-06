"""Phase 3: use the pp49-51 256-byte payload as KEY MATERIAL over the runes.

Rationale: additive application of ANY plaintext-independent key over the whole
12,956-rune corpus is already doublet-excluded (Campaign IV). The live loophole
is LOCAL/per-page use, where the doublet statistic doesn't bite -- especially the
hypothesis that the token table keys the runic lines on its OWN page.

Reuses the rig's verified cipher (apply_stream_to_indices/atbash) + calibrated
quadgram scorer (score_norm: ~-2.2 English, <-4 noise, THRESHOLD -5.2).
"""
import os, sys
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp, ciphers, score as _score
from run_stats import load_pages, english_baseline

N = gp.N
SC = _score.default()
THRESHOLD = -5.2

payload_maj = list(open(os.path.join(HERE, "canon_256.bin"), "rb").read())
payload_dec = list(open(os.path.join(HERE, "canon_256_decpref.bin"), "rb").read())

def translit(idxs):
    return gp.indices_to_translit(idxs)

# --- calibration anchors ---
pages = load_pages()
solved_plain = english_baseline()
print("=== calibration (score_norm) ===")
print(f"  english baseline : {SC.score_norm(translit(solved_plain)):.3f}  (target for a real break)")
# a solved LP page (last two are AN END / PARABLE, already solved plaintext-in-runes? no,
# they are still enciphered in the file) -- use english baseline + random as anchors
import random
rng = random.Random(3301)
rand_idx = [rng.randrange(N) for _ in range(6000)]
print(f"  random runes     : {SC.score_norm(translit(rand_idx)):.3f}  (noise floor)")
print(f"  THRESHOLD        : {THRESHOLD}\n")

unsolved = pages[:-2]
print(f"unsolved pages: {len(unsolved)}  lengths: {[len(p) for p in unsolved]}")
corpus = [i for p in unsolved for i in p]
print(f"total unsolved runes: {len(corpus)}\n")

def key_streams():
    """Yield (name, keylist-of-mod29) candidates."""
    for kname, pl in [("maj", payload_maj), ("dec", payload_dec)]:
        base = [b % N for b in pl]
        yield f"{kname}", base
        yield f"{kname}-rev", base[::-1]

def decrypt(idxs, key, offset, sign, atbash, beaufort):
    L = len(idxs)
    stream = [key[(offset + i) % len(key)] for i in range(L)]
    src = ciphers.atbash_indices(idxs) if atbash else idxs
    if beaufort:                      # p = k - c
        return [(stream[i] - c) % N for i, c in enumerate(src)]
    return ciphers.apply_stream_to_indices(src, stream, sign=sign)

# --- run battery, track global leaderboard ---
results = []
def run_target(tname, idxs, sweep_offsets):
    offsets = range(len(payload_maj)) if sweep_offsets else [0]
    for kname, key in key_streams():
        for sign in (-1, +1):
            for atbash in (False, True):
                for beaufort in (False, True):
                    if beaufort and sign == +1:   # beaufort ignores sign; dedupe
                        continue
                    for off in offsets:
                        p = decrypt(idxs, key, off, sign, atbash, beaufort)
                        sc = SC.score_norm(translit(p))
                        mode = f"{kname} sign{sign:+d}{' atbash' if atbash else ''}{' beaufort' if beaufort else ''} off{off}"
                        results.append((sc, tname, mode))

# per-page (sweep offsets on short pages; offset0 on long)
for pi, p in enumerate(unsolved):
    run_target(f"page{pi}(len{len(p)})", p, sweep_offsets=(len(p) <= 400))
# whole corpus, offset 0 (additive family is doublet-excluded here -- for completeness)
run_target("CORPUS", corpus, sweep_offsets=False)

results.sort(reverse=True)
print("=== TOP 25 decryptions (score_norm, higher=more English) ===")
for sc, tname, mode in results[:25]:
    flag = "  <-- ABOVE THRESHOLD" if sc > THRESHOLD else ""
    print(f"  {sc:7.3f}  {tname:16s}  {mode}{flag}")

hits = [r for r in results if r[0] > THRESHOLD]
print(f"\ntotal configs tried: {len(results)}   above THRESHOLD({THRESHOLD}): {len(hits)}")
if not hits:
    print("VERDICT: no English emerges from the payload as an additive/Beaufort/atbash key,")
    print("per-page or corpus-wide, either canonical variant, forward or reversed. Documented null.")
