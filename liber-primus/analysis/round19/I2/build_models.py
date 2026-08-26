"""I2 / build — the register panel and its null calibration.

Builds nine interpolated rune-index trigram language models (the "register panel") plus the
Monte-Carlo null calibration that turns their raw scores into comparable z statistics, and
writes both to `models/panel.npz` (gitignored, rebuildable by this script) together with a
committed `out_build.json` recording every training corpus and its SHA-256.

Design is fixed in PREREG.md s2 and is NOT tuned here:

  * model form      : Jelinek-Mercer interpolated trigram over rune indices 0..28,
                      lambdas (0.70, 0.20, 0.09, 0.01) fixed a priori
  * held-out split  : first half of each corpus TRAINS, second half is reserved for plants
  * LP1_REAL        : 0.5 * trigram(solved pages) + 0.5 * trigram(EN_KJV train), mixed in
                      probability space; plus five leave-one-page-out variants for the
                      held-out power measurement
  * null            : 20,000 uniform-random rune strings at each of 14 grid lengths

Everything is scored on RUNE INDICES, never on the transliteration string (doctrine s4 r5).

    python3 build_models.py            # full build  (~2 min)
    python3 build_models.py --quick    # 2,000 null draws, for smoke tests
"""
import hashlib
import json
import os
import random
import re
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # liber-primus/
B6 = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")
for _p in (os.path.join(LP, "src"),
           os.path.join(LP, "benchmark"),
           os.path.join(LP, "analysis", "campaign18_skip"),
           os.path.join(LP, "analysis", "round11"),
           B6):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import detectors as D                       # noqa: E402  (text_to_runes, unchanged)
import skipdecode as sk                     # noqa: E402  (eng_to_idx, the validated mapping)

N = 29
MODELDIR = os.path.join(HERE, "models")

# ---- fixed a priori in PREREG.md s2.1; never re-chosen after seeing power -------------
LAMBDAS = (0.70, 0.20, 0.09, 0.01)          # l3 trigram, l2 bigram, l1 unigram, l0 uniform
LP1_MIX = 0.5                               # LP1 own-trigram weight against the KJV backbone

REGISTERS = ["EN_MODERN", "EN_KJV", "LP1_REAL", "LATIN", "OE", "DE", "CY",
             "EN_HALFVOWEL", "EN_NOVOWEL"]
ENGLISH_REF = "EN_MODERN"                   # the model pcon regresses out
NON_ENGLISH = ["LP1_REAL", "LATIN", "OE", "DE", "CY", "EN_HALFVOWEL", "EN_NOVOWEL"]

LEN_GRID = [32, 48, 64, 96, 128, 160, 200, 240, 320, 400, 500, 640, 800, 1000]
NULL_DRAWS = 20000
NULL_SEED = 3301


# ------------------------------------------------------------------ corpus loading
def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def _read(p):
    with open(p, encoding="utf-8", errors="ignore") as f:
        return f.read()


