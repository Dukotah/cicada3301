"""B6 run 2 — NON-ENGLISH plaintext sweep over the monoalphabetic + short-periodic
decode families, plus a machine-token crib search that is exhaustive over every
monoalphabetic decode.

Part A: rune-space trigram LMs for EN / LA / DE / CY (Welsh) / OE / RG (solved-LP
        English). For every unsolved page, hill-climb a periodic Vigenere key of
        length 1..8 to MAXIMISE each language's score. Null = the identical search
        run on shuffled pages (so hill-climb optimism is charged to the null too).

Part B: token cribs (ONION, HTTP, coordinate words, digit words...). Two searches,
        both exhaustive rather than sampled:
          B1 DIFF-PATTERN: match the token's consecutive-difference signature in the
             ciphertext difference stream -> finds the token under ALL 29 shifts at
             once; the negated pattern covers the Atbash-composed family; reversed
             stream covers reading backwards.
          B2 EQUALITY-PATTERN: match only the token's repeated-letter pattern
             -> finds the token under ANY of the 29! monoalphabetic substitutions.
"""
import io
import json
import os
import re
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detectors as D

HERE = os.path.dirname(os.path.abspath(__file__))
LP = D.LP
RNG = np.random.default_rng(760213)
NREP = 10          # null replicates of the whole page set
MAXL = 8


# ------------------------------------------------------------------- corpora

def _mid(t, frac=0.8):
    n = len(t)
    a = int(n * (1 - frac) / 2)
    return t[a:n - a]


def _read(p):
    return io.open(p, encoding="utf-8", errors="replace").read()


def load_corpora():
    c = {}
    c["EN"] = ("EN", _mid(_read(os.path.join(LP, "data", "kjv.txt")))[:1200000])
    la = _mid(_read(os.path.join(LP, "data", "keys", "armada19",
                                 "virgil_aeneid_latin.txt")))
    la += _mid(_read(os.path.join(LP, "analysis", "latin", "latin_28233.txt")))
    c["LA"] = ("LA", la)
    de = _mid(_read(os.path.join(HERE, "corpora", "de_faust.txt")))
    de += _mid(_read(os.path.join(HERE, "corpora", "de_2.txt")))
    c["DE"] = ("DE", de)
    c["CY"] = ("CY", _mid(_read(os.path.join(LP, "data", "keys", "welsh",
                                             "welsh_mabinogion.txt"))))
    oe = _read(os.path.join(HERE, "corpora", "oe_beowulf.txt"))
    oe_lines = [l for l in oe.split("\n")
                if re.search(r"[þðæÞÐÆ]", l)]
    oe = "\n".join(oe_lines)
    oe += _read(os.path.join(LP, "data", "keys", "runepoem_oe.txt"))
    c["OE"] = ("OE", oe)
    sp = _read(os.path.join(LP, "data", "keys", "solved_plaintext.txt"))
    keep = []
    for l in sp.split("\n"):
        s = l.strip()
        if not s:
            continue
        good = sum(ch.isupper() or ch == " " for ch in s)
        if good >= 0.9 * len(s) and len(s) > 8:
            keep.append(s)
    c["RG"] = ("EN", "\n".join(keep))
    return c


def build_lms():
    lms, sizes = {}, {}
    for k, (lang, txt) in load_corpora().items():
        r = D.text_to_runes(txt, lang)
        lms[k] = D.build_trigram(r)
        sizes[k] = len(r)
    return lms, sizes


# -------------------------------------------------------- periodic hill-climb

def hill_climb(lm, ct, L, restarts=3, sweeps=4):
    n = len(ct)
    idx = np.arange(n) % L
    best_key, best_s = None, -1e9
    for r in range(restarts):
        key = np.zeros(L, dtype=np.int64) if r == 0 else RNG.integers(0, D.N, L)
        cur = D.score_trigram(lm, (ct - key[idx]) % D.N)
        for _ in range(sweeps):
            improved = False
            for j in range(L):
                cand = np.tile(key, (D.N, 1))
                cand[:, j] = np.arange(D.N)
                dec = (ct[None, :] - cand[:, idx]) % D.N
                v = lm[dec[:, :-2], dec[:, 1:-1], dec[:, 2:]].mean(axis=1)
                b = int(np.argmax(v))
                if v[b] > cur + 1e-12:
                    cur = float(v[b])
                    key = cand[b].copy()
                    improved = True
            if not improved:
                break
        if cur > best_s:
            best_s, best_key = cur, key.copy()
    return best_s, best_key


def sweep(pages, lms):
    real = {}
    for lk, lm in lms.items():
        for L in range(1, MAXL + 1):
            bs, bp, bk = -1e9, None, None
            for pg, ct in pages:
                s, k = hill_climb(lm, ct, L)
                if s > bs:
                    bs, bp, bk = s, pg, k
            real["%s|L%d" % (lk, L)] = {"best": bs, "page": bp,
                                        "key": [int(v) for v in bk]}
    return real


def null_sweep(pages, lms, nrep=NREP):
    out = {}
    for rep in range(nrep):
        sh = [(pg, RNG.permutation(ct)) for pg, ct in pages]
        r = sweep(sh, lms)
        for k, v in r.items():
            out.setdefault(k, []).append(v["best"])
        print("  null rep %d done" % rep, flush=True)
    return out


# ----------------------------------------------------------- token searches

def _tokens():
    toks = []
    for cls, tl in D.TOKEN_CLASSES.items():
        for t in tl:
            r = D.text_to_runes(t, "EN")
            if len(r) >= 4:
                toks.append((cls, t, r))
    extra = ["DOTONION", "ONIONADDRESS", "HTTPWWW", "BEGINPGPPUBLICKEYBLOCK",
             "DEGREESNORTH", "DEGREESWEST", "COORDINATES", "LATITUDE",
             "LONGITUDE", "PASSWORD", "USERNAME", "DOWNLOAD", "INSTRUCTIONS"]
    for t in extra:
        r = D.text_to_runes(t, "EN")
        if len(r) >= 4:
            toks.append(("extra", t, r))
    return toks


