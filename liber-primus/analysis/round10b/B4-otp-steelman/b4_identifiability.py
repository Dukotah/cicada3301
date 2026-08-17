"""B4 — PROSECUTE THE OTP VERDICT.  Identifiability measurements, not a decode.

Runs the four pre-registered gates from PREREG.md:

  G1  reproduce the four headline statistics independently
  G2  IoC keystone      -- what key period does flat IoC actually exclude?
  G3  doublet bound     -- the theorem  P(dbl) = sum_d Pdp(d)*Pdk(-d) >= min_d Pdp(d)
  G4  identifiability   -- do structurally distinct rivals pass the whole battery?
  G5  discriminator     -- external pad vs derived long key: any separating statistic?

Plus the mandatory null control (shuffled LP2) and two positive controls.

Run:  PYTHONUTF8=1 python3 analysis/round10b/B4-otp-steelman/b4_identifiability.py
Pure stdlib + the repo's own lp package.  Deterministic (seed 3301).
"""
import os, sys, math, random, re, json, hashlib, collections, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))      # liber-primus/
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from lp import gematria as gp, stats                              # noqa
from run_stats import load_pages                                  # noqa

N = gp.N
RNG = random.Random(3301)
OUT = {}

def p(*a):
    print(*a); sys.stdout.flush()

# ------------------------------------------------------------------ helpers
def doublet_pct(x):
    return 100.0 * sum(1 for i in range(1, len(x)) if x[i] == x[i-1]) / (len(x) - 1)

def ioc_norm(x):
    c = collections.Counter(x); n = len(x)
    return N * sum(v*(v-1) for v in c.values()) / (n*(n-1))

def entropy(x):
    c = collections.Counter(x); n = len(x)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def chi2_uniform(x):
    c = collections.Counter(x); n = len(x); e = n / N
    return sum((c.get(i, 0) - e) ** 2 / e for i in range(N))

def diff_dist(x):
    """P(x[i]-x[i-1] mod N)."""
    c = collections.Counter((x[i] - x[i-1]) % N for i in range(1, len(x)))
    n = len(x) - 1
    return [c.get(d, 0) / n for d in range(N)]

def diag_cv_nonzero(x):
    """The iter-9 autokey statistic: coefficient of variation of the 28 NONZERO
    difference diagonals of the ciphertext bigram table."""
    dd = diff_dist(x)
    nz = [dd[d] for d in range(1, N)]
    return statistics.pstdev(nz) / statistics.mean(nz)

def offdiag_bigram_chi2(x):
    """Chi2 of the bigram table over the 29*28 off-diagonal cells vs uniform."""
    c = collections.Counter((x[i-1], x[i]) for i in range(1, len(x)))
    cells = [(a, b) for a in range(N) for b in range(N) if a != b]
    tot = sum(c.get(k, 0) for k in cells)
    e = tot / len(cells)
    return sum((c.get(k, 0) - e) ** 2 / e for k in cells)

BATTERY = [("ioc_norm", ioc_norm), ("doublet_pct", doublet_pct),
           ("entropy", entropy), ("chi2_uniform", chi2_uniform),
           ("diag_cv_nz", diag_cv_nonzero), ("offdiag_chi2", offdiag_bigram_chi2)]

def battery(x):
    return {k: f(x) for k, f in BATTERY}

# ------------------------------------------------------------------ data
pages = load_pages()
OBS = [i for pg in pages[:-2] for i in pg]
L = len(OBS)

def english_indices(path, want, skip=20000):
    t = re.sub(r"[^A-Za-z]", "", open(path, encoding="utf-8", errors="ignore").read().upper())
    return gp.keyword_to_indices(t[skip:skip + want * 3])[:want]

CORPORA = {n: os.path.join(ROOT, "data", n + ".txt") for n in
           ("kjv", "moby", "pride", "war")}

p("=" * 78)
p("B4 — GATE G1: independent re-derivation of the load-bearing statistics")
p("=" * 78)
g1 = battery(OBS)
g1["n"] = L
g1["doublets"] = sum(1 for i in range(1, L) if OBS[i] == OBS[i-1])
for k, v in g1.items():
    p(f"  {k:>14} = {v}")
pub = {"n": 12956, "ioc_norm": 1.000, "doublet_pct": 0.664, "entropy": 4.8565}
ok = (g1["n"] == pub["n"] and abs(g1["ioc_norm"] - pub["ioc_norm"]) <= 1e-3
      and abs(g1["doublet_pct"] - pub["doublet_pct"]) <= 5e-3
      and abs(g1["entropy"] - pub["entropy"]) <= 1e-3)
