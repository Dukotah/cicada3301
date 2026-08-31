"""Round 18 / Marsaglia — dense every-offset sweep of the 1995 Marsaglia CDROM pads.

Instrument: analysis/round17/lib_padsweep.py (SHARED, unedited). Control PASSES on the
real Marsaglia data once the trigram model is rebuilt from committed quadgrams — see
PREREG.md and build_trigram_from_quadgrams.py. Run that builder first.

The pads are uniform binary, so only lib_padsweep's 6 byte builders × {fwd,rev} apply;
no digit/text builders. Resumable: one checkpoint JSON per pad in data/partial/, a
per-invocation time budget, re-run to continue.

Run:  python analysis/round18/marsaglia/build_trigram_from_quadgrams.py   # once
      python analysis/round18/marsaglia/sweep.py --budget 3000            # repeat until done
"""
import os, sys, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "analysis", "round17"))
import numpy as np                                            # noqa: E402
import lib_padsweep as L                                      # noqa: E402
import skipdecode as sk                                       # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "benchmark"))
import null as nullmod                                        # noqa: E402

PADS = os.path.join(HERE, "data", "pads")
MANIFEST = os.path.join(HERE, "pads_manifest.json")
PARTIAL = os.path.join(HERE, "data", "partial")
OUT = os.path.join(HERE, "results.json")
SURVIVAL = 0.375     # measured on the real Marsaglia pad by lib_padsweep.control(bits.01)


def escalate_head(hits, K, C, sign, head, top=40):
    Kl = [int(x) for x in K]
    out = []
    for score, o in hits[:top]:
        o = int(o)
        if o + head * (L.MAX_SKIP + 1) + 8 >= len(Kl):
            continue
        bd = sk.beam_decode([int(x) for x in C[:head]], Kl, sign=sign, o=o,
                            beam_w=L.BEAM_W, max_skip=L.MAX_SKIP)
        out.append({"offset": o, "sign": sign, "pre": float(score),
                    "score": float(bd["score"]), "head": bd["translit"][:64]})
    out.sort(key=lambda r: r["score"], reverse=True)
    return out


def sweep_pad(name, meta_pad, C):
    b = open(os.path.join(PADS, name), "rb").read()
    ks = L.build_keystreams(b)                     # 12 byte-builder variants
    pad_rec = {"pad": name, "bytes": len(b), "sha256": meta_pad["sha256"],
               "source": meta_pad["source"], "variants": {}, "n_offsets_scanned": 0}
    rows, nulls, best_pad = [], {}, None
    for vname, K in sorted(ks.items()):
        nk = int(len(K))
        if nk < 64:
            continue
        noff = max(0, nk - L.PREFILTER_LEN)
        for sign in (-1, +1):
            hits = L.dense_scan(K, C, sign=sign)
            res = escalate_head(hits, K, C, sign, L.HEAD)
            pad_rec["n_offsets_scanned"] += noff
            if not res:
                continue
            top = res[0]
            pad_rec["variants"][f"{vname}|sign{sign:+d}"] = {
                "ks_len": nk, "best_score": top["score"], "best_offset": top["offset"],
                "best_pre": top["pre"], "head_translit": top["head"]}
            r = dict(top); r["pad"] = name; r["variant"] = vname; r["ks_len"] = nk
            rows.append(r)
            if best_pad is None or top["score"] > best_pad["score"]:
                best_pad = r
    pad_rec["best"] = best_pad
    # nulls for every config reaching -5.5, plus the pad's best as reference
    need = [r for r in rows if r["score"] >= -5.5]
    if best_pad and best_pad not in need:
        need.append(best_pad)
    seen = set()
    for r in need:
        k = (r["pad"], r["variant"])
        if k in seen:
            continue
        seen.add(k)
        nm, nx = L.null_ceiling(ks[r["variant"]], seq_len=L.HEAD, n=200)
        nulls["|".join(k)] = {"null_mean": nm, "null_max": nx, "bar": L.hit_bar(nx),
                              "best": r["score"], "HIT": r["score"] >= L.hit_bar(nx)}
    return pad_rec, rows, nulls


