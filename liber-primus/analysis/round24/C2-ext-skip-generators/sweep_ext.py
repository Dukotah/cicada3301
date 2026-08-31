#!/usr/bin/env python3
"""C2-EXT SWEEP -- broaden the skip_by_two closure across generators, offsets, and
the free_drift cousin. Re-decodes the prior-dense slice of each OPEN axis under the
control-validated decoder (pair for A1-A5, drift for A6) the beam cannot represent.

Two-stage per C2: Stage A screen (beam_w=64, L=120) -> promote pmax >= SCREEN_BAR;
Stage B full hitfn20.evaluate on survivors. Ciphertext = unsolved LP2; sign=-1.
Only real ciphertext is scored (controls already validated in control_ext.json).

    python3 sweep_ext.py [--dense 4000] [--seconds 1800]
"""
import argparse, json, os, sys, time

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
NEED_SCREEN = L_SCREEN * 6 + 64
NEED_HIT = L_HIT * 6 + 64


def stage_a(axis, seed, preset_kw, offset=0):
    K = AX.AXES[axis]["fn"](seed, NEED_SCREEN + offset)
    d = DB.beam_decode(C_SCREEN, K, sign=-1, o=offset, beam_w=SCREEN_BEAM_W, **preset_kw)
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return float(a["pmax"])


def stage_b(axis, seed, preset_name, n_adj, offset=0):
    K = AX.AXES[axis]["fn"](seed, NEED_HIT + offset)
    dec = H.HitDecode(C=C_HIT, K=K, o=offset, preset=preset_name, n_round_adjudicated=n_adj)
    v = H.evaluate(dec)
    return dict(seed=(seed.hex() if isinstance(seed, (bytes, bytearray)) else seed),
                offset=offset, hit=v.hit, pmax=round(v.pmax, 3), bar=round(v.bar, 3),
                recovery=round(v.recovery, 4), heldout=round(v.heldout_recovery, 4),
                score=round(v.score, 3), clears=v.clears_null, reason=v.reason)


def sweep_axis(axis, seed_offset_iter, preset_name, preset_kw, tstop):
    """seed_offset_iter yields (seed, offset). Returns axis result dict."""
    screened = 0
    survivors, hits = [], []
    max_pmax, best = -1e9, None
    for seed, offset in seed_offset_iter:
        if time.time() > tstop:
            break
        pm = stage_a(axis, seed, preset_kw, offset=offset)
        screened += 1
        if pm > max_pmax:
            max_pmax, best = pm, (seed.hex() if isinstance(seed, (bytes, bytearray)) else seed, offset, pm)
        if pm >= SCREEN_BAR:
            b = stage_b(axis, seed, preset_name, 10 ** 6, offset=offset)
            survivors.append(b)
            if b["hit"]:
                hits.append(b)
    n_sb = max(1, len(survivors))
    bar_ref = H.PM.panelmax_bar(preset_name, 10 ** 6, 0.01)
    bar_nb = H.PM.panelmax_bar(preset_name, n_sb, 0.01)
    for s in survivors:
        s["bar_at_n_stageb"] = round(bar_nb, 3)
        s["clears_at_n_stageb"] = bool(s["pmax"] >= bar_nb)
    return dict(axis=axis, label=AX.AXES[axis]["label"], preset=preset_name,
                words_screened=screened,
                fraction_of_space=(screened / AX.AXES[axis]["space"]) if AX.AXES[axis]["space"] else None,
                survivors_screen=len(survivors), hits=len(hits),
                hits_at_n_stageb=sum(1 for s in survivors if s.get("clears_at_n_stageb") and s["hit"]),
                panelmax_bar_ref_1e6=round(bar_ref, 3), panelmax_bar_at_n_stageb=round(bar_nb, 3),
                n_stage_b=n_sb, max_pmax=round(max_pmax, 3), best=best,
                survivor_rows=survivors, hit_rows=hits)


# --------------------------------------------------------------- per-axis iterators
def dense_ints(exclude, count, start=1):
    w, made = start, 0
    while made < count:
        if w not in exclude:
            yield (w, 0)
            made += 1
        w += 1


