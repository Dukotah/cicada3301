"""R47-H2: writes ledger_rows.json from c10_baselines.json + the fixed facts below. Run after the C10 arms."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(HERE, "c10_baselines.json")))
base = {"lane": "round47/H2-harden", "round": "47/H2", "date": "2026-11-24"}


def g(prefix):
    return next(v for k, v in B.items() if k.startswith(prefix))


i, ii, iii = g("i|"), g("ii|"), g("iii|")
iv64, iv512 = g("iv_m64|"), g("iv_m512|")
Bbest = max(ii["pass"], iv64["pass"], iv512["pass"])
fin = max(0.80, Bbest + 0.20)
fin = -(-round(fin * 100) // 5) * 5 / 100
published = fin <= 0.95

rows = [
    dict(base, id="R47-H2-CHECKER-ISOLATION", status="measured", threshold_fixed_in_advance=True,
         hypothesis="Running C8/C9/C10 submissions in an isolated `python -I` child that receives only the granted "
                    "inputs, in os.urandom order, defeats R47-X1's in-process cheats.",
         threshold="Each of R47-X1's four cheats (AUDIT.md §3.4) must fail its checker after the fix (brief, item 1).",
         positive_control="passed",
         control_detail="Before the fix the same cheats printed FINISH LINE MET / NEW REGISTER (R47-X1 out_x1_cheat_*.txt).",
         result="All four fail: C7 Dracula-as-Old-Norse rejected by the label gate (JSD 0.024 to English); C8 frame probe "
                "power 0.000 at L=236; C9 frame cheat C3 7/7 but V-NULL 0/40 (seed 99); C10 old cheat 0/20 (signature) and a "
                "frame-walking cheat for the new signature 0/2 in pytest; a call-order cheat on C8 fails too. 11/11 "
                "challenges/test_heavy_checkers.py pass.",
         coverage="In-process frame/object reading and call-order inference.",
         not_covered=["OS-level inspection of the parent process (command line, memory) by a hostile submission: "
                      "code review remains required for credit",
                      "cross-call state inside one child (e.g. C8 shuffled-null multisets) is not blocked, only unordered"],
         evidence=["challenges/_sandbox.py", "challenges/test_heavy_checkers.py",
                   "liber-primus/analysis/round47/H2-harden/out_cheat_c7.txt", "…/out_cheat_c8.txt",
                   "…/out_cheat_c9.txt", "…/out_cheat_c10.txt"],
         reproduce="bash liber-primus/analysis/round47/H2-harden/run_cheats.sh; python -m pytest challenges/test_heavy_checkers.py -q"),
    dict(base, id="R47-H2-C7-LABEL-GATE", status="measured", threshold_fixed_in_advance=False,
         hypothesis="A GP bigram-profile distance separates an English corpus mislabelled as a new register from real "
                    "other-language corpora.",
         threshold="tau = 0.06 JSD, calibrated on in-repo texts (disclosed in H1 PREREG Addendum 3), not pre-registered.",
         positive_control="passed",
         control_detail="Latin worked example validates (0.122 from English); X1's English-as-Old-Norse fails (0.024).",
         result="15 English texts 0.014-0.049 from the English dev pool; Latin-Latin 0.019, German-German 0.017; every "
                "cross-language pair >= 0.079 (Old English vs English). Gate rejects within 0.06 of English or of a covered "
                "language other than the claimed one.",
         coverage="Mislabelled covered-language text with a GP-greedy-like table.",
         not_covered=["a table tuned to move the profile", "close relatives of English (Middle English, Scots) may be "
                      "flagged legitimately; no Middle English text was available to calibrate"],
         evidence=["challenges/c7_corpus_forge.py", "liber-primus/analysis/round47/H2-harden/RESULTS.md"],
         reproduce="python challenges/c7_corpus_forge.py --self-test"),
    dict(base, id="R47-H2-C9-RESCOPE", status="decision", threshold_fixed_in_advance=True,
         hypothesis="After R47-X1 (V-BACK closable in-house, 32/40), C9 should score only loop variants a backstep "
                    "extension does not represent.",
         threshold="Brief item 4; H1 PREREG Addendum 3.",
         result="V-BACK diagnostic (still reported; Round 48: backstep-aware beam + re-adjudicate beam negatives). C9 scores "
                "V-NULL only (recovery gap; beams already score its key as English, -4.54; crossing changes no detection "
                "negative). Self-test seed 4711: keyskip 12/12, V-NULL 0/12, V-BACK 1/12.",
         evidence=["challenges/c9_rejection_loops.py", "CHALLENGES.md"],
         reproduce="python challenges/c9_rejection_loops.py --self-test"),
    dict(base, id="R47-H2-C10-UNKNOWN-KEY-BASELINES", status="measured", threshold_fixed_in_advance=True,
         hypothesis="With the key unknown (F = 65,536 splitmix64 counter keys) and printed lengths shuffled within "
                    "sentence, the repo's exhaustive decoder recovers U2b plants only with true spaces, and cheap "
                    "compositions of the printed-start ranker with R47-X1's segmentation beam do not reach the finish line.",
         threshold="H1 PREREG Addendum 3: (i) >= 0.95 control; FINISH = max(0.80, best of (ii), (iv m=64), (iv m=512) + 0.20) "
                   "rounded up to 0.05; if > 0.95 C10 is not published as a heavy lift.",
         positive_control="passed" if i["pass"] >= 0.95 else "FAILED",
         control_detail=f"(i) exhaustive with TRUE lengths: {i['k']}/{i['n']}, null FP {i['null_fp']}.",
         result=(f"seed 4710, n=100+100: (ii) printed starts {ii['k']}/{ii['n']} (mean rec {ii['mean_recovery']:.3f}); "
                 f"(iv m=64) {iv64['k']}/{iv64['n']} (true key in top 64: {iv64['true_key_in_top_m']:.2f}, null FP {iv64['null_fp']}); "
                 f"(iv m=512) {iv512['k']}/{iv512['n']} (true key in top 512: {iv512['true_key_in_top_m']:.2f}, null FP {iv512['null_fp']}, "
                 f"{iv512['sec_per_unit']} s/unit under 7-way load); (iii) X1 beam per key: correct key beats all 1,024 sampled "
                 f"wrong keys on {iii['correct_key_beats_all_sampled']:.2f} of 16 units (recovery {iii['correct_key_recovery_mean']:.3f}), "
                 f"{iii['sec_per_key']} s/key, ~{iii['est_sec_per_unit_full_enum']} s/unit for full enumeration. "
                 f"B = {Bbest:.2f}; FINISH = {fin:.2f}; " + ("C10 published as a heavy lift." if published else
                 "FINISH > 0.95: C10 not published as a heavy lift (re-scope to Round 48).")),
         coverage="U2b word-jump, unknown key from a stated 2^16 family, b' within-sentence shuffle, English plaintext.",
         not_covered=["the doublet filter", "other word-indexed constructions (R41 W1-W4, G3 lagged pointers, lexicon rows)",
                      "families larger than 2^16 / clue-derived key families", "non-English plaintext (L7-A)",
                      "(iii) measured against a 1,024-key sample, not the full family"],
         three_conditionals={"key_space": "2^16 splitmix64 counter keys, exhaustively searched by (i)/(ii)",
                             "transition_model": "U2b word jump, no doublet filter", "adjudicator_register": "English"},
         crossing_changes="R46-L1-REOPEN-VERDICTS / R46-L1-R37-U2B-U3-RECHECK: an unknown-key b'-robust sweep for the word-jump class.",
         evidence=["challenges/c10_shuffled_lengths.py", "liber-primus/analysis/round47/H2-harden/c10_baselines.py",
                   "…/c10_baselines.json", "…/out_c10_*.txt"],
         reproduce="python -I liber-primus/analysis/round47/H2-harden/c10_baselines.py --arm i_ii --n 100 --seed 4710 (and --arm iv/iii, see RESULTS)"),
    dict(base, id="R47-H2-C10-V1-KEYED-CROSSING-KEPT", status="recorded", threshold_fixed_in_advance=True,
         hypothesis="R47-X1's crossing of the keyed C10 (Addendum 2) is a finding, not an error to erase.",
         result="Kept: with the key in hand a position-synchronous beam recovers 0.962 / 0.976 (R47-X1-C10-SEGMENTATION-BEAM-CROSSING), "
                "so the (b') recovery loss at known key belongs to the printed-start decoder. The v1 checker is preserved verbatim "
                "(in-process, so not safe for outside submissions) at H2-harden/c10_v1_keyed.py; the H2 baselines add that the "
                f"same beam also finds the correct key against 1,024 sampled wrong keys on 16/16 units.",
         evidence=["liber-primus/analysis/round47/H2-harden/c10_v1_keyed.py", "liber-primus/analysis/round47/X1-redteam/AUDIT.md"],
         reproduce="python liber-primus/analysis/round47/H2-harden/c10_v1_keyed.py liber-primus/analysis/round47/X1-redteam/x1_c10_beam_attack.py --n 500 --seed 4702"),
]
json.dump(rows, open(os.path.join(HERE, "ledger_rows.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
print(f"B={Bbest} FINISH={fin} published={published}")
