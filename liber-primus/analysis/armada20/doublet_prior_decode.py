"""Task 15 - Doublet-deficit-as-prior constrained decode (OPEN-AVENUE #1).

Idea: the unsolved LP ciphertext has a ~5x doublet deficit (0.68% vs 3.45%
random). We use that as an EXPLICIT likelihood prior inside a beam/Viterbi
decode, combined with the KJV quadgram English model, over short-keyword and
short-running-key search spaces.

Two distinct, never-before-run experiments here:

 (A) DOUBLET-WEIGHTED KEY SEARCH (Vigenere, short periods).
     Score each candidate key = quadgram(plaintext) + lambda * doublet_prior,
     where doublet_prior rewards plaintexts whose induced doublet rate matches
     the English expectation (~2.97% gematria-mapped) instead of the suppressed
     ciphertext rate. A periodic Vigenere preserves the ciphertext doublet
     deficit in the plaintext (since adding a constant within a key-period chunk
     keeps equal->equal), so the prior should DOWN-weight any key whose
     plaintext inherits the anomalous 0.68% deficit. This is a fundamentally
     different objective than raw quadgram ranking.

 (B) DOUBLET-CONSTRAINED VITERBI keystream decode.
     Treat the keystream k_i as a hidden Markov chain (29 states). Emission =
     quadgram likelihood of the emitted plaintext char. Transition prior =
     penalize keystreams that would IMPLY a ciphertext doublet to have been
     produced, i.e. enforce the measured P(c_i=c_{i+1}). Run Viterbi to find the
     MAP keystream, then read off the plaintext. This is the literal
     "constrained Viterbi using doublet deficit as prior" from the open avenue.

Baseline to beat: best score on unsolved pages so far = -6.23 (score_norm).
Real English ~ -4.2..-5.0. Honest bar: a HIT needs score_norm < ~-5.0 AND
readable words.
"""
import sys, os, re, math, itertools, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from lp import gematria as gp, score as _score

N = gp.N
Q = _score.default()

RUNE_RE = re.compile(r"[ᚠ-ᛸ]")

def load_ciphertext():
    t = open(os.path.join(os.path.dirname(__file__), "..", "..",
                          "data", "krisyotam_runes.txt")).read()
    pages = t.split("%")
    out = []
    for i, p in enumerate(pages):
        idx = gp.runes_to_indices(p)
        if len(idx) >= 40:
            out.append((i, idx))
    return out

def doublet_rate(idxs):
    if len(idxs) < 2: return 0.0
    d = sum(1 for a, b in zip(idxs, idxs[1:]) if a == b)
    return d / (len(idxs) - 1)

ENGLISH_DOUBLET = 0.0297   # gematria-mapped KJV plaintext doublet rate
CIPHER_DOUBLET  = 0.0068   # observed ciphertext deficit
RANDOM_DOUBLET  = 1.0 / N  # 0.0345

def doublet_prior_score(plain_idx):
    """Log-prior favouring plaintexts whose doublet rate looks like ENGLISH
    rather than the suppressed ciphertext rate. Bernoulli log-likelihood of the
    observed doublet count under the English doublet rate, normalised per pair.
    A plaintext that keeps the 0.68% deficit gets a LOWER prior than one that
    restores the natural ~3% rate -> this is the discriminative signal."""
    n = len(plain_idx) - 1
    if n <= 0: return 0.0
    d = sum(1 for i in range(n) if plain_idx[i] == plain_idx[i + 1])
    pe = ENGLISH_DOUBLET
    # per-pair Bernoulli log-likelihood under English doublet model
    ll = (d * math.log(pe) + (n - d) * math.log(1 - pe)) / n
    return ll  # ~ around log(0.97) = -0.030 when rate matches English

# ----------------------------------------------------------------- experiment A
def vigenere_plain(idxs, key, sign=-1):
    L = len(key)
    return [(idxs[i] + sign * key[i % L]) % N for i in range(len(idxs))]

def search_A(pages, max_keylen=4, lam_grid=(0.0, 5.0, 20.0, 50.0), top=5):
    """Doublet-weighted short-Vigenere search per page, several lambda weights.
    For keylen<=2 we exhaustively try all 29^L keys (greedy column-wise for
    speed: each key column is independent under pure Vigenere quadgram? No -
    quadgrams couple columns, so we use a column-wise hill climb seeded by the
    doublet-aware unigram, then full quadgram refine)."""
    results = []
    for pageno, idxs in pages:
        # combine into a single string per page; quadgram needs latin
        best = None
        for L in range(1, max_keylen + 1):
            # too big to brute 29^L for L>2; use random restarts + hillclimb
            n_restarts = 30 if L <= 2 else 60
            import random
            rng = random.Random(1234 + pageno * 31 + L)
            for lam in lam_grid:
                for _ in range(n_restarts):
                    key = [rng.randrange(N) for _ in range(L)]
                    def obj(k):
                        p = vigenere_plain(idxs, k)
                        latin = gp.indices_to_translit(p)
                        return Q.score_norm(latin) + lam * doublet_prior_score(p)
                    cur = obj(key)
                    improved = True
                    while improved:
                        improved = False
                        for pos in range(L):
                            base = key[pos]
                            bestv, bestval = base, cur
                            for v in range(N):
                                if v == base: continue
                                key[pos] = v
                                val = obj(key)
                                if val > bestval:
                                    bestval, bestv = val, v
                            key[pos] = bestv
                            if bestval > cur:
                                cur = bestval; improved = True
                    p = vigenere_plain(idxs, key)
                    latin = gp.indices_to_translit(p)
                    qs = Q.score_norm(latin)
                    dr = doublet_rate(p)
                    cand = (qs, lam, L, list(key), dr, latin[:80])
                    if best is None or qs > best[0]:
                        best = cand
        results.append((pageno, best))
    return results