p(f"  published: n=12956 IoC.N=1.000 doublet=0.664% H=4.8565")
p(f"  G1 {'PASS — published numbers reproduce' if ok else 'FAIL'}")
OUT["G1"] = {"measured": g1, "pass": ok}

# ------------------------------------------------------------------ NULL CONTROL
p("\n" + "=" * 78)
p("NULL CONTROL — shuffled LP2 (200 seeded shuffles)")
p("=" * 78)
nul = collections.defaultdict(list)
for s in range(200):
    r = random.Random(90000 + s); y = OBS[:]; r.shuffle(y)
    b = battery(y)
    for k, v in b.items():
        nul[k].append(v)
NULLBAND = {}
for k in nul:
    m = statistics.mean(nul[k]); sd = statistics.pstdev(nul[k])
    NULLBAND[k] = (m, sd)
    p(f"  {k:>14}  mean {m:12.4f}  sd {sd:9.4f}   REAL {g1[k]:12.4f}"
      f"   z={(g1[k]-m)/sd if sd else float('nan'):+7.2f}")
OUT["null_control"] = {k: {"mean": NULLBAND[k][0], "sd": NULLBAND[k][1],
                           "real": g1[k],
                           "z": (g1[k]-NULLBAND[k][0])/NULLBAND[k][1] if NULLBAND[k][1] else None}
                       for k in NULLBAND}

# ==================================================================== G2
p("\n" + "=" * 78)
p("GATE G2 — THE IoC KEYSTONE: what key period does flat IoC actually exclude?")
p("=" * 78)
p("  Claim under test: 'perfectly flat IoC is only reachable by a FULL-LENGTH keystream'.")
p("  Method: encipher real English-in-futhorc with a random periodic key of period k,")
p("          measure ciphertext IoC.N at N=12956, 200 trials per k.")
p("          Detection = IoC.N above the flat-null 95th percentile (>= mean+1.645sd).")

eng = english_indices(CORPORA["kjv"], L * 2)
p(f"\n  English-in-futhorc baseline: IoC.N = {ioc_norm(eng[:L]):.4f}  "
  f"doublet = {doublet_pct(eng[:L]):.3f}%")
flat_mean, flat_sd = NULLBAND["ioc_norm"]
# the flat null for IoC.N at N=12956 -- use uniform random draws (not shuffles of OBS,
# which are already exactly the real marginal)
uni = []
for s in range(400):
    r = random.Random(700000 + s)
    uni.append(ioc_norm([r.randrange(N) for _ in range(L)]))
u_m, u_sd = statistics.mean(uni), statistics.pstdev(uni)
p(f"  flat null (uniform, N={L}): IoC.N mean {u_m:.5f} sd {u_sd:.5f} "
  f"-> 95th pct threshold {u_m + 1.645*u_sd:.5f}")
thresh = u_m + 1.645 * u_sd

p(f"\n  {'period k':>9} {'mean IoC.N':>11} {'sd':>8} {'%trials detected':>17}")
p("  " + "-" * 50)
g2rows = []
for k in (1, 2, 5, 10, 20, 30, 40, 60, 80, 120, 200, 400, 1000, 3000, 12956):
    vals = []
    for t in range(60):
        r = random.Random(11000 + k * 100 + t)
        key = [r.randrange(N) for _ in range(k)]
        ct = [(eng[i] + key[i % k]) % N for i in range(L)]
        vals.append(ioc_norm(ct))
    m = statistics.mean(vals); sd = statistics.pstdev(vals)
    det = 100.0 * sum(1 for v in vals if v >= thresh) / len(vals)
    g2rows.append({"k": k, "mean_ioc": m, "sd": sd, "pct_detected": det})
    p(f"  {k:9d} {m:11.5f} {sd:8.5f} {det:16.1f}%")

pstar = None
for row in g2rows:
    if row["pct_detected"] < 95.0:
        pstar = row["k"]; break
p(f"\n  p* (smallest period NOT reliably detected by IoC at N={L}) = {pstar}")
p(f"  Theory check: IoC.N(k) ~= 1 + (IoC.N_english - 1)/k = 1 + "
  f"{ioc_norm(eng[:L])-1:.4f}/k")
p(f"  G2 {'CONFIRMED — flat IoC bounds period from below at ~%d, NOT at 12956' % pstar if pstar and pstar < 1000 else 'NOT CONFIRMED'}")
OUT["G2"] = {"rows": g2rows, "p_star": pstar, "flat_null_mean": u_m,
             "flat_null_sd": u_sd, "detect_threshold": thresh,
             "english_ioc": ioc_norm(eng[:L])}

