#!/usr/bin/env python3
"""
i6 LATERAL-FIELD TRANSPLANT — linguistic typology via the CLEARTEXT length channel.

The 0-54 ciphertext keeps word '-', clause '.', line '/' boundaries. No additive
cipher hides WORD LENGTH (measured in runes). This tests, independent of breaking
any cipher, whether a natural-language plaintext even exists behind 0-54.

Runes are a 29-symbol futhorc where 7 runes are MULTI-LETTER (TH EO NG OE AE IA EA).
So genuine English encoded into futhorc has a DISTINCTIVE, COMPRESSED rune-word-length
distribution (a 4-letter English word can be 2-4 runes). A one-time-pad / random
filler at matched boundary density has a different, geometric-ish length profile.

Three hypotheses compared on rune-word-length distribution + length-bigram (Markov):
  (A) 0-54 ciphertext (the mystery)
  (B) genuine natural-language-in-futhorc  = solved LP1 English -> keyword_to_indices
  (C) random filler at matched boundary density (uniform runes, resampled word lens
      from a memoryless process) -- the OTP null

Pure Python, deterministic seed, honest signal-vs-null.
"""
import sys, os, re, random, math
from collections import Counter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "src")))
from lp.gematria import keyword_to_indices, RUNE_TO_IDX

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RUNESET = set(RUNE_TO_IDX)
BOUNDARY = set("-./\n\r&$§0123456789 \t")

random.seed(3301)

# ---------------------------------------------------------------------------
# (A) 0-54 ciphertext rune-word-lengths
# ---------------------------------------------------------------------------
def cipher_wordlens():
    data = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    pages = data.split("%")
    uns = pages[:55]          # segments 0..54 = unsolved LP2
    lens = []
    words_per_page = []
    for p in uns:
        s = p
        for b in BOUNDARY:
            s = s.replace(b, " ")
        ws = [w for w in s.split(" ") if w]
        pl = []
        for w in ws:
            rl = [c for c in w if c in RUNESET]
            if rl:
                pl.append(len(rl))
        lens += pl
        words_per_page.append(len(pl))
    return lens, uns, words_per_page

# ---------------------------------------------------------------------------
# (B) genuine natural-language-in-futhorc: solved LP1 English -> runes
# ---------------------------------------------------------------------------
# Clean English from the solved LP1 pages (WELCOME + koan + AN END + parable).
SOLVED_ENGLISH = """
WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS
IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE
ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE
YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY
ULTIMATELY YOU WILL DISCOVER AN END TO SELF
SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED
ALL THINGS SHOULD BE ENCRYPTED KNOW THIS
A KOAN DURING A LESSON THE MASTER EXPLAINED THE I
THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID
WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID
IT IS A VOICE INSIDE YOUR HEAD
I DO NOT HAVE A VOICE IN MY HEAD THOUGHT THE STUDENT
AND HE RAISED HIS HAND TO TELL THE MASTER
THE MASTER STOPPED THE STUDENT AND SAID
THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I
AND THE STUDENTS WERE ENLIGHTENED AN INSTRUCTION
QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH
IMPOSE NOTHING ON OTHERS KNOW THIS
AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO
IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE
PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE
WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE
"""

def english_futhorc_wordlens():
    lens = []
    seq = []      # concatenated rune-length sequence per line for bigram
    for line in SOLVED_ENGLISH.strip().split("\n"):
        for w in line.split():
            w = re.sub(r"[^A-Z]", "", w.upper())
            if not w:
                continue
            try:
                idx = keyword_to_indices(w)
            except ValueError:
                continue
            lens.append(len(idx))
    return lens

# ---------------------------------------------------------------------------
# (C) random-filler null at matched boundary density.
# Model: words are drawn from a MEMORYLESS process producing the same overall
# rune count and word count as the cipher (so mean length matches by construction);
# lengths ~ geometric-like from a random symbol stream with random break prob.
# We synthesize by laying down N random runes and inserting word breaks with prob p
# tuned to the observed mean word length. This is the OTP/filler hypothesis:
# boundaries are structural, symbols carry no length correlation.
# ---------------------------------------------------------------------------
def random_filler_wordlens(total_runes, total_words):
    # geometric break: mean word length = total_runes/total_words
    mean = total_runes / total_words
    p = 1.0 / mean          # break probability per position
    lens = []
    cur = 0
    produced = 0
    while len(lens) < total_words and produced < total_runes * 3:
        cur += 1
        produced += 1
        if random.random() < p and cur >= 1:
            lens.append(cur)
            cur = 0
    if cur:
        lens.append(cur)
    return lens[:total_words] if len(lens) >= total_words else lens

# ---------------------------------------------------------------------------
# stats helpers
# ---------------------------------------------------------------------------
def dist(lens, maxk=15):
    c = Counter(lens)
    n = len(lens)
    return [c.get(k, 0) / n for k in range(1, maxk + 1)]

def entropy(lens):
    c = Counter(lens); n = len(lens)
    return -sum((v/n) * math.log2(v/n) for v in c.values())

def ks_stat(a, b, maxk=20):
    # two-sample KS on discrete length dists
    ca = Counter(a); cb = Counter(b); na = len(a); nb = len(b)
    d = 0.0; cua = 0.0; cub = 0.0
    for k in range(1, maxk + 1):
        cua += ca.get(k, 0) / na
        cub += cb.get(k, 0) / nb
        d = max(d, abs(cua - cub))
    return d