def build_iters(dense):
    cic = AX.cicada_int_seeds()
    cicset = set(cic)
    iters = {}

    def int_axis(prior, prior_set, dense_start=1):
        def gen():
            for s in prior:
                yield (s, 0)
            for so in dense_ints(prior_set, dense, start=dense_start):
                yield so
        return gen()

    # A1 bash, A2 perl: cicada int seeds + dense contiguous
    iters["A1_bash"] = lambda: int_axis(cic, cicset)
    iters["A2_perl"] = lambda: int_axis(cic, cicset)
    # A3 tex: tex default/date seeds (thin) + cicada ints + dense
    texd = AX.tex_default_seeds()
    texset = set(texd) | cicset

    def tex_gen():
        for s in texd:
            yield (s, 0)
        for s in cic:
            if s < 2 ** 31:
                yield (s, 0)
        for so in dense_ints(texset, dense, start=1):
            yield so
    iters["A3t_texpgf"] = tex_gen
    iters["A3l_texlcg"] = tex_gen
    # A4 sha: full B04 byte dictionary (no offset)
    b04 = AX.b04_byte_seeds()
    iters["A4_sha"] = lambda: ((b, 0) for b in b04)
    # A5 py27 offsets: top-64 prior seeds x offsets 1..16
    top = AX.py27_top_seeds(64)
    iters["A5_py27off"] = lambda: ((s, o) for s in top for o in range(1, 17))
    # A6 free_drift cousin, DRIFT decoder: 433 prior seeds + dense, offset 0
    import json as _J
    prior = _J.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))
    pw = [int(e["seed"]) & 0xFFFFFFFF for e in prior["order"]]
    pwset = set(pw)
    iters["A6_py27"] = lambda: int_axis(pw, pwset)
    return iters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dense", type=int, default=4000,
                    help="dense contiguous seeds appended per int-seed axis")
    ap.add_argument("--seconds", type=float, default=3600, help="global time box")
    ap.add_argument("--out", default=os.path.join(HERE, "sweep_ext.json"))
    args = ap.parse_args()

    ctrl = json.load(open(os.path.join(HERE, "control_ext.json")))
    validated = ctrl["validated_axes"]

    # map ledger-tag axis -> (axis key, preset name, preset kw). A6 combines the two
    # free_drift/drift_at control validations into one drift-decoded sweep axis.
    axis_plan = [
        ("A1_bash", "A1_bash", "pair"),
        ("A2_perl", "A2_perl", "pair"),
        ("A3t_texpgf", "A3t_texpgf", "pair"),
        ("A3l_texlcg", "A3l_texlcg", "pair"),
        ("A4_sha", "A4_sha", "pair"),
        ("A5_py27off", "A5_py27off", "pair"),
        ("A6_py27", "A6_py27", "drift"),
    ]

    t0 = time.time()
    tstop = t0 + args.seconds
    iters = build_iters(args.dense)
    results = {}
    for tag, axis, preset_name in axis_plan:
        # an axis is scored only if its control validated. A6 validated iff BOTH cousins did.
        if tag == "A6_py27":
            ok = validated.get("A6_py27:free_drift") and validated.get("A6_py27:drift_at")
        else:
            ok = validated.get(tag)
        if not ok:
            results[tag] = dict(axis=axis, preset=preset_name, verdict="UNVALIDATED",
                                note="positive control did not validate; no null claimed")
            print(f"{tag:12s} UNVALIDATED -- skipped")
            continue
        preset_kw = DB.PRESETS[preset_name]
        r = sweep_axis(axis, iters[tag](), preset_name, preset_kw, tstop)
        r["verdict"] = "NULL" if r["hits"] == 0 else "HIT-FLAGGED-FOR-ORACLE"
        results[tag] = r
        fr = r["fraction_of_space"]
        print(f"{tag:12s} screened={r['words_screened']:6d}  survivors={r['survivors_screen']:3d}  "
              f"hits={r['hits']}  maxpmax={r['max_pmax']:6.3f}  bar={r['panelmax_bar_ref_1e6']:.3f}  "
              f"frac={('%.2e' % fr) if fr else 'n/a':>8}  {r['verdict']}")

    out = {
        "lane": "round24/C2-ext-skip-generators/sweep",
        "decoders": {"pair": "driftbeam keyskip2 (skip_by_two-exact)",
                     "drift": "driftbeam permissive lam=12 (free_drift/drift_at cousin)"},
        "ciphertext": "lib_numchannel.unsolved(); screen L=120, gate L=240; sign=-1",
        "screen_bar": SCREEN_BAR, "dense_per_axis": args.dense,
        "elapsed_s": round(time.time() - t0, 1),
        "axes": results,
        "any_hit": any(isinstance(r, dict) and r.get("hits", 0) for r in results.values()),
    }
    with open(args.out, "w") as f:
        f.write(json.dumps(out, indent=1))
    print(f"\nwrote {args.out}   any_hit={out['any_hit']}   elapsed={out['elapsed_s']}s")
    return out


if __name__ == "__main__":
    main()
