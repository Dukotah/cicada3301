#!/usr/bin/env python3
"""Round 28 / L3 — first true Py2.7 seed(str) dictionary sweep (amd64 2-word image).

Pipeline (identical to round25/compute-tail/runner.py, which is C2/S-G3's, except the
generator seeds via the Py2.7 string-hash path at wordsize=64):

    generator : gen_py27.py27_seed(<dict string>, wordsize=64)  ->  reducer
    stage A   : driftbeam preset (pair|exact), beam_w=64, L=120  ->  I2 pmax
    stage B   : hitfn20 three-clause gate at the frozen R27 claim bars
                (pair 7.3835 / exact 7.6342 @ N=1e6, conservative for our N<1e6)

Controls (run with --controls BEFORE the sweep; every cell's null is gated on its own
planted control clearing HIT=True at recovery >= 0.90):
    pair cells  : skip_by_two encipherment (reject doubling p=0.83, j+=2)  [S1/C2 model]
    exact cells : skipdecode.encipher_keyskip (one-draw, j+=1)             [R27 S2 model]
    plant seed string: 'THE PRIMES ARE SACRED' (real tier-0 dictionary entry)

Work items run IN ORDER (PREREG amendment A1); a wall-clock budget stops the run
cleanly between seeds; progress28.json checkpoints a resume cursor per item.
A full-gate survivor STOPS everything and is FLAGGED-FOR-ORACLE (never auto-certified).

    nice -n 15 python3 sweep28.py --controls          # per-cell plants, writes controls.json
    nice -n 15 python3 sweep28.py --subsumption       # i386 identity check, subsumption.json
    nice -n 15 python3 sweep28.py --budget 19800      # the sweep (resumable)
"""
import argparse
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis/round20/S-G3", "analysis/round19/I1", "analysis/round19/I2",
          "analysis/round20/P3", "analysis/round11", "analysis/campaign18_skip",
          "src", "analysis/round20/HITFN", "analysis/round19/G3"):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

import lib_numchannel as nc          # noqa
import gen_py27 as G                 # noqa
import driftbeam as DB               # noqa
import adjudicate as AD              # noqa
import hitfn20 as H                  # noqa
import skipdecode as sk              # noqa

L_SCREEN = 120
L_HIT = 240
SCREEN_BAR = 5.0                     # frozen R27 candidate bar (well below claim bars)
SCREEN_BEAM_W = 64
WORDSIZE = 64
N_ADJ_BAR = 10 ** 6                  # frozen claim-bar reference N (conservative)
PLANT_WORD = "THE PRIMES ARE SACRED"

U = list(nc.unsolved())
C_SCREEN = U[:L_SCREEN]
C_HIT = U[:L_HIT]

PROGRESS = os.path.join(HERE, "progress28.json")
CANDS = os.path.join(HERE, "candidates28.jsonl")
DICT = os.path.join(HERE, "dictionary.jsonl")
META = os.path.join(HERE, "dict_meta.json")

# work items in priority order: (name, reducer, relation/preset, tiers, excl_r26c)
ITEMS = [
    ("r29_pair_t0",    "random29",  "pair",  (0,),  True),
    ("r29_exact_t0",   "random29",  "exact", (0,),  True),
    ("grbmod_pair_t0", "grb5_mod",  "pair",  (0,),  True),
    ("grbrej_pair_t0", "grb5_rej",  "pair",  (0,),  True),
    ("shuf_pair_t0",   "shuffle29", "pair",  (0,),  False),  # R26-C had no shuffle29
    ("r29_pair_t1",    "random29",  "pair",  (1,),  False),  # wordlist: disjoint from R26-C strs
    ("r29_exact_t1",   "random29",  "exact", (1,),  False),
    ("r29_pair_t1b",   "random29",  "pair",  (2,),  False),
    ("r29_exact_t1b",  "random29",  "exact", (2,),  False),
    ("r29_pair_t1c",   "random29",  "pair",  (3,),  False),
    ("r29_exact_t1c",  "random29",  "exact", (3,),  False),
]


def keystream(s, mode, n):
    return G.keystream(s, mode, n, wordsize=WORDSIZE)


def stage_a(s, mode, preset):
    K = keystream(s, mode, L_SCREEN * 6 + 64)
    d = DB.beam_decode(C_SCREEN, K, sign=-1, o=0, beam_w=SCREEN_BEAM_W,
                       **DB.PRESETS[preset])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return float(a["pmax"])


