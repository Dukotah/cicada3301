"""Failing-then-passing test for the R3 store check in validate_ledger.py.
    python -m pytest analysis/handoff/test_validate_ledger_r3.py -q
"""
import json, os, sys, tempfile
NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "analysis", "handoff"))
import validate_ledger as V
sys.path.insert(0, os.path.join(V.LP, "analysis", "round19", "I2"))
import adjudicate as A


def _store(d, drop=None, name="s.jsonl"):
    # Synthetic rows: the real panel (models/panel.npz) is gitignored and absent in CI.
    z = [0.1 * i for i in range(9)]
    row = lambda k: [k, 120, -6.0, max(z), 3, 0.5, 0.2, 2, 1.8, 14, 4.2, 0.61, z]
    hdr = {"v": A.SCHEMA_VERSION, "sweep": "t", "fields": list(A.ROW_FIELDS)}
    rows = [row(k) for k in range(2)]
    if drop:                                   # simulate a store that omits one R3 field
        i = hdr["fields"].index(drop)
        hdr["fields"] = [f for f in hdr["fields"] if f != drop]
        rows = [r[:i] + r[i + 1:] for r in rows]
    p = os.path.join(d, name)
    with open(p, "w") as f:
        f.write(json.dumps(hdr) + NL)
        for r in rows:
            f.write(json.dumps(r) + NL)
    return p


def test_compliant_store_passes():
    with tempfile.TemporaryDirectory() as d:
        assert V.check_r3_store(_store(d)) == []


def test_each_missing_r3_field_fails():
    for f in V.R3_STATS:
        with tempfile.TemporaryDirectory() as d:
            assert V.check_r3_store(_store(d, drop=f)), f


def test_english_only_store_fails():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "e.jsonl")
        open(p, "w").write(json.dumps({"v": "x", "fields": ["kid", "en"]}) + "\n[1,-6.0]\n")
        assert V.check_r3_store(p)


def test_scoping_declared_vs_historical():
    with tempfile.TemporaryDirectory() as d:
        bad = _store(d, drop="zl")
        e = {"id": "T", "round": 32, "sweep_store": bad}
        assert V.r3_problems(e, [d])[0]
        assert not V.r3_problems({"id": "T", "round": 32, "sweep_store": _store(d, name="g.jsonl")}, [d])[0]
        assert not V.r3_problems({"id": "T", "round": 18, "sweep_store": bad}, [d])[0]   # pre-R19: untouched
        assert V.r3_problems({"id": "T", "round": 32, "declares_sweep": True}, [d])[0]
        assert V.r3_problems({"id": "T", "round": 32, "sweep_store": "nope.jsonl"}, [d])[0]
