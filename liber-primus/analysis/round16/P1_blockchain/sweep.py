"""Round 16 lane P1 -- dense pad sweep of the Bitcoin blockchain.

Hypothesis
----------
LP2's keystream is a contiguous run of Bitcoin blockchain bytes -- block hashes, merkle
roots, nonces or timestamps, in height order, in either byte order, read either as bytes
or as the hex TEXT a 2013 author would have copy-pasted off a block explorer.  The seed
census calls a seedless full-entropy pad "unreachable"; the blockchain is seedless, full
entropy, permanently public, timestamped and byte-exact retrievable, so it is reachable.

Instrument
----------
`round16/lib_padsweep.py`: dense trigram prefilter over EVERY key offset -> beam
escalation on the survivors, A1's beam width / head / score scale / shuffle null, so the
numbers are directly comparable to `round12/A1/results_560_13.json`.

ONE DELIBERATE DEPARTURE, forced by this lane's own control (`control_ext.py`)
-----------------------------------------------------------------------------
`hash_display.bin` is 18.4 % zero bytes -- every block hash in display order opens with
exactly 4+ zero bytes, so the pad contains a 4-byte constant run every 32 bytes.  Under
the anti-repeat filter a constant key run makes the key pointer advance without changing
the key symbol, so suppressed doublets need MORE skips than on a full-entropy pad
(measured: 12 skips on failed trials vs 6 on the PREREG synthetic pad).  A1's
`max_skip=3` therefore loses power on exactly this pad family:

    plant-and-recover, 60 plants, blockchain hash_display, beam_w=500
      max_skip=3  recovered@0.95 = 0.650   score >= -5.5 at the true offset = 0.867
      max_skip=5  recovered@0.95 = 0.967   score >= -5.5 = 1.000
      max_skip=8  recovered@0.95 = 1.000   score >= -5.5 = 1.000
    (widening the beam to 1500 at max_skip=3 changes nothing -- it is a skip-budget
     limit, not a search-width limit)

So every survivor is escalated TWICE: at `max_skip=3` (A1-comparable) and at
`max_skip=8` (power-restored), each judged against its OWN shuffle null at the same
setting.  Reporting both means the A1-comparable number is still on the record.

Usage
-----
  python sweep.py --control                 # plant-and-recover on the REAL blockchain pad
  python sweep.py --pad hash_display.bin    # one pad: 12 builders x 2 signs x all offsets
  python sweep.py --all                     # every pad in PADS, sequentially
  python sweep.py --merge                   # results_*.json -> results.json + top-20
"""
import os, sys, json, time, argparse, glob, hashlib, datetime, random
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
R16 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, R16)
import lib_padsweep as L                                    # noqa: E402
sys.path.insert(0, os.path.join(L.ROOT, "benchmark"))
import null as nullmod                                      # noqa: E402

C_FULL = L.nc.unsolved()
C_HEAD = np.asarray(C_FULL[:L.HEAD], dtype=np.int16)
SIGNS = (-1, 1)
MAX_SKIPS = (3, 8)          # A1-comparable, and power-restored (see module docstring)
TOP_ESCALATE = 40
NULL_N = 200

PADS = [
    "hash_display.bin", "hash_internal.bin",
    "merkle_display.bin", "merkle_internal.bin",
    "nonce_le.bin", "time_le.bin",
    "hash_display_2013.bin", "hash_internal_2013.bin",
]


