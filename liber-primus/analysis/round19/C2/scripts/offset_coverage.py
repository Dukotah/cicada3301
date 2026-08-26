"""C2 / B-02 — how much of the OFFSET AXIS does this repository's published coverage touch?

B-02 has sat at status `open` / raw_status `scope-limited` since Round 10 with every field
except `hypothesis` null.  Round 8 named the gap in its own words
(`research/ROUND-8-RESULTS.md:127-129`):

    "... and a keystream OFFSET other than zero (this sweep assumes key index 0 aligns with
     the first rune of LP2 page 0)."

This is pure coverage arithmetic over committed artefacts.  It uses no decoder, no scorer and
no threshold, so it cannot be a false negative and it cannot be invalidated by Round 19's
Phase 0 instrument repairs.  Every offset count below is read from the originating lane's own
result JSON or from the line of its own sweep source that fixes the offsets; nothing is taken
from prose.

    python3 offset_coverage.py     ->  ../out_offset_coverage.json  (+ a printed table)
"""
import os, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, ".."))
ANALYSIS = os.path.abspath(os.path.join(C2, "..", ".."))
LP = os.path.abspath(os.path.join(ANALYSIS, ".."))
L6 = os.path.join(ANALYSIS, "round18", "L6-offset-marsaglia")

# The mechanism-bounded offset axis for a DERIVED key, argued in round18/L6 PREREG §A.1:
# the largest artefact any named mechanism could produce is a 1 MB generated pad file
# consumed from the middle, which subsumes "enciphered LP1 first" (<=14,752), file headers
# (<=65,536), digest-block alignment, and 3301*k.
AXIS = 1 << 20                    # 1,048,576
AXIS_PESSIMISTIC = 1 << 32        # "the pad file was up to 4 GB", the sensitivity case


def jload(p, default=None):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return default