# ----------------------------------------------------------------- experiment B
def viterbi_decode(idxs, beam=200, lam=8.0):
    """Beam decode over hidden keystream states 0..28.
    Emission: quadgram extension log-prob of the plaintext char (approx via
    trigram->next using the quadgram table folded; here we score incrementally
    using the running last-3 plaintext chars).
    Doublet prior: an additive penalty when the chosen state implies the
    PLAINTEXT repeats the previous plaintext rune more often than English would,
    OR fails to (we reward matching English doublet odds). Implemented as a
    transition bonus log P_eng(doublet?) for each adjacent plaintext pair.

    plaintext char = (cipher - key) mod 29.  We let key be free per position
    (so this can model ANY keystream, including non-periodic / running key) but
    the quadgram emission + doublet prior jointly select it. This is the literal
    constrained-Viterbi from the open avenue; with a free key it is purely a
    test of whether the quadgram+doublet objective can carve English out of a
    flat-IoC text (it should FAIL on a true OTP, by construction - that's the
    honest control)."""
    # We work in latin-letter space is awkward (multi-char runes). Approximate
    # the quadgram emission by mapping each plaintext index to its translit and
    # scoring the concatenated string in a sliding window. For tractability we
    # score on the FIRST letter of each rune's translit (a coarse but consistent
    # English model) for the beam, then re-score full translit at the end.
    first = [gp.IDX_TO_TRANS[i][0] for i in range(N)]
    logpe_dbl = math.log(ENGLISH_DOUBLET)
    logpe_nod = math.log(1 - ENGLISH_DOUBLET)

    # beam state: (score, plain_indices tuple of last3, full_plain_list)
    States = [(0.0, "", [])]
    for pos, c in enumerate(idxs):
        nxt = []
        for sc, ctx, plain in States:
            for k in range(N):
                p = (c - k) % N
                ch = first[p]
                window = (ctx + ch)[-4:]
                if len(window) >= 4:
                    emis = Q.d.get(window, Q.floor)
                else:
                    emis = 0.0
                # doublet prior on plaintext
                if plain:
                    prior = logpe_dbl if plain[-1] == p else logpe_nod
                else:
                    prior = 0.0
                ns = sc + emis + lam * prior
                nxt.append((ns, (ctx + ch)[-3:], plain + [p]))
        nxt.sort(key=lambda x: -x[0])
        States = nxt[:beam]
    best = States[0]
    plain = best[2]
    latin = gp.indices_to_translit(plain)
    return Q.score_norm(latin), latin

if __name__ == "__main__":
    pages = load_ciphertext()
    print(f"loaded {len(pages)} unsolved pages")
    mode = sys.argv[1] if len(sys.argv) > 1 else "A"
    if mode == "A":
        res = search_A(pages, max_keylen=int(sys.argv[2]) if len(sys.argv)>2 else 3)
        out = []
        for pageno, best in res:
            qs, lam, L, key, dr, snip = best
            out.append({"page": pageno, "score_norm": qs, "lambda": lam,
                        "keylen": L, "key": key, "plain_doublet_rate": dr,
                        "snippet": snip})
            print(f"p{pageno:2d}  score={qs:.3f}  lam={lam}  L={L}  dbl={dr*100:.2f}%  {snip[:50]}")
        out.sort(key=lambda x: -x["score_norm"])
        json.dump(out, open(os.path.join(os.path.dirname(__file__),
                  "doublet_prior_A.json"), "w"), indent=2)
        print("\nBEST:", out[0]["score_norm"], "page", out[0]["page"])
    elif mode == "B":
        # run on a few pages only (expensive)
        lam = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
        beam = int(sys.argv[3]) if len(sys.argv) > 3 else 150
        out = []
        for pageno, idxs in pages[:5]:
            qs, latin = viterbi_decode(idxs[:300], beam=beam, lam=lam)
            print(f"p{pageno:2d}  viterbi score={qs:.3f}  lam={lam}  {latin[:60]}")
            out.append({"page": pageno, "score_norm": qs, "lambda": lam,
                        "snippet": latin[:80]})
        json.dump(out, open(os.path.join(os.path.dirname(__file__),
                  "doublet_prior_B.json"), "w"), indent=2)