# ------------------------------------------------------------------ subset pads
def build_subsets():
    """2013-only blocks are a DIFFERENT byte stream, not a substring of the full pad, so
    a dense scan of the full pad does not cover them.  Everything else the lane brief
    lists -- 'genesis onward', 'blocks near LP2-relevant dates' -- IS a contiguous run of
    the full pad and is therefore already covered by scanning every offset."""
    src = os.path.join(DATA, "blocks.tsv")
    outs = {"hash_display_2013.bin": bytearray(), "hash_internal_2013.bin": bytearray()}
    if all(os.path.exists(os.path.join(DATA, k)) for k in outs):
        return
    lo = int(datetime.datetime(2013, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
    hi = int(datetime.datetime(2014, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
    n = 0
    with open(src, encoding="ascii") as f:
        f.readline()
        for line in f:
            h, bh, bm, non, ts = line.rstrip("\n").split("\t")
            if lo <= int(ts) < hi:
                a = bytes.fromhex(bh)
                outs["hash_display_2013.bin"] += a
                outs["hash_internal_2013.bin"] += a[::-1]
                n += 1
    for k, v in outs.items():
        with open(os.path.join(DATA, k), "wb") as f:
            f.write(bytes(v))
    print("  built 2013-only subset pads: %d blocks, %d B each" % (n, len(bytes(v))))


# ------------------------------------- escalation / null, parameterised by max_skip
def escalate_ms(hits, Kl, C, sign, max_skip, head=L.HEAD, top=TOP_ESCALATE):
    out = []
    for score, o in hits[:top]:
        o = int(o)
        if o + head * (max_skip + 1) + 8 >= len(Kl):
            continue
        bd = L.sk.beam_decode([int(x) for x in C[:head]], Kl, sign=sign, o=o,
                              beam_w=L.BEAM_W, max_skip=max_skip)
        out.append({"offset": o, "sign": sign, "pre": float(score),
                    "score": bd["score"], "head": bd["translit"][:64]})
    out.sort(key=lambda r: r["score"], reverse=True)
    return out


def null_ceiling_ms(Kl, max_skip, seq_len=L.HEAD, n=NULL_N, seed0=3301):
    """A1's shuffle null, at the decoder setting actually used."""
    base = C_FULL[:seq_len]
    span = max(1, len(Kl) - seq_len * (max_skip + 1) - 8)
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(base)
        r.shuffle(s)
        vals.append(L.sk.beam_decode(s, Kl, sign=-1, o=(k * 37) % span,
                                     beam_w=L.BEAM_W, max_skip=max_skip)["score"])
    return float(np.mean(vals)), float(np.max(vals))


# ------------------------------------------------------------------ the sweep
def sweep_pad(pad, signs=SIGNS, keep=400, verbose=True):
    p = os.path.join(DATA, pad)
    blob = open(p, "rb").read()
    sha = hashlib.sha256(blob).hexdigest()
    rec = {"pad": pad, "bytes": len(blob), "sha256": sha, "variants": {},
           "n_offsets_total": 0, "max_skips": list(MAX_SKIPS),
           "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    print("== %s  %d B  sha256=%s" % (pad, len(blob), sha[:16]), flush=True)
    best = {"score": -99.0}
    for bname in L.BUILDERS:
        for rev in (False, True):
            vname = bname + ("_rev" if rev else "")
            t0 = time.time()
            ks = L.BUILDERS[bname](blob[::-1] if rev else blob)
            Kl = [int(x) for x in ks]
            v = {"len": int(len(ks)), "null": {}, "bar": {}, "signs": {}}
            for ms in MAX_SKIPS:
                nmean, nmax = null_ceiling_ms(Kl, ms)
                v["null"][str(ms)] = {"mean": nmean, "max": nmax}
                v["bar"][str(ms)] = L.hit_bar(nmax)
            for sign in signs:
                hits = L.dense_scan(ks, C_HEAD, sign=sign, keep=keep)
                n_off = max(0, len(ks) - L.PREFILTER_LEN)
                rec["n_offsets_total"] += n_off
                sd = {"n_offsets": n_off, "by_max_skip": {}}
                for ms in MAX_SKIPS:
                    res = escalate_ms(hits, Kl, C_HEAD, sign, ms)
                    bar = v["bar"][str(ms)]
                    top = res[:20]
                    sd["by_max_skip"][str(ms)] = {
                        "best_score": (top[0]["score"] if top else None),
                        "best_offset": (top[0]["offset"] if top else None),
                        "hits": [r for r in top if r["score"] >= bar],
                        "top20": top,
                    }
                    if top and top[0]["score"] > best["score"]:
                        best = {"score": top[0]["score"], "pad": pad, "variant": vname,
                                "sign": sign, "max_skip": ms, "offset": top[0]["offset"],
                                "bar": bar, "head": top[0]["head"]}
                v["signs"][str(sign)] = sd
            rec["variants"][vname] = v
            del ks, Kl
            if verbose:
                s = []
                for sg in signs:
                    for ms in MAX_SKIPS:
                        s.append("%+d/ms%d:%.3f" % (
                            sg, ms,
                            v["signs"][str(sg)]["by_max_skip"][str(ms)]["best_score"] or -99))
                print("   %-16s len=%-9d bar3=%.3f bar8=%.3f  %s  (%.0fs)"
                      % (vname, v["len"], v["bar"]["3"], v["bar"]["8"],
                         " ".join(s), time.time() - t0), flush=True)
    rec["best"] = best
    rec["any_hit"] = any(
        b["hits"] for v in rec["variants"].values() for sd in v["signs"].values()
        for b in sd["by_max_skip"].values())
    rec["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    out = os.path.join(HERE, "results_%s.json" % pad.replace(".bin", ""))
    with open(out, "w") as f:
        json.dump(rec, f, indent=1)
    print("   -> %s   best %.3f (%s sign%+d ms%d off=%d) bar %.3f  HIT=%s"
          % (os.path.basename(out), best["score"], best.get("variant"),
             best.get("sign", 0), best.get("max_skip", 0), best.get("offset", -1),
             best.get("bar", 0), rec["any_hit"]), flush=True)
    return rec


# ------------------------------------------------------------------ control
def control_on_real_pad(pad="hash_display.bin", n_trials=8):
    blob = open(os.path.join(DATA, pad), "rb").read()
    print("control: planting into the REAL pad %s (%d B)" % (pad, len(blob)), flush=True)
    r = L.control(blob=blob, n_trials=n_trials)
    r["pad"] = pad
    with open(os.path.join(HERE, "control.json"), "w") as f:
        json.dump(r, f, indent=1)
    print(json.dumps({k: v for k, v in r.items() if k != "rows"}, indent=2))
    print("CONTROL:", "PASS" if r["PASS"] else "FAIL")
    return r


# ------------------------------------------------------------------ merge
def merge():
    recs = [json.load(open(p)) for p in
            sorted(glob.glob(os.path.join(HERE, "results_*.json")))]
    allrows, n_off = [], 0
    for r in recs:
        n_off += r["n_offsets_total"]
        for vn, v in r["variants"].items():
            for sg, sd in v["signs"].items():
                for ms, b in sd["by_max_skip"].items():
                    for row in b["top20"]:
                        allrows.append({"pad": r["pad"], "variant": vn, "sign": int(sg),
                                        "max_skip": int(ms), "offset": row["offset"],
                                        "score": row["score"], "pre": row["pre"],
                                        "bar": v["bar"][ms], "head": row["head"]})
    allrows.sort(key=lambda x: -x["score"])
    ctl, ctlx = None, None
    if os.path.exists(os.path.join(HERE, "control.json")):
        ctl = {k: v for k, v in json.load(open(os.path.join(HERE, "control.json"))).items()
               if k != "rows"}
    if os.path.exists(os.path.join(HERE, "control_ext.json")):
        cx = json.load(open(os.path.join(HERE, "control_ext.json")))
        ctlx = {k: {kk: vv for kk, vv in v.items() if kk not in ("rows", "ranks")}
                for k, v in cx.items()}
    if os.path.exists(os.path.join(HERE, "control_ms.json")):
        ctlx = ctlx or {}
        ctlx["max_skip_sweep"] = json.load(open(os.path.join(HERE, "control_ms.json")))
    nulls3 = [v["null"]["3"]["max"] for r in recs for v in r["variants"].values()]
    nulls8 = [v["null"]["8"]["max"] for r in recs for v in r["variants"].values()]
    best = allrows[0] if allrows else None
    out = {
        "lane": "round16/P1_blockchain",
        "hypothesis": "LP2's keystream is a contiguous run of Bitcoin blockchain bytes",
        "instrument": "round16/lib_padsweep.py dense_scan + beam escalate "
                      "(A1 settings; escalation run at max_skip 3 and 8)",
        "control": ctl,
        "control_ext": ctlx,
        "pads": [{"pad": r["pad"], "bytes": r["bytes"], "sha256": r["sha256"],
                  "n_offsets_total": r["n_offsets_total"],
                  "best": r["best"], "any_hit": r["any_hit"]} for r in recs],
        "n_offsets_total": n_off,
        "fixed_bar": -5.5,
        "null_max_over_lane_ms3": max(nulls3) if nulls3 else None,
        "null_max_over_lane_ms8": max(nulls8) if nulls8 else None,
        "lane_bar_ms3": L.hit_bar(max(nulls3)) if nulls3 else None,
        "lane_bar_ms8": L.hit_bar(max(nulls8)) if nulls8 else None,
        "threshold_for_n_trials": nullmod.threshold_for(n_off) if n_off else None,
        "expected_null_max_at_n": nullmod.expected_max(n_off) if n_off else None,
        "best_overall": best,
        "verdict": ("HIT" if any(r["any_hit"] for r in recs) else "NEGATIVE"),
        "top20": allrows[:20],
    }
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("top20", "control_ext")}, indent=2))
    print("\ntop 20:")
    for r in allrows[:20]:
        print("  %-24s %-16s %+d ms%d off=%-9d score=%7.3f bar=%.3f  %s"
              % (r["pad"], r["variant"], r["sign"], r["max_skip"], r["offset"],
                 r["score"], r["bar"], r["head"][:32]))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--merge", action="store_true")
    ap.add_argument("--subsets", action="store_true")
    a = ap.parse_args()
    if a.subsets:
        build_subsets()
    if a.control:
        control_on_real_pad()
    if a.pad:
        sweep_pad(a.pad)
    if a.all:
        build_subsets()
        for p in PADS:
            if os.path.exists(os.path.join(DATA, p)):
                sweep_pad(p)
    if a.merge:
        merge()
