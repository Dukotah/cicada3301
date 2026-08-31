"""Round 24 / C1-EXT — POSITIVE CONTROL for genuinely LANGUAGE-AWARE non-English adjudication.

For each register, plant its text into rune indices, encipher under the real key + pinned filter,
decode with the CORRECT key, and adjudicate the recovered plain_idx under BOTH:
  - the repo English quadgram scorer (the historic gate), and
  - that register's OWN language-aware rune-TRIGRAM LM (built from its own corpus).

Power = fraction of correct-key replicates whose language-LM score exceeds that register's OWN
seed-3301 order-matched wrong-key null MAX. CONTROL PASS for a register iff its language-LM power
> the English quadgram power on that register's planted text (L7-A direction: English underpowered
on the non-English language, the language-aware LM powered). A register that FAILS control is
UNVALIDATED and MUST be dropped from the real re-adjudication panel (PREREG Q5).

Registers: LATIN, GREEK (calibration, carried from C1), OLD_ENGLISH, ENOCHIAN (tentative),
EN_MODERN (upper bound), EN_NOVOWEL (L7-A 0.00 case), RAND (floor).
Old Norse and romanized Hebrew are UNAVAILABLE (PREREG) and NOT modelled here.

Run: PYTHONUTF8=1 python3 control.py           # writes out_control.json
     PYTHONUTF8=1 python3 control.py --quick   # fewer reps
"""
import os
import sys
import json
import random
import re
import statistics
import time
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
C1 = os.path.join(LP, "analysis", "round24", "C1-matched-runic")
B6 = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round16", "scorer"), B6, C1, HERE):
    sys.path.insert(0, p)

from lp import gematria as gp          # noqa
from lp import score as _score         # noqa
import skipdecode as sk                # noqa
import plant as PL                     # noqa
import detectors as D                  # noqa
from greek_corpus import romanized_greek      # noqa  (C1's Greek corpus)
from nonenglish_corpus import old_english, enochian  # noqa

N = gp.N
Q = _score.default()                   # English quadgram scorer (repo default)
BEAM_W, MAX_SKIP, SUPP = 400, 3, 0.83
LENGTHS = [120]
NREP = 24
NNULL = 60
SEED0 = 33010


def _read(p):
    return open(p, encoding="utf-8", errors="ignore").read()


