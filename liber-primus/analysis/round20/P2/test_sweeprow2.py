"""P2 -- SWEEPROW/2 round-trip + backward-compat test. Run: python3 test_sweeprow2.py"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sweeprow2 as S2
import nskips_lib as NL
import driftbeam as DB
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "analysis", "round19", "I2")))
import adjudicate as A


def test_field_order():
    assert S2.ROW_FIELDS[:13] == A.ROW_FIELDS
    assert S2.ROW_FIELDS[13:] == ["n_skips", "n_unexplained"]
    assert S2.SCHEMA_VERSION == "SWEEPROW/2"
    print("PASS field order: /2 = /1[:13] + [n_skips, n_unexplained]")


def test_roundtrip_and_backcompat():
    # a real planted decode -> full SWEEPROW/2 row
    C, K, P, gt = NL.plant("EN", 120, 0, mech="keyskip", supp=0.83)
    dec = DB.beam_decode(C, K, sign=-1, o=0, mode="keyskip1",
                         **{k: v for k, v in NL.PRESET["keyskip1"].items() if k != "mode"})
    adj = A.adjudicate(dec["plain_idx"])
    row = S2.to_row(adj, dec, kid="plant=keyskip,supp=0.83")
    assert len(row) == 15, row
    # fields 0..12 must STILL validate as SWEEPROW/1 (byte-compat proof)
    A.validate_row(list(row[:13]))
    # full row validates as SWEEPROW/2
    hdr = S2.header("P2/test", key_space="planted", decoder="I1.keyskip1")
    S2.validate_row(row, hdr)
    assert row[13] == dec["n_skips"] and row[14] == dec["n_unexplained"]
    print(f"PASS roundtrip: row[13]=n_skips={row[13]} row[14]=n_unexplained={row[14]}; "
          f"first 13 validate as SWEEPROW/1")

    # store round-trip
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps(hdr) + "\n")
        for i in range(5):
            f.write(json.dumps(S2.to_row(adj, dec, kid=f"k{i}")) + "\n")
        path = f.name
    rep = S2.validate_store(path)
    os.unlink(path)
    assert rep["rows_validated"] == 5 and rep["schema"] == "SWEEPROW/2"
    print(f"PASS store: {rep['rows_validated']} rows validate as /2 AND forward-read as /1")


def test_rejects_missing_skip():
    # a SWEEPROW/1 row (13 fields) must be rejected by the /2 validator
    C, K, P, gt = NL.plant("EN", 120, 1, mech="keyskip", supp=0.83)
    dec = DB.beam_decode(C, K, sign=-1, o=0, mode="keyskip1",
                         **{k: v for k, v in NL.PRESET["keyskip1"].items() if k != "mode"})
    adj = A.adjudicate(dec["plain_idx"])
    short = A.to_row(adj, "k")   # only 13 fields
    try:
        S2.validate_row(short)
    except S2.RowError:
        print("PASS rejects a bare SWEEPROW/1 row (missing skip channel)")
        return
    raise AssertionError("SWEEPROW/2 validator accepted a 13-field row")


def test_screen():
    if not os.path.exists(os.path.join(HERE, "nskips_null.json")):
        print("SKIP screen test: nskips_null.json not built yet")
        return
    r = S2.screen_nskips(2, "keyskip1", 120)
    assert "p_two_sided" in r and "extreme" in r
    print(f"PASS screen: n_skips=2 keyskip1 L120 -> p_two={r['p_two_sided']:.3f} "
          f"extreme={r['extreme']}")


if __name__ == "__main__":
    test_field_order()
    test_roundtrip_and_backcompat()
    test_rejects_missing_skip()
    test_screen()
    print("\nALL P2 SWEEPROW/2 TESTS PASS")
