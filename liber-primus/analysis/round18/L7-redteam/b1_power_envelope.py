"""L7 / sub-attack B — the skip-aware beam's POWER ENVELOPE.

Plant the correct key under progressively harder constructions and measure whether the
repo's decoder still recovers it. The plaintext is held at English throughout, so the
scorer is at full power and every loss measured here is the DECODER's.

The construction that matters most is `free_drift`: `beam_decode` admits a key skip only if
EVERY skipped key position would have reproduced the previous cipher rune. That validity test
is exact for `encipher_keyskip` and for nothing else. Any other reason the key pointer could
advance — an interrupter, a line break, a discarded draw — is not merely harder for the beam,
it is outside its transition relation.

    python3 b1_power_envelope.py            # writes out_b1.json
    python3 b1_power_envelope.py --quick
"""
import os, sys, json, math, random, statistics, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round11")):
    sys.path.insert(0, p)

from lp import gematria as gp                # noqa: E402
from lp import score as _score               # noqa: E402
from lp import stats as _stats               # noqa: E402
import skipdecode as sk                      # noqa: E402
import plant as PL                           # noqa: E402

N = gp.N
Q = _score.default()
BAR = -5.5
L_DEFAULT = 240
NSEED = 7
LP2_DOUBLET_PCT = 0.6638


# ------------------------------------------------------------------ plaintext
def english_stream():
    p = os.path.join(LP, "data", "keys", "self_reliance.txt")
    with open(p, encoding="utf-8", errors="ignore") as f:
        t = f.read()
    idx = sk.eng_to_idx(t)
    return idx[5000:]


ENG = english_stream()


def take_plain(L, seed):
    r = random.Random(9000 + seed)
    s = r.randrange(0, len(ENG) - L - 1)
    return ENG[s:s + L]


# ------------------------------------------------------------- key material
def key_sha(n, seed=b"CICADA3301"):
    return PL.make_key("sha256_ctr", length=n, seed=seed)


def key_runs(n, run, seed=b"CICADA3301"):
    """A keystream with constant runs of length `run` (the low-entropy pad regime that
    Round 17 P1 found breaks max_skip=3)."""
    base = PL.make_key("sha256_ctr", length=n // max(1, run) + 8, seed=seed)
    out = []
    for v in base:
        out.extend([v] * run)
        if len(out) >= n:
            break
    return out[:n]


# --------------------------------------------------------- encipher variants
def enc_keyskip(P, K, supp=0.83, seed=3301, **_):
    C, skips, _u = sk.encipher_keyskip(P, K, sign=-1, supp=supp, seed=seed)
    return C, {"n_skips": int(sum(skips))}


def enc_keyskip_varying(P, K, mode="ramp", seed=3301, **_):
    """Position-varying suppression probability."""
    rng = random.Random(seed)
    n = len(P)

    def supp_at(i):
        if mode == "ramp":
            return i / max(1, n - 1)
        if mode == "blocks":                      # alternating 'pages'
            return 0.60 if (i // 60) % 2 == 0 else 0.98
        if mode == "burst":                       # one hard stretch in the middle
            return 1.0 if n // 3 <= i < 2 * n // 3 else 0.30
        raise ValueError(mode)

    C, j, c_prev, nsk = [], 0, None, 0
    for i, p in enumerate(P):
        s = supp_at(i)
        while True:
            c = (p + K[j]) % N                    # p = (c - k) with sign=-1 -> c = p + k
            if c_prev is not None and c == c_prev and rng.random() < s:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk}


def enc_free_drift(P, K, supp=0.83, q=0.01, seed=3301, **_):
    """The pinned filter PLUS an extra key advance with probability q for a reason
    unrelated to the doublet rule (interrupter, line break, discarded draw).
    The beam's validity test cannot represent this."""
    rng = random.Random(seed)
    C, j, c_prev, nsk, ndrift = [], 0, None, 0, 0
    for p in P:
        if rng.random() < q:
            j += 1
            ndrift += 1
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk, "n_drift": ndrift}


def enc_drift_at(P, K, supp=0.83, ndrift=1, seed=3301, **_):
    """The pinned filter plus EXACTLY `ndrift` extra key advances, at evenly spaced
    positions. Isolates the cost of a single key advance the beam cannot represent."""
    rng = random.Random(seed)
    n = len(P)
    pos = {int((i + 1) * n / (ndrift + 1)) for i in range(ndrift)} if ndrift else set()
    C, j, c_prev, nsk = [], 0, None, 0
    for i, p in enumerate(P):
        if i in pos:
            j += 1
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk, "n_drift": len(pos)}


