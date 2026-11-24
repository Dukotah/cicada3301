"""R45 I1 arm_7gram: R44-W2A2-7GRAM-DIFFPLAIN models each site's plaintext as (3-rune word, 3-rune word, word head),
read off the PRINTED gaps (pattern 001001).  Under H-decoy the true plaintext segmentation of a 7-rune window is not
given by the print.  Measured here: in held-out English runes (pride, moby; panel EN mapping), the fraction of 7-rune
windows whose TRUE segmentation is exactly 3|3|head (a word boundary after rune 3 and after rune 6, word starts at 0,
no other boundary inside).  That fraction is the coverage the lane retains if the printed gaps carry no information.
python -I arm_7gram.py -> out_7gram.json"""
import os, sys, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common45 as G
OUT = os.path.join(HERE, "out_7gram.json")


def frac(words):
    starts = set(); pos = 0
    for w in words:
        starts.add(pos); pos += len(w)
    n = pos - 7; k = 0; k_any_start = 0
    for i in range(n):
        inside = [j for j in range(1, 7) if (i + j) in starts]
        if i in starts and inside == [3, 6]:
            k += 1
        if inside == [3, 6]:
            k_any_start += 1
    return {"windows": n, "shape_331_word_aligned": k, "frac": k / n, "shape_331_any_start": k_any_start, "frac_any_start": k_any_start / n}


def run():
    res = {"date": time.strftime("%Y-%m-%dT%H:%M:%S")}
    for fn in ("pride.txt", "moby.txt"):
        res[fn] = frac(G.text_words(fn))
    # the same fraction read off LP2's own printed gaps (sanity: what the print claims)
    w = [[0] * l for p in G.LP2_PAGES for l in p]
    res["LP2_printed"] = frac(w)
    json.dump(res, open(OUT, "w"), indent=1); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    run()