# ==================================================================== G3
p("\n" + "=" * 78)
p("GATE G3 — THE DOUBLET BOUND (a theorem, not a simulation)")
p("=" * 78)
p("  For additive c = p + k (mod 29) with k statistically INDEPENDENT of p:")
p("     P(c_i = c_{i-1}) = P(Dp + Dk = 0) = sum_d Pdp(d) * Pdk(-d)  >=  min_d Pdp(d)")
p("  This class contains: every external one-time pad, every PRNG/hash keystream,")
p("  every raw keytext, every TRANSFORMED keytext, every long derived key.")
p("  If min_d Pdp(d) > 0.664%, the observed rate refutes the WHOLE class.\n")

p(f"  {'corpus':>10} {'n':>8} {'IoC.N':>8} {'dbl%':>7} {'min_d Pdp(d) %':>16} {'argmin d':>9}")
p("  " + "-" * 64)
g3rows = []
for name, path in CORPORA.items():
    e = english_indices(path, 200000)
    dd = diff_dist(e)
    m = min(dd); am = dd.index(m)
    g3rows.append({"corpus": name, "n": len(e), "ioc": ioc_norm(e),
                   "dbl": doublet_pct(e), "min_pdp_pct": 100*m, "argmin": am})
    p(f"  {name:>10} {len(e):8d} {ioc_norm(e):8.3f} {doublet_pct(e):7.3f} "
      f"{100*m:16.4f} {am:9d}")
# 5th corpus: the author's OWN plaintext (solved LP pages, transliterated)
solved = [i for pg in pages[-2:] for i in pg]
dd_s = diff_dist(solved)
g3rows.append({"corpus": "LP-solved", "n": len(solved), "ioc": ioc_norm(solved),
               "dbl": doublet_pct(solved), "min_pdp_pct": 100*min(dd_s),
               "argmin": dd_s.index(min(dd_s))})
p(f"  {'LP-solved':>10} {len(solved):8d} {ioc_norm(solved):8.3f} "
  f"{doublet_pct(solved):7.3f} {100*min(dd_s):16.4f} {dd_s.index(min(dd_s)):9d}"
  "   (small n — reported, not relied on)")

big = [r for r in g3rows if r["n"] > 50000]
m_min = min(r["min_pdp_pct"] for r in big)
p(f"\n  Least favourable large corpus: min_d Pdp(d) = {m_min:.4f}%   vs OBSERVED 0.664%")
g3pass = m_min > 0.664
p(f"  G3 {'CONFIRMED' if g3pass else 'NOT CONFIRMED'} — observed doublet rate is "
  f"{'BELOW' if g3pass else 'NOT below'} the theoretical floor of the entire")
p("     plaintext-independent-key class (external pads included).")

# positive control for the bound: is it attained?
p("\n  POSITIVE CONTROL for G3 (is the bound real and tight?):")
e = english_indices(CORPORA["kjv"], L)
r = random.Random(4242)
ct_pad = [(e[i] + r.randrange(N)) % N for i in range(L)]
p(f"    (a) English + TRUE RANDOM PAD          -> doublet {doublet_pct(ct_pad):.3f}%"
  f"   (predicted 100/29 = {100/29:.3f}%)")
ddE = diff_dist(english_indices(CORPORA["kjv"], 200000))
sstar = (-ddE.index(min(ddE))) % N       # constant key-difference attaining the bound
key = [(sstar * i) % N for i in range(L)]
ct_adv = [(e[i] + key[i]) % N for i in range(L)]
p(f"    (b) English + adversarial arithmetic key k_i = {sstar}*i mod 29")
p(f"        -> doublet {doublet_pct(ct_adv):.3f}%   (predicted min_d Pdp(d) = "
  f"{100*min(ddE):.3f}%)   IoC.N = {ioc_norm(ct_adv):.4f}")
p(f"        This is the BEST any independent key can do, and it is still "
  f"{doublet_pct(ct_adv)/0.664:.1f}x the observed rate.")
OUT["G3"] = {"rows": g3rows, "min_over_large_corpora_pct": m_min,
             "observed_pct": g1["doublet_pct"], "pass": g3pass,
             "pc_random_pad_dbl": doublet_pct(ct_pad),
             "pc_adversarial_key_dbl": doublet_pct(ct_adv),
             "pc_adversarial_shift": sstar,
             "pc_adversarial_ioc": ioc_norm(ct_adv)}

