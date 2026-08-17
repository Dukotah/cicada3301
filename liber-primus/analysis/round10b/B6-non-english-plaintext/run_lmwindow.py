"""B6 run 4 — SHORT-WINDOW language scan over the whole monoalphabetic decode family.

The page-scale scorers used by every prior sweep would average a 30-rune payload
into noise. Here every one of the 116 monoalphabetic decodes of the full stream
(29 shifts x Atbash x forward/reversed) is scanned with a SLIDING WINDOW under six
rune-space trigram LMs (EN, LA, DE, CY-Welsh, OE, RG=solved-LP English), and the
max-window statistic is compared against the identical scan on shuffled ciphertext.

Also runs the long-window compressibility detector (D4) that was uninformative at
short window sizes.
"""
import json
import os
import sys
import time
import zlib
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detectors as D
import run_lang as RL

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(4242)
WINS = [24, 48, 96, 192]
NNULL = 60


def decodes(x):
    """116 monoalphabetic decodes: 29 shifts x atbash x direction."""
    for rev in (False, True):
        y = x[::-1] if rev else x
        for atb in (False, True):
            z = (D.N - 1 - y) % D.N if atb else y
            for s in range(D.N):
                yield ("rev%d_atb%d_s%02d" % (rev, atb, s), (z - s) % D.N)


def scan(x, lms):
    best = {}
    for tag, d in decodes(x):
        for lk, lm in lms.items():
            pt = lm[d[:-2], d[1:-1], d[2:]]
            cs = np.concatenate([[0.0], np.cumsum(pt)])
            for w in WINS:
                m = w - 2
                if m >= len(pt):
                    continue
                starts = np.arange(0, len(d) - w + 1)
                v = (cs[starts + m] - cs[starts]) / m
                i = int(np.argmax(v))
                k = "%s|%d" % (lk, w)
                if k not in best or v[i] > best[k][0]:
                    best[k] = (float(v[i]), tag, i)
    return best


def raw_deflate_len(b):
    c = zlib.compressobj(9, zlib.DEFLATED, -15)
    return len(c.compress(b) + c.flush())


def d4_long(x, w, step):
    xb = bytes(bytearray(x.tolist()))
    n = len(x)
    out = []
    for s in range(0, n - w + 1, step):
        out.append(-raw_deflate_len(xb[s:s + w]))
    return np.array(out, dtype=float)


def main():
    pages, stream = D.load_unsolved()
    t0 = time.time()
    lms, sizes = RL.build_lms()
    print("LMs built %.1fs" % (time.time() - t0), flush=True)

    real = scan(stream, lms)
    print("real scan done %.1fs" % (time.time() - t0), flush=True)

    null = {}
    for r in range(NNULL):
        s = RNG.permutation(stream)
        b = scan(s, lms)
        for k, v in b.items():
            null.setdefault(k, []).append(v[0])
        if r % 10 == 0:
            print("  null %d  %.1fs" % (r, time.time() - t0), flush=True)

    out = {}
    for k, (val, tag, pos) in real.items():
        a = np.array(null[k])
        z = (val - a.mean()) / a.std(ddof=1)
        out[k] = {"real": val, "decode": tag, "pos": pos,
                  "null_mean": float(a.mean()), "null_sd": float(a.std(ddof=1)),
                  "null_max": float(a.max()), "z": float(z),
                  "PASS": bool(z >= 4.0 and val > a.max())}

    # positive control: plant real English / Latin at the same window sizes into a
    # random stream, apply the identical scan, confirm the instrument fires.
    pc = {}
    from run_agnostic import ENG_TEXT, LAT_TEXT, COORD_TEXT
    for pname, txt, lg in (("english", ENG_TEXT, "EN"), ("latin", LAT_TEXT, "LA"),
                           ("coord", COORD_TEXT, "EN")):
        r = D.text_to_runes(txt * 8, lg)
        pc[pname] = {}
        for L in [16, 24, 32, 48, 64, 96, 128, 192]:
            hits = 0
            for trial in range(3):
                host = RNG.integers(0, D.N, size=len(stream))
                off = int(RNG.integers(0, len(stream) - L))
                host[off:off + L] = r[:L]
                b = scan(host, lms)
                ok = False
                for k, (val, tag, pos) in b.items():
                    if val > out[k]["null_max"] and abs(pos - off) <= L:
                        ok = True
                hits += ok
            pc[pname][L] = hits / 3.0
        print("  pc %s %s" % (pname, pc[pname]), flush=True)

    # D4 long-window compressibility
    d4 = {}
    for w, step in ((192, 4), (512, 8)):
        rv = d4_long(stream, w, step)
        nl = []
        for _ in range(40):
            nl.append(d4_long(RNG.permutation(stream), w, step).max())
        nl = np.array(nl)
        d4["D4|%d" % w] = {"real": float(rv.max()),
                           "null_mean": float(nl.mean()),
                           "null_sd": float(nl.std(ddof=1)),
                           "null_max": float(nl.max()),
                           "z": float((rv.max() - nl.mean()) / nl.std(ddof=1))}
    json.dump({"window_lm": out, "positive_control": pc, "d4_long": d4},
              open(os.path.join(HERE, "lmwindow_results.json"), "w"), indent=1)
    for k in sorted(out, key=lambda k: -out[k]["z"]):
        v = out[k]
        print("%-10s real=%.4f null_mean=%.4f sd=%.4f max=%.4f z=%+.2f %s [%s@%d]" %
              (k, v["real"], v["null_mean"], v["null_sd"], v["null_max"], v["z"],
               "PASS" if v["PASS"] else "", v["decode"], v["pos"]))
    print("D4:", json.dumps(d4, indent=1))
    print("total %.1fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
