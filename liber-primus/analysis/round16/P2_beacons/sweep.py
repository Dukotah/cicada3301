"""ROUND 16 / LANE P2 - DENSE offset sweep of PUBLIC RANDOMNESS ARCHIVES as pads.

What this is
------------
`analysis/round10/L5-seed32/CENSUS.md:87-94` closes the search programme by putting
`random.org` next to `/dev/urandom` and physical dice: "a pad with no compressible key ...
nothing can touch it". Two different properties are merged there - *leaves no seed* and
*leaves no public record*. A published, archived randomness service has the first and not
the second. NIST's Randomness Beacon emitted a signed 512-bit value every 60 s starting
2013-09-05, four months before LP2 was posted; RANDOM.ORG has published one 1 MiB file of
true random data per day since 2006-03-11. Both are seedless full-entropy pads with a
public, dated, byte-exact record. Neither has ever been swept.

Instrument
----------
`round16/lib_padsweep.py`: vectorised rune-index trigram prefilter over a 24-rune head
window scoring EVERY offset, then A1's beam (beam_w=120, max_skip<=3, head=400) on the
survivors, adjudicated on A1's `score_norm` scale against A1's shuffle null (n=200), so
every number here is directly comparable to `round12/A1/results_560_13.json`.

Coverage honesty
----------------
lib_padsweep.control() recovers 8/8 planted pads at the beam stage but the dense prefilter
retains the true offset in only 5/8: **measured survival rate 0.625**. Every coverage number
below is printed twice - raw offsets scanned, and offsets x 0.625. That is a POWER limit,
not a soundness limit.

HIT bar (pre-registered, round16/PREREG.md, = A1's, unchanged)
    score_norm >= -5.5  AND  score_norm >= null_max + 0.5
Nothing else counts. A decode is never called English by reading it (AGENTS.md 3).

Usage
-----
    python fetch.py beacon --start 2013-09-05 --end 2014-01-06
    python fetch.py randomorg --months 2013-09,2013-10,2013-11,2013-12,2014-01
    python sweep.py --pad pad_outputValue_2013-09-05_2014-01-06.bin
    python sweep.py --all
"""
import argparse, hashlib, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
R16 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, R16)

import numpy as np                                   # noqa: E402
import lib_padsweep as L                             # noqa: E402
from lib_padsweep import nc, sk                      # noqa: E402

sys.path.insert(0, os.path.join(L.ROOT, "benchmark"))
import null as NULLMOD                               # noqa: E402

HEAD, BEAM_W, MAX_SKIP = L.HEAD, L.BEAM_W, L.MAX_SKIP
PLEN = L.PREFILTER_LEN
WIN = HEAD * (MAX_SKIP + 1) + 8                      # key symbols one beam_decode reads
DATA = os.path.join(HERE, "data")

# `hexchars` reads the blob as its UPPERCASE HEX STRING. That builder is meaningful for the
# NIST Beacon, whose values are *published as hex text on a web page* - a 2013 author
# copy-pasting an outputValue is handling the hex characters, not the bytes. It is NOT
# meaningful for RANDOM.ORG's archive, which is distributed as an opaque binary file, and on
# a 155 MB pad it doubles an already 2-hour scan. Default: on for beacon pads, off for
# random.org. Override with --hex / --no-hex.
BYTE_BUILDERS = ["mod29", "hi_nibble", "lo_nibble", "byte_scaled", "prime_to_idx"]

# Opt-in builders that are deliberately NOT in `lib_padsweep.BUILDERS`, so that numbers
# measured against the original set stay comparable.
#   nibbles - the TRUE hex-text reading: every hex character as its value 0-15, in order.
#             `hexchars` is NOT this: eng_to_idx drops anything unmappable, so `hexchars` is
#             the A-F SUBSEQUENCE of the hex string (it kept 23,766 of 6,699,648 hex chars
#             on the first beacon pad). Beacon outputValues are PUBLISHED AS HEX TEXT, so
#             for this lane `nibbles` is a higher-prior variant than `hexchars`, and until
#             lane P1 caught the bug it had never been run anywhere in this repo.
EXTRA_BUILDERS = {"nibbles": L.ks_nibbles}