def chi2_to(obs, ref, maxk=14):
    """chi-square of obs length dist against ref expected proportions."""
    co = Counter(obs); n = len(obs)
    cr = Counter(ref); nr = len(ref)
    chi = 0.0; dof = 0
    for k in range(1, maxk + 1):
        e = cr.get(k, 0) / nr * n
        o = co.get(k, 0)
        if e >= 5:
            chi += (o - e) ** 2 / e
            dof += 1
    return chi, dof - 1

def bigram_profile(lens):
    """Markov: P(next word length | current word length bucket). Return
    conditional mean of next-length given current-length bucket."""
    buckets = {}
    for a, b in zip(lens, lens[1:]):
        buckets.setdefault(a, []).append(b)
    return {k: sum(v)/len(v) for k, v in buckets.items() if len(v) >= 20}

def autocorr_lag1(lens):
    if len(lens) < 3: return 0.0
    m = sum(lens)/len(lens)
    num = sum((lens[i]-m)*(lens[i+1]-m) for i in range(len(lens)-1))
    den = sum((x-m)**2 for x in lens)
    return num/den if den else 0.0

# ---------------------------------------------------------------------------
def main():
    A, uns, wpp = cipher_wordlens()
    B = english_futhorc_wordlens()
    total_runes = sum(A)
    C = random_filler_wordlens(total_runes, len(A))

    out = []
    def pr(*a):
        s = " ".join(str(x) for x in a); print(s); out.append(s)

    pr("=== i6 word-length typology (cleartext length channel, pages 0-54) ===")
    pr(f"(A) cipher 0-54 : n={len(A)} words, total runes={sum(A)}, mean={sum(A)/len(A):.3f}, H={entropy(A):.3f} bits")
    pr(f"(B) English->futhorc : n={len(B)} words, mean={sum(B)/len(B):.3f}, H={entropy(B):.3f} bits")
    pr(f"(C) random filler    : n={len(C)} words, mean={sum(C)/len(C):.3f}, H={entropy(C):.3f} bits")
    pr("")

    pr("--- rune-word-length distribution (P for length 1..12) ---")
    dA, dB, dC = dist(A), dist(B), dist(C)
    pr("len  |  cipher   English   randfill")
    for k in range(12):
        pr(f" {k+1:2d}  |  {dA[k]:.4f}   {dB[k]:.4f}   {dC[k]:.4f}")
    pr("")

    pr("--- KS distance (smaller = more similar) ---")
    pr(f" cipher vs English  KS = {ks_stat(A,B):.4f}")
    pr(f" cipher vs randfill KS = {ks_stat(A,C):.4f}")
    pr(f" English vs randfill KS = {ks_stat(B,C):.4f}")
    pr("")

    pr("--- chi-square: cipher length dist AGAINST each hypothesis (lower = better fit) ---")
    chiE, dofE = chi2_to(A, B)
    chiC, dofC = chi2_to(A, C)
    pr(f" cipher fit to English  chi2={chiE:.1f} dof={dofE}  chi2/dof={chiE/max(dofE,1):.2f}")
    pr(f" cipher fit to randfill chi2={chiC:.1f} dof={dofC}  chi2/dof={chiC/max(dofC,1):.2f}")
    pr("")

    pr("--- length-bigram (Markov) profile: E[next len | current len] ---")
    bA, bB, bC = bigram_profile(A), bigram_profile(B), bigram_profile(C)
    pr(f" cipher   lag-1 autocorr = {autocorr_lag1(A):+.4f}")
    pr(f" English  lag-1 autocorr = {autocorr_lag1(B):+.4f}")
    pr(f" randfill lag-1 autocorr = {autocorr_lag1(C):+.4f}")
    pr(" cur | cipherE[next] EnglishE[next] randfillE[next]")
    for k in sorted(set(bA)|set(bB)|set(bC)):
        pr(f" {k:3d} | {bA.get(k,float('nan')):.3f}        {bB.get(k,float('nan')):.3f}         {bC.get(k,float('nan')):.3f}")
    pr("")

    # short-function-word signature: natural language has a spike at length 1-3
    # (THE, OF, TO, AND, A, I). futhorc-encoded: THE=2 runes, AND=3, OF=2, TO=2.
    pr("--- short-word mass (len<=3) : NL has heavy function-word mass ---")
    def sw(x): return sum(1 for v in x if v<=3)/len(x)
    pr(f" cipher   P(len<=3) = {sw(A):.4f}")
    pr(f" English  P(len<=3) = {sw(B):.4f}")
    pr(f" randfill P(len<=3) = {sw(C):.4f}")
    pr("")

    # verdict logic
    verdict = []
    if ks_stat(A,B) < ks_stat(A,C):
        verdict.append("length-DIST closer to English than to random filler")
    else:
        verdict.append("length-DIST closer to random filler than to English")
    if abs(autocorr_lag1(A)) < 0.03:
        verdict.append("negligible length autocorrelation (consistent with independent word lengths / filler)")
    else:
        verdict.append(f"nonzero length autocorrelation {autocorr_lag1(A):+.3f}")
    pr("=== VERDICT ===")
    for v in verdict:
        pr(" - " + v)

    open(os.path.join(HERE, "RESULTS.txt"), "w").write("\n".join(out) + "\n")

if __name__ == "__main__":
    main()
