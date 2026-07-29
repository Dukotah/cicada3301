"""i7 PAD-RESTORATION ORACLE — validation + generator sweep (plaintext-BLIND).

Uses a LARGE-N doubling-ratio oracle (the only regime where the statistic is
stable). Validation vehicle: synthetic English-in-runes (quadgram-Markov,
committed model) enciphered with a KNOWN generator, then confirm the oracle
recovers the English-band doubling ratio when the RIGHT keystream is subtracted,
and NOT for wrong keystreams. Then sweep the Cicada generator family against the
real 0-54 ciphertext and report whether ANY generator diagnostically moves the
residual doubling ratio toward the English band beating controls.
"""
import os, sys, random, math
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp, ciphers
from run_stats import english_baseline

N = gp.N
KRIS = os.path.join(ROOT, "data", "krisyotam_runes.txt")
OUT = os.path.join(HERE, "RESULTS.txt")
LOG = []
def out(s=""):
    print(s); LOG.append(s)

def load_pages_raw():
    return [s for s in open(KRIS, encoding="utf-8").read().split("%")
            if gp.runes_to_indices(s)]
PAGES_RAW = load_pages_raw()
PAGES_IDX = [gp.runes_to_indices(s) for s in PAGES_RAW]
UNSOLVED_PAGES = PAGES_IDX[:55]
CORPUS = [i for p in UNSOLVED_PAGES for i in p]      # pages 0-54, 12,956 runes
PARABLE = PAGES_IDX[56]

# --------- doubling ratio (PRIMARY blind metric; large-N stable)
def dbl(seq):
    if len(seq) < 2: return float("nan")
    eq = sum(1 for a, b in zip(seq, seq[1:]) if a == b)
    return (eq / (len(seq) - 1)) / (1.0 / N)

# --------- legal-bigram plausibility (secondary; PARABLE-learned)
LEGAL = {(a, b) for a, b in zip(PARABLE, PARABLE[1:])}
def plaus(seq):
    if len(seq) < 2: return float("nan")
    return sum(1 for a, b in zip(seq, seq[1:]) if (a, b) in LEGAL) / (len(seq) - 1)

rng = random.Random(3301)
def rnd(n): return [rng.randrange(N) for _ in range(n)]

# ============ GENERATOR FAMILY (the streams Cicada demonstrates) ============
def gen_prime(L, start=0):        return ciphers.prime_stream(L, start)
def gen_totient(L, start=2):      return ciphers.totient_stream(L, start)
def gen_phi_prime(L, start=0):    return ciphers.prime_totient_stream(L, start)  # (p-1)mod29 = AN-END gen
def gen_fib(L, start=0):
    a, b = 1, 1
    for _ in range(start): a, b = b, a + b
    out = []
    while len(out) < L:
        out.append(a % N); a, b = b, a + b
    return out
def gen_golden(L, start=0):
    phi = (1 + 5 ** 0.5) / 2
    return [int(math.floor(((i + start + 1) * phi) % 1 * N)) % N for i in range(L)]

GENERATORS = {
    "prime(n)":        gen_prime,
    "totient(n)":      gen_totient,
    "phi(prime)=AN-END": gen_phi_prime,
    "fibonacci":       gen_fib,
    "golden":          gen_golden,
}

def apply_stream(idxs, K, mode):
    """mode: 'sub' (C-K), 'add' (C+K), 'beau' (K-C)."""
    if mode == "sub":  return [(c - K[i]) % N for i, c in enumerate(idxs)]
    if mode == "add":  return [(c + K[i]) % N for i, c in enumerate(idxs)]
    return [(K[i] - c) % N for i, c in enumerate(idxs)]

# ================================ VALIDATION ================================
out("="*70)
out("VALIDATION: synthetic English-in-runes, known keystream, oracle recovery")
out("="*70)
ENG = english_baseline()[:12956]     # match 0-54 length
out(f"synthetic English-in-runes: {len(ENG)} runes  D={dbl(ENG):.3f}  P={plaus(ENG):.3f}")
# encipher with phi(prime) (AN-END generator), sub direction: C = P + K
Kfull = gen_phi_prime(len(ENG))
CT = [(p + Kfull[i]) % N for i, p in enumerate(ENG)]
out(f"enciphered CT (P+phi):        D={dbl(CT):.3f}  P={plaus(CT):.3f}")
# oracle recovery: subtract RIGHT keystream vs WRONG keystreams
out("\n  subtract keystream -> residual doubling ratio (English band ~0.5-0.7):")
recov = apply_stream(CT, Kfull, "sub")
out(f"    CORRECT phi(prime)   D={dbl(recov):.3f}  P={plaus(recov):.3f}  <- should match English")
val_pass_marks = []
for name in ("prime(n)", "totient(n)", "fibonacci", "golden"):
    Kw = GENERATORS[name](len(ENG))
    r = apply_stream(CT, Kw, "sub")
    out(f"    WRONG {name:14s} D={dbl(r):.3f}  P={plaus(r):.3f}")
    val_pass_marks.append(dbl(r))
Krand = rnd(len(ENG)); r = apply_stream(CT, Krand, "sub")
out(f"    WRONG random         D={dbl(r):.3f}  P={plaus(r):.3f}")
val_pass_marks.append(dbl(r))
GATE_D_correct = dbl(recov)
GATE_P_correct = plaus(recov)
# Correct recovery must match English on BOTH metrics; the discriminating metric
# is bigram plausibility P (D alone can coincide for a wrong stream). Oracle is
# validated iff correct recovers English D AND English-level P, while EVERY wrong
# keystream fails the P test (near the ~0.09 random floor).
wrong_ps = []
for name in ("prime(n)", "totient(n)", "fibonacci", "golden"):
    Kw = GENERATORS[name](len(ENG))
    wrong_ps.append(plaus(apply_stream(CT, Kw, "sub")))
