"""P3 self-tests -- deliverables load, round-trips pass, and the one bar is callable.

Cheap and network-free. Run: python3 -m pytest analysis/round20/P3/test_p3.py -q
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def test_panelmax_bar_callable_and_ordered():
    import panelmax20 as PM
    # the one canonical bar exists and is on the pmax statistic
    con = PM.panelmax_contract(preset="exact", n_round_adjudicated=10 ** 6)
    assert con["statistic"] == "pmax"
    assert con["cell"] == "I19:vecbeam.keyskip1+I2|pmax|L120"
    assert con["cell_status"] == "CALIBRATED"
    # claim bar is stricter (higher) than escalate bar, and both are well above I2's z~=4 scale
    assert con["claim_bar"] > con["escalate_bar"] > 4.0
    # bar grows monotonically with N (family-wise correction)
    b4 = PM.panelmax_bar("exact", 10 ** 4)
    b8 = PM.panelmax_bar("exact", 10 ** 8)
    assert b8 > b4
    # refuses an unknown preset rather than substituting the English/keyskip1 bar
    try:
        PM.panelmax_bar("no_such_preset")
        assert False, "should have raised"
    except KeyError:
        pass


def test_panelmax20_json_present():
    p = os.path.join(HERE, "panelmax20.json")
    assert os.path.exists(p)
    d = json.load(open(p, encoding="utf-8"))
    assert d["claim_statistic"].startswith("pmax")
    assert "exact" in d["presets"] and d["presets"]["exact"]["status"] == "CALIBRATED"
    # never -5.5, never a scalar k_eff
    assert "-5.5" not in d["claim_statistic"] or "NEVER -5.5" in d["claim_statistic"]


def test_seedprior_roundtrip():
    import p3b_seedprior as SP
    r = SP.roundtrip_check()
    assert r["passed"], r
    assert r["rank1_seed"] == 1325734783
    assert r["mismatches"] == 0
    assert SP.seed_order(1) == [1325734783]
    assert len(SP.seed_order()) == 433


def test_plant_recovery_gate_registers():
    """If the plant control has been run, the exact-preset pmax power must be >=0.90 on the
    four gate registers and wrong-key power must be ~0 (the P3a PASS threshold)."""
    p = os.path.join(HERE, "out_plant_recovery.json")
    if not os.path.exists(p):
        return  # control not run in this environment; build/plant produced elsewhere
    d = json.load(open(p, encoding="utf-8"))
    ex = d["by_preset"]["exact"]["by_register"]
    for reg in ("LP1_REAL", "LATIN", "OE", "EN_HALFVOWEL"):
        assert ex[reg]["pmax_power_claim"] >= 0.90, (reg, ex[reg])
        assert (ex[reg]["pmax_wrong_power_claim"] or 0.0) <= 0.05, (reg, ex[reg])