def get_builder(name):
    return L.BUILDERS[name] if name in L.BUILDERS else EXTRA_BUILDERS[name]


def log(m, fh=None):
    print(m, flush=True)
    if fh:
        fh.write(m + "\n")
        fh.flush()


# ---------------------------------------------------------------- windowed beam wrappers
# `sk.beam_decode` takes a python list for K and indexes it absolutely; materialising that
# for a 155 M-symbol keystream costs ~1 GB per config. beam_decode only ever touches
# K[o .. o + HEAD*(MAX_SKIP+1)], so hand it exactly that window with o=0.
# `_assert_window_equiv()` proves the two are bit-identical before any sweeping happens.
def win_len(ms=MAX_SKIP):
    return HEAD * (ms + 1) + 8


def beam_win(K, seq, sign, o, ms=MAX_SKIP):
    W = win_len(ms)
    w = [int(x) for x in K[o:o + W]]
    if len(w) < W:
        return None
    return sk.beam_decode([int(x) for x in seq], w, sign=sign, o=0,
                          beam_w=BEAM_W, max_skip=ms)


def escalate_win(hits, K, C, sign, top=40, ms=MAX_SKIP):
    out = []
    nK = len(K)
    for score, o in hits[:top]:
        o = int(o)
        if o + win_len(ms) >= nK:
            continue
        bd = beam_win(K, C[:HEAD], sign, o, ms=ms)
        if bd is None:
            continue
        out.append({"offset": o, "sign": sign, "pre": float(score),
                    "score": bd["score"], "head": bd["translit"][:64]})
    out.sort(key=lambda r: r["score"], reverse=True)
    return out


def null_win(K, seq_len=HEAD, n=200, seed0=3301, ms=MAX_SKIP):
    """L.null_ceiling verbatim (A1's null), windowed. The null is re-run at whatever
    max_skip the escalation uses - a beam with a bigger skip budget searches a bigger space
    and so has a higher noise ceiling; scoring a candidate at ms=8 against an ms=3 null
    would manufacture a hit out of nothing."""
    base = nc.unsolved()[:seq_len]
    span = max(1, len(K) - seq_len * (ms + 1) - 8)
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(base)
        r.shuffle(s)
        bd = beam_win(K, s, -1, (k * 37) % span, ms=ms)
        if bd is not None:
            vals.append(bd["score"])
    return float(np.mean(vals)), float(np.max(vals))


def _assert_window_equiv():
    """Prove the windowed wrappers reproduce lib_padsweep's own functions exactly."""
    b = hashlib.sha512(b"P2-WINDOW-EQUIV").digest()
    while len(b) < 400000:
        b += hashlib.sha512(b[-64:]).digest()
    K = L.ks_mod29(b)
    C = nc.unsolved()
    h = L.dense_scan(K, C, sign=-1)[:6]
    a = L.escalate(h, K, C, sign=-1, top=6)
    c = escalate_win(h, K, C, -1, top=6)
    assert [r["score"] for r in a] == [r["score"] for r in c], "escalate window MISMATCH"
    assert L.null_ceiling(K, n=12) == null_win(K, n=12), "null window MISMATCH"
    return True



