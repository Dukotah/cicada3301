"""i7 GAME-THEORIST — PAD-RESTORATION ORACLE (plaintext-BLIND).

Hypothesis: pages 0-54's pad is a DETERMINISTIC generator seeded by a value the
solved pages already teach (Cicada is a recruiter; keys are self-contained &
derivable from published constants). Prior lanes scored ENGLISH and were defeated
by interrupter/skip desync. This lane uses a PLAINTEXT-BLIND objective so a
near-correct pad is detectable WITHOUT a language model.

BLIND OBJECTIVE on residual R = decrypt(C, K):
  1. doubling ratio D = observed_adjacent_equal / (1/29)   [PRIMARY, model-free]
       English-in-futhorc ~0.3 (PARABLE) .. 0.19 (0-54 baseline) ; random ~1.0
  2. bigram plausibility P = fraction of R's adjacent pairs in a LEGAL bigram set
     learned ONLY from the PARABLE plaintext page (held out from the AN-END test).
       English high ; random ~0.155 floor

VALIDATION GATE (abort sweep if fail): subtract the KNOWN AN-END phi(prime)
keystream from the KNOWN AN-END ciphertext, isolate the interrupter-free CLEAN
PREFIX, and confirm the oracle recovers English-band D + high P there, while a
WRONG keystream on the same ciphertext gives D~1.0 / low P.
"""
import os, sys, random
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp, ciphers

N = gp.N
KRIS = os.path.join(ROOT, "data", "krisyotam_runes.txt")

def load_pages_raw():
    segs = open(KRIS, encoding="utf-8").read().split("%")
    return [s for s in segs if gp.runes_to_indices(s)]

PAGES_RAW = load_pages_raw()
PAGES_IDX = [gp.runes_to_indices(s) for s in PAGES_RAW]
UNSOLVED = PAGES_IDX[:55]                     # pages 0-54
ANEND_RAW = PAGES_RAW[55]
ANEND_IDX = PAGES_IDX[55]
PARABLE_IDX = PAGES_IDX[56]                   # plaintext English-in-runes (ground truth)
CORPUS_0_54 = [i for p in UNSOLVED for i in p]

# ---- LEGAL bigram set: learned ONLY from PARABLE (held out from AN-END gate)
def learn_legal_bigrams(seq):
    return {(a, b) for a, b in zip(seq, seq[1:])}
LEGAL = learn_legal_bigrams(PARABLE_IDX)

def doubling_ratio(seq):
    if len(seq) < 2: return float("nan")
    eq = sum(1 for a, b in zip(seq, seq[1:]) if a == b)
    return (eq / (len(seq) - 1)) / (1.0 / N)

def bigram_plausibility(seq):
    if len(seq) < 2: return float("nan")
    hit = sum(1 for a, b in zip(seq, seq[1:]) if (a, b) in LEGAL)
    return hit / (len(seq) - 1)

def oracle(seq):
    return doubling_ratio(seq), bigram_plausibility(seq)

rng = random.Random(3301)
def random_seq(n):
    return [rng.randrange(N) for _ in range(n)]

# ============================================================ VALIDATION GATE
# Recover AN-END with the KNOWN phi(prime) keystream; the CLEAN PREFIX (before
# the first interrupter desync) is trustworthy ground-truth plaintext.
_, anend_plain = ciphers.transform_runes(
    ANEND_RAW, lambda L: ciphers.prime_totient_stream(L), sign=-1, interrupters=True)
# clean prefix = "ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGE" = first 37 recovered runes
CLEAN_N = 37
anend_clean = anend_plain[:CLEAN_N]

# For a fair blind test we score the residual R over the CLEAN region of the raw
# ciphertext. The clean region has no interrupters, so residual = (C - K).
anend_ct_clean = ANEND_IDX[:CLEAN_N]          # first 37 ciphertext runes (interrupter-free)
K_right = ciphers.prime_totient_stream(CLEAN_N)      # correct keystream
R_correct = [(c - k) % N for c, k in zip(anend_ct_clean, K_right)]

def gate():
    print("=== VALIDATION GATE (AN-END clean prefix, N=%d) ===" % CLEAN_N)
    print("clean plaintext:", gp.indices_to_translit(anend_clean))
    print("residual==plain:", R_correct == anend_clean)
    dC, pC = oracle(R_correct)
    print(f"  CORRECT keystream  D={dC:.3f}  P={pC:.3f}")
    # WRONG keystreams (controls) on the SAME ciphertext prefix
    ctrls = {
        "prime(n) mod29":  ciphers.prime_stream(CLEAN_N),
        "totient(n) mod29": ciphers.totient_stream(CLEAN_N),
        "random":          random_seq(CLEAN_N),
        "zeros(=raw CT)":   [0] * CLEAN_N,
        "phi+7 offset":    ciphers.prime_totient_stream(CLEAN_N, start=7),
    }
    worst_ctrl_D = 0.0
    for name, K in ctrls.items():
        R = [(c - k) % N for c, k in zip(anend_ct_clean, K)]
        d, p = oracle(R)
        print(f"  WRONG {name:18s} D={d:.3f}  P={p:.3f}")
        worst_ctrl_D = max(worst_ctrl_D, d)
    # gate passes if correct D is clearly in English band AND below controls
    passed = (dC < 0.55) and (pC > 0.5) and (dC < min(
        oracle([(c-k)%N for c,k in zip(anend_ct_clean, K)])[0]
        for K in ctrls.values()))
    print(f"\n  GATE {'PASS' if passed else 'FAIL'}: correct D={dC:.3f} P={pC:.3f} "
          f"in English band & beats all controls")
    return passed, dC, pC

if __name__ == "__main__":
    print(f"pages={len(PAGES_IDX)} 0-54 runes={len(CORPUS_0_54)} legal-bigrams={len(LEGAL)}\n")
    print("=== ANCHORS ===")
    for name, seq in [("PARABLE(Eng)", PARABLE_IDX),
                      ("AN-END clean plain", anend_clean),
                      ("0-54 raw CT", CORPUS_0_54),
                      ("random 5000", random_seq(5000))]:
        d, p = oracle(seq)
        print(f"  {name:20s} D={d:.3f}  P={p:.3f}")
    print()
    ok, dC, pC = gate()
