"""R45 I1 arm_wordsched: word-boundary key schedules, enciphered with the plaintext's TRUE word segmentation and
decoded with the condition's printed segmentation (a true / b permuted / c LP2 decoy / d none).

  R37-C1 U2a (space-blind control), U2b, U3 A1/A2/A3: the lane's own encipherers (enciphers_u2_u3.py) and its own
      decoders + judge() rule (sweep.py), driven through sweep.plant_run with sweep.LENS[0] swapped per condition.
  R41-C1 R14 wordsum_selfkey W1..W5: camp7.decrypt_variant (verbatim campaign7 code) + run_c1.enc_words (copied
      verbatim below, because importing run_c1/lib would write c1.log into the R41 lane dir and needs the gitignored
      build1 panel).
python -I arm_wordsched.py -> out_wordsched.json"""
import os, sys, json, time, random, itertools
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common45 as G
import numpy as np

R37 = G.AN("round37", "C1-composed-clue-readings")
sys.path.insert(0, R37)
SW = G._load("r37_sweep", os.path.join(R37, "sweep.py"))
E = SW.E
AD, PAN = SW.AD, SW.PAN
C7 = G._load("camp7", G.AN("round41", "C1-r14-r15", "camp7.py"))
OUT = os.path.join(HERE, "out_wordsched.json")
CONDS = ("a", "b", "c", "d")
NKEY = SW.NKEY
R41_P_NULLMAX = 5.50          # round41/C1-r14-r15/RESULTS.md: R14 P-level null max


def enc_words(plain_words, variant, sign, atb):          # verbatim from round41/C1-r14-r15/run_c1.py
    tf = (lambda c: (C7.N - 1 - c) if atb else c)
    N = C7.N; out = []
    if variant == "W5":
        flat = [x for w in plain_words for x in w]; prev = 0; cf = []
        for p in flat:
            c = tf((p - sign * (C7.gp.PRIMES[prev] % N)) % N); cf.append(c); prev = c
        pos = 0
        for w in plain_words: out.append(cf[pos:pos + len(w)]); pos += len(w)
        return out
    k, cum = 0, 0
    for w in plain_words:
        cw = [tf((p - sign * k) % N) for p in w]; out.append(cw)
        if variant == "W1": k = C7.primesum(cw) % N
        elif variant == "W2": k = C7.primesum(w) % N
        elif variant == "W3": cum += C7.primesum(cw); k = cum % N
        elif variant == "W4": k = C7._totient(C7.primesum(cw)) % N
    return out


def cond_lens_long(cond, true_lens, rng, Lpage=240):
    """printed lengths covering >= NKEY runes. b permutes within the first page (Lpage runes) and within the rest."""
    if cond == "a":
        return list(true_lens)
    if cond == "b":
        n, k = 0, 0
        while n < Lpage: n += true_lens[k]; k += 1
        x, y = list(true_lens[:k]), list(true_lens[k:]); rng.shuffle(x); rng.shuffle(y); return x + y
    if cond == "c":
        return G.decoy_lengths(rng, NKEY)
    if cond == "d":
        return [sum(true_lens)]


def regroup(flat, lens):
    out, i = [], 0
    for l in lens:
        if i >= len(flat): break
        out.append(flat[i:i + l]); i += l
    if i < len(flat): out.append(flat[i:])
    return out


def r37_arm(words_all, t0):
    rows = []
    rng0 = random.Random(45370)
    jobs = []
    for (ch, nm, m) in E.VARIANTS:
        for mode in ("a", "b"):
            jobs.append(("U2", (ch, nm, m, mode)))
    for rho, mode in itertools.product((1, 2, 3), ("A1", "A2", "A3k1", "A3k2")):
        for rep in range(2):
            jobs.append(("U3", (rho, 29, mode, rep)))
    for ji, (sub, spec) in enumerate(jobs):
        rng = random.Random(45371 + ji)
        pw = G.page_words(words_all, NKEY, rng)
        true_lens = [len(w) for w in pw]
        P = G.flat(pw)[:240]
        seed = rng.randrange(1, 10 ** 9)
        if sub == "U2":
            ch, nm, m, mode = spec; rel = SW.RELS[rng.randrange(2)]; o = rng.randrange(8)
            Cc = (E.enc_u2a(P, ch, nm, m, o, rel, seed) if mode == "a" else E.enc_u2b(P, ch, nm, m, o, true_lens, rel, seed))[:240]
            j = {"sub": "U2", "ch": ch, "nm": nm, "m": m, "mode": mode, "rel": rel, "sign": -1, "o": o, "page": 0}
            cell = "U2%s" % mode
        else:
            rho, Mm, mode, rep = spec; s = rng.randrange(29); sigma = rng.choice((-1, 1))
            m3 = "A3" if mode.startswith("A3") else mode
            rel = {"A3k1": "keyskip1", "A3k2": "keyskip2"}.get(mode, "direct")
            Cc = E.enc_u3(P, true_lens, rho, Mm, s, sigma, m3, rel if m3 == "A3" else None, seed)[:240]
            j = {"sub": "U3", "rho": rho, "M": Mm, "mode": m3, "s": s, "sigma": sigma, "rel": rel, "sign": sigma, "o": 0, "page": 0}
            cell = "U3%s" % mode
        row = {"job": ji, "cell": cell, "spec": [str(x) for x in spec], "rel": rel}
        for cond in CONDS:
            lens = cond_lens_long(cond, true_lens, random.Random(seed + ord(cond)))
            saved = SW.LENS[0]
            SW.LENS[0] = lens
            try:
                p1, a1 = SW.plant_run(j, Cc, 120); p2, a2 = SW.plant_run(j, Cc, 240)
            finally:
                SW.LENS[0] = saved
            rec = SW.rec_of(p2, P)
            jd = SW.judge(float(a1["pmax"]), float(a2["pmax"]), rec, rel)
            jd["hash"] = G.h(p2)
            row[cond] = jd
        rows.append(row)
        if ji % 8 == 0:
            print("r37 %d/%d %s a=%s c=%s %.0fs" % (ji, len(jobs), cell, row["a"]["recover"], row["c"]["recover"], time.time() - t0), flush=True)
    return rows


