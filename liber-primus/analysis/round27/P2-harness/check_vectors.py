#!/usr/bin/env python3
"""Check 1 -- vector parity (SPEC V1).

C engine, --mode score --full, over all 64 seeds in vectors.json["seed_vectors"]:
  ks128 exact / plain_idx exact / ptr_end,n_skips,nchars exact / pmax |diff| <= 1e-9
  (which at these magnitudes is also <= 1e-6 relative, the task-level gate).
Also verifies P1's panel_lm.f32 export sha256 against the panel.npz that generated the
vectors.

  --pyref : additionally re-score a subset with the PYTHON reference and require exact
            reproduction (harness self-check; runs without the binary).

Exit: 0 PASS, 1 FAIL, 2 BLOCKED-ON-BINARY.
"""
import argparse
import hashlib
import os
import sys

import engine
import pyref

ABS_TOL = 1e-9
REL_TOL = 1e-6


def close(a, b):
    d = abs(a - b)
    return d <= ABS_TOL or d <= REL_TOL * max(abs(a), abs(b))


def pyref_selfcheck(vecs):
    subset = [r for r in vecs["seed_vectors"]
              if r["seed"] in (0, 1, 3301, 1325734783, 2149309687, 4294967295)]
    subset += vecs["seed_vectors"][6:8]  # two of the random-draw seeds
    bad = 0
    for r in subset:
        got = pyref.stage_a_full(r["seed"])
        ok = (got["ks128"] == r["ks128"] and got["plain_idx"] == r["plain_idx"]
              and got["pmax"] == float(r["pmax"]) and got["ptr_end"] == r["ptr_end"]
              and got["n_skips"] == r["n_skips"] and got["nchars"] == r["nchars"])
        print("  pyref seed %-10d pmax %-22r %s" % (r["seed"], got["pmax"],
                                                    "OK" if ok else "MISMATCH"))
        bad += 0 if ok else 1
    return bad == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pyref", action="store_true",
                    help="also exact-reproduce a vector subset with the Python reference")
    args = ap.parse_args()

    vecs = pyref.vectors()
    print("check_vectors: %d seed vectors" % len(vecs["seed_vectors"]))

    if args.pyref:
        print("pyref self-check (Python reference must reproduce vectors exactly):")
        if not pyref_selfcheck(vecs):
            print("FAIL: Python reference no longer reproduces vectors.json -- "
                  "pipeline drifted; regenerate vectors or find the drift FIRST.")
            return 1
        print("  pyref self-check OK")

    # ---- LM export integrity (P1 must export from the SAME panel.npz) ----------
    try:
        lm_path = engine.find_lm()
        want = pyref.expected_lm_sha256()
        got = hashlib.sha256(open(lm_path, "rb").read()).hexdigest()
        if got != want:
            print("FAIL: panel_lm.f32 sha256 mismatch\n  got  %s\n  want %s" % (got, want))
            return 1
        print("panel_lm.f32 sha256 OK (%s)" % want[:16])
    except engine.Blocked as e:
        engine.blocked_exit("%s (pyref side %s)" % (
            e, "verified" if args.pyref else "not requested; rerun with --pyref"))

    # ---- drive the C engine over all 64 vectors --------------------------------
    try:
        rows = engine.score_seeds([r["seed"] for r in vecs["seed_vectors"]], full=True)
    except engine.Blocked as e:
        engine.blocked_exit(str(e))

    fails = []
    worst = 0.0
    for ref, got in zip(vecs["seed_vectors"], rows):
        w = ref["seed"]
        if got.get("seed") != w:
            fails.append((w, "row order/seed mismatch: got %r" % got.get("seed")))
            continue
        d = abs(float(got["pmax"]) - float(ref["pmax"]))
        worst = max(worst, d)
        if got.get("ks128") != ref["ks128"]:
            fails.append((w, "ks128 mismatch"))
        if got.get("plain_idx") != ref["plain_idx"]:
            fails.append((w, "plain_idx mismatch"))
        if not close(float(got["pmax"]), float(ref["pmax"])):
            fails.append((w, "pmax %r vs ref %s (|d|=%.3g)" % (got["pmax"], ref["pmax"], d)))
        for k in ("ptr_end", "n_skips", "nchars"):
            if got.get(k) != ref[k]:
                fails.append((w, "%s %r vs %r" % (k, got.get(k), ref[k])))

    print("max |pmax diff| over 64 seeds: %.3g (tol %.0e abs / %.0e rel)"
          % (worst, ABS_TOL, REL_TOL))
    if fails:
        for w, msg in fails[:20]:
            print("  FAIL seed %d: %s" % (w, msg))
        print("FAIL: %d mismatches" % len(fails))
        return 1
    print("PASS: all 64 seed vectors match (ks128/plain_idx/ptr_end/n_skips/nchars exact, "
          "pmax within tolerance)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
