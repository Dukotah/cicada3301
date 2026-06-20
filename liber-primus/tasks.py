#!/usr/bin/env python3
"""Convenience task runner for the Liber Primus rig — one entry to common jobs.

Usage:
  python tasks.py <task>

Tasks:
  validate   reproduce all solved pages (the trust anchor)
  test       fast regression gate (pytest -m "not network")
  test-full  full regression gate incl. live provenance check (pytest)
  analyze    run the statistical + structural + crypto-rigor analyses
  cross      transcription cross-diff (auto-fetches sources)
  dataset    rebuild dataset/liber_primus.json
  fetch      download the gitignored third-party transcription sources
  all        validate + test + analyze
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def _run(*args):
    print(f"$ {' '.join(os.path.basename(a) if a == PY else a for a in args)}")
    return subprocess.run(args, cwd=HERE,
                          env=dict(os.environ, PYTHONUTF8="1")).returncode


TASKS = {
    "validate":  [[PY, "tests/validate.py"]],
    "test":      [[PY, "-m", "pytest", "tests/test_rig.py", "-q", "-m", "not network"]],
    "test-full": [[PY, "-m", "pytest", "tests/test_rig.py", "-q"]],
    "analyze":   [[PY, "analysis/run_stats.py"],
                  [PY, "analysis/structure_analysis.py"],
                  [PY, "analysis/crypto_rigor.py"]],
    "cross":     [[PY, "analysis/transcription/crossdiff.py"]],
    "dataset":   [[PY, "dataset/build_dataset.py"]],
    "fetch":     [[PY, "data/fetch_sources.py"]],
    "all":       [[PY, "tests/validate.py"],
                  [PY, "-m", "pytest", "tests/test_rig.py", "-q", "-m", "not network"],
                  [PY, "analysis/run_stats.py"],
                  [PY, "analysis/crypto_rigor.py"]],
}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in TASKS:
        print(__doc__)
        print("available:", ", ".join(TASKS))
        return 1
    for cmd in TASKS[sys.argv[1]]:
        rc = _run(*cmd)
        if rc != 0:
            print(f"FAILED ({rc}): {' '.join(cmd[1:])}")
            return rc
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
