"""S-MARS -- the held Marsaglia physical-randomness units as the honest control.

Runs REAL physical random keystream (Marsaglia CDROM, hash-verified, 630 MB) through the FULL
repaired Round-20 instrument -- I1 driftbeam (keyskip1 baseline + drift_rec channel) -> I2
9-register panel -> P3 calibrated panel-max null -> HITFN recovery-gated is_hit() -- and confirms
that physical randomness fires is_hit() on NOTHING. A clean null here is the calibration that lets
every OTHER S-lane negative be trusted.

MANDATORY positive control runs FIRST: a key drawn from a REAL Marsaglia pad (mod29 builder over
BITS.NN bytes) enciphering a REAL readable plaintext must recover rank-1 and fire is_hit(). Only
then is the null interpretable (doctrine: a null from an unvalidated instrument is not a negative).

  python3 smars_sweep.py --budget 780        # 13 min compute box (leaves margin under 15)

Writes: out/control.json, out/sweep.jsonl (SWEEPROW/3), out/summary.json
"""
import os, sys, json, time, glob, random, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
L6 = os.path.join(LP, "analysis", "round18", "L6-offset-marsaglia")
for _p in (os.path.join(LP, "analysis", "round19", "I1"),
           os.path.join(LP, "analysis", "round19", "I2"),
           os.path.join(LP, "analysis", "round19", "I3"),
           os.path.join(LP, "analysis", "round20", "P3"),
           os.path.join(LP, "analysis", "round20", "HITFN"),
           os.path.join(LP, "analysis", "campaign18_skip"),
           os.path.join(L6, "scripts"),
           os.path.join(LP, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import driftbeam as DB          # noqa: E402  I1 beam (keyskip1=exact, drift_rec=drift)
import adjudicate as AD         # noqa: E402  I2 9-register panel + SWEEPROW/1
import panelmax20 as PM         # noqa: E402  P3a calibrated panel-max bars
import hitfn20 as H             # noqa: E402  recovery-gated is_hit()
import skipdecode as sk         # noqa: E402  encipher_keyskip (the keyskip1 relation)
import lib_l6 as X              # noqa: E402  the physical-pad builders (mod29, nibbles, ...)
import run_fp                   # noqa: E402  run_fp.lp2() -> real 12,956-rune LP2 stream

N = 29
L = 240                          # I2 k_eff regime; the calibrated bar's segment length family
SEED = 3301
BUILDERS = ["mod29", "hi_nibble", "lo_nibble", "byte_scaled", "prime_to_idx", "nibbles"]
ISO_DIR = os.path.join(L6, "data", "iso")
PRESETS = ("exact", "drift")     # keyskip1 (clean bar) AND drift_rec (transcription-robust)


# ----------------------------------------------------------------- unit population (679 held)
def held_units():
    """The 679 held units = full 756-grid MINUS L6's 77 checkpointed units. Deterministic."""
    ck = sorted(glob.glob(os.path.join(L6, "out", "ckpt_M", "*.json")))
    done = set()
    for p in ck:
        d = json.load(open(p))
        done.add((d["pad"], d["builder"], bool(d["rev"])))
    pads = json.load(open(os.path.join(LP, "analysis", "round19", "C2",
                                       "out_verify.json")))["random_data_pads"]
    names = [p if isinstance(p, str) else p["name"] for p in pads]
    grid = [(n, b, r) for n in names for b in BUILDERS for r in (False, True)]
    held = [u for u in grid if u not in done]
    return held, len(grid), len(done)


def pad_bytes(name):
    p = os.path.join(ISO_DIR, name)
    return np.fromfile(p, dtype=np.uint8)


def keystream_from_unit(name, builder, rev, cap=None):
    """Materialise the Z29 keystream for one physical unit (pad x builder x byte-order)."""
    a = pad_bytes(name)
    if rev:
        a = a[::-1]
    if cap is not None:
        need = cap // (2 if builder == "nibbles" else 1) + 8
        a = a[:need]
    K = X.build_full(np.ascontiguousarray(a), builder)
    return [int(x) for x in K]


# ----------------------------------------------------------------- MANDATORY positive control
def positive_control():
    """Plant a REAL Marsaglia-sourced key over REAL readable plaintext; recover rank-1 + is_hit.
    Also a wrong Marsaglia key that must NOT fire is_hit."""
    from plants import _panels
    panels = _panels()
    lp2 = run_fp.lp2()  # not used for the control cipher, but proves the loader

    # a real physical key: mod29 over BITS.01 (a HELD-family builder/pad, forward order)
    K = keystream_from_unit("BITS.01", "mod29", False, cap=L * 12 + 4096)
    WK = keystream_from_unit("BITS.02", "hi_nibble", False, cap=L * 12 + 4096)  # wrong phys key

    out = {"L": L, "supp": 0.83, "key_source": "BITS.01 mod29 fwd (real Marsaglia)",
           "wrong_key_source": "BITS.02 hi_nibble fwd", "registers": {}}
    ok_all = True
    for reg in ("EN_MODERN", "LP1_REAL"):
        stream = panels[reg]
        rng = random.Random(SEED + hash(reg) % 1000)
        s = rng.randrange(0, len(stream) - L - 1)
        P = list(stream[s:s + L])
        C, _sk, _ = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=SEED)

        # correct-key hit (strict, truth supplied)
        dec = H.HitDecode(C=C, K=K, o=0, preset="exact", n_round_adjudicated=10 ** 6,
                          truth_idx=P)
        v = H.evaluate(dec)

        # wrong physical key on same ciphertext -> must NOT fire
        decw = H.HitDecode(C=C, K=WK, o=0, preset="exact", n_round_adjudicated=10 ** 6,
                           truth_idx=P)
        vw = H.evaluate(decw)

        # rank-1 check: correct key pmax must beat a battery of wrong physical keys
        wrong_pmax = []
        for i, (nm, bd, rv) in enumerate([("BITS.03", "mod29", False),
                                          ("BITS.04", "lo_nibble", True),
                                          ("BITS.05", "byte_scaled", False),
                                          ("BITS.06", "nibbles", False),
                                          ("BITS.07", "prime_to_idx", True),
                                          ("BITS.08", "mod29", True),
                                          ("BITS.09", "hi_nibble", True),
                                          ("BITS.10", "lo_nibble", False)]):
            WKi = keystream_from_unit(nm, bd, rv, cap=L * 12 + 4096)
            dw = DB.beam_decode(C, WKi, sign=-1, o=0, beam_w=400, **DB.PRESETS["exact"])
            aw = AD.adjudicate(dw["plain_idx"], translit=dw.get("translit"))
            wrong_pmax.append(float(aw["pmax"]))
        rank1 = v.pmax > max(wrong_pmax)

        reg_ok = bool(v.hit and (not vw.hit) and rank1)
        ok_all = ok_all and reg_ok
        out["registers"][reg] = {
            "correct_pmax": round(v.pmax, 3), "bar": round(v.bar, 3),
            "correct_recovery": round(v.recovery, 4),
            "correct_heldout": round(v.heldout_recovery, 4),
            "correct_is_hit": bool(v.hit), "correct_reason": v.reason,
            "wrong_key_pmax": round(vw.pmax, 3), "wrong_key_is_hit": bool(vw.hit),
            "wrong_battery_max_pmax": round(max(wrong_pmax), 3),
            "rank1_over_wrong": bool(rank1), "reg_control_pass": reg_ok,
        }
    out["control_pass"] = bool(ok_all)
    return out


# ----------------------------------------------------------------- null sweep (stated fraction)
def sweep(budget_s, offsets_per_unit=3, windows_per_offset=1):
    """Slide LP2 page-windows, decode under real physical keystream, is_hit() every decode."""
    held, grid_total, done = held_units()
    rng = random.Random(SEED)
    order = held[:]
    rng.shuffle(order)                # seed-3301 deterministic order over the 679

    lp2 = run_fp.lp2()
    n_lp2_windows = len(lp2) - L - 1

    hdr = H.header_v3("S-MARS/null", dec_preset="exact", n_round_adjudicated=10 ** 6)
    fout = open(os.path.join(HERE, "out", "sweep.jsonl"), "w")
    fout.write(json.dumps({"header": hdr}) + "\n")

    t0 = time.time()
    units_touched = 0
    decodes = 0
    hits = []
    max_pmax = {"exact": -1e9, "drift": -1e9}
    max_reco = 0.0
    pmax_clears = 0
    reg_hist = {}

    for (name, builder, rev) in order:
        if time.time() - t0 > budget_s:
            break
        # materialise a usable keystream prefix (enough for many windows + skips)
        need = L * 8 * (offsets_per_unit + 2)
        K = keystream_from_unit(name, builder, rev, cap=need + 8192)
        if len(K) < L * 4:
            continue
        units_touched += 1
        urng = random.Random(SEED + units_touched)
        for _ in range(offsets_per_unit):
            if time.time() - t0 > budget_s:
                break
            # ciphertext window: a real LP2 page-window (physical key vs the REAL cipher)
            cw = urng.randrange(0, n_lp2_windows)
            C = [int(x) for x in lp2[cw:cw + L]]
            # key offset into the physical pad
            omax = max(1, len(K) - L * 4 - 8)
            o = urng.randrange(0, omax)
            for preset in PRESETS:
                if time.time() - t0 > budget_s:
                    break
                dec = H.HitDecode(C=C, K=K, o=o, preset=preset, n_round_adjudicated=10 ** 6)
                v = H.evaluate(dec)
                decodes += 1
                max_pmax[preset] = max(max_pmax[preset], v.pmax)
                max_reco = max(max_reco, v.recovery)
                if v.clears_null:
                    pmax_clears += 1
                reg_hist[v.preg_name] = reg_hist.get(v.preg_name, 0) + 1
                row = [name, builder, int(rev), preset, cw, o,
                       round(v.pmax, 3), round(v.bar, 3), round(v.score, 3),
                       v.preg_name, round(v.recovery, 4), round(v.heldout_recovery, 4),
                       bool(v.clears_null), bool(v.hit)]
                fout.write(json.dumps(row) + "\n")
                if v.hit:
                    hits.append({"unit": [name, builder, rev], "preset": preset,
                                 "cw": cw, "o": o, "pmax": v.pmax, "recovery": v.recovery,
                                 "heldout": v.heldout_recovery, "reason": v.reason})
    fout.close()
    elapsed = time.time() - t0

    summary = {
        "lane": "S-MARS",
        "grid_total_units": grid_total, "checkpointed_by_L6": done,
        "held_units": len(held),
        "units_touched": units_touched,
        "coverage_fraction_of_held": round(units_touched / len(held), 4),
        "decodes_scored": decodes,
        "presets": list(PRESETS),
        "panelmax_bar_exact_1e6": round(PM.panelmax_bar("exact", 10 ** 6, 0.01), 4),
        "panelmax_bar_drift_1e6": round(PM.panelmax_bar("drift", 10 ** 6, 0.01), 4),
        "max_pmax_seen": {k: round(v, 3) for k, v in max_pmax.items()},
        "n_decodes_clearing_bar": pmax_clears,
        "max_recovery_seen": round(max_reco, 4),
        "n_hits": len(hits), "hits": hits,
        "preg_histogram": reg_hist,
        "elapsed_s": round(elapsed, 1), "budget_s": budget_s,
        "offsets_per_unit": offsets_per_unit,
    }
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=720.0)
    ap.add_argument("--offsets", type=int, default=3)
    args = ap.parse_args()

    print("=" * 70)
    print("S-MARS  positive control (MANDATORY, runs first)")
    print("=" * 70)
    ctl = positive_control()
    json.dump(ctl, open(os.path.join(HERE, "out", "control.json"), "w"), indent=1)
    for reg, r in ctl["registers"].items():
        print(f"  {reg:10s} correct pmax={r['correct_pmax']:.2f} (bar {r['bar']:.2f}) "
              f"rec={r['correct_recovery']:.3f} held={r['correct_heldout']:.3f} "
              f"is_hit={r['correct_is_hit']} | wrong is_hit={r['wrong_key_is_hit']} "
              f"| rank1={r['rank1_over_wrong']}  -> {r['reg_control_pass']}")
    print(f"  CONTROL_PASS = {ctl['control_pass']}")
    if not ctl["control_pass"]:
        print("  ABORT: positive control failed -> instrument blind to Marsaglia keys; null uninterpretable")
        json.dump({"aborted": True, "reason": "positive control failed", "control": ctl},
                  open(os.path.join(HERE, "out", "summary.json"), "w"), indent=1)
        return 2

    print("\n" + "=" * 70)
    print(f"S-MARS  null sweep of held physical-randomness units (budget {args.budget:.0f}s)")
    print("=" * 70)
    summ = sweep(args.budget, offsets_per_unit=args.offsets)
    summ["control"] = ctl
    json.dump(summ, open(os.path.join(HERE, "out", "summary.json"), "w"), indent=1)
    print(f"  held units: {summ['held_units']}   touched: {summ['units_touched']} "
          f"({summ['coverage_fraction_of_held']*100:.1f}% of held)")
    print(f"  decodes scored: {summ['decodes_scored']}")
    print(f"  panel-max bars: exact {summ['panelmax_bar_exact_1e6']}  drift {summ['panelmax_bar_drift_1e6']}")
    print(f"  max pmax seen: {summ['max_pmax_seen']}   (# clearing bar: {summ['n_decodes_clearing_bar']})")
    print(f"  max recovery seen: {summ['max_recovery_seen']}")
    print(f"  is_hit fired on: {summ['n_hits']} decodes")
    print(f"  elapsed: {summ['elapsed_s']}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
