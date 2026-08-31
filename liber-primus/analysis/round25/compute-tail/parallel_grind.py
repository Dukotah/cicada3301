#!/usr/bin/env python3
"""Round 25 -- COMPUTE-TAIL -- 6-core PARALLEL supervisor over the Py2.7-MT 2^32 tail.

This is a SUPERVISOR ONLY. It does NOT reimplement the cryptographic pipeline: it
imports `runner.py`'s already-control-validated functions (stage_a screen, stage_b
three-clause hitfn20 gate, word_stream generator, build_exclusion) and drives them
across 6 disjoint contiguous seed bands, one worker per core.

Design (owner chose full 6-core power):

  * The remaining tail [RESUME_START .. 2^32) is split into 6 EQUAL contiguous bands.
    RESUME_START defaults to the chunk-1 checkpoint cursor (progress.json.next_seed).
    Each band [band_start, band_end) is a WORKER's territory -- disjoint, contiguous.

  * Each worker owns its OWN checkpoint file progress_w{i}.json (cursor / seeds_done /
    seeds_skipped / best_pmax / best_word / flagged_survivors). NO shared mutable state,
    so workers never collide and a crash of one loses at most CKPT_EVERY seconds of ITS
    own progress. On restart each worker resumes from its own file's cursor.

  * The SAME exclusion set runner.build_exclusion() (the 45,975 prior+neighbourhood
    words, all >= 20.1M) is applied per worker so coverage is never double counted.

  * HIT handling: if a worker's stage_a screen clears SCREEN_BAR it runs the full
    stage_b three-clause gate; if that gate fires (pmax>=pair-bar AND recovery>=0.90
    AND held-out>=0.90) the worker writes HIT.json and sets a shared multiprocessing
    Event that STOPS all workers. The supervisor then exits NON-ZERO with the hit as the
    headline. The hit is FLAGGED-FOR-ORACLE (R21-L1), never auto-certified.

  * --status reads the 6 progress files (no worker contact) and prints aggregate
    coverage % of 2^32, per-worker cursors, global best pmax, and any HIT.

    python3 parallel_grind.py                 # launch the continuous 6-core grind
    python3 parallel_grind.py --status        # cheap poll of the 6 checkpoint files
    python3 parallel_grind.py --seconds 60    # time-boxed (smoke test / bounded run)
    python3 parallel_grind.py --reset         # wipe worker checkpoints (fresh partition)
    python3 parallel_grind.py --self-test     # runner planted-seed self-test, then exit
"""
import argparse, json, multiprocessing as mp, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import runner  # noqa: reuse its control-validated pipeline verbatim

N_WORKERS = 6
SPACE = runner.SPACE                       # 2**32
SCREEN_BAR = runner.SCREEN_BAR             # frozen 5.0 (identical to single-core)
CKPT_EVERY = 30.0                          # atomic checkpoint cadence (s)
HIT_POLL = 1000                            # check the stop-event every N screened words

# Where the parallel campaign resumes from: the chunk-1 single-core cursor.
def default_resume_start():
    p = os.path.join(HERE, "progress.json")
    if os.path.exists(p):
        try:
            return int(json.load(open(p))["next_seed"])
        except Exception:
            pass
    return runner.TAIL_START_DEFAULT

HIT_FILE = os.path.join(HERE, "HIT.json")


def wpath(i):
    return os.path.join(HERE, "progress_w%d.json" % i)


# ----------------------------------------------------------------- partition
def compute_bands(resume_start):
    """6 disjoint contiguous bands covering [resume_start, SPACE)."""
    total = SPACE - resume_start
    step = total // N_WORKERS
    bands = []
    for i in range(N_WORKERS):
        b0 = resume_start + i * step
        b1 = resume_start + (i + 1) * step if i < N_WORKERS - 1 else SPACE
        bands.append((b0, b1))
    return bands


# ----------------------------------------------------------------- checkpoint
def load_worker(i, band):
    p = wpath(i)
    if os.path.exists(p):
        st = json.load(open(p))
        # honour the stored cursor (resume), but keep the band fixed
        st.setdefault("flagged_survivors", [])
        return st
    b0, b1 = band
    return {
        "worker": i,
        "band_start": b0,
        "band_end": b1,
        "cursor": b0,                 # next word this worker will sweep
        "seeds_done": 0,              # screened (excludes skipped)
        "seeds_skipped_excluded": 0,
        "best_pmax": -1e9,
        "best_word": None,
        "flagged_survivors": [],
        "done": False,                # band fully swept
    }


