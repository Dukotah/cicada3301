"""Tests for the register-aware oracle (verify_solution.py). Single process, small L; < 2 min."""
import os
import random
import subprocess
import sys

import pytest

LP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, LP)
import verify_solution as vs  # noqa: E402

pytestmark = pytest.mark.skipif(
    not (os.path.exists(vs.PANEL_R36_PATH) and os.path.exists(vs.PANEL_R36_TEST)),
    reason="panel-R36 build artefacts not present in this checkout")


def test_selftest_four_registers_recovered(capsys):
    assert vs.selftest() == 0
    out = capsys.readouterr().out
    for reg in ("EN_MODERN", "LATIN", "EN_NOVOWEL", "GREEK"):
        assert f"{reg}=ok" in out
        # Round 44 audit A0: a key that runs as ONE stream across the page break must also pass
        assert f"{reg}:cont=ok" in out


def test_continuous_key_passes_where_restart_judge_fails():
    """The defect closed on 2026-11-12: every seeded-generator sweep assumes one continuous key
    stream, but the oracle decoded every page from K[0]. A correct continuous key must PASS the
    continuous judge; the per-page-restart judge alone must not be what decides it."""
    vs.load_instruments(quiet=True)
    rnd = random.Random(20261112)
    plain = vs._plant_pages("EN_MODERN")
    K = [rnd.randrange(29) for _ in range(4096)]
    c_flat = vs._encipher([x for pg in plain for x in pg], K, seed=7)[0]
    pages = [c_flat[:len(plain[0])], c_flat[len(plain[0]):]]
    ok_c, rel, _ = vs.decide_continuous(vs.judge_continuous(K, pages, relations=("keyskip1",)))
    ok_r, _, _ = vs.decide(vs.judge_register(K, pages, relations=("keyskip1",)))
    assert ok_c and rel == "keyskip1"
    assert not ok_r
    wrong = [random.Random(5).randrange(29) for _ in range(4096)]
    assert not vs.decide_continuous(vs.judge_continuous(wrong, pages, relations=("keyskip1",)))[0]


def test_random_key_fails_with_conditionals(tmp_path):
    rnd = random.Random(99)
    ks = tmp_path / "rand_key.txt"
    ks.write_text(" ".join(str(rnd.randrange(29)) for _ in range(13000)))
    r = subprocess.run([sys.executable, os.path.join(LP, "verify_solution.py"), "--keystream", str(ks),
                        "--pages", "2", "--skip-anchor"],
                       capture_output=True, text=True, timeout=600, cwd=LP)
    out = r.stdout
    assert r.returncode == 1, out + r.stderr
    assert "VERDICT: FAIL" in out
    assert "exactly three conditionals" in out
    assert "NEGATIVE UNDER THESE REGISTERS/RELATIONS ONLY" in out
    assert "LEGACY" in out
    assert "VERDICT: PASS" not in out