# ---------------------------------------------------------------- fast dense scan
# Pure performance refactor of `lib_padsweep.dense_scan`, proved bit-identical by
# `_assert_scan_equiv()` below before any sweeping happens. Same arithmetic, different
# memory layout: dense_scan builds a (chunk, plen) sliding window and then does 3-D fancy
# indexing down NON-CONTIGUOUS columns, which is memory-bound and ~10x slower than it needs
# to be. The identity  P[i, j] = (C[j] + sign*K[i+j]) % N  lets the transposed (plen, chunk)
# array be built from plen CONTIGUOUS 1-D slices of K, after which the trigram lookup is a
# single flat take() into T.ravel() with preallocated output buffers. This matters because
# the honest answer to "did you scan every offset" has to survive a 95 MB pad.
def fast_dense_scan(K, C, sign=-1, plen=PLEN, keep=400, chunk=1 << 21):
    T = L.trigram_model()
    flat = np.ascontiguousarray(T.reshape(-1))
    K = np.ascontiguousarray(np.asarray(K, dtype=np.int16))
    C = np.asarray(C[:plen], dtype=np.int16)
    n_off = len(K) - plen
    if n_off <= 0:
        return []
    best_s = np.full(0, -np.inf, dtype=np.float32)
    best_o = np.zeros(0, dtype=np.int64)
    P = np.empty((plen, min(chunk, n_off)), dtype=np.int32)
    idx = np.empty(min(chunk, n_off), dtype=np.int32)
    buf = np.empty(min(chunk, n_off), dtype=np.float32)
    for start in range(0, n_off, chunk):
        stop = min(start + chunk, n_off)
        m = stop - start
        Pv = P[:, :m]
        for j in range(plen):
            np.mod(C[j] + sign * K[start + j:start + j + m].astype(np.int32), L.N, out=Pv[j])
        sc = np.zeros(m, dtype=np.float32)
        iv, bv = idx[:m], buf[:m]
        for j in range(2, plen):
            np.multiply(Pv[j - 2], 841, out=iv)
            iv += Pv[j - 1] * 29
            iv += Pv[j]
            np.take(flat, iv, out=bv)
            sc += bv
        sc /= (plen - 2)
        offs = np.arange(start, stop, dtype=np.int64)
        cat_s = np.concatenate([best_s, sc])
        cat_o = np.concatenate([best_o, offs])
        k = min(keep, len(cat_s))
        top = np.argpartition(-cat_s, k - 1)[:k]
        order = top[np.argsort(-cat_s[top])]
        best_s, best_o = cat_s[order], cat_o[order]
    return list(zip(best_s.tolist(), best_o.tolist()))


def _assert_scan_equiv():
    """fast_dense_scan must reproduce lib_padsweep.dense_scan EXACTLY - same offsets in the
    same order with the same float32 scores - across builders and both signs."""
    b = hashlib.sha512(b"P2-SCAN-EQUIV").digest()
    while len(b) < 600_000:
        b += hashlib.sha512(b[-64:]).digest()
    C = nc.unsolved()
    for name in ("mod29", "hi_nibble", "hexchars"):
        K = L.BUILDERS[name](b)
        for sign in (-1, +1):
            a = L.dense_scan(K, C, sign=sign, keep=400)
            c = fast_dense_scan(K, C, sign=sign, keep=400)
            assert len(a) == len(c), "scan length MISMATCH %s %d" % (name, sign)
            assert all(x[1] == y[1] for x, y in zip(a, c)),                 "scan offset MISMATCH %s %d" % (name, sign)
            assert all(x[0] == y[0] for x, y in zip(a, c)),                 "scan score MISMATCH %s %d" % (name, sign)
    return True



# ---------------------------------------------------------------- one config at a time
# A 95 MB pad x 10 keystream variants x 2 signs is hours of wall clock in ONE process. That
# is a bad shape: a single interruption costs everything, and this box is shared with three
# other lanes. So the unit of work here is ONE (pad, builder, direction, sign) config, each
# a few minutes, each writing its own part file. `merge.py` reassembles them. The shuffle
# null is a property of the KEYSTREAM, not of the sign, so it is computed once per variant
# and cached - recomputing it per sign would double the fixed cost for nothing.
PARTS = os.path.join(HERE, "parts")


def _null_cached(pad, vname, K, fh=None, ms=MAX_SKIP):
    os.makedirs(PARTS, exist_ok=True)
    cp = os.path.join(PARTS, "null__%s__%s%s.json"
                      % (pad, vname, "" if ms == MAX_SKIP else "__ms%d" % ms))
    if os.path.exists(cp):
        d = json.load(open(cp, encoding="utf-8"))
        return d["mean"], d["max"]
    t = time.time()
    nmean, nmax = null_win(K, n=200, ms=ms)
    json.dump({"pad": pad, "variant": vname, "mean": nmean, "max": nmax, "n": 200,
               "max_skip": ms,
               "seconds": round(time.time() - t, 1)}, open(cp, "w", encoding="utf-8"),
              indent=2)
    return nmean, nmax


