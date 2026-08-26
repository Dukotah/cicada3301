"""L6 / sub-lane B — THE MARSAGLIA RANDOM NUMBER CDROM (1995), swept at last.

`round17/SYNTHESIS.md` named this the single live, reachable, unswept public-pad item and
"the cheapest remaining item in this branch": 634,124,288 bytes of published physical
randomness, dated 1995, with published SHA-256s.  Lane P2 found it, recorded its
identifier and a verified HTTP 206, and deliberately left it alone.  Nobody had ever fed
it to the decoder.

Every pad below is hash-verified first (verify_marsaglia.py -> data/MANIFEST.json;
110/110 published SHA-256s).  `hexchars` is EXCLUDED and `nibbles` used instead
(audit_builders.py re-derives why).  max_skip=8 throughout.  Every offset is scored.

Checkpointed per (pad, builder, byte-order) in out/ckpt_M - resumable, never recomputes.
Run:  python3 sweep_marsaglia.py --nproc 4 --budget 2400 [--pads BITS.01,...]
"""
import os, sys, json, time, glob, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import lib_l6 as X
import lib_padsweep as L

KEEP = 1000
TOP = 40
BUILDERS = ["mod29", "hi_nibble", "lo_nibble", "byte_scaled", "prime_to_idx", "nibbles"]
CKD = os.path.join(X.OUT, "ckpt_M")
_G = {}


def _init():
    L.trigram_model()
    _G["C"] = [int(x) for x in L.nc.unsolved()]