def _mid(t):
    """Drop Gutenberg boiler-plate head/tail crudely -- L7-A / B6's loader, verbatim."""
    return t[len(t) // 8: -len(t) // 8] if len(t) > 40000 else t


def _drop_vowels(text, frac=1.0, seed=7):
    """L7-A's abbreviation model, verbatim."""
    r = random.Random(seed)
    out = []
    for ch in text.upper():
        if ch in "AEIOUY" and (frac >= 1.0 or r.random() < frac):
            continue
        out.append(ch)
    return "".join(out)


def load_corpora():
    """register -> (rune index array, [source file paths]).

    Identical sources and identical loader to round18/L7-redteam/a1_scorer_language.py, so
    the corpora are literally L7-A's corpora and the two lanes' numbers are comparable.
    """
    src = {}
    P = {}

    f_self = os.path.join(LP, "data", "keys", "self_reliance.txt")
    f_mab = os.path.join(LP, "data", "keys", "mabinogion.txt")
    en_held = _mid(_read(f_self)) + _mid(_read(f_mab))
    P["EN_MODERN"] = D.text_to_runes(en_held, "EN")
    src["EN_MODERN"] = [f_self, f_mab]

    f_kjv = os.path.join(LP, "data", "kjv.txt")
    P["EN_KJV"] = D.text_to_runes(_mid(_read(f_kjv))[:900000], "EN")
    src["EN_KJV"] = [f_kjv]

    f_sp = os.path.join(LP, "SOLVED-PAGES.json")
    sp = json.load(open(f_sp, encoding="utf-8"))
    P["_LP1_PAGES"] = [np.array(sk.eng_to_idx(p["plaintext_transliteration"]), dtype=np.int64)
                       for p in sp["pages"]]
    P["LP1_REAL"] = np.concatenate(P["_LP1_PAGES"])
    src["LP1_REAL"] = [f_sp]

    f_la1 = os.path.join(LP, "analysis", "latin", "latin_218.txt")
    f_la2 = os.path.join(LP, "analysis", "latin", "latin_28233.txt")
    P["LATIN"] = D.text_to_runes(_mid(_read(f_la1)) + _mid(_read(f_la2)), "LA")
    src["LATIN"] = [f_la1, f_la2]

    f_oe1 = os.path.join(B6, "corpora", "oe_beowulf.txt")
    f_oe2 = os.path.join(LP, "data", "keys", "runepoem_oe.txt")
    oe_raw = _read(f_oe1)
    oe = "\n".join(l for l in oe_raw.split("\n") if re.search(r"[þðæÞÐÆ]", l))
    oe += _read(f_oe2)
    P["OE"] = D.text_to_runes(oe, "OE")
    src["OE"] = [f_oe1, f_oe2]

    f_de1 = os.path.join(B6, "corpora", "de_faust.txt")
    f_de2 = os.path.join(B6, "corpora", "de_2.txt")
    P["DE"] = D.text_to_runes(_mid(_read(f_de1)) + _mid(_read(f_de2)), "DE")
    src["DE"] = [f_de1, f_de2]

    f_cy = os.path.join(LP, "data", "keys", "welsh", "welsh_mabinogion.txt")
    P["CY"] = D.text_to_runes(_mid(_read(f_cy)), "CY")
    src["CY"] = [f_cy]

    P["EN_NOVOWEL"] = D.text_to_runes(_drop_vowels(en_held, 1.0), "EN")
    src["EN_NOVOWEL"] = [f_self, f_mab]
    P["EN_HALFVOWEL"] = D.text_to_runes(_drop_vowels(en_held, 0.5), "EN")
    src["EN_HALFVOWEL"] = [f_self, f_mab]

    return P, src


def split_half(a):
    """PREREG s2.1: first half TRAINS, second half is reserved for plant windows."""
    h = len(a) // 2
    return a[:h], a[h:]


# ------------------------------------------------------------------ the model
def build_lm(runes, lams=LAMBDAS, extra_counts=None, mix=None):
    """Interpolated trigram over rune indices -> dense log10 table, shape (29,29,29).

    Backoff mass from an unseen context is redistributed to the lower orders, so every
    conditional distribution sums to exactly 1 (no silent leakage into the floor).

    `extra_counts` / `mix`: if given, the trigram probability table is mixed in PROBABILITY
    space as  mix*P(this corpus) + (1-mix)*P(extra corpus).  Used for LP1_REAL, whose 1,769
    runes cannot support a standalone trigram (PREREG s2.1).
    """
    def probs(r):
        r = np.asarray(r, dtype=np.int64)
        c3 = np.zeros((N, N, N), dtype=np.float64)
        c2 = np.zeros((N, N), dtype=np.float64)
        c1 = np.zeros(N, dtype=np.float64)
        if len(r) >= 3:
            np.add.at(c3, (r[:-2], r[1:-1], r[2:]), 1.0)
        if len(r) >= 2:
            np.add.at(c2, (r[:-1], r[1:]), 1.0)
        np.add.at(c1, r, 1.0)

        l3, l2, l1, _l0 = lams
        s3 = c3.sum(axis=2, keepdims=True)
        P3 = np.where(s3 > 0, c3 / np.maximum(s3, 1.0), 0.0)
        w3 = np.where(s3 > 0, l3, 0.0)                       # (N,N,1)

        s2 = c2.sum(axis=1, keepdims=True)
        P2 = np.where(s2 > 0, c2 / np.maximum(s2, 1.0), 0.0)  # (N,N)
        w2 = np.where(s2 > 0, l2, 0.0)                        # (N,1)

        s1 = c1.sum()
        P1 = c1 / s1 if s1 > 0 else np.full(N, 1.0 / N)
        w1 = l1 if s1 > 0 else 0.0

        Pm = (w3 * P3
              + (w2 * P2)[None, :, :] * np.ones((N, 1, 1))
              + w1 * P1[None, None, :])
        rest = 1.0 - w3 - w2[None, :, :] - w1
        Pm = Pm + rest / N
        return Pm

    Pm = probs(runes)
    if extra_counts is not None and mix is not None:
        Pm = mix * Pm + (1.0 - mix) * probs(extra_counts)
    Pm = np.maximum(Pm, 1e-12)
    Pm /= Pm.sum(axis=2, keepdims=True)
    return np.log10(Pm)


# ------------------------------------------------------------------ vectorised scoring
def flat_idx(x):
    x = np.asarray(x, dtype=np.int64)
    return x[..., :-2] * (N * N) + x[..., 1:-1] * N + x[..., 2:]


def score_panel_flat(LMF, x):
    """LMF: (R, 29^3) float64.  x: (L,) rune indices -> (R,) mean log10 per position."""
    f = flat_idx(x)
    if f.size == 0:
        return np.full(LMF.shape[0], -9.9)
    return LMF[:, f].mean(axis=1)


def score_panel_batch(LMF, X, chunk=400):
    """X: (B, L) -> (B, R)."""
    B = X.shape[0]
    out = np.empty((B, LMF.shape[0]))
    for s in range(0, B, chunk):
        f = flat_idx(X[s:s + chunk])                 # (b, L-2)
        out[s:s + chunk] = LMF[:, f].mean(axis=2).T  # (R, b) -> (b, R)
    return out


# ------------------------------------------------------------------ null calibration
def calibrate(LMF, lengths, ndraws, seed=NULL_SEED):
    """Uniform-random-rune null: mu, sd per (L, register) and the 9x9 correlation matrix.

    Returns arrays mu (nL, R), sd (nL, R), corr (nL, R, R) and the raw z-quantiles that I3
    needs for the max-over-panel inflation measurement.
    """
    rng = np.random.default_rng(seed)
    R = LMF.shape[0]
    nL = len(lengths)
    mu = np.zeros((nL, R))
    sd = np.zeros((nL, R))
    corr = np.zeros((nL, R, R))
    qs = {}
    for i, L in enumerate(lengths):
        vals = np.empty((ndraws, R))
        done = 0
        while done < ndraws:
            b = min(400, ndraws - done)
            X = rng.integers(0, N, size=(b, L))
            vals[done:done + b] = score_panel_batch(LMF, X)
            done += b
        mu[i] = vals.mean(axis=0)
        sd[i] = vals.std(axis=0, ddof=1)
        Z = (vals - mu[i]) / sd[i]
        corr[i] = np.corrcoef(Z, rowvar=False)
        qs[str(L)] = {"n": int(ndraws),
                      "z_quantiles": {str(q): np.quantile(Z, q, axis=0).round(4).tolist()
                                      for q in (0.5, 0.9, 0.99, 0.999, 0.9999)}}
    return mu, sd, corr, qs


# ------------------------------------------------------------------ main
def main():
    quick = "--quick" in sys.argv
    ndraws = 2000 if quick else NULL_DRAWS
    t0 = time.time()
    os.makedirs(MODELDIR, exist_ok=True)

    print("loading corpora ...")
    P, src = load_corpora()

    train, test = {}, {}
    for r in REGISTERS:
        if r == "LP1_REAL":
            continue
        a, b = split_half(P[r])
        train[r], test[r] = a, b
    # LP1_REAL: too small to halve; leave-one-page-out is its held-out protocol.
    train["LP1_REAL"] = P["LP1_REAL"]
    test["LP1_REAL"] = P["LP1_REAL"]

    print("building panel (held-out: TRAIN halves only) ...")
    lms = {}
    for r in REGISTERS:
        if r == "LP1_REAL":
            lms[r] = build_lm(P["LP1_REAL"], extra_counts=train["EN_KJV"], mix=LP1_MIX)
        else:
            lms[r] = build_lm(train[r])
        print(f"  {r:14s} train {len(train[r]):8d} runes   test {len(test[r]):8d}")

    # leave-one-page-out LP1 variants, for the held-out LP1 power measurement only
    pages = P["_LP1_PAGES"]
    lp1_loo = []
    for i in range(len(pages)):
        rest = np.concatenate([p for j, p in enumerate(pages) if j != i])
        lp1_loo.append(build_lm(rest, extra_counts=train["EN_KJV"], mix=LP1_MIX))

    LM = np.stack([lms[r] for r in REGISTERS])            # (R,29,29,29)
    LMF = LM.reshape(len(REGISTERS), -1)                  # (R, 24389)

    print(f"calibrating null ({ndraws} draws x {len(LEN_GRID)} lengths) ...")
    mu, sd, corr, qs = calibrate(LMF, LEN_GRID, ndraws)
    for i, L in enumerate(LEN_GRID[:4] + LEN_GRID[-2:]):
        j = LEN_GRID.index(L)
        print(f"  L={L:4d}  mu[EN]={mu[j,0]:7.4f}  sd[EN]={sd[j,0]:6.4f}  "
              f"rho(OE,EN)={corr[j,0,REGISTERS.index('OE')]:5.3f}")

    np.savez_compressed(
        os.path.join(MODELDIR, "panel.npz"),
        registers=np.array(REGISTERS), LM=LM.astype(np.float32),
        LP1_LOO=np.stack(lp1_loo).astype(np.float32),
        len_grid=np.array(LEN_GRID), mu=mu, sd=sd, corr=corr,
        lambdas=np.array(LAMBDAS), lp1_mix=np.array([LP1_MIX]),
        null_draws=np.array([ndraws]), null_seed=np.array([NULL_SEED]))

    # test-half rune streams, so the power lane plants only from held-out text
    np.savez_compressed(
        os.path.join(MODELDIR, "testhalves.npz"),
        **{r: test[r].astype(np.int16) for r in REGISTERS},
        **{f"LP1PAGE{i}": p.astype(np.int16) for i, p in enumerate(pages)})

    out = {
        "lane": "round19/I2",
        "built": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model_form": ("Jelinek-Mercer interpolated trigram over rune indices 0..28; "
                       "lambdas (l3,l2,l1,l0)=(0.70,0.20,0.09,0.01) fixed a priori in "
                       "PREREG.md s2.1; backoff mass from unseen contexts redistributed to "
                       "lower orders so every conditional sums to 1"),
        "registers": REGISTERS,
        "english_ref": ENGLISH_REF,
        "non_english": NON_ENGLISH,
        "held_out_rule": ("first half of each corpus TRAINS, second half reserved for plant "
                          "windows; LP1_REAL uses leave-one-page-out instead (1,769 runes)"),
        "corpora": {r: [{"path": os.path.relpath(p, LP), "sha256": _sha(p),
                         "bytes": os.path.getsize(p)} for p in src[r]] for r in REGISTERS},
        "rune_counts": {r: {"total": int(len(P[r])), "train": int(len(train[r])),
                            "test": int(len(test[r]))} for r in REGISTERS},
        "lp1_page_runes": [int(len(p)) for p in pages],
        "null": {"len_grid": LEN_GRID, "draws_per_length": ndraws, "seed": NULL_SEED,
                 "source": "uniform random rune strings",
                 "mu": {r: mu[:, i].round(5).tolist() for i, r in enumerate(REGISTERS)},
                 "sd": {r: sd[:, i].round(5).tolist() for i, r in enumerate(REGISTERS)},
                 "rho_vs_EN_MODERN": {r: corr[:, REGISTERS.index(ENGLISH_REF), i].round(4).tolist()
                                      for i, r in enumerate(REGISTERS)},
                 "corr_at_L240": corr[LEN_GRID.index(240)].round(4).tolist(),
                 "z_quantiles": qs},
        "artifacts": {"models/panel.npz": "gitignored, rebuilt by build_models.py",
                      "models/testhalves.npz": "gitignored, rebuilt by build_models.py"},
        "elapsed_s": round(time.time() - t0, 1),
    }
    json.dump(out, open(os.path.join(HERE, "out_build.json"), "w"), indent=1)
    print(f"\nwrote models/panel.npz + out_build.json  ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
