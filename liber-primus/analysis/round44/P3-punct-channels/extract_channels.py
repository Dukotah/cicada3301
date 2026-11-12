"""R44/P3 step 1 — extraction glue + witness cross-check (PREREG.md protocol).

Parses the relikd witness files (source of truth for positions), re-verifies the rune
stream against the krisyotam canon, extracts the quote spans / separator-identity stream /
apostrophe+numeral positions, and cross-checks every quote span against scream314_lp.md.
Writes channels.json. The SAME parse function is used by plants.py on synthetic witness
files (the R42 X1 own-glue rule).

Kill rule (PREREG Q5): any witness disagreement that leaves a span or the rune stream
undetermined -> {"killed": true, reason} and no downstream decode may run.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp  # noqa

RELIKD_ORDER = ["p0-2", "p3-7", "p8-14", "p15-22", "p23-26", "p27-32",
                "p33-39", "p40-53", "p54-55"]
SEPS3 = "⁘⁚⁜"   # ⁘ ⁚ ⁜
WORD = "•"                # •
F2B_SPANS = [(1659, 1677), (5459, 5478), (9715, 9727), (9811, 9869),
             (10211, 10279), (10279, 10439), (12522, 12592)]
F2B_APOS = [1110, 5138, 8515, 10089]


def parse_witness(text):
    """Walk a relikd-format text once; return the channel structures, all positioned by
    rune offset (number of runes strictly before the token)."""
    runes = []          # rune indices
    toks = []           # (rune_offset, char) for every non-rune mark we care about
    quote_marks, apostrophes, numerals = [], [], []
    for ch in text:
        if gp.is_rune(ch):
            runes.append(gp.RUNE_TO_IDX[ch])
        elif ch == '"':
            quote_marks.append(len(runes))
            toks.append((len(runes), ch))
        elif ch == "'":
            apostrophes.append(len(runes))
            toks.append((len(runes), ch))
        elif ch in SEPS3 or ch == WORD:
            toks.append((len(runes), ch))
        elif ch.isdigit():
            numerals.append((len(runes), ch))
    if len(quote_marks) % 2:
        raise ValueError("odd number of quote marks: %d" % len(quote_marks))
    spans = [(quote_marks[i], quote_marks[i + 1])
             for i in range(0, len(quote_marks), 2)]
    return {"runes": runes, "toks": toks, "spans": spans,
            "apostrophes": apostrophes, "numerals": numerals}


def sep_streams(parsed):
    """The separator-identity streams (PREREG reading b). Returns
    (sep3_incl, sep3_excl_grid, sep4) as symbol strings over the raw glyphs."""
    sep3 = [(off, ch) for off, ch in parsed["toks"] if ch in SEPS3]
    sep4 = [ch for _, ch in parsed["toks"] if ch in SEPS3 or ch == WORD]
    # grid-row dots: the 4 ⁘ terminating the p15 number-grid rows -- they sit at the SAME
    # rune offset as each other and as the grid (zero runes between them: the grid has no
    # runes), i.e. consecutive sep3 tokens sharing one rune offset with >=4 in the clump
    # AND adjacent digit tokens.  Identified instead directly: ⁘ tokens whose rune offset
    # equals the offset of >=8 numeral digits (the grid rows).
    grid_offsets = {}
    for off, _d in parsed["numerals"]:
        grid_offsets[off] = grid_offsets.get(off, 0) + 1
    excl = [ch for off, ch in sep3
            if not (ch == "⁘" and grid_offsets.get(off, 0) >= 8)]
    return "".join(ch for _, ch in sep3), "".join(excl), "".join(sep4)


def main():
    rel_text = "".join(open(os.path.join(LP, "data", "relikd", n + ".txt"),
                            encoding="utf-8").read() for n in RELIKD_ORDER)
    parsed = parse_witness(rel_text)
    out = {"killed": False, "checks": {}}

    # --- check 1: relikd rune stream == krisyotam canon prefix -----------------------
    kris = gp.runes_to_indices(open(os.path.join(LP, "data", "krisyotam_runes.txt"),
                                    encoding="utf-8").read())
    n = len(parsed["runes"])
    ok1 = (n == 12956 and kris[:n] == parsed["runes"])
    out["checks"]["relikd_eq_kris"] = {"relikd_n": n, "kris_n": len(kris), "match": ok1}
    if not ok1:
        out.update(killed=True, reason="relikd rune stream != krisyotam canon prefix")

    # --- check 2: spans match the F2b table ------------------------------------------
    out["checks"]["spans_eq_f2b"] = {"extracted": parsed["spans"],
                                     "f2b": F2B_SPANS,
                                     "match": parsed["spans"] == F2B_SPANS}
    if parsed["spans"] != F2B_SPANS:
        out.update(killed=True, reason="extracted spans differ from F2b table")

    # --- check 3: cross-witness: every span's rune sequence quoted in scream314 ------
    scream = open(os.path.join(LP, "data", "scream314_lp.md"), encoding="utf-8").read()
    # reduce scream314 to its rune+quote skeleton (runes and " only, in order)
    skel = "".join(ch for ch in scream if gp.is_rune(ch) or ch == '"')
    span_checks = []
    for (a, b) in parsed["spans"]:
        seq = gp.indices_to_runes(parsed["runes"][a:b])
        quoted = ('"' + seq + '"') in skel
        present = seq in skel
        span_checks.append({"span": [a, b], "len": b - a,
                            "quoted_in_scream314": quoted, "present": present})
    ok3 = all(c["quoted_in_scream314"] for c in span_checks)
    out["checks"]["scream314_spans"] = {"per_span": span_checks, "all_quoted": ok3}
    if not ok3:
        out.update(killed=True, reason="span not quoted verbatim in scream314")

    # --- check 4: apostrophes --------------------------------------------------------
    out["checks"]["apostrophes"] = {"extracted": parsed["apostrophes"],
                                    "f2b": F2B_APOS,
                                    "match": parsed["apostrophes"] == F2B_APOS}
    if parsed["apostrophes"] != F2B_APOS:
        out.update(killed=True, reason="apostrophe positions differ from F2b")

    # --- channels --------------------------------------------------------------------
    s3i, s3x, s4 = sep_streams(parsed)
    out["channels"] = {
        "spans": [{"start": a, "end": b,
                   "runes": parsed["runes"][a:b]} for a, b in parsed["spans"]],
        "concat_runes": sum((parsed["runes"][a:b] for a, b in parsed["spans"]), []),
        "sep3_incl": s3i, "sep3_excl": s3x, "sep4": s4,
        "sep3_counts": {c: s3i.count(c) for c in SEPS3},
        "sep4_len": len(s4),
        "apostrophes": parsed["apostrophes"],
        "numerals": parsed["numerals"],
    }
    out["checks"]["sep_counts"] = {
        "sep3_incl": len(s3i), "sep3_excl": len(s3x), "sep4": len(s4),
        "expected": {"sep3_incl": 180, "sep3_excl": 176, "sep4": 2911}}

    json.dump(out, open(os.path.join(HERE, "channels.json"), "w"), indent=1)
    print(json.dumps({k: out["checks"][k] if k != "sep_counts" else out["checks"][k]
                      for k in out["checks"]}, indent=1, default=str)[:3000])
    print("KILLED:", out["killed"], out.get("reason", ""))


if __name__ == "__main__":
    main()
