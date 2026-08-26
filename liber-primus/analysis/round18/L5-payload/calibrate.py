"""L5 / A-04 — score the blind calibration reads against canon_256.bin.

The 40 indices are the pre-registered seeded sample (montage.calib_sample()).
READS below were written down from the max-zoom crops BEFORE this script was run and
before canon_256.bin was consulted at those positions.

Pre-registered gate: >= 38/40 (95%) exact-token agreement.
"""
import json
import os

import montage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CANON = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51", "canon_256.bin")

# --- the blind reads (visual, max-zoom, recorded before scoring) -------------
READS = {
    12: "47", 14: "33", 16: "21", 20: "1g",
    31: "2D", 42: "0S", 46: "3J", 49: "0G",
    52: "1Q", 58: "2Q", 60: "1k", 66: "0P",
    67: "3C", 78: "0k", 100: "1N", 103: "3Q",
    104: "22", 108: "0E", 110: "0W", 113: "2N",
    119: "34", 121: "3v", 125: "0K", 129: "2x",
    137: "29", 154: "0E", 160: "3r", 171: "0s",
    176: "3t", 183: "1L", 195: "1T", 200: "1o",
    202: "3T", 205: "1G", 212: "1A", 214: "4B",
    223: "2V", 232: "1k", 245: "0u", 255: "1K",
}

AMBIG = set("IilLOo0WwSsKk1")


def digit_val(c):
    if c.isdigit():
        return ord(c) - 48
    if "A" <= c <= "Z":
        return ord(c) - 65 + 10
    if "a" <= c <= "x":
        return ord(c) - 97 + 36
    raise ValueError(c)


def tok_to_byte(t):
    return digit_val(t[0]) * 60 + digit_val(t[1])


def byte_to_tok(b):
    alpha = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx"
    return alpha[b // 60] + alpha[b % 60]


def main():
    canon = open(CANON, "rb").read()
    sample = montage.calib_sample()
    assert sorted(READS) == sample, "READS keys != pre-registered sample"

    ok = 0
    amb_tot = amb_ok = 0
    misses = []
    for i in sample:
        got = READS[i]
        want = byte_to_tok(canon[i])
        hit = got == want
        ok += hit
        if set(want) & AMBIG:
            amb_tot += 1
            amb_ok += hit
        if not hit:
            misses.append((i, got, tok_to_byte(got), want, canon[i]))

    n = len(sample)
    print(f"CALIBRATION  overall: {ok}/{n} = {100*ok/n:.1f}% exact-token")
    print(f"             case-ambiguous-class cells: {amb_ok}/{amb_tot}"
          f" = {100*amb_ok/amb_tot:.1f}%   (glyph classes {sorted(AMBIG)})")
    for m in misses:
        print(f"   MISS idx {m[0]:3d}: read {m[1]}={m[2]}  canon {m[3]}={m[4]}")
    gate = ok >= 38
    print(f"\nPRE-REGISTERED GATE (>=38/40): {'PASS' if gate else 'FAIL'}")

    out = {
        "sample": sample,
        "reads": READS,
        "canon_tokens": {str(i): byte_to_tok(canon[i]) for i in sample},
        "overall_correct": ok,
        "overall_n": n,
        "overall_accuracy": ok / n,
        "ambiguous_class_correct": amb_ok,
        "ambiguous_class_n": amb_tot,
        "ambiguous_class_accuracy": amb_ok / amb_tot if amb_tot else None,
        "misses": [{"idx": m[0], "read": m[1], "read_byte": m[2],
                    "canon": m[3], "canon_byte": m[4]} for m in misses],
        "gate_threshold": "38/40 exact-token",
        "gate": "PASS" if gate else "FAIL",
    }
    with open(os.path.join(HERE, "calibration.json"), "w") as f:
        json.dump(out, f, indent=1)
    return gate


if __name__ == "__main__":
    main()
