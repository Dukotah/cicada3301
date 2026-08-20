"""Round 16 / lane P3 - ADDENDUM sweep, folding in two lane-P1 corrections.

1. `lib_padsweep.ks_hexchars` silently drops the digits 0-9 (`eng_to_idx` discards
   non-letters), so it is the **A-F subsequence** of a hex string, not the hex reading.
   P1 added `lib_padsweep.ks_nibbles` (each hex char as its value 0-15, in order),
   deliberately outside `BUILDERS`.  This addendum sweeps `nibbles` on every pad - it is
   the keystream a person actually gets by reading a blob as hex, and for a *binary* pad
   it is new coverage (the main sweep's hi_nibble/lo_nibble see the two nibble streams
   separately, never interleaved in order).

2. A1's `max_skip=3` is underpowered on pads with constant byte runs: repeated symbols
   make the anti-repeat filter burn skips without changing the key symbol.  P1 measured
   6/8 plant recovery at ms=3 versus 60/60 at ms=8.  `data/run_structure.json` shows this
   lane is squarely in that regime - `rand_digits` under hi_nibble is a run of 500,000
   identical symbols, the page JPEGs run to 25,348, and the armored-text pads repeat
   20-39% of the time - so every survivor here is re-escalated at **max_skip=8**, each
   against its own null measured at ms=8.

Everything else (dense scan over every offset, beam width, score scale, the -5.5 /
null_max+0.5 bar, per-pad checkpointing) is unchanged from `sweep.py`.

Run (resumable, one checkpoint per pad in data/partial_ms8/):
    python sweep_ms8.py [--only pad1,pad2] [--budget SECONDS]
    python sweep_ms8.py --budget 0        # collect only
"""
import os, sys, json, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import numpy as np                                            # noqa: E402
import lib_padsweep as L                                      # noqa: E402
import skipdecode as sk                                       # noqa: E402

