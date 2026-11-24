"""R45 I1 inventory: (1) grep the standing instruments' source for word-boundary consumption; (2) grep every LEDGER.json
row; (3) attach the hand classification below (A conditional / B printed-structure-as-channel / C solved-page true
spaces / D space-blind, in-order plants).  Every classified id is asserted to exist.  python -I inventory.py -> inventory.json"""
import os, sys, re, io, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "inventory.json")

INSTRUMENTS = {
    "beam_v3": "analysis/round33/I1-register-aware-beam/beam_v3.py",
    "beam_v2 (enciphers, recovery)": "analysis/round32/I1-skipbytwo-decoder/beam_v2.py",
    "pf_v4": "analysis/round35/I1-skip-tolerant-screen/pf_v4.py",
    "pf_v4_12": "analysis/round37/I2-pfv4-12reg/pf_v4_12.py",
    "panel adjudicate": "analysis/round32/I2-multiregister-readjudication/adjudicate.py",
    "bars_v3": "analysis/round34/I1-v3-null/bars_v3.py",
    "panel build (R36)": "analysis/round36/I1-new-registers/build_models_r36.py",
    "verify_solution.py (oracle)": "verify_solution.py",
    "HUMAN-ORACLE.md": "HUMAN-ORACLE.md",
    "tests/validate.py (trust anchor)": "tests/validate.py",
}
PAT = re.compile(r"word|space|separator|boundar|'-'|\"-\"|split\(", re.I)

# hand classification (read from each row's hypothesis/coverage/control and, where noted, the lane code)
CLASS = {
    # A: negative conditional on printed spaces = plaintext word boundaries in order
    "C-01": ("A", "SKELETON word-length plaintext identification (Round 8, 51 texts / 8.2M words) aligns LP2 printed lengths to corpus lengths", "arm_skeleton"),
    "R37-C1-U2-LP1-NUMBER-SCHEDULES": ("A", "U2b pointer jumps applied at ciphertext word boundaries (encipherer assumes plaintext word lengths = cipher word lengths); U2a is space-blind", "arm_wordsched U2a/U2b"),
    "R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION": ("A", "per-word shift / key advance at each cleartext word boundary, word index/offset/length from printed words", "arm_wordsched U3"),
    "R38-C1-SEMANTIC-WORDNET": ("A", "per-cipher-word direction d_k (same lens-indexed A1/A2/A3 form as U3, round38/C1-semantic-road/enciphers.py)", "inherits U3 (not separately run)"),
    "R38-C1-SEMANTIC-FREQRANK": ("A", "as R38-C1-SEMANTIC-WORDNET", "inherits U3"),
    "R39-C1-SENSE-SIMILARITY": ("A", "per-cipher-word direction, same U3 form", "inherits U3"),
    "R38-C2-G3-LAGGED-POINTERS": ("A", "pointer from previous cipher word / decoded word in the U3 rule", "inherits U3"),
    "R41-C1-R14-WORDSUM-SELFKEY": ("A", "word gematria sums of printed words key the next word (W1-W4); W5 per-rune autokey is space-blind", "arm_wordsched R14"),
    "R44-W2A2-7GRAM-DIFFPLAIN": ("A", "site plaintext modelled as (3-rune word, 3-rune word, head) from the printed 001001 gap pattern", "arm_7gram"),
    "R40-C1-INCONCLUSIVE-R31": ("A", "R10b B3 page-local crib readouts placed at printed word positions (inconclusive already)", "not run (inconclusive row)"),
    # B: the printed structure itself is the channel read -> not conditional; MORE relevant under H-decoy
    "C-02": ("B", "ciphertext word/line initials+finals as a forced channel", None),
    "R10-L2-MAP": ("B", "ciphertext word structure (initials, sums, lengths, pointers) read as message", None),
    "R10-L3-ROAD": ("B", "ciphertext word gematria sums as marks/symbols/pointers", None),
    "R37-C3-U5-L2-MAP": ("B", "R10 L2 streams re-scored in 12 registers", None),
    "R37-C3-U5-L3-ROAD": ("B", "R10 L3 word-sum streams re-scored", None),
    "R40-C1-R04-M4-LP1-POINTER": ("B", "LP2 printed word numbers/lengths as pointers into LP1 word list", None),
    "B-12": ("B", "per-page word counts / line fill as data channel", None),
    "R11-S2-NUMBER-CHANNEL": ("B", "separator run-lengths as channel", None),
    "R37-C3-U6A-S2": ("B", "separator run-lengths mod 29", None),
    "R44-P3-SEPARATOR-IDENTITY": ("B", "separator identity stream as channel", None),
    "R44-P3-QUOTESPAN-SELECTION": ("B", "quote-delimited spans (punctuation layer, not word breaks) as selection", None),
    "R44-P3-QUOTESPAN-CRIB-DERIVED": ("B", "cribs slid over ALL alignments inside quote spans (no word-position constraint); depends on quote marks, not word breaks", None),
    # C: true spaces of SOLVED pages only (measured true: solved-LP MI z=+7.4)
    "R22-A-SELFEMBEDDED-READ": ("C", "selections of the solved plaintext", None),
    "R23-A2-LINE-ACROSTIC": ("C", "word/line acrostics of SOLVED pages with true spacing", None),
    "R40-C1-R28-R23A2-LINE-ACROSTIC": ("C", "re-score of R23-A2", None),
    "R37-C2-U7-BOOK-CODE": ("C", "indices into LP1 plaintext words", None),
    "R37-C2-U7-BOOK-CODE-W": ("C", "whole LP1 word retrieval (row itself notes it needs a word-order statistic)", None),
    "R44-W2A2-P55-CRIB-SWEEP": ("C", "1-rune crib from solved p55", None),
    # D: space-blind instruments whose plants are in-order prose (affected only by H-shuffle)
    "R33-I1-REGISTER-AWARE-BEAM": ("D", "beam_v3 power envelope: plants = contiguous held-out prose (no spaces consumed)", "arm_beam"),
    "L7-B-BEAM-ENVELOPE": ("D", "beam transition envelope, English plaintext held fixed", "arm_beam"),
    "R41-I1-NULL-REFIT-SURVIVOR12": ("D", "bars from wrong-key decodes; plants in-order prose", "arm_beam"),
    "R44-R1-RESET-SWEEP": ("D", "key resets at page/LINE/section boundaries (line breaks, not word breaks); sentence '&' resets listed not_covered", "arm_beam (rune stream); line layer not audited here"),
}


