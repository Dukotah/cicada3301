"""B4 SUPPLEMENT — the three measurements the first pass left out.

S1  THE UNCONDITIONAL PAD THEOREM.
    If k is i.i.d. uniform over Z_29 and independent of p, then
    Dc = Dp + Dk is uniform over Z_29 for ANY plaintext distribution whatsoever,
    so P(doublet) = 1/29 = 3.448% EXACTLY -- no English assumption needed.
    Measure how far the real stream is from that, and check the escape hatch:
    could an author have reached 86 doublets by SELECTING among random pads
    rather than by constructing a filter?

S2  WHAT MUST THE PLAINTEXT LOOK LIKE for a plaintext-INDEPENDENT key to be
    possible at all?  The floor is min_d P_Dp(d).  Tabulate it across plaintext
    classes (English prose, the author's own solved LP plaintext, restricted
    alphabets, digit strings, already-enciphered text).  This converts the
    doublet deficit from a negative result into a POSITIVE constraint on the
    plaintext, and hands lane B6 a target.

S3  IS THE RESIDUE STOCHASTIC?  86 doublets.  Under the repo's pinned model
    (soft rejection-sampling, p_keep~0.18 applied i.i.d.) their positions are a
    Bernoulli thinning -> gaps geometric, index-of-dispersion ~1.  A human or
    a rule-based pass would not be.  This is the one discriminator INSIDE the
    filter itself, and it is measurable from the ciphertext alone.

Run: PYTHONUTF8=1 python3 analysis/round10b/B4-otp-steelman/b4_supplement.py
Pure stdlib + the repo's own lp package.  Deterministic (seed 3301).
"""
import os, sys, math, random, re, json, collections, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))      # liber-primus/
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp                                     # noqa
from run_stats import load_pages                                  # noqa

N = gp.N
OUT = {}
def p(*a):
    print(*a); sys.stdout.flush()

pages = load_pages()
OBS = [i for pg in pages[:-2] for i in pg]
L = len(OBS)
SOLVED = [i for pg in pages[-2:] for i in pg]
DBL = [i for i in range(1, L) if OBS[i] == OBS[i-1]]

def diff_dist(x):
    c = collections.Counter((x[i] - x[i-1]) % N for i in range(1, len(x)))
    n = len(x) - 1
    return [c.get(d, 0) / n for d in range(N)]

def english_indices(path, want, skip=20000):
    t = re.sub(r"[^A-Za-z]", "", open(path, encoding="utf-8", errors="ignore").read().upper())
    return gp.keyword_to_indices(t[skip:skip + want * 3])[:want]

KJV = os.path.join(ROOT, "data", "kjv.txt")

# ===================================================================== S1
p("=" * 78)
p("S1 — THE UNCONDITIONAL PAD THEOREM (no English assumption anywhere)")
p("=" * 78)
p("  Theorem. k i.i.d. uniform on Z_29, independent of p  =>  Dk uniform")
p("  =>  Dc = Dp + Dk uniform for ANY p  =>  P(c_i = c_{i-1}) = 1/29 exactly.")
p("  The plaintext CANNOT affect this. English, Klingon, coordinates, base-29")
p("  digits, a key block, random filler -- all give 3.448%.\n")

k_obs = len(DBL)
n_trials = L - 1
q = 1.0 / N
mu = n_trials * q
sd = math.sqrt(n_trials * q * (1 - q))
z = (k_obs - mu) / sd
p(f"  observed doublets           : {k_obs} / {n_trials}  = {100*k_obs/n_trials:.4f}%")
p(f"  uniform-pad prediction      : {mu:.1f} = {100*q:.4f}%   (sd {sd:.1f})")
p(f"  z                           : {z:+.2f}")

# exact binomial upper tail probability of <= 86, in logs (Poisson-accurate here)
def log_binom_cdf(k, n, pr):
    # log-sum-exp of exact binomial pmf terms 0..k
    terms = []
    lg = math.lgamma
    for j in range(0, k + 1):
        terms.append(lg(n+1) - lg(j+1) - lg(n-j+1) + j*math.log(pr) + (n-j)*math.log1p(-pr))
    m = max(terms)
    return m + math.log(sum(math.exp(t - m) for t in terms))

lp_tail = log_binom_cdf(k_obs, n_trials, q)
p(f"  P(Binom(n={n_trials}, 1/29) <= {k_obs}) = exp({lp_tail:.1f}) "
  f"= 10^{lp_tail/math.log(10):.1f}")
p("\n  => AN UNFILTERED ONE-TIME PAD IS REFUTED UNCONDITIONALLY. This is a theorem,")
p("     not an inference, and it needs no assumption about the plaintext at all.")

p("\n  ESCAPE HATCH: could the author have SELECTED a lucky pad instead of")
p("  constructing a filter?  Expected number of pads that must be drawn:")
p(f"    1 / P = 10^{-lp_tail/math.log(10):.1f} pads.")
p(f"    At 10^9 pads/second since the Big Bang (4.4e17 s) one could draw 10^26.")
p("    Selection is infeasible by ~{:.0f} orders of magnitude.".format(
    -lp_tail/math.log(10) - 26))