def sweep_config(path, bname, rev, sign, keep=400, top=40, fh=None, ms=MAX_SKIP):
    pad = os.path.basename(path)
    vname = bname + ("_rev" if rev else "")
    os.makedirs(PARTS, exist_ok=True)
    outp = os.path.join(PARTS, "%s__%s__s%+d%s.json"
                        % (pad, vname, sign, "" if ms == MAX_SKIP else "__ms%d" % ms))
    if os.path.exists(outp):
        log("  SKIP (done) %s %s s%+d" % (pad, vname, sign), fh)
        return json.load(open(outp, encoding="utf-8"))
    blob = open(path, "rb").read()
    sha = hashlib.sha256(blob).hexdigest()
    t0 = time.time()
    K = get_builder(bname)(blob[::-1] if rev else blob)
    del blob
    nmean, nmax = _null_cached(pad, vname, K, fh, ms=ms)
    bar = L.hit_bar(nmax)
    n_off = max(0, len(K) - PLEN)
    C = nc.unsolved()
    hits = fast_dense_scan(K, C, sign=sign, keep=keep)
    esc = escalate_win(hits, K, C, sign, top=top, ms=ms)
    rows = [{"pad": pad, "variant": vname, "sign": sign, "offset": r["offset"],
             "pre": r["pre"], "score": r["score"], "head": r["head"],
             "null_max": nmax, "bar": bar} for r in esc]
    rows.sort(key=lambda r: r["score"], reverse=True)
    res = {"pad": pad, "sha256": sha, "bytes": os.path.getsize(path), "builder": bname,
           "rev": bool(rev), "variant": vname, "sign": sign, "max_skip": ms,
           "beam_w": BEAM_W, "head": HEAD, "prefilter_len": PLEN,
           "keystream_len": int(len(K)), "offsets_scanned": int(n_off),
           "null_mean": nmean, "null_max": nmax, "bar": bar,
           "beam_escalations": len(rows), "top": rows[:20],
           "hits": [r for r in rows if r["score"] >= -5.5 and r["score"] >= r["bar"]],
           "best": rows[0]["score"] if rows else None,
           "seconds": round(time.time() - t0, 1)}
    json.dump(res, open(outp, "w", encoding="utf-8"), indent=2)
    log("  %-16s s%+d ms=%d |K|=%12s off=%12s null_max=%.3f bar=%.3f best=%.3f [%.0fs] -> %s"
        % (vname, sign, ms, format(len(K), ","), format(n_off, ","), nmax, bar,
           res["best"] if res["best"] is not None else float("nan"),
           res["seconds"], os.path.basename(outp)), fh)
    return res


# ---------------------------------------------------------------- one pad
def sweep_pad(path, C, builders, fh, keep=400, top=40, checkpoint=None):
    label = os.path.basename(path)
    n_bytes = os.path.getsize(path)
    blob = open(path, "rb").read()
    sha = hashlib.sha256(blob).hexdigest()
    log("\n" + "=" * 78, fh)
    log("PAD %s  %s B  sha256 %s" % (label, format(n_bytes, ","), sha), fh)

    rows, cov = [], {"offsets": 0, "configs": 0, "beams": 0}
    nulls = {}
    for bname in builders:
        for rev in (False, True):
            vname = bname + ("_rev" if rev else "")
            t0 = time.time()
            try:
                K = L.BUILDERS[bname](blob[::-1] if rev else blob)
            except MemoryError:
                log("  %s: MemoryError building keystream -- SKIPPED" % vname, fh)
                continue
            if len(K) < WIN + 64:
                log("  %s: keystream too short (%d) -- skipped" % (vname, len(K)), fh)
                del K
                continue
            nmean, nmax = null_win(K, n=200)
            bar = L.hit_bar(nmax)
            nulls[vname] = {"mean": nmean, "max": nmax, "bar": bar}
            n_off = max(0, len(K) - PLEN)
            for sign in (-1, +1):
                hits = fast_dense_scan(K, C, sign=sign, keep=keep)
                esc = escalate_win(hits, K, C, sign, top=top)
                cov["offsets"] += n_off
                cov["configs"] += 1
                cov["beams"] += len(esc)
                for r in esc:
                    rows.append({"pad": label, "variant": vname, "sign": sign,
                                 "offset": r["offset"], "pre": r["pre"],
                                 "score": r["score"], "head": r["head"],
                                 "null_max": nmax, "bar": bar})
            best = max((r["score"] for r in rows if r["variant"] == vname),
                       default=float("nan"))
            log("  %-16s |K|=%12s  off/sign=%12s  null_max=%.3f bar=%.3f  best=%.3f  [%.0fs]"
                % (vname, format(len(K), ","), format(n_off, ","), nmax, bar, best,
                   time.time() - t0), fh)
            del K
            # Checkpoint after EVERY variant. On a contended box a run can be cut off part
            # way through; a partial sweep is still a valid (smaller) coverage bound, but
            # only if it survives on disk. Losing 11 completed variants because the 12th
            # was interrupted would be self-inflicted.
            if checkpoint:
                checkpoint(_pack(label, path, n_bytes, sha, builders, rows, cov, nulls,
                                 partial=True))
    return _pack(label, path, n_bytes, sha, builders, rows, cov, nulls, partial=False)


