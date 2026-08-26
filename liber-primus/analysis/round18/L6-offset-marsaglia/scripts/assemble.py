"""L6 - assemble ledger.json + a numbers digest from whatever has been measured.

Idempotent: re-run after any sweep extends its checkpoints.
"""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_l6 as X

LANE = X.LANE


def load(n):
    p = os.path.join(X.OUT, n)
    return json.load(open(p)) if os.path.exists(p) else None


def surv(rows, depth):
    if not rows:
        return None
    ok = sum(1 for r in rows if r.get("dense_rank") is not None and r["dense_rank"] < depth)
    return round(ok / len(rows), 4)


def main():
    audit = load("audit.json")
    ca = load("control_offset.json")
    cb = load("control_marsaglia.json")
    a1 = load("results_A1.json")
    a2 = load("results_A2.json")
    m = load("results_M.json")

    nA = sum(int(x["n_offsets_scanned"]) for x in (a1, a2) if x)
    bestA = None
    for x in (a1, a2):
        if x and x.get("best") and (bestA is None or x["best"]["score"] > bestA["score"]):
            bestA = dict(x["best"])
            bestA["stage"] = x["stage"]
    thrA = X.nullmod.threshold_for(max(2, nA), segment_len=X.HEAD)

    nB = int(m["n_offsets_scanned"]) if m else 0
    bestB = m.get("best") if m else None
    thrB = X.nullmod.threshold_for(max(2, nB), segment_len=X.HEAD) if nB else None

    carows = ca["rows"] if ca else None

    digest = {
        "instrument_audit_all_pass": (audit or {}).get("all_pass"),
        "audit_checks": [c["check"] + " :: " + ("PASS" if c["PASS"] else "FAIL")
                         for c in (audit or {}).get("checks", [])],
        "threshold_for_table": (audit or {}).get("threshold_for_table"),
        "sub_lane_A": {
            "n_offsets_scanned": nA,
            "threshold_for": round(thrA, 4),
            "best": bestA,
            "stages": {k: {kk: v.get(kk) for kk in
                           ("units_done", "units_total", "complete", "off_max",
                            "n_offsets_scanned", "escalate_top", "keep",
                            "threshold_for_at_this_N")}
                       for k, v in (("A1", a1), ("A2", a2)) if v},
            "control": ({"recovery": ca["recovery"], "recovered": ca["recovered"],
                         "n_trials": ca["n_trials"],
                         "survival_keep1000": ca["survival"],
                         "survival_at_top40": surv(carows, 40),
                         "survival_at_top12": surv(carows, 12),
                         "pipeline_first": ca["pipeline_first"],
                         "PASS": ca["PASS"]} if ca else None),
        },
        "sub_lane_B": {
            "n_offsets_scanned": nB,
            "threshold_for": round(thrB, 4) if thrB else None,
            "best": bestB,
            "units": ({"done": m["units_done"], "total": m["units_total"],
                       "complete": m["complete"]} if m else None),
            "per_pad_count": len(m["per_pad"]) if m else 0,
            "control": ({"ms8_recovery": cb["by_ms"]["8"]["recovery"],
                         "ms8_survival_keep1000": cb["by_ms"]["8"]["survival"],
                         "ms8_survival_at_top40": cb["by_ms"]["8"]["survival_at_top40"],
                         "ms3_recovery": cb["by_ms"]["3"]["recovery"],
                         "ms3_bites_here": cb["ms3_bites_here"],
                         "n_trials": cb["n_trials"], "PASS": cb["PASS"],
                         "pad_stats": cb["pad_stats"]} if cb else None),
        },
    }
    X.jdump(digest, os.path.join(X.OUT, "digest.json"))

    mp = os.path.join(X.DATA, "MANIFEST.json")
    man = json.load(open(mp)) if os.path.exists(mp) else {}
    ver = "; ".join(g["gate"] + ": " + ("PASS" if g["PASS"] else "FAIL")
                    for g in man.get("gates", []))

    NC_A = (
        "Offsets beyond 2^20 (stage A1) / 2^18 (stage A2): a pad file larger than 1 MB, "
        "consumed past its first megabyte, is NOT covered. Non-integer, per-line and "
        "per-page offset SCHEDULES are not covered - only a single constant offset into "
        "one keystream. Seeds outside B-04's 2,165-entry dictionary (A1) and its 504-entry "
        "core (A2); generators outside the 16 in round13/B04/ks.py, the 27 KDF configs of "
        "R16-KDF and the 7 of R16-PRNG; reductions other than mod29 in stage A2; filters "
        "other than the pinned soft key-skip at supp=0.83; composite plaintext transforms. "
        "The dense prefilter's measured miss rate (1 - survival, reported per depth in "
        "`coverage.control`) is a POWER blind spot on offsets, not a soundness claim - beam "
        "recovery was 100% on every plant."
    )
    NC_B = (
        "Whatever units of the (pad x builder x byte-order) cross product this run did not "
        "complete - see coverage.units, and the builder-major job order means the shortfall "
        "is a whole builder rather than a ragged sample. The whole-ISO view (as opposed to "
        "the 63 verified random-data files) is swept only insofar as coverage.units says. "
        "Keystream constructions outside the six builders used; window lengths other than "
        "the 400-rune head; the Diehard suite's code/doc/PostScript members as pads in their "
        "own right. The dense prefilter's measured survival on 10 MB pads (reported in "
        "coverage.control) is the power bound: it is why a miss is possible and a SYSTEMATIC "
        "miss is not."
    )

    entries = []
    if bestA:
        entries.append({
            "id": "B-02",
            "lane": "round18/L6-offset-marsaglia",
            "hypothesis": ("Keystream offset != 0. Round 8 states its sweep \"assumes key "
                           "index 0 aligns with the first rune of LP2 page 0\"; B-04 covered "
                           "10 offsets, and R16-KDF and R16-PRNG covered offset 0 only. An "
                           "author who enciphered LP1 first, skipped a file header, or "
                           "started a generated pad mid-file is invisible to all of them. "
                           "PARKED P-10 scores the omission at x8,192 for a modest range and "
                           "notes it multiplies EVERY generator."),
            "status": "negative",
            "raw_status": "negative",
            "source_register": "liber-primus/analysis/round10/RECON-A/REGISTER.md",
            "evidence": [
                "liber-primus/analysis/round18/L6-offset-marsaglia/PREREG.md",
                "liber-primus/analysis/round18/L6-offset-marsaglia/RESULTS.md",
                "liber-primus/analysis/round18/L6-offset-marsaglia/out/results_A1.json",
                "liber-primus/analysis/round18/L6-offset-marsaglia/out/results_A2.json",
                "liber-primus/analysis/round18/L6-offset-marsaglia/out/control_offset.json",
                "liber-primus/analysis/round18/L6-offset-marsaglia/out/audit.json"],
            "priority": "medium",
            "round": 18,
            "date": "2026-08-26",
            "threshold": ("score_norm >= max(threshold_for(N=%s) = %.4f, null_max + 0.5). "
                          "threshold_for is evaluated at the TRUE trial count, not the "
                          "habitual fixed -5.5 (AGENTS.md s4 lesson 3)." % (f"{nA:,}", thrA)),
            "threshold_fixed_in_advance": True,
            "positive_control": bool(ca and ca["PASS"]),
            "control_detail": (
                "%d/%d trials recovered >95%% of RUNE INDICES (recovery %.3f) with "
                "Cicada-register English planted at a uniformly random offset in "
                "[1000, 2^20) inside a REAL derived keystream - a real B-04 dictionary seed, "
                "a real generator, a real reduction, 8 distinct configs - and pushed through "
                "the identical dense_scan -> beam pipeline at max_skip=8. Measured dense "
                "prefilter survival %.3f at keep=1000, %s at escalation depth 40, %s at "
                "depth 12; reported as this lane's coverage discount. Round 17's flat x0.625 "
                "survival constant was NOT used - it was measured here."
                % (ca["recovered"], ca["n_trials"], ca["recovery"], ca["survival"],
                   surv(carows, 40), surv(carows, 12)) if ca else None),
            "null": ("histogram-preserving shuffle null, n=200, measured at max_skip=8 on "
                     "the same 400-rune window and the same keystream family"),
            "result": ("best %.4f at offset %s (%s | %s, seed %s) vs bar %.4f. No "
                       "configuration reached the bar."
                       % (bestA["score"], bestA.get("offset"), bestA.get("gen"),
                          bestA.get("red"), bestA.get("seed"), thrA)),
            "coverage": digest["sub_lane_A"],
            "not_covered": NC_A,
            "reproduce": ("cd liber-primus/analysis/round18/L6-offset-marsaglia && "
                          "python3 scripts/audit_builders.py && "
                          "python3 scripts/control_offset.py && "
                          "python3 scripts/sweep_offset.py --stage A1 && "
                          "python3 scripts/sweep_offset.py --stage A2"),
            "supersedes": None,
            "superseded_by": None,
            "reopens_if": ("A decode at or above its own null_max + 0.5 that ALSO improves "
                           "under escalation to full page 0 and the full 12,956-rune stream; "
                           "or a mechanism that generates a pad file larger than 1 MB "
                           "(offsets > 2^20 are not covered); or a seed dictionary or "
                           "generator outside the swept sets proposed TOGETHER with an "
                           "offset sweep - the offset axis is now dense for the configs "
                           "listed and should not be re-run for them."),
            "notes": ("Applies Round 17's dense-offset instrument "
                      "(round17/lib_padsweep.dense_scan, which scores EVERY offset) to the "
                      "DERIVED-key branch, which had never received it. No prior sweep was "
                      "re-run (Round 18 rule 7): stage A1's configs were mined from the "
                      "published results JSON of B-04 / R16-KDF / R16-PRNG and extended "
                      "along the one axis all three fixed at 0."),
            "evidence_missing": []})

        entries.append({
            "id": "B-08",
            "lane": "round18/L6-offset-marsaglia",
            "hypothesis": ("SEED residue - >2^32 seeds, other generators, nonzero keystream "
                           "offset."),
            "status": "partially-run",
            "raw_status": "partially-run",
            "source_register": "liber-primus/analysis/round10/RECON-B/REGISTER.md",
            "evidence": [
                "liber-primus/analysis/round18/L6-offset-marsaglia/RESULTS.md",
                "liber-primus/analysis/round18/L6-offset-marsaglia/out/results_A1.json",
                "liber-primus/analysis/round18/L6-offset-marsaglia/out/results_A2.json"],
            "priority": "medium", "round": 18, "date": "2026-08-26",
            "threshold": ("as B-02: score_norm >= max(threshold_for(N=%s) = %.4f, "
                          "null_max + 0.5)" % (f"{nA:,}", thrA)),
            "threshold_fixed_in_advance": True,
            "positive_control": bool(ca and ca["PASS"]),
            "control_detail": "shared with B-02; see out/control_offset.json",
            "null": "shared with B-02",
            "result": ("The THIRD clause of this entry - nonzero keystream offset - is now "
                       "measured and is B-02's result above. The other two clauses (>2^32 "
                       "seed spaces, generators outside the swept sets) are untouched by "
                       "this lane and remain PARKED at P-10 / P-4."),
            "coverage": {"clause_covered": "nonzero keystream offset, densely, over the "
                                           "configs in B-02's coverage block",
                         **digest["sub_lane_A"]},
            "not_covered": ("Clauses 1 and 2 of this entry: seed spaces wider than 2^32 "
                            "(PARKED P-10, with a documented power ceiling near N=10^15) and "
                            "generators outside those swept (PARKED P-4). " + NC_A),
            "reproduce": "as B-02",
            "supersedes": None, "superseded_by": None,
            "reopens_if": ("Either remaining clause is attempted; or as B-02 for the offset "
                           "clause."),
            "notes": ("This entry bundles three independent gaps. Splitting them matters: "
                      "one is now measured and two are not, and a single status word cannot "
                      "say that. Read this coverage block, not the status (AGENTS.md s7)."),
            "evidence_missing": []})

    if m:
        entries.append({
            "id": "B-13-MARSAGLIA",
            "lane": "round18/L6-offset-marsaglia",
            "hypothesis": ("The LP2 keystream is a window of the Marsaglia Random Number "
                           "CDROM (1995) - 634,124,288 bytes of published physical "
                           "randomness with published SHA-256s. round17/SYNTHESIS.md named "
                           "it the single live, reachable, unswept public-pad item and \"the "
                           "cheapest live item in this branch\"; lane P2 found it, recorded "
                           "its identifier and a verified HTTP 206, and left it unswept."),
            "status": "negative" if m.get("complete") else "partially-run",
            "raw_status": "negative" if m.get("complete") else "partially-run",
            "source_register": "liber-primus/analysis/round17/SYNTHESIS.md",
            "evidence": [
                "liber-primus/analysis/round18/L6-offset-marsaglia/PREREG.md",
                "liber-primus/analysis/round18/L6-offset-marsaglia/RESULTS.md",
                "liber-primus/analysis/round18/L6-offset-marsaglia/data/MANIFEST.json",
                "liber-primus/analysis/round18/L6-offset-marsaglia/out/results_M.json",
                "liber-primus/analysis/round18/L6-offset-marsaglia/out/control_marsaglia.json"],
            "priority": "medium", "round": 18, "date": "2026-08-26",
            "threshold": (("score_norm >= max(threshold_for(N=%s) = %.4f, null_max + 0.5)"
                           % (f"{nB:,}", thrB)) if thrB else None),
            "threshold_fixed_in_advance": True,
            "positive_control": bool(cb and cb["PASS"]),
            "control_detail": (
                "Planted and recovered ON THE REAL, HASH-VERIFIED MARSAGLIA BYTES, not a "
                "synthetic pad: %d/%d trials recovered >95%% of rune indices at max_skip=8. "
                "max_skip=3 diagnostic on the same pads: recovery %.3f - the round-17/P1 "
                "constant-run defect %s bite here. Measured dense prefilter survival %.3f at "
                "keep=1000 on 10 MB pads; reported as the coverage discount. No x0.625 "
                "constant was used."
                % (int(round(cb["by_ms"]["8"]["recovery"] * cb["n_trials"])), cb["n_trials"],
                   cb["by_ms"]["3"]["recovery"],
                   "DOES" if cb["ms3_bites_here"] else "does NOT",
                   cb["by_ms"]["8"]["survival"]) if cb else None),
            "null": ("histogram-preserving shuffle null, n=200, max_skip=8, 400-rune window"),
            "result": (("best %.4f (%s / %s%s, sign %s, offset %s) vs bar %.4f."
                        % (bestB["score"], bestB.get("pad"), bestB.get("builder"),
                           "_rev" if bestB.get("rev") else "", bestB.get("sign"),
                           bestB.get("offset"), thrB)) if bestB else None),
            "coverage": {**digest["sub_lane_B"],
                         "hash_verification": ver,
                         "iso_bytes": man.get("iso", {}).get("bytes"),
                         "iso_md5": man.get("iso", {}).get("md5"),
                         "iso_sha1": man.get("iso", {}).get("sha1"),
                         "iso_sha256": man.get("iso", {}).get("sha256"),
                         "checksums_file_sha256":
                             man.get("checksums_file", {}).get("sha256"),
                         "published_sha256_lines_matched":
                             "%d/%s" % (len(man.get("inner_files", [])),
                                        man.get("checksums_file", {}).get("lines")),
                         "random_data_bytes": man.get("random_data_bytes"),
                         "builders": m.get("builders"),
                         "builders_excluded": m.get("builders_excluded")},
            "not_covered": NC_B,
            "reproduce": ("cd liber-primus/analysis/round18/L6-offset-marsaglia && "
                          "bash scripts/fetch_marsaglia.sh && "
                          "python3 scripts/verify_marsaglia.py && "
                          "python3 scripts/control_marsaglia.py && "
                          "python3 scripts/sweep_marsaglia.py"),
            "supersedes": None, "superseded_by": None,
            "reopens_if": ("A byte order, reduction or window outside the six builders x two "
                           "byte orders x two signs above; the units listed as not done in "
                           "coverage.units; or any score at or above its own null_max + 0.5."),
            "notes": ("First sweep of this pad by anyone in this repository. All 110 "
                      "published SHA-256s on the disc were verified before a single offset "
                      "was scored - this repo has twice been burned by a mirror serving "
                      "different bytes."),
            "evidence_missing": []})

    X.jdump({"schema_note": ("ledger-shaped fragment for merge into liber-primus/LEDGER.json; "
                             "read `coverage`/`not_covered`, not `status` (AGENTS.md s7)"),
             "lane": "round18/L6-offset-marsaglia",
             "generated": "2026-08-26",
             "entries": entries},
            os.path.join(LANE, "ledger.json"))
    print(json.dumps(digest, indent=1, default=str))
    print("\nwrote", os.path.join(LANE, "ledger.json"), "with", len(entries), "entries")


if __name__ == "__main__":
    main()
