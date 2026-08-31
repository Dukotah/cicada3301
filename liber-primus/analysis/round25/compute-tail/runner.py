#!/usr/bin/env python3
"""Round 25 -- COMPUTE-TAIL -- resumable, checkpointed sweep of the Py2.7-MT 2^32 tail.

The one remaining runnable lane (owner's call, low prior, accepted). This sweeps a
CONTIGUOUS RANGE of Py2.7 MT19937 init_by_array([w]) words under the SAME
control-validated pipeline as round24/C2-skip-by-two and round20/S-G3:

    generator : Py2.7 MT19937().init_by_array([w]); reducer random29   (gen_py27)
    decoder   : driftbeam preset 'pair' (mode keyskip2) -- the skip_by_two-exact
                relation the beam cannot represent (control-validated in C2)
    hit gate  : hitfn20 three-clause recovery-gated predicate
                (pmax >= panel-max null bar AND rune-index recovery >= 0.90
                 AND held-out-3/4 recovery >= 0.90). Score alone is never a hit.

It is IDENTICAL to C2's sweep except:
  * it sweeps a contiguous TAIL range instead of the prior slice, and
  * it CHECKPOINTS a next-seed cursor to progress.json so the next chunk resumes
    exactly where this one stopped, and
  * it EXCLUDES the already-swept coverage (C2 dense baseline [0, DENSE_MAX) and the
    433 prior words + their +/-512 neighbourhood) so coverage is never double-counted.

A survivor of the FULL gate STOPS the sweep immediately and is FLAGGED-FOR-ORACLE
(never auto-certified -- the no-oracle proxy is leaky, R21-L1).

    python3 runner.py --seconds 1300            # run one time-boxed chunk, resume from cursor
    python3 runner.py --seconds 60 --self-test  # planted-seed recovery=1.000 spot-check + short run
"""
import argparse, json, os, random, sys, time

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

# ---- frozen pipeline constants (identical to round24/C2 sweep) ---------------
PRESET = "pair"                       # keyskip2 -- skip_by_two-exact, control-validated
L_SCREEN = 120
L_HIT = 240
SCREEN_BAR = 5.0                      # frozen (= S-G3 / C2): well below the pair claim bar
SCREEN_BEAM_W = 64
MODE = "random29"
SPACE = 2 ** 32

# ---- already-swept coverage that this tail must NOT recount ------------------
# C2 dense baseline swept the first 200,000 words not in the prior 'seen' set,
# counting up from w=0. So [0, DENSE_MAX) is (modulo the sparse prior words in it,
# of which there are none below 20.1M) already covered. Start the tail past it.
DENSE_MAX = 200_000
TAIL_START_DEFAULT = 3_000_000        # safely past the dense baseline

U = list(nc.unsolved())
C_SCREEN = U[:L_SCREEN]
C_HIT = U[:L_HIT]

PROGRESS = os.path.join(HERE, "progress.json")


# ----------------------------------------------------------------- generator
def word_stream(w, n):
    r = G.MT19937()
    r.init_by_array([w] if w else [0])
    return G.REDUCERS[MODE](r, n)


# ----------------------------------------------------------------- excl set
def build_exclusion():
    """The scattered prior+neighbourhood words already swept by S-G3 / C2 (all >= 20.1M,
    so a tail starting at 3M only meets them once it climbs there). Returned as a set so
    the cursor skips them without recounting coverage."""
    prior = json.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))
    seeds = [int(e["seed"]) & 0xFFFFFFFF for e in prior["order"]]
    excl = set(seeds)
    for s in seeds[:64]:
        for d in range(-512, 513):
            excl.add((s + d) & 0xFFFFFFFF)
    return excl


# ----------------------------------------------------------------- pipeline
def stage_a(w):
    K = word_stream(w, L_SCREEN * 6 + 64)
    d = DB.beam_decode(C_SCREEN, K, sign=-1, o=0, beam_w=SCREEN_BEAM_W, **DB.PRESETS[PRESET])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return float(a["pmax"])


def stage_b(w, n_adj):
    K = word_stream(w, L_HIT * 6 + 64)
    dec = H.HitDecode(C=C_HIT, K=K, o=0, preset=PRESET, n_round_adjudicated=n_adj)
    v = H.evaluate(dec)
    return dict(w=w, hit=bool(v.hit), pmax=round(v.pmax, 3), bar=round(v.bar, 3),
                recovery=round(v.recovery, 4), heldout=round(v.heldout_recovery, 4),
                preg=v.preg_name, score=round(v.score, 3), clears=bool(v.clears_null),
                reason=v.reason)


