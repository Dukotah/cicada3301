#!/usr/bin/env python3
"""Convenience task runner for the Liber Primus rig — one entry to common jobs.

Usage:
  python tasks.py <task>

Tasks:
  validate   reproduce all solved pages (the trust anchor)
  test       fast regression gate (pytest -m "not network")
  test-full  full regression gate incl. live network checks (pytest)
  analyze    statistical + structural + crypto-rigor analyses (hardening track)
  seek       answer-seeking probes (novel attack angles)
  cross      transcription cross-diff (auto-fetches sources)
  dataset    rebuild dataset/liber_primus.json
  fetch      download the gitignored third-party transcription sources
  all        validate + test + analyze            (harden track)
  evo        validate + test + analyze + seek      (dual-track: harden AND seek)
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


# Base tasks: each maps to a list of commands.
TASKS = {
    "validate":  [[PY, "tests/validate.py"]],
    "test":      [[PY, "-m", "pytest", "tests/", "-q", "-m", "not network"]],
    "test-full": [[PY, "-m", "pytest", "tests/", "-q"]],
    "analyze":   [[PY, "analysis/run_stats.py"],
                  [PY, "analysis/structure_analysis.py"],
                  [PY, "analysis/crypto_rigor.py"]],
    "seek":      [[PY, "analysis/seek_primes.py"]],   # answer-seeking probes
    "cross":     [[PY, "analysis/transcription/crossdiff.py"]],
    "dataset":   [[PY, "dataset/build_dataset.py"]],
    "fetch":     [[PY, "data/fetch_sources.py"]],
}
# Composite tasks: expand to other task names (no command duplication).
COMPOSITE = {
    "all": ["validate", "test", "analyze"],     # hardening track
    "evo": ["validate", "test", "analyze", "seek"],  # dual-track: harden + seek
}


def _commands(task):
    if task in COMPOSITE:
        return [cmd for sub in COMPOSITE[task] for cmd in TASKS[sub]]
    return TASKS.get(task, [])


def main():
    valid = set(TASKS) | set(COMPOSITE)
    if len(sys.argv) != 2 or sys.argv[1] not in valid:
        print(__doc__)
        print("available:", ", ".join(sorted(valid)))
        return 1
    for cmd in _commands(sys.argv[1]):
        rc = _run(*cmd)
        if rc != 0:
            print(f"FAILED ({rc}): {' '.join(cmd[1:])}")
            return rc
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
