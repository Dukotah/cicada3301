"""Seven-register LITE panel for lane I1 (Round 32).

round19/I2/models/panel.npz cannot be rebuilt on this checkout: data/keys/mabinogion.txt,
data/kjv.txt and data/keys/welsh/welsh_mabinogion.txt are absent.  This builds the same
statistic (adjudicate.Panel npz format, same interpolated trigram, lambdas, null recipe) over the
registers that ARE buildable: EN_MODERN (self_reliance only), LP1_REAL (solved pages mixed 0.5
with EN_MODERN train in place of the KJV backbone), LATIN, OE, DE, EN_HALFVOWEL, EN_NOVOWEL.
EN_KJV and CY are NOT covered.  Its z scale is NOT the I2 panel's, so I3's calib19 cells do not
apply; lane I1 uses its own shuffle-null bars.
"""
import os, sys, re, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import beam_v2  # noqa: F401  (sets sys.path)
import build_models as BM
import detectors as D
import skipdecode as sk

LEN_GRID = [32, 64, 120, 240, 400, 800]
NDRAWS = 3000
REGS = ["EN_MODERN", "LP1_REAL", "LATIN", "OE", "DE", "EN_HALFVOWEL", "EN_NOVOWEL"]


def corpora():
    f = lambda *a: os.path.join(BM.LP, *a)
    en_raw = BM._read(f("data", "keys", "self_reliance.txt"))
    P = {"EN_MODERN": D.text_to_runes(en_raw, "EN"),
         "LATIN": D.text_to_runes(BM._mid(BM._read(f("analysis", "latin", "latin_218.txt")))
                                  + BM._mid(BM._read(f("analysis", "latin", "latin_28233.txt"))), "LA")}
    oe_raw = BM._read(os.path.join(BM.B6, "corpora", "oe_beowulf.txt"))
    oe = "\n".join(l for l in oe_raw.split("\n") if re.search("[þðæÞÐÆ]", l))
    oe += BM._read(f("data", "keys", "runepoem_oe.txt"))
    P["OE"] = D.text_to_runes(oe, "OE")
    P["DE"] = D.text_to_runes(BM._mid(BM._read(os.path.join(BM.B6, "corpora", "de_faust.txt")))
                              + BM._mid(BM._read(os.path.join(BM.B6, "corpora", "de_2.txt"))), "DE")
    P["EN_NOVOWEL"] = D.text_to_runes(BM._drop_vowels(en_raw, 1.0), "EN")
    P["EN_HALFVOWEL"] = D.text_to_runes(BM._drop_vowels(en_raw, 0.5), "EN")
    sp = json.load(open(f("SOLVED-PAGES.json"), encoding="utf-8"))
    P["LP1_REAL"] = np.concatenate([np.array(sk.eng_to_idx(p["plaintext_transliteration"]), dtype=np.int64)
                                    for p in sp["pages"]])
    return P


def main():
    P = corpora()
    train, test = {}, {}
    for r in REGS:
        if r == "LP1_REAL":
            train[r] = test[r] = P[r]
            continue
        a, b = BM.split_half(P[r])
        train[r], test[r] = a, b
    lms = {}
    for r in REGS:
        if r == "LP1_REAL":
            lms[r] = BM.build_lm(P[r], extra_counts=train["EN_MODERN"], mix=BM.LP1_MIX)
        else:
            lms[r] = BM.build_lm(train[r])
    LM = np.stack([lms[r] for r in REGS])
    LMF = LM.reshape(len(REGS), -1)
    mu, sd, corr, _ = BM.calibrate(LMF, LEN_GRID, NDRAWS)
    os.makedirs(os.path.join(HERE, "models"), exist_ok=True)
    np.savez_compressed(os.path.join(HERE, "models", "panel_lite.npz"),
                        registers=np.array(REGS), LM=LM.astype(np.float32),
                        len_grid=np.array(LEN_GRID), mu=mu, sd=sd, corr=corr,
                        lambdas=np.array(BM.LAMBDAS), null_draws=np.array([NDRAWS]),
                        null_seed=np.array([BM.NULL_SEED]))
    np.savez_compressed(os.path.join(HERE, "models", "testhalves_lite.npz"),
                        **{r: test[r].astype(np.int16) for r in REGS})
    print({r: (len(train[r]), len(test[r])) for r in REGS})


if __name__ == "__main__":
    main()
