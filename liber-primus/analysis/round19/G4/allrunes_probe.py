"""ROUND 19 / G4, side-deliverable (PREREG.md 8) — is LP2 plausibly `allrunes'-typeset?

Round 18's L1 left NC-5 open: the `allrunes' Type-1 faces are in its font bank as files
but "are custom-encoded (not Unicode-mapped), so matching them requires an unordered
glyph-slot search rather than a codepoint lookup."

This probe checks that claim and, if it is wrong, does the lookup L1 could not do.

METHOD (fixed before running):
  1. Read every allrunes .pfb in L1's bank with fontTools, take each glyph's INK
     BOUNDING BOX from the Type-1 charstrings.  This is the same quantity L1 measured
     off the page images (`runes_observed_meta.json`: shape = [height, width] with all
     heights normalised to 114 px).
  2. Map runes to glyphs by NAME (f, u, eth, o, r, c, g, w, h, n, i, j, p, x, s, t, b,
     e, m, l, eng, oe, d, a, ae, y) — 26 of the 29 futhorc runes are unambiguous.
     EO / EA / IA are dropped rather than guessed.
  3. Normalise each face's widths to L1's height scale, then fit ONE horizontal scale
     factor `s` per face by least squares against L1's observed widths.  A face that
     the author used *condensed* would fit with s < 1 and a small residual; L1's F5
     says the observed face differs from every stock face "chiefly in proportion".
  4. CONTROL (order-destroying null): refit against 200 random permutations of the
     observed width vector.  If the real assignment is not clearly better than the
     permuted ones, the fit is about overall spread, not about which rune is which,
     and the result is reported as uninformative.

THIS IS A SCREEN, NOT A VERDICT.  218 faces of one design family will all fit somewhat;
what the output supports is at most "consistent with / not consistent with", and it is
reported that way in RESULTS.md 6.

    python3 allrunes_probe.py
"""
from __future__ import annotations

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
L1 = os.path.abspath(os.path.join(HERE, "..", "..", "round18", "L1-toolchain"))
PFB = os.path.join(L1, "fonts", "allrunes", "allrunes", "type1", "pfb")
OBS = os.path.join(L1, "runes_observed_meta.json")

# transliteration (L1's labels) -> allrunes Type-1 charstring name
NAME = {
    "F": "f", "U": "u", "TH": "eth", "O": "o", "R": "r", "C": "c", "G": "g",
    "W": "w", "H": "h", "N": "n", "I": "i", "J": "j", "P": "p", "X": "x",
    "S": "s", "T": "t", "B": "b", "E": "e", "M": "m", "L": "l", "NG": "eng",
    "OE": "oe", "D": "d", "A": "a", "AE": "ae", "Y": "y",
    # EO / EA / IA deliberately omitted: no unambiguous charstring name
}
H_OBS = 114.0          # L1 normalised every observed glyph to this pixel height


def observed_widths():
    meta = json.load(open(OBS, encoding="utf-8"))
    return {v["translit"]: float(v["shape"][1]) for v in meta.values()}


def face_widths(path):
    from fontTools.t1Lib import T1Font
    from fontTools.pens.boundsPen import BoundsPen
    f = T1Font(path)
    f.parse()
    gs = f.getGlyphSet()
    cs = f.font["CharStrings"]
    box = {}
    for n in cs:
        if n == ".notdef":
            continue
        bp = BoundsPen(gs)
        try:
            gs[n].draw(bp)
        except Exception:
            continue
        if bp.bounds:
            box[n] = bp.bounds
    return box


def profile(box):
    """26 ink widths, scaled so the face's median glyph height equals L1's 114 px."""
    need = [NAME[t] for t in NAME if NAME[t] in box]
    if len(need) < len(NAME):
        return None
    hs = sorted((box[n][3] - box[n][1]) for n in need)
    H = hs[len(hs) // 2]
    if H <= 0:
        return None
    return {t: (box[NAME[t]][2] - box[NAME[t]][0]) * H_OBS / H for t in NAME}


def fit(pred, obs, keys):
    """Least-squares horizontal scale s minimising sum (s*pred - obs)^2, + residual."""
    num = sum(pred[k] * obs[k] for k in keys)
    den = sum(pred[k] * pred[k] for k in keys)
    if den == 0:
        return None, None
    s = num / den
    rss = sum((s * pred[k] - obs[k]) ** 2 for k in keys)
    rms = (rss / len(keys)) ** 0.5
    return s, rms


def main():
    obs = observed_widths()
    keys = [t for t in NAME if t in obs]
    files = sorted(f for f in os.listdir(PFB) if f.endswith(".pfb"))
    rows, skipped = [], 0
    for fn in files:
        box = face_widths(os.path.join(PFB, fn))
        pred = profile(box)
        if pred is None:
            skipped += 1
            continue
        s, rms = fit(pred, obs, keys)
        rows.append({"face": fn[:-4], "scale": round(s, 4), "rms_px": round(rms, 3)})
    rows.sort(key=lambda r: r["rms_px"])

    # order-destroying control on the best face
    best = rows[0]
    box = face_widths(os.path.join(PFB, best["face"] + ".pfb"))
    pred = profile(box)
    rng = random.Random(3301)
    null = []
    vals = [obs[k] for k in keys]
    for _ in range(200):
        v = vals[:]
        rng.shuffle(v)
        perm = dict(zip(keys, v))
        _, r = fit(pred, perm, keys)
        null.append(r)
    null.sort()

    res = {
        "lane": "round19/G4",
        "probe": "allrunes ink-width profile vs LP2 observed (PREREG 8) — SCREEN, NOT A VERDICT",
        "nc5_claim_under_test": ("round18/L1 NC-5: 'the allrunes Type-1 faces are custom-encoded "
                                 "(not Unicode-mapped), so matching them requires an unordered "
                                 "glyph-slot search rather than a codepoint lookup'"),
        "nc5_finding": ("FALSE as stated for these files. The .pfb charstrings carry ordinary "
                        "Adobe glyph names that ARE the transliteration letters — f, u, eth, o, "
                        "r, c, g, w, h, n, i, j, p, x, s, t, b, e, m, l, eng, oe, d, a, ae, y — "
                        "so 26 of the 29 futhorc runes are a direct name lookup and no unordered "
                        "slot search is needed. Only EO / EA / IA lack an unambiguous name."),
        "n_faces": len(rows), "n_skipped": skipped, "n_runes_compared": len(keys),
        "runes_compared": keys,
        "top10": rows[:10],
        "worst3": rows[-3:],
        "scale_range": [min(r["scale"] for r in rows), max(r["scale"] for r in rows)],
        "permutation_control": {
            "face": best["face"], "real_rms_px": best["rms_px"],
            "null_n": len(null), "null_min_rms_px": round(null[0], 3),
            "null_median_rms_px": round(null[len(null) // 2], 3),
            "p_value_le_real": round(sum(1 for r in null if r <= best["rms_px"]) / len(null), 4),
        },
    }
    ctl = res["permutation_control"]
    res["verdict"] = (
        "INFORMATIVE" if ctl["p_value_le_real"] <= 0.05 else "UNINFORMATIVE"
    )
    out = os.path.join(HERE, "allrunes_probe.json")
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    print(json.dumps(res, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
