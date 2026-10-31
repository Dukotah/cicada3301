"""Round 41 I1: the survivor-population refit and the standing matched null.  python -m pytest tests/test_null_refit.py -q

Pins the bar of record (family='survivor12'), checks the stored refit against its own recognizer (Q1a), and the
position-structure-matched shuffle (benchmark/bars_matched.py) against X1's construction and the R13 fixture."""
import json, math, os, random, sys
import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, ".."))
AN = os.path.join(LP, "analysis")
sys.dont_write_bytecode = True
for p in (os.path.join(LP, "benchmark"), os.path.join(AN, "round34", "I1-v3-null")):
    sys.path.insert(0, p)
import bars_matched as BM        # noqa: E402
import bars_v3 as B              # noqa: E402

LANE = os.path.join(AN, "round41", "I1-null-refit")
NS = os.path.join(LANE, "null_survivor12.json")
FIT = os.path.join(LANE, "fit.json")
FIX = os.path.join(LANE, "fixture_r13.json")
X1 = os.path.join(AN, "round40", "X1-redteam")
have_refit = pytest.mark.skipif(not os.path.exists(NS), reason="round41 I1 refit not present")


@have_refit
def test_survivor12_pins_and_monotone():
    assert round(B.bar_v3(131786, 120, "keyskip1", family="survivor12"), 2) == 9.63
    assert round(B.bar_v3(131786, 120, "keyskip2", family="survivor12"), 2) == 9.65
    assert round(B.bar_v3(1e6, 120, "keyskip1", family="survivor12"), 2) == 10.46
    assert round(B.bar_v3(1e6, 120, "keyskip2", family="survivor12"), 2) == 10.49
    for rel in ("keyskip1", "keyskip2"):
        for L in (120, 180, 240):
            assert B.bar_v3(1e9, L, rel, family="survivor12") > B.bar_v3(1e6, L, rel, family="survivor12") > B.bar_v3(1e5, L, rel, family="survivor12")


@have_refit
def test_survivor12_refuses_extrapolation_and_free():
    with pytest.raises(ValueError):
        B.bar_v3(1e6, 400, "keyskip1", family="survivor12")
    with pytest.raises(ValueError):
        B.bar_v3(1e6, 120, "free", family="survivor12")
    with pytest.raises(ValueError):
        B.bar_v3(1e6, 120, "keyskip1", family="survivor12", method="gpd")


def test_default_family_unchanged():
    assert round(B.bar_v3(2e5, 120, "keyskip1"), 2) == 8.62
    assert round(B.bar_v3(1e6, 120, "free"), 2) == 15.3


@have_refit
def test_refit_dominates_null12_and_recognizer_q1a():
    d = json.load(open(NS))
    assert d["n_survivors"] >= 40000
    f = json.load(open(FIT))
    for rel in ("keyskip1", "keyskip2"):
        c = f["cells"]["L120|" + rel]
        assert c["n"] >= 40000 and f["cells"]["L240|" + rel]["n"] >= 5000
        # the stored null12 survivor-N bar was lenient: refit at survivor N sits above it by > 1
        assert B.bar_v3(131786, 120, rel, family="survivor12") - c["null12"]["bar_N131786"] > 1.0
        # bar of record >= the pooled real-sweep survivor POT bar (X1's empirical ~9.6)
        assert B.bar_v3(131786, 120, rel, family="survivor12") >= f["real_stores"]["pooled"][rel]["bars"]["N=131786"] - 1e-6
        # the refit survivor median is the real-sweep median (2.8), not null12's 2.33
        assert abs(c["median_pmax"] - f["real_stores"]["pooled"][rel]["median_pmax"]) < 0.05


def test_matched_shuffle_properties():
    s = list(range(1000))
    a = BM.matched_shuffle(s, 100, random.Random(5)); b = BM.matched_shuffle(s, 100, random.Random(5))
    assert a == b and sorted(a) == s and a != s
    # block order only: every output block of 100 is a contiguous run of the input
    for i in range(0, 1000, 100):
        blk = a[i:i + 100]; assert blk == list(range(blk[0], blk[0] + 100))
    t = [0, 5, 0, 7, 9, 0, 2, 3, 0, 1]
    w = BM.matched_shuffle(t, 5, random.Random(1), mode="within")
    assert [i for i, x in enumerate(w) if x == 0] == [i for i, x in enumerate(t) if x == 0]
    assert sorted(w) == sorted(t)


def test_matched_equals_x1_construction():
    """X1's rerun_r13_matched.py: blocks=[U[i:i+BS]...]; Random(60000+j).shuffle(blocks)."""
    U = list(np.random.default_rng(3).integers(0, 29, 1234))
    for BS in (100, 250, 1000):
        for j in (0, 7):
            r = random.Random(60000 + j); blocks = [list(U[i:i + BS]) for i in range(0, len(U), BS)]; r.shuffle(blocks)
            assert BM.matched_shuffle(U, BS, random.Random(BM.SEED_BASE + j)) == [v for b in blocks for v in b]


def test_bar_matched_shape():
    r = BM.bar_matched(list(range(500)), (100, 250), 30, stat_fn=lambda x: float(x[0]))
    assert set(r) == {100, 250} and len(r[100]["stats"]) == 30 and r[100]["bar"] <= max(r[100]["stats"])
    assert 0 < BM.p_matched(1e9, r[100]["stats"]) < 0.05


@pytest.mark.skipif(not (os.path.exists(FIX) or os.path.exists(os.path.join(X1, "rerun_r13_matched_BS250.json"))), reason="R13 fixture outputs absent")
def test_r13_fixture_family_p():
    """R13 walk family p under page-/region-scale matched nulls: 0.004 / 0.018 / 0.070 (X1, 500 draws), reproduced by the standing shuffle."""
    exp = {100: 0.004, 250: 0.018, 1000: 0.070}
    if os.path.exists(FIX):
        fx = json.load(open(FIX))
        for bs, p in exp.items():
            if str(bs) in fx:
                assert abs(fx[str(bs)]["p_family"] - p) < 0.006, (bs, fx[str(bs)]["p_family"])
    for bs, p in exp.items():
        x = json.load(open(os.path.join(X1, "rerun_r13_matched_BS%d.json" % bs)))["blockperm_family"]
        assert abs(x["p_family"] - p) < 0.006