def collect_and_write():
    man = json.load(open(MANIFEST))
    names = [p["name"] for p in man["pads"]]
    rows, per_pad, nulls, n_trials, missing = [], [], {}, 0, []
    for nm in names:
        ck = os.path.join(PARTIAL, nm + ".json")
        if not os.path.exists(ck):
            missing.append(nm); continue
        d = json.load(open(ck))
        per_pad.append(d["pad_rec"]); rows.extend(d["rows"]); nulls.update(d["nulls"])
        n_trials += d["pad_rec"]["n_offsets_scanned"]
    rows.sort(key=lambda r: r["score"], reverse=True)
    hits = [k for k, v in nulls.items() if v["HIT"]]
    best = rows[0] if rows else None
    fw = nullmod.threshold_for(n_trials) if n_trials else None
    out = {
        "lane": "round18/marsaglia",
        "hypothesis": "The LP2 keystream is a reading of the Marsaglia Random Number CDROM (1995).",
        "instrument": "analysis/round17/lib_padsweep.py",
        "control": {"status": "PASS (lib_padsweep.control on bits.01)",
                    "beam_recovered": "8/8", "dense_survival": SURVIVAL},
        "n_pads_swept": len(per_pad), "n_pads_total": len(names),
        "pads_not_yet_swept": missing,
        "n_offsets_scanned": n_trials,
        "n_offsets_effective_after_survival_discount": int(round(n_trials * SURVIVAL)),
        "prereg_bar": "score_norm >= -5.5 AND >= null_max + 0.5",
        "benchmark_null_threshold_for_n_trials": fw,
        "best_raw": best,
        "HITS": hits,
        "verdict": ("INCOMPLETE" if missing else
                    ("NEGATIVE (no configuration reached the bar)" if not hits else "HIT")),
        "nulls": nulls, "top20": rows[:20], "per_pad": per_pad,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    return out, missing


def main(budget):
    os.makedirs(PARTIAL, exist_ok=True)
    man = json.load(open(MANIFEST))
    C = L.nc.unsolved()
    L.trigram_model()
    # guard: refuse to run on the uniform fallback model
    T = L.trigram_model()
    if float(T.max() - T.min()) < 1.0:
        sys.exit("ABORT: trigram model is ~uniform. Run build_trigram_from_quadgrams.py first.")
    print(f"unsolved stream {len(C)} runes; budget {budget:.0f}s")
    t0 = time.time()
    for p in man["pads"]:
        name = p["name"]
        ck = os.path.join(PARTIAL, name + ".json")
        if os.path.exists(ck):
            continue
        if time.time() - t0 > budget:
            print(f"[budget reached; re-run to continue]"); break
        ts = time.time()
        pad_rec, rows, nulls = sweep_pad(name, p, C)
        json.dump({"pad_rec": pad_rec, "rows": rows, "nulls": nulls},
                  open(ck, "w"), indent=1)
        bp = pad_rec["best"]
        print(f"[{name}] {pad_rec['n_offsets_scanned']:,} offsets  "
              f"best {bp['score']:+.3f} ({bp['variant']} sign{bp['sign']:+d})  "
              f"{time.time()-ts:.0f}s", flush=True)
    out, missing = collect_and_write()
    print("=" * 70)
    print(f"swept {out['n_pads_swept']}/{out['n_pads_total']} pads  "
          f"offsets {out['n_offsets_scanned']:,}  best {out['best_raw']['score']:+.3f}"
          if out["best_raw"] else "no rows yet")
    print(f"HITS: {out['HITS'] or 'none'}   VERDICT: {out['verdict']}")
    if missing:
        print(f"remaining: {len(missing)} pads")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=3000.0)
    main(ap.parse_args().budget)
