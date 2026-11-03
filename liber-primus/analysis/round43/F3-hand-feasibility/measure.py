"""R43 F3a — hand-feasibility lane: measure the unsolved pages from first principles.

Parses data/krisyotam_runes.txt (%, &, $ separators; - word sep; . sentence; / line end),
classifies pages solved/unsolved by actually decrypting with the demonstrated toolkit
(direct/atbash/shift, Vigenere DIVINITY & FIRFUMFERENFE w/ interrupter beam, phi(prime)),
then measures the unsolved block: IoC, doublet structure (within-word / cross-word /
cross-line), difference-stream IoCs (autokey tests), transition-matrix flatness,
lag coincidence spectrum, word-length distribution, F-rune behaviour, repeats.

Finally SIMULATES the mechanical options a hand scribe actually has and prints each
option's fingerprint next to the measured text.

Run: PYTHONUTF8=1 python analysis/round43/F3-hand-feasibility/measure.py
"""
import collections
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from lp import gematria as gp, ciphers, solve, stats, score as _score  # noqa

N = gp.N
RUNES_PATH = os.path.join(ROOT, "data", "krisyotam_runes.txt")
scorer = _score.default()


# ---------------------------------------------------------------- parse pages
def parse_pages(path=RUNES_PATH):
    """Returns list of pages; each page = dict(raw=str, idxs=list, tokens=word
    structure). '%' ends a page. '&'/'$' are section marks (kept as events)."""
    pages, cur = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s == "%":
                pages.append("\n".join(cur))
                cur = []
            elif s in ("&", "$", "§"):
                cur.append(s)
            else:
                cur.append(s)
    if cur:
        pages.append("\n".join(cur))
    out = []
    for raw in pages:
        idxs = gp.runes_to_indices(raw)
        out.append({"raw": raw, "idxs": idxs, "n": len(idxs)})
    return out


def words_of(raw):
    """Split a page's raw text into words (lists of indices). Separators: - . & $ newline
    is NOT a word break ('/' means the word continues on next line in the original;
    in this dump a line often ends mid-word with '/')."""
    # remove line-continuation: join lines, then split on - and . and marks
    joined = raw.replace("/", "").replace("\n", "")
    toks = []
    cur = []
    for ch in joined:
        if ch in gp.RUNE_TO_IDX:
            cur.append(gp.RUNE_TO_IDX[ch])
        else:
            if cur:
                toks.append(cur)
                cur = []
    if cur:
        toks.append(cur)
    return toks


def boundary_pairs(raw):
    """Classify every adjacent rune pair as within-word / cross-word / cross-line.
    Returns dict kind -> list of (a,b)."""
    kinds = {"word": [], "cross": [], "line": []}
    prev = None          # last rune index
    sep_seen = ""        # separators seen since last rune
    for ch in raw:
        if ch in gp.RUNE_TO_IDX:
            i = gp.RUNE_TO_IDX[ch]
            if prev is not None:
                if any(c in sep_seen for c in "-.&$"):
                    kinds["cross"].append((prev, i))
                elif "/" in sep_seen or "\n" in sep_seen:
                    kinds["line"].append((prev, i))  # line break mid-word
                else:
                    kinds["word"].append((prev, i))
            prev = i
            sep_seen = ""
        else:
            sep_seen += ch
    return kinds


# ---------------------------------------------------------------- classification
def vig_best(raw, key):
    """Try the keyword at every rotation, interrupter beam, sign=-1."""
    kidx = gp.keyword_to_indices(key)
    nr = len(gp.runes_to_indices(raw))
    best = None
    for rot in range(len(kidx)):
        k = kidx[rot:] + kidx[:rot]
        stream = ciphers.repeat_key(k, nr)
        res = solve.find_interrupters(raw, stream, sign=-1, beam_width=120, scorer=scorer)
        if best is None or res["score_norm"] > best[0]:
            best = (res["score_norm"], f"vig:{key}@rot{rot}", res)
    return best


def phi_prime_stream(length, start=0):
    primes = []
    p = 2
    while len(primes) < length + start:
        if all(p % q for q in primes if q * q <= p):
            primes.append(p)
        p += 1
    return [(primes[i + start] - 1) % N for i in range(length)]


