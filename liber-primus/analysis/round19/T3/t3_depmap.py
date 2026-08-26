"""T3 job 1 — THE DEPENDENCY GRAPH.

For every LEDGER.json entry and every load-bearing synthesis claim: is it computed from the
12,956-rune stream, and if so, by which script and through which channel?

Channels (the classification that makes the map useful -- each has a DIFFERENT sensitivity
curve, measured elsewhere in this lane):

  S0  NOT stream-dependent          image bytes, PGP, OSINT, toolchain, provenance
  S1  stream -> SUMMARY STATISTIC   doublet rate / IoC / entropy / Delta-spectrum / chi2
  S2  stream -> DECODE SCORE        every keystream, keytext, pad and KDF sweep
  S3  stream -> LAYOUT / COUNTS     line breaks, glyph widths, positional subsets
  S4  stream -> the OBJECT ITSELF   the transcription is the claim
  UNK provenance not establishable from the repo

`reproduce_script_exists` is checked on disk: a claim whose reproduce path is missing is
flagged, because its provenance cannot be re-established.

Run: python3 t3_depmap.py            (writes dependency_map.json)
"""
import json, os, re, sys
import t3_lib as T

HERE = os.path.dirname(os.path.abspath(__file__))

# id -> (channel, statistics/mechanism, note)
CLASS = {
    # ---- verdicts
    "VERDICT-OTP-CLASS": ("S1+S2", "B4 6-statistic separation battery (doublet rate, IoC, entropy, "
                          "bigram, delta, run stats) + D3 planted-key decode",
                          "the headline verdict; its doublet leg is the object of this lane"),
    "VERDICT-UNSOLVABLE-BY-DESIGN": ("S1+S2", "as above", "superseded by VERDICT-OTP-CLASS"),
    # ---- keystream / keytext sweeps: every one is a decode score against THIS ciphertext
    "B-04": ("S2", "beam_decode score_norm vs null over 6.2M decodes", "round13/B04"),
    "B-05": ("S2", "beam_decode score_norm, 70,680 decodes", "round13/B05"),
    "B-21": ("S2", "Round 8 SEED sweep, 2.52e9 decodes, fixed bar", "seed_sweep"),
    "R12-A1": ("S2", "beam_decode over 6 CicadaOS binary pads, 768 decodes", "round12/A1"),
    "R12-C1": ("S2", "beam_decode, 1,155 decodes", "round12/C1"),
    "R12-C2": ("S2", "(never run) keytext sweep", "round12/C2"),
    "R17-PUBLIC-PAD": ("S2", "trigram prefilter + beam escalation over public pads", "round17/P0-P3"),
    "R16-KDF": ("S2", "beam_decode, 692,064 decodes", "round16/KDF"),
    "R16-PRNG": ("S2", "beam_decode, 52,556 decodes", "round16/prng"),
    "F-01": ("S2", "LP2-as-pad inversion, 40 decodes", "round16/F-01"),
    "R18-L2-DRIFT-LADDER": ("S2", "drift-corrected beam ladder", "round18/L2"),
    "L7-A-ARCHIVE-RESCORE": ("S2", "340 archived candidate decode strings re-scored", "round18/L7"),
    # ---- mechanism / filter: summary statistics of the stream
    "B-16": ("S1", "doublet rate + rewrite-vs-keyskip gate", "round12/D1"),
    "R12-D2": ("S1", "doublet floor min_d Pdp(d) over 4 English corpora; recomputes 86/0.664%",
               "round12/D2 -- the ORIGIN of the doublet-deficit argument"),
    "D-01": ("S1", "lag-1 suppression 80.75%, lag-2..8 bleed, line-scope test", "round17/P4"),
    "A-03": ("S1", "haplography count-audit of the 86 doublet SITES", "round16/A-03"),
    "R18-L2-A-LOCUS": ("S1", "7 filter models vs the real stream's doublet rate + Delta-spectrum",
                       "round18/L2"),
    "R18-L2-B-DRIFT": ("S1", "s* and rho derived by inverting the observed doublet rate",
                       "round18/L2"),
    "R18-L2-SKIP-CHANNEL": ("S1+S2", "inferred skip count as a ranking channel", "round18/L2"),
    "R18-L2-INFO-BUDGET": ("S1", "closed-form information budget from n and the doublet rate",
                           "round18/L2"),
    "L7-C-HEADLINE-STATS": ("S1", "n, doublets, doublet rate, IoC*N, entropy, lag-1 suppression",
                            "round18/L7 C.1 -- reproduced exactly by this lane (PC-3)"),
    "L7-C-G3-FLOOR-EXTENDED": ("S1", "min_d Pdp(d) over 9 registers vs the observed 0.664%",
                               "round18/L7 C.2 -- the floor this lane's headline k is measured against"),
    # ---- layout / counts
    "C-02": ("S3", "line-initial chi2 78.656 + layout-aware null + glyph-width table",
             "round18/L4"),
    "B-12": ("S3", "line geometry / ornament band tests", "round18/L3"),
    "A-06": ("S3+S0", "47 ornament bands: image-derived, band contents not in the rune stream",
             "round18/L3"),
    "B-02": ("S2", "key-offset ladder: every sweep assumed key index 0 = rune 0", "round18/L6"),
    "B-08": ("S2", "as B-02", "round18/L6"),
    "B-13-MARSAGLIA": ("S2", "Marsaglia CDROM pads", "round18/L6"),
    # ---- transcription: the object itself
    "A-01": ("S4", "the transcription of the dense pages", "THE OBJECT -- lane T2"),
    "A-02": ("S4", "the 450 located O/A/AE disagreements", "THE OBJECT -- lane T1; mapped to "
             "stream coordinates for the first time by THIS lane"),
    "R12-frontB": ("S4", "forced re-segmentation of pages 45-54, 98.0% validated-instrument "
                   "agreement", "round12/frontB"),
    "A-05": ("S4", "further transcription checks", ""),
    # ---- instrument
    "R16-scorer": ("S2", "scorer measurement on decodes of this ciphertext", "round16/scorer"),
    "L7-A-SCORER-ENGLISH-ONLY": ("S2", "correct-key score by plaintext register (SYNTHETIC "
                                 "ciphertext, not LP2)", "round18/L7 A -- instrument property, "
                                 "independent of the LP2 transcription"),
    "L7-B-BEAM-ENVELOPE": ("S2", "67 decoder constructions on SYNTHETIC ciphertext",
                           "round18/L7 B -- instrument property, transcription-independent"),
    "R18-L2-BEAM-LENGTH-POWER": ("S2", "full-book positive control at L=12,956 (n only)",
                                 "round18/L2 -- uses the LENGTH of the stream, not its content"),
    "L7-C-THRESHOLD-CALIBRATION": ("S0", "Gumbel constants of threshold_for(); a property of the "
                                   "null generator", "round18/L7 C.3"),
    "L7-C-B17-TALLY": ("S0", "counting of hypotheses/decodes", "round18/L7 C.6"),
    "L7-A-HANDOFF-NONCOMPLIANCE": ("S0", "process audit", "round18/L7 A.6"),
    "RESTATE-B-21-ROUND8-BAR": ("S0", "restatement of a bar", "round18/L7"),
    "RESTATE-B-04": ("S0", "restatement", "round18/L7"),
    "RESTATE-R16-KDF": ("S0", "restatement", "round18/L7"),
    "RESTATE-R16-PRNG": ("S0", "restatement", "round18/L7"),
    "RESTATE-R17-PUBLIC-PAD": ("S0", "restatement", "round18/L7"),
    "R17-P2-CENSUS-CORRECTION": ("S0", "record integrity", "round17/P2"),
    # ---- payload / images / provenance / OSINT: not the rune stream
    "A-04": ("S0", "6 contested pp49-51 payload BYTES (image-derived)", "round18/L5"),
    "E-01": ("S0", "7A35090F moduli", "round18/L5"),
    "E-02": ("S0", "zero-FP tests", "round16/zeroFP"),
    "H-03": ("S0", "zero-FP tests", "round16/zeroFP"),
    "G-01": ("S0", "JPEG/toolchain fingerprints of the source images", "round18/L1"),
    "G-02": ("S0", "corpus gaps", "round18"),
    "G-09": ("S0", "seed candidate list", "round18/L8"),
    "B-11": ("S0+S3", "glyph extraction geometry from the images", "round18/L1"),
    "I-01": ("S0", "PGP provenance base rate", "round18/L8"),
    "I-03": ("S0", "provenance", "round18/L8"),
    # ---- open / never-run register items (no published result yet; classified by what
    #      a run of them WOULD consume, so the map is complete rather than half-blank)
    "B-01": ("S2", "32-bit PRNG seed sweep -> beam_decode score", "open, 2/10 complete"),
    "B-03": ("S2", "further generator families -> beam_decode score", "open"),
    "C-01": ("S2+S1", "word-length / skeleton match against the stream's line structure", "open"),
    "D-02": ("S1", "PPM bits/rune of the stream vs matched controls", "open"),
    "D-03": ("S2", "homophonic-downward annealing over the stream", "open"),
    "D-04": ("S2", "non-additive ciphertext-feedback sweep", "partially-run, 3 of 55 pages"),
    "F-02": ("S0", "the 2016-01-01 signed message (external artifact)", "open"),
    "H-01": ("S0", "onion HTTP/server-status anomalies", "never-run"),
    "H-02": ("S3", "full-corpus WHITESPACE re-audit -- word/line segmentation of the stream",
             "partially-run; an S3 claim, and the one class this lane's substitution-only "
             "models do NOT cover"),
    "I-02": ("S0", "2013/2014 winner forum OSINT", "partially-run"),
    "I-04": ("S0", "Schoenberger court docket", "partially-run"),
    "J-01": ("S0", "repo maintenance note", "open"),
    "B-10": ("S0", "OutGuess 0.2 Linux control (image stego)", "open"),
    "B-13": ("S4", "O/A/AE per-glyph adjudication -- the same object as A-02",
             "open; THIS lane maps its 450 positions into the stream"),
    "B-23": ("S3", "separator audit, 170 of 604 lines; 19 disagreements unread",
             "partially-run; separators are the S3/whitespace class"),
    "B-09": ("S0", "OSINT residue, T2/T3 blobs", "open"),
    "B-06": ("S0", "a signed/archival pointer to a keytext", "never-run"),
    "B-07": ("S0", "a locally-held archive for the AN END page", "never-run"),
    "B-14": ("S2", "AUTO_EVOLUTION epoch-6 SEEK roadmap", "never-run"),
    "B-17": ("S0", "multiple-comparisons tally", "open; recomputed by L7-C.6"),
    "B-15": ("S2", "Round 6 trigram arm, restated closure", "open"),
    "B-18": ("S0", "navigation-doc visibility of Round 9", "open"),
    "B-19": ("S2+S1", "Round 9 LENGTH estimate from the stream", "open"),
    "B-20": ("S2", "Round 9 DIRECTION, 400-rune reads", "open"),
    "B-22": ("S0", "repo premise about orphaned .pyc", "open"),
    "B-24": ("S2", "Round 2 specificity anchor on the 85-rune AN END page (SOLVED page, "
             "not the 12,956-rune unsolved stream)", "open"),
    "A-05": ("S4", "further transcription checks", ""),
    "I-01": ("S0", "PGP provenance base rate", "round18/L8"),
}

