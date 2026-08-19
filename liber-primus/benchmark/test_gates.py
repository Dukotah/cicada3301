"""pytest wrapper for the plant-and-recover gates.

    python3 -m pytest liber-primus/benchmark/ -q

Every gate asserts BOTH directions: a planted signal is recovered, and a wrong key stays
in noise. A gate that could never fail would be decoration, so the negative-direction
assertions are as load-bearing as the positive ones.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gates as G


def _assert_gate(r):
    assert r["passed"], (
        f"GATE FAILED: {r['gate']}\n"
        f"  why it exists : {r['why']}\n"
        f"  recovered     : {r.get('recovered_score', r.get('beam_correct_key'))}\n"
        f"  wrong key     : {r.get('wrong_key_score', r.get('rigid_correct_key'))}\n"
        f"  recovery      : {r.get('recovery')}\n"
        f"A failing gate means the instrument cannot detect the family it covers, so any "
        f"null over that family is not a negative result.")


def test_running_key_no_filter_rigid():
    _assert_gate(G.gate_running_rigid())


def test_running_key_skip_filter_beam():
    _assert_gate(G.gate_running_skip())


def test_running_key_rewrite_filter_beam():
    """RECON-B/B-16: the decoder was validated on key-skip, never on value-rewrite."""
    _assert_gate(G.gate_running_rewrite())


def test_derived_sha256_ctr():
    """The one hypothesis class the ciphertext cannot exclude."""
    _assert_gate(G.gate_derived_sha_ctr())


def test_seeded_prng():
    _assert_gate(G.gate_prng())


def test_rigid_scores_correct_key_as_noise():
    """The most important single fact in this repository.

    Same filtered ciphertext, same CORRECT key: rigid decoding lands in the noise band
    while the skip-aware beam recovers the plaintext. Any rigid-decoder null over a
    filtered cipher is therefore unsound -- which invalidates a large fraction of the
    published 'ruled out' claims about Liber Primus, including years of this repo's own.
    """
    r = G.gate_rigid_vs_beam()
    _assert_gate(r)
    assert r["rigid_correct_key"] <= G.NOISE_CEIL
    assert r["beam_correct_key"] >= G.ENGLISH
    assert r["margin"] > 1.0


def test_shuffled_plant_is_not_recovered():
    """Negative direction: guards against a scorer that rewards letter frequency."""
    _assert_gate(G.gate_shuffled_plant_not_recovered())


def test_all_gates_pass():
    results = G.run_all(verbose=False)
    failed = [r["gate"] for r in results if not r["passed"]]
    assert not failed, f"gates failed: {failed}"