def save_worker(st):
    p = wpath(st["worker"])
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f, indent=1)
    os.replace(tmp, p)


# ----------------------------------------------------------------- worker
def worker_main(i, band, seconds, stop_evt, plant_at=None):
    """Sweep this worker's band start->end through runner's pipeline.

    plant_at: TEST-ONLY. If set to (seed, truth_idx), the worker treats that seed as
    a forced full-gate hit when the cursor reaches it -- used by the in-band planted-hit
    validation to prove the parallel HIT path fires. Never used in a real grind.
    """
    excl = runner.build_exclusion()
    st = load_worker(i, band)
    if st.get("done"):
        return
    b_end = st["band_end"]
    w = st["cursor"]
    t0 = time.time()
    last_ckpt = t0
    since_poll = 0

    try:
        while w < b_end:
            if seconds is not None and time.time() - t0 >= seconds:
                break
            if stop_evt.is_set():
                break
            if w in excl:
                st["seeds_skipped_excluded"] += 1
                w += 1
                continue

            # ---- TEST-ONLY forced-hit injection (parallel HIT path validation) ----
            if plant_at is not None and w == plant_at[0]:
                b = _planted_stage_b(w, plant_at[1])
                st["seeds_done"] += 1
                if b["hit"]:
                    _fire_hit(i, w, b, st, stop_evt)
                    w += 1
                    st["cursor"] = w
                    save_worker(st)
                    return
                w += 1
                continue

            pm = runner.stage_a(w)
            st["seeds_done"] += 1
            if pm > st["best_pmax"]:
                st["best_pmax"] = pm
                st["best_word"] = w
            if pm >= SCREEN_BAR:
                b = runner.stage_b(w, 10 ** 6)
                if b["hit"]:
                    _fire_hit(i, w, b, st, stop_evt)
                    w += 1
                    st["cursor"] = w
                    save_worker(st)
                    return
            w += 1
            since_poll += 1

            if since_poll >= HIT_POLL:
                since_poll = 0
                if stop_evt.is_set():
                    break
            if time.time() - last_ckpt >= CKPT_EVERY:
                st["cursor"] = w
                save_worker(st)
                last_ckpt = time.time()
    finally:
        st["cursor"] = w
        if w >= b_end:
            st["done"] = True
        save_worker(st)


def _fire_hit(i, w, b, st, stop_evt):
    b["FLAGGED_FOR_ORACLE"] = True
    b["auto_certified"] = False
    b["worker"] = i
    st["flagged_survivors"].append(b)
    # write HIT.json atomically, then signal every worker to stop
    rec = {
        "worker": i,
        "seed": w,
        "page": "LP2 0-54 (lib_numchannel.unsolved)",
        "recovery": b.get("recovery"),
        "heldout": b.get("heldout"),
        "pmax": b.get("pmax"),
        "bar": b.get("bar"),
        "clears_null": b.get("clears"),
        "reason": b.get("reason"),
        "decode": b,
        "FLAGGED_FOR_ORACLE": True,
        "auto_certified": False,
        "note": "R21-L1: no-oracle proxy is leaky. Flagged for ORACLE, NOT certified.",
    }
    tmp = HIT_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(rec, f, indent=1)
    os.replace(tmp, HIT_FILE)
    stop_evt.set()


def _planted_stage_b(w, truth_idx):
    """TEST-ONLY: enciphers held-out English under the skip_by_two relation with THIS
    seed and decodes with the SAME seed via hitfn20's strict truth_idx path -- i.e. the
    exact construction runner.planted_seed_selftest() uses, but routed through the
    PARALLEL worker so we prove the parallel HIT path flags a real full-gate clearance."""
    import random
    import lib_numchannel as nc
    import hitfn20 as H
    K = runner.word_stream(w, runner.L_HIT * 6 + 64)
    rng = random.Random(w)
    C, j, c_prev = [], 0, None
    for p in truth_idx:
        while True:
            c = (p + K[j]) % 29
            if c_prev is not None and c == c_prev and rng.random() < 0.83:
                j += 2
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    dec = H.HitDecode(C=C, K=K, o=0, preset=runner.PRESET, n_round_adjudicated=10 ** 6,
                      truth_idx=truth_idx[:len(C)])
    v = H.evaluate(dec)
    return dict(w=w, hit=bool(v.hit), pmax=round(v.pmax, 3), bar=round(v.bar, 3),
                recovery=round(v.recovery, 4), heldout=round(v.heldout_recovery, 4),
                preg=v.preg_name, score=round(v.score, 3), clears=bool(v.clears_null),
                reason=v.reason)


