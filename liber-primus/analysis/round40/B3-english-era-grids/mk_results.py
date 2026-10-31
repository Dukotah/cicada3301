#!/usr/bin/env python3
"""R40-B3: assemble RESULTS.md, ledger.json, ledger_patches.json from the lane's JSON artefacts."""
import sys, os, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
F = lambda n: os.path.join(HERE, n)
J = lambda n: json.load(open(F(n))) if os.path.exists(F(n)) else None

counts = J("counts.json"); cpads = J("counts_pads.json") or {}
ctrl = {k: J("control_%s.json" % k) for k in ("B04", "KDF", "COSPAD", "R17PAD", "B04red")}
fin = {k: J("final_%s.json" % k) for k in ("B04", "KDF", "R17PAD", "COSPAD")}
p3 = J("p3_regen_compare.json"); cos = J("cos_pads_regen.json")
GN = {"B04": "B04", "KDF": "KDF", "R17PAD": "R17PAD", "COSPAD": "COSPAD"}
GP = {"R17PAD": "G3", "COSPAD": "G4"}
TITLE = {"B04": "B-04 seed dictionary (SHA/HMAC/RC4/AES/ChaCha expanders)", "KDF": "R16-KDF (PBKDF2/scrypt/iterated/EVP, 534 secrets)",
         "R17PAD": "R17 public pads (P3: RAND digits + 3301's published bytes)", "COSPAD": "CicadaOS pads (R12-A1 / R28-L1)"}


def ctab(c):
    if not c: return "(control not available)"
    L = ["| register | skip split | n | screen pass | pass | recover (>=0.90) |", "|---|---|---:|---:|---:|---:|"]
    for k, v in c["pooled_by_register_skip"].items():
        reg, sk = k.split("|")
        L.append("| %s | %s | %d | %d | %d | %d |" % (reg, sk, v["n"], v["prefilter"], v["pass"], v["recover"]))
    fp = c["decoy_fpr"]
    L.append("")
    L.append("Decoy columns screened with the plants: %d, survivors %d (rate %.2e). Registers licensed by the >=3-per-cell gate: %s." % (fp["n"], fp["survivors"], fp["rate"], c["register_licensed"]))
    return "\n".join(L)


def wil(k, n, z=1.96):
    if n == 0: return float("nan")
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); r = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (c - r) / d


def regtab():
    L = ["| register | " + " | ".join(k for k in ("B04", "KDF", "R17PAD", "COSPAD")) + " | pooled | Wilson 95% lower |", "|---|---|---|---|---|---|---|"]
    for reg in ("EN_MODERN", "EN_NOVOWEL", "LATIN"):
        cells = []; K = N = 0
        for k in ("B04", "KDF", "R17PAD", "COSPAD"):
            c = ctrl.get(k)
            if not c: cells.append("n/a"); continue
            kk = sum(v["recover"] for kn, v in c["pooled_by_register_skip"].items() if kn.startswith(reg + "|")); nn = sum(v["n"] for kn, v in c["pooled_by_register_skip"].items() if kn.startswith(reg + "|"))
            cells.append("%d/%d" % (kk, nn)); K += kk; N += nn
        L.append("| %s | %s | %d/%d | %.3f |" % (reg, " | ".join(cells), K, N, wil(K, N)))
    return chr(10).join(L)


def rtab(f):
    L = ["| relation | N decodes (survivors) | screened | best pmax (register) | bar L120 actual N | bar L120 N=1e6 | bar L120 N=screened | clears actual N | clears N=1e6 |", "|---|---:|---:|---|---:|---:|---:|---|---|"]
    for r, e in f["rels"].items():
        L.append("| %s | %d | %d | %.3f (%s)%s | %.3f | %.3f | %.3f | %s | %s |" % (r, e["N_actual"], e["N_screened"], e["best_pmax"], e["best_preg"], " degenerate" if e["best_degenerate"] else "",
                                                                                      e["bar120_actualN"], e["bar120_declN"], e["bar120_screenedN"], e["clears_actualN"], e["clears_declN"]))
    return "\n".join(L)


def frac(g):
    pc = (cpads.get(g) or {}).get("per_cell") or {}
    c = sum(v[0] for v in pc.values()); n = sum(v[1] for v in pc.values())
    return "%d of %d (builder x direction) offset-columns = %.4f%% of the dense offset space of these cells" % (c, n, 100.0 * c / max(n, 1)) if n else "n/a"