def _pack(label, path, n_bytes, sha, builders, rows, cov, nulls, partial):
    rows = sorted(rows, key=lambda r: r["score"], reverse=True)
    hits = [r for r in rows if r["score"] >= -5.5 and r["score"] >= r["bar"]]
    return {
        "pad": label, "bytes": n_bytes, "sha256": sha, "partial_pad": partial,
        "builders": list(builders), "signs": [-1, 1], "directions": ["fwd", "rev"],
        "coverage": {
            "configs": cov["configs"],
            "offsets_scanned": cov["offsets"],
            "survival_rate": 0.625,
            "effective_offsets": int(round(cov["offsets"] * 0.625)),
            "beam_escalations": cov["beams"],
        },
        "nulls": nulls,
        "best": rows[0] if rows else None,
        "n_hits": len(hits), "hits": hits,
        "top": rows[:20],
        "verdict": "HIT" if hits else "NEGATIVE",
    }


def discover():
    if not os.path.isdir(DATA):
        return []
    return sorted(f for f in os.listdir(DATA) if f.startswith("pad_") and f.endswith(".bin"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", action="append", default=None, help="filename inside data/")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--hex", dest="hex", action="store_true", default=None)
    ap.add_argument("--no-hex", dest="hex", action="store_false")
    ap.add_argument("--out", default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--builder", default=None,
                    help="sweep ONE variant of ONE pad and write a part file")
    ap.add_argument("--rev", type=int, default=0)
    ap.add_argument("--sign", type=int, default=None, help="-1 or +1; omit for both")
    ap.add_argument("--max-skip", type=int, default=MAX_SKIP,
                    help="beam skip budget for the escalation AND its null (A1 used 3)")
    ap.add_argument("--skip-equiv", action="store_true",
                    help="skip the two equivalence proofs (run them once per session)")
    a = ap.parse_args()

    if a.builder:
        os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
        fh = open(os.path.join(HERE, "logs", "parts.log"), "a", encoding="utf-8")
        if not a.skip_equiv:
            _assert_window_equiv()
            _assert_scan_equiv()
            log("  equivalence proofs OK", fh)
        for fn in (a.pad or []):
            for sg in ([a.sign] if a.sign else [-1, 1]):
                sweep_config(os.path.join(DATA, fn), a.builder, a.rev, sg, fh=fh,
                             ms=a.max_skip)
        fh.close()
        return

    pads = a.pad or (discover() if a.all else [])
    if not pads:
        print("no pads. run fetch.py first. available:", discover())
        return
    tag = a.tag or (pads[0].replace("pad_", "").replace(".bin", "") if len(pads) == 1
                    else "all")
    out_json = a.out or os.path.join(HERE, "results_%s.json" % tag)
    logf = open(os.path.join(HERE, "logs", "sweep_%s.log" % tag), "a", encoding="utf-8")

    t0 = time.time()
    log("=" * 78, logf)
    log("ROUND 16 / P2 - DENSE offset sweep of PUBLIC RANDOMNESS ARCHIVES", logf)
    log("pads=%s" % pads, logf)
    log("beam_w=%d max_skip=%d head=%d prefilter_len=%d" % (BEAM_W, MAX_SKIP, HEAD, PLEN),
        logf)
    log("=" * 78, logf)
    log("window-equivalence check ...", logf)
    _assert_window_equiv()
    log("  OK: windowed beam/null are bit-identical to lib_padsweep's", logf)
    log("dense-scan equivalence check ...", logf)
    _assert_scan_equiv()
    log("  OK: fast_dense_scan is bit-identical to lib_padsweep.dense_scan", logf)

    C = nc.unsolved()
    log("unsolved runes: %d" % len(C), logf)

    results = []
    for fn in pads:
        p = os.path.join(DATA, fn)
        if not os.path.exists(p):
            log("MISSING pad %s -- skipped" % p, logf)
            continue
        use_hex = a.hex
        if use_hex is None:
            use_hex = "randomorg" not in fn        # see BYTE_BUILDERS comment
        builders = BYTE_BUILDERS + (["hexchars"] if use_hex else [])
        def _ckpt(row, _r=results, _o=out_json):
            json.dump({"partial": True, "pads": _r + [row]}, open(_o, "w"), indent=2)
        results.append(sweep_pad(p, C, builders, logf, checkpoint=_ckpt))
        json.dump({"partial": True, "pads": results}, open(out_json, "w"), indent=2)

    tot_off = sum(p["coverage"]["offsets_scanned"] for p in results)
    tot_cfg = sum(p["coverage"]["configs"] for p in results)
    tot_beam = sum(p["coverage"]["beam_escalations"] for p in results)
    allrows = sorted((r for p in results for r in p["top"]),
                     key=lambda r: r["score"], reverse=True)
    allhits = [r for p in results for r in p["hits"]]
    best = allrows[0] if allrows else None

    out = {
        "lane": "round16/P2_beacons",
        "date": time.strftime("%Y-%m-%d"),
        "instrument": "round16/lib_padsweep.py dense_scan + A1 beam (w=120, skip<=3, head=400)",
        "control": {"source": "lib_padsweep.control()", "PASS": True,
                    "dense_found": 5, "beam_recovered": 8, "n_trials": 8,
                    "survival_rate": 0.625,
                    "note": "PREREG.md gate, 2026-08-19; window-equivalence re-checked here"},
        "hit_bar_rule": "score_norm >= -5.5 AND >= null_max + 0.5 (pre-registered, A1's)",
        "coverage_total": {
            "pads": len(results), "configs": tot_cfg,
            "offsets_scanned": tot_off, "survival_rate": 0.625,
            "effective_offsets": int(round(tot_off * 0.625)),
            "beam_escalations": tot_beam,
            "A1_offsets_per_variant_for_comparison": 8,
        },
        "extreme_value_check": {
            "note": "AGENTS.md lesson 3: a fixed bar is invalid at large N. "
                    "benchmark/null.threshold_for() at this lane's trial counts.",
            "threshold_for_offsets_scanned": NULLMOD.threshold_for(max(2, tot_off)),
            "threshold_for_beam_escalations": NULLMOD.threshold_for(max(2, tot_beam)),
            "raw_best": best["score"] if best else None,
        },
        "best": best, "n_hits": len(allhits), "hits": allhits,
        "top20": allrows[:20], "pads": results,
        "verdict": "HIT" if allhits else "NEGATIVE",
        "elapsed_s": round(time.time() - t0, 1),
    }
    json.dump(out, open(out_json, "w"), indent=2)

    log("\n" + "=" * 78, logf)
    log("TOTAL: %d configs, %s offsets scanned = %s effective (x0.625); %s beam escalations"
        % (tot_cfg, format(tot_off, ","), format(int(round(tot_off * 0.625)), ","),
           format(tot_beam, ",")), logf)
    if best:
        log("best score_norm = %.4f  (%s %s s%+d o=%d)  bar=%.3f"
            % (best["score"], best["pad"], best["variant"], best["sign"],
               best["offset"], best["bar"]), logf)
    log("threshold_for(%s offsets) = %.4f ; threshold_for(%s beams) = %.4f"
        % (format(tot_off, ","), out["extreme_value_check"]["threshold_for_offsets_scanned"],
           format(tot_beam, ","), out["extreme_value_check"]["threshold_for_beam_escalations"]),
        logf)
    log("VERDICT: %s   -> %s   (%.0fs)" % (out["verdict"], out_json, out["elapsed_s"]), logf)
    logf.close()


if __name__ == "__main__":
    main()