wrong_ps.append(plaus(apply_stream(CT, Krand, "sub")))
GATE = (abs(GATE_D_correct - dbl(ENG)) < 0.05) and (GATE_P_correct > 0.30) \
       and all(p < 0.15 for p in wrong_ps)
out(f"\n  correct recovery: D={GATE_D_correct:.3f}~English({dbl(ENG):.3f}) "
    f"P={GATE_P_correct:.3f}")
out(f"  wrong-keystream P values: {[round(p,3) for p in wrong_ps]} (all <0.15 = fail)")
out(f"  ORACLE_VALIDATED = {GATE}  "
    f"(correct recovers English D AND P; every wrong keystream fails P)")

# ================================ SWEEP ================================
out("\n" + "="*70)
out("SWEEP: Cicada generator family vs REAL pages 0-54 ciphertext")
out("="*70)
out(f"REAL 0-54 raw ciphertext:     D={dbl(CORPUS):.3f}  P={plaus(CORPUS):.3f}  (baseline)")
out(f"English target band:          D~{dbl(ENG):.3f} (quadgram)  / 0.31 (PARABLE)")
out(f"Random-keystream control band D~1.0")
out("")
# For each generator x mode x (offset/stride) sweep, subtract from CORPUS and
# measure residual doubling ratio. restoration = residual D moves toward English
# band (i.e. UP toward ~0.3-0.7 AND above the raw 0.19 baseline meaningfully),
# beating what a random keystream does.
BASE = dbl(CORPUS)
best = []
OFFSETS = list(range(0, 40))
STRIDES = [1, 2, 3]
for gname, gfn in GENERATORS.items():
    # base long stream (with headroom for offset/stride)
    Lmax = len(CORPUS) * max(STRIDES) + max(OFFSETS) + 10
    base_stream = gfn(Lmax)
    for stride in STRIDES:
        for off in OFFSETS:
            K = [base_stream[off + i * stride] for i in range(len(CORPUS))]
            for mode in ("sub", "add", "beau"):
                R = apply_stream(CORPUS, K, mode)
                d = dbl(R)
                best.append((d, gname, mode, stride, off))
# random-keystream control distribution (null): what residual D looks like for
# an arbitrary deterministic-but-wrong stream
ctrl_ds = []
for s in range(30):
    rc = random.Random(1000 + s)
    K = [rc.randrange(N) for _ in range(len(CORPUS))]
    ctrl_ds.append(dbl(apply_stream(CORPUS, K, "sub")))
ctrl_mean = sum(ctrl_ds) / len(ctrl_ds)
ctrl_min = min(ctrl_ds); ctrl_max = max(ctrl_ds)
out(f"random-keystream control residual D: mean={ctrl_mean:.3f} "
    f"[{ctrl_min:.3f}..{ctrl_max:.3f}] over 30 seeds")
out("")
# restoration signal: any generator whose residual D lands clearly in the English
# band (0.25..0.75) AND is far below the control min (i.e. NOT what a random
# keystream does). NOTE raw baseline is already 0.19 (below English) — a real
# restoration would move it UP toward English, or a doublet-injecting fingerprint
# would push toward control ~1.0. We flag ONLY English-band landings.
best.sort()
out("--- lowest residual doubling ratios (most doublet-suppressed) ---")
for d, g, m, st, o in best[:8]:
    out(f"  D={d:.3f}  {g:18s} {m}  stride={st} off={o}")
# English-band candidates
eng_band = [b for b in best if 0.25 <= b[0] <= 0.75]
out(f"\nresiduals in English band (0.25-0.75): {len(eng_band)} of {len(best)} configs")
for d, g, m, st, o in sorted(eng_band)[:10]:
    out(f"  D={d:.3f}  {g:18s} {m}  stride={st} off={o}")
# a restoration must ALSO beat controls AND ideally lift plausibility
RESTORE = False
restore_detail = "no generator landed a residual in the English band below the "\
                 "random-control floor"
if eng_band:
    # check the best english-band candidate's plausibility vs control
    d, g, m, st, o = sorted(eng_band)[0]
    K = [GENERATORS[g](len(CORPUS)*max(st,1)+o+10)[o+i*st] for i in range(len(CORPUS))]
    Rr = apply_stream(CORPUS, K, m)
    pl = plaus(Rr)
    # control plausibility baseline
    ctrl_pl = plaus(apply_stream(CORPUS, [random.Random(7).randrange(N)
                    for _ in range(len(CORPUS))], "sub"))
    out(f"\n  best English-band cand: {g} {m} stride={st} off={o} "
        f"D={d:.3f} P={pl:.3f} (control P~{ctrl_pl:.3f})")
    RESTORE = (d < ctrl_min) and (pl > ctrl_pl * 1.3)
    restore_detail = f"best English-band residual D={d:.3f} P={pl:.3f} vs "\
                     f"control floor D={ctrl_min:.3f} P~{ctrl_pl:.3f}"

out(f"\nRESTORATION_SIGNAL = {RESTORE}")
out(restore_detail)
out(f"ORACLE_VALIDATED   = {GATE}")

open(OUT, "w").write("\n".join(LOG))
print(f"\nwrote {OUT}")