def r41_arm(words_all, t0):
    rows = []
    VARS = [(v, s, a) for v in ("W1", "W2", "W3", "W4", "W5") for s in (-1, 1) for a in (False, True)]
    for vi, (v, s, a) in enumerate(VARS):
        rng = random.Random(45410 + vi)
        pw = G.page_words(words_all, 240, rng)
        P = G.flat(pw)
        cw = enc_words(pw, v, s, a)
        cflat = G.flat(cw)
        row = {"variant": "%s|s%+d|a%d" % (v, s, int(a))}
        for cond in CONDS:
            lens = G.cond_lengths(cond, [len(w) for w in pw], random.Random(vi * 7 + ord(cond)), len(P)) if cond != "b" else None
            if cond == "b":
                x = [len(w) for w in pw]; random.Random(vi * 7 + 98).shuffle(x); lens = x
            dec = C7.decrypt_variant(regroup(cflat, lens), v, s, a)
            rec = float(np.mean(np.array(dec) == np.array(P)))
            pm = float(AD.adjudicate(dec, pan=PAN)["pmax"])
            row[cond] = {"rec": round(rec, 4), "exact": rec == 1.0, "pmax": round(pm, 3), "over_null": pm > R41_P_NULLMAX, "hash": G.h(dec)}
        rows.append(row)
    print("r41 done %.0fs" % (time.time() - t0), flush=True)
    return rows


def summarize(rows, key_cell, ok_field):
    out = {}
    cells = sorted({r[key_cell] for r in rows})
    for c in cells + ["ALL"]:
        rr = [r for r in rows if c == "ALL" or r[key_cell] == c]
        out[c] = {"n": len(rr)}
        for cond in CONDS:
            k = sum(bool(r[cond][ok_field]) for r in rr)
            out[c][cond] = {"power": round(k / len(rr), 3), "k": k, "wilson": G.wilson(k, len(rr)),
                            "median_rec": float(np.median([r[cond].get("recovery240", r[cond].get("rec")) for r in rr]))}
        out[c]["abcd_identical_frac"] = round(sum(len({r[x]["hash"] for x in CONDS}) == 1 for r in rr) / len(rr), 3)
    return out


def run():
    t0 = time.time()
    words_all = G.text_words("pride.txt")
    r37 = r37_arm(words_all, t0)
    r41 = r41_arm(words_all, t0)
    for r in r41:
        r["W"] = r["variant"].split("|")[0]
    res = {"date": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "r37_rule": "judge(): pmax120>=bar_v3(1e6,120) & pmax240>=bar_v3(1e6,240) & recovery240>=0.90",
           "r37_summary": summarize(r37, "cell", "recover"),
           "r41_rule_exact": "rune recovery == 1.0", "r41_summary_exact": summarize(r41, "W", "exact"),
           "r41_rule_pmax": "pmax > R41 P-level null max 5.50", "r41_summary_pmax": summarize(r41, "W", "over_null"),
           "r37_rows": r37, "r41_rows": r41, "elapsed_s": round(time.time() - t0, 1)}
    json.dump(res, open(OUT, "w"), indent=1)
    for k, v in res["r37_summary"].items():
        print("R37", k, v["n"], {c: v[c]["power"] for c in CONDS})
    for k, v in res["r41_summary_exact"].items():
        print("R41exact", k, v["n"], {c: v[c]["power"] for c in CONDS}, "pmax:", {c: res["r41_summary_pmax"][k][c]["power"] for c in CONDS})


if __name__ == "__main__":
    run()
