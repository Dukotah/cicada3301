"""Round 24 / C1 — RE-ADJUDICATION of the strongest prior B-04 slice under the matched-runic scorer.

This is NOT a new key-space sweep. It re-decodes a BOUNDED, prior-ordered slice of the B-04
derived-key family and adjudicates every decode with BOTH:
  - the repo English quadgram scorer (the historic English-only gate), and
  - the round16/scorer matched-runic quadgram scorer (the axis no lane adopted),
persisting R3's four language-agnostic statistics PER ROW at sweep time (doctrine R3):
decrypt IoC.N, min distinct symbols over a 32-rune window, best non-English rune-trigram LM
(LA/GR/EN panel), and a compressibility figure.

Slice (the three conditionals, PREREG Q4):
  key space   : top-K R20-prior seeds (round20/P3/seedprior20.json, rank-1 = 1325734783)
                x B-04 generators (round13/B04/ks.py) x reductions x sign x atbash x offset 0.
                Each unix-second seed is fed to a crypto generator as BOTH its ASCII decimal bytes
                and its raw big-endian bytes (the two forms B-04 seeds.py uses for numeric seeds).
  decoder     : skipdecode.beam_decode(max_skip=3) - the ONE key-skip relation (INHERITS L7-B).
  adjudicator : English + matched-runic + LA/GR/EN rune-trigram panel + 4 agnostic stats.

Target ciphertext = the real unsolved LP2 head (nc.unsolved()[:L]). A bar-clearing survivor is
FLAGGED-FOR-ORACLE (R21-L1 seal), never auto-certified.

Run: PYTHONUTF8=1 python3 readjudicate.py            # writes results.json
     PYTHONUTF8=1 python3 readjudicate.py --topk 40  # smaller slice
"""
import os, sys, json, math, random, time, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
B6 = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round16", "scorer"),
          os.path.join(LP, "analysis", "round11"),
          os.path.join(LP, "analysis", "round13", "B04"),
          os.path.join(LP, "analysis", "round20", "P3"), B6, HERE):
    sys.path.insert(0, p)

from lp import gematria as gp          # noqa
from lp import score as _score         # noqa
import skipdecode as sk                # noqa
import lib_numchannel as nc            # noqa
import ks                              # noqa
import detectors as D                  # noqa
from scorer import matched_scorer      # noqa
import null as NULLMOD                 # benchmark/null.py  # noqa
from p3b_seedprior import seed_order   # noqa
from greek_corpus import romanized_greek  # noqa

N = gp.N
Q = _score.default()
MQ = matched_scorer()
BEAM_W, MAX_SKIP = 400, 3
L = 120           # B-04 stage-A/B head length (harness HEAD_L)


# ---- R3 language-agnostic statistics (rune-index space) ----
def stat_ioc_n(idx):
    n = len(idx)
    if n < 2:
        return 0.0
    from collections import Counter
    c = Counter(idx)
    num = sum(v * (v - 1) for v in c.values())
    return (num / (n * (n - 1))) * N


def stat_min_distinct_32(idx):
    w = 32
    if len(idx) < w:
        return len(set(idx))
    return min(len(set(idx[i:i + w])) for i in range(len(idx) - w + 1))


def stat_compress(idx):
    b = bytes(x % 256 for x in idx)
    if not b:
        return 1.0
    return len(zlib.compress(b, 9)) / len(b)


# ---- LA/GR/EN rune-space trigram panel (language-aware, unlike the matched scorer) ----
def _build_trigram_panel():
    en = D.text_to_runes(open(os.path.join(LP, "data", "keys", "self_reliance.txt"),
                              encoding="utf-8", errors="ignore").read(), "EN")
    la = D.text_to_runes(open(os.path.join(LP, "analysis", "latin", "latin_28233.txt"),
                              encoding="utf-8", errors="ignore").read(), "LA")
    gr = D.text_to_runes(romanized_greek(), "LA")
    return {"EN": D.build_trigram(en), "LA": D.build_trigram(la), "GR": D.build_trigram(gr)}