# ----------------------------------------------------- red-team sanity control
def planted_seed_selftest(seed=777):
    """Confirm the SAME control-validated pipeline recovers a planted seed at recovery
    1.000 under the pair (keyskip2) relation, so a null this chunk is a true negative and
    not a broken scan. We encipher held-out English under the skip_by_two relation with
    THIS seed's random29 keystream, then decode with the SAME key via hitfn20's truth_idx
    (strict) path and require rune-index recovery == 1.000."""
    # held-out English plaintext (self_reliance), transliterated to rune indices
    import skipdecode as sk
    with open(os.path.join(LP, "data", "keys", "self_reliance.txt"),
              encoding="utf-8", errors="ignore") as f:
        eng = sk.eng_to_idx(f.read())[5000:5000 + L_HIT]
    K = word_stream(seed, L_HIT * 6 + 64)
    # skip_by_two encipherment (C2 control model), supp=0.83
    rng = random.Random(seed)
    C, j, c_prev = [], 0, None
    for p in eng:
        while True:
            c = (p + K[j]) % nc.__dict__.get("N", 29) if False else (p + K[j]) % 29
            if c_prev is not None and c == c_prev and rng.random() < 0.83:
                j += 2
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    dec = H.HitDecode(C=C, K=K, o=0, preset=PRESET, n_round_adjudicated=10 ** 6,
                      truth_idx=eng[:len(C)])
    v = H.evaluate(dec)
    ok = v.recovery >= 0.999
    return {"seed": seed, "recovery": round(v.recovery, 4),
            "heldout": round(v.heldout_recovery, 4), "pmax": round(v.pmax, 3),
            "bar": round(v.bar, 3), "hit": bool(v.hit), "recovery_1000": bool(ok)}


# ----------------------------------------------------------------- checkpoint
def load_progress(tail_start):
    if os.path.exists(PROGRESS):
        return json.load(open(PROGRESS))
    return {
        "lane": "round25/compute-tail",
        "space": SPACE,
        "generator": "Py2.7 MT19937 init_by_array([w]); reducer random29",
        "decoder": "driftbeam preset 'pair' (keyskip2) -- skip_by_two-exact, control-validated (C2)",
        "hit_gate": "hitfn20 three-clause: pmax>=panelmax_bar AND recovery>=0.90 AND heldout-3/4>=0.90",
        "excluded_regions": {
            "dense_baseline_contiguous": [0, DENSE_MAX],
            "prior_plus_neighbourhood_words": 45975,
            "note": "C2/S-G3 already swept [0,%d) plus the 433 prior words + their +/-512 nbhd "
                    "(all >= 20.1M). Tail starts at %d to avoid the dense baseline; scattered "
                    "prior words are skipped via the exclusion set." % (DENSE_MAX, tail_start),
        },
        "tail_start": tail_start,
        "next_seed": tail_start,          # cursor: next word to sweep
        "seeds_done": 0,                  # cumulative tail words screened (excludes skipped)
        "seeds_skipped_excluded": 0,      # words skipped because already swept
        "best_pmax": -1e9,
        "best_word": None,
        "flagged_survivors": [],          # full-gate hits -> FLAGGED-FOR-ORACLE
        "chunks": [],                     # per-chunk log
    }