def classify(pages):
    """Return per-page best decode + verdict."""
    results = []
    prime_cursor = 0  # running offset for phi(prime) continuation across pages
    for pi, pg in enumerate(pages):
        idxs, raw = pg["idxs"], pg["raw"]
        if not idxs:
            results.append({"page": pi, "n": 0, "verdict": "empty"})
            continue
        cands = []
        # simple family
        for atb in (False, True):
            base = [(N - 1) - c for c in idxs] if atb else idxs
            for k in range(N):
                for sign in (-1, +1):
                    out = [(c + sign * k) % N for c in base]
                    txt = gp.indices_to_translit(out)
                    cands.append((scorer.score_norm(txt),
                                  f"{'atbash+' if atb else ''}shift{sign*k:+d}", txt))
        cands.sort(reverse=True)
        best = cands[0]
        # vigenere known keys (only if simple failed; beam is the expensive part)
        if best[0] < -3.0:
            for key in ("DIVINITY", "FIRFUMFERENFE"):
                sc, lbl, res = vig_best(raw, key)
                if sc > best[0]:
                    best = (sc, lbl, res["plaintext"])
        # phi(prime), offsets 0 and the running cursor
        if best[0] < -3.0:
            nr = len(idxs)
            for start in {0, prime_cursor}:
                stream = phi_prime_stream(nr, start)
                res = solve.find_interrupters(raw, stream, sign=-1, beam_width=120,
                                              scorer=scorer)
                if res["score_norm"] > best[0]:
                    best = (res["score_norm"], f"phi(prime)@{start}", res["plaintext"])
                    enc = nr - res["n_interrupters"]
                    prime_cursor = start + enc
        verdict = "solved" if best[0] > -3.1 else "unsolved"
        results.append({"page": pi, "n": pg["n"], "ioc": round(stats.ioc_norm(idxs), 3),
                        "dbl_pct": round(100 * stats.doublet_rate(idxs), 3),
                        "best": round(best[0], 3), "method": best[1],
                        "verdict": verdict, "peek": str(best[2])[:60]})
    return results


# ---------------------------------------------------------------- deep measures
def diff_ioc(idxs, lag, sign=-1):
    """IoC of the stream (c_i + sign*c_{i-lag}) mod N. sign=-1 difference, +1 sum."""
    s = [(idxs[i] + sign * idxs[i - lag]) % N for i in range(lag, len(idxs))]
    return stats.ioc_norm(s)


def lag_coincidence(idxs, maxlag=60):
    out = {}
    for L in range(1, maxlag + 1):
        m = sum(1 for i in range(L, len(idxs)) if idxs[i] == idxs[i - L])
        out[L] = m / (len(idxs) - L)
    return out


def transition_offdiag_flatness(pairs):
    """For pairs (a,b): chi2 of the aggregated distribution of (b-a) mod 29 vs
    uniform, and chi2 excluding 0 (the doublet cell)."""
    diffs = collections.Counter((b - a) % N for a, b in pairs)
    n = len(pairs)
    exp = n / N
    chi_all = sum((diffs.get(d, 0) - exp) ** 2 / exp for d in range(N))
    n_off = n - diffs.get(0, 0)
    exp_off = n_off / (N - 1)
    chi_off = sum((diffs.get(d, 0) - exp_off) ** 2 / exp_off for d in range(1, N))
    return diffs, chi_all, chi_off


def repeats(idxs, L):
    seen, reps = {}, []
    for i in range(len(idxs) - L + 1):
        g = tuple(idxs[i:i + L])
        if g in seen:
            reps.append((g, seen[g], i))
        else:
            seen[g] = i
    return reps


def longest_repeat(idxs):
    best = 0
    L = 4
    while True:
        if not repeats(idxs, L):
            return L - 1
        best = L
        L += 1
        if L > 200:
            return best


def doublet_z(idxs):
    """Observed doublets vs expectation under independence with observed unigram freqs."""
    n = len(idxs)
    counts = collections.Counter(idxs)
    p_same = sum((c / n) ** 2 for c in counts.values())
    exp = p_same * (n - 1)
    obs = stats.doublet_count(idxs)
    sd = math.sqrt((n - 1) * p_same * (1 - p_same))
    return obs, exp, (obs - exp) / sd if sd else 0.0


