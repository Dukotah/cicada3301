"""L6 / sub-lane A — THE OFFSET SWEEP.  PREREG s3.

Round 8 states its 2.52e9-decode sweep "assumes key index 0 aligns with the first rune of
LP2 page 0".  B-04 (6,224,300 decodes) covered ten offsets.  R16-KDF (692,064) and
R16-PRNG (52,556) covered offset 0 only.  PARKED P-10 scores that omission at x8,192 for a
modest range and notes it multiplies EVERY generator.

Round 17 fixed exactly this defect for external pads - lib_padsweep.dense_scan scores every
offset instead of A1's eight-offset ladder.  The derived/seeded branch never got the same
treatment.  This applies it.

  A1  the mined survivors of B-04 / R16-KDF / R16-PRNG, dense over [0, 2^20)
  A2  a fresh 504-seed x 6-generator grid, dense over [0, 2^18)

Nothing here re-runs a prior sweep (Round 18 rule 7): A1's configs are READ from those
lanes' published results JSON and extended along the one axis they all fixed at 0.

Checkpointed per work unit in out/ckpt_A1 / out/ckpt_A2 - resumable, never recomputes.
Run:  python3 sweep_offset.py --stage A1 --nproc 5 [--budget SECONDS]
"""
import os, sys, json, time, argparse, glob, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import lib_l6 as X
import lib_padsweep as L

KEEP = 1000
TOP_A1 = 40          # escalation depth, stage A1
TOP_A2 = 12          # escalation depth, stage A2 (6,048 configs; depth traded for breadth,
                     # and the control's rank distribution reports survival at BOTH depths)
A2_GENS = ["sha256_ctr", "sha512_ctr", "sha1_ctr", "md5_ctr", "sha256_chain",
           "hmac_sha256_ctr"]

CK = {"A1": os.path.join(X.OUT, "ckpt_A1"), "A2": os.path.join(X.OUT, "ckpt_A2")}
_G = {}


def _init(stage):
    _G["stage"] = stage
    L.trigram_model()
    _G["C0"] = [int(x) for x in L.nc.unsolved()]
    _G["C1"] = [(29 - 1) - c for c in _G["C0"]]


def _ct(atbash):
    return _G["C1"] if int(atbash or 0) else _G["C0"]


def _unit_A1(job):
    i, cfg = job
    nsym = X.OFF_MAX_A1 + X.SPAN + 256
    K = X.derived_keystream(cfg, nsym)
    Kl = [int(x) for x in K]
    C = _ct(cfg.get("atbash", 0))
    sign = int(cfg["sign"])
    hits = L.dense_scan(K, C, sign=sign, keep=KEEP)
    esc = X.escalate(hits, Kl, C, sign, top=TOP_A1, head=X.HEAD, ms=X.MS, beam_w=X.BEAM_W)
    n_off = max(0, min(len(Kl) - X.PLEN, X.OFF_MAX_A1))
    return {"i": i, "cfg": cfg, "n_offsets": n_off, "ks_len": len(Kl),
            "best": esc[0] if esc else None, "top5": esc[:5],
            "best_pre": float(hits[0][0]) if hits else None}


def _unit_A2(job):
    i, label, seed_hex, gen = job
    nsym = X.OFF_MAX_A2 + X.SPAN + 256
    cfg = {"kind": "b04", "seed_hex": seed_hex, "gen": gen, "red": "mod29", "dir": "fwd"}
    K = X.derived_keystream(cfg, nsym)
    Kl = [int(x) for x in K]
    C = _G["C0"]
    n_off = 0
    rows = []
    for sign in (-1, 1):
        hits = L.dense_scan(K, C, sign=sign, keep=KEEP)
        esc = X.escalate(hits, Kl, C, sign, top=TOP_A2, head=X.HEAD, ms=X.MS,
                         beam_w=X.BEAM_W)
        n_off += max(0, min(len(Kl) - X.PLEN, X.OFF_MAX_A2))
        if esc:
            r = dict(esc[0]); r.update(sign=sign)
            rows.append(r)
    rows.sort(key=lambda r: r["score"], reverse=True)
    return {"i": i, "label": label, "seed_hex": seed_hex, "gen": gen,
            "n_offsets": n_off, "best": rows[0] if rows else None, "rows": rows}


