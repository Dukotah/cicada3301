"""FRONT D1 red-team — test B-16's decisive question directly.

B-16 (RECON-B, Round 10) flagged a possible circularity in the keytext closure:
  - Campaign X/XI PIN the mechanism as a SOFT ANTI-REPEAT REWRITE of the OUTPUT
    (`soft_norepeat_pad`: when a doublet would occur, RESAMPLE the ciphertext rune
    at the SAME position; the key does NOT advance / desync).
  - Campaign XVIII BUILT + VALIDATED its beam decoder against a different mechanism:
    KEY-SKIP (`encipher_keyskip`: when a doublet would occur, ADVANCE the key index;
    the key DESYNCS). The decoder tracks that desync.

Both mechanisms reproduce the doublet deficit (0.66%) AND flat IoC (1.00) — they are
observationally near-identical on ciphertext statistics. But they corrupt a running-key
decode DIFFERENTLY:
  - SKIP: key desyncs after ~1/35 runes; beam re-aligns -> recovers English.
  - REWRITE: ~2.8% of ciphertext positions are random garbage, key stays SYNCED; there
    is nothing for the SKIP-beam to re-align. A rewrite is a substitution error, not a
    desync.

If the *correct* running key, enciphered under the REWRITE model, does NOT decode to the
English band under the EXISTING validated beam decoder, then every ~200-text keytext null
in the repo is UNSOUND the same way rigid alignment was shown unsound in Campaign XVIII —
and the keytext lane REOPENS under a rewrite-tolerant decoder.

POSITIVE CONTROL: the SKIP arm must recover English (proves the machinery works on the
mechanism it was built for). Then the REWRITE arm is the real test.

Run: PYTHONUTF8=1 python3 rewrite_gate.py
"""
import os, sys, random, json, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))
from lp import gematria as gp, score as sc                      # noqa
from skipdecode import eng_to_idx, idx_to_trans, encipher_keyskip, beam_decode, rigid_decode  # noqa

N = gp.N
Q = sc.default()

def load(name):
    return open(os.path.join(ROOT, "data", "keys", name), encoding="utf-8", errors="ignore").read()

# ---------------------------------------------------------- the two encipher models
def encipher_rewrite(P, K, sign=-1, supp=0.83, seed=3301):
    """B-16 model. Encipher plaintext P under running key K, key SYNCED 1:1 (no skip).
    When the emitted rune would double the previous, with prob `supp` REWRITE the
    ciphertext rune to a random different value (soft anti-repeat rewrite of OUTPUT).
    Returns (C, n_rewrites)."""
    rng = random.Random(seed)
    C, nrw, c_prev = [], 0, None
    for i, p in enumerate(P):
        c = (p - sign * K[i]) % N              # invert p = c + sign*k, KEY SYNCED to i
        if c_prev is not None and c == c_prev and rng.random() < supp:
            # rewrite to a random rune != c_prev (soft anti-repeat on the output)
            alt = rng.randrange(N - 1)
            if alt >= c_prev:
                alt += 1
            c = alt
            nrw += 1
        C.append(c); c_prev = c
    return C, nrw

