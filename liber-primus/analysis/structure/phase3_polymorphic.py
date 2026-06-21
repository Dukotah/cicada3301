"""Phase 3: per-page polymorphic attack, pages 42-55 (krisyotam segment index).

For EACH page independently throw the full known-Cicada toolkit:
  - Atbash; Atbash+shift (all 29); plain shift (all 29) both signs
  - Vigenere ALL keys length 1-4 over 29-rune alphabet, both signs, +/-atbash
    (+ interrupter beam on the best raw vigenere candidates)
  - prime / totient / prime-1 keystreams, per-page offset search, both signs, +/-atbash
  - autokey (ciphertext + plaintext), seed*K grid, both signs, +/-atbash

Score every result with quadgram score_norm. Record per-page best.
"""
import os, sys, itertools, re, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lp import gematria as gp, ciphers, autokey, solve, score as _score
from run_stats import load_pages

N = gp.N
scorer = _score.default()
sc = scorer.score_norm

PAGES = load_pages()
RAW_SEGS = open(os.path.join(os.path.dirname(__file__), "..", "..", "data",
              "krisyotam_runes.txt"), encoding="utf-8").read().split("%")

def raw_runes(i):
    return "".join(re.findall(r"[ᚠ-᛿]", RAW_SEGS[i]))

def translit(idxs):
    return gp.indices_to_translit(idxs)

MAXLEN = max(len(p) for p in PAGES) + 300
PRIME  = ciphers.prime_stream(MAXLEN)
TOT    = ciphers.totient_stream(MAXLEN)
PRIME1 = ciphers.prime_totient_stream(MAXLEN)

# English monogram freq mapped onto 29-rune indices, for fast column shift
def _engfreq():
    base = {"E":12.7,"T":9.1,"A":8.2,"O":7.5,"I":7.0,"N":6.7,"S":6.3,"H":6.1,
            "R":6.0,"D":4.3,"L":4.0,"C":2.8,"U":2.8,"M":2.4,"W":2.4,"F":2.2,
            "G":2.0,"Y":2.0,"P":1.9,"B":1.5,"V":1.0,"K":0.8,"J":0.15,"X":0.15,
            "Q":0.1,"Z":0.07}
    import math
    f = [0.01] * N
    for ch, v in base.items():
        try:
            i = gp.keyword_to_indices(ch)[0]
            f[i] += v
        except Exception:
            pass
    tot = sum(f)
    return [math.log10(x / tot) for x in f]

def _best_col_shift(col, sign, eng):
    bestk, bests = 0, -1e9
    for k in range(N):
        s = 0.0
        for c in col:
            s += eng[(c + sign * k) % N]
        if s > bests:
            bests, bestk = s, k
    return bestk

def best_per_page(pi):
    idxs = PAGES[pi]
    n = len(idxs)
    best = [-999.0, "none", ""]

    def consider(s, method, txt):
        if s > best[0]:
            best[0], best[1], best[2] = s, method, txt

    # ---- shift + atbash + atbash-shift, both signs
    for atb in (False, True):
        base = ciphers.atbash_indices(idxs) if atb else idxs
        for k in range(N):
            for sign in (-1, +1):
                out = [(c + sign * k) % N for c in base]
                consider(sc(translit(out)),
                         f"{'atbash+' if atb else ''}shift{sign*k:+d}", translit(out))

    # ---- Vigenere keys length 2-3 EXHAUSTIVE (full quadgram), both signs, +/- atbash
    vig_top = []
    for atb in (False, True):
        base = ciphers.atbash_indices(idxs) if atb else idxs
        for L in (2, 3):
            for key in itertools.product(range(N), repeat=L):
                for sign in (-1, +1):
                    out = [(base[i] + sign * key[i % L]) % N for i in range(n)]
                    s = sc(translit(out))
                    if s > -6.0:
                        vig_top.append((s, L, key, sign, atb))
                    if s > best[0]:
                        consider(s, f"vig L{L} key{key} sign{sign:+d} atb{atb}", translit(out))
    # ---- Vigenere L=4..12 via per-column best-shift (monogram) hill, full-score check
    eng = _engfreq()
    for atb in (False, True):
        base = ciphers.atbash_indices(idxs) if atb else idxs
        for L in range(4, 13):
            for sign in (-1, +1):
                key = []
                for r in range(L):
                    col = [base[i] for i in range(r, n, L)]
                    key.append(_best_col_shift(col, sign, eng))
                out = [(base[i] + sign * key[i % L]) % N for i in range(n)]
                s = sc(translit(out))
                if s > -6.0:
                    vig_top.append((s, L, tuple(key), sign, atb))
                if s > best[0]:
                    consider(s, f"vigauto L{L} key{tuple(key)} sign{sign:+d} atb{atb}", translit(out))
    vig_top.sort(reverse=True)
    vig_top = vig_top[:8]

    # ---- interrupter beam on top vigenere candidates
    rr = raw_runes(pi)
    n_f = rr.count(gp.INTERRUPTER)
    if n_f > 0:
        for s0, L, key, sign, atb in vig_top:
            stream = ciphers.repeat_key(list(key), len(rr))
            res = solve.find_interrupters(rr, stream, sign=sign, atbash=atb,
                                          beam_width=300, scorer=scorer)
            consider(res["score_norm"],
                     f"vig L{L} key{key} sign{sign:+d} atb{atb} +interrupt({res['n_interrupters']})",
                     res["plaintext"])

    # ---- prime / totient / prime-1 keystreams, offset search
    for name, stream in (("prime", PRIME), ("totient", TOT), ("prime-1", PRIME1)):
        for atb in (False, True):
            base = ciphers.atbash_indices(idxs) if atb else idxs
            for off in range(0, 120):
                for sign in (-1, +1):
                    out = [(base[i] + sign * stream[off + i]) % N for i in range(n)]
                    s = sc(translit(out))
                    if s > best[0]:
                        consider(s, f"keystream {name} off{off} sign{sign:+d} atb{atb}", translit(out))

    # ---- autokey ct + pt, seed/K grid
    for kind, fn in (("ct-autokey", autokey.decrypt_ciphertext_autokey),
                     ("pt-autokey", autokey.decrypt_plaintext_autokey)):
        for atb in (False, True):
            for sign in (-1, +1):
                for seed in range(N):
                    for K in range(N):
                        out = fn(idxs, seed=seed, K=K, sign=sign, atbash=atb)
                        s = sc(translit(out))
                        if s > best[0]:
                            consider(s, f"{kind} seed{seed} K{K} sign{sign:+d} atb{atb}", translit(out))
    return best

results = []
for pi in range(42, 56):
    s, method, txt = best_per_page(pi)
    flag = "  <-- INVESTIGATE" if s > -5.5 else ""
    print(f"page {pi:2d}: best {s:7.3f}  {method}{flag}", flush=True)
    print(f"          {txt[:90]}", flush=True)
    results.append({"page": pi, "score": round(s, 4), "method": method, "plaintext": txt})

out = {"range": "42-55", "results": results}
json.dump(out, open(os.path.join(os.path.dirname(__file__), "phase3_results.json"), "w"), indent=2)
best_overall = max(results, key=lambda r: r["score"])
print("\nBEST OVERALL:", best_overall["page"], best_overall["score"], best_overall["method"], flush=True)