# ---------------------------------------------------------------- simulations
def load_english_rune_plaintext(nrunes=12000):
    """Tokenize KJV into gematria indices (greedy multi-letter), keep word breaks."""
    path = os.path.join(ROOT, "data", "kjv.txt")
    import re
    txt = open(path, encoding="utf-8", errors="ignore").read()[100000:400000].upper()
    words = re.findall(r"[A-Z]+", txt)
    out_words = []
    total = 0
    for w in words:
        try:
            ix = gp.keyword_to_indices(w)
        except ValueError:
            continue
        out_words.append(ix)
        total += len(ix)
        if total >= nrunes:
            break
    return out_words


def flat_pairs(words):
    """Adjacent pairs within+across words (page-level glyph stream)."""
    flat = [i for w in words for i in w]
    return flat


def rng_pad(n, seed=7):
    rnd = random.Random(seed)
    return [rnd.randrange(N) for _ in range(n)]


def sim_fingerprint(name, cidx, extra=""):
    ioc = stats.ioc_norm(cidx)
    dbl = 100 * stats.doublet_rate(cidx)
    d1 = diff_ioc(cidx, 1, -1)
    s1 = diff_ioc(cidx, 1, +1)
    lag2 = sum(1 for i in range(2, len(cidx)) if cidx[i] == cidx[i - 2]) / (len(cidx) - 2)
    return {"sim": name, "n": len(cidx), "ioc": round(ioc, 3), "dbl_pct": round(dbl, 3),
            "diffIoC": round(d1, 3), "sumIoC": round(s1, 3),
            "lag2_pct": round(100 * lag2, 3), "note": extra}


def run_sims(plain_flat):
    sims = []
    n = len(plain_flat)
    pad = rng_pad(n)

    # 0. plain English runes (reference)
    sims.append(sim_fingerprint("english plaintext (ref)", plain_flat))

    # 1. true random pad (printed pad, no avoidance)
    c = [(p + k) % N for p, k in zip(plain_flat, pad)]
    sims.append(sim_fingerprint("random pad, no avoidance", c))

    # 2. pad + RE-DRAW (nudge +1 until != prev)  [scribe fixes doublet by altering output]
    c, prev = [], None
    for p, k in zip(plain_flat, pad):
        o = (p + k) % N
        while o == prev:
            o = (o + 1) % N
        c.append(o)
        prev = o
    sims.append(sim_fingerprint("pad + re-draw(+1) on doublet", c,
                                "excess at diff +1"))

    # 3. pad + SKIP-ON-REPEAT (advance pad one extra step when doublet would occur)
    c, prev, j = [], None, 0
    pad2 = rng_pad(2 * n, seed=11)
    for p in plain_flat:
        o = (p + pad2[j]) % N
        while o == prev:
            j += 1
            o = (p + pad2[j]) % N
        c.append(o)
        prev = o
        j += 1
    sims.append(sim_fingerprint("pad + skip-key on doublet", c))

    # 4. ciphertext autokey (c_i = p_i + c_{i-1})
    c, prev = [], 0
    for p in plain_flat:
        o = (p + prev) % N
        c.append(o)
        prev = o
    sims.append(sim_fingerprint("ciphertext autokey (+)", c,
                                "diffIoC = plaintext IoC"))

    # 5. plaintext autokey (c_i = p_i + p_{i-1})
    c, prev = [], 0
    for p in plain_flat:
        c.append((p + prev) % N)
        prev = p
    sims.append(sim_fingerprint("plaintext autokey (+)", c))

    # 6. two-stream choice: two pads; pick the one avoiding a doublet (pad1 default)
    p1, p2 = rng_pad(n, 3), rng_pad(n, 4)
    c, prev = [], None
    forced = 0
    for i, p in enumerate(plain_flat):
        o1, o2 = (p + p1[i]) % N, (p + p2[i]) % N
        o = o1 if o1 != prev else o2
        if o == prev:
            forced += 1
        c.append(o)
        prev = o
    sims.append(sim_fingerprint("two-stream choose-non-doublet", c,
                                f"forced doublets={forced}"))

    # 7. Vigenere short key + skip-on-repeat (tableau row-switch feel)
    key = gp.keyword_to_indices("FIRFUMFERENFE")
    c, prev, j = [], None, 0
    for p in plain_flat:
        o = (p + key[j % len(key)]) % N
        while o == prev:
            j += 1
            o = (p + key[j % len(key)]) % N
        c.append(o)
        prev = o
        j += 1
    sims.append(sim_fingerprint("vigenere13 + skip-key on doublet", c,
                                "period survives at lag 13?"))

    # 8. ciphertext autokey, subtractive (c_i = p_i - c_{i-1})
    c, prev = [], 0
    for p in plain_flat:
        o = (p - prev) % N
        c.append(o)
        prev = o
    sims.append(sim_fingerprint("ciphertext autokey (-)", c,
                                "sumIoC = plaintext IoC"))
    return sims, key