# Load-bearing synthesis claims that are NOT ledger entries.
SYNTHESIS = [
    ("doublet deficit 0.664% is THE anomaly", "S1",
     "FINAL-SYNTHESIS.md GOAL 1; PROBLEM.json measured_statistics",
     "lp.stats.doublet_rate over the pinned stream",
     "the entire OTP argument's ciphertext-side evidence"),
    ("IoC*N = 1.0000 (flat / polyalphabetic)", "S1",
     "PROBLEM.json measured_statistics", "lp.stats.ioc_norm", "flatness"),
    ("Shannon entropy 4.857 bits (max 4.858)", "S1",
     "PROBLEM.json measured_statistics", "lp.stats.shannon_entropy", "incompressibility"),
    ("anti-repeat suppression ~83% / lag-1 80.75%", "S1",
     "round17/P4 RESULTS.md; round18/L7 C.1", "1 - r_obs/IoC", "the pinned filter constant"),
    ("s* = 0.81288 derived rather than fitted", "S1",
     "round18/L2 §1", "invert r(s)=q(1-s)/(1-qs)", "first derivation of the filter constant"),
    ("draw count 373.6 +/- 19.6 over the book", "S1",
     "round18/L2 §1/B.1", "rho*n from s*", "keystream index lead; sets B-02's offset ladder"),
    ("4 of 86 doublets cross a line break -> the filter had no per-line scope (power 1.000)",
     "S3", "round17/P4; round18/L4 §0", "line-break doublet count over global_lines()",
     "excludes a hand-applied per-line filter"),
    ("Delta-spectrum chi2/df = 1.533, max|z| = 2.64 at D=17", "S1",
     "round18/L2 §2", "28-cell delta histogram",
     "L2 EXPLICITLY deferred a transcription re-check of this to a later lane"),
    ("line-initial chi2 = 78.656, p <= 5e-6, explained by layout (p = 0.177)", "S3",
     "round18/L4 Arm A1 + §2", "positional subset chi2 + layout-aware null",
     "the only ciphertext-visible structural anomaly that is not the filter"),
    ("glyph-width table for the 29 runes", "S3", "round18/L4 §2",
     "derived from the transcription's own line lengths",
     "the durable output any future positional attack must use"),
    ("min_d Pdp(d) floor 0.972% (German) .. 2.339% (Welsh); margin 1.46x", "S1(+corpora)",
     "round18/L7 C.2", "min over key shift of the plaintext-independent doublet rate",
     "the threshold the doublet deficit is compared against"),
    ("O/A/AE family = 10.70% of the corpus; family collapse moves IoC 1.00->1.14, "
     "doublet 0.68%->1.46%", "S1",
     "independent-read/FINDINGS.md §4", "crypto_exposure.py",
     "the ONLY previously published sensitivity number in the repo; reproduced by this lane"),
    ("krisyotam == relikd char-for-char over the full 12,956-rune overlap", "S4",
     "transcription/TRANSCRIPTION-VERDICT.md", "diff", "not independent: one 2017 root"),
    ("96.93% agreement (5,047/5,207) on 232/604 count-exact lines", "S4",
     "retranscribe/FINDINGS.md", "template DP read vs canon", "audit 1"),
    ("98.0% over 5,150 glyphs on the 232 count-exact lines", "S4",
     "round12/frontB/RESULTS.md", "R9 raw-band template DP", "audit 2"),
    ("450 located O/A/AE disagreements", "S4",
     "independent-read/oae_mismatch.json", "label-free KMeans sub-clustering",
     "audit 3; positions were in GLYPH-index space until this lane mapped them"),
    ("whole-page AI vision re-transcription: mean alignment 0.145 = noise", "S4",
     "vision/AVENUE-1-VISION-VERDICT.md", "alignment", "audit 4 (failed instrument)"),
]


