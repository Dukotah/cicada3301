"""Campaign VII — the book's OWN matrices as Hill-cipher keys (hint-derived).

Cicada printed three matrices in the Liber Primus corpus: the SOME WISDOM 5x5
magic square (trace 1033, cells partly spelled as words whose gematria sums
complete it), a second 5x5 (trace 3301), and a 4x4 (trace 10673). The 2014
interactive phase demanded solvers "post the three magic squares" -- matrices
are first-class objects to Cicada. Our prior Hill coverage (2x2 exhaustive, 3x3
sampled) never included these specific matrices; r4nd0mD3v3l0p3r ran them but
segment-split only, one direction, with no automated scoring and no published
result. This is the first rigorous, quadgram-scored, recorded run.

For each matrix (and r4nd0m's phi-substituted variants): reduce mod 29, check
invertibility (det != 0 mod 29), and apply all four linear transforms -- M, M^T,
M^-1, (M^T)^-1 -- to consecutive rune blocks, per page and whole book. Score.
score_norm > -5.0 = readable-English break.
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))
from lp import gematria as gp, score as _score  # noqa
from run_stats import load_pages  # noqa

N = gp.N
SC = _score.default()
BREAK = -5.0

MATRICES = {
    "M1_1033": [[272, 138, 341, 131, 151], [366, 199, 130, 320, 18],
                [226, 245, 91, 245, 226], [18, 320, 130, 199, 366],
                [151, 131, 341, 138, 272]],
    "M2_3301": [[434, 1311, 312, 278, 966], [204, 812, 934, 280, 1071],
                [626, 620, 809, 620, 626], [1071, 280, 934, 812, 204],
                [966, 278, 312, 1311, 434]],
    "M3_4x4":  [[3258, 3222, 3152, 3038], [3278, 3299, 3298, 2838],
                [3288, 3294, 3296, 2472], [4516, 1206, 708, 820]],
    # r4nd0m's phi(n)-substituted variants (their tasks.examples.txt)
    "M1_phi":  [[289, 139, 341, 131, 151], [367, 199, 131, 425, 19],
                [227, 245, 91, 245, 227], [19, 425, 131, 199, 367],
                [151, 131, 341, 139, 289]],
    "M2_phi":  [[434, 1311, 313, 278, 967], [309, 841, 934, 281, 1071],
                [626, 933, 809, 933, 626], [1071, 281, 934, 841, 309],
                [967, 278, 313, 1311, 434]],
    "M3_phi":  [[3259, 3222, 3152, 3038], [3278, 3299, 3299, 2838],
                [4115, 3294, 3296, 2473], [4517, 1206, 709, 821]],
}


def mat_mod(M):
    return [[v % N for v in row] for row in M]


def mat_inv_mod(M):
    """Gaussian elimination mod prime N; returns inverse or None."""
    n = len(M)
    A = [row[:] + [1 if i == j else 0 for j in range(n)]
         for i, row in enumerate(M)]
    for col in range(n):
        piv = next((r for r in range(col, n) if A[r][col] % N), None)
        if piv is None:
            return None
        A[col], A[piv] = A[piv], A[col]
        inv = pow(A[col][col], N - 2, N)
        A[col] = [(v * inv) % N for v in A[col]]
        for r in range(n):
            if r != col and A[r][col]:
                f = A[r][col]
                A[r] = [(A[r][c] - f * A[col][c]) % N for c in range(2 * n)]
    return [row[n:] for row in A]


def transpose(M):
    return [list(r) for r in zip(*M)]


def apply_hill(idxs, M):
    n = len(M)
    out = []
    for b in range(0, len(idxs) - n + 1, n):
        block = idxs[b:b + n]
        out.extend(sum(M[r][c] * block[c] for c in range(n)) % N for r in range(n))
    return out


def run():
    pages = load_pages()
    unsolved = pages[:-2]
    whole = [i for pg in unsolved for i in pg]
    targets = [("p%02d" % pi, pg) for pi, pg in enumerate(unsolved)]
    targets.append(("WHOLE", whole))

    best = {"score": -99.0, "rec": None}
    per_matrix = {}
    invertibility = {}

    for mname, Mraw in MATRICES.items():
        M = mat_mod(Mraw)
        Minv = mat_inv_mod([r[:] for r in M])
        invertibility[mname] = Minv is not None
        variants = {"M": M, "MT": transpose(M)}
        if Minv is not None:
            variants["Minv"] = Minv
            MTinv = mat_inv_mod(transpose(M))
            if MTinv is not None:
                variants["MTinv"] = MTinv
        for vname, mat in variants.items():
            for tname, idxs in targets:
                p = apply_hill(idxs, mat)
                if not p:
                    continue
                s = SC.score_norm(gp.indices_to_translit(p))
                key = f"{mname}.{vname}"
                if s > per_matrix.get(key, -99):
                    per_matrix[key] = round(s, 3)
                if s > best["score"]:
                    best.update(score=s, rec={"matrix": mname, "variant": vname,
                                "target": tname,
                                "text": gp.indices_to_translit(p)[:70]})

    out = {"campaign": "VII", "track": "hill5-magic (hint-derived)",
           "break_threshold": BREAK, "invertible_mod29": invertibility,
           "best_score": round(best["score"], 3), "best": best["rec"],
           "per_matrix_best": per_matrix}
    json.dump(out, open(os.path.join(HERE, "hill5_magic_results.json"), "w"), indent=2)
    print("Book matrices as Hill keys (mod 29). Invertibility:", invertibility)
    print(f"best score_norm = {best['score']:.3f} (break > {BREAK}, noise ~ -7.4)")
    for k, s in sorted(per_matrix.items(), key=lambda x: -x[1])[:8]:
        print(f"  {k:14} {s}")
    r = best["rec"]
    print(f"  best: {r['matrix']}.{r['variant']} {r['target']}\n    {r['text']}")
    print("  BREAK!" if best["score"] > BREAK else "  null — the book's matrices are not the key")
    return out


if __name__ == "__main__":
    run()