p("  => the doublet suppression was CONSTRUCTED at encryption time by a rule that")
p("     looked at the output. The key is therefore NOT independent of the message.")
p("     'External pad' (a document applied blindly) is excluded; what remains is an")
p("     ALGORITHM with a feedback rule. That is a mechanism, not a pad.")

OUT["S1"] = {"observed_doublets": k_obs, "n": n_trials,
             "uniform_pad_pct": 100*q, "observed_pct": 100*k_obs/n_trials,
             "z": z, "log10_p": lp_tail/math.log(10),
             "selection_pads_needed_log10": -lp_tail/math.log(10)}

# ===================================================================== S2
p("\n" + "=" * 78)
p("S2 — POSITIVE CONSTRAINT ON THE PLAINTEXT")
p("=" * 78)
p("  For ANY key independent of the plaintext (pad, PRNG, hash, raw or TRANSFORMED")
p("  keytext, any long derived key):   P(dbl) >= min_d P_Dp(d).")
p("  So a plaintext-independent key can only reach 0.664% if the PLAINTEXT's")
p("  first-difference distribution already has a hole at or below 0.664%.")
p("  Which plaintexts have such a hole?\n")

def mk_restricted(alphabet_size, n, seed):
    r = random.Random(seed)
    return [r.randrange(alphabet_size) for _ in range(n)]

def mk_digits(n, seed):
    """A coordinate / number list: digits 0-9 mapped to the first 10 runes."""
    r = random.Random(seed)
    return [r.randrange(10) for _ in range(n)]

def mk_hexish(n, seed):
    r = random.Random(seed)
    return [r.randrange(16) for _ in range(n)]

def mk_lp_like(n, seed):
    """Already-enciphered material: flat and doublet-suppressed (e.g. the output
    of a previous cipher stage used as the plaintext of this one)."""
    r = random.Random(seed); out = []
    for i in range(n):
        c = r.randrange(N)
        if i and c == out[-1] and r.random() < 0.83:
            c = r.randrange(N)
        out.append(c)
    return out

CASES = [
    ("English prose (KJV)",        lambda: english_indices(KJV, 200000)),
    ("author's own LP plaintext",  lambda: SOLVED),
    ("uniform random over 29",     lambda: mk_restricted(29, 200000, 11)),
    ("restricted alphabet 20",     lambda: mk_restricted(20, 200000, 12)),
    ("restricted alphabet 16 (hex)", lambda: mk_hexish(200000, 13)),
    ("digit string 0-9 (coords)",  lambda: mk_digits(200000, 14)),
    ("prior-stage ciphertext",     lambda: mk_lp_like(200000, 15)),
    ("REAL LP2 ITSELF",            lambda: OBS),
]
p(f"  {'plaintext class':<32}{'n':>8}{'min_d P_Dp(d)':>16}{'argmin':>8}"
  f"{'  can reach 0.664% w/ indep key?':>34}")
p("  " + "-" * 96)
s2 = []
for name, fn in CASES:
    x = fn()
    dd = diff_dist(x)
    m = min(dd); am = dd.index(m)
    can = m <= 0.00664
    s2.append({"class": name, "n": len(x), "min_pdp_pct": 100*m, "argmin": am,
               "can_reach": can})
    p(f"  {name:<32}{len(x):>8}{100*m:>15.4f}%{am:>8}"
      f"{('  YES' if can else '  NO'):>34}")
p("\n  READING: every natural-language and every full-alphabet plaintext is EXCLUDED")
p("  from the plaintext-independent-key class. Only RESTRICTED-ALPHABET plaintexts")
p("  (digit strings, coordinates, hex, base-N payloads) leave the door open -- and")
p("  they leave it open trivially, because the unused runes give exact zeros.")
p("  This is a falsifiable, positive prediction, not an absence of evidence:")
p("     IF the key is plaintext-independent, THEN the plaintext uses a restricted")
p("     alphabet -- which is exactly what every English-scoring attack in this repo")
p("     is constructed to be blind to. -> hand-off to lane B6.")
OUT["S2"] = s2

# ===================================================================== S3
p("\n" + "=" * 78)
p("S3 — IS THE 86-DOUBLET RESIDUE A STOCHASTIC THINNING? (the filter's own signature)")
p("=" * 78)
p("  Repo's pinned model: soft rejection sampling, i.i.d. p_keep~0.18. Then the")
p("  surviving doublets are a Bernoulli(p) thinning of a Bernoulli(1/29) process:")
p("  gaps geometric, index of dispersion (Fano factor) ~= 1 on any binning.")
p("  A rule-based or human pass would leave a NON-stochastic residue.\n")

gaps = [DBL[i] - DBL[i-1] for i in range(1, len(DBL))]
p(f"  86 doublets, {len(gaps)} gaps. mean gap {statistics.mean(gaps):.1f} "
  f"(geometric prediction {n_trials/k_obs:.1f}), sd {statistics.pstdev(gaps):.1f}")
