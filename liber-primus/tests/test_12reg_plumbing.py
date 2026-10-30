"""Round 37 T1: 12-register plumbing.  python -m pytest tests/test_12reg_plumbing.py -q
Fixtures: the R36 B1 12-wide store and the R35 B1 9-wide store (committed), panel-R36 (data/panels)."""
import json, os, sys, importlib.util
import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, ".."))
AN = os.path.join(LP, "analysis")
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(AN, "handoff"))
sys.path.insert(0, os.path.join(AN, "round19", "I2"))
import validate_ledger as V      # noqa: E402
import adjudicate as A           # noqa: E402

P36 = os.path.join(LP, "data", "panels", "panel-r36.npz")
S12 = os.path.join(AN, "round36", "B1-orbit-12reg", "readjud_rows.jsonl")
S9 = os.path.join(AN, "round35", "B1-bash-orbit-pfv4", "sweep_rows.jsonl")
TH36 = os.path.join(LP, "data", "panels", "testhalves-r36.npz")
NL = chr(10)


def _head(path):
    with open(path, encoding="utf-8") as f:
        return json.loads(f.readline())


def _copy_head(src, dst, n=50):
    with open(src, encoding="utf-8") as f, open(dst, "w", encoding="utf-8") as g:
        for i, line in enumerate(f):
            if i > n:
                break
            g.write(line)
    return dst


def test_12wide_store_validates_stock(tmp_path):
    p = _copy_head(S12, str(tmp_path / "s12.jsonl"))
    r = A.validate_store(p)
    assert r["rows_validated"] == 50 and len(r["header"]["registers"]) == 12
    assert V.check_r3_store(p) == []


def test_12wide_full_store_validates_stock():
    r = A.validate_store(S12)
    assert r["rows_validated"] == 276242
    assert V.check_r3_store(S12) == []


def test_9wide_store_still_validates(tmp_path):
    p = _copy_head(S9, str(tmp_path / "s9.jsonl"))
    assert A.validate_store(p)["rows_validated"] == 50
    assert V.check_r3_store(p) == []


def test_header_width_is_enforced(tmp_path):
    """A 12-register header with a 9-vector z must FAIL; a header without `registers` falls back to 9."""
    h = _head(S12)
    z = [0.1 * i for i in range(9)]
    row = [0, 120, -6.0, max(z), 3, 0.5, 0.2, 2, 1.8, 14, 4.2, 0.61, z]
    p = tmp_path / "bad.jsonl"
    p.write_text(json.dumps(h) + NL + json.dumps(row) + NL)
    with pytest.raises(A.RowError):
        A.validate_store(str(p))
    h2 = dict(h); h2.pop("registers")
    p2 = tmp_path / "fallback.jsonl"
    p2.write_text(json.dumps(h2) + NL + json.dumps(row) + NL)
    assert A.validate_store(str(p2))["rows_validated"] == 1


def test_row_dtype_sized_from_registers():
    assert A.ROW_DTYPE.itemsize == 77 and A.row_dtype(12).itemsize == 77 + 12


def _load_beam():
    d = os.path.join(AN, "round33", "I1-register-aware-beam")
    sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location("beam_v3_t1", os.path.join(d, "beam_v3.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


needs36 = pytest.mark.skipif(not (os.path.exists(P36) and os.path.exists(TH36)), reason="panel-R36 absent")


def test_derive_clusters_unit():
    B = _load_beam()
    nine = ["EN_MODERN", "EN_KJV", "LP1_REAL", "LATIN", "OE", "DE", "CY", "EN_HALFVOWEL", "EN_NOVOWEL"]
    c = B.derive_clusters(nine)
    assert [n for n, _ in c] == ["EN", "LATIN", "OE", "DE", "CY", "EN_HALFVOWEL", "EN_NOVOWEL"]
    c12 = B.derive_clusters(nine + ["GREEK", "HEBREW", "NORSE", "KLINGON"])
    assert c12[0] == ("EN", nine[:3]) and ("KLINGON", ["KLINGON"]) in c12 and len(c12) == 11


@needs36
def test_beam_v3_panel_r36_plant_both_designs():
    B = _load_beam()
    cl = B.set_panel(P36)
    assert B.panel().R == 12 and B.PANEL_PATH == P36
    assert {r for _, rs in cl for r in rs} == set(B.panel().registers) and len(cl) == 10
    th = np.load(TH36)["EN_MODERN"].astype(np.int64)
    rng = np.random.default_rng(3301)
    L = 120
    P = th[5000:5000 + L]
    K = rng.integers(0, 29, 400)
    C = ((P + K[:L]) % 29).tolist()      # sign -1 convention: plain = C - K, skip-free keyskip1
    for design in ("panel_max", "register_cond"):
        out = B.beam_decode_v3(C, K.tolist(), 1, design)
        rec = B.B2.recovery(out["plain_idx"], P.tolist())
        assert rec >= 0.9, (design, rec)
    assert len(B.panel().registers) == 12


@needs36
def test_hitfn20_refuses_mismatched_panel():
    sys.path.insert(0, os.path.join(AN, "round19", "I3"))
    sys.path.insert(0, os.path.join(AN, "round20", "P3"))
    import panelmax20 as PM
    with pytest.raises(ValueError, match="REFUSED"):
        PM.panelmax_bar(preset="exact", panel=P36)
    with pytest.raises(ValueError, match="REFUSED"):
        PM.panelmax_contract(preset="exact", panel=A.Panel(P36))
    assert PM.check_panel_matches_bar(None) is True       # legacy signature untouched
    for d in ("round19/I1", "round20/P3", "round20/HITFN"):
        sys.path.insert(0, os.path.join(AN, *d.split("/")))
    sys.path.insert(0, os.path.join(LP, "src"))
    sys.path.insert(0, os.path.join(AN, "campaign18_skip"))
    import hitfn20 as H
    dec = H.HitDecode(C=[0] * 40, K=[0] * 40, panel=P36)
    with pytest.raises(ValueError, match="REFUSED"):
        H.evaluate(dec)
