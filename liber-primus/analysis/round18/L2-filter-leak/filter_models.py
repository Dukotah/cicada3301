"""Round 18 / L2 -- the seven filter-locus models and the statistic battery.

PREREG section 2.A.1 fixes the models; section 2.A.2 fixes the battery.  Nothing here is
tuned after the fact: every model with a free suppression parameter is calibrated by
bisection to the REAL lag-1 rate (the same fairness device lane P4 used), so the doublet
rate itself carries no discriminating information.

The point of the exercise: "no two consecutive equal runes" can be enforced on the
CIPHERTEXT, on the KEYSTREAM, or on the PLAINTEXT.  Those are three different machines and
they make three different predictions.  This repo has assumed the first for two years
without ever testing it.
"""
import os, re, sys, math, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # liber-primus/
for p in ("src", "analysis", os.path.join("analysis", "round11"),
          os.path.join("analysis", "campaign18_skip")):
    sys.path.insert(0, os.path.join(ROOT, p))

from lp import gematria as gp          # noqa: E402
import lib_numchannel as nc            # noqa: E402

N = gp.N
Q = 1.0 / N


# ------------------------------------------------------------------ data
def real_stream():
    x = nc.unsolved()
    assert len(x) == 12956, f"handshake failed: {len(x)} runes, expected 12956"
    return np.asarray(x, dtype=np.int64)


def english_runes(n):
    """n runes of archaic English (KJV), greedy multi-letter Gematria mapping."""
    kjv = os.path.join(ROOT, "data", "kjv.txt")
    t = re.sub(r"[^A-Za-z]", "", open(kjv, encoding="utf-8", errors="ignore").read())
    out = []
    pos = 5000
    while len(out) < n:
        out.extend(gp.keyword_to_indices(t[pos:pos + 4 * n]))
        pos += 4 * n
    return out[:n]


# ------------------------------------------------------------------ models
# decode relation p = (c + sign*k) mod N  =>  c = (p - sign*k) mod N,  sign = -1

def m0_nofilter(P, rng, **kw):
    return [(p + rng.randrange(N)) % N for p in P], 0


def m1_ct_keyskip(P, rng, supp=0.8129, **kw):
    """CIPHERTEXT rejection, key pointer ADVANCES on reject (the repo's pinned model).
    This is the only model in the set that desynchronises key index from rune index."""
    C, cprev, skips = [], None, 0
    for p in P:
        while True:
            c = (p + rng.randrange(N)) % N
            if cprev is not None and c == cprev and rng.random() < supp:
                skips += 1
                continue
            break
        C.append(c); cprev = c
    return C, skips


def m2_ct_rewrite(P, rng, supp=0.8129, **kw):
    """CIPHERTEXT rejection, output OVERWRITTEN with a fresh uniform draw; the key pointer
    does NOT move (RECON-B/B-16's 'value rewrite applied to the output')."""
    C, cprev = [], None
    for p in P:
        c = (p + rng.randrange(N)) % N
        while cprev is not None and c == cprev and rng.random() < supp:
            c = rng.randrange(N)
        C.append(c); cprev = c
    return C, 0


def m2n_ct_nudge(P, rng, supp=0.8075, delta=1, **kw):
    """CIPHERTEXT rejection, output nudged by a FIXED delta. Key pointer does not move."""
    C, cprev = [], None
    for p in P:
        c = (p + rng.randrange(N)) % N
        if cprev is not None and c == cprev and rng.random() < supp:
            c = (c + delta) % N
        C.append(c); cprev = c
    return C, 0


def m3_ks_filtered(P, rng, supp=1.0, **kw):
    """KEYSTREAM filtered at generation: the pad itself never repeats a symbol.
    Key index stays aligned; the ciphertext is a rigid sum."""
    C, kprev = [], None
    for p in P:
        while True:
            k = rng.randrange(N)
            if kprev is not None and k == kprev and rng.random() < supp:
                continue
            break
        C.append((p + k) % N); kprev = k
    return C, 0


