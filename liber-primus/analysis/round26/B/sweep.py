#!/usr/bin/env python3
"""LANE B -- the R12-C2 keytext running-key sweep, THE one un-run keytext lane.

Each of the 33 R12-C2 texts (analysis/round12/C2/texts/) is mapped to rune indices
and slid as a RUNNING KEY K across every UNSOLVED rune-bearing LP2 page (the OTP-class
target). Rigid running-key is already doublet-excluded; that is exactly why this is
SKIP-AWARE: both preset 'exact' (keyskip1) and preset 'pair' (keyskip2) are run.
Panel-max adjudicated, and every survivor of the panel-max bar goes through hitfn20.

Language-agnostic per-(text,offset,page,preset) stats persisted at sweep time:
  pmax, panel-max bar, clears_null, ioc, mds (min distinct in 32-window), h2 (entropy),
  distinct-count, best non-English panel score, all-register z vector, score, recovery
  (heldout self-consistency for real candidates).

Offsets per text: OFFN evenly spaced starts into the keytext (stated in RESULTS).
Sign: -1 (the repo decode relation). Bounded, prior-dense: 33 texts x OFFN offsets
x |unsolved pages| x 2 presets.

Run: python3 sweep.py   # writes sweep.jsonl (per-decode rows) + sweep_summary.json
"""
import os, sys, json, math, glob, statistics, collections

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "benchmark",
          os.path.join("analysis", "campaign18_skip"),
          os.path.join("analysis", "round19", "I1"),
          os.path.join("analysis", "round20", "HITFN")):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

from lp import corpus, gematria as gp     # noqa
import skipdecode as sk                   # noqa
import driftbeam as DB                    # noqa
import hitfn20 as HF                      # noqa
import adjudicate as AD                   # noqa

N = gp.N
TEXTDIR = os.path.join(LP, "analysis", "round12", "C2", "texts")
OFFN = 4                    # start offsets per text (evenly spaced across usable range)
PRESETS = ["exact", "pair"]
SIGN = -1
N_ADJ = None               # set after we count total decodes (family-wise bar N)


def unsolved_pages():
    D = corpus.parse()
    out = []
    for i, pg in enumerate(D):
        r = pg.get("runes", "") or ""
        idx = gp.runes_to_indices(r) if r else []
        if len(idx) >= 20 and not pg.get("plaintext"):
            out.append((i, pg["label"], idx))
    return out


def keytexts():
    out = []
    for fp in sorted(glob.glob(os.path.join(TEXTDIR, "*.txt"))):
        with open(fp, encoding="utf-8", errors="ignore") as f:
            idx = sk.eng_to_idx(f.read())
        out.append((os.path.basename(fp), idx))
    return out


def min_distinct_window(idx, w=32):
    if len(idx) <= w:
        return len(set(idx))
    m = len(idx)
    for i in range(0, len(idx) - w + 1):
        m = min(m, len(set(idx[i:i + w])))
    return m


def entropy(idx):
    c = collections.Counter(idx)
    n = len(idx)
    return -sum((v / n) * math.log2(v / n) for v in c.values()) if n else 0.0


def main():
    pages = unsolved_pages()
    texts = keytexts()
    print("unsolved rune pages:", [(i, len(idx)) for i, _, idx in pages])
    print("keytexts:", len(texts))

    # count total decodes for the family-wise panel-max bar N
    total = 0
    plan = []
    # ascending page length: cheap pages complete first -> broad early coverage
    pages = sorted(pages, key=lambda t: len(t[2]))
    for pi, plabel, C in pages:
        Lc = len(C)
        for tname, K in texts:
            usable = len(K) - Lc * (8 + 1) - 8   # room for max_skip=8 running-key
            if usable <= OFFN:
                continue
            offs = [int(o) for o in
                    (usable * k // OFFN for k in range(OFFN))]
            for o in offs:
                for pr in PRESETS:
                    plan.append((pi, plabel, C, tname, K, o, pr))
                    total += 1
    global N_ADJ
    N_ADJ = total
    print("total decodes planned:", total)

    outp = open(os.path.join(HERE, "sweep.jsonl"), "w")
    best = None
    flags = []
    n_clear = 0
    done = 0
    for (pi, plabel, C, tname, K, o, pr) in plan:
        dec = HF.HitDecode(C=C, K=K, o=o, sign=SIGN, preset=pr,
                           n_round_adjudicated=N_ADJ)
        v = HF.evaluate(dec)
        d = dec._decoded
        pidx = d["plain_idx"]
        a = AD.adjudicate(pidx, translit=d.get("translit"))
        # best non-English panel raw score: registers 2..8 are the non-EN_MODERN panels;
        # non-english = everything except EN_MODERN(0)/EN_KJV(1). Use adjudicate's pmax_ne.
        row = {
            "page": pi, "label": plabel, "text": tname, "offset": o, "preset": pr,
            "n": v.n, "score": round(v.score, 4),
            "pmax": round(v.pmax, 4), "bar": round(v.bar, 4),
            "clears_null": v.clears_null,
            "recovery": round(v.recovery, 4), "heldout": round(v.heldout_recovery, 4),
            "hit": v.hit, "preg": v.preg_name,
            "ioc": round(float(a["ioc"]), 5),
            "mds": min_distinct_window(pidx, 32),
            "h2": round(entropy(pidx), 4),
            "distinct": len(set(pidx)),
            "pmax_ne": round(float(a["pmax_ne"]), 4),
            "ne_reg": AD.panel().registers[int(a["ne_reg"])],
            "z": [round(float(x), 3) for x in a["z"]],
        }
        outp.write(json.dumps(row) + "\n")
        outp.flush()
        if v.clears_null:
            n_clear += 1
            if v.hit:
                flags.append(row)   # a certified HIT (should be none)
            else:
                flags.append(row)   # bar-clearing survivor -> FLAG-FOR-ORACLE
        if best is None or v.pmax > best["pmax"]:
            best = row
        done += 1
        if done % 500 == 0:
            print("  ...%d/%d  best pmax so far %.3f (%s@%s/%s)" %
                  (done, total, best["pmax"], best["text"], best["offset"], best["preset"]))
    outp.close()

    summary = {
        "lane": "round26/B",
        "n_texts": len(texts), "n_pages": len(pages), "offsets_per_text": OFFN,
        "presets": PRESETS, "sign": SIGN,
        "total_decodes": total, "n_clear_bar": n_clear,
        "n_flagged_for_oracle": len(flags),
        "best_row": best,
        "flags": flags[:50],
    }
    with open(os.path.join(HERE, "sweep_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("DONE. decodes=%d  cleared-bar=%d  flagged=%d" % (total, n_clear, len(flags)))
    print("best pmax %.3f  bar %.3f  text=%s off=%s preset=%s page=%s" %
          (best["pmax"], best["bar"], best["text"], best["offset"], best["preset"], best["page"]))


if __name__ == "__main__":
    main()
