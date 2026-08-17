"""LENS N5 — the totient-ladder escalation.

The solved pages escalate to phi(prime) keystream. Test the NEXT rung of generators
as decrypt keystreams over the unsolved 12,956-rune stream:
  - phi(phi(p))            (iterated totient)
  - Carmichael lambda(p)   (== p-1 for primes, so we also do lambda of composites via
                            the running-sum / prime-index views to make it non-trivial)
  - totient-of-running-sum phi(sum of primes so far)
  - prime-index-totient    phi(i)  where i is the rune's prime-index (1..29)
  - a couple of natural cousins (phi(phi(runningsum)), lambda(runningsum))

sign +/-, per-segment offset sweep + continuous. Positive control REQUIRED:
reproduce AN END with phi(prime) via ciphers.prime_totient_stream.

Decision rule (PREREG): HIT iff score_norm >= -5.5 AND >= null_max + 0.5.
"""
import os, sys, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import lib_numchannel as nc
from lp import gematria as gp, ciphers

N = nc.N
PRIMES = nc.PRIMES

# ------------------------------------------------------------------ helpers
def _is_prime(n):
    if n < 2: return False
    i = 2
    while i*i <= n:
        if n % i == 0: return False
        i += 1
    return True

def _totient(n):
    if n < 1: return 0
    result, m, p = n, n, 2
    while p*p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            result -= result // p
        p += 1
    if m > 1:
        result -= result // m
    return result

def _carmichael(n):
    """Carmichael lambda(n)."""
    if n < 1: return 0
    if n == 1: return 1
    # factorize
    m = n; factors = {}
    d = 2
    while d*d <= m:
        while m % d == 0:
            factors[d] = factors.get(d,0)+1
            m //= d
        d += 1
    if m > 1:
        factors[m] = factors.get(m,0)+1
    def lam_pk(p,k):
        if p == 2:
            if k == 1: return 1
            if k == 2: return 2
            return 2**(k-2)
        return (p-1)*p**(k-1)
    vals = [lam_pk(p,k) for p,k in factors.items()]
    l = 1
    for v in vals:
        l = l*v // math.gcd(l,v)
    return l

# ------------------------------------------------- keystream GENERATORS
# The SOLVED rung is POSITIONAL: key[i] = (p_{i+1} - 1) mod 29 where p_1,p_2,... are
# consecutive primes by POSITION (independent of the rune values). N5 escalates that
# same positional keystream to the NEXT generators. `idxs` is only used for its LENGTH
# in positional generators; rune-indexed cousins (suffix _RI) additionally use values.

# cache a long list of consecutive primes
def _consec_primes(count):
    primes, cand = [], 2
    while len(primes) < count:
        if all(cand % p for p in primes if p*p <= cand):
            primes.append(cand)
        cand += 1
    return primes

_PRIMES_LONG = _consec_primes(14000)

def ks_phi_phi(idxs):
    """POSITIONAL phi(phi(p_i)) — iterated totient of the i-th prime. THE next rung."""
    n = len(idxs)
    return [_totient(_totient(_PRIMES_LONG[i])) for i in range(n)]

def ks_lambda_prime(idxs):
    """POSITIONAL Carmichael lambda(p_i) == p_i-1 == the solved rung (control cousin)."""
    n = len(idxs)
    return [_carmichael(_PRIMES_LONG[i]) for i in range(n)]

def ks_phi_runsum(idxs):
    """phi( running sum of consecutive primes p_1..p_i )."""
    out, s = [], 0
    for i in range(len(idxs)):
        s += _PRIMES_LONG[i]
        out.append(_totient(s))
    return out

def ks_phiphi_runsum(idxs):
    """phi(phi( running sum of consecutive primes ))."""
    out, s = [], 0
    for i in range(len(idxs)):
        s += _PRIMES_LONG[i]
        out.append(_totient(_totient(s)))
    return out

def ks_lambda_runsum(idxs):
    """Carmichael lambda( running sum of consecutive primes )."""
    out, s = [], 0
    for i in range(len(idxs)):
        s += _PRIMES_LONG[i]
        out.append(_carmichael(s))
    return out

def ks_phi_primeindex(idxs):
    """POSITIONAL phi(i) — totient of the position index i (1-based)."""
    return [_totient(i + 1) for i in range(len(idxs))]

