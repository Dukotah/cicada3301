"""Round 24 / C1-EXT — RE-ADJUDICATION of the IDENTICAL C1 B-04 slice under a WIDENED,
control-validated, genuinely LANGUAGE-AWARE non-English rune-trigram panel.

Same slice, same decoder, same target as C1's readjudicate.py (top-K R20-prior seeds x B-04
generators x reductions x sign x atbash x 2 seed-forms, offset 0, L=120, target = real unsolved
LP2 head). The ONLY change is the adjudicator panel: C1 used EN/LA/GR; this lane uses the
control-VALIDATED language set {EN, LATIN, GREEK, OLD_ENGLISH, ENOCHIAN} (validation from
out_control.json). Old Norse + romanized Hebrew are UNAVAILABLE (PREREG) and absent.

Multiple-comparisons / double-max hazard (PREREG Family-wise bar): the panel-max statistic is
computed identically for BOTH the observed decodes AND the seed-3301 order-matched null, so the
null already carries the max-over-registers and threshold_for(N) on that null is the correctly
inflated family-wise bar for the WIDENED panel. No prefilter-max compounded with panel-max.

A bar-clearing survivor is FLAGGED-FOR-ORACLE (R21-L1 seal), never auto-certified.

Run: PYTHONUTF8=1 python3 readjudicate.py            # writes results.json
     PYTHONUTF8=1 python3 readjudicate.py --topk 40  # slice depth (default 40, = C1)
"""
import os
import sys
import json
import math
import random
import time
import zlib
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
C1 = os.path.join(LP, "analysis", "round24", "C1-matched-runic")
B6 = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round16", "scorer"),
          os.path.join(LP, "analysis", "round11"),
          os.path.join(LP, "analysis", "round13", "B04"),
          os.path.join(LP, "analysis", "round20", "P3"), B6, C1, HERE):
    sys.path.insert(0, p)

from lp import gematria as gp          # noqa
from lp import score as _score         # noqa
import skipdecode as sk                # noqa
import lib_numchannel as nc            # noqa
import ks                              # noqa
import detectors as D                  # noqa
import null as NULLMOD                 # benchmark/null.py  # noqa
from p3b_seedprior import seed_order   # noqa
from greek_corpus import romanized_greek       # noqa
from nonenglish_corpus import old_english, enochian  # noqa
import numpy as np

N = gp.N
Q = _score.default()
BEAM_W, MAX_SKIP = 400, 3
L = 120


