"""Round 22 Lane A -- run the self-embedded-read sweep over the REAL solved plaintext.

Gated on PHASE0-GATE.py PASS (recovery/power 1.000). Enumerates the frozen selection set
over the concatenated solved-page plaintext, in TWO representations (letter stream + greedy
rune-index stream), scores each candidate with the English quadgram recognizer, and compares
each candidate to its OWN size-matched null (same selection length, order-shuffled source,
seed 3301, FPR 1e-3). Persists language-agnostic secondary stats per candidate (doctrine R3).

A candidate is a SURVIVOR iff score_norm > its size-matched null bar (per-cell, FPR 1e-3)
AND it also clears the family-wise Gumbel/max-of-N bar across the whole sweep. Any survivor is
FLAGGED-FOR-ORACLE, never auto-certified (R21 L1 seal note).
"""
import os, sys, json, math, random
import lib_selfread as L

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 3301
FPR = 0.001
N_SHUFFLES = 1000


def length_keyed_null(base_syms, lengths, n_shuffles=N_SHUFFLES, seed=SEED):
    """For each distinct selection length, the null distribution of score_norm for a random
    contiguous slice of that length from order-shuffles of base_syms. Returns
    {len: (bar_fpr, mean, max)}.  base_syms is a list (letters or rune-index ints)."""
    rnd = random.Random(seed)
    syms = list(base_syms)
    out = {}
    for Ln in sorted(set(lengths)):
        scores = []
        for _ in range(n_shuffles):
            rnd.shuffle(syms)
            scores.append(L.english_score(syms[:Ln]))
        scores.sort()
        idx = min(len(scores) - 1, int(math.ceil((1 - FPR) * len(scores))) - 1)
        mean = sum(scores) / len(scores)
        out[Ln] = (scores[idx], mean, scores[-1])
    return out


def run_stream(name, seq):
    """Sweep one representation. seq is a list of letters (chars) or rune-index ints."""
    # collect all selections + their lengths
    sels = list(L.enumerate_selections(seq))
    lengths = [len(sub) for _, sub in sels]
    print(f"[{name}] {len(sels)} selection functions, "
          f"{len(set(lengths))} distinct lengths, source len {len(seq)}")
    bars = length_keyed_null(seq, lengths)

    rows = []
    for desc, sub in sels:
        st = L.full_stats(sub)
        Ln = len(sub)
        bar, nmean, nmax = bars[Ln]
        st["desc"] = desc
        st["null_bar_fpr1e-3"] = round(bar, 4)
        st["null_mean"] = round(nmean, 4)
        st["excess_over_bar"] = round(st["score_norm"] - bar, 4)
        st["z_over_null_mean"] = round(st["score_norm"] - nmean, 4)
        st["survivor_percell"] = st["score_norm"] > bar
        st["text"] = L.to_letters(sub)[:120]
        rows.append(st)

    # family-wise (max-of-N) bar: the max over ALL null draws across all lengths, i.e. what
    # the single best selection would have to beat if the whole book were pure noise.
    fam_bar = max(b[2] for b in bars.values())
    survivors_cell = [r for r in rows if r["survivor_percell"]]
    survivors_fam = [r for r in rows if r["score_norm"] > fam_bar]
    rows.sort(key=lambda r: -r["excess_over_bar"])

    print(f"[{name}] per-cell survivors (FPR1e-3): {len(survivors_cell)} / {len(rows)}")
    print(f"[{name}] family-wise bar (max null over all lengths) = {fam_bar:.3f}; "
          f"family survivors: {len(survivors_fam)}")
    print(f"[{name}] top-5 by excess over own null bar:")
    for r in rows[:5]:
        print(f"    {r['desc']:>18}  L={r['len']:<4} score={r['score_norm']:.3f} "
              f"bar={r['null_bar_fpr1e-3']:.3f} excess={r['excess_over_bar']:.3f}  "
              f"{r['text'][:48]}")
    return {
        "stream": name,
        "source_len": len(seq),
        "n_selections": len(sels),
        "n_distinct_lengths": len(set(lengths)),
        "family_bar": round(fam_bar, 4),
        "n_survivors_percell": len(survivors_cell),
        "n_survivors_family": len(survivors_fam),
        "survivors_percell": sorted(survivors_cell, key=lambda r: -r["excess_over_bar"]),
        "survivors_family": survivors_fam,
        "top20_by_excess": rows[:20],
    }


def main():
    letters = list(L.concat_letters())
    runes = L.concat_rune_indices()
    print(f"solved concat: {len(letters)} letters, {len(runes)} rune indices (greedy)\n")

    out = {
        "lane": "R22-A-SELFEMBEDDED-READ",
        "hypothesis": "the message is a selection (acrostic/every-k/diagonal) of the "
                      "ALREADY-SOLVED plaintext, not the ciphertext (roadmap X2)",
        "seed": SEED, "fpr": FPR, "n_shuffles": N_SHUFFLES,
        "phase0_recovery": 1.0,
        "streams": [],
    }
    out["streams"].append(run_stream("letters", letters))
    print()
    out["streams"].append(run_stream("runes", runes))

    # overall verdict
    any_cell = sum(s["n_survivors_percell"] for s in out["streams"])
    any_fam = sum(s["n_survivors_family"] for s in out["streams"])
    out["total_percell_survivors"] = any_cell
    out["total_family_survivors"] = any_fam
    out["verdict"] = ("NULL -- no selection of the solved plaintext is more English than "
                      "chance at the pre-registered bar"
                      if any_fam == 0 else
                      "SURVIVOR(S) -- FLAGGED-FOR-ORACLE (not auto-certified, R21 L1)")
    with open(os.path.join(HERE, "sweep_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"\n=== TOTAL per-cell survivors: {any_cell} | family survivors: {any_fam} ===")
    print("VERDICT:", out["verdict"])
    return out


if __name__ == "__main__":
    main()
