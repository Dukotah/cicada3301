"""R44/W2-A4 — positive-control GATE (PREREG section 4), run BEFORE the sweep.

G1: tier-A glue plant (pages 10 & 20, theta* = s1=+1, s2=-1, k=1, scope=page,
    ch=s3, f=prime_index, sig3=-1, s=17).
G2: tier-B glue plant (pages 0-2, theta** = s1=-1, s2=+1, k=2, scope=continuous,
    ch=r, f=cumulative, sig3=+1, s=5).
Any failure => INSTRUMENT-INCOMPLETE; run_sweep.py refuses to run.
Writes gate.json + plant_results.json.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chained as CH                              # noqa: E402

LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))
sys.path.insert(0, os.path.join(LP, "src"))
import adjudicate as A                            # noqa: E402
from lp import gematria as gp                     # noqa: E402

PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))

# the F5b-T LP-register control plaintexts of record (as in R44-R1 plant_gate.py)
PT1 = ("A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE "
       "KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE "
       "MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED SOME WISDOM "
       "THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED "
       "KNOW THIS WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS")
PT2 = ("WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP "
       "BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND "
       "AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND "
       "YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF")
PT3 = ("SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO "
       "DESTROY ALL THAT YOU OWN AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY A KOAN DURING "
       "A LESSON THE MASTER EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID WHEN "
       "ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID IT IS A VOICE INSIDE YOUR "
       "HEAD")


def to_idx(text):
    out = []
    for w in text.split():
        out.extend(gp.keyword_to_indices(w))
    return out


def pt_pool():
    pool = to_idx(PT1) + to_idx(PT2) + to_idx(PT3)
    while len(pool) < 1200:                        # cycle if short (PREREG G2 note)
        pool = pool + pool
    return pool


def sweep_one_page(pages, pi, bar):
    """The IDENTICAL tier-A grid on one page: 16 variants x 29 offsets = 464 rows."""
    rows, meta = [], []
    for (s1, s2, k, sc) in CH.tierA_variants():
        rows.append(CH.decode_page_grid(pages, pi, s1, s2, k, sc))
        meta.extend((s1, s2, k, sc, o) for o in range(CH.N))
    X = np.concatenate(rows, axis=0)
    r = A.adjudicate_batch(X, pan=PAN)
    return X, meta, r


def recovery(a, b):
    a, b = list(a), list(b)
    return sum(1 for x, y in zip(a, b) if x == y) / max(1, len(b))


def main():
    t0 = time.time()
    corpus = CH.load_corpus()
    assert CH.collapse_lemma_check(corpus["chans"])
    pages, lens, chans = corpus["pages"], corpus["lens"], corpus["chans"]
    pool = pt_pool()
    out = {"bars": CH.BARS, "n_bar": CH.N_BAR, "controls": [], "passed": None}

    # ------------------------------------------------ G1 (tier A)
    th1 = dict(ch="s3", f="prime_index", sig3=-1, s=17)
    o1 = CH.offsets_for(th1, chans)
    s1, s2, k, sc = +1, -1, 1, "page"
    g1 = {"name": "G1", "theta": dict(th1, s1=s1, s2=s2, k=k, scope=sc), "pages": []}
    ok1 = True
    syn = [p.copy() for p in pages]
    used = 0
    plant_pt = {}
    for pi in (10, 20):
        pt = pool[used:used + lens[pi]]
        used += lens[pi]
        plant_pt[pi] = pt
        syn[pi] = np.asarray(
            CH.encipher_page(pt, None, s1, s2, k, sc, int(o1[pi])), dtype=np.int64)
    for pi in (10, 20):
        bar = CH.bar_for(lens[pi])
        X, meta, r = sweep_one_page(syn, pi, bar)
        pm = r["pmax"]
        i = int(pm.argmax())
        ms1, ms2, mk, msc, mo = meta[i]
        # the planted cell's own row
        jp = next(j for j, m in enumerate(meta)
                  if m == (s1, s2, k, sc, int(o1[pi])))
        rec = recovery(X[jp], plant_pt[pi])
        argmax_matches = (ms1, ms2, mk, mo) == (s1, s2, k, int(o1[pi]))
        page_ok = bool(rec == 1.0 and argmax_matches and pm[jp] >= bar)
        full = A.adjudicate(X[jp], pan=PAN)
        g1["pages"].append(dict(page=pi, L=int(lens[pi]), bar=bar, o_p=int(o1[pi]),
                                planted_pmax=float(pm[jp]), grid_max=float(pm[i]),
                                argmax_cell=[ms1, ms2, mk, msc, mo],
                                recovery=rec, degenerate=bool(full["degenerate"]),
                                ok=page_ok))
        ok1 = ok1 and page_ok
        # differential (report only): wrong offset, wrong feedback sign
        dwo = CH.decode_page(syn, pi, s1, s2, k, sc, (int(o1[pi]) + 1) % 29)
        dws = CH.decode_page(syn, pi, s1, -s2, k, sc, int(o1[pi]))
        g1["pages"][-1]["differential"] = {
            "wrong_offset": dict(recovery=recovery(dwo, plant_pt[pi]),
                                 pmax=float(A.adjudicate(dwo, pan=PAN)["pmax"])),
            "wrong_fb_sign": dict(recovery=recovery(dws, plant_pt[pi]),
                                  pmax=float(A.adjudicate(dws, pan=PAN)["pmax"]))}
    g1["ok"] = ok1
    out["controls"].append(g1)

    # ------------------------------------------------ G2 (tier B)
    th2 = dict(ch="r", f="cumulative", sig3=+1, s=5)
    o2 = CH.offsets_for(th2, chans)
    s1, s2, k, sc = -1, +1, 2, "continuous"
    syn2 = [p.copy() for p in pages]
    pt_head = pool[:729]
    pos = 0
    for pi in range(3):
        prev_tail = list(syn2[pi - 1][-k:]) if pi > 0 else None
        pt = pt_head[pos:pos + lens[pi]]
        pos += lens[pi]
        syn2[pi] = np.asarray(
            CH.encipher_page(pt, prev_tail, s1, s2, k, sc, int(o2[pi])), dtype=np.int64)
    # IDENTICAL tier-B enumeration on the planted head
    thetas = CH.tierB_thetas()
    best = {"pmax": -99.0}
    planted_stream = None
    uniq = {}
    for th in thetas:
        ov = CH.offsets_for(th, chans)
        key = (th["s1"], th["s2"], th["k"], th["scope"],
               int(ov[0]), int(ov[1]), int(ov[2]))
        uniq.setdefault(key, []).append(th)
    Xs, keys = [], []
    for key in uniq:
        ks1, ks2, kk, ksc, a, b, c = key
        Xs.append(CH.decode_head(syn2, lens, ks1, ks2, kk, ksc, [a, b, c]))
        keys.append(key)
    X = np.stack(Xs)
    r = A.adjudicate_batch(X, pan=PAN)
    pm = r["pmax"]
    i = int(pm.argmax())
    kstar = (s1, s2, k, sc, int(o2[0]), int(o2[1]), int(o2[2]))
    rec = recovery(X[i], pt_head)
    ok2 = bool(keys[i] == kstar and rec == 1.0 and pm[i] >= CH.BARS[729])
    g2 = {"name": "G2", "theta": dict(th2, s1=s1, s2=s2, k=k, scope=sc),
          "planted_key": list(kstar), "argmax_key": list(keys[i]),
          "n_thetas": len(thetas), "n_unique": len(keys),
          "pmax": float(pm[i]), "bar": CH.BARS[729], "recovery": rec, "ok": ok2}
    out["controls"].append(g2)

    out["passed"] = bool(ok1 and ok2)
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "plant_results.json"), "w"), indent=1)
    json.dump({"passed": out["passed"], "when": time.strftime("%Y-%m-%dT%H:%M:%S")},
              open(os.path.join(HERE, "gate.json"), "w"), indent=1)
    print("GATE", "PASSED" if out["passed"] else "FAILED (INSTRUMENT-INCOMPLETE)",
          "in", out["seconds"], "s")
    print(json.dumps(out["controls"], indent=1)[:2000])


if __name__ == "__main__":
    main()
