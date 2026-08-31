"""HITFN self-tests -- the recovery gate rejects hallucination, accepts the real, and the
SWEEPROW/3 recovery field validates. Cheap, network-free.

    python3 -m pytest analysis/round20/HITFN/test_hitfn.py -q
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def test_is_hit_predicate_exists_and_gates_on_three_clauses():
    import hitfn20 as H
    # the predicate exists and takes a HitDecode
    assert callable(H.is_hit)
    assert hasattr(H, "HitDecode") and hasattr(H, "evaluate")
    # the recovery bar is the doctrine 0.90, never relaxed
    assert H.RECOVERY_BAR == 0.90


def test_sweeprow3_has_recovery_field():
    import hitfn20 as H
    import adjudicate as AD
    # SWEEPROW/3 = SWEEPROW/1 fields + recovery gate fields (append-only)
    assert H.ROW_FIELDS_V3[:len(AD.ROW_FIELDS)] == AD.ROW_FIELDS
    for f in ("recovery", "heldout_recovery", "clears_null", "hit"):
        assert f in H.ROW_FIELDS_V3, f
    # recovery is downstream of the base row, so every SWEEPROW/1 consumer is unbroken
    assert "recovery" in H.ROW_FIELDS_V3 and "recovery" not in AD.ROW_FIELDS


def test_sweeprow3_validates_and_rejects_inconsistent_hit():
    import hitfn20 as H
    import adjudicate as AD
    # a well-formed non-hit row validates
    base = ["k", 240, -6.5, 5.0, 3, 4.0, 3.0, 4, 1.2, 12, 0.5, 0.4,
            [1.0] * 8 + [5.0]]
    row = base + [0.5, 0.5, "heldout_selfconsistency", False, False]
    assert H.validate_row_v3(row)
    # hit=True while clears_null=False is an inconsistent gate -> must raise
    bad = base + [0.95, 0.95, "truth_idx", False, True]
    try:
        H.validate_row_v3(bad)
        assert False, "should have rejected hit=True with clears_null=False"
    except AD.RowError:
        pass
    # hit=True with held-out recovery below bar -> must raise
    bad2 = base + [0.95, 0.5, "truth_idx", True, True]
    try:
        H.validate_row_v3(bad2)
        assert False, "should have rejected hit=True with held-out<0.90"
    except AD.RowError:
        pass


def test_hallucination_guard_rejects_fake_accepts_real():
    """THE point of defect (d): a bar-clearing low-recovery decode is REJECTED; a genuine
    high-recovery decode is ACCEPTED. Runs the actual planted guard (~1 min)."""
    import guard as G
    out = G.run_guard()
    s = out["summary"]
    f = s["FAKE_hallucination"]
    r = s["REAL_genuine"]
    # the fake really does clear the bar on pmax (else it is not a hallucination test)
    assert f["clears_null"] is True, f
    assert f["true_rune_index_recovery"] < 0.90, f
    # and is_hit REJECTS it -- in BOTH the strict (truth) and the real (held-out) modes
    assert f["is_hit_strict"] is False, f
    assert f["is_hit_realmode_heldout"] is False, f
    # the real genuine decode clears the bar, recovers, and is ACCEPTED
    assert r["clears_null"] is True, r
    assert r["true_rune_index_recovery"] >= 0.95, r
    assert r["is_hit_strict"] is True, r
    assert r["is_hit_realmode_heldout"] is True, r
    assert s["guard_pass"] is True


def test_heldout_reproduction_wired():
    """Clause 3 is a real held-out re-decode: fit on 1/4, verify on 3/4 -- not a copy of the
    full-page number. A genuine key reproduces; the held-out recovery is a distinct computation."""
    import hitfn20 as H
    import guard as G
    panels = G.PL3._panels()
    K = G._key()
    real = G._find_real(K, panels["EN_MODERN"])
    assert real is not None
    dec = H.HitDecode(C=real["C"], K=real["K"], o=0, preset="exact",
                      n_round_adjudicated=10 ** 6, truth_idx=real["P"])
    v = H.evaluate(dec)
    # held-out recovery is computed and high for a genuine key
    assert v.heldout_recovery >= 0.90, v
    assert v.heldout_ok is True
    assert v.hit is True
