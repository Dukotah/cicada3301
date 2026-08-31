"""Round 23 Lane A2 — sweep the printed-line/word acrostic reads over the REAL
solved plaintext laid out to the TRUE page-image line/word geometry.

Gated on PHASE0-GATE.py PASS (recovery 1.000 for line-first AND word-first).
Enumerates the FROZEN read set (PREREG.md): {line_first, line_last, word_first,
word_last} x {5 per-page + 1 concat} x {forward, reversed} = 48 candidates. Scores
each with the English quadgram recognizer against its OWN size-matched, structure-
preserving null (solved letter pool, order-shuffled, seed 3301, FPR 1e-3). Persists
language-agnostic secondary stats per candidate (doctrine R3).

A candidate is a per-cell SURVIVOR iff score_norm > its size-matched bar (FPR 1e-3);
a FAMILY survivor iff it also clears the max-of-null-over-all-lengths bar. Any survivor
is FLAGGED-FOR-ORACLE (R21 L1), never auto-certified.
"""
import os, sys, json, math, random, gzip
from collections import Counter
import lib_geom as G

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 3301
FPR = 0.001
N_SHUFFLES = 1000

READS = {
    "line_first": G.line_first_tokens,
    "line_last": G.line_last_tokens,
    "word_first": G.word_first_tokens,
    "word_last": G.word_last_tokens,
}


# ---------------------------------------------------------------- secondary stats

def _letters_and_syms(letters):
    return list(letters)


def ioc_times_n(letters):
    syms = list(letters)
    n = len(syms)
    if n < 2:
        return 0.0
    c = Counter(syms)
    num = sum(v * (v - 1) for v in c.values())
    return (num / (n * (n - 1))) * len(set(syms))


def min_distinct_32(letters):
    syms = list(letters)
    if len(syms) <= 32:
        return len(set(syms))
    m = 999
    for i in range(len(syms) - 32 + 1):
        m = min(m, len(set(syms[i:i + 32])))
    return m


