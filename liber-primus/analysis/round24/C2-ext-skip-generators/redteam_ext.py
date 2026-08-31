#!/usr/bin/env python3
"""C2-EXT RED-TEAM (R6, mandatory) -- per-axis FP ceiling under the SAME decoder the
sweep used. Refute-by-default. seed-3301 order-matched wrong keys, drawn NOT from the
axis' prior slice, decoded on the SAME unsolved C[:120]/C[:240]. Measures:

  1. wrong keys clearing the Stage-A screen bar (5.0),
  2. of those, how many clear the full three-clause hitfn20 gate at the axis' claim bar,
  3. the wrong-key pmax distribution (max / p99 / median) vs the claim bar.

Expected FP over the axis' real slice = P(clears full gate) * N_screened. Any sweep
survivor must be refuted against this ceiling before any oracle flag stands.

    python3 redteam_ext.py [--n 2000]
"""
import argparse, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis/round19/I1", "analysis/round19/I2", "analysis/round20/P3",
          "analysis/round11", "analysis/campaign18_skip", "src",
          "analysis/round20/HITFN"):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

import axes as AX                  # noqa
import lib_numchannel as nc        # noqa
import driftbeam as DB             # noqa
import adjudicate as AD            # noqa
import hitfn20 as H                # noqa

L_SCREEN, L_HIT = 120, 240
SCREEN_BAR, SCREEN_BEAM_W = 5.0, 64
U = list(nc.unsolved())
C_SCREEN, C_HIT = U[:L_SCREEN], U[:L_HIT]
NEED_SCREEN, NEED_HIT = L_SCREEN * 6 + 64, L_HIT * 6 + 64

# (ledger tag, axis key, preset). A6 uses the drift decoder.
PLAN = [("A1_bash", "A1_bash", "pair"), ("A2_perl", "A2_perl", "pair"),
        ("A3t_texpgf", "A3t_texpgf", "pair"), ("A3l_texlcg", "A3l_texlcg", "pair"),
        ("A4_sha", "A4_sha", "pair"), ("A5_py27off", "A5_py27off", "pair"),
        ("A6_py27", "A6_py27", "drift")]


def wrong_seed_iter(axis, rng, prior_set, n, space):
    """Draw n wrong keys not in the axis' prior slice."""
    made = 0
    while made < n:
        if AX.AXES[axis]["kind"] == "bytes":
            k = ("WRONG_%d_%d" % (rng.randrange(2 ** 30), rng.randrange(2 ** 30))).encode()
            yield (k, 0)
            made += 1
        else:
            s = rng.randrange(0, space)
            if s in prior_set:
                continue
            # A5 is an offset axis: pair a wrong seed with a random offset 1..16
            off = rng.randrange(1, 17) if axis == "A5_py27off" else 0
            yield (s, off)
            made += 1


def prior_set_for(tag):
    if tag in ("A1_bash", "A2_perl"):
        return set(AX.cicada_int_seeds())
    if tag in ("A3t_texpgf", "A3l_texlcg"):
        return set(AX.tex_default_seeds()) | set(AX.cicada_int_seeds())
    if tag == "A5_py27off":
        return set(AX.py27_top_seeds(64))
    if tag == "A6_py27":
        import json as _J
        p = _J.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))
        return {int(e["seed"]) & 0xFFFFFFFF for e in p["order"]}
    return set()


def run_axis(tag, axis, preset_name, n):
    preset_kw = DB.PRESETS[preset_name]
    rng = random.Random(3301)
    pset = prior_set_for(tag)
    space = AX.AXES[axis]["space"] or 2 ** 32
    pmaxes, screen_pass, full_pass, passers = [], 0, 0, []
    tested = 0
    for seed, off in wrong_seed_iter(axis, rng, pset, n, space):
        tested += 1
        K = AX.AXES[axis]["fn"](seed, NEED_SCREEN + off)
        d = DB.beam_decode(C_SCREEN, K, sign=-1, o=off, beam_w=SCREEN_BEAM_W, **preset_kw)
        a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
        pm = float(a["pmax"])
        pmaxes.append(pm)
        if pm >= SCREEN_BAR:
            screen_pass += 1
            Kh = AX.AXES[axis]["fn"](seed, NEED_HIT + off)
            dec = H.HitDecode(C=C_HIT, K=Kh, o=off, preset=preset_name, n_round_adjudicated=10 ** 6)
            v = H.evaluate(dec)
            if v.hit:
                full_pass += 1
                passers.append(dict(seed=(seed.hex() if isinstance(seed, (bytes, bytearray)) else seed),
                                    offset=off, pmax=round(v.pmax, 3), rec=round(v.recovery, 4),
                                    heldout=round(v.heldout_recovery, 4)))
    pmaxes.sort()
    m = len(pmaxes)
    bar_ref = H.PM.panelmax_bar(preset_name, 10 ** 6, 0.01)
    return dict(tag=tag, axis=axis, preset=preset_name, n_wrong=tested,
                wrong_clearing_screen=screen_pass, p_clear_screen=screen_pass / tested,
                wrong_clearing_full_gate=full_pass, p_clear_full_gate=full_pass / tested,
                pmax_max=round(pmaxes[-1], 3), pmax_p99=round(pmaxes[int(0.99 * m)], 3),
                pmax_median=round(pmaxes[m // 2], 3), claim_bar_1e6=round(bar_ref, 3),
                wrong_clearing_claim_bar=sum(1 for x in pmaxes if x >= bar_ref),
                passers=passers)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--out", default=os.path.join(HERE, "redteam_ext.json"))
    args = ap.parse_args()

    ctrl = json.load(open(os.path.join(HERE, "control_ext.json")))
    validated = ctrl["validated_axes"]

    t0 = time.time()
    out = {"lane": "round24/C2-ext-skip-generators/redteam (R6)",
           "null": "seed-3301 wrong keys (random.Random(3301)), not in axis prior, SAME decoder/ciphertext",
           "n_wrong_per_axis": args.n, "axes": {}}
    print("axis         | screen_pass | full_gate_pass | pmax_max | claim_bar | clear_bar")
    print("-" * 82)
    for tag, axis, preset in PLAN:
        ok = (validated.get("A6_py27:free_drift") and validated.get("A6_py27:drift_at")) \
            if tag == "A6_py27" else validated.get(tag)
        if not ok:
            out["axes"][tag] = {"verdict": "UNVALIDATED -- skipped"}
            print(f"{tag:12s} UNVALIDATED -- skipped")
            continue
        r = run_axis(tag, axis, preset, args.n)
        out["axes"][tag] = r
        print(f"{tag:12s} | {r['wrong_clearing_screen']:4d}/{r['n_wrong']:<6d} | "
              f"{r['wrong_clearing_full_gate']:4d}/{r['n_wrong']:<9d} | {r['pmax_max']:7.3f} | "
              f"{r['claim_bar_1e6']:8.3f} | {r['wrong_clearing_claim_bar']}")
    out["elapsed_s"] = round(time.time() - t0, 1)
    out["any_full_gate_fp"] = any(isinstance(r, dict) and r.get("wrong_clearing_full_gate", 0)
                                  for r in out["axes"].values())
    with open(args.out, "w") as f:
        f.write(json.dumps(out, indent=1))
    print("-" * 82)
    print(f"any wrong key clears a full gate: {out['any_full_gate_fp']}   elapsed {out['elapsed_s']}s")
    return out


if __name__ == "__main__":
    main()
