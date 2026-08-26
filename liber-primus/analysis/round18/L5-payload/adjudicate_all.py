"""L5 / A-04 - adjudicate ALL 11 conflict cells, not only the 6 pre-registered contested ones.

Motivation (this is a coverage extension, not a moved goalpost). The 6 pre-registered cells
are the ones where witnesses A and B agree and only scream314's decimal column dissents.
The other 5 are token-SPLIT cells, where canonicalize.py used that same decimal column as
the tie-breaker. If the decimal column turns out to be an unreliable witness on the 6, its
authority over the other 5 is exactly as questionable -- so the same validated instrument
is turned on all 11 and the outcome is reported either way.

Emits adjudication.json and payload_resolved.json.

    python3 adjudicate_all.py
"""
import json
import os

import numpy as np

import grid
import glyphmatch as gm
import pixelmatch as pm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PP = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51")
ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx"
CONTESTED = [25, 175, 182, 199, 215, 237]
CONFLICT = [25, 45, 50, 165, 172, 175, 182, 199, 215, 237, 246]

# three-pass visual reads recorded by the reader BEFORE this script was run.
# Pass A = scale 10/pad 16 ascending, B = scale 7/pad 4 descending,
# C = scale 14/pad 24 in i%7 order. Only the 6 pre-registered cells were read visually;
# the other 5 are adjudicated by the pixel instrument alone and are labelled as such.
VISUAL = {
    25:  ("3I", "3I", "3I"),
    175: ("0I", "0I", "0I"),
    182: ("2l", "2l", "2l"),
    199: ("0l", "0l", "0l"),
    215: ("1O", "1O", "1O"),
    237: ("0W", "0W", "0W"),
    45:  ("1l", "1l", "1l"),
    50:  ("0l", "0l", "0l"),
    246: ("3I", "3I", "3I"),
}


def tok_to_byte(t):
    return ALPHA.index(t[0]) * 60 + ALPHA.index(t[1])


def main():
    canon = open(os.path.join(PP, "canon_256.bin"), "rb").read()
    decpref = open(os.path.join(PP, "canon_256_decpref.bin"), "rb").read()
    G = pm.extract()

    uncontested = [i for i in range(256) if i not in CONFLICT and G[i] is not None]
    byclass, bydigit = {}, {}
    for i in uncontested:
        byclass.setdefault(ALPHA[canon[i] % 60], []).append(i)
        bydigit.setdefault(str(canon[i] // 60), []).append(i)

    out = {}
    for i in CONFLICT:
        if G[i] is None:
            out[i] = {"error": "cell did not segment into exactly 2 glyphs"}
            continue
        rec = {}
        for what, table, key in (("digit", bydigit, "d"), ("symbol", byclass, "s")):
            sc = sorted(((max(pm.best_iou(G[i][key], G[k][key]) for k in idxs), c)
                         for c, idxs in table.items()), reverse=True)
            rec[what] = {"best": sc[0][1], "best_iou": round(sc[0][0], 4),
                         "margin": round(sc[0][0] - sc[1][0], 4),
                         "top": [{"cls": c, "iou": round(v, 4)} for v, c in sc[:5]]}
        tok = rec["digit"]["best"] + rec["symbol"]["best"]
        rec["token"] = tok
        rec["byte"] = tok_to_byte(tok)
        rec["canon_byte"] = canon[i]
        rec["decpref_byte"] = decpref[i]
        rec["agrees_with_canon"] = rec["byte"] == canon[i]
        rec["agrees_with_decimal"] = rec["byte"] == decpref[i]
        rec["class"] = ("pre-registered contested (tokens agree, decimal dissents)"
                        if i in CONTESTED else
                        "token-split (canonicalize.py used the decimal column as tie-breaker)")
        if i in VISUAL:
            rec["visual_passes"] = list(VISUAL[i])
            rec["visual_concordant"] = len(set(VISUAL[i])) == 1
            rec["visual_matches_pixel"] = VISUAL[i][0] == tok
        out[i] = rec

    print("%-5s %-42s %-6s %-6s %-6s %-8s %-7s" %
          ("idx", "class", "token", "byte", "canon", "decimal", "iou(sym)"))
    for i in CONFLICT:
        r = out[i]
        if "error" in r:
            print("%-5d %s" % (i, r["error"]))
            continue
        print("%-5d %-42s %-6s %-6d %-6d %-8d %-7.4f  %s" %
              (i, r["class"][:42], r["token"], r["byte"], r["canon_byte"],
               r["decpref_byte"], r["symbol"]["best_iou"],
               "= canon" if r["agrees_with_canon"] else "*** DIFFERS FROM CANON ***"))

    changed = [i for i in CONFLICT if "error" not in out[i] and not out[i]["agrees_with_canon"]]
    dec_ok = sum(1 for i in CONFLICT if "error" not in out[i] and out[i]["agrees_with_decimal"])
    print("\ncells where the image disagrees with canon_256.bin: %s" % (changed or "none"))
    print("scream314 decimal column agrees with the image on %d/%d conflict cells"
          % (dec_ok, sum(1 for i in CONFLICT if "error" not in out[i])))

    resolved = bytearray(canon)
    for i in changed:
        resolved[i] = out[i]["byte"]
    resolved = bytes(resolved)

    with open(os.path.join(HERE, "adjudication.json"), "w") as f:
        json.dump({str(k): v for k, v in out.items()}, f, indent=1)

    import hashlib
    payload = {
        "instrument": "native-resolution nearest-exemplar glyph match (pixelmatch.py) "
                      "+ 3 independent visual passes (visualpass.py)",
        "calibration": {
            "visual_blind_40_cell": "40/40 exact-token (calibration.json), "
                                    "case-ambiguous subset 22/22",
            "pixel_leave_one_out_symbol": "236/237 = 99.58%, case-ambiguous subset 74/74 = 100%",
            "pixel_leave_one_out_digit": "242/242 = 100%",
            "gate": "PREREG A.3 gate was >=38/40; measured 40/40 -- PASS",
        },
        "sha256_resolved": hashlib.sha256(resolved).hexdigest(),
        "sha256_canon_256_bin": hashlib.sha256(canon).hexdigest(),
        "identical_to_canon_256_bin": resolved == canon,
        "bytes_changed": changed,
        "cells": {str(k): v for k, v in out.items()},
        "hex": resolved.hex(),
    }
    with open(os.path.join(HERE, "payload_resolved.json"), "w") as f:
        json.dump(payload, f, indent=1)
    with open(os.path.join(HERE, "payload_resolved.bin"), "wb") as f:
        f.write(resolved)
    print("\nwrote adjudication.json, payload_resolved.json, payload_resolved.bin")
    print("resolved payload sha256 = %s" % payload["sha256_resolved"])
    print("identical to canon_256.bin: %s" % payload["identical_to_canon_256_bin"])


if __name__ == "__main__":
    main()
