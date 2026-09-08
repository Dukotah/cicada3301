#!/usr/bin/env python3
"""Round 27 / P2 -- the ONE adapter that knows how to invoke the P1 C engine.

If P1 ships a different CLI, edit THIS file only (see ENGINE-CONTRACT.md); the checks
call engine.score_seeds / engine.sweep / engine.self_test and never build argv themselves.

Exit-code convention used by every check: 0 PASS, 1 FAIL, 2 BLOCKED-ON-BINARY.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P1 = os.path.join(LP, "analysis", "round27", "P1-engine")
VECTORS = os.path.join(LP, "analysis", "round27", "P0-spec", "vectors.json")

BLOCKED = 2


class Blocked(RuntimeError):
    """Binary or LM export not present yet -- check must exit 2, not fail."""


def find_binary():
    cands = [os.environ.get("GRIND27"),
             os.path.join(P1, "grind27"),
             os.path.join(P1, "build", "grind27")]
    for c in cands:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    raise Blocked("grind27 binary not found (probed: %s)" % [c for c in cands if c])


def find_lm():
    lm = os.environ.get("GRIND27_LM", os.path.join(P1, "panel_lm.f32"))
    if os.path.isfile(lm):
        return lm
    raise Blocked("panel_lm.f32 not found at %s" % lm)


def _run(argv, timeout=None):
    print("  [engine] %s" % " ".join(argv), file=sys.stderr)
    p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    return p


def _parse_jsonl(path):
    rows = []
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                rows.append(json.loads(ln))
            except ValueError:
                pass  # tolerate non-JSON noise lines
    return rows


def _last_json_line(text):
    for ln in reversed(text.strip().splitlines()):
        ln = ln.strip()
        if ln.startswith("{"):
            try:
                return json.loads(ln)
            except ValueError:
                continue
    return None


def score_seeds(seeds, full=False, cipher_idx=None, timeout=3600):
    """Run --mode score on a list of seeds; returns list of parsed JSON rows."""
    binary, lm = find_binary(), find_lm()
    with tempfile.TemporaryDirectory(prefix="p2harness.") as td:
        sf = os.path.join(td, "seeds.txt")
        of = os.path.join(td, "out.jsonl")
        with open(sf, "w") as f:
            f.write("\n".join(str(int(s)) for s in seeds) + "\n")
        argv = [binary, "--vectors", VECTORS, "--lm", lm, "--mode", "score",
                "--seeds", sf, "--out", of]
        if full:
            argv.append("--full")
        cf = None
        if cipher_idx is not None:
            cf = os.path.join(td, "cipher.json")
            with open(cf, "w") as f:
                json.dump({"cipher_idx": list(cipher_idx)}, f)
            argv += ["--cipher", cf]
        p = _run(argv, timeout=timeout)
        if p.returncode != 0:
            raise RuntimeError("engine score mode failed rc=%d\nstderr: %s"
                               % (p.returncode, p.stderr[-2000:]))
        rows = _parse_jsonl(of)
    if len(rows) != len(seeds):
        raise RuntimeError("engine returned %d rows for %d seeds" % (len(rows), len(seeds)))
    return rows


def sweep(band_start, band_end, out_candidates, threads=6, cipher_idx=None,
          progress_dir=None, timeout=None):
    """Run --mode sweep over [band_start, band_end); returns (summary, candidates)."""
    binary, lm = find_binary(), find_lm()
    argv = [binary, "--vectors", VECTORS, "--lm", lm, "--mode", "sweep",
            "--band-start", str(int(band_start)), "--band-end", str(int(band_end)),
            "--threads", str(int(threads)), "--out", out_candidates]
    tmp_cf = None
    if cipher_idx is not None:
        fd, tmp_cf = tempfile.mkstemp(prefix="p2cipher.", suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump({"cipher_idx": list(cipher_idx)}, f)
        argv += ["--cipher", tmp_cf]
    if progress_dir:
        argv += ["--progress-dir", progress_dir]
    try:
        p = _run(argv, timeout=timeout)
    finally:
        if tmp_cf:
            os.unlink(tmp_cf)
    if p.returncode != 0:
        raise RuntimeError("engine sweep failed rc=%d\nstderr: %s"
                           % (p.returncode, p.stderr[-2000:]))
    summary = _last_json_line(p.stdout)
    cands = _parse_jsonl(out_candidates) if os.path.exists(out_candidates) else []
    return summary, cands


def self_test(timeout=300):
    """Run --mode self-test; returns (returncode, parsed_json_or_None, raw stdout)."""
    binary, lm = find_binary(), find_lm()
    p = _run([binary, "--vectors", VECTORS, "--lm", lm, "--mode", "self-test"],
             timeout=timeout)
    return p.returncode, _last_json_line(p.stdout), p.stdout


def blocked_exit(msg):
    print("BLOCKED-ON-BINARY: %s" % msg)
    sys.exit(BLOCKED)