# ----------------------------------------------------------------- status
def read_status(resume_start_for_missing):
    bands = compute_bands(resume_start_for_missing)
    workers = []
    total_done = 0
    total_skipped = 0
    global_best = -1e9
    global_best_word = None
    survivors = []
    for i in range(N_WORKERS):
        p = wpath(i)
        if os.path.exists(p):
            st = json.load(open(p))
        else:
            b0, b1 = bands[i]
            st = {"worker": i, "band_start": b0, "band_end": b1, "cursor": b0,
                  "seeds_done": 0, "seeds_skipped_excluded": 0, "best_pmax": None,
                  "best_word": None, "flagged_survivors": [], "done": False}
        total_done += st.get("seeds_done", 0)
        total_skipped += st.get("seeds_skipped_excluded", 0)
        bp = st.get("best_pmax")
        if bp is not None and bp > global_best:
            global_best = bp
            global_best_word = st.get("best_word")
        survivors += st.get("flagged_survivors", [])
        b0 = st["band_start"]; b1 = st["band_end"]; cur = st["cursor"]
        span = max(b1 - b0, 1)
        workers.append({
            "worker": i,
            "band": [b0, b1],
            "cursor": cur,
            "band_progress_pct": round(100.0 * (cur - b0) / span, 4),
            "seeds_done": st.get("seeds_done", 0),
            "seeds_skipped": st.get("seeds_skipped_excluded", 0),
            "best_pmax": (round(bp, 3) if bp not in (None,) else None),
            "done": st.get("done", False),
        })

    # aggregate coverage of 2^32 = parallel tail work + the single-core chunk-1 tail work
    # already recorded in progress.json + the C2/S-G3 baseline already swept.
    chunk1_tail = 0
    p1 = os.path.join(HERE, "progress.json")
    if os.path.exists(p1):
        try:
            chunk1_tail = int(json.load(open(p1)).get("seeds_done", 0))
        except Exception:
            chunk1_tail = 0
    baseline = runner.DENSE_MAX + 45975
    cumulative = total_done + total_skipped + chunk1_tail + baseline

    hit = None
    if os.path.exists(HIT_FILE):
        hit = json.load(open(HIT_FILE))

    return {
        "lane": "round25/compute-tail (6-core parallel)",
        "workers": workers,
        "aggregate": {
            "parallel_seeds_done": total_done,
            "parallel_seeds_skipped_excluded": total_skipped,
            "chunk1_singlecore_tail_seeds": chunk1_tail,
            "baseline_already_swept": baseline,
            "cumulative_words_covered": cumulative,
            "coverage_fraction_2pow32": cumulative / SPACE,
            "coverage_pct_2pow32": 100.0 * cumulative / SPACE,
        },
        "global_best_pmax": (round(global_best, 3) if global_best > -1e8 else None),
        "global_best_word": global_best_word,
        "flagged_survivors": survivors,
        "HIT": hit,
    }


def print_status(resume_start_for_missing):
    s = read_status(resume_start_for_missing)
    print("=== round25/compute-tail :: 6-core parallel status ===")
    for w in s["workers"]:
        print("  w%d band [%d, %d)  cursor=%d  %.4f%% of band  done=%d skip=%d  best_pmax=%s%s"
              % (w["worker"], w["band"][0], w["band"][1], w["cursor"],
                 w["band_progress_pct"], w["seeds_done"], w["seeds_skipped"],
                 w["best_pmax"], "  [BAND COMPLETE]" if w["done"] else ""))
    a = s["aggregate"]
    print("  ---")
    print("  parallel seeds screened : %d  (skipped-excluded %d)"
          % (a["parallel_seeds_done"], a["parallel_seeds_skipped_excluded"]))
    print("  + chunk-1 single-core   : %d" % a["chunk1_singlecore_tail_seeds"])
    print("  + baseline already swept: %d" % a["baseline_already_swept"])
    print("  cumulative 2^32 coverage: %d words = %.6f%%"
          % (a["cumulative_words_covered"], a["coverage_pct_2pow32"]))
    print("  global best pmax        : %s  (word %s)  [pair claim bar 7.384]"
          % (s["global_best_pmax"], s["global_best_word"]))
    if s["HIT"]:
        print("  *** HIT FLAGGED-FOR-ORACLE ***  seed=%s recovery=%s heldout=%s pmax=%s"
              % (s["HIT"]["seed"], s["HIT"]["recovery"], s["HIT"]["heldout"], s["HIT"]["pmax"]))
    elif s["flagged_survivors"]:
        print("  *** %d flagged survivor(s) ***" % len(s["flagged_survivors"]))
    else:
        print("  HIT: none")
    return s


