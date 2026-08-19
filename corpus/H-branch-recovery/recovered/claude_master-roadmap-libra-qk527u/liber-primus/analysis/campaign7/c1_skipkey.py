"""Campaign VII — Track C1: the doublet-avoiding running key (novel mechanism).

Finding #2 ruled out natural-language running keys because a real English key
*injects* ~3.3% adjacent doublets, but LP2 shows 0.68%. That objection dies if the
encoder used a running key BUT skipped a key char whenever the raw output would
create an adjacent ciphertext doublet. Such a "doublet-avoiding running key"
reproduces the exact fingerprint (suppressed doublets, no clean period) AND is NOT
covered by the do-not-redo list (which tested only PLAIN running keys and the
short-key collision-skip variant — not a long key with insertions).

Mechanism (encryption): c_i = (p_i + T[u_i]) mod 29 where the key pointer u
advances by 1 normally but by 2 (one skip) at the ~0.66% of positions where the
un-skipped output would equal c_{i-1}. Decryption is a beam search over the key-
pointer trajectory u (advance in {1,2} per step), scoring the recovered plaintext
with quadgrams. If the right key text is among our candidates, English emerges.

Bounded probe: candidate key texts we already hold locally (Tao Te Ching, Gospel
of Thomas, Cicada PGP prose) + a coarse key-offset sweep, over the longer unsolved
pages. Not exhaustive over all pages/offsets — a mechanism sanity test, logged as
such. Any plaintext score_norm > -5.0 is a readable-English break.
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
A20 = os.path.join(HERE, "..", "armada20")
KEY_TEXTS = {
    "taoteching": os.path.join(A20, "taoteching.txt"),
    "thomas": os.path.join(A20, "thomas.txt"),
    "pgp_prose": os.path.join(A20, "pgp_english_prose.txt"),
}
BEAM = 120


def load_key(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    out = []
    for ch in txt.upper():
        try:
            out.extend(gp.keyword_to_indices(ch))
        except ValueError:
            pass
    return out


def beam_decrypt(cidx, key, offset):
    """Beam search over key-pointer trajectory; advance in {1,2} per position."""
    # beam: dict u_pointer -> (cum_score, plaintext_indices)
    beams = {offset: (0.0, [])}
    for c in cidx:
        nxt = {}
        for u, (sc, pl) in beams.items():
            for a in (1, 2):
                nu = u + a
                if nu >= len(key):
                    continue
                p = (c - key[nu]) % N
                npl = pl + [p]
                # incremental quadgram score on the tail
                if len(npl) >= 4:
                    q = SC.score(gp.indices_to_translit(npl[-4:]))
                else:
                    q = 0.0
                nsc = sc + q
                if nu not in nxt or nsc > nxt[nu][0]:
                    nxt[nu] = (nsc, npl)
        # prune to top BEAM by score
        beams = dict(sorted(nxt.items(), key=lambda kv: -kv[1][0])[:BEAM])
        if not beams:
            break
    # best final beam by normalized plaintext score
    best = None
    for u, (sc, pl) in beams.items():
        txt = gp.indices_to_translit(pl)
        s = SC.score_norm(txt)
        if best is None or s > best[0]:
            best = (s, txt)
    return best or (-99.0, "")


def run():
    pages = load_pages()
    unsolved = pages[:-2]
    # sample: the longer pages carry more signal for a mechanism test
    idx_by_len = sorted(range(len(unsolved)), key=lambda i: -len(unsolved[i]))
    sample = idx_by_len[:6]

    best = {"score": -99.0, "rec": None}
    results = []
    for kname, path in KEY_TEXTS.items():
        key = load_key(path)
        if len(key) < 400:
            continue
        offsets = [0, len(key) // 4, len(key) // 2]
        for pi in sample:
            cidx = unsolved[pi]
            for off in offsets:
                s, txt = beam_decrypt(cidx, key, off)
                rec = {"key_text": kname, "page": pi, "offset": off,
                       "score": round(s, 3), "plaintext": txt[:80]}
                results.append(rec)
                if s > best["score"]:
                    best.update(score=s, rec=rec)

    results.sort(key=lambda r: -r["score"])
    out = {"campaign": "VII", "track": "C1",
           "mechanism": "doublet-avoiding running key (beam over skip trajectory)",
           "beam": BEAM, "break_threshold": BREAK,
           "best_score": round(best["score"], 3), "best": best["rec"],
           "top": results[:15],
           "note": "Bounded mechanism test: 6 longest pages x 3 texts x 3 offsets, "
                   "advance in {1,2}. Not exhaustive over all pages/offsets/texts."}
    json.dump(out, open(os.path.join(HERE, "c1_skipkey_results.json"), "w"), indent=2)
    print(f"Track C1 — doublet-avoiding running key. best score_norm = {best['score']:.3f} "
          f"(break threshold {BREAK}, noise ~ -7.4)")
    for r in results[:8]:
        print(f"  {r['key_text']:10} p{r['page']:<2} off{r['offset']:<5} "
              f"{r['score']:.3f}  {r['plaintext'][:50]}")
    print("  BREAK!" if best["score"] > BREAK else "  no readable-English break (null)")
    return out


if __name__ == "__main__":
    run()