def jobs_for(stage):
    if stage == "A1":
        return [(i, c) for i, c in enumerate(X.mine_configs())]
    seeds = X.core_seeds()
    out, i = [], 0
    for lab, sd in seeds:
        for g in A2_GENS:
            out.append((i, lab, sd.hex(), g))
            i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=("A1", "A2"))
    ap.add_argument("--nproc", type=int, default=5)
    ap.add_argument("--budget", type=float, default=3300.0)
    a = ap.parse_args()
    stage = a.stage
    os.makedirs(CK[stage], exist_ok=True)
    js = jobs_for(stage)
    done = {int(os.path.basename(p)[:-5]) for p in glob.glob(os.path.join(CK[stage], "*.json"))}
    todo = [j for j in js if j[0] not in done]
    print(f"[{stage}] {len(js)} units, {len(done)} checkpointed, {len(todo)} to run "
          f"on {a.nproc} procs, budget {a.budget:.0f}s", flush=True)
    fn = _unit_A1 if stage == "A1" else _unit_A2
    t0 = time.time()
    if todo:
        from multiprocessing import Pool
        with Pool(a.nproc, initializer=_init, initargs=(stage,)) as pool:
            for k, r in enumerate(pool.imap_unordered(fn, todo, chunksize=1)):
                X.jdump(r, os.path.join(CK[stage], f"{r['i']}.json"))
                if k % 25 == 0 or k == len(todo) - 1:
                    b = (r.get("best") or {}).get("score")
                    print(f"  [{stage}] {k+1}/{len(todo)}  {time.time()-t0:.0f}s  "
                          f"last_best={b}", flush=True)
                if time.time() - t0 > a.budget:
                    print(f"  [{stage}] budget reached; {len(todo)-k-1} units left "
                          f"(resumable)", flush=True)
                    pool.terminate()
                    break
    collect(stage)


def collect(stage):
    rows, n_off, units = [], 0, 0
    for p in sorted(glob.glob(os.path.join(CK[stage], "*.json"))):
        d = json.load(open(p))
        units += 1
        n_off += int(d.get("n_offsets", 0))
        b = d.get("best")
        if b:
            r = dict(b)
            if stage == "A1":
                c = d["cfg"]
                r.update(src=c.get("src"), kind=c["kind"], gen=c.get("gen") or c.get("kdf"),
                         red=c.get("red") or c.get("reduction"), salt=c.get("salt"),
                         seed=c.get("label") or c.get("seed"),
                         seed_hex=c.get("seed_hex") or c.get("secret_hex"),
                         atbash=c.get("atbash", 0), dir=c.get("dir", "fwd"),
                         prior_score=c.get("prior_score"))
            else:
                r.update(src="A2-grid", kind="b04", gen=d["gen"], red="mod29",
                         seed=d["label"], seed_hex=d["seed_hex"], atbash=0, dir="fwd")
            rows.append(r)
    rows.sort(key=lambda r: r["score"], reverse=True)
    total_units = len(jobs_for(stage))
    out = {"stage": stage, "units_done": units, "units_total": total_units,
           "complete": units == total_units,
           "off_max": X.OFF_MAX_A1 if stage == "A1" else X.OFF_MAX_A2,
           "escalate_top": TOP_A1 if stage == "A1" else TOP_A2,
           "keep": KEEP, "max_skip": X.MS, "head": X.HEAD, "beam_w": X.BEAM_W,
           "n_offsets_scanned": n_off,
           "threshold_for_at_this_N": X.nullmod.threshold_for(max(2, n_off),
                                                              segment_len=X.HEAD),
           "best": rows[0] if rows else None, "top30": rows[:30]}
    X.jdump(out, os.path.join(X.OUT, f"results_{stage}.json"))
    print(f"\n[{stage}] units {units}/{total_units}  offsets {n_off:,}")
    if rows:
        print(f"[{stage}] best {rows[0]['score']:+.4f}  off={rows[0]['offset']} "
              f"{rows[0].get('gen')}|{rows[0].get('red')} seed={rows[0].get('seed')}")
    print(f"[{stage}] threshold_for({n_off:,}) = {out['threshold_for_at_this_N']:+.4f}")


if __name__ == "__main__":
    main()
