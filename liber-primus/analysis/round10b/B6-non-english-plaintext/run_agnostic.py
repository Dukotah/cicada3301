"""B6 run 1 — language-agnostic short-window structure scan.

Three parts, all pre-registered in PREREG.md:
  (A) NULL calibration: 200 shuffles of the real LP2 stream -> max-statistic null.
  (B) POSITIVE CONTROL: plant payloads of many lengths into random rune streams,
      report the DETECTION FLOOR per (detector, payload type).
  (C) REAL scan: raw stream + difference transforms, all window sizes.

Detectors D1/D2/D3/D7 are invariant under any monoalphabetic substitution of the
29 runes, so part (C) on the raw ciphertext simultaneously covers every shift,
Atbash, and alphabet-reordering decode.
"""
import json
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detectors as D

OUT = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260812)

WINDOWS = [12, 16, 24, 32, 48, 64, 96, 128]
FAST = {k: v for k, v in D.AGNOSTIC.items() if k != "D4_compress"}
N_NULL = 200


def scan_max(x, det, w, step=1):
    v = det(x, w, step)
    if len(v) == 0:
        return -1e9, -1
    i = int(np.argmax(v))
    return float(v[i]), i * step


def diffstream(x, k=1):
    return (x[k:] - x[:-k]) % D.N


# ------------------------------------------------------------------ (A) nulls

def calibrate(stream):
    n = len(stream)
    null = {name: {w: [] for w in WINDOWS} for name in FAST}
    t0 = time.time()
    for r in range(N_NULL):
        s = RNG.permutation(stream)
        for name, det in FAST.items():
            for w in WINDOWS:
                m, _ = scan_max(s, det, w)
                null[name][w].append(m)
    print("null calibration %.1fs" % (time.time() - t0), flush=True)
    tab = {}
    for name in FAST:
        for w in WINDOWS:
            a = np.array(null[name][w])
            tab["%s|%d" % (name, w)] = {
                "null_mean": float(a.mean()), "null_sd": float(a.std(ddof=1)),
                "null_max": float(a.max()), "n": len(a)}
    return tab


# ------------------------------------------------------- (B) positive control

def payload_subalpha(L, k):
    """A payload drawn from a restricted k-symbol subalphabet (hex-like k=16,
    digit-like k=10, base32-like k=29 i.e. unrestricted)."""
    sub = RNG.choice(D.N, size=min(k, D.N), replace=False)
    return sub[RNG.integers(0, len(sub), size=L)]


COORD_TEXT = ("FIFTY ONE DEGREES THIRTY ONE MINUTES NORTH ZERO DEGREES "
              "SEVEN MINUTES WEST FOLLOW THE COORDINATES TO THE POSTER ")
ENG_TEXT = ("A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE "
            "TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH ")
LAT_TEXT = ("GALLIA EST OMNIS DIVISA IN PARTES TRES QUARUM UNAM INCOLUNT BELGAE "
            "ALIAM AQUITANI TERTIAM QUI IPSORUM LINGUA CELTAE APPELLANTUR ")
ONION_TEXT = ("THE ANSWER IS AT HTTP SLASH SLASH SEVEN FOUR RUNES DOT ONION "
              "GO THERE NOW AND BRING THE KEY ")


def make_payloads():
    p = {}
    p["hex16"] = lambda L: payload_subalpha(L, 16)
    p["digit10"] = lambda L: payload_subalpha(L, 10)
    p["base32_full"] = lambda L: payload_subalpha(L, 29)
    for nm, txt in (("coord_runeglish", COORD_TEXT), ("english", ENG_TEXT),
                    ("latin", LAT_TEXT), ("onion_runeglish", ONION_TEXT)):
        r = D.text_to_runes(txt * 6, "LA" if nm == "latin" else "EN")
        p[nm] = (lambda rr: (lambda L: rr[:L]))(r)
    return p


def positive_control(stream, tab):
    n = len(stream)
    lens = [8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]
    pays = make_payloads()
    res = {}
    for pname, gen in pays.items():
        res[pname] = {}
        for L in lens:
            pl = gen(L)
            if len(pl) < L:
                continue
            found = {}
            for trial in range(5):
                host = RNG.integers(0, D.N, size=n)
                off = int(RNG.integers(0, n - L))
                host[off:off + L] = pl
                for name, det in FAST.items():
                    for w in WINDOWS:
                        if w > L:
                            continue
                        key = "%s|%d" % (name, w)
                        thr = tab[key]["null_max"]
                        m, pos = scan_max(host, det, w)
                        hit = (m > thr) and (off - w <= pos <= off + L)
                        found.setdefault(name, {}).setdefault(w, []).append(bool(hit))
            res[pname][L] = {nm: {str(w): float(np.mean(v))
                                  for w, v in d.items()}
                             for nm, d in found.items()}
        print("  pos-control %s done" % pname, flush=True)
    return res


def detection_floor(pc):
    """Shortest planted length detected in >=4/5 trials, per (payload, detector)."""
    floors = {}
    for pname, byL in pc.items():
        floors[pname] = {}
        for name in FAST:
            best = None
            for L in sorted(int(k) for k in byL):
                d = byL[L].get(name, {})
                if any(v >= 0.8 for v in d.values()):
                    best = L
                    break
            floors[pname][name] = best
    return floors


# ------------------------------------------------------------------ (C) real

def real_scan(stream, tab):
    streams = {
        "raw": stream,
        "diff1": diffstream(stream, 1),
        "diff2": diffstream(diffstream(stream, 1), 1),
        "reversed_diff1": diffstream(stream[::-1], 1),
    }
    out = {}
    for sname, x in streams.items():
        for name, det in FAST.items():
            for w in WINDOWS:
                key = "%s|%d" % (name, w)
                t = tab[key]
                m, pos = scan_max(x, det, w)
                z = (m - t["null_mean"]) / t["null_sd"] if t["null_sd"] > 0 else 0.0
                out["%s|%s|%d" % (sname, name, w)] = {
                    "real_max": m, "pos": pos, "z": z,
                    "null_mean": t["null_mean"], "null_sd": t["null_sd"],
                    "null_max": t["null_max"],
                    "PASS": bool(z >= 3.0 and m > t["null_max"])}
    return out


def main():
    pages, stream = D.load_unsolved()
    print("stream", len(stream), flush=True)
    tab = calibrate(stream)
    json.dump(tab, open(os.path.join(OUT, "null_table.json"), "w"), indent=1)
    print("--- positive control ---", flush=True)
    pc = positive_control(stream, tab)
    fl = detection_floor(pc)
    json.dump({"raw": pc, "floors": fl},
              open(os.path.join(OUT, "positive_control.json"), "w"), indent=1)
    print(json.dumps(fl, indent=1))
    print("--- real scan ---", flush=True)
    rs = real_scan(stream, tab)
    json.dump(rs, open(os.path.join(OUT, "real_scan.json"), "w"), indent=1)
    passes = {k: v for k, v in rs.items() if v["PASS"]}
    print("PASSES:", json.dumps(passes, indent=1))
    top = sorted(rs.items(), key=lambda kv: -kv[1]["z"])[:12]
    for k, v in top:
        print("%-34s real=%.4f z=%+.2f nullmax=%.4f pos=%d" %
              (k, v["real_max"], v["z"], v["null_max"], v["pos"]))


if __name__ == "__main__":
    main()
