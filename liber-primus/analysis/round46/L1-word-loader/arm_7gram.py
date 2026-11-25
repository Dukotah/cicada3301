"""R46-L1 arm 7-gram (R44-W2A2-7GRAM-DIFFPLAIN): (1) the two sites' printed gap shapes under words.py vs the legacy
'%'-splitting rule; (2) on plants over LP2's real layout, P(true segmentation of a 7-rune window is 3|3|head |
the print says 3|3|head), regimes a / b / bp, loaders L (words.py) and O (legacy: '-' '.' '%' break).
python -I arm_7gram.py -> sevengram.json"""
import os, sys, json, random
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import l1lib as G
import words as W
SITES = {"A": 6555, "B": 12950}                  # round44/W2-A2-7gram/PREREG.md s1 (global rune index of site start)


def starts_from_lens(lens):
    s, t = set(), 0
    for l in lens: s.add(t); t += l
    return s


def shape(starts, i):
    return "".join("1" if (i + j) in starts else "0" for j in range(1, 7)), i in starts


def legacy_starts(text):
    """word starts under '-' '.' '%' breaking (mapcommon / skeleton rule)."""
    s = set(); pos = 0; prev_break = True
    for ch in text:
        if ch in W.IDX:
            if prev_break: s.add(pos)
            prev_break = False; pos += 1
        elif ch in "-.%" or ch in "&$§" or ch.isdigit():
            prev_break = True
    return s


def main():
    txt = open(W.KRIS, encoding="utf-8").read()
    A = W.lp2_all()
    newS = set(w["start"] for w in A.words); oldS = legacy_starts(txt)
    out = {"sites": {}}
    for k, i in SITES.items():
        out["sites"][k] = {"global_start": i, "words_py_gap_pattern": shape(newS, i)[0], "words_py_starts_word": shape(newS, i)[1],
                           "legacy_gap_pattern": shape(oldS, i)[0], "legacy_starts_word": shape(oldS, i)[1],
                           "page_break_inside": [j for j in range(1, 7) if (i + j) in set(A.page_starts)],
                           "line_break_inside": [j for j in range(1, 7) if (i + j) in set(A.line_starts)]}
    cells = {}
    for regime in ("a", "b", "bp"):
        num = {"L": 0, "O": 0}; den = {"L": 0, "O": 0}
        for rep in range(10):
            P = G.make_plant(regime, random.Random(46700 + 10 * ("a", "b", "bp").index(regime) + rep))
            trueS = starts_from_lens(P.true_lens)
            text = W.render(G.regroup(P.flat, P.printed_lens), P.sent_ends, G.LINE_STARTS, G.PAGE_STARTS)
            prS = {"L": set(w["start"] for w in W.parse(text).words), "O": legacy_starts(text)}
            for i in range(W.N_LP2 - 7):
                for ld in ("L", "O"):
                    pat, st = shape(prS[ld], i)
                    if st and pat == "001001":
                        den[ld] += 1; tp, ts = shape(trueS, i); num[ld] += int(ts and tp == "001001")
        for ld in ("L", "O"):
            cells["%s|%s" % (regime, ld)] = {"printed_331_windows": den[ld], "true_331": num[ld], "precision": round(num[ld] / den[ld], 4)}
    out["shape_precision"] = cells
    json.dump(out, open(os.path.join(HERE, "sevengram.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