def _mid(t):
    return t[len(t) // 8: -len(t) // 8] if len(t) > 40000 else t


def _drop_vowels(text):
    return "".join(c for c in text.upper() if c not in "AEIOUY")


def _strip_diacritics(s):
    """Fold macrons/accents to base letters so OE long vowels survive text_to_runes (which
    strips non-A-Z). WITHOUT this, macron vowels vanish and OE looks vowel-dropped -> unfair."""
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def build_registers():
    """Return {name: (rune_index_list, fold_lang)} for planting AND {name: LM} for scoring."""
    reg = {}
    en = _mid(_read(os.path.join(LP, "data", "keys", "self_reliance.txt"))) + \
        _mid(_read(os.path.join(LP, "data", "keys", "mabinogion.txt")))
    la = _mid(_read(os.path.join(LP, "analysis", "latin", "latin_218.txt"))) + \
        _mid(_read(os.path.join(LP, "analysis", "latin", "latin_28233.txt")))
    oe = _strip_diacritics(old_english())
    eno = _strip_diacritics(enochian())

    reg["EN_MODERN"] = D.text_to_runes(en, "EN").tolist()
    reg["LATIN"] = D.text_to_runes(la, "LA").tolist()
    reg["GREEK"] = D.text_to_runes(romanized_greek(), "LA").tolist()
    reg["OLD_ENGLISH"] = D.text_to_runes(oe, "OE").tolist()
    reg["ENOCHIAN"] = D.text_to_runes(eno, "EN").tolist()
    reg["EN_NOVOWEL"] = D.text_to_runes(_drop_vowels(en), "EN").tolist()
    r = random.Random(3301)
    reg["RAND"] = [r.randrange(N) for _ in range(60000)]

    # Language-aware rune-trigram LMs, each built from its OWN corpus.
    import numpy as np
    lm = {}
    lm["EN_MODERN"] = D.build_trigram(np.array(reg["EN_MODERN"], dtype=np.int64))
    lm["LATIN"] = D.build_trigram(np.array(reg["LATIN"], dtype=np.int64))
    lm["GREEK"] = D.build_trigram(np.array(reg["GREEK"], dtype=np.int64))
    lm["OLD_ENGLISH"] = D.build_trigram(np.array(reg["OLD_ENGLISH"], dtype=np.int64))
    lm["ENOCHIAN"] = D.build_trigram(np.array(reg["ENOCHIAN"], dtype=np.int64))
    lm["EN_NOVOWEL"] = D.build_trigram(np.array(reg["EN_NOVOWEL"], dtype=np.int64))
    lm["RAND"] = lm["EN_MODERN"]  # RAND scored under EN LM (floor); its own LM is meaningless
    return reg, lm


def _decode_correct(P_idx, L, rep):
    rng = random.Random(SEED0 + rep * 977 + L)
    if len(P_idx) < L + 10:
        return None
    start = rng.randrange(0, len(P_idx) - L - 1)
    P = P_idx[start:start + L]
    need = L * (MAX_SKIP + 1) + 512
    K = PL.make_key("sha256_ctr", length=need, seed=b"CICADA3301")
    C, skips, _ = sk.encipher_keyskip(P, K, sign=-1, supp=SUPP, seed=SEED0 + rep)
    bd = sk.beam_decode(C, K, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
    rec = sum(1 for a, b in zip(bd["plain_idx"], P) if a == b) / len(P)
    return rec, bd["plain_idx"], sk.idx_to_trans(bd["plain_idx"]), C


def run():
    import numpy as np
    quick = "--quick" in sys.argv
    lengths = LENGTHS
    nrep = 8 if quick else NREP
    nnull = 30 if quick else NNULL

    reg, LM = build_registers()
    out = {
        "lane": "round24/C1-ext-nonenglish (control)",
        "instrument": ("encipher_keyskip(supp=0.83) -> beam_decode(400,3) CORRECT key; "
                       "adjudicate recovered plain_idx under EN quadgram AND per-register "
                       "language-aware rune-trigram LM"),
        "key_family": "sha256_ctr(seed=CICADA3301)  [B-04/D3 live class]",
        "null": "seed-3301 order-matched uniform-random wrong-key decodes, per register x length",
        "nrep": nrep, "nnull": nnull, "lengths": lengths,
        "register_sizes": {k: len(v) for k, v in reg.items()},
        "note_unavailable": {
            "OLD_NORSE": "no non-translation Latin-script Old Norse in repo (all Eddas/sagas are "
                         "English translations) -> UNAVAILABLE, not modelled",
            "HEBREW_ROMANIZED": "only isolated romanized proper nouns; 18k chars are NATIVE script "
                                "(unmappable to Latin runes) -> UNAVAILABLE, not modelled",
        },
        "summary": {},
    }
    rng_null = random.Random(3301)
    t0 = time.time()

    for name, idxs in reg.items():
        for L in lengths:
            corr = []
            for rep in range(nrep):
                d = _decode_correct(idxs, L, rep)
                if d:
                    corr.append(d)
            if not corr:
                continue
            lm = LM[name]
            en_corr = [Q.score_norm(t) for _, _, t, _ in corr]
            lm_corr = [D.score_trigram(lm, np.array(pi, dtype=np.int64))
                       for _, pi, _, _ in corr]
            rec = [r for r, _, _, _ in corr]

            en_null, lm_null = [], []
            for j in range(nnull):
                _, _, _, C = corr[j % len(corr)]
                WK = [rng_null.randrange(N) for _ in range(len(C) * (MAX_SKIP + 1) + 8)]
                wd = sk.beam_decode(C, WK, sign=-1, o=0, beam_w=BEAM_W, max_skip=MAX_SKIP)
                wt = sk.idx_to_trans(wd["plain_idx"])
                en_null.append(Q.score_norm(wt))
                lm_null.append(D.score_trigram(lm, np.array(wd["plain_idx"], dtype=np.int64)))
            en_bar = max(en_null)
            lm_bar = max(lm_null)

            # (a) power = fraction of correct-key decodes above that scorer's OWN order-matched
            #     null MAX (both saturate at 1.0 for clean languages -> not discriminating enough).
            en_power = sum(1 for s in en_corr if s > en_bar) / len(en_corr)
            lm_power = sum(1 for s in lm_corr if s > lm_bar) / len(lm_corr)

            # (b) d-prime = (median correct-key score - null mean) / null sd. Scale-free measure of
            #     how far the correct-key SIGNAL sits above the wrong-key noise floor. THIS is the
            #     honest L7-A instrument-power comparison across scorers on different score scales.
            def dprime(corr_scores, null_scores):
                nm = statistics.fmean(null_scores)
                nsd = statistics.pstdev(null_scores) or 1e-9
                return (statistics.median(corr_scores) - nm) / nsd
            en_d = dprime(en_corr, en_null)
            lm_d = dprime(lm_corr, lm_null)

            key = f"{name}|{L}"
            # Control pass for a register = its language-aware LM discriminates its OWN planted
            # language BETTER than the English quadgram scorer does (larger d-prime). This is the
            # measured L7-A gap: English underpowered on the non-English language.
            passed = lm_d > en_d
            out["summary"][key] = {
                "panel": name, "L": L, "n": len(corr),
                "median_recovery": round(statistics.median(rec), 4),
                "median_correct_EN": round(statistics.median(en_corr), 4),
                "median_correct_LM": round(statistics.median(lm_corr), 4),
                "null_max_EN": round(en_bar, 4),
                "null_max_LM": round(lm_bar, 4),
                "null_mean_LM": round(statistics.fmean(lm_null), 4),
                "null_sd_LM": round(statistics.pstdev(lm_null), 4),
                "power_EN": en_power,
                "power_LM": lm_power,
                "dprime_EN": round(en_d, 3),
                "dprime_LM": round(lm_d, 3),
                "lm_beats_english": passed,
            }
            s = out["summary"][key]
            print(f"  {name:12s} L={L:3d} rec={s['median_recovery']:.0%} "
                  f"EN corr={s['median_correct_EN']:8.3f} LM corr={s['median_correct_LM']:8.3f} | "
                  f"d' EN={en_d:6.2f} LM={lm_d:6.2f} | "
                  f"pow EN={en_power:.2f} LM={lm_power:.2f}  "
                  f"{'<<LM WINS (validated)' if passed else ''}")

    # Which non-English registers VALIDATE (control pass) -> eligible for the real panel.
    noneng = ("LATIN", "GREEK", "OLD_ENGLISH", "ENOCHIAN")
    validated = [k.split("|")[0] for k, v in out["summary"].items()
                 if v["panel"] in noneng and v["lm_beats_english"] and v["L"] == 120]
    out["validated_registers"] = sorted(set(validated))
    out["control_pass"] = len(out["validated_registers"]) > 0
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "out_control.json"), "w"), indent=1)
    print(f"\nvalidated non-English registers = {out['validated_registers']}")
    print(f"control_pass={out['control_pass']}  ({out['elapsed_s']}s)  wrote out_control.json")


if __name__ == "__main__":
    run()
