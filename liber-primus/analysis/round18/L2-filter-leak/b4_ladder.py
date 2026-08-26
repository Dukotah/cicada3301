"""Round 18 / L2 -- SUB-ATTACK B.4 + B.5.

B.4  THE DRIFT-CORRECTED OFFSET LADDER.  Under a single continuous keystream (which is what
     round17/P4's flat, unscoped verdict implies) the correct key index at the first rune of
     page k is start_k + S_k, where S_k has mean rho*start_k and sd sqrt(start_k*var).  For
     page 52 that is start ~ 12,200 => o ~ 12,552 +/- 19.  No stage of any campaign has
     tested that.  B-04 Stage A/B tested only the 120-rune HEAD at offsets {0..3301};
     Stage C tested each page at a RESTART (offset 0); Stage D tested the full stream for
     150 configs only.  And the beam cannot repair the gap by itself: it can insert skips
     but never remove them, so it can never reach an offset LOWER than the one it started
     at, and closing a 352-draw deficit inside a 100-rune page would need 3.5 skips per rune
     against max_skip=3 and a validity test that passes with probability 1/29.

     Candidates are MINED from the published result JSON of round13/B04, round16/KDF and
     round16/prng.  Those sweeps are not re-run (CAMPAIGN-PLAN rule 7).

B.5  THE SKIP-COUNT CHANNEL.  fastbeam returns the number of keystream draws the winning
     path says the rejection sampler consumed.  Under a correct key that must track
     rho*L = 373.6 over the book (measured: 383/383 exact on the plant).  Under a wrong key
     it has no reason to.  Measured here on the REAL ciphertext against a wrong-key null.

Checkpoints after every candidate, so an interrupted run resumes.

Run:  PYTHONUTF8=1 python3 b4_ladder.py --stage ladder --cands 120 --nproc 6
      PYTHONUTF8=1 python3 b4_ladder.py --stage skipchannel
"""
import os, sys, json, math, time, random, hashlib, argparse, heapq
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fastbeam as fb                                   # noqa: E402
import filter_models as fm                              # noqa: E402
ROOT = fb.ROOT
for p in (os.path.join(ROOT, "analysis", "campaign18_skip"),
          os.path.join(ROOT, "analysis", "round11"),
          os.path.join(ROOT, "analysis", "round13", "B04"),
          os.path.join(ROOT, "analysis", "round15", "KDF"),
          os.path.join(ROOT, "analysis", "round16", "prng"),
          os.path.join(ROOT, "benchmark")):
    sys.path.insert(0, p)

import skipdecode as sk                                 # noqa: E402
import lib_numchannel as nc                             # noqa: E402
import ks as b04ks                                      # noqa: E402
import kdf as r15kdf                                    # noqa: E402
import null as bnull                                    # noqa: E402

N = 29
SUPP = 0.8129
Q = 1.0 / N
RHO = Q * SUPP / (1 - Q * SUPP)
VAR_PER = Q * SUPP / (1 - Q * SUPP) ** 2
SEG_L = 100
BEAM_W = 400
MAX_SKIP = 3
ANA = os.path.join(ROOT, "analysis")