def save_progress(pr):
    tmp = PROGRESS + ".tmp"
    with open(tmp, "w") as f:
        json.dump(pr, f, indent=1)
    os.replace(tmp, PROGRESS)


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=1300,
                    help="wall-clock budget for this chunk's sweeping")
    ap.add_argument("--tail-start", type=int, default=TAIL_START_DEFAULT)
    ap.add_argument("--self-test", action="store_true",
                    help="run the planted-seed recovery=1.000 spot-check first")
    args = ap.parse_args()

    selftest = None
    if args.self_test:
        selftest = planted_seed_selftest()
        print("SELF-TEST (planted seed, pair relation):", json.dumps(selftest))
        if not selftest["recovery_1000"]:
            print("SELF-TEST FAILED -- pipeline does not recover a plant; ABORT (broken scan).")
            sys.exit(1)

    excl = build_exclusion()
    pr = load_progress(args.tail_start)

    t0 = time.time()
    w = pr["next_seed"]
    chunk_screened = 0
    chunk_skipped = 0
    chunk_best_pmax = -1e9
    chunk_best_word = None
    hit_row = None

    # checkpoint cadence: every ~30s of wall clock (cheap, atomic write)
    last_ckpt = t0
    CKPT_EVERY = 30.0

    while time.time() - t0 < args.seconds and w < SPACE:
        if w in excl:
            chunk_skipped += 1
            pr["seeds_skipped_excluded"] += 1
            w += 1
            continue
        pm = stage_a(w)
        chunk_screened += 1
        pr["seeds_done"] += 1
        if pm > chunk_best_pmax:
            chunk_best_pmax = pm
            chunk_best_word = w
        if pm > pr["best_pmax"]:
            pr["best_pmax"] = pm
            pr["best_word"] = w
        if pm >= SCREEN_BAR:
            b = stage_b(w, 10 ** 6)
            if b["hit"]:
                # FULL GATE CLEARED -> STOP, FLAG-FOR-ORACLE, save everything.
                b["FLAGGED_FOR_ORACLE"] = True
                b["auto_certified"] = False
                pr["flagged_survivors"].append(b)
                hit_row = b
                w += 1
                break
        w += 1
        # periodic checkpoint so a kill loses at most CKPT_EVERY of progress
        if time.time() - last_ckpt >= CKPT_EVERY:
            pr["next_seed"] = w
            save_progress(pr)
            last_ckpt = time.time()

    elapsed = time.time() - t0
    pr["next_seed"] = w                    # resume cursor for the NEXT chunk

    # re-express the panel-max bar (reference N=1e6) for the report
    bar_ref = H.PM.panelmax_bar(PRESET, 10 ** 6, 0.01)

    chunk = {
        "chunk_index": len(pr["chunks"]) + 1,
        "start_word": pr["chunks"][-1]["end_word"] if pr["chunks"] else args.tail_start,
        "end_word": w,
        "seeds_screened_this_chunk": chunk_screened,
        "seeds_skipped_excluded_this_chunk": chunk_skipped,
        "elapsed_s": round(elapsed, 1),
        "throughput_seeds_per_s": round(chunk_screened / elapsed, 1) if elapsed else None,
        "best_pmax_this_chunk": round(chunk_best_pmax, 3) if chunk_best_pmax > -1e8 else None,
        "best_word_this_chunk": chunk_best_word,
        "hit_flagged": bool(hit_row),
        "hit_row": hit_row,
        "claim_bar_pair_1e6": round(bar_ref, 3),
        "self_test": selftest,
    }
    pr["chunks"].append(chunk)

    # cumulative coverage: tail words done + the already-swept baseline coverage
    tail_done = pr["seeds_done"]
    baseline_done = DENSE_MAX + 45975      # C2 dense baseline + prior+nbhd (approx, no overlap)
    cumulative_covered = tail_done + baseline_done
    pr["cumulative_words_covered_incl_baseline"] = cumulative_covered
    pr["cumulative_coverage_fraction_2pow32"] = cumulative_covered / SPACE

    save_progress(pr)

    report = {
        "lane": "round25/compute-tail",
        "chunk": chunk,
        "cumulative": {
            "tail_seeds_done": tail_done,
            "baseline_already_swept": baseline_done,
            "cumulative_words_covered": cumulative_covered,
            "coverage_fraction_2pow32": cumulative_covered / SPACE,
            "coverage_pct_2pow32": 100.0 * cumulative_covered / SPACE,
            "next_seed_cursor": w,
        },
        "verdict": ("HIT-FLAGGED-FOR-ORACLE" if hit_row else "clean null"),
        "best_pmax_vs_bar": {"best_pmax_this_chunk": chunk["best_pmax_this_chunk"],
                             "claim_bar_pair_1e6": round(bar_ref, 3),
                             "margin_below_bar": (round(bar_ref - chunk["best_pmax_this_chunk"], 3)
                                                  if chunk["best_pmax_this_chunk"] is not None else None)},
    }
    print(json.dumps(report, indent=1))
    return report


if __name__ == "__main__":
    main()
