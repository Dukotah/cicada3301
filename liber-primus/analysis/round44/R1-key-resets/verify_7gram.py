"""R44/R1 step 1 — verify the repeated ciphertext 7-gram (claimed p27:28 / p54:70) from canon.

Canon = data/krisyotam_runes.txt. '%' page break, '/' line break, '-' word sep, '.' sentence.
The scan runs over the CONCATENATED rune stream (all 57 canon pages) because the claimed second
occurrence sits at the very end of p54 (length 76): offsets 70..75 are p54's last six runes and
the 7th matching rune is the FIRST rune of p55 — a per-page scan is structurally blind to it
(this lane's first run was, and this file documents that correction).
Writes sevengram.json.  Pure python3, no network.
"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp  # noqa: E402

KRIS = os.path.join(LP, "data", "krisyotam_runes.txt")
SECTIONS = [0, 3, 6, 7, 8, 15, 23, 27, 33, 39, 40, 53, 54]  # red-head section map (X0/F1)
N7 = 7


def parse_pages():
    """-> list of 57 canon pages; each = dict(idx, gapsep (separator string between consecutive
    runes), line_of)."""
    txt = open(KRIS, encoding="utf-8").read()
    pages = []
    for seg in txt.split("%"):
        idx, gapsep, line_of = [], [], []
        line, pending = 0, ""
        for ch in seg:
            if ch in gp.RUNE_TO_IDX:
                if idx:
                    gapsep.append(pending)
                pending = ""
                idx.append(gp.RUNE_TO_IDX[ch])
                line_of.append(line)
            else:
                if ch == "/":
                    line += 1
                pending += ch
        if idx:
            pages.append(dict(idx=idx, gapsep=gapsep, line_of=line_of))
    return pages


def main():
    pages = parse_pages()
    assert len(pages) == 57, len(pages)
    full, page_of, off_of, gaps = [], [], [], []
    for pi, pg in enumerate(pages):
        for j, v in enumerate(pg["idx"]):
            if full:
                # separator between previous rune and this one; page join = hard boundary
                gaps.append("%" if j == 0 else pg["gapsep"][j - 1])
            full.append(v)
            page_of.append(pi)
            off_of.append(j)

    def gap_pattern(s):
        return "".join("1" if any(c in "-.&$/%\n" for c in gaps[s + j]) else "0"
                       for j in range(N7 - 1))

    occ = defaultdict(list)
    for s in range(len(full) - N7 + 1):
        occ[tuple(full[s:s + N7])].append(s)
    rep = {k: v for k, v in occ.items() if len(v) > 1}

    total_pos = len(full) - N7 + 1
    exp_pairs = total_pos * (total_pos - 1) / 2.0 * (1.0 / 29.0) ** N7

    out = {"n_pages": len(pages), "total_runes": len(full),
           "unsolved_runes_0_54": sum(len(p["idx"]) for p in pages[:55]),
           "expected_matching_pairs_uniform_iid": exp_pairs,
           "n_repeated_7grams_concatenated": len(rep), "repeats": [],
           "note_first_run": "a per-page scan finds ZERO repeated 7-grams: the p54 occurrence "
                             "crosses the p54->p55 page boundary (p54 len 76, site at 70)."}

    for k, v in sorted(rep.items(), key=lambda kv: -len(kv[1])):
        rec = {"gram_idx": list(k),
               "gram_translit": "".join(gp.IDX_TO_TRANS[i] for i in k),
               "occurrences": []}
        pats = []
        for s in v:
            pi, pj = page_of[s], off_of[s]
            pat = gap_pattern(s)
            pats.append(pat)
            sec_start = max(x for x in SECTIONS if x <= pi)
            sec_off = sum(len(pages[q]["idx"]) for q in range(sec_start, pi)) + pj
            end_pi = page_of[s + N7 - 1]
            rec["occurrences"].append(dict(
                page=pi, pos=pj, page_len=len(pages[pi]["idx"]),
                crosses_into_page=(None if end_pi == pi else end_pi),
                word_gap_pattern=pat, line=pages[pi]["line_of"][pj],
                section_start_page=sec_start, section_offset=sec_off,
                page_is_section_start=pi in SECTIONS))
        rec["word_gap_patterns_identical"] = len(set(pats)) == 1
        out["repeats"].append(rec)

    claimed = [r for r in out["repeats"]
               if {o["page"] for o in r["occurrences"]} == {27, 54}]
    out["claimed_p27_p54"] = claimed
    out["claim_verified"] = bool(
        claimed
        and any(o["page"] == 27 and o["pos"] == 28 for r in claimed for o in r["occurrences"])
        and any(o["page"] == 54 and o["pos"] == 70 for r in claimed for o in r["occurrences"])
        and all(r["word_gap_patterns_identical"] for r in claimed))

    # the anchor sites the sweep consumes (fixed here, read by run_sweep.py)
    if out["claim_verified"]:
        occA = [o for o in claimed[0]["occurrences"] if o["page"] == 27][0]
        occB = [o for o in claimed[0]["occurrences"] if o["page"] == 54][0]
        out["anchor"] = {
            "gram": claimed[0]["gram_translit"],
            "page_mode": {"a_page": 27, "a_pos": occA["pos"], "b_page": 54, "b_pos": occB["pos"],
                          "b_crossing": "7th rune = p55 pos 0 -> key index o+0 under page reset"},
            "section_mode": {"a_secoff": occA["section_offset"], "b_secoff": occB["section_offset"],
                             "note": "p27 and p54 both OPEN red-head sections; p55 continues "
                                     "the p54 section, so the b site is contiguous 70..76"}}

    json.dump(out, open(os.path.join(HERE, "sevengram.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("n_repeated_7grams_concatenated",
                                          "expected_matching_pairs_uniform_iid",
                                          "claim_verified")}, indent=1))
    for r in out["repeats"]:
        print(r["gram_translit"],
              [(o["page"], o["pos"], o["word_gap_pattern"], o["page_is_section_start"],
                o["crosses_into_page"], o["section_offset"]) for o in r["occurrences"]],
              "patterns_identical=%s" % r["word_gap_patterns_identical"])


if __name__ == "__main__":
    main()