def base32_fraction(letters):
    if not letters:
        return 0.0
    b32 = sum(1 for ch in letters if ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
    return b32 / len(letters)


def gzip_ratio(letters):
    s = letters.encode()
    if not s:
        return 1.0
    return len(gzip.compress(s, 9)) / max(1, len(s))


def stats(letters):
    return {
        "len": len(letters),
        "score_norm": round(G.scorer().score_norm(letters), 4) if letters else 0.0,
        "ioc_n": round(ioc_times_n(letters), 4),
        "min_distinct_32": min_distinct_32(letters) if letters else 0,
        "base32_frac": round(base32_fraction(letters), 4),
        "gzip_ratio": round(gzip_ratio(letters), 4),
    }


# ---------------------------------------------------------------- null

_POOL = None


def pool():
    global _POOL
    if _POOL is None:
        s = ""
        for _, _, lines in G.load_all_pages():
            s += G.page_flat_letters(lines)
        _POOL = s
    return _POOL


def length_keyed_null(lengths, n_shuffles=N_SHUFFLES, seed=SEED, fpr=FPR):
    """{L: (bar_fpr1e-3, mean, max)} — size-matched null of the solved letter pool."""
    rnd = random.Random(seed)
    chars = list(pool())
    out = {}
    for L in sorted(set(lengths)):
        if L == 0:
            out[0] = (0.0, 0.0, 0.0)
            continue
        scores = []
        for _ in range(n_shuffles):
            rnd.shuffle(chars)
            scores.append(G.scorer().score_norm("".join(chars[:L])))
        scores.sort()
        idx = min(len(scores) - 1, int(math.ceil((1 - fpr) * len(scores))) - 1)
        out[L] = (scores[idx], sum(scores) / len(scores), scores[-1])
    return out


# ---------------------------------------------------------------- enumerate reads

def enumerate_candidates(pages):
    """Yield (descriptor, letters) over the FROZEN 48-candidate read set."""
    # per-page
    for label, _, lines in pages:
        tag = label.replace(".jpg", "").replace(" ", "").replace("-", "")
        for rname, rfn in READS.items():
            toks = rfn(lines)
            letters = G.tokens_to_letters(toks)
            yield (f"{tag}|{rname}|fwd", letters)
            yield (f"{tag}|{rname}|rev", letters[::-1])
    # concatenated across all pages, book order
    for rname, rfn in READS.items():
        toks = []
        for _, _, lines in pages:
            toks += rfn(lines)
        letters = G.tokens_to_letters(toks)
        yield (f"CONCAT|{rname}|fwd", letters)
        yield (f"CONCAT|{rname}|rev", letters[::-1])


def main():
    pages = G.load_all_pages()
    cands = list(enumerate_candidates(pages))
    lengths = [len(s) for _, s in cands]
    print(f"[A2] {len(cands)} candidate reads, "
          f"{len(set(lengths))} distinct lengths, pool len {len(pool())}")

    bars = length_keyed_null(lengths)
    fam_bar = max(b[2] for b in bars.values())

    rows = []
    for desc, letters in cands:
        st = stats(letters)
        L = len(letters)
        bar, nmean, nmax = bars[L]
        st["desc"] = desc
        st["null_bar_fpr1e-3"] = round(bar, 4)
        st["null_mean"] = round(nmean, 4)
        st["excess_over_bar"] = round(st["score_norm"] - bar, 4)
        st["survivor_percell"] = st["score_norm"] > bar and L >= 4
        st["survivor_family"] = st["score_norm"] > fam_bar and L >= 4
        st["text"] = letters[:120]
        rows.append(st)

    rows.sort(key=lambda r: -r["excess_over_bar"])
    survivors_cell = [r for r in rows if r["survivor_percell"]]
    survivors_fam = [r for r in rows if r["survivor_family"]]
    exp_fp = round(len(cands) * FPR, 4)

    print(f"[A2] family-wise bar (max null over all lengths) = {fam_bar:.3f}")
    print(f"[A2] per-cell survivors (FPR1e-3): {len(survivors_cell)} "
          f"(expected FP ~{exp_fp}); family survivors: {len(survivors_fam)}")
    print("[A2] top-8 by excess over own null bar:")
    for r in rows[:8]:
        print(f"   {r['desc']:>22}  L={r['len']:<4} score={r['score_norm']:.3f} "
              f"bar={r['null_bar_fpr1e-3']:.3f} exc={r['excess_over_bar']:+.3f}  "
              f"{r['text'][:40]}")

    out = {
        "lane": "R23-A2-LINE-ACROSTIC",
        "hypothesis": "self-embedded message hides as first-rune-of-each-printed-line "
                      "(or per-word) acrostic of the solved pages, using TRUE page-image "
                      "line breaks + word spacing (roadmap A2 / R22-A not_covered)",
        "geometry_source": "data/scream314_lp.md via src/lp/corpus.py (same as validate.py)",
        "seed": SEED, "fpr": FPR, "n_shuffles": N_SHUFFLES,
        "phase0_recovery_linefirst_wordfirst": 1.0,
        "n_candidates": len(cands),
        "n_distinct_lengths": len(set(lengths)),
        "family_bar": round(fam_bar, 4),
        "expected_fp_percell": exp_fp,
        "n_survivors_percell": len(survivors_cell),
        "n_survivors_family": len(survivors_fam),
        "survivors_percell": survivors_cell,
        "survivors_family": survivors_fam,
        "all_candidates_sorted": rows,
    }
    out["verdict"] = ("NULL -- no line/word acrostic of the solved plaintext (at the true "
                      "printed geometry) is more English than chance at the pre-registered "
                      "bar" if len(survivors_fam) == 0 else
                      "SURVIVOR(S) -- FLAGGED-FOR-ORACLE (not auto-certified, R21 L1)")
    with open(os.path.join(HERE, "sweep_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\nVERDICT:", out["verdict"])
    return out


if __name__ == "__main__":
    main()