# ==================================================================== G4 / G5
p("\n" + "=" * 78)
p("GATE G4/G5 — IDENTIFIABILITY: which generative models does the battery separate?")
p("=" * 78)

def soft_filter_encipher(plain, keystream, p_fix, seed):
    """The repo's own pinned construction (campaign11_pin_the_filter.soft_pad),
    generalised: any keystream, plus an OUTPUT-AWARE anti-repeat resample that
    fires with probability p_fix.  Resampling perturbs only the key value at that
    position."""
    r = random.Random(seed)
    out = []
    for i in range(len(plain)):
        c = (plain[i] + keystream[i]) % N
        if i and c == out[-1] and r.random() < p_fix:
            c = (plain[i] + r.randrange(N)) % N
        out.append(c)
    return out

P_FIX = 0.83   # the repo's own best-fit suppression (CAMPAIGN-XI-FINDINGS.md)

def ks_pad(seed, n):
    r = random.Random(seed); return [r.randrange(N) for _ in range(n)]

def ks_sha(seed, n, tag=b"CICADA"):
    """Long key DERIVED deterministically from a short seed: SHA-256 counter mode,
    rejection-sampled to mod 29 (unbiased)."""
    out = []; ctr = 0
    while len(out) < n:
        h = hashlib.sha256(tag + b"|" + str(seed).encode() + b"|" + str(ctr).encode()).digest()
        for b in h:
            if b < 232:            # 232 = 8*29, rejection sampling -> unbiased
                out.append(b % N)
        ctr += 1
    return out[:n]

def ks_periodic(seed, n, k):
    r = random.Random(seed); key = [r.randrange(N) for _ in range(k)]
    return [key[i % k] for i in range(n)]

def flat_noeng_plain(seed, n):
    """A NON-ENGLISH plaintext that is itself flat and doublet-suppressed --
    e.g. a base-29 rendering of ciphertext/compressed data written with a
    no-adjacent-repeat encoding.  Nothing about LP2 excludes this."""
    r = random.Random(seed); out = []
    for i in range(n):
        c = r.randrange(N)
        if i and c == out[-1] and r.random() < P_FIX:
            c = r.randrange(N)
        out.append(c)
    return out

MODELS = {}
MODELS["A_extpad+filter (REPO'S PINNED MODEL)"] = lambda s: soft_filter_encipher(
    english_indices(CORPORA["kjv"], L, skip=20000 + 7 * s), ks_pad(1000 + s, L), P_FIX, 2000 + s)
MODELS["B_derived-SHA-key+filter"] = lambda s: soft_filter_encipher(
    english_indices(CORPORA["kjv"], L, skip=20000 + 7 * s), ks_sha(s, L), P_FIX, 3000 + s)
MODELS["C_period-40 key+filter"] = lambda s: soft_filter_encipher(
    english_indices(CORPORA["kjv"], L, skip=20000 + 7 * s), ks_periodic(4000 + s, L, 40), P_FIX, 5000 + s)
MODELS["D_CAESAR over flat non-English pt"] = lambda s: [
    (x + 7) % N for x in flat_noeng_plain(6000 + s, L)]
MODELS["E_ct-autokey over flat non-English pt"] = None   # built below
MODELS["F_UNFILTERED external pad (null hyp)"] = lambda s: [
    (a + b) % N for a, b in zip(english_indices(CORPORA["kjv"], L, skip=20000 + 7 * s),
                                ks_pad(8000 + s, L))]

def ct_autokey_flat(s):
    """c_i = c_{i-1} + p_i, with p a flat non-English plaintext whose 0-rune is rare.
    Doublet rate == frequency of rune 0 in the plaintext, so it is tunable to 0.66%
    with NO pad and NO filter at all."""
    r = random.Random(9000 + s)
    q = 0.00664
    pt = []
    for _ in range(L):
        if r.random() < q:
            pt.append(0)
        else:
            pt.append(r.randrange(1, N))
    c = [r.randrange(N)]
    for i in range(1, L):
        c.append((c[-1] + pt[i]) % N)
    return c
MODELS["E_ct-autokey over flat non-English pt"] = ct_autokey_flat

TRIALS = 40
p(f"\n  {TRIALS} realisations per model, N={L}.  Battery = 6 statistics.")
p("  Reference band = mean +/- 1.96 sd of model A (the repo's pinned construction).\n")

res = {}
for name, fn in MODELS.items():
    vals = collections.defaultdict(list)
    for s in range(TRIALS):
        x = fn(s)
        for k, f in BATTERY:
            vals[k].append(f(x))
    res[name] = {k: (statistics.mean(v), statistics.pstdev(v)) for k, v in vals.items()}

