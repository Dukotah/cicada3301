"""R47-H2: the new C10's in-house baselines (H1 PREREG Addendum 3). Writes c10_baselines.json.

    python -I liber-primus/analysis/round47/H2-harden/c10_baselines.py --arm i_ii --n 100 --seed 4710
    python -I liber-primus/analysis/round47/H2-harden/c10_baselines.py --arm iv --m 64  --n 100 --seed 4710
    python -I liber-primus/analysis/round47/H2-harden/c10_baselines.py --arm iv --m 512 --n 100 --seed 4710
    python -I liber-primus/analysis/round47/H2-harden/c10_baselines.py --arm iii --units 16 --wrong 1024 --seed 4710

(i)   exhaustive over all F keys with the TRUE lengths (checker's baseline_true)
(ii)  exhaustive over all F keys with jumps at the PRINTED starts (checker's baseline_printed)
(iii) R47-X1's arrangement beam (x1_c10_beam_attack.attack, width 16) given NO key: i.e. run per key. Full
      enumeration costs F x t_key per unit, so it is measured on the correct key + `wrong` sampled wrong keys
      (does the correct key's beam output out-score every sampled wrong key's?) and its cost extrapolated.
(iv)  two-stage: rank all F keys by the printed-start decode (ii's ranker), run X1's beam on the top m, return
      the best quadgram-scored output.
Everything runs in-process with access to the plant (these are the repo's own baselines, not submissions).
"""
import argparse
import json
import multiprocessing as mp
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "challenges"))
sys.path.insert(0, os.path.join(ROOT, "liber-primus", "analysis", "round47", "X1-redteam"))
os.environ["X1_BEAM"] = "16"
import _heavy as H  # noqa: E402
import c10_shuffled_lengths as C10  # noqa: E402
import x1_c10_beam_attack as X1  # noqa: E402

OUT = os.path.join(HERE, "c10_baselines.json")
_CASES = None


def init(seed, n):
    global _CASES
    p, nl = C10.make_cases(n, seed, H.english_sentences())
    _CASES = p + nl


def klen(c):
    return max(C10.positions(c["true_lens"])) + 1


def job_i_ii(i):
    c = _CASES[i]
    t = time.time()
    a = C10.baseline_true(c)
    ta = time.time() - t
    t = time.time()
    b = C10.baseline_printed(c)
    return i, a, b, ta, time.time() - t


def job_iv(args):
    i, m = args
    c = _CASES[i]
    t = time.time()
    pr = [l for s in c["printed"] for l in s]
    top = sorted(C10.rank_keys(c["C"], pr), reverse=True)[:m]
    best = None
    for _, s in top:
        out = X1.attack(c["C"], C10.key_stream(s, klen(c)), c["printed"])
        q = H.english_score(out)
        if best is None or q > best[0]:
            best = (q, out, s)
    true_rank = next((r for r, (_, s) in enumerate(top) if s == c["s"]), None)
    return i, best[1], time.time() - t, true_rank


def job_iii(args):
    i, wrong, seed = args
    c = _CASES[i]
    rng = random.Random(f"{seed}|iii|{i}")
    keys = [c["s"]] if c["s"] < C10.F_KEYS else []
    keys += [s for s in rng.sample(range(C10.F_KEYS), wrong + 1) if s != c["s"]][:wrong]
    t = time.time()
    sc = []
    for s in keys:
        out = X1.attack(c["C"], C10.key_stream(s, klen(c)), c["printed"])
        sc.append((H.english_score(out), s, C10.recovery(out, c["P"])))
    return i, sc, (time.time() - t) / len(keys)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["i_ii", "iv", "iii"])
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--seed", type=int, default=4710)
    ap.add_argument("--m", type=int, default=64)
    ap.add_argument("--units", type=int, default=16)
    ap.add_argument("--wrong", type=int, default=1024)
    ap.add_argument("--procs", type=int, default=7)
    a = ap.parse_args()
    init(a.seed, a.n)
    plants, nulls = _CASES[:a.n], _CASES[a.n:]
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    t0 = time.time()
    with mp.Pool(a.procs, initializer=init, initargs=(a.seed, a.n)) as pool:
        if a.arm == "i_ii":
            got = sorted(pool.map(job_i_ii, range(2 * a.n)))
            for k, name, col, tcol in (("i", "(i) exhaustive, TRUE lengths", 1, 3), ("ii", "(ii) exhaustive, PRINTED starts", 2, 4)):
                outs = [g[col] for g in got]
                r = C10.summarise(plants, nulls, outs[:a.n], outs[a.n:])
                r["sec_per_unit"] = round(sum(g[tcol] for g in got) / len(got), 2)
                res[f"{k}|seed{a.seed}|n{a.n}"] = r
                C10.row(name, r, r["sec_per_unit"])
        elif a.arm == "iv":
            got = sorted(pool.map(job_iv, [(i, a.m) for i in range(2 * a.n)]))
            outs = [g[1] for g in got]
            r = C10.summarise(plants, nulls, outs[:a.n], outs[a.n:])
            r["sec_per_unit"] = round(sum(g[2] for g in got) / len(got), 2)
            ranks = [g[3] for g in got[:a.n]]
            r["true_key_in_top_m"] = sum(x is not None for x in ranks) / a.n
            res[f"iv_m{a.m}|seed{a.seed}|n{a.n}"] = r
            C10.row(f"(iv) printed-start rank, X1 beam on top {a.m}", r, r["sec_per_unit"])
            print(f"  true key in top {a.m}: {r['true_key_in_top_m']:.3f}")
        else:
            idx = list(range(a.units)) + list(range(a.n, a.n + a.units))
            got = sorted(pool.map(job_iii, [(i, a.wrong, a.seed) for i in idx]))
            win, recs, nullmax, plantbest, tk = 0, [], [], [], []
            for i, sc, t in got:
                tk.append(t)
                if i < a.n:
                    corr, wr = sc[0], sc[1:]
                    w = corr[0] > max(x[0] for x in wr)
                    win += w
                    recs.append(corr[2])
                    plantbest.append(round(corr[0], 3))
                    passes = w and corr[2] >= C10.MIN_RECOVERY and corr[0] >= C10.ENGLISH
                    recs[-1] = (corr[2], passes, round(max(x[0] for x in wr), 3))
                else:
                    nullmax.append(round(max(x[0] for x in sc), 3))
            tkey = sum(tk) / len(tk)
            r = {"units": a.units, "wrong_keys_sampled": a.wrong,
                 "correct_key_beats_all_sampled": win / a.units,
                 "pass_if_full_enum_matched_sample": sum(p for _, p, _ in recs) / a.units,
                 "correct_key_recovery_mean": sum(x for x, _, _ in recs) / a.units,
                 "correct_key_score": plantbest, "max_wrong_key_score_per_plant": [m for _, _, m in recs],
                 "null_max_score_over_sample": nullmax,
                 "sec_per_key": round(tkey, 4), "est_sec_per_unit_full_enum": round(tkey * C10.F_KEYS)}
            res[f"iii|seed{a.seed}|units{a.units}|wrong{a.wrong}"] = r
            print(json.dumps(r, indent=1))
    print(f"wall {time.time() - t0:.0f}s")
    json.dump(res, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