def sect(k):
    f = fin[k]
    if not f: return "### %s\n\n(not run / not finalized)\n" % TITLE[k]
    c = ctrl.get(GN[k])
    L = ["### %s" % TITLE[k], ""]
    if k == "B04":
        L += ["Keys regenerated: **%d seeds / %d core** (original 2,165 / 504); 16 generators x 5 reductions; configs screened **%d** (planned %d: A %d, B %d, C %d). Original B-04 decodes: 6,224,300 (legacy beam)."
              % (counts["B04"]["seeds"], counts["B04"]["core"], f["screened"], counts["B04"]["planned_total"], counts["B04"]["planned"]["A"], counts["B04"]["planned"]["B"], counts["B04"]["planned"]["C"])]
    elif k == "KDF":
        L += ["Keys regenerated: **%d secrets** (original 534) x 27 KDFs x 3 salts x 2 reductions x 8 variants = **%d** configs screened (original 692,064 legacy decodes)." % (counts["KDF"]["secrets"], f["screened"])]
    elif k == "R17PAD":
        c3 = cpads.get("G3", {})
        L += ["Pads regenerated: P3 list **%d of 28** (sha256 match %d, mismatch %d, missing %d); builders %s; configs screened **%d**, planned columns %s. "
              "P1 (Bitcoin) and P2 (beacon + random.org) are NOT regenerated. Offset coverage: %s." % (p3["regen_n"] if p3 else -1, len(p3["match_sha"]) if p3 else -1, len(p3["mismatch"]) if p3 else -1, len(p3["missing_in_regen"]) if p3 else -1,
                                                                                    ", ".join(c3.get("builders", [])), f["screened"], c3.get("columns_planned"), frac("G3"))]
    else:
        c4 = cpads.get("G4", {})
        L += ["Pads regenerated from the ISO: %s; builders %s; configs screened **%d**, planned columns %s. Offset coverage: %s." % (", ".join("%s (%d B, receipt %s)" % (n, v["bytes"], v["receipt_match"]) for n, v in (cos or {}).items()),
                                                                                                         ", ".join(c4.get("builders", [])), f["screened"], c4.get("columns_planned"), frac("G4"))]
    L += ["", "Planted controls (natural rate, real route, 10 per register x relation):", "", ctab(c), "", rtab(f), "",
          "Flagged-for-oracle: **%d**. Near-miss (cleared actual-N L=120 but not the gate / N=1e6): **%d**. Survivor rate (screen FPR) %.2e; decode errors %d; elapsed %.0fs." %
          (len(f["flagged"]), len(f["near_miss"]), f["survivors"] / max(f["screened"], 1), f["decode_errors"], f["elapsed_s"] or 0)]
    for r, e in f["rels"].items():
        L.append("- top (%s): %s" % (r, "; ".join("%.3f %s [%s]" % (t[0], t[1], t[2]) for t in e["top5"][:3])))
    L.append("- screen survivor rate by group: " + ", ".join("%s %.1e" % (g, v["rate"]) for g, v in list(f["by_group"].items())[:12]))
    L.append("- store validation: validate_store=%s, check_r3_store=%s" % (f["validate_store"], f["check_r3_store"]))
    return "\n".join(L) + "\n"