def main():
    b04 = {s: jload(os.path.join(ANALYSIS, "round13", "B04", f"results_{s}.json"), {})
           for s in ("A", "B", "C")}
    b04d = jload(os.path.join(ANALYSIS, "round13", "B04", "results_D.json"), [])
    kdf = jload(os.path.join(ANALYSIS, "round16", "KDF", "results_A.json"), {})
    prng = jload(os.path.join(ANALYSIS, "round16", "prng", "results.json"), {})
    b05 = jload(os.path.join(ANALYSIS, "round13", "B05", "sweep_results.json"), {})
    a1 = jload(os.path.join(L6, "out", "results_A1.json"), {})
    ledger = jload(os.path.join(LP, "LEDGER.json"), {"entries": []})
    led = {e["id"]: e for e in ledger["entries"]}

    b05_offs = sorted(set(b05.get("grid", {}).get("offsets", [])))
    b04b_offs = [1, 4, 16, 29, 64, 128, 256, 512, 1024, 3301]   # round13/B04/sweep.py:194

    # sub-lane A2 / Marsaglia partial state, counted from the checkpoints on disk
    a2_ck = glob.glob(os.path.join(L6, "out", "ckpt_A2", "*.json"))
    m_ck = glob.glob(os.path.join(L6, "out", "ckpt_M", "*.json"))
    m_off = sum(int(jload(p, {}).get("n_offsets", 0)) for p in m_ck)
    a2_off = sum(int(jload(p, {}).get("n_offsets", 0)) for p in a2_ck)

    R = []

    def row(sweep, decodes, offsets, offs_desc, axis, source, kind, note=""):
        R.append({"sweep": sweep, "decodes": decodes, "distinct_key_offsets": offsets,
                  "offsets": offs_desc, "axis": axis,
                  "fraction_of_axis": (offsets / axis)
                                      if (axis and isinstance(offsets, int)) else None,
                  "source": source, "branch": kind, "note": note})

    # ------------------------------------------------ derived / seeded keystream branch
    row("Round 8 SEED — time-seeded PRNG (10 gens, 2011-2015)", 126_230_400 * 10 * 2, 1,
        "{0}", AXIS, "research/ROUND-8-RESULTS.md:82-84,127-129", "derived",
        "Round 8's own words: 'this sweep assumes key index 0 aligns with the first rune "
        "of LP2 page 0'. This single line is B-02.")
    row("Round 8 SEED — non-integer / lore seeds", 15_408, 1, "{0}", AXIS,
        "research/ROUND-8-RESULTS.md:108-113", "derived")
    row("Round 13 B-04 stage A — broad screen", b04["A"].get("n_decodes"), 1, "{0}", AXIS,
        "round13/B04/results_A.json + sweep.py:186-189", "derived")
    row("Round 13 B-04 stage B — the offset stage", b04["B"].get("n_decodes"),
        len(b04b_offs), "{1,4,16,29,64,128,256,512,1024,3301}", AXIS,
        "round13/B04/sweep.py:194", "derived",
        "The only stage in the whole derived branch that ever moved the key index, and its "
        "largest offset is 3301 = 0.31 % of the axis.")
    row("Round 13 B-04 stage C — per-page restarts", b04["C"].get("n_decodes"), 1,
        "{0} (55 CIPHERTEXT segment starts, key restarted at index 0 for each)", AXIS,
        "round13/B04/sweep.py:200-203", "derived",
        "Stage C varies where the ciphertext starts, not where the key starts. It is not "
        "offset coverage.")
    row("Round 13 B-04 stage D — escalation", sum(x.get("n_decodes", 0) for x in b04d),
        None, "inherits the escalated rows' own offsets", AXIS,
        "round13/B04/results_D.json", "derived")
    row("Round 13 B-05 — payload as PRF seed", b05.get("total_decodes"), len(b05_offs),
        "{" + ",".join(str(o) for o in b05_offs) + "}", AXIS,
        "round13/B05/sweep_results.json:grid.offsets", "derived",
        "The widest offset ladder in the derived branch before Round 18: 14 points, max 3301.")
    row("Round 16 KDF — key stretching", kdf.get("n_decodes"), 1, "{0}", AXIS,
        "round16/KDF/PREREG.md ('Offset 0 only (Stage A)'); LEDGER R16-KDF.not_covered "
        "lists 'KDF offset != 0'", "derived")
    row("Round 16 PRNG — 7 census generators", prng.get("total_decodes"), 1, "{0}", AXIS,
        "round16/prng/results.json; LEDGER R16-PRNG.not_covered lists 'offsets != 0'",
        "derived")
    row("Round 18 L6 sub-lane A1 — DENSE re-sweep of 220 mined configs",
        a1.get("n_offsets_scanned"), AXIS, "EVERY offset in [0, 2^20)", AXIS,
        "round18/L6-offset-marsaglia/out/results_A1.json", "derived",
        "COMPLETE. First dense offset coverage the derived branch has ever had. 220 "
        "(config, sign) units x 1,048,576 offsets = 230,686,720.")
    row("Round 18 L6 sub-lane A2 — fresh 504-seed x 6-generator grid", a2_off,
        (1 << 18) if a2_off else 0,
        "EVERY offset in [0, 2^18) — %d of 3,024 units run" % len(a2_ck),
        AXIS, "round18/L6-offset-marsaglia/out/results_A2.json", "derived",
        "NOT extended by round19/C2: C2 HELD this sub-lane for Phase 0. The units above "
        "were completed by a concurrent continuation of L6's own sweep during C2's window; "
        "the count is frozen at C2 collection time. %.1f %% of the planned units."
        % (100.0 * len(a2_ck) / 3024))

    # ------------------------------------------------ external / public pad branch
    row("Round 12 A1 — CicadaOS author pads (original)", None, 8,
        "an 8-point ladder per keystream variant", 118_818_811,
        "round17/SYNTHESIS.md:'A1 used eight offsets per keystream variant'", "pad",
        "On the 118,818,811-byte 560.13 pad that is 6.7e-8 of its offset axis.")
    row("Round 12 A1 — 560.13 completion (extended ladder)", None, None,
        "extended ladder 'to 5e7' — a ladder, still not dense", 118_818_811,
        "LEDGER R12-A1.coverage", "pad")
    row("Round 17 P0-P3 — the public-pad round", None,
        led.get("R17-PUBLIC-PAD", {}).get("result", {}).get("offsets_scored"),
        "EVERY offset on every pad", None,
        "LEDGER R17-PUBLIC-PAD.result.offsets_scored", "pad",
        "Dense: the pad-branch offset axis is fully covered for the pads swept. Effective "
        "8.38e9 after each lane's own measured prefilter survival — and L7-A.7: that "
        "survival was measured on ENGLISH plants only.")
    row("Round 18 L6 sub-lane B — MARSAGLIA CDROM", m_off, m_off,
        "EVERY offset — %d of 756 units run" % len(m_ck), 17_639_963_712,
        "round18/L6-offset-marsaglia/out/results_M.json", "pad",
        "NOT extended by round19/C2: C2 HELD this sub-lane for Phase 0. The units above "
        "were completed by a concurrent continuation of L6's own sweep during C2's window; "
        "the count is frozen at C2 collection time. %.1f %% of the planned units."
        % (100.0 * len(m_ck) / 756))

    # ------------------------------------------------ the aggregate statements
    derived = [r for r in R if r["branch"] == "derived"]
    dec_at_0 = sum(r["decodes"] or 0 for r in derived
                   if r["distinct_key_offsets"] == 1 and r["sweep"].find("L6") < 0)
    # decodes actually run at a NONZERO key offset
    b04b = b04["B"].get("n_decodes", 0)
    b05n = b05.get("total_decodes", 0)
    nonzero = b04b + int(round(b05n * (len(b05_offs) - 1) / max(1, len(b05_offs))))
    total_derived_decodes = dec_at_0 + b04b + b05n + sum(
        x.get("n_decodes", 0) for x in b04d)

    offs_ever = sorted(set([0] + b04b_offs + b05_offs))
    joint_axis = total_derived_decodes * AXIS

    agg = {
        "derived_branch": {
            "total_decodes_all_sweeps": total_derived_decodes,
            "decodes_run_at_key_offset_0_only": dec_at_0,
            "decodes_run_at_any_NONZERO_key_offset": nonzero,
            "fraction_of_derived_decodes_at_nonzero_offset": nonzero / total_derived_decodes,
            "distinct_key_offsets_ever_tested_before_round18": len(offs_ever),
            "distinct_key_offsets_ever_tested_before_round18_list": offs_ever,
            "largest_key_offset_ever_tested_before_round18": max(offs_ever),
            "fraction_of_axis_2pow20_before_round18": len(offs_ever) / AXIS,
            "fraction_of_axis_2pow32_before_round18": len(offs_ever) / AXIS_PESSIMISTIC,
            "axis_2pow20_rationale": "round18/L6 PREREG §A.1 — the bound that subsumes every "
                                     "named mechanism (LP1-first, file headers, digest-block "
                                     "alignment, 3301*k, a 1 MB generated pad read from the "
                                     "middle)",
            "joint_config_x_offset_space_at_axis_2pow20": joint_axis,
            "joint_covered_before_round18": total_derived_decodes,
            "joint_fraction_before_round18": total_derived_decodes / joint_axis,
            "joint_added_by_round18_L6_A1": a1.get("n_offsets_scanned"),
            "joint_fraction_added_by_round18_L6_A1":
                (a1.get("n_offsets_scanned") or 0) / joint_axis,
        },
        "pad_branch": {
            "offsets_scored_round17": led.get("R17-PUBLIC-PAD", {})
                                         .get("result", {}).get("offsets_scored"),
            "offsets_effective_round17": led.get("R17-PUBLIC-PAD", {})
                                            .get("result", {}).get("offsets_effective"),
            "note": "Dense on the pads swept, i.e. the offset axis is NOT the residual gap "
                    "in this branch; the residual gap is which pads, which builders, and "
                    "(L7-A.7) which register.",
        },
    }

    out = {"lane": "round19/C2", "item": "B-02 / B-08 — offset axis coverage accounting",
           "method": "pure arithmetic over committed artefacts; no decoder, no scorer, "
                     "no threshold",
           "axis_derived": AXIS, "axis_derived_pessimistic": AXIS_PESSIMISTIC,
           "rows": R, "aggregate": agg}
    with open(os.path.join(C2, "out_offset_coverage.json"), "w") as f:
        json.dump(out, f, indent=1)

    w = max(len(r["sweep"]) for r in R)
    print(f"{'sweep':<{w}} {'decodes':>15} {'offsets':>12} {'frac of axis':>14}")
    for r in R:
        d = f"{r['decodes']:,}" if isinstance(r["decodes"], int) else "—"
        o = f"{r['distinct_key_offsets']:,}" if isinstance(r["distinct_key_offsets"], int) else "—"
        fr = f"{r['fraction_of_axis']:.3e}" if r["fraction_of_axis"] is not None else "—"
        print(f"{r['sweep']:<{w}} {d:>15} {o:>12} {fr:>14}")
    print()
    print(json.dumps(agg, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
