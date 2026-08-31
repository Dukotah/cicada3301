#!/usr/bin/env python3
"""C2-EXT POSITIVE CONTROLS (mandatory, pre-registered) -- one per new axis.

For each axis, plant the axis' relation using the axis' OWN generator as the key,
then confirm the decoder models it (recovery >= 0.90) where the beam fails (< 0.90):

  A1-A5 : plant enc_skip_by_two (j+=2)         -> decode with PAIR  vs beam(keyskip1)
  A6    : plant enc_free_drift AND enc_drift_at -> decode with DRIFT vs beam(keyskip1)

Protocol mirrors ../C2-skip-by-two/control.py (L=240, held-out self_reliance.txt,
7 seeds), except the KEY is that axis' generator stream and axis A6 uses the
continuous-cousin plant + the drift/permissive preset.

An axis whose control does NOT validate is marked UNVALIDATED and no null will be
claimed over it. Writes control_ext.json.

    python3 control_ext.py
"""
import os, sys, json, random, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis/round19/I1", "analysis/campaign18_skip"):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

import axes as AX                              # noqa  (this lane's axis harness)
import skipdecode as sk                        # noqa  (eng_to_idx)
import driftbeam as DB                         # noqa  (keyskip1 / keyskip2 / permissive)

L = 240
NSEED = 7
RECOVERY_BAR = 0.90
PAIR = DB.PRESETS["pair"]
DRIFT = DB.PRESETS["drift"]
BEAM = DB.PRESETS["exact_ms8"]                 # keyskip1, ms=8 (the L7-B relation)


def english_stream():
    p = os.path.join(LP, "data", "keys", "self_reliance.txt")
    with open(p, encoding="utf-8", errors="ignore") as f:
        return sk.eng_to_idx(f.read())[5000:]


ENG = english_stream()


def take_plain(Ln, seed):
    r = random.Random(9000 + seed)
    s = r.randrange(0, len(ENG) - Ln - 1)
    return ENG[s:s + Ln]


# ------------------------------------------------------------- plant constructions
def enc_skip_by_two(P, K, supp=0.83, seed=3301):
    rng = random.Random(seed)
    C, j, c_prev, nsk = [], 0, None, 0
    for p in P:
        while True:
            c = (p + K[j]) % AX.N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 2
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, nsk


def enc_free_drift(P, K, supp=0.83, q=0.05, seed=3301):
    rng = random.Random(seed)
    C, j, c_prev, nsk, nd = [], 0, None, 0, 0
    for p in P:
        if rng.random() < q:
            j += 1
            nd += 1
        while True:
            c = (p + K[j]) % AX.N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, nsk + nd


def enc_drift_at(P, K, supp=0.83, ndrift=10, seed=3301):
    rng = random.Random(seed)
    n = len(P)
    pos = {int((i + 1) * n / (ndrift + 1)) for i in range(ndrift)}
    C, j, c_prev, nsk = [], 0, None, 0
    for i, p in enumerate(P):
        if i in pos:
            j += 1
        while True:
            c = (p + K[j]) % AX.N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, nsk + len(pos)


def rec(a, truth):
    return sum(1 for x, y in zip(a, truth) if x == y) / max(1, len(truth))


def axis_key(axis, seed_int, need):
    """Draw the axis' generator keystream. Uses a fixed LP2-plausible base seed per
    axis, shifted per control seed s so 7 independent plants are measured."""
    spec = AX.AXES[axis]
    if spec["kind"] == "bytes":
        return spec["fn"](("CICADA3301_%d" % seed_int).encode(), need)
    return spec["fn"](seed_int, need)


