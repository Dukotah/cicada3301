"""Campaign VII — reading-direction transforms ("their numbers are the DIRECTION").

The last untested literal reading of the verified 2016 hint: DIRECTION = the
physical reading order of the runes on the page. The transcription preserves
line breaks ('/'), so we can re-read each page in alternate orders and then
apply the cipher families that solve real LP pages. Prior work eliminated
generic transposition-only and page reorderings, but never line-structured
reading orders (boustrophedon, column-major) COMBINED with the solved-page
cipher set.

Reading orders per page: rows (control), whole-page reversed, boustrophedon
(alternate lines reversed), column-major, column-major reversed.
Ciphers after reorder: direct, atbash, all 29 shifts, prime / prime-1 / totient
streams, Vigenere DIVINITY. score_norm > -5.0 = readable-English break.
(Grid-spiral is not runnable: lines are ragged, no rectangular grid exists.)
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))
from lp import gematria as gp, ciphers, score as _score  # noqa

N = gp.N
SC = _score.default()
BREAK = -5.0
KRIS = os.path.join(HERE, "..", "..", "data", "krisyotam_runes.txt")


def line_pages():
    """Pages as lists of lines; each line = list of rune indices."""
    txt = open(KRIS, encoding="utf-8").read()
    pages = []
    for seg in txt.split("%"):
        lines = []
        for ln in seg.split("/"):
            idxs = gp.runes_to_indices(ln)
            if idxs:
                lines.append(idxs)
        if lines:
            pages.append(lines)
    return pages


def orders(lines):
    rows = [i for ln in lines for i in ln]
    yield "rows", rows
    yield "reversed", rows[::-1]
    yield "boustro", [i for j, ln in enumerate(lines)
                      for i in (ln if j % 2 == 0 else ln[::-1])]
    maxw = max(len(ln) for ln in lines)
    cm = [ln[c] for c in range(maxw) for ln in lines if c < len(ln)]
    yield "colmajor", cm
    yield "colmajor_rev", cm[::-1]


def cipher_suite(idxs):
    L = len(idxs)
    yield "direct", idxs
    yield "atbash", ciphers.atbash_indices(idxs)
    for sh in range(1, N):
        yield f"shift{sh}", [(c - sh) % N for c in idxs]
    for nm, st in [("prime", ciphers.prime_stream(L)),
                   ("prime-1", ciphers.prime_totient_stream(L)),
                   ("totient", ciphers.totient_stream(L))]:
        for sign in (-1, +1):
            yield f"{nm}{sign:+d}", [(c + sign * st[i]) % N
                                     for i, c in enumerate(idxs)]
    key = gp.keyword_to_indices("DIVINITY")
    st = ciphers.repeat_key(key, L)
    yield "DIVINITY", [(c - st[i]) % N for i, c in enumerate(idxs)]


def run():
    pages = line_pages()
    unsolved_n = len(pages) - 2  # known-solved tail
    best = {"score": -99.0, "rec": None}
    best_unsolved = {"score": -99.0, "rec": None}
    per_order = {}

    for pi, lines in enumerate(pages):
        for oname, idxs in orders(lines):
            for cname, plain in cipher_suite(idxs):
                if oname == "rows" and cname in ("direct",):
                    pass  # control included deliberately
                s = SC.score_norm(gp.indices_to_translit(plain))
                rec = {"page": pi, "order": oname, "cipher": cname,
                       "text": gp.indices_to_translit(plain)[:70]}
                if s > per_order.get(oname, -99):
                    per_order[oname] = round(s, 3)
                if s > best["score"]:
                    best.update(score=s, rec=rec)
                if pi < unsolved_n and s > best_unsolved["score"]:
                    best_unsolved.update(score=s, rec=rec)

    out = {"campaign": "VII", "track": "reading-direction (hint-derived)",
           "break_threshold": BREAK,
           "best_all": {"score": round(best["score"], 3), **best["rec"]},
           "best_unsolved": {"score": round(best_unsolved["score"], 3),
                             **best_unsolved["rec"]},
           "per_order_best": per_order,
           "note": "best_all may re-find known solved tail pages (control); "
                   "best_unsolved is the real result."}
    json.dump(out, open(os.path.join(HERE, "reading_direction_results.json"), "w"),
              indent=2)
    print("Reading-direction transforms x solved-page cipher suite:")
    for o, s in sorted(per_order.items(), key=lambda x: -x[1]):
        print(f"  {o:14} best {s}")
    ru = best_unsolved["rec"]
    print(f"  best (known-tail control): {best['score']:.3f} "
          f"p{best['rec']['page']} {best['rec']['order']}/{best['rec']['cipher']}")
    print(f"  best UNSOLVED: {best_unsolved['score']:.3f} "
          f"p{ru['page']} {ru['order']}/{ru['cipher']}\n    {ru['text']}")
    print("  BREAK on unsolved!" if best_unsolved["score"] > BREAK
          else "  null on unsolved — reading direction is not the mechanism")
    return out


if __name__ == "__main__":
    run()