def main():
    led = json.load(open(os.path.join(T.ROOT, "LEDGER.json"), encoding="utf-8"))
    entries = led["entries"]
    rows, unknown, missing = [], [], []
    for e in entries:
        eid = e["id"]
        ch, mech, note = CLASS.get(eid, ("UNK", "", ""))
        rep = e.get("reproduce") or ""
        exists = None
        # `reproduce` comes in two shapes: absolute-ish "liber-primus/a/b.py", and
        # "cd <dir> && python3 x.py" where x.py is relative to <dir>.  Resolve both.
        cds = re.findall(r"cd\s+(?:liber-primus/)?([\w\-/\.]+)", rep)
        base = os.path.join(T.ROOT, cds[-1]) if cds else T.ROOT
        cand_paths = []
        for pth in re.findall(r"(liber-primus/[\w\-/\.]+\.(?:py|sh))", rep):
            cand_paths.append((pth, os.path.join(T.ROOT, pth[len("liber-primus/"):])))
        for pth in re.findall(r"(?:python3?|bash)\s+([\w\-/\.]+\.(?:py|sh))", rep):
            if pth.startswith("liber-primus/"):
                continue
            cand_paths.append((pth, os.path.join(base, pth)))
        if cand_paths:
            paths = [(pth, os.path.exists(c)) for pth, c in cand_paths]
            exists = all(v for _, v in paths)
            if not exists:
                missing.append({"id": eid, "base": cds[-1] if cds else "",
                                "paths": paths})
        row = {
            "id": eid, "lane": e.get("lane"), "status": e.get("status"),
            "round": e.get("round"), "hypothesis": (e.get("hypothesis") or "")[:400],
            "stream_dependent": ch != "S0" and ch != "UNK",
            "channel": ch,
            "mechanism": mech,
            "note": note,
            "reproduce": rep[:200],
            "reproduce_script_exists": exists,
            "has_coverage_field": bool(e.get("coverage")),
            "has_not_covered_field": bool(e.get("not_covered")),
            "evidence_missing": e.get("evidence_missing") or [],
        }
        rows.append(row)
        if ch == "UNK":
            unknown.append({"id": eid, "status": e.get("status"),
                            "hypothesis": (e.get("hypothesis") or "")[:200]})

    syn = [{"claim": c, "channel": ch, "source": src, "computed_by": by, "why_load_bearing": w}
           for c, ch, src, by, w in SYNTHESIS]

    counts = {}
    for r in rows:
        counts[r["channel"]] = counts.get(r["channel"], 0) + 1

    # the sensitivity each channel inherits, filled from this lane's own measurements
    channel_sensitivity = {
        "S0": "insensitive to the rune stream by construction.",
        "S1": "smooth. Measured in out_random.json / out_targeted.json: the doublet rate moves "
              "+1 doublet per ~14.5 random substitutions and +2 per adversarial substitution.",
        "S2": "DISCONTINUOUS. Measured in out_decode_L400.json: a corrupted cipher rune breaks "
              "the beam's skip-validity relation, so correct-key recovery falls far faster than "
              "the error rate. This is the fragile channel and it carries every sweep negative.",
        "S3": "smooth but coupled to the line parse; unchanged by substitution-only errors that "
              "preserve n. An insertion/deletion error would re-index every line and is NOT "
              "covered by this lane.",
        "S4": "the object itself. These are the audits, not consumers.",
        "UNK": "provenance not established -- FLAGGED.",
    }

    out = {
        "generated_by": "round19/T3/t3_depmap.py",
        "baseline_sha256": T.sha_of(T.stream()),
        "n_ledger_entries": len(rows),
        "channel_counts": counts,
        "channel_sensitivity": channel_sensitivity,
        "n_stream_dependent": sum(1 for r in rows if r["stream_dependent"]),
        "unknown_provenance": unknown,
        "reproduce_paths_missing": missing,
        "ledger_entries": rows,
        "synthesis_claims": syn,
    }
    json.dump(out, open(os.path.join(HERE, "dependency_map.json"), "w"), indent=1)
    print(json.dumps({"channel_counts": counts,
                      "n_stream_dependent": out["n_stream_dependent"],
                      "n_unknown": len(unknown),
                      "n_missing_scripts": len(missing)}, indent=1))
    for u in unknown:
        print("UNK:", u["id"], "|", u["status"], "|", u["hypothesis"][:120])
    for m_ in missing:
        print("MISSING SCRIPT:", m_["id"], m_["paths"])


if __name__ == "__main__":
    main()