def enc_skip_by_two(P, K, supp=0.83, seed=3301, **_):
    """Rejection CONSUMES TWO draws (the rejected symbol plus a fresh one), i.e. the
    rejection sampler burns key material at a different rate than the beam assumes."""
    rng = random.Random(seed)
    C, j, c_prev, nsk = [], 0, None, 0
    for p in P:
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 2
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk}


def enc_rewrite(P, K, supp=0.83, seed=3301, **_):
    C, info = PL.encipher_rewrite(P, K, sign=-1, supp=supp, seed=seed)
    return C, {"n_rewrites": info["n_rewrites"]}


def enc_keyside(P, K, supp=0.83, seed=3301, **_):
    """The KEYSTREAM was generated doublet-free; encipherment is rigid. Never tested."""
    Kf, prev = [], None
    r = random.Random(seed)
    for k in K:
        if prev is not None and k == prev and r.random() < supp:
            continue
        Kf.append(k)
        prev = k
    C = [(P[i] + Kf[i]) % N for i in range(len(P))]
    return C, {"n_key_drops": len(K) - len(Kf)}


def enc_plainside(P, K, supp=0.83, seed=3301, **_):
    """The PLAINTEXT was written doublet-free; encipherment is rigid. Never tested."""
    r = random.Random(seed)
    Pf, prev = [], None
    for p in P:
        if prev is not None and p == prev and r.random() < supp:
            continue
        Pf.append(p)
        prev = p
    C = [(Pf[i] + K[i]) % N for i in range(len(Pf))]
    return C, {"n_plain_drops": len(P) - len(Pf), "_P_used": Pf}


MECH = {"keyskip": enc_keyskip, "keyskip_varying": enc_keyskip_varying,
        "free_drift": enc_free_drift, "drift_at": enc_drift_at,
        "skip_by_two": enc_skip_by_two,
        "rewrite": enc_rewrite, "keyside": enc_keyside, "plainside": enc_plainside}


# --------------------------------------------------------------------- runner
def run_case(name, mech, mkw=None, L=L_DEFAULT, max_skip=3, beam_w=400,
             key="sha", key_kw=None, nseed=NSEED):
    mkw = dict(mkw or {})
    key_kw = dict(key_kw or {})
    rows = []
    for s in range(nseed):
        P = take_plain(L, s)
        need = L * (max_skip + 2) * 3 + 1024
        K = key_runs(need, **key_kw) if key == "runs" else key_sha(need)
        C, info = MECH[mech](P, K, seed=3301 + s, **mkw)
        Ptrue = info.pop("_P_used", P)
        bd = sk.beam_decode(C, K, sign=-1, o=0, beam_w=beam_w, max_skip=max_skip)
        rec = sum(1 for a, b in zip(bd["plain_idx"], Ptrue) if a == b) / max(1, len(Ptrue))
        dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / max(1, len(C) - 1)
        rows.append({"seed": s, "score": bd["score"], "recovery": rec,
                     "ct_doublet_pct": 100 * dbl, **info})
    med = statistics.median(r["score"] for r in rows)
    medrec = statistics.median(r["recovery"] for r in rows)
    meddbl = statistics.median(r["ct_doublet_pct"] for r in rows)
    return {"case": name, "mechanism": mech, "params": {**mkw, **key_kw},
            "min_score": min(r["score"] for r in rows),
            "max_score": max(r["score"] for r in rows),
            "min_recovery": min(r["recovery"] for r in rows),
            "L": L, "max_skip": max_skip, "beam_w": beam_w, "key": key,
            "n_seeds": nseed,
            "median_score": med, "median_recovery": medrec,
            "median_ct_doublet_pct": meddbl,
            "doublet_matches_LP2_pm0.3": abs(meddbl - LP2_DOUBLET_PCT) <= 0.3,
            "frac_over_bar": sum(1 for r in rows if r["score"] >= BAR) / len(rows),
            "MISSED": med < BAR, "rows": rows}