p(f"  geometric sd prediction = sqrt(1-p)/p with p={k_obs/n_trials:.5f} -> "
  f"{math.sqrt(1-k_obs/n_trials)/(k_obs/n_trials):.1f}")

def fano(positions, nbins, total):
    w = total / nbins
    c = collections.Counter(int(x / w) for x in positions)
    counts = [c.get(b, 0) for b in range(nbins)]
    m = statistics.mean(counts)
    return statistics.pvariance(counts) / m if m else float("nan")

p(f"\n  {'bins':>6}{'Fano (real)':>14}{'null mean':>12}{'null sd':>10}{'z':>8}")
p("  " + "-" * 52)
s3 = []
for nbins in (10, 26, 50, 100):
    real = fano(DBL, nbins, L)
    nul = []
    for s in range(2000):
        r = random.Random(77000 + s)
        pos = r.sample(range(1, L), k_obs)
        nul.append(fano(pos, nbins, L))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    zz = (real - m) / sd
    s3.append({"nbins": nbins, "real_fano": real, "null_mean": m, "null_sd": sd, "z": zz})
    p(f"  {nbins:>6}{real:>14.4f}{m:>12.4f}{sd:>10.4f}{zz:>+8.2f}")

# Kolmogorov-Smirnov of the gaps against the geometric with the observed rate
pr = k_obs / n_trials
gs = sorted(gaps)
ks = 0.0
for i, g in enumerate(gs):
    cdf = 1 - (1 - pr) ** g
    ks = max(ks, abs((i + 1) / len(gs) - cdf), abs(cdf - i / len(gs)))
crit = 1.36 / math.sqrt(len(gs))
p(f"\n  KS(gaps vs Geometric(p={pr:.5f})) = {ks:.4f}   "
  f"critical(0.05) = {crit:.4f}  -> {'REJECT geometric' if ks > crit else 'consistent with geometric'}")
p("\n  READING: a stochastic residue is consistent with the repo's soft-filter model")
p("  AND with any ciphertext-feedback rule that fires probabilistically. It does NOT")
p("  discriminate pad-plus-filter from feedback-cipher. The filter leaves no")
p("  recoverable fingerprint -- which is itself the reason the two cannot be told")
p("  apart from the ciphertext.")
OUT["S3"] = {"gaps_mean": statistics.mean(gaps), "gaps_sd": statistics.pstdev(gaps),
             "fano": s3, "ks": ks, "ks_crit": crit,
             "geometric_ok": bool(ks <= crit)}

# ===================================================================== S4
p("\n" + "=" * 78)
p("S4 — WHAT IS ACTUALLY FALSIFIABLE, AND HOW MUCH OF IT HAS BEEN SEARCHED")
p("=" * 78)
p("  G5 established: no ciphertext-only STATISTIC separates a true pad from a")
p("  long key derived from a short seed. That is PRG indistinguishability, and it")
p("  is a theorem, so no future statistic will do it either.")
p("  The only discriminator is ENUMERATION of the seed space. That makes the")
p("  derived-key hypothesis falsifiable and the true-pad hypothesis NOT falsifiable.")
p("  Asymmetry: you can only ever kill derived-key families one at a time; you can")
p("  never confirm 'true pad'. 'Unfalsifiable' and 'proven' are opposite conditions.\n")
searched = {
    "integer-seeded library PRNGs (glibc/MSVC/MT19937/CPython/Java), unix-second seeds 2011-2015":
        "2.52e9 decodes — DONE (Round 8 SEED)",
    "lore/string/date seeds over the same PRNGs": "15,408 decodes — DONE (Round 8 SEED)",
    "hash counter/chain-mode keystreams (MD5/SHA-1/SHA-256/SHA-512), HMAC-DRBG":
        "NOT RUN (queued twice in campaign14/REDTEAM-PROPOSALS.md)",
    "stream ciphers (RC4/ARC4, AES-CTR)":
        "NOT RUN (Round 8's own residue paragraph names RC4 as untested)",
    "pp49-51 payload EXPANDED as a PRF seed (RC4/AES-CTR/SHA-CTR/HMAC-DRBG)":
        "NOT RUN (all payload lanes used it DIRECTLY as key material)",
}
for k, v in searched.items():
    p(f"    [{'x' if 'DONE' in v else ' '}] {k}\n        {v}")
p("\n  The repo's own strongest claim ('the pad has no structure') is supported by an")
p("  enumeration of exactly ONE generator family. The families a 2014 author with a")
p("  laptop would most plausibly reach for -- openssl rand, RC4, a SHA-256 counter --")
p("  are the ones not enumerated.")
OUT["S4"] = {"searched": searched}

with open(os.path.join(HERE, "b4_supplement_results.json"), "w") as f:
    json.dump(OUT, f, indent=1, default=float)
p("\nwrote b4_supplement_results.json")