def _unit(job):
    uid, path, name, builder, rev, nbytes = job
    a = np.fromfile(path, dtype=np.uint8)
    C = _G["C"]
    res = {"uid": uid, "pad": name, "builder": builder, "rev": bool(rev),
           "bytes": int(a.size), "n_offsets": 0, "rows": []}
    for sign in (-1, 1):
        hits, n_off, tot = X.sharded_scan(a, builder, sign, C, keep=KEEP,
                                          shard_bytes=1 << 25, reverse=bool(rev))
        res["n_offsets"] += int(n_off)
        res["ks_len"] = int(tot)
        if not hits:
            continue
        # escalate on the true keystream around each surviving offset: build only the
        # window each candidate needs, so a 634 MB pad never becomes a 1.3 GB int16 array
        fn, spb = X.BUILDERS[builder]
        src = a[::-1] if rev else a
        rows = []
        for pre, o in hits[:TOP]:
            o = int(o)
            b0 = o // spb
            b1 = min(a.size, b0 + (X.SPAN + X.PLEN + 64) // spb + 64)
            if (b1 - b0) * spb <= X.SPAN + 8:
                continue
            Kw = [int(x) for x in fn(np.ascontiguousarray(src[b0:b1]))]
            loc = o - b0 * spb
            if loc + X.SPAN + 8 >= len(Kw):
                continue
            import skipdecode as sk
            bd = sk.beam_decode([int(x) for x in C[:X.HEAD]], Kw, sign=sign, o=loc,
                                beam_w=X.BEAM_W, max_skip=X.MS)
            rows.append({"offset": o, "sign": sign, "pre": float(pre),
                         "score": float(bd["score"]), "head": bd["translit"][:64]})
        rows.sort(key=lambda r: r["score"], reverse=True)
        res["rows"].extend(rows[:5])
    res["rows"].sort(key=lambda r: r["score"], reverse=True)
    res["best"] = res["rows"][0] if res["rows"] else None
    return res


def build_jobs(only=None, include_iso=True):
    man = json.load(open(os.path.join(X.DATA, "MANIFEST.json")))
    assert man.get("all_gates_pass"), "hash gates did not pass - refusing to sweep"
    pads = man["verified_pads"]
    if only:
        pads = [p for p in pads if p["name"] in only]
    jobs = []
    ent = [(os.path.join(X.DATA, "iso", p["extracted"]), p["name"], p["bytes"]) for p in pads]
    if include_iso:
        ent.append((os.path.join(X.DATA, "MARSAGLIA_CDROM.iso"),
                    "MARSAGLIA_CDROM.iso", man["iso"]["bytes"]))
    # uid is a STABLE function of (pad, builder, rev) so checkpoints survive any reordering
    for bi, builder in enumerate(BUILDERS):
        for rev in (0, 1):
            for pi, (path, name, nb) in enumerate(ent):
                uid = (bi * 2 + rev) * 1000 + pi
                jobs.append((uid, path, name, builder, rev, nb))
    # BUILDER-MAJOR order: the highest-prior builder (mod29) completes across every pad
    # before the next one starts, so a budget cut leaves a CLEAN coverage statement
    # ("mod29 complete on 63/63 pads") rather than a ragged one.
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nproc", type=int, default=4)
    ap.add_argument("--budget", type=float, default=2400.0)
    ap.add_argument("--pads")
    ap.add_argument("--no-iso", action="store_true")
    ap.add_argument("--collect-only", action="store_true")
    a = ap.parse_args()
    os.makedirs(CKD, exist_ok=True)
    jobs = build_jobs(set(a.pads.split(",")) if a.pads else None, not a.no_iso)
    done = {int(os.path.basename(p)[:-5]) for p in glob.glob(os.path.join(CKD, "*.json"))}
    todo = [j for j in jobs if j[0] not in done]
    print(f"[M] {len(jobs)} units ({len(done)} checkpointed, {len(todo)} to run) "
          f"nproc={a.nproc} budget={a.budget:.0f}s", flush=True)
    if not a.collect_only and todo:
        from multiprocessing import Pool
        t0 = time.time()
        with Pool(a.nproc, initializer=_init) as pool:
            for k, r in enumerate(pool.imap_unordered(_unit, todo, chunksize=1)):
                X.jdump(r, os.path.join(CKD, f"{r['uid']}.json"))
                print(f"  [M] {k+1}/{len(todo)} {time.time()-t0:.0f}s {r['pad']}/"
                      f"{r['builder']}{'_rev' if r['rev'] else ''} "
                      f"off={r['n_offsets']:,} best="
                      f"{(r.get('best') or {}).get('score')}", flush=True)
                if time.time() - t0 > a.budget:
                    print(f"  [M] budget reached; {len(todo)-k-1} units left (resumable)",
                          flush=True)
                    pool.terminate()
                    break
    collect(jobs)


def collect(jobs):
    rows, n_off, units, pads = [], 0, 0, {}
    for p in sorted(glob.glob(os.path.join(CKD, "*.json"))):
        d = json.load(open(p))
        units += 1
        n_off += int(d.get("n_offsets", 0))
        pads.setdefault(d["pad"], {"bytes": d["bytes"], "units": 0, "offsets": 0})
        pads[d["pad"]]["units"] += 1
        pads[d["pad"]]["offsets"] += int(d.get("n_offsets", 0))
        for r in d.get("rows", [])[:3]:
            q = dict(r); q.update(pad=d["pad"], builder=d["builder"], rev=d["rev"])
            rows.append(q)
    rows.sort(key=lambda r: r["score"], reverse=True)
    out = {"lane": "round18/L6 sub-lane B (MARSAGLIA CDROM 1995)",
           "units_done": units, "units_total": len(jobs),
           "complete": units == len(jobs),
           "builders": BUILDERS,
           "builders_excluded": X.EXCLUDED_BUILDERS,
           "max_skip": X.MS, "head": X.HEAD, "beam_w": X.BEAM_W,
           "keep": KEEP, "escalate_top": TOP,
           "n_offsets_scanned": n_off,
           "threshold_for_at_this_N": X.nullmod.threshold_for(max(2, n_off),
                                                              segment_len=X.HEAD),
           "per_pad": pads, "best": rows[0] if rows else None, "top30": rows[:30]}
    X.jdump(out, os.path.join(X.OUT, "results_M.json"))
    print(f"\n[M] units {units}/{len(jobs)}  offsets {n_off:,}")
    if rows:
        print(f"[M] best {rows[0]['score']:+.4f}  {rows[0]['pad']}/{rows[0]['builder']}"
              f"{'_rev' if rows[0]['rev'] else ''} sign{rows[0]['sign']:+d} "
              f"off={rows[0]['offset']}")
    print(f"[M] threshold_for({n_off:,}) = {out['threshold_for_at_this_N']:+.4f}")


if __name__ == "__main__":
    main()