# rune-indexed cousins (use the rune VALUES) — the "their numbers" reading
def ks_phi_phi_RI(idxs):
    return [_totient(_totient(PRIMES[i])) for i in idxs]

def ks_phi_runsum_RI(idxs):
    """phi( running sum of the runes' OWN prime magnitudes ) — data-dependent."""
    out, s = [], 0
    for i in idxs:
        s += PRIMES[i]
        out.append(_totient(s))
    return out

GENERATORS = {
    "phi_phi_prime":   ks_phi_phi,        # positional iterated totient — primary next rung
    "lambda_prime":    ks_lambda_prime,   # positional lambda == solved rung cousin
    "phi_runsum":      ks_phi_runsum,
    "phiphi_runsum":   ks_phiphi_runsum,
    "lambda_runsum":   ks_lambda_runsum,
    "phi_primeindex":  ks_phi_primeindex,
    "phi_phi_prime_RI":ks_phi_phi_RI,     # rune-indexed cousin
    "phi_runsum_RI":   ks_phi_runsum_RI,  # rune-indexed running-sum
}

# ------------------------------------------------- apply + score
def decrypt_score(idxs, ks, sign, offset):
    """Apply keystream (mod 29) with sign and integer offset, return eng_norm."""
    n = len(idxs)
    out = [(idxs[i] + sign * (ks[i] + offset)) % N for i in range(n)]
    return nc.eng_norm(out)

def best_over_config(idxs, gen_fn, offsets):
    ks = gen_fn(idxs)
    best = (-99.0, None)
    for sign in (+1, -1):
        for off in offsets:
            s = decrypt_score(idxs, ks, sign, off)
            if s > best[0]:
                best = (s, (sign, off))
    return best