def diff_pattern_hits(x, toks):
    dx = (x[1:] - x[:-1]) % D.N
    res = {}
    for cls, t, r in toks:
        pat = (r[1:] - r[:-1]) % D.N
        m = len(pat)
        if m < 3 or m > len(dx):
            continue
        c = 0
        for sign in (1, -1):
            p = (sign * pat) % D.N
            W = np.lib.stride_tricks.sliding_window_view(dx, m)
            c += int((W == p[None, :]).all(axis=1).sum())
        res[t] = c
    return res


def _eqpat(r):
    """canonical equality pattern of a token, e.g. ONION -> (0,1,2,0,1)."""
    seen, out = {}, []
    for v in r.tolist():
        if v not in seen:
            seen[v] = len(seen)
        out.append(seen[v])
    return np.array(out)


def eq_pattern_hits(x, toks):
    res = {}
    for cls, t, r in toks:
        pat = _eqpat(r)
        m = len(pat)
        if m < 4 or m > len(x):
            continue
        W = np.lib.stride_tricks.sliding_window_view(x, m)
        idxs = np.arange(len(W))
        cons = [(i, j, pat[i] == pat[j])
                for i in range(m) for j in range(i + 1, m)]
        # equality constraints first: they prune hardest
        cons.sort(key=lambda c: not c[2])
        for i, j, eq in cons:
            if len(idxs) == 0:
                break
            col_i = W[idxs, i]
            col_j = W[idxs, j]
            idxs = idxs[(col_i == col_j) if eq else (col_i != col_j)]
        res[t] = int(len(idxs))
    return res


def token_search(stream):
    toks = _tokens()
    real_d = diff_pattern_hits(stream, toks)
    real_dr = diff_pattern_hits(stream[::-1], toks)
    real_e = eq_pattern_hits(stream, toks)
    nd, ne = {}, {}
    for rep in range(200):
        s = RNG.permutation(stream)
        for k, v in diff_pattern_hits(s, toks).items():
            nd.setdefault(k, []).append(v)
        if rep < 40:
            for k, v in eq_pattern_hits(s, toks).items():
                ne.setdefault(k, []).append(v)
    out = {}
    for cls, t, r in toks:
        if t not in real_d:
            continue
        a = np.array(nd[t])
        e = np.array(ne.get(t, [0]))
        out[t] = {
            "class": cls, "len": int(len(r)),
            "diff_fwd": real_d[t], "diff_rev": real_dr.get(t, 0),
            "diff_null_mean": float(a.mean()), "diff_null_max": int(a.max()),
            "eq_real": real_e.get(t, 0),
            "eq_null_mean": float(e.mean()), "eq_null_max": int(e.max()),
            "HIT": bool(max(real_d[t], real_dr.get(t, 0)) > a.max())}
    return out


def main():
    pages, stream = D.load_unsolved()
    t0 = time.time()
    lms, sizes = build_lms()
    print("LM corpus sizes (runes):", sizes, "%.1fs" % (time.time() - t0), flush=True)
    # sanity: each LM must score its own language's held-out text best
    probe = {
        "EN": "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG AND THE WORD OF GOD",
        "LA": "ARMA VIRUMQUE CANO TROIAE QUI PRIMUS AB ORIS ITALIAM FATO PROFUGUS",
        "DE": "ICH BIN DER GEIST DER STETS VERNEINT UND DAS MIT RECHT DENN ALLES",
        "CY": "AC YNA Y DOETH Y BRENHIN AR Y MARCH GUYN AC Y DYUOT ATTAU",
        "OE": "HUAET UE GARDENA IN GEARDAGUM THEODCYNINGA THRYM GEFRUNON",
    }
    ident = {}
    for pk, txt in probe.items():
        r = D.text_to_runes(txt, pk)
        ident[pk] = {lk: round(D.score_trigram(lm, r), 4) for lk, lm in lms.items()}
    print("LM identification matrix:", json.dumps(ident, indent=1), flush=True)

    print("--- real language sweep ---", flush=True)
    real = sweep(pages, lms)
    print("--- null language sweep (%d reps) ---" % NREP, flush=True)
    null = null_sweep(pages, lms)
    lang = {}
    for k, v in real.items():
        a = np.array(null[k])
        z = (v["best"] - a.mean()) / a.std(ddof=1) if a.std(ddof=1) > 0 else 0.0
        lang[k] = {**v, "null_mean": float(a.mean()), "null_sd": float(a.std(ddof=1)),
                   "null_max": float(a.max()), "z": float(z),
                   "PASS": bool(z >= 4.0 and v["best"] > a.max())}

    print("--- token search ---", flush=True)
    tok = token_search(stream)

    json.dump({"lm_sizes": sizes, "lm_identification": ident,
               "language_sweep": lang, "token_search": tok},
              open(os.path.join(HERE, "lang_results.json"), "w"), indent=1)

    for k in sorted(lang, key=lambda k: -lang[k]["z"])[:15]:
        v = lang[k]
        print("%-8s best=%.4f null_mean=%.4f sd=%.4f nullmax=%.4f z=%+.2f %s" %
              (k, v["best"], v["null_mean"], v["null_sd"], v["null_max"], v["z"],
               "PASS" if v["PASS"] else ""))
    hits = {k: v for k, v in tok.items() if v["HIT"]}
    print("TOKEN HITS:", json.dumps(hits, indent=1))
    print("total time %.1fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