# ----------------------------------------------------------------- reset
def reset_workers():
    for i in range(N_WORKERS):
        for suff in ("", ".tmp"):
            p = wpath(i) + suff
            if os.path.exists(p):
                os.remove(p)
    if os.path.exists(HIT_FILE):
        os.remove(HIT_FILE)


# ----------------------------------------------------------------- supervise
def supervise(seconds, resume_start, plant=None):
    if os.path.exists(HIT_FILE):
        print("HIT.json already present from a prior run:")
        print(open(HIT_FILE).read())
        print("Refusing to launch over an un-cleared HIT. Move/inspect HIT.json first.")
        return 2

    bands = compute_bands(resume_start)
    # print the partition once so the launch is auditable
    print("6-core parallel grind :: resume_start=%d  space=%d" % (resume_start, SPACE))
    for i, (b0, b1) in enumerate(bands):
        st = load_worker(i, bands[i])
        print("  w%d band [%d, %d)  width=%d  resume-cursor=%d"
              % (i, b0, b1, b1 - b0, st["cursor"]))
    sys.stdout.flush()

    ctx = mp.get_context("spawn")
    stop_evt = ctx.Event()
    procs = []
    for i in range(N_WORKERS):
        pa = plant if (plant is not None and plant[0] == i) else None
        pa_arg = (plant[1], plant[2]) if pa is not None else None
        p = ctx.Process(target=worker_main,
                        args=(i, bands[i], seconds, stop_evt, pa_arg))
        p.start()
        procs.append(p)

    t0 = time.time()
    try:
        for p in procs:
            p.join()
    except KeyboardInterrupt:
        print("\nInterrupted -- signalling workers to checkpoint and stop...")
        stop_evt.set()
        for p in procs:
            p.join(timeout=CKPT_EVERY + 10)
    elapsed = time.time() - t0

    s = read_status(resume_start)
    total = s["aggregate"]["parallel_seeds_done"]
    thr = total / elapsed if elapsed else 0
    print("\n--- supervisor summary ---")
    print("elapsed %.1fs  parallel seeds screened %d  aggregate throughput %.1f seeds/s"
          % (elapsed, total, thr))
    print_status(resume_start)

    if os.path.exists(HIT_FILE):
        print("\n*** HIT FLAGGED-FOR-ORACLE -- sweep stopped. See HIT.json. NOT auto-certified. ***")
        return 3
    return 0


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=None,
                    help="wall-clock budget (default: run until bands exhausted / HIT / Ctrl-C)")
    ap.add_argument("--resume-start", type=int, default=None,
                    help="override the parallel partition start (default: progress.json cursor)")
    ap.add_argument("--status", action="store_true", help="poll the 6 checkpoint files and exit")
    ap.add_argument("--reset", action="store_true", help="wipe worker checkpoints + HIT.json")
    ap.add_argument("--self-test", action="store_true",
                    help="runner planted-seed self-test (recovery 1.000 / HIT=True) then exit")
    ap.add_argument("--plant", type=str, default=None,
                    help="TEST-ONLY 'worker,seed' -- force a planted full-gate hit in that "
                         "worker's band to validate the parallel HIT path")
    args = ap.parse_args()

    resume_start = args.resume_start if args.resume_start is not None else default_resume_start()

    if args.self_test:
        st = runner.planted_seed_selftest()
        print("SELF-TEST (planted seed, pair relation):", json.dumps(st))
        return 0 if st["recovery_1000"] and st["hit"] else 1

    if args.status:
        print_status(resume_start)
        return 0

    if args.reset:
        reset_workers()
        print("worker checkpoints + HIT.json cleared.")
        return 0

    plant = None
    if args.plant:
        wi, seed = args.plant.split(",")
        wi, seed = int(wi), int(seed)
        # build the held-out English truth_idx once (same source as runner self-test)
        import skipdecode as sk
        with open(os.path.join(runner.LP, "data", "keys", "self_reliance.txt"),
                  encoding="utf-8", errors="ignore") as f:
            truth = sk.eng_to_idx(f.read())[5000:5000 + runner.L_HIT]
        plant = (wi, seed, truth)

    return supervise(args.seconds, resume_start, plant=plant)


if __name__ == "__main__":
    sys.exit(main())