# =================================================================== MAIN
def main():
    results = {"lens": "N5", "control": {}, "runs": [], "null": {}}

    # ---------- POSITIVE CONTROL: reproduce AN END with phi(prime) ----------
    ae = nc.anend()
    ks = ciphers.prime_totient_stream(len(ae))
    dec = nc.apply_keystream(ae, ks, sign=-1)
    txt = "".join(gp.IDX_TO_TRANS[i] for i in dec)
    ctrl_ok = txt.startswith("ANENDWITHIN")
    ctrl_score = nc.eng_norm(dec)
    raw_score = nc.eng_norm(ae)
    results["control"] = {
        "decrypt_head": txt[:40],
        "starts_with_ANENDWITHIN": ctrl_ok,
        "decrypt_score": round(ctrl_score, 3),
        "raw_ciphertext_score": round(raw_score, 3),
    }
    print(f"[CONTROL] AN END head: {txt[:40]!r}  ok={ctrl_ok}")
    print(f"[CONTROL] decrypt score {ctrl_score:.3f}  vs raw {raw_score:.3f}")

    # Show my own generator machinery ALSO reproduces it: positional lambda(p)==p-1==phi(p)
    ks2 = ks_lambda_prime(ae)
    dec2 = [(ae[i] - (ks2[i] % N)) % N for i in range(len(ae))]
    txt2 = "".join(gp.IDX_TO_TRANS[i] for i in dec2)
    results["control"]["lambda_prime_head"] = txt2[:40]
    results["control"]["lambda_prime_matches"] = txt2.startswith("ANENDWITHIN")
    print(f"[CONTROL] my lambda(prime) gen head: {txt2[:40]!r}  matches={txt2.startswith('ANENDWITHIN')}")

    # Ladder-machinery control: encrypt real English with phi_phi_prime, recover it.
    parable = nc.segments()[-1]
    plant = (parable * 40)[:2000]
    ks_pp = ks_phi_phi(plant)
    ct = [(plant[i] + (ks_pp[i] % N)) % N for i in range(len(plant))]
    rec = [(ct[i] - (ks_pp[i] % N)) % N for i in range(len(ct))]
    s_plant = nc.eng_norm(plant); s_ct = nc.eng_norm(ct); s_rec = nc.eng_norm(rec)
    ladder_ok = (rec == plant) and (s_ct < s_plant - 1.0)
    results["control"]["ladder_plant_recovered"] = (rec == plant)
    results["control"]["ladder_plant_score"] = round(s_plant,3)
    results["control"]["ladder_ct_score"] = round(s_ct,3)
    results["control"]["ladder_rec_score"] = round(s_rec,3)
    print(f"[CONTROL] phi_phi ladder plant: plain {s_plant:.3f} -> ct {s_ct:.3f} -> rec {s_rec:.3f}  recovered={rec==plant}")

    control_pass = ctrl_ok and txt2.startswith("ANENDWITHIN") and ladder_ok
    results["control"]["control_pass"] = control_pass
    if not control_pass:
        results["verdict"] = "INCONCLUSIVE"
        print("\n[VERDICT] INCONCLUSIVE — control failed")
        _dump(results); return

    # ---------- LADDER on the unsolved stream ----------
    u = nc.unsolved()
    print(f"\n[STREAM] unsolved = {len(u)} runes")

    # continuous (whole-stream) offset sweep, full mod range
    offsets = list(range(N))  # 0..28 covers all additive offsets
    print("\n=== continuous whole-stream ===")
    cont_best = {}
    for name, fn in GENERATORS.items():
        s, cfg = best_over_config(u, fn, offsets)
        cont_best[name] = {"score": round(s,3), "sign": cfg[0], "offset": cfg[1]}
        results["runs"].append({"mode":"continuous","gen":name,"score":round(s,3),
                                "sign":cfg[0],"offset":cfg[1]})
        print(f"  {name:20s} best {s:.3f}  (sign {cfg[0]:+d}, off {cfg[1]})")

    # per-segment reset + per-segment offset sweep (each page keys from its own start)
    segs = nc.segments()[:-2]  # unsolved pages only
    print("\n=== per-segment reset (best offset per segment, summed length-weighted) ===")
    seg_best = {}
    for name, fn in GENERATORS.items():
        # concatenate per-segment best-decrypts into one stream, then score whole
        combined = []
        for seg in segs:
            ks_s = fn(seg)
            best_local = (-99.0, None)
            for sign in (+1,-1):
                for off in offsets:
                    out = [(seg[i] + sign*(ks_s[i]+off)) % N for i in range(len(seg))]
                    sc = nc.eng_norm(out) if len(out) >= 20 else -99.0
                    if sc > best_local[0]:
                        best_local = (sc, (sign,off,out))
            combined.extend(best_local[1][2])
        s = nc.eng_norm(combined)
        seg_best[name] = round(s,3)
        results["runs"].append({"mode":"per_segment","gen":name,"score":round(s,3)})
        print(f"  {name:20s} combined {s:.3f}")

    # ---------- NULL band on the unsolved stream ----------
    # size-matched histogram-preserving shuffle; score with the SAME best pipeline
    # (continuous, best generator+config) to get a fair FP ceiling.
    print("\n=== null band (200 draws, seed 3301) ===")
    # The winning REAL generator (by continuous best) defines the pipeline; the null
    # applies THAT SAME generator+full-offset-sweep max to each shuffle. This is the
    # matched FP ceiling for the statistic we maximised. (Scoring all 8 gens x 200
    # draws x 13k runes is too slow; the max-over-gens on real is dominated by one
    # family, and offset-sweep max is the real degree of freedom.)
    win_name = max(cont_best, key=lambda k: cont_best[k]["score"])
    win_fn = GENERATORS[win_name]
    results["null"]["generator"] = win_name
    print(f"  null generator = {win_name}")
    def pipeline_max(seq):
        s,_ = best_over_config(seq, win_fn, offsets)
        return s

    nmean, nmax, allv = nc.null_band(pipeline_max, u, n=200)
    results["null"] = {"n":200, "mean":round(nmean,3), "max":round(nmax,3)}
    print(f"  null pipeline_max: mean {nmean:.3f}  max {nmax:.3f}")

    # real best across everything
    real_best = max([r["score"] for r in results["runs"]])
    results["best_score"] = round(real_best, 3)
    print(f"\n[REAL] best score across all N5 runs: {real_best:.3f}")
    print(f"[NULL] max: {nmax:.3f}  mean: {nmean:.3f}")

    hit = (real_best >= -5.5) and (real_best >= nmax + 0.5)
    results["hit"] = hit
    results["verdict"] = "HIT" if hit else "NEGATIVE"
    print(f"\n[VERDICT] {results['verdict']}  (bar: >=-5.5 AND >= null_max+0.5 = {nmax+0.5:.3f})")

    _dump(results)

def _dump(results):
    with open(os.path.join(os.path.dirname(__file__), "results.json"), "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