def run_axis(axis, plant_fn, decoder_preset, supp=0.83, **plant_kw):
    rows = []
    need = L * 10 + 1024
    for s in range(NSEED):
        P = take_plain(L, s)
        # a distinct, LP2-plausible base seed per control replicate
        base_seed = (3301 + s) if AX.AXES[axis]["kind"] == "int" else (3301 + s)
        K = axis_key(axis, base_seed, need)
        C, nsk = plant_fn(P, K, supp=supp, seed=3301 + s, **plant_kw)
        dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / max(1, len(C) - 1)
        beam = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, **BEAM)
        dec = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, **decoder_preset)
        rows.append({"seed": 3301 + s, "n_events": nsk, "ct_doublet_pct": 100 * dbl,
                     "beam_score": beam["score"], "beam_rec": rec(beam["plain_idx"], P),
                     "dec_score": dec["score"], "dec_rec": rec(dec["plain_idx"], P)})
    return rows


def med(rows, k):
    return statistics.median(r[k] for r in rows)


def summarize(rows):
    return {"dec_median_rec": med(rows, "dec_rec"), "beam_median_rec": med(rows, "beam_rec"),
            "dec_median_score": med(rows, "dec_score"), "beam_median_score": med(rows, "beam_score"),
            "min_dec_rec": min(r["dec_rec"] for r in rows),
            "ct_doublet_pct": med(rows, "ct_doublet_pct"), "rows": rows}


def main():
    out = {"lane": "round24/C2-ext-skip-generators/control_ext",
           "recovery_bar": RECOVERY_BAR, "n_seeds": NSEED, "axes": {}}

    # A1-A5: skip_by_two, PAIR decoder
    pair_axes = [("A1_bash", "pair"), ("A2_perl", "pair"), ("A3t_texpgf", "pair"),
                 ("A3l_texlcg", "pair"), ("A4_sha", "pair"), ("A5_py27off", "pair")]
    print("axis          | decoder | dec_rec | beam_rec | dec_score | ct-dbl% | VALID")
    print("-" * 82)
    for axis, _ in pair_axes:
        rows = run_axis(axis, enc_skip_by_two, PAIR, supp=0.83)
        summ = summarize(rows)
        valid = summ["dec_median_rec"] >= RECOVERY_BAR and summ["beam_median_rec"] < RECOVERY_BAR
        summ["decoder"] = "pair"
        summ["plant"] = "enc_skip_by_two (j+=2)"
        summ["control_validated"] = bool(valid)
        out["axes"][axis] = summ
        print(f"{axis:13s} | pair    | {summ['dec_median_rec']:6.1%} | "
              f"{summ['beam_median_rec']:7.1%} | {summ['dec_median_score']:8.3f} | "
              f"{summ['ct_doublet_pct']:5.2f} | {'YES' if valid else 'NO'}")

    # A6: continuous cousin -- free_drift AND drift_at, DRIFT decoder
    for tag, pfn, kw in (("A6_py27:free_drift", enc_free_drift, dict(q=0.05)),
                         ("A6_py27:drift_at", enc_drift_at, dict(ndrift=10))):
        rows = run_axis("A6_py27", pfn, DRIFT, supp=0.83, **kw)
        summ = summarize(rows)
        valid = summ["dec_median_rec"] >= RECOVERY_BAR and summ["beam_median_rec"] < RECOVERY_BAR
        summ["decoder"] = "drift"
        summ["plant"] = tag.split(":")[1]
        summ["control_validated"] = bool(valid)
        out["axes"][tag] = summ
        print(f"{tag:19s}| drift   | {summ['dec_median_rec']:6.1%} | "
              f"{summ['beam_median_rec']:7.1%} | {summ['dec_median_score']:8.3f} | "
              f"{summ['ct_doublet_pct']:5.2f} | {'YES' if valid else 'NO'}")

    validated = {k: v["control_validated"] for k, v in out["axes"].items()}
    out["validated_axes"] = validated
    out["all_validated"] = all(validated.values())
    json.dump(out, open(os.path.join(HERE, "control_ext.json"), "w"), indent=1)
    print("-" * 82)
    for k, v in validated.items():
        print(f"  {k:20s} {'VALIDATED' if v else 'UNVALIDATED -> no null claimed over it'}")
    return out


if __name__ == "__main__":
    main()
