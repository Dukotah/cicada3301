"""Comprehensive attack battery against the unsolved Liber Primus pages.

Subcommands (each writes JSON hits above an English threshold to --out):
  selftest                  prove the harness can re-find a known key (DIVINITY)
  vigenere   --wordlist F   keyed Vigenere over a keyword list + interrupter beam
  runningkey --key F        running key from a text file, all offsets (numpy)
  keystream                 prime / totient / fibonacci / square streams, swept

A "hit" is any per-page decryption whose quadgram score_norm exceeds THRESHOLD.
Real English ≈ -4.0..-4.4; gibberish ≈ -7.4. THRESHOLD = -5.2 catches anything
English-like with margin, while staying well clear of noise.

Usage:
  PYTHONUTF8=1 python attack.py vigenere --wordlist data/keys/words.txt --out hits.json
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "analysis"))
from lp import gematria as gp, ciphers, solve, score as _score, corpus  # noqa
from run_stats import load_pages, english_baseline  # noqa

import numpy as np  # noqa

N = gp.N
THRESHOLD = -5.2
SC = _score.default()


def unsolved_pages():
    pages = load_pages()
    return pages[:-2]  # last two are solved AN END / PARABLE


# monogram log-freq table for fast numpy filtering
def _mono_logp():
    eng = english_baseline()
    counts = np.bincount(np.array(eng), minlength=N).astype(float)
    counts += 1.0
    p = counts / counts.sum()
    return np.log10(p)


MONO = _mono_logp()


_BEST = {"score": -99.0, "rec": None}


def consider(score, rec):
    if score > _BEST["score"]:
        _BEST["score"] = score
        _BEST["rec"] = rec


def emit(hits, out):
    hits = sorted(hits, key=lambda h: -h["score"])
    payload = {"threshold": THRESHOLD, "n_hits": len(hits),
               "best_score_seen": round(_BEST["score"], 3),
               "best_candidate": _BEST["rec"], "hits": hits}
    if out:
        json.dump(payload, open(out, "w", encoding="utf-8"), indent=2)
    print(f"{len(hits)} hits over threshold {THRESHOLD}")
    print(f"best score seen: {_BEST['score']:.3f}  "
          f"(real English ~ -4.0..-4.4, gibberish ~ -7.4)")
    if _BEST["rec"]:
        print(f"  best: p{_BEST['rec'].get('page')} {_BEST['rec'].get('method','')} "
              f"{_BEST['rec'].get('key','')}  {_BEST['rec'].get('plaintext','')[:60]}")
    for h in hits[:12]:
        print(f"  p{h['page']:<2} {h['score']:.2f} {h['method']:<28} "
              f"{h.get('key','')[:18]:<18} {h['plaintext'][:60]}")
    return hits


# --------------------------------------------------------------- vigenere
def attack_vigenere(wordlist, out, interrupters=True):
    words = [w.strip().upper() for w in open(wordlist, encoding="utf-8")
             if w.strip() and w.strip().isalpha()]
    pages = unsolved_pages()
    hits = []
    for pi, idxs in enumerate(pages):
        runes_text = gp.indices_to_runes(idxs)
        best = None
        for w in words:
            try:
                key = gp.keyword_to_indices(w)
            except ValueError:
                continue
            for sign in (-1, +1):
                for atb in (False, True):
                    # cheap pass: no interrupters
                    stream = ciphers.repeat_key(key, len(idxs))
                    p = [( (N-1-c if atb else c) + sign*stream[j]) % N
                         for j, c in enumerate(idxs)]
                    s = SC.score_norm(gp.indices_to_translit(p))
                    consider(s, {"page": pi, "method": f"vigenere sign{sign:+d} atb{atb}",
                                 "key": w, "plaintext": gp.indices_to_translit(p)[:80]})
                    if best is None or s > best[0]:
                        best = (s, w, sign, atb)
        if best and best[0] > THRESHOLD - 1.0:  # promising: refine w/ interrupters
            s0, w, sign, atb = best
            key = gp.keyword_to_indices(w)
            stream = ciphers.repeat_key(key, len(idxs))
            if interrupters:
                r = solve.find_interrupters(runes_text, stream, sign=sign,
                                            atbash=atb, beam_width=300)
                s, txt = r["score_norm"], r["plaintext"]
            else:
                p = [((N-1-c if atb else c) + sign*stream[j]) % N
                     for j, c in enumerate(idxs)]
                s, txt = s0, gp.indices_to_translit(p)
            if s > THRESHOLD:
                hits.append({"page": pi, "method": f"vigenere sign{sign:+d} atb{atb}",
                             "key": w, "score": round(s, 3), "plaintext": txt[:200]})
    return emit(hits, out)


# --------------------------------------------------------------- running key
def attack_runningkey(keyfile, out, label=None):
    label = label or os.path.basename(keyfile)
    raw = open(keyfile, encoding="utf-8", errors="ignore").read()
    import re
    letters = re.sub(r"[^A-Za-z]", "", raw)
    key = np.array(gp.keyword_to_indices(letters[:60000]))
    pages = unsolved_pages()
    hits = []
    for pi, idxs in enumerate(pages):
        c = np.array(idxs)
        L = len(c)
        if len(key) < L + 1:
            continue
        noff = len(key) - L
        # vectorised: for each offset, plaintext = (c - key_window) mod N,
        # filtered by monogram log-prob; keep top-K offsets, then quadgram them.
        for sign in (-1, +1):
            for atb in (False, True):
                cc = (N - 1 - c) if atb else c
                # build sliding key matrix lazily in chunks to bound memory
                best_off, best_mono = [], []
                step = 4000
                for o0 in range(0, noff, step):
                    o1 = min(o0 + step, noff)
                    win = np.lib.stride_tricks.sliding_window_view(key, L)[o0:o1]
                    p = (cc[None, :] - sign * win) % N
                    mono = MONO[p].sum(axis=1)
                    k = min(8, len(mono))
                    top = np.argpartition(-mono, k - 1)[:k]
                    for t in top:
                        best_off.append(o0 + int(t))
                        best_mono.append(float(mono[t]))
                # quadgram-score the top monogram offsets
                order = np.argsort(best_mono)[::-1][:40]
                for oi in order:
                    o = best_off[oi]
                    p = (cc - sign * key[o:o + L]) % N
                    s = SC.score_norm(gp.indices_to_translit(p.tolist()))
                    consider(s, {"page": pi, "method": f"runningkey {label} sign{sign:+d} atb{atb} off{o}",
                                 "key": label, "plaintext": gp.indices_to_translit(p.tolist())[:80]})
                    if s > THRESHOLD:
                        hits.append({"page": pi,
                                     "method": f"runningkey {label} sign{sign:+d} atb{atb} off{o}",
                                     "key": label, "score": round(s, 3),
                                     "plaintext": gp.indices_to_translit(p.tolist())[:200]})
    return emit(hits, out)


# --------------------------------------------------------------- keystreams
def _fib(n, a, b):
    out = []
    for _ in range(n):
        out.append(a % N)
        a, b = b, (a + b) % N
    return out


def attack_keystream(out):
    pages = unsolved_pages()
    hits = []
    for pi, idxs in enumerate(pages):
        L = len(idxs)
        streams = {}
        for start in range(0, 40):
            streams[f"primes+{start}"] = ciphers.prime_stream(L, start)
            streams[f"totient(p)+{start}"] = ciphers.prime_totient_stream(L, start)
        for a in range(N):
            for b in range(N):
                if a == 0 and b == 0:
                    continue
                streams[f"fib({a},{b})"] = _fib(L, a, b)
        for name, st in streams.items():
            for sign in (-1, +1):
                for atb in (False, True):
                    p = [((N-1-c if atb else c) + sign*st[j]) % N
                         for j, c in enumerate(idxs)]
                    s = SC.score_norm(gp.indices_to_translit(p))
                    consider(s, {"page": pi, "method": f"keystream {name} sign{sign:+d} atb{atb}",
                                 "key": name, "plaintext": gp.indices_to_translit(p)[:80]})
                    if s > THRESHOLD:
                        hits.append({"page": pi, "method": f"keystream {name} sign{sign:+d} atb{atb}",
                                     "key": name, "score": round(s, 3),
                                     "plaintext": gp.indices_to_translit(p)[:200]})
    return emit(hits, out)


# --------------------------------------------------------------- selftest
def selftest(out):
    """Prove the Vigenere attack re-finds DIVINITY on the solved WELCOME page."""
    page = corpus.page_by_label("03.jpg")
    idxs = gp.runes_to_indices(page["runes"])
    runes_text = page["runes"]
    found = None
    for w in ["RANDOM", "DIVINITY", "PILGRIM", "SACRED"]:
        key = gp.keyword_to_indices(w)
        stream = ciphers.repeat_key(key, len(idxs))
        r = solve.find_interrupters(runes_text, stream, sign=-1, beam_width=400)
        ok = "WELCOME" in r["plaintext"].upper()
        print(f"  key={w:10s} score={r['score_norm']:.2f} hasWELCOME={ok}")
        if w == "DIVINITY" and ok:
            found = True
    print("SELFTEST", "PASS" if found else "FAIL")
    return 0 if found else 1


def main():
    ap = argparse.ArgumentParser()
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--out", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest", parents=[parent])
    a = sub.add_parser("vigenere", parents=[parent]); a.add_argument("--wordlist", required=True)
    a.add_argument("--no-interrupters", action="store_true")
    b = sub.add_parser("runningkey", parents=[parent]); b.add_argument("--key", required=True)
    b.add_argument("--label")
    sub.add_parser("keystream", parents=[parent])
    args = ap.parse_args()
    if args.cmd == "selftest":
        return selftest(args.out)
    if args.cmd == "vigenere":
        attack_vigenere(args.wordlist, args.out, not args.no_interrupters)
    elif args.cmd == "runningkey":
        attack_runningkey(args.key, args.out, args.label)
    elif args.cmd == "keystream":
        attack_keystream(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