def stage_b(s, mode, preset):
    K = keystream(s, mode, L_HIT * 6 + 64)
    dec = H.HitDecode(C=C_HIT, K=K, o=0, preset=preset,
                      n_round_adjudicated=N_ADJ_BAR)
    v = H.evaluate(dec)
    row = H.adjudicate_hit_row(dec, kid="py27str64:%s:%s:%r" % (mode, preset, s))
    if isinstance(row, (list, tuple)):
        row = dict(zip(H.ROW_FIELDS_V3, row))
    return v, row


# ------------------------------------------------------------- planted controls
def encipher_skip_by_two(P, K, supp=0.83, seed=777):
    """S1/C2 pair-relation control model: reject a doubling key symbol w.p. supp,
    advancing the key pointer by TWO per rejection."""
    rng = random.Random(seed)
    C, j, c_prev = [], 0, None
    for p in P:
        while True:
            c = (p + K[j]) % 29
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 2
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C


def plant_cell(mode, preset):
    """Plant PLANT_WORD's w64 keystream under this cell's own relation model and
    require the REAL stage-B gate to flag it (HIT=True, recovery >= 0.90)."""
    eng = sk.eng_to_idx(open(os.path.join(LP, "data", "keys", "self_reliance.txt"),
                             encoding="utf-8", errors="ignore").read())[5000:5000 + L_HIT]
    K = keystream(PLANT_WORD, mode, L_HIT * 6 + 64)
    if preset == "pair":
        C = encipher_skip_by_two(eng, K)
    else:
        C, _skips, _used = sk.encipher_keyskip(eng, K, sign=-1, supp=0.83, seed=777)
        C = list(C)[:L_HIT]
    dec = H.HitDecode(C=C[:L_HIT], K=K, o=0, preset=preset,
                      n_round_adjudicated=N_ADJ_BAR, truth_idx=eng[:len(C[:L_HIT])])
    v = H.evaluate(dec)
    ok = bool(v.hit) and v.recovery >= 0.90
    return {"cell": "%s x %s" % (mode, preset), "seed_string": PLANT_WORD,
            "wordsize": WORDSIZE, "pmax": round(v.pmax, 3), "bar": round(v.bar, 4),
            "recovery": round(v.recovery, 4), "heldout": round(v.heldout_recovery, 4),
            "hit": bool(v.hit), "pass": ok}


def run_controls():
    cells = sorted({(mode, preset) for _, mode, preset, _, _ in ITEMS})
    out = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"), "plant_word": PLANT_WORD,
           "gate": "HIT=True AND recovery>=0.90 through the real stage-B code path",
           "cells": []}
    all_ok = True
    for mode, preset in cells:
        r = plant_cell(mode, preset)
        out["cells"].append(r)
        all_ok &= r["pass"]
        print(json.dumps(r))
    out["all_pass"] = all_ok
    json.dump(out, open(os.path.join(HERE, "controls.json"), "w"), indent=1)
    print("CONTROLS:", "ALL PASS — nulls armed" if all_ok else "FAILURE — do not sweep")
    return 0 if all_ok else 1


# ------------------------------------------------------- i386 subsumption check
def run_subsumption(n_words=200):
    """Empirical: the i386 (wordsize=32) string-seed image is keystream-identical to
    init_by_array([hash32]) — i.e. a subset of the integer word space R27-S1 swept to
    measured exhaustion (pair) and S2 is completing (exact)."""
    rows = [json.loads(l) for l in open(DICT)]
    random.Random(1).shuffle(rows)
    checked, ok = 0, 0
    for r in rows[:n_words]:
        s = r["s"]
        h32 = G.py2_str_hash(s.encode("latin-1"), 32) & 0xFFFFFFFF
        ks_str = G.keystream(s, "random29", 64, wordsize=32)
        m = G.MT19937()
        m.init_by_array([h32])
        ks_int = G.ks_random29(m, 64)
        checked += 1
        ok += (ks_str == ks_int)
    res = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "claim": "every i386 Py2.7 string seed == init_by_array([hash32]) == a member "
                    "of the [0,2^32) integer word space (R27-S1 pair-exhausted; S2 exact in flight)",
           "n_checked": checked, "n_identical": ok, "pass": ok == checked}
    json.dump(res, open(os.path.join(HERE, "subsumption.json"), "w"), indent=1)
    print(json.dumps(res))
    return 0 if res["pass"] else 1


