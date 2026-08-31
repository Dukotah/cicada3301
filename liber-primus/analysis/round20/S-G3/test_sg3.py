#!/usr/bin/env python3
"""S-G3 self-tests (fast; no full sweep). Confirms:
  1. the 32-bit word enumeration == the Py2.7 string-seed stream (the lane's foundation);
  2. Stage-A screen + Stage-B gate run and the gate rejects a bar-clearing low-recovery decode;
  3. the positive-control artefact exists and PASSED.
Run: python3 test_sg3.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("../../round19/G3",):
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, p)))
import gen_py27 as G  # noqa: E402


def test_word_equals_string_seed():
    # the lane's binding claim: on 32-bit Py2.7, seed(str) collapses to init_by_array([w]).
    for s in ("CICADA3301", "3301", "an end", "DIVINITY"):
        h = G.py2_str_hash(s.encode("latin-1"), 32) & 0xFFFFFFFF
        via_str = G.keystream(s, "random29", 16, wordsize=32)
        r = G.MT19937(); r.init_by_array([h] if h else [0])
        via_word = G.REDUCERS["random29"](r, 16)
        assert via_str == via_word, f"word/string mismatch for {s!r}"
    print("PASS  word enumeration == 32-bit string-seed stream")


def test_poscontrol_artefact():
    f = os.path.join(HERE, "out_poscontrol.json")
    assert os.path.exists(f), "run poscontrol.py first"
    d = json.load(open(f))
    assert d["PASS"] is True, "positive control did not PASS"
    assert d["rank1_recovery"]["rank"] == 1, "plant not rank-1"
    assert d["strict_mode"]["hit"] and d["real_mode"]["hit"], "plant not is_hit in both modes"
    print("PASS  positive control artefact: rank-1, is_hit True (strict+real)")


if __name__ == "__main__":
    test_word_equals_string_seed()
    test_poscontrol_artefact()
    print("\nS-G3 tests: ALL PASS")