# ---------------------------------------------------------------- candidates
def mine_candidates(cap=120):
    """Union of the published top lists. Nothing is re-swept; these are read off disk."""
    rows = []

    def add(**kw):
        rows.append(kw)

    for stage, fn, k in (("A", "results_A.json", 50), ("B", "results_B.json", 50),
                         ("C", "results_C.json", 50)):
        d = json.load(open(os.path.join(ANA, "round13", "B04", fn)))
        for r in d["top50"][:k]:
            add(src=f"B04-{stage}", pub_score=r["score"], fam="b04",
                seed_hex=r["seed_hex"], gen=r["gen"], red=r["red"],
                sign=r["sign"], atbash=r["atbash"], dir=r["dir"])
    for st in json.load(open(os.path.join(ANA, "round13", "B04", "results_D.json"))):
        for r in st["top50"][:50]:
            add(src="B04-D:" + st["stage"], pub_score=r["score"], fam="b04",
                seed_hex=r["seed_hex"], gen=r["gen"], red=r["red"],
                sign=r["sign"], atbash=r["atbash"], dir=r["dir"])

    ks_sum = json.load(open(os.path.join(ANA, "round16", "KDF", "results_summary.json")))
    for r in ks_sum["gates"]["K2"]["top10"]:
        add(src="R16KDF-K2", pub_score=r["score"], fam="kdf", seed_hex=r["secret_hex"],
            kdf=r["kdf"], salt=r["salt"], red=r["reduction"], sign=r["sign"],
            atbash=r["atbash"], dir=r["dir"])
    ka = json.load(open(os.path.join(ANA, "round16", "KDF", "results_A.json")))
    top = ka.get("top50") or ka.get("top") or []
    for r in top[:50]:
        add(src="R16KDF-A", pub_score=r["score"], fam="kdf",
            seed_hex=r.get("secret_hex"), kdf=r.get("kdf"), salt=r.get("salt"),
            red=r.get("reduction", "mod29"), sign=r.get("sign", -1),
            atbash=r.get("atbash", 0), dir=r.get("dir", "fwd"))

    pr = json.load(open(os.path.join(ANA, "round16", "prng", "results.json")))
    for r in pr["top20"]:
        add(src="R16PRNG", pub_score=r["score"], fam="prng", gen=r["gen"],
            seed=r["seed"], sign=r["sign"], dir=r["dir"], red="mod29", atbash=0)

    seen, out = set(), []
    for r in sorted(rows, key=lambda x: -x["pub_score"]):
        key = (r["fam"], r.get("seed_hex"), r.get("seed"), r.get("gen"), r.get("kdf"),
               r.get("salt"), r["red"], r["sign"], r["atbash"], r["dir"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
        if len(out) >= cap:
            break
    return out


def build_ks(cand, nsym):
    """Rebuild a candidate's keystream from its published parameters."""
    if cand["fam"] == "b04":
        seed = bytes.fromhex(cand["seed_hex"])
        base = b04ks.make_ks(cand["gen"], cand["red"], seed, nsym)
    elif cand["fam"] == "kdf":
        seed = bytes.fromhex(cand["seed_hex"])
        base = r15kdf.keystream(seed, cand["salt"], cand["kdf"], nsym, cand["red"])
    else:
        import prng_sweep as ps
        gen = {"php_mt_rand": ps.php_mt_rand_stream, "dotnet_sysrandom": ps.dotnet_random_stream,
               "isaac": ps.isaac_stream, "bbs_small": ps.bbs_stream_small,
               "bbs_large": ps.bbs_stream_large, "lfsr32": ps.lfsr_stream,
               "geffe": ps.geffe_stream}[cand["gen"]]
        base = list(gen(cand["seed"], nsym))
    base = list(base)
    while len(base) < nsym:
        base = base + base
    return base[:nsym] if cand["dir"] == "fwd" else base[:nsym][::-1]


# ---------------------------------------------------------------- ladder geometry
def page_geometry():
    segs = nc.segments()[:-2]
    starts, out = [], []
    s = 0
    for i, pg in enumerate(segs):
        starts.append(s)
        s += len(pg)
    assert s == 12956, s
    for i, pg in enumerate(segs):
        st = starts[i]
        mu = RHO * st
        sd = math.sqrt(st * VAR_PER)
        w = max(4, int(math.ceil(4 * sd)))   # PREREG 3.B.4: o_k +/- 4 sd
        lo = int(round(st + mu)) - w
        hi = int(round(st + mu)) + w
        offs = list(range(max(0, lo), hi + 1))
        for extra in (st, 0):                       # uncorrected + Stage-C restart controls
            if extra not in offs:
                offs.append(extra)
        out.append({"page": i, "start": st, "len": len(pg), "mu": mu, "sd": sd,
                    "offsets": offs, "C": [int(x) for x in pg[:SEG_L]]})
    return out


_G = {}


def _init(geo, maxoff):
    _G["geo"] = geo
    _G["maxoff"] = maxoff


def _atb(C):
    return [(N - 1) - c for c in C]


def _work(cand):
    geo, maxoff = _G["geo"], _G["maxoff"]
    nsym = maxoff + SEG_L * (MAX_SKIP + 2) + 256
    try:
        K = build_ks(cand, nsym)
    except Exception as e:                                    # pragma: no cover
        return {"cand": cand, "error": repr(e)}
    best = (-99.0, None)
    ctrl_best = (-99.0, None)
    ndec = 0
    heap = []
    for g in geo:
        C = g["C"] if cand["atbash"] == 0 else _atb(g["C"])
        for o in g["offsets"]:
            if o + SEG_L * (MAX_SKIP + 1) + 8 >= len(K):
                continue
            r = fb.beam_decode(C, K, sign=cand["sign"], o=o, beam_w=BEAM_W,
                               max_skip=MAX_SKIP, want_path=False)
            ndec += 1
            row = (r["score"], g["page"], o, r["n_skips"],
                   "corrected" if abs(o - g["start"] - g["mu"]) <= 4 * g["sd"] + 1 else "control")
            if len(heap) < 8:
                heapq.heappush(heap, row)
            elif r["score"] > heap[0][0]:
                heapq.heapreplace(heap, row)
            if r["score"] > best[0]:
                best = (r["score"], row)
            if row[4] == "control" and r["score"] > ctrl_best[0]:
                ctrl_best = (r["score"], row)
    return {"cand": cand, "n_decodes": ndec, "best": best[1],
            "best_control_only": ctrl_best[1], "top8": sorted(heap, reverse=True)}


def stage_ladder(cap, nproc, ckpt):
    geo = page_geometry()
    maxoff = max(max(g["offsets"]) for g in geo)
    cands = mine_candidates(cap)
    per_cand = sum(len(g["offsets"]) for g in geo)
    print(f"candidates {len(cands)}   pages {len(geo)}   ladder points/candidate {per_cand}"
          f"   total decodes {len(cands)*per_cand:,}   max offset {maxoff}")
    done = {}
    if os.path.exists(ckpt):
        done = {json.dumps(r["cand"], sort_keys=True): r
                for r in json.load(open(ckpt))["rows"]}
        print(f"  resuming: {len(done)} candidates already on disk")
    todo = [c for c in cands if json.dumps(c, sort_keys=True) not in done]
    t0 = time.time()
    rows = list(done.values())
    with Pool(nproc, initializer=_init, initargs=(geo, maxoff)) as pool:
        for i, r in enumerate(pool.imap_unordered(_work, todo), 1):
            rows.append(r)
            if i % 3 == 0 or i == len(todo):
                ok = [x for x in rows if "best" in x and x["best"]]
                bb = max(ok, key=lambda x: x["best"][0]) if ok else None
                json.dump({"rho": RHO, "seg_len": SEG_L, "n_candidates": len(cands),
                           "ladder_points_per_candidate": per_cand,
                           "elapsed_s": round(time.time() - t0, 1), "rows": rows},
                          open(ckpt, "w"), indent=1)
                print(f"  [{len(rows)}/{len(cands)}] {time.time()-t0:.0f}s  "
                      f"best so far {bb['best'][0]:.3f} "
                      f"({bb['cand'].get('gen') or bb['cand'].get('kdf')}, "
                      f"page {bb['best'][1]}, off {bb['best'][2]}, {bb['best'][4]})",
                      flush=True)
    json.dump({"rho": RHO, "seg_len": SEG_L, "n_candidates": len(cands),
               "ladder_points_per_candidate": per_cand,
               "n_decodes": sum(r.get("n_decodes", 0) for r in rows),
               "elapsed_s": round(time.time() - t0, 1), "rows": rows},
              open(ckpt, "w"), indent=1)
    print("ladder done ->", ckpt)


# ---------------------------------------------------------------- B4 positive control
def stage_b4pc(out_path):
    """Plant a dictionary-resident keystream into a SYNTHETIC book, slice out one page, and
    require the ladder to find it at rank #1. The ladder may not report a negative unless
    this passes (PREREG 3.B.4)."""
    geo = page_geometry()
    P = fm.english_runes(12956)
    seed = b"THE PRIMES ARE SACRED"
    nsym = 13000 * 2
    Ktrue = b04ks.make_ks("sha256_ctr", "mod29", seed, nsym)
    C, skips, used = sk.encipher_keyskip(P, Ktrue, sign=-1, supp=SUPP, seed=3301)
    cum = [0]
    for s in skips:
        cum.append(cum[-1] + s)
    results = []
    for pg in (10, 30, 52):
        g = geo[pg]
        st = g["start"]
        true_off = st + cum[st]                       # exact key index at that rune
        seg = C[st:st + SEG_L]
        inside = abs(true_off - st - g["mu"]) <= 4 * g["sd"] + 1
        scored = []
        for o in g["offsets"]:
            r = fb.beam_decode(seg, Ktrue, sign=-1, o=o, beam_w=BEAM_W,
                               max_skip=MAX_SKIP, want_path=False)
            scored.append((r["score"], o, r["n_skips"]))
        # decoy candidates: 20 wrong keystreams over the same ladder
        decoy_best = -99.0
        for j in range(20):
            Kw = b04ks.make_ks("sha256_ctr", "mod29",
                               ("decoy%d" % j).encode(), nsym)
            for o in g["offsets"][::7]:
                r = fb.beam_decode(seg, Kw, sign=-1, o=o, beam_w=BEAM_W,
                                   max_skip=MAX_SKIP, want_path=False)
                decoy_best = max(decoy_best, r["score"])
        scored.sort(reverse=True)
        rank = 1 + [o for _, o, _ in scored].index(true_off) if any(
            o == true_off for _, o, _ in scored) else None
        results.append({
            "page": pg, "start": st, "true_offset": true_off,
            "predicted_mu": st + g["mu"], "sd": g["sd"],
            "true_offset_inside_ladder": bool(inside),
            "ladder_points": len(g["offsets"]),
            "rank_of_true_offset": rank,
            "score_at_true_offset": next((s for s, o, _ in scored if o == true_off), None),
            "best_score_on_ladder": scored[0][0],
            "best_offset_on_ladder": scored[0][1],
            "score_at_uncorrected_start": next((s for s, o, _ in scored if o == st), None),
            "score_at_restart_0": next((s for s, o, _ in scored if o == 0), None),
            "best_decoy_score": decoy_best,
        })
        r = results[-1]
        print(f"  page {pg:2d}: true off {true_off} (predicted {r['predicted_mu']:.0f} "
              f"+/- {r['sd']:.1f}), inside={inside}, rank {rank}, "
              f"score {r['score_at_true_offset']:.3f}, uncorrected "
              f"{r['score_at_uncorrected_start']:.3f}, restart0 "
              f"{r['score_at_restart_0']:.3f}, best decoy {decoy_best:.3f}")
    ok = all(x["true_offset_inside_ladder"] and x["rank_of_true_offset"] == 1
             and x["score_at_true_offset"] >= -5.5 for x in results)
    out = {"planted_seed": seed.decode(), "gen": "sha256_ctr", "red": "mod29",
           "total_skips_in_synthetic_book": sum(skips), "results": results, "pass": ok}
    json.dump(out, open(out_path, "w"), indent=1)
    print("B4 positive control:", "PASS" if ok else "FAIL")
    return out


# ---------------------------------------------------------------- B5 skip channel
def stage_skipchannel(out_path, n_wrong=40, n_top=20):
    """Is the beam's inferred skip count an English-independent ranking channel?"""
    X = nc.unsolved()
    P = fm.english_runes(12956)
    nsym = 13000 * 2
    Kt = b04ks.make_ks("sha256_ctr", "mod29", b"CICADA3301", nsym)
    Cp, skips, _ = sk.encipher_keyskip(P, Kt, sign=-1, supp=SUPP, seed=3301)
    true_row = fb.beam_decode(Cp, Kt, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP,
                              want_path=False)
    print(f"  planted TRUE key : score {true_row['score']:.3f}  "
          f"skips {true_row['n_skips']} (true {sum(skips)})")

    wrong_plant, wrong_real = [], []
    for j in range(n_wrong):
        Kw = b04ks.make_ks("sha256_ctr", "mod29", ("wrong%03d" % j).encode(), nsym)
        a = fb.beam_decode(Cp, Kw, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP,
                           want_path=False)
        b = fb.beam_decode(X, Kw, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP,
                           want_path=False)
        wrong_plant.append((a["score"], a["n_skips"]))
        wrong_real.append((b["score"], b["n_skips"]))
        if (j + 1) % 5 == 0:
            json.dump({"partial": True, "true": true_row, "true_skips": sum(skips),
                       "wrong_on_plant": wrong_plant, "wrong_on_real": wrong_real},
                      open(out_path, "w"), indent=1)
            print(f"   ...{j+1}/{n_wrong}", flush=True)

    import numpy as np
    wp = np.array([s for _, s in wrong_plant], dtype=float)
    wr = np.array([s for _, s in wrong_real], dtype=float)
    exp_true = RHO * 12956
    sep = (true_row["n_skips"] - wp.mean()) / wp.std(ddof=1)
    # top real candidates, full book, offset 0
    cands = mine_candidates(n_top)
    top_rows = []
    for c in cands:
        try:
            K = build_ks(c, nsym)
        except Exception as e:
            continue
        Cx = X if c["atbash"] == 0 else _atb(X)
        r = fb.beam_decode(Cx, K, sign=c["sign"], o=0, beam_w=BEAM_W, max_skip=MAX_SKIP,
                           want_path=False)
        z = (r["n_skips"] - wr.mean()) / wr.std(ddof=1)
        top_rows.append({"src": c["src"], "gen": c.get("gen") or c.get("kdf"),
                         "seed_hex": c.get("seed_hex"), "seed": c.get("seed"),
                         "pub_score": c["pub_score"], "full_book_score": r["score"],
                         "n_skips": r["n_skips"], "skip_z_vs_wrong_null": z})
        json.dump({"partial": True, "top_rows": top_rows}, open(out_path + ".tmp", "w"))
    out = {
        "expected_skips_true_key": exp_true,
        "true_key_on_plant": {"score": true_row["score"], "n_skips": true_row["n_skips"],
                              "actual_skips": sum(skips)},
        "wrong_keys_on_plant": {"n": len(wp), "mean_skips": float(wp.mean()),
                                "sd_skips": float(wp.std(ddof=1)),
                                "min": float(wp.min()), "max": float(wp.max())},
        "wrong_keys_on_real_ciphertext": {"n": len(wr), "mean_skips": float(wr.mean()),
                                          "sd_skips": float(wr.std(ddof=1)),
                                          "min": float(wr.min()), "max": float(wr.max())},
        "separation_sd_true_vs_wrong": float(sep),
        "real_candidates_full_book": sorted(top_rows,
                                            key=lambda r: -r["skip_z_vs_wrong_null"]),
    }
    json.dump(out, open(out_path, "w"), indent=1)
    print(f"  wrong on plant : {wp.mean():.1f} +/- {wp.std(ddof=1):.1f}")
    print(f"  wrong on REAL  : {wr.mean():.1f} +/- {wr.std(ddof=1):.1f}")
    print(f"  separation true vs wrong: {sep:.2f} sd")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="ladder")
    ap.add_argument("--cands", type=int, default=120)
    ap.add_argument("--nproc", type=int, default=6)
    a = ap.parse_args()
    if a.stage == "ladder":
        stage_ladder(a.cands, a.nproc, os.path.join(HERE, "b4_ladder.json"))
    elif a.stage == "b4pc":
        stage_b4pc(os.path.join(HERE, "b4_control.json"))
    elif a.stage == "skipchannel":
        stage_skipchannel(os.path.join(HERE, "b5_skipchannel.json"))