# ------------------------------------------------------------------- the sweep
def load_progress():
    if os.path.exists(PROGRESS):
        return json.load(open(PROGRESS))
    return {"lane": "round28/L3", "items": {}, "flagged_survivors": [],
            "controls_ok_stamp": None}


def save_progress(pr):
    tmp = PROGRESS + ".tmp"
    json.dump(pr, open(tmp, "w"), indent=1)
    os.replace(tmp, PROGRESS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--subsumption", action="store_true")
    ap.add_argument("--budget", type=float, default=19800.0)
    a = ap.parse_args()
    if a.controls:
        return run_controls()
    if a.subsumption:
        return run_subsumption()

    ctrl = json.load(open(os.path.join(HERE, "controls.json")))
    if not ctrl.get("all_pass"):
        print("controls.json not all_pass — refusing to sweep")
        return 1

    meta = json.load(open(META))
    excl_imgs = set(meta["r26c_exclusion_images"])
    rows = [json.loads(l) for l in open(DICT)]
    by_tier = {}
    for r in rows:
        by_tier.setdefault(r["t"], []).append(r)

    pr = load_progress()
    pr["controls_ok_stamp"] = ctrl["date"]
    t0 = time.time()
    last_ckpt = t0
    stopped = None

    for name, mode, preset, tiers, use_excl in ITEMS:
        st = pr["items"].setdefault(name, {
            "reducer": mode, "relation": preset, "tiers": list(tiers),
            "cursor": 0, "done": 0, "skipped_excluded": 0, "status": "not-started",
            "best_pmax": -1e9, "best_seed": None, "n_stage_b": 0,
            "hist": {}, "top": []})
        if st["status"] == "complete":
            continue
        work = []
        for t in tiers:
            work.extend(by_tier.get(t, []))
        st["n_total"] = len(work)
        st["status"] = "in-progress"
        i = st["cursor"]
        while i < len(work):
            if time.time() - t0 > a.budget:
                stopped = "budget"
                break
            r = work[i]
            if use_excl and r["img"] in excl_imgs:
                st["skipped_excluded"] += 1
                i += 1
                continue
            pm = stage_a(r["s"], mode, preset)
            st["done"] += 1
            b = "%.1f" % (float(int(pm * 10)) / 10.0)
            st["hist"][b] = st["hist"].get(b, 0) + 1
            if pm > st["best_pmax"]:
                st["best_pmax"] = round(pm, 4)
                st["best_seed"] = r["s"]
            st["top"].append([round(pm, 3), r["s"]])
            if len(st["top"]) > 4000:
                st["top"] = sorted(st["top"], reverse=True)[:32]
            if pm >= SCREEN_BAR:
                v, rowb = stage_b(r["s"], mode, preset)
                st["n_stage_b"] += 1
                rowb["_item"] = name
                rowb["_stage_a_pmax"] = round(pm, 4)
                with open(CANDS, "a") as f:
                    f.write(json.dumps(rowb) + "\n")
                if v.hit:
                    surv = {"item": name, "seed_string": r["s"], "label": r["l"],
                            "img": r["img"], "pmax": round(v.pmax, 3),
                            "bar": round(v.bar, 4), "recovery": round(v.recovery, 4),
                            "heldout": round(v.heldout_recovery, 4),
                            "FLAGGED_FOR_ORACLE": True, "auto_certified": False}
                    pr["flagged_survivors"].append(surv)
                    st["cursor"] = i + 1
                    save_progress(pr)
                    print("FULL-GATE SURVIVOR — FLAGGED-FOR-ORACLE — STOPPING:",
                          json.dumps(surv))
                    return 2
            i += 1
            if time.time() - last_ckpt >= 30.0:
                st["cursor"] = i
                st["top"] = sorted(st["top"], reverse=True)[:32]
                save_progress(pr)
                last_ckpt = time.time()
        st["cursor"] = i
        st["top"] = sorted(st["top"], reverse=True)[:32]
        if i >= len(work):
            st["status"] = "complete"
        save_progress(pr)
        if stopped:
            break

    pr["elapsed_s"] = round(time.time() - t0, 1)
    pr["stopped"] = stopped or "all-items-complete"
    save_progress(pr)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("hist", "top")}
                      for k, v in pr["items"].items()}, indent=1))
    print("STOPPED:", pr["stopped"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
