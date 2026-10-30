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
