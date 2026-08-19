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
def beam_win(K, seq, sign, o):
    w = [int(x) for x in K[o:o + WIN]]
    if len(w) < WIN:
        return None
    return sk.beam_decode([int(x) for x in seq], w, sign=sign, o=0,
                          beam_w=BEAM_W, max_skip=MAX_SKIP)


def escalate_win(hits, K, C, sign, top=40):
    out = []
    nK = len(K)
    for score, o in hits[:top]:
        o = int(o)
        if o + WIN >= nK:
            continue
        bd = beam_win(K, C[:HEAD], sign, o)
        if bd is None:
            continue
        out.append({"offset": o, "sign": sign, "pre": float(score),
                    "score": bd["score"], "head": bd["translit"][:64]})
    out.sort(key=lambda r: r["score"], reverse=True)
    return out


def null_win(K, seq_len=HEAD, n=200, seed0=3301):
    """L.null_ceiling verbatim (A1's null), windowed."""
    base = nc.unsolved()[:seq_len]
    span = max(1, len(K) - seq_len * (MAX_SKIP + 1) - 8)
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(base)
        r.shuffle(s)
        bd = beam_win(K, s, -1, (k * 37) % span)
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


# ---------------------------------------------------------------- one pad
def sweep_pad(path, C, builders, fh, keep=400, top=40):
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
                hits = L.dense_scan(K, C, sign=sign, keep=keep)
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
    rows.sort(key=lambda r: r["score"], reverse=True)
    hits = [r for r in rows if r["score"] >= -5.5 and r["score"] >= r["bar"]]
    return {
        "pad": label, "bytes": n_bytes, "sha256": sha,
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
    a = ap.parse_args()

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
        results.append(sweep_pad(p, C, builders, logf))
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