def main():
    now = time.strftime("%Y-%m-%d")
    R = ["# R40-B3 RESULTS: the English-era seed / key grids re-decoded under beam_v3 keyskip1+keyskip2 on panel-R36", "",
         "_Run %s. Instrument = R37-I2 imported unchanged (pf_v4_12 frozen screen, beam_v3 panel_max, panel-R36 12 registers, null12 POT bars). "
         "PREREG: `PREREG.md` + `PREREG-ADDENDUM-1.md`, dated before the first grid row. No `git` was run. No terminal verdicts are claimed: every line below is a bound on the regenerated list._" % now, ""]
    R += ["## 1. Per-grid table", "", "| grid | keys regenerated / original | configs screened | N per relation | best pmax keyskip1 / keyskip2 | actual-N bar L120 (ks1/ks2) | flagged | near-miss |", "|---|---|---:|---:|---|---|---:|---:|"]
    kr = {"B04": "2,165 seeds (504 core) / 2,165 (504)", "KDF": "534 secrets / 534", "R17PAD": "%s pads (P3) / 28" % (p3["regen_n"] if p3 else "?"), "COSPAD": "4 ISO pads / 6 (R12-A1) or 2 authoritative (R28-L1)"}
    for k in ("B04", "KDF", "R17PAD", "COSPAD"):
        f = fin[k]
        if not f: R.append("| %s | %s | not run | | | | | |" % (k, kr[k])); continue
        a = f["rels"]["keyskip1"]; b = f["rels"]["keyskip2"]
        R.append("| %s | %s | %d | %d | %.3f / %.3f | %.3f / %.3f | %d | %d |" % (k, kr[k], f["screened"], a["N_actual"], a["best_pmax"], b["best_pmax"], a["bar120_actualN"], b["bar120_actualN"], len(f["flagged"]), len(f["near_miss"])))
    R += ["", "Planted-control recovery per register (recovered = screen pass + pmax120 and pmax240 >= N=1e6 bars + recovery >= 0.90; KDF rev plants are L=120 only):", "", regtab(), ""]
    fl = [(k, e) for k in fin if fin[k] for e in fin[k]["flagged"]]
    R += ["## Flagged / near-miss", ""]
    if fl:
        for k, e in fl:
            R.append("- **FLAGGED_FOR_ORACLE** (%s): `%s` pmax120 %.3f (%s) vs actual-N bar %.3f; clears N=1e6 bar: %s; gate: %s. Not certified; bundle `ORACLE-KDF-iter_md5_1000-rev/bundle.json`, notes `ORACLE-PENDING.md` (score falls with read length 6.528 -> 5.531, gibberish transliteration, single-cell exceedance P=0.6%%, 8 cells run)." % (k, e["kid"], e["pmax120"], e["preg120"], e["bar120_actualN"], e["clears_declN_L120"], e["gate"]))
    else:
        R.append("- none flagged")
    R += ["- Near-misses (cleared the actual-N L=120 bar but failed the gate or N=1e6): none other than the row above.", "- Rows with pmax >= 6.0 (retained, `keep_*.json`): " + ", ".join("%s %d" % (k, len(json.load(open(F("keep_%s.json" % k))))) for k in fin if fin[k]) + ". Top rows per grid are listed in section 2; none is degenerate.", ""]
    R += ["## 2. Grids", ""]
    for k in ("B04", "KDF", "R17PAD", "COSPAD"): R.append(sect(k))
    if ctrl.get("B04red"):
        R += ["### Supplementary B-04 control (Z16 / bit-group reductions)", "", "Plants restricted to hi_nib, lo_nib, bits5 (stage A, offset 0), EN_MODERN + EN_NOVOWEL, 10 per register x relation:", "", ctab(ctrl["B04red"]), ""]
    R += ["## 3. What could not be regenerated", "",
          "- **R12-A1 truncated `_560.00`** (2,412,544 B), `folly`/`wisdom` (3,368 B) and `prime_echo` (12,248 B): sources were the cicada-solvers mirror and local OSINT artifacts not on this disk. The 3,992,970 B ISO `DATA/_560.00` (the R28-L1 authoritative pad) IS regenerated.",
          "- **R17-P1 Bitcoin heights 0-303,726 and R17-P2 NIST beacon v1 + random.org 153 files**: multi-GB network fetches; not regenerated; their (English-only) negatives keep all three conditionals.",
          "- **R17 and R12/R28 dense offset spaces**: only the stated sampled fractions below were re-decoded (not a dense re-sweep). R17 scored 1.45e10 offsets; this lane screened a sampled subset.",
          "- **B-04 Stage D** (survivor escalation) is superseded by the L=240 gate; B-05 payload-as-seed and B-02 offset scans were not in this lane's list.",
          "- **KDF**: Stage B salt expansion was never run in the original and is not run here; rev-direction L=240 gate is unavailable (184-symbol buffer).", ""]
    R += ["## 4. Conditionals now carried (doctrine Q4)", "",
          "1. **Key space**: exactly the regenerated lists above (counts), with pad grids at the stated sampled fractions.",
          "2. **Transition model**: `keyskip1` + `keyskip2`, heads with <= 2 skips in 24 runes (pf_v4_12); `skip_by_4`, `skip_by_5`, reset-per-page/line, `free`, combined axes unrepresented. This REPLACES the legacy keyskip1-only conditional (legacy beam recovered 0.258 of a `skip_by_two` plant).",
          "3. **Register**: panel-R36, 12 registers (reach per register = screen power 0.952-0.994 x v3 recovery); planted controls here cover **EN_MODERN, EN_NOVOWEL, LATIN** only: `[plants: EN_MODERN / EN_NOVOWEL / LATIN]`; the other nine registers are assumed from the R37-I2 screen-power table and the pooled v3 recovery.",
          "4. The screen thresholds were calibrated on bash heads (uniform Z29); the realised survivor rates on these hash/KDF/pad key heads (table above) are the empirical check that the screen FPR transfers.", ""]
    R += ["## 5. Files", "", "`PREREG.md`, `PREREG-ADDENDUM-1.md`, `engine.py`, `grids.py`, `pads.py`, `b3.py`, `b3pads.py`, `b3extra.py`, `finalize.py`, `mk_results.py`, `control_*.json`, `final_*.json`, `summary_*.json`, `keep_*.json`, `rows_*.jsonl` (SWEEPROW, 14 fields, append-mode), `counts*.json`, `p3_regen_compare.json`, `cos_pads_regen.json`, `ledger.json`, `ledger_patches.json`."]
    open(F("RESULTS.md"), "w").write("\n".join(R) + "\n")

    # ---------------- ledger
    ent = []
    def entry(k, id_, hyp, cov_extra, notcov, reopens, status="negative", extra=None):
        f = fin[k]
        if not f: return
        c = ctrl.get(GN[k]); a = f["rels"]["keyskip1"]; b = f["rels"]["keyskip2"]
        pooled = c["pooled_by_register_skip"] if c else {}
        cd = "control_%s.json: %d plants (10 each EN_MODERN/EN_NOVOWEL/LATIN x keyskip1/keyskip2) through the grid's real key route and the sweep's screen; recovered per register x skip split: %s; decoy screen FPR %.2e." % (
            GN[k], len(c["plants"]) if c else 0, "; ".join("%s %d/%d" % (kk, v["recover"], v["n"]) for kk, v in pooled.items()), c["decoy_fpr"]["rate"] if c else float("nan"))
        ent.append({"round": 40, "lane": "B3", "date": now, "id": id_, "status": status, "positive_control": "passed" if c and all(c["register_licensed"].values()) else "partial",
                    "control_detail": cd, "hypothesis": hyp,
                    "coverage": "%d configs screened with pf_v4_12; %d survivors decoded under beam_v3 panel_max keyskip1+keyskip2 at L=120 on panel-R36 (%d rows in the store); %s" % (f["screened"], f["survivors"], 2 * f["survivors"], cov_extra),
                    "result": "flagged %d, near-miss %d. Best keyskip1 %.3f (%s) vs 12-register bar %.3f at actual N (N=%d; %.3f at N=1e6); keyskip2 %.3f (%s) vs %.3f (%.3f at N=1e6)." % (
                        len(f["flagged"]), len(f["near_miss"]), a["best_pmax"], a["best_preg"], a["bar120_actualN"], a["N_actual"], a["bar120_declN"], b["best_pmax"], b["best_preg"], b["bar120_actualN"], b["bar120_declN"]),
                    "threshold": "round36 null12.json POT bars at actual N and N=1e6 (L=120 screen, L=240 gate); screen thresholds frozen R37 (7.4155 / 7.4412)", "threshold_fixed_in_advance": True,
                    "three_conditionals": {"key_space": cov_extra, "transition_model": "keyskip1+keyskip2 under beam_v3 panel_max; heads with <=2 skips in 24 runes screened; not free, skip_by_4/5, resets",
                                           "adjudicator_register": "panel-R36 12 registers; planted controls EN_MODERN / EN_NOVOWEL / LATIN only"},
                    "not_covered": notcov, "reopens_if": reopens,
                    "evidence": ["analysis/round40/B3-english-era-grids/RESULTS.md", "analysis/round40/B3-english-era-grids/PREREG.md", "analysis/round40/B3-english-era-grids/final_%s.json" % k,
                                 "analysis/round40/B3-english-era-grids/control_%s.json" % GN[k], "analysis/round40/B3-english-era-grids/rows_%s.jsonl" % k],
                    "sweep_store": "analysis/round40/B3-english-era-grids/rows_%s.jsonl" % k, **(extra or {})})
    entry("B04", "R40-B3-B04-REDECODE", "The LP2 key is a hash/MAC/stream-cipher expansion of one of the 2,165 regenerated B-04 seeds (16 generators x 5 reductions, direction, sign, atbash; offsets 0..7 + ladder; per-page restarts).",
          "2,165 seeds (504 core) regenerated; stage A offset 0 (1,385,600), stage B offsets {0..7,16,29,64,128,256,512,1024,3301} on core (2,064,384), stage C 55 page heads (3,548,160)",
          "Seeds outside the 2,165; key stretching; salts; offsets beyond 3301 and per-line restarts; B-05 payload-as-seed; heads with >=3 skips in 24 runes; registers beyond EN_MODERN/EN_NOVOWEL/LATIN planted; page heads <120 runes use an uncalibrated bar",
          "a seed outside the dictionary, a stretching/salting construction, or an oracle flag")
    entry("KDF", "R40-B3-R16KDF-REDECODE", "The LP2 key is a KDF (PBKDF2/scrypt/iterated/EVP, 27 configs) expansion of one of 534 regenerated secrets with salt empty/3301/self.",
          "534 secrets x 27 KDFs x 3 salts x 2 reductions x 8 variants, offset 0, 184-symbol buffer",
          "KDF configs outside the 27; salts beyond empty/3301/self (Stage B never run); offsets != 0; rev-direction L=240 gate unavailable",
          "a KDF config, salt or secret outside the covered lists, or the owner's oracle read of the flagged row says PASS", status="partially-run",
          extra={"flagged_for_oracle": [e["kid"] for e in (fin["KDF"] or {"flagged": []})["flagged"]], "oracle_note": "analysis/round40/B3-english-era-grids/ORACLE-PENDING.md; below the N=1e6 and screened-N bars; no L=240 gate for rev; protocol flag, not a finding"})
    entry("R17PAD", "R40-B3-R17-PUBLIC-PAD-REDECODE", "The LP2 key is a slice of one of the R17-P3 public pads (RAND digits or 3301's published bytes) under a byte-to-symbol builder.",
          "R17-P3 28-pad list regenerated, builders as listed, offsets = 0..7 + A1 ladder + capped stride sample per cell (a sampled fraction of the 5.76e9 dense offsets, NOT a dense re-sweep); R17-P1/P2 not regenerated",
          "Dense offsets; R17-P1 Bitcoin and R17-P2 beacon/random.org pads; Marsaglia CDROM; hexchars for pads >2 MB; builders outside the list",
          "the dense offsets or any unregenerated public pad are screened under beam_v3 and a row crosses", status="partially-run")
    entry("COSPAD", "R40-B3-COSPAD-REDECODE", "The LP2 key is a literal byte-to-symbol reduction of a CicadaOS ISO pad (560.00 authoritative, 560.13, 560.17, 761.mp3).",
          "4 ISO pads, 5 reductions x fwd/rev x sign; offsets 0..7 + ladder + R28-L1 stride grids + capped stride sample per cell (sampled fraction, not dense)",
          "Dense offsets; the truncated 2,412,544 B `_560.00`, folly, prime_echo (unregenerable here); pads as PRF seed/salt; atbash",
          "dense offsets screened under beam_v3 and a row crosses, or the pads are used as a PRF seed/salt", status="partially-run")
    json.dump({"$comment": "written by R40 B3 lane agent; not merged into LEDGER.json", "lane": "B3", "entries": ent}, open(F("ledger.json"), "w"), indent=1)

    # ---------------- patches
    cons = lambda k: ("%d configs, best %.3f/%.3f vs actual-N bars %.3f/%.3f, flagged %d" % (fin[k]["screened"], fin[k]["rels"]["keyskip1"]["best_pmax"], fin[k]["rels"]["keyskip2"]["best_pmax"],
                                                                                          fin[k]["rels"]["keyskip1"]["bar120_actualN"], fin[k]["rels"]["keyskip2"]["bar120_actualN"], len(fin[k]["flagged"]))) if fin[k] else "not run"
    patches = [
        {"id": "B-04", "coverage_add": "R40-B3: the 2,165-seed dictionary (504 core) re-decoded under pf_v4_12 + beam_v3 panel_max keyskip1+keyskip2 on panel-R36, 16 generators x 5 reductions x dir x sign x atbash; stages A, B (offsets 0..7 + ladder), C (55 page heads): %s. Planted controls EN_MODERN/EN_NOVOWEL/LATIN. See R40-B3-B04-REDECODE." % cons("B04"),
         "not_covered_remove": "English-only / keyskip1-only decode of the seed dictionary (now keyskip1+keyskip2, 12 registers, plants in 3 registers)",
         "pin_suggestion": "<!-- pin: R40-B3-B04-REDECODE | 6,998,144 -->"},
        {"id": "R16-KDF", "coverage_add": "R40-B3: 534 secrets x 27 KDFs x 3 salts re-decoded under the same instrument: %s. See R40-B3-R16KDF-REDECODE." % cons("KDF"),
         "not_covered_remove": "English-only / keyskip1-only decode of the KDF grid", "pin_suggestion": "<!-- pin: R40-B3-R16KDF-REDECODE | 692,064 -->"},
        {"id": "R17-PUBLIC-PAD", "coverage_add": "R40-B3: the regenerated R17-P3 pads (RAND digits, 3301's published bytes) re-decoded at a STATED SAMPLED FRACTION of offsets (0..7 + ladder + capped stride): %s. R17-P1/P2 not regenerated. See R40-B3-R17-PUBLIC-PAD-REDECODE." % cons("R17PAD"),
         "not_covered_remove": "none (dense offsets and P1/P2 remain)", "pin_suggestion": "<!-- pin: R40-B3-R17-PUBLIC-PAD-REDECODE | configs -->"},
        {"id": "R12-A1", "coverage_add": "R40-B3: the four ISO pads (560.00 authoritative, 560.13, 560.17, 761.mp3) re-decoded under keyskip1+keyskip2 on panel-R36 at a sampled offset fraction: %s. See R40-B3-COSPAD-REDECODE." % cons("COSPAD"),
         "not_covered_remove": "keyskip2 / twelve-register decode of the sampled offsets"},
        {"id": "R28-L1-CICADAOS-PADS-DENSE-PAIR", "coverage_add": "R40-B3: R28-L1 stride grids re-included in the offset set and re-decoded under pf_v4_12 + beam_v3 12-register panel with the R28 reductions plus 560.17/761.mp3: %s." % cons("COSPAD"),
         "not_covered_remove": "nine-register-panel-only adjudication of the stride-grid offsets"},
    ]
    cr = []
    if fin["B04"] and fin["KDF"]:
        cr.append({"ceiling_line": "SHA-256-CTR / HMAC-DRBG / AES-CTR / RC4 / ChaCha20 seed lists; PBKDF2 and the 27 tested KDF configs; payload-as-seed",
                   "append_to_coverage": "R40-B3 re-decode of the regenerated lists under pf_v4_12 + beam_v3 keyskip1+keyskip2 on panel-R36: B-04 %s; R16-KDF %s [pins: R40-B3-B04-REDECODE | %d ; R40-B3-R16KDF-REDECODE | %d]" % (cons("B04"), cons("KDF"), fin["B04"]["screened"], fin["KDF"]["screened"]),
                   "replace_in_measured_power": "the English-register-only / keyskip1-only 'excluded at power 1.00' qualifier now has a keyskip1+keyskip2, 12-register re-decode for the regenerated lists (planted EN_MODERN / EN_NOVOWEL / LATIN only: [plants: EN_MODERN / EN_NOVOWEL / LATIN]); the original sweeps keep their legacy conditional",
                   "status_note": "one KDF row (rev, 184-symbol buffer, keyskip2, 6.528 vs actual-N bar 6.342) is flagged-for-oracle by protocol, below the N=1e6 and screened-N bars; see ORACLE-PENDING.md"})
    if fin["R17PAD"]:
        cr.append({"ceiling_line": "Public randomness: blockchain, beacon, archives (English plaintext) and a date-indexed pad", "append_to_coverage": "R40-B3: the regenerated R17-P3 pad list re-decoded under beam_v3 keyskip1+keyskip2 on panel-R36 at a stated sampled offset fraction (%s); P1/P2 pads not regenerated [pin: R40-B3-R17-PUBLIC-PAD-REDECODE | %d]" % (cons("R17PAD"), fin["R17PAD"]["screened"])})
    if fin["COSPAD"]:
        cr.append({"ceiling_line": "The author's own CicadaOS pads and literal pad files as byte-to-symbol reductions", "append_to_coverage": "R40-B3: ISO pads 560.00 auth / 560.13 / 560.17 / 761.mp3 re-decoded with pf_v4_12 + beam_v3 12-register panel, sampled offsets incl. the R28 stride grids (%s) [pin: R40-B3-COSPAD-REDECODE | %d]" % (cons("COSPAD"), fin["COSPAD"]["screened"])})
    json.dump({"$comment": "R40 B3 patches (not applied by the lane); MEASURED-CEILING lines for B-04/R16-KDF/R17-PUBLIC-PAD/CicadaOS pads to refresh with the pin suggestions", "patches": patches, "ceiling_refresh": cr}, open(F("ledger_patches.json"), "w"), indent=1)
    print("wrote RESULTS.md ledger.json ledger_patches.json")


if __name__ == "__main__":
    main()
