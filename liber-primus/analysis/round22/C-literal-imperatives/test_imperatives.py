"""Round 22 Lane C self-checks: the operations are invertible and the recognizer works.

Run: python3 analysis/round22/C-literal-imperatives/test_imperatives.py
These are the plant-and-recover gates the null trusts (doctrine mechanic 2). They must pass
before any negative in RESULTS.md means anything.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import imperatives as I  # noqa: E402


def test_interleave_roundtrip():
    seq = I.known_english(400)
    assert I.deinterleave4(I.interleave4(seq)) == seq, "X1c de-interleave must invert interleave"


def test_reversal_roundtrip():
    seq = I.known_english(300)
    k = 7
    ct = I.shift(list(reversed(seq)), k)
    back = list(reversed(I.shift(ct, -k)))
    assert back == seq, "X3a reversal decrypt must recover the plaintext"


def test_phase0_controls_recover():
    p0 = I.phase0()
    assert p0["X1_deinterleave_recovers"]["pass"], p0["X1_deinterleave_recovers"]
    assert p0["X3a_reversal_recovers"]["pass"], p0["X3a_reversal_recovers"]
    assert p0["X3b_runningkey_recovers"]["pass"], p0["X3b_runningkey_recovers"]
    assert p0["X4_numberkeystream_recovers"]["pass"], p0["X4_numberkeystream_recovers"]


def test_recognizer_rejects_flat_stream():
    # a decimated LP2 substream is flat -> must NOT clear the panel-max bar.
    seq = I.lp2_stream()
    rows = I.score_structural([("decim0", I.decimate(seq, 0, 4))])
    assert not rows[0]["clears_null"], "flat decimated stream should never clear the bar"


if __name__ == "__main__":
    test_interleave_roundtrip()
    test_reversal_roundtrip()
    test_recognizer_rejects_flat_stream()
    test_phase0_controls_recover()
    print("OK: all Round-22 Lane-C self-checks pass")