def m4_pt_filtered(P, rng, supp=1.0, **kw):
    """PLAINTEXT filtered: the message never repeats a rune (doubles are dropped/rewritten
    BEFORE encipherment). Key index stays aligned."""
    C, pprev = [], None
    for p in P:
        pp = p
        while pprev is not None and pp == pprev and rng.random() < supp:
            pp = rng.randrange(N)
        C.append((pp + rng.randrange(N)) % N); pprev = pp
    return C, 0


def m5_ct_hard(P, rng, **kw):
    """HARD ciphertext rule: redraw (advancing the key) until the output differs."""
    C, cprev, skips = [], None, 0
    for p in P:
        while True:
            c = (p + rng.randrange(N)) % N
            if cprev is not None and c == cprev:
                skips += 1
                continue
            break
        C.append(c); cprev = c
    return C, skips


MODELS = {
    "M0_nofilter":   (m0_nofilter,   None),
    "M1_ct_keyskip": (m1_ct_keyskip, "supp"),
    "M2_ct_rewrite": (m2_ct_rewrite, "supp"),
    "M2n_ct_nudge":  (m2n_ct_nudge,  "supp"),
    "M3_ks_filtered": (m3_ks_filtered, "supp"),
    "M4_pt_filtered": (m4_pt_filtered, "supp"),
    "M5_ct_hard":    (m5_ct_hard,    None),
}


# ------------------------------------------------------------------ battery
def battery(x):
    """PREREG 2.A.2. x = int array of rune indices."""
    x = np.asarray(x, dtype=np.int64)
    n = len(x)
    out = {}
    # 1. lag profile
    for k in range(1, 9):
        eq = int((x[k:] == x[:-k]).sum()); m = n - k
        out["lag%d_rate" % k] = eq / m
        out["lag%d_z" % k] = (eq - m * Q) / math.sqrt(m * Q * (1 - Q))
    eq = sum(int((x[k:] == x[:-k]).sum()) for k in range(2, 9))
    m = sum(n - k for k in range(2, 9))
    out["bleed28_rate"] = eq / m
    out["bleed28_z"] = (eq - m * Q) / math.sqrt(m * Q * (1 - Q))

    # 2. THE DELTA-SPECTRUM (new here): distribution of (c_i - c_{i-1}) mod 29
    dlt = (x[1:] - x[:-1]) % N
    cnt = np.bincount(dlt, minlength=N).astype(float)
    nz = cnt[1:]                                  # the 28 non-doublet cells
    tot = nz.sum()
    exp = tot / 28.0
    chi2 = float(((nz - exp) ** 2 / exp).sum())
    out["delta_chi2"] = chi2
    out["delta_chi2_df"] = chi2 / 27.0
    sd = math.sqrt(exp * (1 - 1.0 / 28))
    zs = (nz - exp) / sd
    out["max_abs_delta_z"] = float(np.max(np.abs(zs)))
    out["argmax_delta"] = int(np.argmax(np.abs(zs)) + 1)
    out["delta0_count"] = int(cnt[0])

    # 3. runs / alternation
    d = (x[1:] == x[:-1])
    out["run2"] = int(d.sum())
    out["run3"] = int((d[1:] & d[:-1]).sum())
    a, b, c, e = x[3:], x[2:-1], x[1:-2], x[:-3]
    ab = ((a == c) & (b == e) & (a != b))
    k = int(ab.sum()); mm = len(ab); pp = Q * Q
    out["abab"] = k
    out["abab_z"] = (k - mm * pp) / math.sqrt(mm * pp * (1 - pp))
    return out


PRIMARY = ["lag1_rate", "delta_chi2_df", "max_abs_delta_z", "bleed28_z", "abab_z"]


# ------------------------------------------------------------------ calibration
def calibrate(name, P, target_rate, seed=3301, reps=6, lo=0.0, hi=0.999, iters=26):
    """Bisect the model's suppression parameter to the REAL lag-1 rate (fairness device)."""
    fn, par = MODELS[name]
    if par is None:
        return None
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        rates = []
        for r in range(reps):
            rng = random.Random(seed + 1000 * r)
            C, _ = fn(P, rng, **{par: mid})
            C = np.asarray(C)
            rates.append(float((C[1:] == C[:-1]).mean()))
        if np.mean(rates) > target_rate:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
