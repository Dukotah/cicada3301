"""Campaign VII — community "false holes": untried ideas from the solver wiki.

The Uncovering-Cicada "Ideas and Suggestions" wiki + solver repos propose several
methods "never tried" that our rig had not tested because it strips separators.
We test them and record the negatives so a future solver sees they were run:

  FH1 "count spaces as runes"  — the word/clause/line separators (- . /) ADVANCE
       the keystream instead of being ignored, desyncing the key by the separator
       count. (Our attacks strip separators, so this alignment was never tested.)
  FH2 "section-split + first-rune gematria shift" — Caesar-shift each page by the
       Gematria value (index or prime) of its own first rune.
  FH3 "segment key-reset Vigenere" (r4nd0mD3v3l0p3r's splitBy=segment) — the key
       index resets at each segment/clause/word boundary rather than running
       continuously across the page.
  FH4 "OutGuess-relocate the runes before shifting" — NOT run: premise is false
       (see note in output); our Campaign VII stego proved the LP rune pages carry
       no OutGuess payload, so there is no relocation data to apply.

Keystreams for FH1/FH3 use the families that solve real LP pages (prime, prime-1,
totient) + the known key DIVINITY. score_norm > -5.0 = readable-English break.
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
WORD, CLAUSE, LINE = "-", ".", "/"
SEG = set("&$")


def raw_pages():
    txt = open(KRIS, encoding="utf-8").read()
    return [seg for seg in txt.split("%") if any(gp.is_rune(c) for c in seg)]


def stream(name, L):
    if name == "prime":
        return ciphers.prime_stream(L)
    if name == "prime_minus_1":
        return ciphers.prime_totient_stream(L)
    if name == "totient":
        return ciphers.totient_stream(L)
    if name == "DIVINITY":
        return ciphers.repeat_key(gp.keyword_to_indices("DIVINITY"), L)
    return [0] * L


def fh1_spaces_advance(pages):
    """Separators advance the key index (count as runes)."""
    best = {"score": -99, "rec": None}
    for sepset_name, seps in [("-", {WORD}), ("-.", {WORD, CLAUSE}),
                              ("-./", {WORD, CLAUSE, LINE})]:
        for kname in ("prime", "prime_minus_1", "totient", "DIVINITY"):
            for pi, raw in enumerate(pages):
                # length = runes + counted separators
                total = sum(1 for c in raw if gp.is_rune(c) or c in seps)
                st = stream(kname, total + 4)
                k, plain = 0, []
                for c in raw:
                    if gp.is_rune(c):
                        plain.append((gp.RUNE_TO_IDX[c] - st[k]) % N)
                        k += 1
                    elif c in seps:
                        k += 1  # advance key, emit nothing
                s = SC.score_norm(gp.indices_to_translit(plain))
                if s > best["score"]:
                    best.update(score=s, rec={"sepset": sepset_name, "key": kname,
                                "page": pi, "text": gp.indices_to_translit(plain)[:70]})
    return best


def fh2_first_rune_shift(pages):
    best = {"score": -99, "rec": None}
    for pi, raw in enumerate(pages):
        idxs = gp.runes_to_indices(raw)
        if not idxs:
            continue
        first = idxs[0]
        for shift, sname in [(first, "idx"), (gp.PRIMES[first] % N, "prime"),
                             ((N - 1 - first), "atbash_idx")]:
            for sign in (-1, +1):
                plain = [(c + sign * shift) % N for c in idxs]
                s = SC.score_norm(gp.indices_to_translit(plain))
                if s > best["score"]:
                    best.update(score=s, rec={"page": pi, "shift": sname,
                                "sign": sign, "text": gp.indices_to_translit(plain)[:70]})
    return best


def fh3_segment_reset(pages, known_tail=2):
    """Vigenere/keystream with key index reset at each boundary char.

    Reports both the all-pages best (which correctly RE-SOLVES the known AN END
    page, validating the mechanism) and the unsolved-only best (the real result:
    the last `known_tail` pages are already-solved AN END / parable)."""
    best_all = {"score": -99, "rec": None}
    best_uns = {"score": -99, "rec": None}
    for reset_name, resets in [("word", {WORD}), ("clause", {CLAUSE}),
                               ("line", {LINE}), ("segment", SEG)]:
        for kname in ("DIVINITY", "prime", "prime_minus_1"):
            for pi, raw in enumerate(pages):
                plain, k = [], 0
                seg_stream = stream(kname, 300)
                for c in raw:
                    if gp.is_rune(c):
                        plain.append((gp.RUNE_TO_IDX[c] - seg_stream[k % len(seg_stream)]) % N)
                        k += 1
                    elif c in resets:
                        k = 0  # reset key at boundary
                s = SC.score_norm(gp.indices_to_translit(plain))
                rec = {"reset": reset_name, "key": kname, "page": pi,
                       "text": gp.indices_to_translit(plain)[:70]}
                if s > best_all["score"]:
                    best_all.update(score=s, rec=rec)
                if pi < len(pages) - known_tail and s > best_uns["score"]:
                    best_uns.update(score=s, rec=rec)
    return {"best_all_pages": best_all, "best_unsolved_only": best_uns,
            "note": "best_all_pages is a correct re-solve of the KNOWN AN END page "
                    "(validates the segment-reset mechanism); best_unsolved_only is "
                    "the real negative on genuinely-unsolved pages."}


def run():
    pages = raw_pages()
    fh1 = fh1_spaces_advance(pages)
    fh2 = fh2_first_rune_shift(pages)
    fh3 = fh3_segment_reset(pages)
    out = {"campaign": "VII", "track": "false-holes", "break_threshold": BREAK,
           "FH1_spaces_advance_keystream": fh1,
           "FH2_first_rune_gematria_shift": fh2,
           "FH3_segment_key_reset": fh3,
           "FH4_outguess_relocation": {
               "status": "NOT RUN — premise false",
               "reason": "Requires OutGuess payload on the LP rune pages to relocate "
                         "runes. Campaign VII stego (real OutGuess 0.4, built from "
                         "source, validated on all 2012-14 payloads) proved the rune "
                         "pages carry NO payload; the tabs/spaces OutGuess data belongs "
                         "to the 2012/2014 CLUE images, not the rune pages. No "
                         "relocation data exists to apply."}}
    json.dump(out, open(os.path.join(HERE, "false_holes_results.json"), "w"), indent=2)
    print("Community 'false holes' — best score_norm (break > -5.0, noise ~ -7.4):")
    print(f"  FH1 spaces-advance-keystream       {fh1['score']:.3f}   {fh1['rec']['text'][:44]}")
    print(f"  FH2 first-rune gematria shift      {fh2['score']:.3f}   {fh2['rec']['text'][:44]}")
    print(f"  FH3 segment key-reset (all pages)  {fh3['best_all_pages']['score']:.3f}   "
          f"{fh3['best_all_pages']['rec']['text'][:44]}  <- KNOWN AN END re-solve")
    print(f"  FH3 segment key-reset (unsolved)   {fh3['best_unsolved_only']['score']:.3f}   "
          f"{fh3['best_unsolved_only']['rec']['text'][:44]}")
    print("  FH4 OutGuess-relocation: NOT RUN — premise false (no payload on rune pages)")
    hit = max(fh1["score"], fh2["score"], fh3["best_unsolved_only"]["score"])
    print("  BREAK on an unsolved page!" if hit > BREAK
          else "  all null on unsolved pages — these community ideas are false holes")
    return out


if __name__ == "__main__":
    run()
