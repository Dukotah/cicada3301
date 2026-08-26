"""I2 tests.  `python3 -m pytest test_adjudicate.py -q` (or run directly).

Covers the three things a Phase 2 lane depends on:
  * `adjudicate()` returns a well-formed SWEEPROW and separates a plant from noise
  * the SWEEPROW validator rejects the exact 0/15 failure mode R3 exists to prevent
  * the plant-and-recover positive control still works end to end (doctrine §4 r2)
"""
import json
import os
import random
import sys
import tempfile

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
           os.path.join(LP, "analysis", "campaign18_skip")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import adjudicate as AJ            # noqa: E402
import skipdecode as sk            # noqa: E402
import plant as PL                 # noqa: E402

N = 29
pytestmark = pytest.mark.skipif(
    not os.path.exists(os.path.join(HERE, "models", "panel.npz")),
    reason="run build_models.py first (models/ is gitignored and rebuildable)")


# ------------------------------------------------------------------ shape
def test_row_shape_and_validation():
    rng = np.random.default_rng(0)
    r = AJ.adjudicate(rng.integers(0, N, 240))
    row = AJ.to_row(r, "kid")
    assert len(row) == len(AJ.ROW_FIELDS) == 13
    assert AJ.validate_row(row)
    assert len(r["z"]) == 9


def test_validator_rejects_english_only_row():
    """The 0/15 failure mode: a row carrying only (params, English score, head)."""
    with pytest.raises(AJ.RowError):
        AJ.validate_row(["kid", 240, -5.5])
    rng = np.random.default_rng(1)
    row = AJ.to_row(AJ.adjudicate(rng.integers(0, N, 240)), "kid")
    row[12] = None
    with pytest.raises(AJ.RowError):
        AJ.validate_row(row)


def test_validator_rejects_inconsistent_pmax():
    rng = np.random.default_rng(2)
    row = AJ.to_row(AJ.adjudicate(rng.integers(0, N, 240)), "kid")
    row[3] = row[3] + 5.0
    with pytest.raises(AJ.RowError):
        AJ.validate_row(row)


def test_store_roundtrip():
    rng = np.random.default_rng(3)
    hdr = AJ.header("test/sweep", key_space="unit test")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "s.jsonl")
        with open(p, "w") as f:
            f.write(json.dumps(hdr) + "\n")
            for i in range(20):
                f.write(json.dumps(
                    AJ.to_row(AJ.adjudicate(rng.integers(0, N, 160)), i)) + "\n")
        out = AJ.validate_store(p)
        assert out["rows_validated"] == 20


def test_binary_record_is_77_bytes():
    assert AJ.ROW_DTYPE.itemsize == 77
    rng = np.random.default_rng(4)
    rec = AJ.to_record(AJ.adjudicate(rng.integers(0, N, 120)), 7)
    assert int(rec["kid"]) == 7 and int(rec["n"]) == 120


# ------------------------------------------------------------------ statistics
def test_agnostic_statistics_are_sane():
    rng = np.random.default_rng(5)
    x = rng.integers(0, N, 400)
    r = AJ.adjudicate(x)
    assert 0.5 < r["ioc"] < 1.6                 # random runes: IoC*N ~ 1
    assert 15 <= r["mds"] <= 25                 # E[distinct in a 32-window] ~ 19.4
    assert 0.6 < r["zl"] < 1.3

    flat = np.zeros(400, dtype=np.int64)        # degenerate stream
    r2 = AJ.adjudicate(flat)
    assert r2["mds"] == 1
    assert r2["ioc"] > 20
    assert r2["zl"] < 0.2

    y = np.tile(np.arange(4), 100)              # 4-symbol alphabet
    assert AJ.adjudicate(y)["mds"] == 4


def test_fast_min_distinct_equals_reference():
    """The O(n) prev-occurrence path must equal the obvious cumsum oracle, everywhere.

    G-SPEED was met by optimising the IMPLEMENTATION; if that ever changes a statistic's
    VALUE it is no longer the statistic that was pre-registered.  This is the guard.
    """
    rng = np.random.default_rng(21)
    for n in (0, 1, 5, 31, 32, 33, 64, 120, 240, 401):
        for alpha in (2, 5, 29):
            x = rng.integers(0, alpha, size=n)
            assert AJ.min_distinct(x) == AJ.min_distinct_ref(x), (n, alpha)
    for x in (np.zeros(200, dtype=np.int64), np.tile(np.arange(29), 20),
              np.repeat(np.arange(10), 40)):
        assert AJ.min_distinct(x) == AJ.min_distinct_ref(x)


def test_panel_raw_transposed_gather_matches():
    pan = AJ.panel()
    rng = np.random.default_rng(22)
    for n in (3, 50, 240, 700):
        x = rng.integers(0, N, size=n)
        f = x[:-2] * (N * N) + x[1:-1] * N + x[2:]
        ref = pan.LMF[:, f].mean(axis=1, dtype=np.float64)
        assert np.allclose(pan.raw(x), ref, atol=1e-12)


