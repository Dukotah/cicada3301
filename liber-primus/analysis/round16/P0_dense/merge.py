"""Merge every P0 pass into the lane's single results.json and print the RESULTS.md tables.

Passes merged
  primary   ms=3 (A1's skip budget), 6 builders x fwd/rev x 2 signs, all pads
            -> results_small.json + results_big.json
  nibbles   ms=3, P1's `ks_nibbles` builder (true hex-text reading)
            -> results_all_nib.json
  ms8       max_skip=8 (P1's powered setting) re-escalation, own null at ms=8
            -> results_small_ms8.json + results_big_ms8.json
  controls  lib_padsweep.control() survival gate + control_skip.json (ms3 vs ms8 plants
            in the REAL pads) + per-pad constant-run statistics

    python merge.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R16 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, R16)
import numpy as np                                          # noqa: E402
import lib_padsweep as L                                    # noqa: E402
sys.path.insert(0, os.path.join(L.ROOT, "benchmark"))
import null as NULLMOD                                      # noqa: E402

PADDIR = os.path.join(L.ROOT, "analysis", "round12", "A1", "pads")
FILES = {"560.13": "DATA_560.13",
         "_560.00_auth": "DATA__560.00.iso-authoritative",
         "_560.00_trunc": "DATA__560.00",
         "560.17": "DATA_560.17",
         "prime_echo": "usr_local_bin_prime_echo",
         "tmp_folly": "tmp_folly", "tmp_wisdom": "tmp_wisdom"}


def load(*names):
    pads = []
    for fn in names:
        p = os.path.join(HERE, fn)
        if os.path.exists(p):
            d = json.load(open(p))
            if not d.get("partial"):
                pads.extend(d["pads"])
    return pads


def from_ckpt(ckdir, have):
    """Reconstruct pads whose sweep did not finish, from per-variant checkpoints, so a
    PARTIAL coverage bound is still reportable."""
    out, CK = [], os.path.join(HERE, ckdir)
    if not os.path.isdir(CK):
        return out
    part = {}
    for f in sorted(os.listdir(CK)):
        if not f.endswith(".json"):
            continue
        d = json.load(open(os.path.join(CK, f)))
        if d["pad"] in have:
            continue
        p = part.setdefault(d["pad"], {"rows": [], "nulls": {}, "off": 0, "cfg": 0,
                                       "beams": 0, "variants": []})
        p["rows"].extend(d["rows"])
        p["nulls"][d["variant"]] = d["null"]
        p["off"] += d["offsets"]; p["cfg"] += d["configs"]; p["beams"] += d["beams"]
        p["variants"].append(d["variant"])
    for lab, p in part.items():
        rows = sorted(p["rows"], key=lambda r: r["score"], reverse=True)
        hits = [r for r in rows if r["score"] >= -5.5 and r["score"] >= r["bar"]]
        out.append({"pad": lab, "file": FILES.get(lab, lab), "PARTIAL": True,
                    "bytes": os.path.getsize(os.path.join(PADDIR, FILES.get(lab, lab))),
                    "variants_completed": sorted(p["variants"]),
                    "coverage": {"configs": p["cfg"], "offsets_scanned": p["off"],
                                 "survival_rate": 0.625,
                                 "effective_offsets": int(round(p["off"] * 0.625)),
                                 "beam_escalations": p["beams"]},
                    "nulls": p["nulls"], "best": rows[0] if rows else None,
                    "n_hits": len(hits), "hits": hits, "top": rows[:20],
                    "verdict": "HIT" if hits else "NEGATIVE (partial coverage)"})
    return out


# ---- per-pad MEASURED prefilter survival ------------------------------------------------
# The round's flat 0.625 was measured by planting in a 1 MB blob. Retention inside a fixed
# keep window is a rank statistic, so it falls as the pad grows; a flat constant overstates
# effective coverage on a 118.8 MB pad. control_at_scale.py measures it per pad, under the
# criterion this lane actually uses (rank < 40, the top-40 that sweep.py escalates).
SURV = {}
_p = os.path.join(HERE, "control_at_scale.json")
if os.path.exists(_p):
    for x in json.load(open(_p))["pads"]:
        SURV[x["pad"]] = x
# borrowed rates, stated as borrowed: byte-identical / prefix pads of a measured one
BORROW = {"tmp_wisdom": "tmp_folly",          # byte-identical blob
          "_560.00_trunc": "_560.00_auth"}    # exact byte prefix, same order of magnitude


def surv_for(pad):
    src, borrowed = pad, False
    if pad not in SURV and pad in BORROW:
        src, borrowed = BORROW[pad], True
    if src in SURV:
        return SURV[src]["survival_rank_lt_40"], src, borrowed
    return 0.625, "round constant (1 MB plant) - NOT measured at this pad size", True


def summarise(pads, name):
    off = sum(p["coverage"]["offsets_scanned"] for p in pads)
    cfg = sum(p["coverage"]["configs"] for p in pads)
    bm = sum(p["coverage"]["beam_escalations"] for p in pads)
    eff = 0
    for p in pads:
        s, src, borrowed = surv_for(p["pad"])
        p["coverage"]["survival_measured"] = s
        p["coverage"]["survival_source"] = src + (" (borrowed)" if borrowed else "")
        p["coverage"]["effective_offsets"] = int(round(
            p["coverage"]["offsets_scanned"] * s))
        eff += p["coverage"]["effective_offsets"]
    rows = sorted((r for p in pads for r in p["top"]), key=lambda r: r["score"], reverse=True)
    hits = [r for p in pads for r in p["hits"]]
    return {
        "pass": name,
        "pads": [p["pad"] for p in pads],
        "coverage": {"configs": cfg, "offsets_scanned": off,
                     "survival": "per-pad MEASURED (control_at_scale.py), not the flat 0.625",
                     "effective_offsets": eff,
                     "effective_offsets_at_flat_0625": int(round(off * 0.625)),
                     "beam_escalations": bm},
        "best": rows[0] if rows else None,
        "n_hits": len(hits), "hits": hits, "top20": rows[:20],
        "threshold_for_offsets": NULLMOD.threshold_for(max(2, off)),
        "threshold_for_beams": NULLMOD.threshold_for(max(2, bm)),
        "verdict": "HIT" if hits else "NEGATIVE",
        "pad_detail": pads,
    }


prim = load("results_small.json", "results_big.json")
prim += from_ckpt("ckpt", {p["pad"] for p in prim})
nib = load("results_all_nib.json")
nib += from_ckpt("ckpt_nib", {p["pad"] for p in nib})
ms8 = load("results_small_ms8.json", "results_big_ms8.json")
ms8 += from_ckpt("ckpt_ms8", {p["pad"] for p in ms8})

P = summarise(prim, "primary ms=3, builders=6 x fwd/rev x 2 signs")
NB = summarise(nib, "nibbles builder, ms=3") if nib else None
M8 = summarise(ms8, "max_skip=8 re-escalation, null at ms=8") if ms8 else None

# --- does ms=8 change anything? compare per (pad,variant,sign,offset) ------------------
ms8_cmp = None
if ms8:
    a = {(r["pad"], r["variant"], r["sign"], r["offset"]): r["score"]
         for p in prim for r in p["top"]}
    b = {(r["pad"], r["variant"], r["sign"], r["offset"]): r["score"]
         for p in ms8 for r in p["top"]}
    common = sorted(set(a) & set(b))
    diffs = [b[k] - a[k] for k in common]
    ms8_cmp = {"compared_rows": len(common),
               "identical": int(sum(1 for d in diffs if d == 0.0)),
               "max_abs_delta": float(max((abs(d) for d in diffs), default=0.0)),
               "reading": ("The beam only admits a skip when every skipped key position "
                           "would have reproduced the previous cipher rune (p ~ 1/29 each). "
                           "On a high-entropy pad that validity test, not the budget, is "
                           "binding, so raising max_skip 3 -> 8 changes nothing. On a pad "
                           "with constant byte runs (lane P1's, 18.4% zeros) the same test "
                           "is trivially satisfiable many times in a row, which is why the "
                           "budget bites there and not here.")}

ctl_skip = None
p = os.path.join(HERE, "control_skip.json")
if os.path.exists(p):
    d = json.load(open(p))
    ctl_skip = {"design": d["note"], "supp": d.get("supp"),
                "pads": [{"pad": x["pad"], "trials": x["trials"],
                          "zero_frac": x["pad_stats"]["zero_frac"],
                          "adj_equal_frac": x["pad_stats"]["adj_equal_frac"],
                          "max_const_run": x["pad_stats"]["max_const_run"],
                          "frac_bytes_in_runs_ge8": x["pad_stats"]["frac_bytes_in_runs_ge8"],
                          "recovered_ms3": x.get("recovered_ms3"),
                          "recovered_ms8": x.get("recovered_ms8"),
                          "max_consecutive_skip_observed":
                              max(r["max_consecutive_skip"] for r in x["rows"])}
                         for x in d["pads"]]}

out = {
    "lane": "round16/P0_dense",
    "verdict": "HIT" if (P["n_hits"] or (NB and NB["n_hits"]) or (M8 and M8["n_hits"]))
               else "NEGATIVE",
    "hypothesis": ("Round 12 front A1 swept these same CicadaOS pads on an 8-offset ladder "
                   "per keystream variant and returned NEGATIVE. On the 118,818,811-byte "
                   "DATA/560.13 that is 6.7e-8 of the offset space. A1's verdict is sound "
                   "for those eight offsets and is not a bound on the pad. Re-sweep with "
                   "dense_scan, which scores EVERY offset."),
    "instrument": ("round16/lib_padsweep.py dense_scan (rigid rune-index trigram prefilter, "
                   "24-rune head window, keep=400) -> beam escalation of the top 40 "
                   "survivors per sign with A1's settings (beam_w=120, max_skip=3, "
                   "head=400) on A1's score_norm scale, vs A1's shuffle null (n=200)."),
    "hit_bar_rule": "score_norm >= -5.5 AND score_norm >= null_max + 0.5 (pre-registered)",
    "controls": {
        "survival_gate": {
            "source": "lib_padsweep.control(), re-run on this box 2026-08-19",
            "PASS": True, "n_trials": 8, "beam_recovered": 8, "dense_found": 5,
            "survival_rate_round_constant": 0.625,
            "note": "reproduces PREREG.md exactly: the beam recovers 8/8 planted pads at "
                    "100% of runes (-4.212); the dense prefilter retains the true offset in "
                    "5/8. 0.625 is the coverage discount, and it is a POWER limit, not a "
                    "soundness limit.",
            "SUPERSEDED_BY": "controls.survival_measured_per_pad",
            "caveat": "0.625 was measured against 1e6 competing offsets and is NOT used for "
                      "this lane's coverage numbers. Retention inside a fixed keep window is "
                      "a rank statistic and falls with pad size; measured per pad below.",
        },
        "survival_measured_per_pad": {
            "source": "control_at_scale.py, 24 plants per pad in the REAL pad",
            "criterion": "rank_lt_40 is operative (sweep.py escalates the top 40 per sign); "
                         "rank_lt_400 is reported for comparability with the round constant "
                         "and with lane P2",
            "finding": "survival falls steeply with pad size, well below the round's flat "
                       "0.625 for every pad above ~1 MB. Beam recovery stays at 24/24 "
                       "throughout, so this is a POWER limit, not a soundness limit.",
            "pads": [{k: v for k, v in x.items() if k != "rows"} for x in
                     sorted(SURV.values(), key=lambda z: z["pad_bytes"])],
        },
        "skip_budget": ctl_skip,
        "window_equivalence": ("sweep.py::_assert_window_equiv asserts the windowed beam and "
                               "null wrappers are bit-identical to lib_padsweep.escalate and "
                               "lib_padsweep.null_ceiling; it runs at the start of every "
                               "sweep."),
        "null_reproduces_A1": ("this lane's mod29 shuffle null reproduces A1's published "
                               "null_max exactly: -6.995 on _560.00 authoritative "
                               "(A1: -6.995405944815296) and -7.037 on 560.13 "
                               "(A1: -7.036791950110792)."),
    },
    "passes": {"primary_ms3": P, "nibbles_ms3": NB, "max_skip_8": M8},
    "ms8_vs_ms3": ms8_cmp,
    "extreme_value_check": {
        "note": "AGENTS.md lesson 3 - a fixed bar is invalid at large N.",
        "threshold_for_offsets_scanned": P["threshold_for_offsets"],
        "threshold_for_beam_escalations": P["threshold_for_beams"],
        "raw_best": P["best"]["score"] if P["best"] else None,
        "reading": ("threshold_for() returns the -5.5 floor at both trial counts: with "
                    "mu=-7.2517, beta=0.0725 the family-wise bar only clears -5.5 above "
                    "~1e11 trials. The floor binds here, and the raw best misses it by "
                    ">1.2 either way."),
    },
    "duplicate_pads": {
        "tmp_folly == tmp_wisdom": "byte-identical (sha256 7e5ec097...); 7 pad files, "
                                   "6 distinct blobs",
        "_560.00_trunc subset of _560.00_auth": "the mirror copy is an exact byte prefix of "
                                                "the ISO copy, so its rows duplicate the "
                                                "auth rows at the same offsets",
    },
}
json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=2)


def table(rows, n=20):
    print("| # | pad | variant | sign | offset | pre | score_norm | bar | head (48 runes) |")
    print("|---:|---|---|---:|---:|---:|---:|---:|---|")
    for i, r in enumerate(rows[:n], 1):
        print("| %d | `%s` | `%s` | %+d | %s | %.3f | **%.4f** | %.2f | `%s` |"
              % (i, r["pad"], r["variant"], r["sign"], format(r["offset"], ","),
                 r["pre"], r["score"], r["bar"], r["head"][:48]))


print("### TOP 20 (primary ms=3 pass)\n")
table(P["top20"])
print("\n### per-pad coverage (primary ms=3)\n")
print("| pad file | bytes | configs | offsets scanned | measured survival | effective | best | verdict |")
print("|---|---:|---:|---:|---:|---:|---:|---|")
for p in sorted(P["pad_detail"], key=lambda x: -x["bytes"]):
    print("| `%s` | %s | %d%s | %s | %.3f%s | %s | %.4f | %s |"
          % (p["file"], format(p["bytes"], ","), p["coverage"]["configs"],
             " (PARTIAL)" if p.get("PARTIAL") else "",
             format(p["coverage"]["offsets_scanned"], ","),
             p["coverage"]["survival_measured"],
             "*" if "borrowed" in p["coverage"]["survival_source"] else "",
             format(p["coverage"]["effective_offsets"], ","),
             p["best"]["score"], p["verdict"]))
for nm, S in (("nibbles ms=3", NB), ("max_skip=8", M8)):
    if S:
        print("\n%s: %d configs, %s offsets, best %.4f, verdict %s"
              % (nm, S["coverage"]["configs"],
                 format(S["coverage"]["offsets_scanned"], ","),
                 S["best"]["score"], S["verdict"]))
if ms8_cmp:
    print("ms8 vs ms3: %d rows compared, %d identical, max |delta| %.6f"
          % (ms8_cmp["compared_rows"], ms8_cmp["identical"], ms8_cmp["max_abs_delta"]))
print("\nTOTAL primary: %d configs, %s offsets = %s effective, %s beams"
      % (P["coverage"]["configs"], format(P["coverage"]["offsets_scanned"], ","),
         format(P["coverage"]["effective_offsets"], ","),
         format(P["coverage"]["beam_escalations"], ",")))
print("VERDICT:", out["verdict"])
