"""VALIDATION GATE — the rig must re-derive KNOWN solved pages or it is useless.

For each solved page we either apply the documented transform or brute-force the
small space of simple transforms (direct / Atbash / shift, both directions) and
confirm the best-scoring output is real English containing the documented words.
Vigenère pages additionally run the interrupter beam search.

Run: PYTHONUTF8=1 python tests/validate.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from lp import corpus, ciphers, solve, gematria as gp, score as _score  # noqa


def clean(s):
    return re.sub(r"[^A-Z]", "", s.upper())


def canon(s):
    """Collapse shared-rune transliteration ambiguities so word-matching is
    fair: ᚳ=C/K, ᚢ=U/V, ᛋ=S/Z, and treat Q as C. (The rune alphabet genuinely
    cannot distinguish these — it is not a decryption error.)"""
    s = clean(s)
    for a, b in (("K", "C"), ("V", "U"), ("Z", "S"), ("Q", "C")):
        s = s.replace(a, b)
    return s


def brute_simple(idxs, scorer):
    """Try direct, atbash, and all caesar shifts (+/- ) with/without atbash.
    Return (best_label, best_text, best_score)."""
    cands = []
    for atb in (False, True):
        base = ciphers.atbash_indices(idxs) if atb else idxs
        for k in range(gp.N):
            for sign in (-1, +1):
                out = [(c + sign * k) % gp.N for c in base]
                txt = gp.indices_to_translit(out)
                lbl = f"{'atbash+' if atb else ''}shift{sign*k:+d}"
                cands.append((lbl, txt, scorer.score_norm(txt)))
    cands.sort(key=lambda x: x[2], reverse=True)
    return cands[0]


def main():
    scorer = _score.default()
    ok = True
    # page label, type, (key), must-contain words
    SOLVED = [
        ("Runes - 01.jpg", "simple",  None,       ["WARN", "BELIEVE", "FROMTHIS", "TRUE"]),
        ("05.jpg",         "simple",  None,       ["PRIMES", "SACRED", "TOTIENT"]),
        ("06.jpg",         "simple",  None,       ["MANDECIDED", "MASTER", "STUDY"]),
        ("03.jpg",         "vigenere", "DIVINITY", ["WELCOME", "PILGRIM", "JOURNEY", "NECESSARY"]),
        ("14.jpg",         "vigenere", "FIRFUMFERENFE", ["LESSON", "MASTER", "EXPLAINED", "STUDENT"]),
    ]
    for label, kind, key, expect in SOLVED:
        page = corpus.page_by_label(label)
        if not page or not page["runes"]:
            print(f"FAIL  {label:16s} no runes parsed")
            ok = False
            continue
        idxs = gp.runes_to_indices(page["runes"])
        if kind == "simple":
            lbl, txt, sc = brute_simple(idxs, scorer)
            method = lbl
        else:
            nr = len(idxs)
            stream = ciphers.repeat_key(gp.keyword_to_indices(key), nr)
            res = solve.find_interrupters(page["runes"], stream, sign=-1,
                                          beam_width=500, scorer=scorer)
            txt, sc = res["plaintext"], res["score_norm"]
            method = f"vigenere {key} (+{res['n_interrupters']} interrupters)"
        up = canon(txt)
        hits = sum(canon(w) in up for w in expect)
        passed = hits == len(expect)
        ok = ok and passed
        print(f"{'PASS' if passed else 'FAIL'}  {label:16s} {hits}/{len(expect)} "
              f"words  score={sc:6.2f}  via {method}")
        print(f"      {up[:96]}")
    print("\n" + ("=== ALL VALIDATIONS PASSED — rig reproduces known solves. ==="
                  if ok else "=== VALIDATION FAILED ==="))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