def main():
    L = json.load(io.open(os.path.join(LP, "LEDGER.json"), encoding="utf-8"))
    E = {e["id"]: e for e in L["entries"]}
    for k in CLASS:
        assert k in E, k
    inst = {}
    for name, rel in INSTRUMENTS.items():
        lines = open(os.path.join(LP, rel), encoding="utf-8", errors="ignore").read().split("\n")
        hits = [(i + 1, l.strip()[:140]) for i, l in enumerate(lines) if PAT.search(l)]
        inst[name] = {"path": rel, "n_hits": len(hits), "hits": hits[:40]}
    rx = re.compile(r"word[- ]?(length|len|boundar|break|sum|initial|start|position|crib|count|pattern|shape)|SKELETON|"
                    r"printed (space|word)|crib|wordlength|quote[- ]span|acrostic|separator|segmentation", re.I)
    grep = [e["id"] for e in L["entries"] if rx.search(json.dumps(e, ensure_ascii=False))]
    out = {"n_ledger_rows": len(L["entries"]), "n_grep_hits": len(grep), "grep_hits": grep,
           "classified": {k: {"class": v[0], "how": v[1], "measured_by": v[2], "status": E[k].get("status")} for k, v in CLASS.items()},
           "grep_hits_unclassified_reason": "remaining grep hits mention words/cribs/separators incidentally (generator seeds, "
           "string literals, interrupter bookkeeping, separator transcription audits) and consume no word boundary of LP2",
           "instruments": inst}
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(len(grep), "grep hits;", {c: sum(1 for v in CLASS.values() if v[0] == c) for c in "ABCD"})
    for n, v in inst.items():
        print(n, v["n_hits"])


if __name__ == "__main__":
    main()
