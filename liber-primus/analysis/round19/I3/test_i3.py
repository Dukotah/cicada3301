"""I3 / Round 19 — tests.

    python3 -m pytest liber-primus/analysis/round19/I3/test_i3.py -q

G-BACKCOMPAT is the load-bearing one: every published number in `LEDGER.json` was compared
against `benchmark/null.py: threshold_for`, so the extended API has to return exactly the
same value for the English/keyskip1/score_norm cell or the ledger stops being comparable
with itself.
"""
import math
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LP, "benchmark"))

import nullcurve19 as NC          # noqa: E402
import null as LEGACY             # noqa: E402  (benchmark/null.py)

NS = [2, 3, 200, 10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7, 10 ** 8,
      313_000_000, 10 ** 9, 10 ** 10, 17_058_157_809]
LS = [None, 25, 31, 120, 240, 400]
ALPHAS = [0.001, 0.01, 0.05, 0.1]


# ------------------------------------------------------------------ G-BACKCOMPAT
def test_backcompat_default_signature():
    """threshold_for(n) and threshold_for(n, L) must be bit-identical to benchmark/null.py."""
    bad = []
    for n in NS:
        for L in LS:
            a, b = NC.threshold_for(n, L), LEGACY.threshold_for(n, L)
            if a != b:
                bad.append((n, L, a, b))
    assert not bad, f"legacy cell diverged in {len(bad)} places: {bad[:5]}"


def test_backcompat_every_keyword():
    bad = []
    for n in NS:
        for al in ALPHAS:
            for mu, beta, floor in ((NC.DEFAULT_MU, NC.DEFAULT_BETA, NC.FIXED_BAR),
                                    (-7.0, 0.10, -5.5), (-7.5, 0.05, -6.0),
                                    (-7.2517, 0.0725, -99.0)):
                a = NC.threshold_for(n, None, alpha=al, mu=mu, beta=beta, floor=floor)
                b = LEGACY.threshold_for(n, None, alpha=al, mu=mu, beta=beta, floor=floor)
                if a != b:
                    bad.append((n, al, mu, beta, floor, a, b))
    assert not bad, f"keyword path diverged: {bad[:5]}"


def test_backcompat_expected_max():
    for n in NS:
        assert NC.expected_max(n) == LEGACY.expected_max(n)


def test_backcompat_docstring_invariants():
    """The two properties benchmark/null.py's own doctests assert."""
    assert round(NC.threshold_for(200), 2) == -5.5
    assert NC.threshold_for(10 ** 9) > NC.threshold_for(10 ** 3)


def test_legacy_floor_crossing_unmoved():
    """N* = 3.13e8 is quoted in L7-C.5; it must not move."""
    lo, hi = 10 ** 6, 10 ** 10
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if NC.threshold_for(mid) > NC.FIXED_BAR:
            hi = mid
        else:
            lo = mid
    assert abs(hi / 3.13e8 - 1) < 0.02, f"floor crossing moved to {hi:.3e}"


# ------------------------------------------------------------------ new-API discipline
def test_unmeasured_cell_raises_rather_than_substituting_english():
    with pytest.raises(KeyError):
        NC.threshold_for(10 ** 6, 120, register="KLINGON", mode="keyskip1")


def test_permissive_mode_does_not_silently_reuse_the_keyskip1_bar():
    """A bar calibrated under keyskip1 is invalid under a permissive relation."""
    if not NC.calib()["cells"]:
        pytest.skip("no calibration file yet")
    with pytest.raises(KeyError):
        NC.threshold_for(10 ** 6, 120, register="EN_QUAD", mode="union0_001")


def test_length_correction_is_opt_in_only():
    for L in (31, 240, 400):
        assert NC.threshold_for(10 ** 9, L) == NC.threshold_for(10 ** 9, None)
    assert (NC.threshold_for(10 ** 9, 31, length_correct=True)
            > NC.threshold_for(10 ** 9, 31))


# ------------------------------------------------------------------ the fitter
def test_fitter_recovers_a_planted_gumbel():
    from scipy import stats
    mu, beta = -7.25, 0.0725
    v = stats.gumbel_r.rvs(loc=mu, scale=beta, size=400_000,
                           random_state=np.random.default_rng(11))
    f = NC.fit_cell(v)
    assert abs(f["mu"] - mu) <= 0.02
    assert abs(f["beta"] - beta) / beta <= 0.05


def test_gcal_rejects_a_bar_that_is_known_to_be_wrong():
    """A gate that can only pass is decoration (benchmark/README.md)."""
    from scipy import stats
    mu, beta = -7.25, 0.0725
    v = stats.gumbel_r.rvs(loc=mu, scale=beta, size=400_000,
                           random_state=np.random.default_rng(12))
    assert NC.gcal(v, mu, beta, alpha=0.01)["passed"]
    assert not NC.gcal(v, mu, beta * 2.0, alpha=0.01)["passed"]
    assert not NC.gcal(v, mu, beta * 0.5, alpha=0.01)["passed"]


def test_bulk_sd_beta_is_not_the_tail_beta():
    """The trap benchmark/null.py documents, reproduced as an assertion on real cells."""
    cells = NC.calib()["cells"]
    if not cells:
        pytest.skip("no calibration file yet")
    c = cells.get("EN_QUAD|keyskip1|L120") or cells.get("EN_QUAD|keyskip1|L31")
    if c is None:
        pytest.skip("legacy-statistic cell not calibrated yet")
    assert c["bulk_sd_beta"] / c["beta"] > 1.5


def test_effective_tests_below_naive_bonferroni_for_correlated_panel():
    rng = np.random.default_rng(3)
    base = rng.normal(size=(20000, 1))
    z = base + 0.4 * rng.normal(size=(20000, 9))       # strongly correlated panel
    e = NC.effective_tests_eigen(z)
    assert e["li_ji"] < 9.0


# ------------------------------------------------------------------ the engine
@pytest.mark.parametrize("L", [31, 120])
def test_vecbeam_reproduces_the_reference_decoder(L):
    import vecbeam as V
    rows = V.selftest_exact(n=20, lengths=(L,), verbose=False)
    assert rows[0]["passed"], rows[0]


def test_vecbeam_permissive_mode_raises_the_null():
    """The whole reason this lane exists: a wider transition relation has a higher null."""
    import vecbeam as V
    rng = np.random.default_rng(9)
    C = rng.integers(0, 29, size=(48, 120))
    K = rng.integers(0, 29, size=(48, 120 * 8 + 64))
    base = V.batch_decode(C, K, mode="keyskip1")["score"].mean()
    perm = V.batch_decode(C, K, mode="drift3")["score"].mean()
    assert perm > base + 1.0, (base, perm)
