"""Campaign VII — token bytes as INDICES into the rune corpus (book-cipher reading).

Every keystream pairing failed, so test the other role: the 256 token bytes as a
selection/index over the runes (a book cipher), or as a self-contained gematria
message. Interpretations scored by English quadgram fitness:
  idx_abs   : rune at absolute corpus position token[i] (0-255 reach)
  idx_page  : rune at position token[i] within each token page's neighbour text
  idx_gaps  : cumulative-sum indexing (token[i] as a step) over the corpus
  self_gem  : the token values mod 29 read directly as Gematria runes (is the
              token pad itself a gematria message?)
A score_norm > -5.0 is a readable-English break. Self-contained.
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))
from lp import gematria as gp, score as _score  # noqa
from run_stats import load_pages  # noqa
from campaign7.a2_tokenpad import P49, P50, P51  # noqa

N = gp.N
SC = _score.default()
BREAK = -5.0
TOKEN = P49 + P50 + P51


def run():
    pages = load_pages()
    corpus = [i for pg in pages for i in pg]
    results = {}

    # idx_abs: rune at absolute position token[i]
    sel = [corpus[b] for b in TOKEN if b < len(corpus)]
    results["idx_abs"] = gp.indices_to_translit(sel)

    # idx_gaps: cumulative-sum stepping
    pos, sel2 = 0, []
    for b in TOKEN:
        pos = (pos + b) % len(corpus)
        sel2.append(corpus[pos])
    results["idx_gaps"] = gp.indices_to_translit(sel2)

    # idx_page: token[i] modulo each page length, over the three neighbour pages
    sel3 = []
    for pi, seq in ((49, P49), (50, P50), (51, P51)):
        pg = pages[pi]
        sel3 += [pg[b % len(pg)] for b in seq]
    results["idx_page"] = gp.indices_to_translit(sel3)

    # self_gem: token values mod 29 as runes directly
    results["self_gem"] = gp.indices_to_translit([b % N for b in TOKEN])

    scored = {k: round(SC.score_norm(v), 3) for k, v in results.items()}
    best = max(scored.items(), key=lambda kv: kv[1])
    out = {"campaign": "VII", "track": "token-as-index", "break_threshold": BREAK,
           "scores": scored, "best": {"interp": best[0], "score": best[1],
           "text": results[best[0]][:100]},
           "samples": {k: v[:80] for k, v in results.items()}}
    json.dump(out, open(os.path.join(HERE, "token_as_index_results.json"), "w"), indent=2)
    print("Token-as-index (book-cipher readings). score_norm (break > -5.0, noise ~ -7.4):")
    for k, s in sorted(scored.items(), key=lambda x: -x[1]):
        print(f"  {k:10} {s:.3f}  {results[k][:52]}")
    print("  BREAK!" if best[1] > BREAK else "  no readable-English break (null)")
    return out


if __name__ == "__main__":
    run()
