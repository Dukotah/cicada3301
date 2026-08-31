"""G3 -- coordinate / base32 pointer decode of the LP2 number stream.

If the number stream is a POINTER (an onion address, a lat/long) rather than prose,
a symbol-level statistic and even the turtle detector miss it: it is a short, sparse,
format-valid substring. This scans the value / pi / phi streams (and their mod-32 /
digit framings) for:
  - base32 (RFC4648 + onion v3 charset) runs of length 16 (v2) or 56 (v3),
  - decimal lat/long patterns,
against the seed-3301 histogram-preserving shuffle null. Null-by-default: the bar is
EXCESS over the shuffle, not mere existence.
"""
import os, sys, re, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R11 = os.path.abspath(os.path.join(HERE, "..", "..", "round11"))
sys.path.insert(0, HERE)
sys.path.insert(0, R11)
import lib_numchannel as lc

B32 = "abcdefghijklmnopqrstuvwxyz234567"  # RFC4648 lower / onion charset
ONION_V2 = re.compile(r"[a-z2-7]{16}")
ONION_V3 = re.compile(r"[a-z2-7]{56}")
LATLON = re.compile(r"[+-]?\d{1,3}\.\d{3,}[ ,]+[+-]?\d{1,3}\.\d{3,}")


def to_base32_str(stream):
    return "".join(B32[v % 32] for v in stream)


def to_digit_str(stream):
    return "".join(str(v) for v in stream)


def scan_base32(s):
    return {"v2_16": len(ONION_V2.findall(s)), "v3_56": len(ONION_V3.findall(s))}


def longest_lowentropy_run(s, k=8):
    """Longest run where the local k-window alphabet is unusually small (a
    non-random pointer repeats a small charset). Single left-to-right pass:
    extend the current run while every trailing k-window stays <= k//2 distinct."""
    n = len(s)
    best = start = 0
    i = 0
    while i < n - k:
        if len(set(s[i:i + k])) <= k // 2:
            j = i + k
            while j < n and len(set(s[j - k:j])) <= k // 2:
                j += 1
            best = max(best, j - i)
            i = j  # non-overlapping advance past the run just measured
        else:
            i += 1
    return best


def digit_pairs_as_coords(stream):
    """Read consecutive values as decimal-degree pairs; count plausible lat/long."""
    hits = 0
    for i in range(0, len(stream) - 1, 2):
        lat = stream[i] % 180 - 90
        lon = stream[i + 1] % 360 - 180
        # 'plausible pointer' = both integer-degree land-ish; too weak alone, so
        # we only report the *rate* vs null, computed by caller.
        if -60 < lat < 75 and -170 < lon < 170:
            hits += 1
    return hits


def metrics(stream):
    b32 = to_base32_str(stream)
    dig = to_digit_str(stream)
    m = scan_base32(b32)
    m["b32_lowentropy_run"] = longest_lowentropy_run(b32)
    m["latlon_regex"] = len(LATLON.findall(dig))
    m["coord_pair_rate"] = digit_pairs_as_coords(stream)
    return m


def null_rate(streamfn, base_idxs, key, n=200, seed0=3301):
    vals = []
    for k in range(n):
        sh = lc.shuffled(base_idxs, seed0 + k)
        vals.append(metrics(streamfn(sh))[key])
    return float(np.mean(vals)), float(np.max(vals))


def main():
    idxs = lc.unsolved()
    out = {"streams": {}, "verdict": {}}
    flagged = []
    for sname, sfn in {"value": lc.v_prime, "pi": lc.v_prime_index,
                       "phi": lc.v_totient}.items():
        stream = sfn(idxs)
        m = metrics(stream)
        entry = {"real": m, "null": {}}
        for key in ["v2_16", "v3_56", "b32_lowentropy_run", "latlon_regex", "coord_pair_rate"]:
            nm, nmax = null_rate(sfn, idxs, key, n=200)
            entry["null"][key] = {"mean": nm, "max": nmax}
            # A pointer is a SPARSE low-entropy substring, not the trivial
            # base32 tiling of the whole stream (v2_16/v3_56 count 16/56-char
            # windows and are identical for real & null -> not evidence). The
            # only genuine pointer signal is a low-entropy base32 run that
            # EXCEEDS the seed-3301 null max, or a real lat/long regex hit.
            if key == "b32_lowentropy_run" and m[key] > nmax and m[key] >= 16:
                flagged.append({"stream": sname, "key": key, "real": m[key],
                                "null_max": nmax})
            if key == "latlon_regex" and m[key] > nmax:
                flagged.append({"stream": sname, "key": key, "real": m[key],
                                "null_max": nmax})
        out["streams"][sname] = entry
    out["flagged_pointers"] = flagged
    out["pointer_found"] = len(flagged) > 0
    with open(os.path.join(HERE, "g3_results.json"), "w") as f:
        json.dump(out, f, indent=2, default=float)
    for sname, e in out["streams"].items():
        print(f"== {sname} ==")
        for key, v in e["real"].items():
            nb = e["null"][key]
            print(f"   {key:20} real={v}   null_mean={nb['mean']:.3g} null_max={nb['max']:.3g}")
    print("\nFLAGGED POINTERS:", flagged)
    print("POINTER_FOUND =", out["pointer_found"])


if __name__ == "__main__":
    main()
