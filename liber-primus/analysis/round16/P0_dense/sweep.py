"""ROUND 16 / LANE P0 - DENSE re-sweep of the author's own CicadaOS binary pads.

What this is
------------
Round 12 front A1 fed six CicadaOS blobs (incl. the 118,818,811-byte `DATA/560.13`) to the
skip-aware beam decoder and returned NEGATIVE. It walked an **eight-offset ladder** per
keystream variant. On 560.13 that is 8 / 118,818,811 = 6.7e-8 of the offset space. A1's
verdict is sound *for those eight offsets*; it is not a bound on the pad.

This lane re-runs the same pads with `lib_padsweep.dense_scan`, which scores **every**
offset with a vectorised rune-index trigram model over a 24-rune head window, then beam-
decodes the survivors with A1's exact settings (beam_w=120, max_skip=3, head=400) on A1's
exact `score_norm` scale, against A1's own shuffle null (n=200).

Coverage honesty
----------------
The instrument's control (lib_padsweep.control(), re-run 2026-08-19 on this box) recovers
8/8 planted pads at the beam stage but the dense prefilter retains the true offset in only
5/8. **Measured survival rate 0.625.** Every coverage number this script prints is therefore
reported twice: raw offsets scanned, and offsets x 0.625 - the honest effective coverage.
That is a POWER limit, not a soundness limit.

HIT bar (pre-registered, round16/PREREG.md, = A1's, unchanged)
    score_norm >= -5.5  AND  score_norm >= null_max + 0.5
Nothing else counts. A decode is never called English by reading it.

Usage
-----
    python sweep.py --pads small          # everything except 560.13   (~10 min)
    python sweep.py --pads big            # DATA_560.13 only           (~50 min)
    python sweep.py --pads all
    python sweep.py --pads small --no-hex # skip the hexchars builder
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
PADDIR = os.path.join(L.ROOT, "analysis", "round12", "A1", "pads")

# label -> (filename, note)
PADS = {
    "560.13":        ("DATA_560.13",                   "118.8 MB; A1 swept 8 offsets"),
    "_560.00_auth":  ("DATA__560.00.iso-authoritative", "untruncated ISO copy"),
    "_560.00_trunc": ("DATA__560.00",                  "mirror copy, byte-prefix of auth"),
    "560.17":        ("DATA_560.17",                   ""),
    "prime_echo":    ("usr_local_bin_prime_echo",      "ELF binary"),
    "tmp_folly":     ("tmp_folly",                     ""),
    "tmp_wisdom":    ("tmp_wisdom",                    ""),
}
SMALL = ["_560.00_auth", "_560.00_trunc", "560.17", "prime_echo", "tmp_folly", "tmp_wisdom"]
BIG = ["560.13"]


def log(m, fh=None):
    print(m, flush=True)
    if fh:
        fh.write(m + "\n")
        fh.flush()


# ---------------------------------------------------------------- windowed beam wrappers
# `sk.beam_decode` takes a python list for K and indexes it absolutely. On a 118 M-symbol
# keystream materialising that list costs ~1 GB and minutes, per config. beam_decode only
# ever touches K[o .. o + HEAD*(MAX_SKIP+1)], so we hand it exactly that window with o=0.
# `_assert_window_equiv()` proves the two are bit-identical before any sweeping happens.
def beam_win(K, seq, sign, o):
    w = [int(x) for x in K[o:o + WIN]]
    if len(w) < WIN:
        return None
    return sk.beam_decode([int(x) for x in seq], w, sign=sign, o=0,
                          beam_w=BEAM_W, max_skip=MAX_SKIP)


def escalate_win(hits, K, C, sign, top=40):
    """A1's beam on the dense scan's survivors - same as L.escalate, windowed."""
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
    """L.null_ceiling verbatim (A1's null), windowed. Offsets are identical to the
    unwindowed version because `span` is computed from the FULL keystream length."""
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
    b = open(os.path.join(PADDIR, "DATA_560.17"), "rb").read()[:400000]
    K = L.ks_mod29(b)
    C = nc.unsolved()
    h = L.dense_scan(K, C, sign=-1)[:6]
    a = L.escalate(h, K, C, sign=-1, top=6)
    c = escalate_win(h, K, C, -1, top=6)
    assert [r["score"] for r in a] == [r["score"] for r in c], "escalate window MISMATCH"
    assert L.null_ceiling(K, n=12) == null_win(K, n=12), "null window MISMATCH"
    return True


# ---------------------------------------------------------------- one pad
def sweep_pad(label, path, C, builders, fh, keep=400, top=40):
    n_bytes = os.path.getsize(path)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    blob = open(path, "rb").read()
    log("\n" + "=" * 74, fh)
    log("PAD %s  %s B  sha256 %s" % (label, format(n_bytes, ","), h.hexdigest()), fh)

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
            log("  %-16s |K|=%11s  off/sign=%11s  null_max=%.3f bar=%.3f  best=%.3f  [%.0fs]"
                % (vname, format(len(K), ","), format(n_off, ","), nmax, bar, best,
                   time.time() - t0), fh)
            del K
    rows.sort(key=lambda r: r["score"], reverse=True)
    hits = [r for r in rows if r["score"] >= -5.5 and r["score"] >= r["bar"]]
    return {
        "pad": label, "file": os.path.basename(path), "bytes": n_bytes,
        "sha256": h.hexdigest(),
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pads", default="all", choices=["all", "small", "big"])
    ap.add_argument("--no-hex", action="store_true", help="skip the hexchars builder")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    labels = {"all": SMALL + BIG, "small": SMALL, "big": BIG}[a.pads]
    builders = [b for b in L.BUILDERS if not (a.no_hex and b == "hexchars")]
    out_json = a.out or os.path.join(HERE, "results_%s.json" % a.pads)
    logf = open(os.path.join(HERE, "sweep_%s.log" % a.pads), "a", encoding="utf-8")

    t0 = time.time()
    log("=" * 74, logf)
    log("ROUND 16 / P0 - DENSE offset re-sweep of the CicadaOS pads", logf)
    log("pads=%s  builders=%s  signs=(-1,+1)  fwd+rev" % (labels, builders), logf)
    log("beam_w=%d max_skip=%d head=%d prefilter_len=%d" % (BEAM_W, MAX_SKIP, HEAD, PLEN),
        logf)
    log("=" * 74, logf)

    log("window-equivalence check ...", logf)
    _assert_window_equiv()
    log("  OK: windowed beam/null are bit-identical to lib_padsweep's", logf)

    C = nc.unsolved()
    log("unsolved runes: %d" % len(C), logf)

    pads = []
    for lab in labels:
        fn = PADS[lab][0]
        p = os.path.join(PADDIR, fn)
        if not os.path.exists(p):
            log("MISSING pad %s at %s -- skipped" % (lab, p), logf)
            continue
        pads.append(sweep_pad(lab, p, C, builders, logf))
        json.dump({"partial": True, "pads": pads}, open(out_json, "w"), indent=2)

    tot_off = sum(p["coverage"]["offsets_scanned"] for p in pads)
    tot_cfg = sum(p["coverage"]["configs"] for p in pads)
    tot_beam = sum(p["coverage"]["beam_escalations"] for p in pads)
    allrows = sorted((r for p in pads for r in p["top"]),
                     key=lambda r: r["score"], reverse=True)
    allhits = [r for p in pads for r in p["hits"]]
    best = allrows[0] if allrows else None

    thr_off = NULLMOD.threshold_for(max(2, tot_off))
    thr_beam = NULLMOD.threshold_for(max(2, tot_beam))

    out = {
        "lane": "round16/P0_dense",
        "date": time.strftime("%Y-%m-%d"),
        "instrument": "round16/lib_padsweep.py dense_scan + A1 beam (w=120, skip<=3, head=400)",
        "control": {"source": "lib_padsweep.control()", "PASS": True,
                    "dense_found": 5, "beam_recovered": 8, "n_trials": 8,
                    "survival_rate": 0.625,
                    "note": "re-run on this box 2026-08-19, reproduces PREREG.md exactly"},
        "hit_bar_rule": "score_norm >= -5.5 AND >= null_max + 0.5 (pre-registered, A1's)",
        "coverage_total": {
            "pads": len(pads),
            "configs": tot_cfg,
            "offsets_scanned": tot_off,
            "survival_rate": 0.625,
            "effective_offsets": int(round(tot_off * 0.625)),
            "beam_escalations": tot_beam,
            "A1_offsets_per_variant_for_comparison": 8,
        },
        "extreme_value_check": {
            "note": "AGENTS.md lesson 3: a fixed bar is invalid at large N. "
                    "benchmark/null.threshold_for() at this lane's trial counts.",
            "threshold_for_offsets_scanned": thr_off,
            "threshold_for_beam_escalations": thr_beam,
            "raw_best": best["score"] if best else None,
        },
        "best": best,
        "n_hits": len(allhits), "hits": allhits,
        "top20": allrows[:20],
        "pads": pads,
        "verdict": "HIT" if allhits else "NEGATIVE",
        "elapsed_s": round(time.time() - t0, 1),
    }
    json.dump(out, open(out_json, "w"), indent=2)

    log("\n" + "=" * 74, logf)
    log("TOTAL coverage: %d configs, %s offsets scanned = %s effective (x0.625 survival); "
        "%s beam escalations"
        % (tot_cfg, format(tot_off, ","), format(int(round(tot_off * 0.625)), ","),
           format(tot_beam, ",")), logf)
    log("A1 for comparison: 8 offsets per variant.", logf)
    if best:
        log("best score_norm = %.4f  (%s %s s%+d o=%d)  bar=%.3f"
            % (best["score"], best["pad"], best["variant"], best["sign"],
               best["offset"], best["bar"]), logf)
    log("threshold_for(n=%s) = %.4f   threshold_for(n=%s) = %.4f"
        % (format(tot_off, ","), thr_off, format(tot_beam, ","), thr_beam), logf)
    log("VERDICT: %s   -> %s   (%.0fs)" % (out["verdict"], out_json, out["elapsed_s"]), logf)
    logf.close()


if __name__ == "__main__":
    main()
