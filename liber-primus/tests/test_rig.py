"""Pytest regression suite for the Liber Primus rig.

Wraps the rig's self-validations as real assertions so `pytest` is the single
regression gate (CI runs this). Fast: the heavy work is the rig reproducing
known solved pages, which is the whole point of the gate.

Run:  pytest               (from liber-primus/)
"""
import os
import subprocess
import sys

import pytest

LP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(LP, "src"))


def _run(*args):
    env = dict(os.environ, PYTHONUTF8="1")
    return subprocess.run([sys.executable, *args], cwd=LP, env=env,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


# ---- unit: gematria is the single source of truth -----------------------
def test_gematria_table():
    from lp import gematria as gp
    assert gp.N == 29
    assert gp.PRIMES[0] == 2 and gp.PRIMES[-1] == 109
    # DIVINITY parses; V shares the U rune (ᚢ), so it transliterates to DIUINITY
    idx = gp.keyword_to_indices("DIVINITY")
    assert gp.indices_to_translit(idx) == "DIUINITY"
    assert gp.keyword_to_indices("DIVINITY") == gp.keyword_to_indices("DIUINITY")


# ---- core finding regression guard --------------------------------------
def test_unsolved_corpus_is_otp_flat():
    """The load-bearing statistical finding must not silently drift."""
    sys.path.insert(0, os.path.join(LP, "analysis"))
    from run_stats import load_pages
    from lp.stats import ioc_norm, doublet_rate
    unsolved = [i for p in load_pages()[:-2] for i in p]
    assert 9000 < len(unsolved) < 14000
    assert abs(ioc_norm(unsolved) - 1.0) < 0.05      # perfectly flat
    assert doublet_rate(unsolved) < 0.015            # ~5x doublet deficit


# ---- integration: the rig reproduces known solves -----------------------
def test_validate_reproduces_solved_pages():
    r = _run("tests/validate.py")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ALL VALIDATIONS PASSED" in r.stdout


def test_attack_selftest_refinds_divinity():
    r = _run("attack.py", "selftest")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "SELFTEST PASS" in r.stdout


def test_lp_try_scorer_selftest():
    r = _run("lp_try.py", "--selftest")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout


# ---- english baseline works WITHOUT the gitignored kjv.txt --------------
def test_english_baseline_fresh_clone_fallback():
    sys.path.insert(0, os.path.join(LP, "analysis"))
    from run_stats import english_baseline
    from lp.stats import ioc_norm, doublet_rate
    eng = english_baseline()
    assert len(eng) > 1000
    assert ioc_norm(eng) > 1.4                        # English-class, not flat
    assert 0.01 < doublet_rate(eng) < 0.06            # natural doublets


# ---- provenance: live images still match the published onion7 hashes --------
def test_image_provenance_live():
    """Guards the headline claim: the onion7 LP2 images are byte-authentic.
    Network-gated — skips (never fails) if archive.org is unreachable."""
    import hashlib, re, urllib.request
    base = "https://archive.org/download/ky2khlqdf7qdznac.onion"
    try:
        def fetch(url):
            req = urllib.request.Request(url, headers={"User-Agent": "cicada3301-rig"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        xml = fetch(base + "/ky2khlqdf7qdznac.onion_files.xml").decode("utf-8", "replace")
        pub = {m.group(1): re.search(r"<sha1>([0-9a-f]+)</sha1>", m.group(2)).group(1)
               for m in re.finditer(r'<file name="([^"]+\.jpg)"[^>]*>(.*?)</file>', xml, re.S)
               if re.search(r"<sha1>", m.group(2))}
        for name in ("0.jpg", "17.jpg"):
            got = hashlib.sha1(fetch(f"{base}/{name}")).hexdigest()
            assert got == pub[name], f"{name}: {got} != published {pub[name]}"
    except AssertionError:
        raise
    except Exception as e:
        pytest.skip(f"archive.org unreachable: {e}")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