_PANEL = None


def panel_scores(idx):
    global _PANEL
    if _PANEL is None:
        _PANEL = _build_trigram_panel()
    import numpy as np
    a = np.array(idx, dtype=np.int64)
    return {k: round(D.score_trigram(lm, a), 4) for k, lm in _PANEL.items()}


def atbash(C):
    return [(N - 1) - c for c in C]


def _decode_row(C, K, sign, atb, label):
    Cx = atbash(C) if atb else C
    bd = sk.beam_decode(Cx, K, sign=sign, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
    idx = bd["plain_idx"]
    tl = sk.idx_to_trans(idx)
    ps = panel_scores(idx)
    return {
        "label": label, "sign": sign, "atbash": atb,
        "en_score": round(Q.score_norm(tl), 4),
        "matched_score": round(MQ.score_norm(tl), 4),
        "panel_EN": ps["EN"], "panel_LA": ps["LA"], "panel_GR": ps["GR"],
        "panel_max": round(max(ps.values()), 4),
        "ioc_n": round(stat_ioc_n(idx), 4),
        "min_distinct_32": stat_min_distinct_32(idx),
        "compress": round(stat_compress(idx), 4),
        "head": tl[:48],
    }


def run():
    topk = 40
    for i, a in enumerate(sys.argv):
        if a == "--topk":
            topk = int(sys.argv[i + 1])

    seeds_int = seed_order(topk)          # R20 prior, rank-1 first
    C_full = nc.unsolved()[:L]
    gens = ks.GEN_NAMES
    reds = ["mod29", "rej29", "hi_nib", "bits5"]
    signs = [-1, +1]
    atbs = [False, True]
    need = L * (MAX_SKIP + 1) + 512

    rows = []
    t0 = time.time()
    n_decodes = 0
    # collect matched-scorer scores for a real order-matched null on the SAME ciphertext
    for si, sd in enumerate(seeds_int):
        seed_forms = [("dec", str(sd).encode("ascii")),
                      ("raw", sd.to_bytes((sd.bit_length() + 7) // 8 or 1, "big"))]
        for sform, sbytes in seed_forms:
            for gen in gens:
                for red in reds:
                    try:
                        Kfull = ks.make_ks(gen, red, sbytes, need)
                    except Exception:
                        continue
                    if red == "lo_nib":
                        continue
                    K = [k % N for k in Kfull[:need]]
                    for sign in signs:
                        for atb in atbs:
                            label = f"seed{sd}|{sform}|{gen}|{red}"
                            row = _decode_row(C_full, K, sign, atb, label)
                            rows.append(row)
                            n_decodes += 1

    # ---- seed-3301 order-matched null on the SAME real ciphertext, matched scorer ----
    rng = random.Random(3301)
    n_null = 400
    null_en, null_mq, null_panelmax = [], [], []
    for _ in range(n_null):
        WK = [rng.randrange(N) for _ in range(need)]
        r = _decode_row(C_full, WK, -1, False, "NULL")
        null_en.append(r["en_score"])
        null_mq.append(r["matched_score"])
        null_panelmax.append(r["panel_max"])

    def summ(v):
        m = sum(v) / len(v)
        sd = math.sqrt(sum((x - m) ** 2 for x in v) / len(v))
        return {"mean": round(m, 4), "sd": round(sd, 4), "max": round(max(v), 4)}

    null = {"n": n_null, "en": summ(null_en), "matched": summ(null_mq),
            "panel_max": summ(null_panelmax)}

    # ---- family-wise bars at true N (benchmark/null.py) ----
    Nreal = n_decodes
    bar_en = NULLMOD.threshold_for(Nreal, mu=null["en"]["mean"],
                                   beta=NULLMOD.gumbel_params(null["en"]["sd"]))
    bar_mq = NULLMOD.threshold_for(Nreal, mu=null["matched"]["mean"],
                                   beta=NULLMOD.gumbel_params(null["matched"]["sd"]))
    bar_panel = NULLMOD.threshold_for(Nreal, mu=null["panel_max"]["mean"],
                                      beta=NULLMOD.gumbel_params(null["panel_max"]["sd"]))

    best_en = max(rows, key=lambda r: r["en_score"])
    best_mq = max(rows, key=lambda r: r["matched_score"])
    best_panel = max(rows, key=lambda r: r["panel_max"])

    # survivors: clear BOTH the order-matched null max AND the family-wise bar
    def survivors(rows, key, nullmax, bar):
        return [r for r in rows if r[key] > nullmax and r[key] > bar]

    surv_en = survivors(rows, "en_score", null["en"]["max"], bar_en)
    surv_mq = survivors(rows, "matched_score", null["matched"]["max"], bar_mq)
    surv_panel = survivors(rows, "panel_max", null["panel_max"]["max"], bar_panel)

    out = {
        "lane": "round24/C1-matched-runic (re-adjudication)",
        "slice": {"topk_seeds": topk, "generators": gens, "reductions": reds,
                  "signs": signs, "atbash": atbs, "offset": 0, "L": L,
                  "target": "real unsolved LP2 head nc.unsolved()[:120]"},
        "n_decodes": n_decodes,
        "conditionals": {
            "key_space": f"top-{topk} R20-prior seeds x {len(gens)} gens x {len(reds)} reds "
                         f"x 2 signs x 2 atbash x 2 seed-forms, offset 0",
            "decoder": "beam_decode(max_skip=3) - one key-skip relation; inherits L7-B",
            "adjudicator": "EN quadgram + round16 matched-runic + EN/LA/GR rune-trigram panel + 4 R3 stats",
        },
        "null_seed": 3301, "null": null,
        "family_wise_bars": {"en": round(bar_en, 4), "matched": round(bar_mq, 4),
                             "panel_max": round(bar_panel, 4)},
        "best": {
            "en": {"score": best_en["en_score"], "label": best_en["label"], "head": best_en["head"]},
            "matched": {"score": best_mq["matched_score"], "label": best_mq["label"],
                        "head": best_mq["head"]},
            "panel_max": {"score": best_panel["panel_max"], "label": best_panel["label"],
                          "which": max(("EN", "LA", "GR"),
                                       key=lambda k: best_panel[f"panel_{k}"]),
                          "head": best_panel["head"]},
        },
        "survivors": {"en": len(surv_en), "matched": len(surv_mq), "panel_max": len(surv_panel)},
        "survivor_rows": (surv_mq + surv_panel)[:20],
        "elapsed_s": round(time.time() - t0, 1),
    }
    # keep the full row archive compressed-out; store only top-50 per scorer + the survivors (R3: the
    # agnostic stats ARE persisted for the retained rows; the point is they exist per-row at sweep time)
    out["top50_matched"] = sorted(rows, key=lambda r: -r["matched_score"])[:50]
    out["top50_panel"] = sorted(rows, key=lambda r: -r["panel_max"])[:50]

    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)

    print(f"n_decodes = {n_decodes:,}   ({out['elapsed_s']}s)")
    print(f"null(matched) mean={null['matched']['mean']} sd={null['matched']['sd']} "
          f"max={null['matched']['max']}")
    print(f"bars  EN={bar_en:.3f}  MATCHED={bar_mq:.3f}  PANEL={bar_panel:.3f}")
    print(f"best  EN={best_en['en_score']:.3f} ({best_en['label']})")
    print(f"      MATCHED={best_mq['matched_score']:.3f} ({best_mq['label']})")
    print(f"      PANEL={best_panel['panel_max']:.3f} ({best_panel['label']} "
          f"-> {out['best']['panel_max']['which']})")
    print(f"survivors  EN={len(surv_en)}  MATCHED={len(surv_mq)}  PANEL={len(surv_panel)}")
    print("wrote results.json")


if __name__ == "__main__":
    run()
