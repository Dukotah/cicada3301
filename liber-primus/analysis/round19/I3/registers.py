"""I3 / Round 19 — the 9-register adjudicator panel, as a set of scorers with
INDEPENDENTLY CALIBRATED null curves.

Round 18 L7-A measured what happens when the plaintext is not modern English: the beam
recovers 100 % of the runes and the English quadgram scorer calls the result noise. I2 fixes
that by scoring every decode under a panel. This module builds the panel *for calibration
purposes* — the null of each register has to be measured before a max over the panel means
anything.

THE COMMENSURABILITY PROBLEM, stated once.  The nine registers do not share a scale. The
legacy statistic is a per-quadgram log10 probability over a 22-letter transliteration; the
others are per-trigram log10 probabilities over 29 rune indices, and their entropies differ
by language. On the correct key L7-A.1 measured scores from -3.77 (EN_KJV) to -7.60
(EN_NOVOWEL). A raw `max` over such a panel is not a test: it is a fixed preference for
whichever register has the highest-located null. The panel max must therefore be taken over
each register's OWN null-standardised score,

    z_r = (s_r - mu_r) / beta_r        with (mu_r, beta_r) the register's fitted null curve
    panel_max = max_r z_r

which is what this lane calibrates and what INTERFACE.md requires of I2.

Corpora and folding are reused verbatim from
`round18/L7-redteam/a1_scorer_language.build_panels` so that this lane's registers are the
same objects L7-A measured power against.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (os.path.join(LP, "src"),
           os.path.join(LP, "benchmark"),
           os.path.join(LP, "analysis", "campaign18_skip"),
           os.path.join(LP, "analysis", "round11"),
           os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext"),
           os.path.join(LP, "analysis", "round18", "L7-redteam")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import detectors as D                      # noqa: E402

N = 29

# The nine registers of the panel. EN_QUAD is the LEGACY statistic (the repo's translit
# quadgram score_norm) and is carried so that the panel remains backward comparable.
PANEL = ["EN_QUAD", "EN_MODERN", "LP1_REAL", "LATIN", "OE", "DE", "CY",
         "EN_HALFVOWEL", "EN_NOVOWEL"]
TRI_REGISTERS = [r for r in PANEL if r != "EN_QUAD"]

_LMS = None


def build_lms(cache=True):
    """(9-1) rune-space trigram LMs, one per non-legacy register. Cached as .npz."""
    global _LMS
    if _LMS is not None:
        return _LMS
    path = os.path.join(HERE, "_lms.npz")
    if cache and os.path.exists(path):
        z = np.load(path)
        _LMS = {k: z[k] for k in z.files}
        return _LMS
    from a1_scorer_language import build_panels      # noqa: E402
    panels = build_panels()
    lms = {}
    for r in TRI_REGISTERS:
        lms[r] = D.build_trigram(np.asarray(panels[r], dtype=np.int64))
    if cache:
        np.savez_compressed(path, **lms)
    _LMS = lms
    return lms


def score_panel_rescore(plain, lms=None):
    """PANEL MODE 'rescore': one English-driven beam decode, nine scorings of its output.

    plain (T, L) int rune indices. Returns {register: (T,)} for the 8 trigram registers.
    This is the CHEAP panel: 1 decode per trial. Its cost is that the decode path was
    chosen to maximise ENGLISH, so a non-English register sees a path that is not its own
    argmax — which lowers both its null and its power.
    """
    lms = lms or build_lms()
    p = np.asarray(plain, dtype=np.int64)
    a, b, c = p[:, :-2], p[:, 1:-1], p[:, 2:]
    return {r: lms[r][a, b, c].mean(axis=1) for r in TRI_REGISTERS}


def corpus_sizes():
    from a1_scorer_language import build_panels      # noqa: E402
    return {k: len(v) for k, v in build_panels().items()}


if __name__ == "__main__":
    lms = build_lms()
    print(json.dumps({k: list(v.shape) for k, v in lms.items()}, indent=2))