# ---------------------------------------------------------------- main
def main():
    pages = parse_pages()
    total = sum(p["n"] for p in pages)
    print(f"pages={len(pages)}  total runes={total}\n")

    print("== per-page classification ==")
    res = classify(pages)
    for r in res:
        if r.get("verdict") == "empty":
            print(f"p{r['page']:02d}  EMPTY")
            continue
        print(f"p{r['page']:02d} n={r['n']:4d} ioc={r['ioc']:5.3f} dbl={r['dbl_pct']:5.2f}% "
              f"best={r['best']:6.2f} {r['verdict']:8s} {r['method'][:28]:28s} {r['peek'][:48]}")

    solved = [r["page"] for r in res if r.get("verdict") == "solved"]
    unsolved = [r["page"] for r in res if r.get("verdict") == "unsolved"]
    print(f"\nsolved pages: {solved}")
    print(f"unsolved pages: {unsolved}")

    # ---- unsolved aggregate
    U_raw = "\n%\n".join(pages[i]["raw"] for i in unsolved)
    U = [i for p in unsolved for i in pages[p]["idxs"]]
    print(f"\n== UNSOLVED aggregate: n={len(U)} ==")
    print("summary:", stats.summary(U))
    obs, exp, z = doublet_z(U)
    print(f"doublets: obs={obs} exp={exp:.1f} z={z:+.1f}")

    # per-page IoC distribution of unsolved
    iocs = [stats.ioc_norm(pages[i]["idxs"]) for i in unsolved]
    print(f"unsolved per-page IoC: min={min(iocs):.3f} max={max(iocs):.3f} "
          f"mean={sum(iocs)/len(iocs):.3f}")

    # unigram flatness
    print(f"chi2 uniform (df=28): {stats.chi2_uniform(U):.1f}")
    cnt = collections.Counter(U)
    fr = sorted(((cnt.get(i, 0), gp.IDX_TO_TRANS[i]) for i in range(N)), reverse=True)
    print("unigram top/bottom:", fr[:4], fr[-4:])
    f_rate = cnt.get(0, 0) / len(U)
    print(f"F-rune rate unsolved: {100*f_rate:.2f}%  (uniform=3.45%)")

    # boundary-classified doublets
    kinds = boundary_pairs(U_raw)
    print("\n== doublets by boundary type (unsolved) ==")
    for k, prs in kinds.items():
        if not prs:
            continue
        d = sum(1 for a, b in prs if a == b)
        print(f"{k:6s} pairs={len(prs):5d} doublets={d:3d} rate={100*d/len(prs):5.3f}% "
              f"(uniform exp {len(prs)/N:.1f})")

    # transition flatness
    allpairs = kinds["word"] + kinds["cross"] + kinds["line"]
    diffs, chi_all, chi_off = transition_offdiag_flatness(allpairs)
    print(f"\ndiff-distribution chi2 all cells (df=28): {chi_all:.1f}")
    print(f"diff-distribution chi2 excl 0  (df=27): {chi_off:.1f}")
    print("diff counts around 0:",
          {d: diffs.get(d % N, 0) for d in (-2, -1, 0, 1, 2)})

    # difference/sum IoC (autokey family tests) + with atbash variant
    print("\n== autokey-family tests on unsolved ==")
    for lag in (1, 2, 3):
        print(f"lag{lag}: diffIoC={diff_ioc(U, lag, -1):.3f} sumIoC={diff_ioc(U, lag, +1):.3f}")

    # lag coincidence spectrum (periodicity)
    lc = lag_coincidence(U, 60)
    hot = sorted(lc.items(), key=lambda kv: -kv[1])[:6]
    print("lag-coincidence top:", [(L, round(100 * v, 2)) for L, v in hot],
          " uniform=3.45%")

    # word structure
    W = [w for i in unsolved for w in words_of(pages[i]["raw"])]
    wl = collections.Counter(len(w) for w in W)
    mean_wl = sum(len(w) for w in W) / len(W)
    print(f"\nunsolved words={len(W)} mean_len={mean_wl:.2f} dist={dict(sorted(wl.items())[:12])}")
    # word-position IoC (does key reset per word?)
    for pos in range(4):
        col = [w[pos] for w in W if len(w) > pos]
        print(f"IoC at word-position {pos}: {stats.ioc_norm(col):.3f} (n={len(col)})")
    # first-rune-of-word uniformity
    first = [w[0] for w in W]
    print(f"first-rune chi2 vs uniform: {stats.chi2_uniform(first):.1f} (df=28)")

    # solved-plain reference word lengths
    plain_pages = [r["page"] for r in res
                   if r.get("verdict") == "solved" and "shift+0" in r.get("method", "")]
    PW = [w for i in plain_pages for w in words_of(pages[i]["raw"])]
    if PW:
        mean_pwl = sum(len(w) for w in PW) / len(PW)
        print(f"solved-plain words={len(PW)} mean_len={mean_pwl:.2f}")

    # repeats
    print("\n== repeat structure (unsolved) ==")
    for L in (3, 4, 5):
        reps = repeats(U, L)
        e = (len(U) ** 2 / 2) / (N ** L)
        print(f"repeated {L}-grams: {len(reps)} (poisson exp ~{e:.1f})")
    lr = longest_repeat(U)
    print(f"longest repeated n-gram: {lr}")
    for g, i, j in repeats(U, lr):
        print(f"  len{lr} at {i} and {j} gap={j-i}: {gp.indices_to_translit(list(g))}")

    # doublet contexts: where do residual doublets sit relative to line breaks?
    print("\n== residual doublet contexts ==")
    # walk raw with line info
    prev, prev_line = None, 0
    line_no = 0
    dbl_line_break = 0
    dbl_total = 0
    for ch in U_raw:
        if ch == "/" or ch == "\n":
            line_no += 1 if ch == "/" else 0
            continue
        if ch in gp.RUNE_TO_IDX:
            i = gp.RUNE_TO_IDX[ch]
            if prev is not None and i == prev:
                dbl_total += 1
                if line_no != prev_line:
                    dbl_line_break += 1
            prev, prev_line = i, line_no
    print(f"doublets total={dbl_total}, of which at a line break={dbl_line_break}")

    # F-rune positional behaviour in unsolved (interrupter convention reuse?)
    f_per_page = [(i, pages[i]["idxs"].count(0), pages[i]["n"]) for i in unsolved]
    rates = [c / n for _, c, n in f_per_page if n]
    print(f"\nF-rate per unsolved page: min={100*min(rates):.2f}% max={100*max(rates):.2f}% "
          f"mean={100*sum(rates)/len(rates):.2f}%")

    # solved vigenere ciphertext reference stats
    print("\n== solved-page ciphertext reference ==")
    for r in res:
        if r.get("verdict") == "solved":
            i = r["page"]
            idxs = pages[i]["idxs"]
            print(f"p{i:02d} {r['method'][:24]:24s} ioc={stats.ioc_norm(idxs):5.3f} "
                  f"dbl={100*stats.doublet_rate(idxs):5.2f}%")

    # ---- simulations
    print("\n== MECHANICAL-OPTION SIMULATIONS (English-rune plaintext, n~12000) ==")
    words = load_english_rune_plaintext()
    flat = flat_pairs(words)
    print(sim_fingerprint("english-rune plaintext", flat))
    sims, _ = run_sims(flat)
    for s in sims:
        print(s)

    # measured row for comparison
    print("\nMEASURED unsolved:", sim_fingerprint("MEASURED unsolved", U))

    # persist
    out = {
        "total_runes": total, "solved_pages": solved, "unsolved_pages": unsolved,
        "unsolved_summary": stats.summary(U),
        "doublet_obs_exp_z": [obs, exp, z],
        "per_page": res,
        "sims": sims,
        "measured_fingerprint": sim_fingerprint("MEASURED unsolved", U),
    }
    with open(os.path.join(HERE, "measurements.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    print("\nwrote measurements.json")


if __name__ == "__main__":
    main()
