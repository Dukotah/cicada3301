"""Round 39 T1: standing nulls and flags.  python -m pytest tests/test_standing_nulls.py -q"""
import json, math, os, sys
import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, ".."))
AN = os.path.join(LP, "analysis")
sys.dont_write_bytecode = True
for p in (os.path.join(AN, "round19", "I2"), os.path.join(LP, "benchmark"), os.path.join(AN, "round34", "I1-v3-null")):
    sys.path.insert(0, p)
import adjudicate as A            # noqa: E402
import bars_keymatched as K       # noqa: E402
import bars_v3 as B               # noqa: E402

P36 = os.path.join(LP, "data", "panels", "panel-r36.npz")
NULL120 = os.path.join(AN, "round38", "I2-x4-null", "null_rows_L120.jsonl")
needs_panel = pytest.mark.skipif(not os.path.exists(P36), reason="panel-r36 not present")
# The R38 X4 per-shuffle null store is a large gitignored corpus, absent on a fresh CI checkout;
# guard it like needs_panel so the fixture-reproduction test runs only where the store was regenerated.
needs_null120 = pytest.mark.skipif(not os.path.exists(NULL120), reason="R38 X4 null rows absent (gitignored)")


def _res(x, panel=True):
    return A.adjudicate(x, pan=A.Panel(P36))


def test_constant_decode_is_degenerate_without_panel():
    const = np.full(120, 5, dtype=np.int64)
    rnd = np.random.default_rng(1).integers(0, 29, 120)
    assert A.is_degenerate(A.min_distinct(const), A.ioc_n(const))
    assert not A.is_degenerate(A.min_distinct(rnd), A.ioc_n(rnd))


@needs_panel
def test_degenerate_flag_on_adjudicate_and_row_roundtrip():
    const = np.full(120, 5, dtype=np.int64)
    rnd = np.random.default_rng(1).integers(0, 29, 120)
    rc, rr = _res(const), _res(rnd)
    assert rc["degenerate"] is True and rr["degenerate"] is False
    # pmax_nondegenerate excludes the constant even when it scores higher
    rows = [A.to_row(rc, "c", True), A.to_row(rr, "r", True)]
    assert A.pmax_nondegenerate(rows) == rows[1][3]
    assert A.pmax_nondegenerate([A.to_row(rc, "c")]) is None      # 13-field rows work too
    assert A.pmax_nondegenerate([rc, rr]) == rr["pmax"]


@needs_panel
def test_optional_field_is_header_driven():
    rnd = np.random.default_rng(2).integers(0, 29, 120)
    r = _res(rnd)
    r13, r14 = A.to_row(r, "k"), A.to_row(r, "k", with_degenerate=True)
    assert len(r13) == 13 and len(r14) == 14
    h13 = {"v": A.SCHEMA_VERSION, "fields": A.ROW_FIELDS}
    h14 = {"v": A.SCHEMA_VERSION, "fields": A.ROW_FIELDS_DEG}
    nreg = len(r["z"])
    assert A.validate_row(r13, h13, nreg) and A.validate_row(r14, h14, nreg)
    assert A.validate_row(r13, None, nreg) and A.validate_row(r14, None, nreg)   # without header: either
    with pytest.raises(A.RowError):
        A.validate_row(r14, h13, nreg)          # header says 13, row has 14
    with pytest.raises(A.RowError):
        A.validate_row(r13, h14, nreg)
    bad = list(r14); bad[13] = not bad[13]
    with pytest.raises(A.RowError):
        A.validate_row(bad, h14, nreg)          # flag disagrees with (mds, ioc)
    with pytest.raises(A.RowError):
        A.validate_row(r14[:12] + [r14[12], True, 1], None, nreg)


def test_adjudicate_copies_identical():
    other = os.path.join(AN, "round32", "I2-multiregister-readjudication", "adjudicate.py")
    assert open(A.__file__, "rb").read() == open(other, "rb").read()


@needs_null120
def test_keymatched_fixture_reproduces_r38_x4_bar():
    """I2-R38 X4 L=120 bar 6.994 from the stored per-shuffle rows (no re-decoding)."""
    for rel in ("keyskip1", "keyskip2"):
        m = K.family_maxima_from_rows(NULL120, rel)
        assert len(m) == 2000
        assert round(K.bar_from_maxima(m), 3) == 6.994
        assert round(K.bar_from_maxima(m, 1e6, 60), 1) > K.bar_from_maxima(m)     # Gumbel shift grows with N
    nd = json.load(open(os.path.join(AN, "round38", "I2-x4-null", "null_x4.json")))["120"]["by_rel"]["keyskip1"]
    assert round(K.bar_from_maxima(K.family_maxima_from_rows(NULL120, "keyskip1")), 3) == nd["bar_empirical_q99"]
    m = K.family_maxima_from_rows(NULL120, "keyskip1")
    mu, beta = K.gumbel_params(m)
    assert abs((mu - beta * math.log(-math.log(0.99))) - nd["bar_gumbel_q99"]) < 0.01


def test_keymatched_generic_machinery_drops_degenerate():
    """Toy family: member 0 decodes to a constant (huge fake pmax), member 1 to the shuffled stream; the constant must not set the max."""
    def adj(x):
        x = np.asarray(x, dtype=np.int64)
        return {"pmax": 99.0 if len(set(x.tolist())) == 1 else float(x[:5].sum() % 7),
                "mds": A.min_distinct(x), "ioc": A.ioc_n(x)}
    stream = list(np.random.default_rng(0).integers(0, 29, 400))
    derive = lambda S: [0, 1]
    decode = lambda m, L: [[3] * L] if m == 0 else [list(np.array(stream_s[0][:L]))]
    stream_s = [None]
    def derive2(S): stream_s[0] = S; return [0, 1]
    bar, maxima, n0 = K.bar_keymatched(derive2, decode, 120, 1, 30, stream=stream, adjudicate_fn=adj, with_maxima=True)
    assert max(maxima) < 7 and n0 == 1 and len(maxima) == 30


def test_free_L120_is_the_12_register_node():
    f = json.load(open(os.path.join(AN, "round37", "I1-free-null", "fit_free.json")))["fit"]["120"]
    expect = f["u"] + f["beta"] * math.log(f["p_u"]) + f["beta"] * math.log(1e6 / -math.log1p(-0.01))
    assert abs(B.bar_v3(1e6, 120, "free") - expect) < 1e-4
    assert abs(B.bar_v3(1e6, 120, "free", panel="r36") - expect) < 1e-4
    assert abs(B.bar_v3(1e6, 120, "free", panel="r32") - 17.4315) < 1e-3       # the old node, kept as an escape
    assert B.bar_v3(1e6, 120, "free") < B.bar_v3(1e6, 120, "free", panel="r32")
    assert round(B.bar_v3(1e6, 240, "free"), 1) == 20.6                        # L>=240 unchanged