# ------------------------------------------------------------------- the experiment
def run():
    plain = ("BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE "
             "KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK "
             "OR THE MESSAGE WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED THE "
             "INSTAR EMERGES AND THE PILGRIM WALKS THE PATH OF THE CIRCUMFERENCE UNTO THE END")
    P = eng_to_idx(plain)
    keytexts = ["mabinogion.txt", "king_in_yellow.txt", "agrippa.txt", "book_of_the_law.txt"]
    offsets = (137, 4096)
    results = {"skip": [], "rewrite": [], "rewrite_rigid": []}
    ENGLISH_BAND = -5.2   # project confirm threshold; genuine English -4.0..-4.35

    print("=" * 78)
    print("FRONT D1 — B-16 REWRITE-model robustness of the Campaign XVIII beam decoder")
    print("=" * 78)
    print(f"plaintext runes: {len(P)}   scale: English ~-4.0..-4.35 | thresh -5.2 | noise ~-7.5\n")

    print("--- ARM 1 (POSITIVE CONTROL): SKIP model, correct key, EXISTING beam decoder ---")
    for kt in keytexts:
        K = eng_to_idx(load(kt))
        for o in offsets:
            C, skips, _ = encipher_keyskip(P, K[o:], sign=-1, supp=0.83, seed=o + 7)
            dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / (len(C) - 1)
            bd = beam_decode(C, K, sign=-1, o=o, beam_w=600, max_skip=3)
            m = sum(a == b for a, b in zip(bd['plain_idx'], P)) / len(P)
            results["skip"].append(bd['score'])
            print(f"  {kt:20s} o={o:5d} skips={sum(skips):2d} dbl={dbl*100:4.2f}%  "
                  f"beam={bd['score']:6.3f}  match={m*100:5.1f}%")

    print("\n--- ARM 2 (THE TEST): REWRITE model, correct key, SAME beam decoder ---")
    for kt in keytexts:
        K = eng_to_idx(load(kt))
        for o in offsets:
            C, nrw = encipher_rewrite(P, K[o:], sign=-1, supp=0.83, seed=o + 7)
            dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / (len(C) - 1)
            bd = beam_decode(C, K, sign=-1, o=o, beam_w=600, max_skip=3)
            m = sum(a == b for a, b in zip(bd['plain_idx'], P)) / len(P)
            rd = rigid_decode(C, K, sign=-1, o=o)   # plain 1:1, no skip logic
            mr = sum(a == b for a, b in zip(rd['plain_idx'], P)) / len(P)
            results["rewrite"].append(bd['score'])
            results["rewrite_rigid"].append(rd['score'])
            print(f"  {kt:20s} o={o:5d} rewr={nrw:2d} dbl={dbl*100:4.2f}%  "
                  f"beam={bd['score']:6.3f}(m{m*100:4.0f}%)  rigid={rd['score']:6.3f}(m{mr*100:4.0f}%)")

    print("\n" + "-" * 78)
    skip_min = min(results["skip"]); rw_max = max(results["rewrite"]); rwr_max = max(results["rewrite_rigid"])
    print(f"SKIP arm (control): min beam score = {skip_min:.3f}  "
          f"(need < -5.0 to be 'English band' recovered)")
    print(f"REWRITE arm beam:   best (max) score = {rw_max:.3f}")
    print(f"REWRITE arm rigid:  best (max) score = {rwr_max:.3f}")

    control_ok = skip_min > -5.0          # control recovered English
    rewrite_recovered = rw_max > ENGLISH_BAND
    print("\nCONTROL (skip recovers English):", "PASS" if control_ok else "FAIL")
    if not control_ok:
        print("  -> machinery broken; verdict INCONCLUSIVE")
    else:
        if rewrite_recovered:
            print("REWRITE arm: correct key STILL recovers English -> coverage assumption VERIFIED;")
            print("  the keytext closure is sound (reword 'by mechanism' -> 'by exhaustion'). NO reopener.")
        else:
            print("REWRITE arm: correct key does NOT reach the English band under the beam decoder.")
            print("  -> B-16 CONFIRMED: the ~200-text keytext nulls do NOT cover the pinned REWRITE")
            print("     mechanism. The keytext lane REOPENS under a rewrite-tolerant decoder.")
    out = {"skip_scores": results["skip"], "rewrite_beam": results["rewrite"],
           "rewrite_rigid": results["rewrite_rigid"], "skip_min": skip_min,
           "rewrite_beam_max": rw_max, "rewrite_rigid_max": rwr_max,
           "control_ok": control_ok, "rewrite_recovered": rewrite_recovered,
           "english_band_threshold": ENGLISH_BAND}
    json.dump(out, open(os.path.join(HERE, "rewrite_gate_results.json"), "w"), indent=2)
    return out

if __name__ == "__main__":
    run()