def main():
    quick = "--quick" in sys.argv
    nseed = 3 if quick else NSEED
    cases = []
    t0 = time.time()

    def go(*a, **kw):
        kw.setdefault("nseed", nseed)
        r = run_case(*a, **kw)
        cases.append(r)
        print(f"  {r['case']:44s} score {r['median_score']:7.3f}  rec {r['median_recovery']:6.1%}"
              f"  dbl {r['median_ct_doublet_pct']:5.2f}%  "
              f"{'MISSED' if r['MISSED'] else 'found'}"
              f"{'  [LP2-like doublet]' if r['doublet_matches_LP2_pm0.3'] else ''}")
        return r

    print("\n1. POSITIVE CONTROL + suppression sweep (key-skip)")
    for supp in (0.0, 0.2, 0.4, 0.6, 0.83, 0.95, 1.0):
        go(f"keyskip supp={supp}", "keyskip", {"supp": supp})

    print("\n2. WHERE THE FILTER ACTS (and whether it even reproduces LP2's 0.664%)")
    for m in ("keyskip", "rewrite", "keyside", "plainside"):
        go(f"placement:{m} supp=0.83", m, {"supp": 0.83})

    print("\n3. POSITION-VARYING suppression")
    for mode in ("ramp", "blocks", "burst"):
        go(f"varying:{mode}", "keyskip_varying", {"mode": mode})

    print("\n4. FREE KEY DRIFT (skips the beam's validity test cannot represent)")
    for q in (0.0, 0.002, 0.005, 0.01, 0.02, 0.05):
        go(f"free_drift q={q}", "free_drift", {"supp": 0.83, "q": q})
    print("   ... and with the skip budget raised to 8:")
    for q in (0.005, 0.02):
        go(f"free_drift q={q} ms=8", "free_drift", {"supp": 0.83, "q": q}, max_skip=8)

    print("\n4b. EXACTLY n UNREPRESENTABLE KEY ADVANCES (cost per event)")
    for nd in (0, 1, 2, 3, 5, 10):
        go(f"drift_at n={nd}", "drift_at", {"supp": 0.83, "ndrift": nd})
    for nd in (1, 3):
        go(f"drift_at n={nd} ms=8 bw=1000", "drift_at", {"supp": 0.83, "ndrift": nd},
           max_skip=8, beam_w=1000)

    print("\n5. REJECTION CONSUMES TWO DRAWS")
    for supp in (0.4, 0.83, 1.0):
        go(f"skip_by_two supp={supp}", "skip_by_two", {"supp": supp})
    go("skip_by_two supp=0.83 ms=8", "skip_by_two", {"supp": 0.83}, max_skip=8)

    print("\n6. LOW-ENTROPY PAD (constant runs), max_skip 3 vs 8")
    for run in (1, 2, 4, 8, 16, 32):
        for ms in (3, 8):
            for sp in (0.83, 1.0):
                go(f"runs r={run} supp={sp} ms={ms}", "keyskip", {"supp": sp},
                   max_skip=ms, key="runs", key_kw={"run": run})

    print("\n7. BUDGET AND BEAM WIDTH at supp=1.0 (high-entropy pad)")
    for ms in (1, 2, 3, 5, 8):
        go(f"supp=1.0 ms={ms}", "keyskip", {"supp": 1.0}, max_skip=ms)
    for bw in (50, 120, 400, 1000):
        go(f"supp=1.0 beam_w={bw}", "keyskip", {"supp": 1.0}, beam_w=bw)

    out = {"lane": "round18/L7-redteam/B1",
           "bar": BAR, "plaintext": "held-out English (self_reliance.txt), L=240",
           "instrument": "skipdecode.beam_decode with the CORRECT key",
           "rule": "MISSED = median correct-key score < -5.5 over the seeds",
           "LP2_doublet_pct": LP2_DOUBLET_PCT,
           "elapsed_s": round(time.time() - t0, 1),
           "cases": cases}
    json.dump(out, open(os.path.join(HERE, "out_b1.json"), "w"), indent=1)

    miss = [c for c in cases if c["MISSED"]]
    lp2like = [c for c in miss if c["doublet_matches_LP2_pm0.3"]]
    print(f"\nMISSED {len(miss)}/{len(cases)} constructions; "
          f"{len(lp2like)} of those also reproduce LP2's doublet rate to +-0.3pp:")
    for c in lp2like:
        print(f"   {c['case']:44s} score {c['median_score']:7.3f} "
              f"rec {c['median_recovery']:6.1%} dbl {c['median_ct_doublet_pct']:.2f}%")
    print("\nwrote out_b1.json (%.1fs)" % out["elapsed_s"])


if __name__ == "__main__":
    main()