def _strip_diacritics(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


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


# ---- validated language-aware trigram panel ----
def _load_validated():
    """Return the list of non-English registers the control validated (out_control.json)."""
    cp = os.path.join(HERE, "out_control.json")
    if not os.path.exists(cp):
        raise SystemExit("out_control.json missing - run control.py first (PREREG Q5).")
    d = json.load(open(cp))
    if not d.get("control_pass"):
        raise SystemExit("control did not pass - no validated non-English register; STOP (PREREG Q5).")
    return d["validated_registers"]


_PANEL = None
_PANEL_KEYS = None


def _build_panel(validated):
    global _PANEL, _PANEL_KEYS
    en = D.text_to_runes(open(os.path.join(LP, "data", "keys", "self_reliance.txt"),
                              encoding="utf-8", errors="ignore").read(), "EN")
    lms = {"EN": D.build_trigram(en)}
    if "LATIN" in validated:
        la = D.text_to_runes(open(os.path.join(LP, "analysis", "latin", "latin_28233.txt"),
                                  encoding="utf-8", errors="ignore").read(), "LA")
        lms["LA"] = D.build_trigram(la)
    if "GREEK" in validated:
        lms["GR"] = D.build_trigram(D.text_to_runes(romanized_greek(), "LA"))
    if "OLD_ENGLISH" in validated:
        lms["OE"] = D.build_trigram(D.text_to_runes(_strip_diacritics(old_english()), "OE"))
    if "ENOCHIAN" in validated:
        lms["EN0"] = D.build_trigram(D.text_to_runes(_strip_diacritics(enochian()), "EN"))
    _PANEL = lms
    _PANEL_KEYS = list(lms.keys())


def panel_scores(idx):
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
    row = {
        "label": label, "sign": sign, "atbash": atb,
        "en_score": round(Q.score_norm(tl), 4),
        "panel_max": round(max(ps.values()), 4),
        "panel_argmax": max(ps, key=ps.get),
        "ioc_n": round(stat_ioc_n(idx), 4),
        "min_distinct_32": stat_min_distinct_32(idx),
        "compress": round(stat_compress(idx), 4),
        "head": tl[:48],
    }
    for k, v in ps.items():
        row[f"panel_{k}"] = v
    return row


def run():
    topk = 40
    for i, a in enumerate(sys.argv):
        if a == "--topk":
            topk = int(sys.argv[i + 1])

    validated = _load_validated()
    _build_panel(validated)

    seeds_int = seed_order(topk)
    C_full = nc.unsolved()[:L]
    gens = ks.GEN_NAMES
    reds = ["mod29", "rej29", "hi_nib", "bits5"]
    signs = [-1, +1]
    atbs = [False, True]
    need = L * (MAX_SKIP + 1) + 512

    rows = []
    t0 = time.time()
    n_decodes = 0
    for sd in seeds_int:
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
                            rows.append(_decode_row(C_full, K, sign, atb, label))
                            n_decodes += 1

    # ---- seed-3301 order-matched null on the SAME real ciphertext, SAME widened panel ----
    rng = random.Random(3301)
    n_null = 400
    null_en, null_panelmax = [], []
    for _ in range(n_null):
        WK = [rng.randrange(N) for _ in range(need)]
        r = _decode_row(C_full, WK, -1, False, "NULL")
        null_en.append(r["en_score"])
        null_panelmax.append(r["panel_max"])

    def summ(v):
        m = sum(v) / len(v)
        sd = math.sqrt(sum((x - m) ** 2 for x in v) / len(v))
        return {"mean": round(m, 4), "sd": round(sd, 4), "max": round(max(v), 4)}

    null = {"n": n_null, "en": summ(null_en), "panel_max": summ(null_panelmax)}

    Nreal = n_decodes
    bar_en = NULLMOD.threshold_for(Nreal, mu=null["en"]["mean"],
                                   beta=NULLMOD.gumbel_params(null["en"]["sd"]))
    bar_panel = NULLMOD.threshold_for(Nreal, mu=null["panel_max"]["mean"],
                                      beta=NULLMOD.gumbel_params(null["panel_max"]["sd"]))

    best_en = max(rows, key=lambda r: r["en_score"])
    best_panel = max(rows, key=lambda r: r["panel_max"])

    def survivors(rows, key, nullmax, bar):
        return [r for r in rows if r[key] > nullmax and r[key] > bar]

    surv_en = survivors(rows, "en_score", null["en"]["max"], bar_en)
    surv_panel = survivors(rows, "panel_max", null["panel_max"]["max"], bar_panel)

    # Expected false-positives AT the family-wise bar (double-max FP-ceiling check, R6/PREREG).
    # For a Gumbel(mu,beta) null, P(one draw > bar) = 1 - exp(-exp(-(bar-mu)/beta)); x N = E[FP].
    def exp_fp(bar, mu, sd, n):
        beta = NULLMOD.gumbel_params(sd) or 1e-9
        p = 1.0 - math.exp(-math.exp(-(bar - mu) / beta))
        return p * n
    fp_en = exp_fp(bar_en, null["en"]["mean"], null["en"]["sd"], Nreal)
    fp_panel = exp_fp(bar_panel, null["panel_max"]["mean"], null["panel_max"]["sd"], Nreal)

    # per-register best (which language, if any, ever leads a decode)
    per_reg_best = {}
    for k in _PANEL_KEYS:
        br = max(rows, key=lambda r: r.get(f"panel_{k}", -99))
        per_reg_best[k] = {"score": br[f"panel_{k}"], "label": br["label"],
                           "head": br["head"]}

    out = {
        "lane": "round24/C1-ext-nonenglish (re-adjudication)",
        "validated_registers": validated,
        "panel_registers": _PANEL_KEYS,
        "unavailable": ["OLD_NORSE (all repo Norse is English translation)",
                        "HEBREW_ROMANIZED (no connected romanized corpus; native script unmappable)"],
        "slice": {"topk_seeds": topk, "generators": gens, "reductions": reds,
                  "signs": signs, "atbash": atbs, "offset": 0, "L": L,
                  "target": "real unsolved LP2 head nc.unsolved()[:120]  (IDENTICAL to C1)"},
        "n_decodes": n_decodes,
        "conditionals": {
            "key_space": f"top-{topk} R20-prior seeds x {len(gens)} gens x {len(reds)} reds "
                         f"x 2 signs x 2 atbash x 2 seed-forms, offset 0  (IDENTICAL to C1)",
            "decoder": "beam_decode(max_skip=3) - one key-skip relation; inherits L7-B",
            "adjudicator": f"EN quadgram + language-aware trigram panel {_PANEL_KEYS} "
                           f"(control-validated) + 4 R3 agnostic stats",
        },
        "null_seed": 3301, "null": null,
        "family_wise_bars": {"en": round(bar_en, 4), "panel_max": round(bar_panel, 4)},
        "expected_fp_at_bar": {"en": round(fp_en, 4), "panel_max": round(fp_panel, 4),
                               "alpha_design": 0.01},
        "best": {
            "en": {"score": best_en["en_score"], "label": best_en["label"], "head": best_en["head"]},
            "panel_max": {"score": best_panel["panel_max"], "label": best_panel["label"],
                          "which": best_panel["panel_argmax"], "head": best_panel["head"]},
        },
        "per_register_best": per_reg_best,
        "survivors": {"en": len(surv_en), "panel_max": len(surv_panel)},
        "survivor_rows": surv_panel[:20],
        "elapsed_s": round(time.time() - t0, 1),
    }
    out["top50_panel"] = sorted(rows, key=lambda r: -r["panel_max"])[:50]

    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)

    print(f"n_decodes = {n_decodes:,}   ({out['elapsed_s']}s)")
    print(f"panel registers = {_PANEL_KEYS}")
    print(f"null(panel_max) mean={null['panel_max']['mean']} sd={null['panel_max']['sd']} "
          f"max={null['panel_max']['max']}")
    print(f"bars  EN={bar_en:.3f}  PANEL={bar_panel:.3f}")
    print(f"best  EN={best_en['en_score']:.3f} ({best_en['label']})")
    print(f"      PANEL={best_panel['panel_max']:.3f} ({best_panel['label']} "
          f"-> {best_panel['panel_argmax']})")
    print(f"expected FP at bar  EN={fp_en:.4f}  PANEL={fp_panel:.4f}  (alpha design 0.01)")
    print(f"survivors  EN={len(surv_en)}  PANEL={len(surv_panel)}")
    print("wrote results.json")


if __name__ == "__main__":
    run()
