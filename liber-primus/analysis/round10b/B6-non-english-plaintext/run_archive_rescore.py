"""B6 run 3 — re-score every ARCHIVED best-candidate decrypt in the repo under the
non-English / language-agnostic instruments.

This executes campaign14/REDTEAM-PROPOSALS.md item
"[very-low] Language-agnostic and non-English re-scoring of all sweep bests".

IMPORTANT STRUCTURAL FINDING recorded by this script: the archives do NOT contain
the sweeps' candidate decodes. Every sweep stored only the argmax-under-the-ENGLISH-
metric candidate, truncated to ~80 characters. Re-scoring what survived therefore
cannot recover a non-English hit that the sweep passed over -- the selection was
performed by the very metric we are trying to bypass. This script quantifies what
IS recoverable and states the residue.
"""
import glob
import io
import json
import os
import re
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detectors as D
import run_lang as RL

HERE = os.path.dirname(os.path.abspath(__file__))
LPROOT = D.LP
RNG = np.random.default_rng(31337)

TR2IDX = sorted([(t, i) for i, t in enumerate(D.TRANSLIT)], key=lambda p: -len(p[0]))


def translit_to_runes(s):
    s = s.upper()
    out, i = [], 0
    while i < len(s):
        hit = None
        for tr, idx in TR2IDX:
            if s.startswith(tr, i):
                hit = (tr, idx)
                break
        if hit:
            out.append(hit[1])
            i += len(hit[0])
        else:
            i += 1
    return np.array(out, dtype=np.int64)


def collect():
    """Every archived 'plaintext' string in the repo's result JSONs."""
    cands = []
    pats = [os.path.join(LPROOT, "*.json"),
            os.path.join(LPROOT, "analysis", "**", "*.json")]
    for pat in pats:
        for f in glob.glob(pat, recursive=True):
            if "round10b" + os.sep + "B6" in f:
                continue
            try:
                txt = io.open(f, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for m in re.finditer(r'"plaintext":\s*"([^"]{20,})"', txt):
                cands.append((os.path.relpath(f, LPROOT), m.group(1)))
    return cands


def main():
    cands = collect()
    print("archived candidate decrypts found:", len(cands))
    lms, sizes = RL.build_lms()
    rows = []
    for src, s in cands:
        r = translit_to_runes(s)
        if len(r) < 20:
            continue
        row = {"src": src, "len_runes": int(len(r)), "text": s[:120]}
        for lk, lm in lms.items():
            row["LM_" + lk] = round(D.score_trigram(lm, r), 4)
        w = min(24, len(r))
        for nm, det in D.AGNOSTIC.items():
            if nm == "D4_compress":
                continue
            v = det(r, w)
            row[nm] = round(float(v.max()), 4) if len(v) else None
        row["tokens"] = D.d6_tokens(r)
        rows.append(row)

    # null: random rune strings of the same lengths, same instruments
    Ls = sorted(set(r["len_runes"] for r in rows))
    null = {}
    for L in Ls:
        acc = {}
        for _ in range(400):
            x = RNG.integers(0, D.N, size=L)
            for lk, lm in lms.items():
                acc.setdefault("LM_" + lk, []).append(D.score_trigram(lm, x))
            w = min(24, L)
            for nm, det in D.AGNOSTIC.items():
                if nm == "D4_compress":
                    continue
                v = det(x, w)
                acc.setdefault(nm, []).append(float(v.max()) if len(v) else 0.0)
        null[L] = {k: {"mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1)),
                       "max": float(np.max(v))} for k, v in acc.items()}

    flagged = []
    for row in rows:
        nl = null[row["len_runes"]]
        row["z"] = {}
        for k, st in nl.items():
            if row.get(k) is None:
                continue
            z = (row[k] - st["mean"]) / st["sd"] if st["sd"] > 0 else 0.0
            row["z"][k] = round(z, 2)
            if z >= 4.0 and row[k] > st["max"]:
                flagged.append((row["src"], k, row[k], z))
    json.dump({"n_candidates": len(rows), "rows": rows, "null": null,
               "flagged": flagged},
              open(os.path.join(HERE, "archive_rescore.json"), "w"), indent=1)
    print("scored:", len(rows))
    print("FLAGGED (z>=4 and above null max):", json.dumps(flagged, indent=1))
    # summary: best z per instrument across the whole archive
    best = {}
    for row in rows:
        for k, z in row["z"].items():
            if k not in best or z > best[k][0]:
                best[k] = (z, row["src"])
    for k in sorted(best, key=lambda k: -best[k][0]):
        print("%-14s best z=%+.2f  (%s)" % (k, best[k][0], best[k][1]))


if __name__ == "__main__":
    main()