# lib_padsweep prepends analysis/campaign18_skip to sys.path and THAT directory has its
# own sweep.py, so this lane's module must be loaded by explicit path.
_spec = importlib.util.spec_from_file_location("p3sweep", os.path.join(HERE, "sweep.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "benchmark")))
import null as nullmod                                        # noqa: E402

MS = 8                       # the corrected skip budget
PADS = os.path.join(HERE, "data", "pads")
MANIFEST = os.path.join(HERE, "pads_manifest.json")
PARTIAL = os.path.join(HERE, "data", "partial_ms8")
OUT = os.path.join(HERE, "results_ms8.json")
SURVIVAL = 0.625


def keystreams(b):
    """The main sweep's builder set with `hexchars` REPLACED by `nibbles`.

    `hexchars` is dropped here because P1 showed it is the A-F subsequence of the hex
    string rather than the hex reading, and `nibbles` is that same hypothesis done
    correctly.  The main sweep's `hexchars` numbers are retained in results.json for
    comparability with round12/A1; they are not re-run.
    """
    ks, meta = S.all_keystreams(b, drop={"hexchars"})
    ks["nibbles"] = L.ks_nibbles(b)
    ks["nibbles_rev"] = L.ks_nibbles(b[::-1])
    return ks, meta


def head_for(nk, ms=MS):
    cap = (nk - 8) // (ms + 1) - 1
    return int(max(24, min(L.HEAD, cap)))


def escalate_ms(hits, K, C, sign, head, ms=MS, top=40):
    Kl = [int(x) for x in K]
    out = []
    for score, o in hits[:top]:
        o = int(o)
        if o + head * (ms + 1) + 8 >= len(Kl):
            continue
        bd = sk.beam_decode([int(x) for x in C[:head]], Kl, sign=sign, o=o,
                            beam_w=L.BEAM_W, max_skip=ms)
        out.append({"offset": o, "sign": sign, "pre": float(score),
                    "score": float(bd["score"]), "head": bd["translit"][:64]})
    out.sort(key=lambda r: r["score"], reverse=True)
    return out


def null_ms(K, seq_len, ms=MS, n=200, seed0=3301):
    """A1's shuffle null, re-measured at this skip budget (a bigger skip budget gives the
    beam more freedom, so the null rises and the bar must be re-derived, not reused)."""
    import random
    Kl = [int(x) for x in K]
    base = L.nc.unsolved()[:seq_len]
    span = max(1, len(Kl) - seq_len * (ms + 1) - 8)
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(base); r.shuffle(s)
        vals.append(sk.beam_decode(s, Kl, sign=-1, o=(k * 37) % span,
                                   beam_w=L.BEAM_W, max_skip=ms)["score"])
    return float(np.mean(vals)), float(np.max(vals))


def main(only=None, budget=540.0):
    os.makedirs(PARTIAL, exist_ok=True)
    man = json.load(open(MANIFEST))
    pads = man["pads"] if not only else [p for p in man["pads"] if p["name"] in only]
    C = L.nc.unsolved()
    L.trigram_model()
    t0 = time.time()

    for p in pads:
        name = p["name"]
        ck = os.path.join(PARTIAL, name + ".json")
        if os.path.exists(ck):
            continue
        if time.time() - t0 > budget:
            print(f"[budget {budget:.0f}s reached - re-run to continue]", flush=True)
            break
        b = open(os.path.join(PADS, name + ".bin"), "rb").read()
        ks, meta = keystreams(b)
        rec = {"pad": name, "bytes": len(b), "sha256": p["sha256"],
               "source": p["source"], "keys_full_stream": p["keys_full_stream"],
               "max_skip": MS, "content": meta, "variants": {}, "n_offsets_scanned": 0}
        print(f"[{name}] {len(b):,} B  {len(ks)} variants  ms={MS}", flush=True)
        rows, best = [], None
        for vname, K in sorted(ks.items()):
            nk = int(len(K))
            if nk < 64:
                continue
            head = head_for(nk)
            noff = max(0, nk - L.PREFILTER_LEN)
            for sign in (-1, +1):
                hits = L.dense_scan(K, C, sign=sign)
                res = escalate_ms(hits, K, C, sign, head)
                rec["n_offsets_scanned"] += noff
                if not res:
                    continue
                top = res[0]
                rec["variants"][f"{vname}|sign{sign:+d}"] = {
                    "ks_len": nk, "head": head, "offsets": noff,
                    "best_score": top["score"], "best_offset": top["offset"],
                    "head_translit": top["head"]}
                r = dict(top); r.update(pad=name, variant=vname, ks_len=nk, head=head)
                rows.append(r)
                if best is None or top["score"] > best["score"]:
                    best = r
        rec["best"] = best
        nulls = {}
        need = [r for r in rows if r["score"] >= -5.5]
        if best and best not in need:
            need.append(best)
        seen = set()
        for r in need:
            k = (r["pad"], r["variant"], r["head"])
            if k in seen:
                continue
            seen.add(k)
            nm, nx = null_ms(ks[r["variant"]], seq_len=r["head"])
            nulls["|".join(map(str, k))] = {"null_mean": nm, "null_max": nx,
                                            "bar": L.hit_bar(nx), "best": r["score"],
                                            "HIT": r["score"] >= L.hit_bar(nx)}
            print(f"    null ms8 {r['variant']}(head={r['head']}): mean={nm:.3f} "
                  f"max={nx:.3f} bar={L.hit_bar(nx):.3f} best={r['score']:.3f}", flush=True)
        del ks
        json.dump({"pad_rec": rec, "rows": rows, "nulls": nulls}, open(ck, "w"), indent=1)
        if best:
            print(f"    best {best['score']:+.3f}  {best['variant']} "
                  f"sign{best['sign']:+d} off={best['offset']} head={best['head']} "
                  f"({rec['n_offsets_scanned']:,} offsets, {time.time()-t0:.0f}s)", flush=True)

    # ---- collect -------------------------------------------------------
    rows, per_pad, nulls, n_trials = [], [], {}, 0
    missing = []
    for q in man["pads"]:
        ck = os.path.join(PARTIAL, q["name"] + ".json")
        if not os.path.exists(ck):
            missing.append(q["name"]); continue
        d = json.load(open(ck))
        per_pad.append(d["pad_rec"]); rows.extend(d["rows"]); nulls.update(d["nulls"])
        n_trials += d["pad_rec"]["n_offsets_scanned"]
    rows.sort(key=lambda r: r["score"], reverse=True)
    hits = [k for k, v in nulls.items() if v["HIT"]]
    out = {"lane": "round16/P3_tables (ADDENDUM: max_skip=8 + corrected hex reading)",
           "corrections_folded_in": [
               "lib_padsweep.ks_hexchars drops digits 0-9; ks_nibbles added as a builder",
               "max_skip raised 3 -> 8 (P1: 6/8 vs 60/60 plant recovery on run-heavy pads)"],
           "max_skip": MS,
           "instrument": "analysis/round16/lib_padsweep.py",
           "control": {"status": "PASS (lib_padsweep.control, 2026-08-19)",
                       "beam_recovered": "8/8", "dense_survival": SURVIVAL,
                       "note": "control was measured at max_skip=3; P1 measured 60/60 at ms=8"},
           "n_pads": len(per_pad), "pads_not_yet_swept": missing,
           "n_offsets_scanned": n_trials,
           "n_offsets_effective_after_survival_discount": int(round(n_trials * SURVIVAL)),
           "prereg_bar": "score_norm >= -5.5 AND >= null_max + 0.5",
           "benchmark_null_threshold_for_n_trials": nullmod.threshold_for(max(2, n_trials)),
           "best_raw": rows[0] if rows else None, "HITS": hits,
           "verdict": ("INCOMPLETE" if missing else
                       ("NEGATIVE (no configuration reached the bar)" if not hits else "HIT")),
           "nulls": nulls, "top20": rows[:20], "per_pad": per_pad}
    json.dump(out, open(OUT, "w"), indent=1)
    print("\n" + "=" * 74)
    print(f"ms={MS}  pads {len(per_pad)}/{len(man['pads'])}  offsets {n_trials:,}")
    if missing:
        print(f"NOT YET SWEPT ({len(missing)}): {missing}")
    if rows:
        b = rows[0]
        print(f"best raw {b['score']:+.3f}  ({b['pad']} / {b['variant']} "
              f"sign{b['sign']:+d} off={b['offset']})")
    print(f"threshold_for({n_trials:,}) = {out['benchmark_null_threshold_for_n_trials']:+.3f}")
    print(f"HITS: {hits if hits else 'none'}   VERDICT: {out['verdict']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--budget", type=float, default=540.0)
    a = ap.parse_args()
    main(only=set(a.only.split(",")) if a.only else None, budget=a.budget)