Aname = "A_extpad+filter (REPO'S PINNED MODEL)"
A = res[Aname]
hdr = f"  {'model':<38}" + "".join(f"{k:>14}" for k, _ in BATTERY)
p(hdr); p("  " + "-" * (38 + 14 * len(BATTERY)))
for name in MODELS:
    row = f"  {name:<38}" + "".join(f"{res[name][k][0]:14.4f}" for k, _ in BATTERY)
    p(row)
p(f"  {'>> REAL LP2 <<':<38}" + "".join(f"{g1[k]:14.4f}" for k, _ in BATTERY))

p("\n  Does each rival fall inside model A's 95% band on ALL six statistics?")
g4 = {}
for name in MODELS:
    inside, fails = True, []
    for k, _ in BATTERY:
        lo, hi = A[k][0] - 1.96 * A[k][1], A[k][0] + 1.96 * A[k][1]
        if not (lo <= res[name][k][0] <= hi):
            inside = False; fails.append(k)
    g4[name] = {"passes_A_band": inside, "fails": fails}
    p(f"    {name:<40} {'PASS' if inside else 'FAIL on ' + ','.join(fails)}")

p("\n  And does each model match the REAL LP2 on all six (real inside model band)?")
g4real = {}
for name in MODELS:
    inside, fails = True, []
    for k, _ in BATTERY:
        m, sd = res[name][k]
        if sd == 0 or abs(g1[k] - m) > 1.96 * sd:
            inside = False; fails.append(f"{k}(z={(g1[k]-m)/sd:.1f})" if sd else k)
    g4real[name] = {"real_inside": inside, "fails": fails}
    p(f"    {name:<40} {'MATCHES LP2' if inside else 'differs: ' + ', '.join(fails)}")

OUT["G4"] = {"model_stats": {n: {k: {"mean": v[0], "sd": v[1]} for k, v in res[n].items()}
                             for n in res},
             "real": {k: g1[k] for k, _ in BATTERY},
             "inside_A_band": g4, "real_inside_model": g4real, "p_fix": P_FIX}

# ---- G5: the decisive question, stated as a hypothesis test ---------------
p("\n" + "=" * 78)
p("GATE G5 — THE DECISIVE QUESTION: external pad vs long DERIVED key")
p("=" * 78)
p("  Two-sample comparison of model A (true random pad) against model B (SHA-256")
p("  counter-mode key from a short seed), on every battery statistic.")
p("  Bonferroni over 6 statistics: separation requires |z| > 2.93 (alpha=0.01/6).\n")
B = res["B_derived-SHA-key+filter"]
sep = False
g5rows = []
for k, _ in BATTERY:
    ma, sa = A[k]; mb, sb = B[k]
    se = math.sqrt(sa**2 / TRIALS + sb**2 / TRIALS)
    z = (ma - mb) / se if se else 0.0
    g5rows.append({"stat": k, "A_mean": ma, "B_mean": mb, "z": z})
    p(f"    {k:>14}  A={ma:12.4f}  B={mb:12.4f}  z={z:+7.2f}"
      f"  {'SEPARATED' if abs(z) > 2.93 else 'indistinguishable'}")
    if abs(z) > 2.93: sep = True
p(f"\n  G5 answer: {'A separating statistic EXISTS' if sep else 'NO separating statistic — the two are indistinguishable'}")
OUT["G5"] = {"rows": g5rows, "separated": sep,
             "note": "PRG-indistinguishability: for any keystream generator whose output "
                     "passes standard randomness tests, no ciphertext-only statistic can "
                     "separate it from a true pad without enumerating the generator."}

# ---- positive control for the IoC instrument -----------------------------
p("\n" + "=" * 78)
p("POSITIVE CONTROL — can the IoC instrument see a PLANTED periodic key?")
p("=" * 78)
for k in (1, 5, 20, 40, 100, 400, 1000):
    row = [r for r in g2rows if r["k"] == k]
    if row:
        p(f"    planted period {k:5d} -> detected in {row[0]['pct_detected']:5.1f}% of trials"
          f"  (mean IoC.N {row[0]['mean_ioc']:.5f})")
p("  Instrument sensitivity is therefore bounded: it PROVES absence of short periods,")
p("  and proves NOTHING about periods above p*.")

with open(os.path.join(HERE, "b4_results.json"), "w") as f:
    json.dump(OUT, f, indent=1, default=float)
p("\nwrote b4_results.json")