def test_h2_matches_bincount_definition():
    rng = np.random.default_rng(23)
    for n in (3, 40, 240, 600):
        x = rng.integers(0, N, size=n)
        tri = x[:-2] * (N * N) + x[1:-1] * N + x[2:]
        bi = x[:-2] * N + x[1:-1]
        ct = np.bincount(tri)
        cb = np.bincount(bi)
        ct = ct[ct > 0].astype(float)
        cb = cb[cb > 0].astype(float)
        m = float(len(tri))
        ref = -(ct / m * np.log2(ct / m)).sum() + (cb / m * np.log2(cb / m)).sum()
        assert abs(AJ.h2_cond(x) - ref) < 1e-10, n


def test_short_and_empty_inputs():
    for n in (0, 1, 2, 3, 5):
        r = AJ.adjudicate(np.zeros(n, dtype=np.int64))
        assert r["n"] == n
        assert isinstance(r["pmax"], float)


def test_scores_runes_not_transliteration():
    """A decode is scored from its rune indices; passing a translit only affects `en`."""
    rng = np.random.default_rng(6)
    x = rng.integers(0, N, 200)
    a = AJ.adjudicate(x)
    b = AJ.adjudicate(x, translit=AJ.idx_to_trans(x))
    assert a["z"] == b["z"] and abs(a["en"] - b["en"]) < 1e-12


def test_batch_matches_single():
    rng = np.random.default_rng(7)
    X = rng.integers(0, N, size=(8, 240))
    B = AJ.adjudicate_batch(X)
    for i in range(8):
        s = AJ.adjudicate(X[i])
        assert abs(B["pmax"][i] - s["pmax"]) < 1e-9
        assert abs(B["pcon"][i] - s["pcon"]) < 1e-9
        assert int(B["preg"][i]) == s["preg"]


# ------------------------------------------------------------------ the control
def _plant_and_decode(text, L=240, seed=99):
    P = sk.eng_to_idx(text)
    assert len(P) >= L
    P = P[:L]
    K = PL.make_key("sha256_ctr", length=L * 4 + 512, seed=b"CICADA3301")
    C, _s, _u = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=seed)
    bd = sk.beam_decode(C, K, sign=-1, o=0, beam_w=400, max_skip=3)
    return P, bd["plain_idx"]


def test_positive_control_english_plant():
    """Doctrine §4 r2: plant, prove recovery, THEN trust silence."""
    txt = (PL.PLAINTEXTS["primes"] + PL.PLAINTEXTS["warning"]) * 3
    P, dec = _plant_and_decode(txt)
    rec = sum(a == b for a, b in zip(P, dec)) / len(P)
    assert rec > 0.95
    r = AJ.adjudicate(dec)
    assert r["en"] > -5.5                       # the legacy scorer still sees it
    assert r["pmax"] > 8.0                      # and so does the panel, hugely
    assert AJ.panel().registers[r["preg"]].startswith("EN") or \
        AJ.panel().registers[r["preg"]] == "LP1_REAL"


def test_panel_separates_plant_from_wrong_key():
    txt = (PL.PLAINTEXTS["primes"] + PL.PLAINTEXTS["warning"]) * 3
    P = sk.eng_to_idx(txt)[:240]
    K = PL.make_key("sha256_ctr", length=240 * 4 + 512, seed=b"CICADA3301")
    C, _s, _u = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=1)
    good = AJ.adjudicate(sk.beam_decode(C, K, sign=-1, o=0, beam_w=400,
                                        max_skip=3)["plain_idx"])
    rng = random.Random(5)
    WK = [rng.randrange(N) for _ in range(len(K))]
    bad = AJ.adjudicate(sk.beam_decode(C, WK, sign=-1, o=0, beam_w=400,
                                       max_skip=3)["plain_idx"])
    assert good["pmax"] > bad["pmax"] + 5.0
    assert good["ioc"] > bad["ioc"]


def test_lp1_real_register_is_not_lost():
    """G-LP1's shape, as a unit test: the puzzle's own register must stay visible."""
    sp = json.load(open(os.path.join(LP, "SOLVED-PAGES.json"), encoding="utf-8"))
    txt = "".join(p["plaintext_transliteration"] for p in sp["pages"])
    P, dec = _plant_and_decode(txt, L=240, seed=7)
    r = AJ.adjudicate(dec)
    assert r["en"] >= -4.5, f"LP1_REAL regressed on the legacy scorer: {r['en']}"
    assert r["pmax"] > 10.0


# ------------------------------------------------------------------ calibration
def test_null_is_centred():
    """z should be ~N(0,1) on uniform random runes at any length, on or off the grid."""
    rng = np.random.default_rng(11)
    for L in (128, 175, 240, 333):
        Z = AJ.adjudicate_batch(rng.integers(0, N, size=(400, L)))["z"]
        assert abs(Z.mean()) < 0.25, (L, Z.mean())
        assert 0.75 < Z.std() < 1.3, (L, Z.std())


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
