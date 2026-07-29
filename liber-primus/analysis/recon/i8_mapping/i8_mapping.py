"""i8 DEVIL'S-ADVOCATE BELIEVER — GLYPH->INDEX MAPPING ATTACK (premise b).

Question: is the 0-54 rune stream being read in the WRONG alphabet? If the raw
glyphs are actually plaintext under a permuted symbol->index assignment (a
monoalphabetic relabeling of the true Gematria Primus), then NO decryption is
needed — only re-labeling. A monoalphabetic substitution PRESERVES bigram
structure up to relabeling, so there would EXIST a permutation pi of the 29
symbols that lifts an English-bigram score from the random floor into the
English band. This lane searches for that pi WITHOUT any decryption.

Instruments (both plaintext-blind wrt the ciphertext; NO language model of the
ciphertext, only English-in-runes statistics as the fixed reference):
  P  = oracle-style binary bigram plausibility: fraction of adjacent index
       pairs that occur in a LEGAL English-in-GP-index bigram set. Correct
       English ~0.4+; random floor ~0.09  (matches validated i7 oracle scale).
  F  = log-bigram fitness (standard monoalphabetic cryptanalysis score): mean
       log P_english(a,b) over adjacent pairs. Higher = more English-like.

Reference English-in-GP-index bigram stats are learned from large plaintext
English corpora mapped letter->rune-index (multi-letter runes greedy), NOT from
the ciphertext. A random-permutation control establishes the null band; a real
mapping hit must beat that null DECISIVELY.
"""
import os, sys, math, random, json, itertools
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp

N = gp.N
DATA = os.path.join(ROOT, "data")
KRIS = os.path.join(DATA, "krisyotam_runes.txt")

# ------------------------------------------------------------ raw 0-54 stream
def load_pages_raw():
    segs = open(KRIS, encoding="utf-8").read().split("%")
    return [s for s in segs if gp.runes_to_indices(s)]

PAGES_RAW = load_pages_raw()
PAGES_IDX = [gp.runes_to_indices(s) for s in PAGES_RAW]
UNSOLVED = [i for p in PAGES_IDX[:55] for i in p]     # pages 0-54 as GP indices
print(f"raw 0-54 runes = {len(UNSOLVED)}  distinct symbols = {len(set(UNSOLVED))}")

# ---------------------------------------------- English-in-GP-index reference
def english_to_gp_indices(text):
    """Map raw English text -> GP index stream, greedy multi-letter runes.
    Keeps only letters; word breaks flush (no cross-word bigrams)."""
    out = []
    word = []
    def flush():
        if not word:
            return
        s = "".join(word).upper()
        i = 0
        run = []
        while i < len(s):
            for t, idx in gp._TRANS_SORTED:
                if s.startswith(t, i):
                    run.append(idx); i += len(t); break
            else:
                alias = {"V":1,"K":5,"Z":15,"Q":5,"X":14}.get(s[i])
                if alias is None:
                    i += 1; continue
                run.append(alias); i += 1
        out.append(run)
        word.clear()
    for ch in text:
        if ch.isalpha():
            word.append(ch)
        else:
            flush()
    flush()
    return out  # list of per-word index runs

# Build English bigram counts (within-word only, matches how runes segment)
CORP_FILES = ["pride.txt", "kjv.txt", "war.txt", "moby.txt"]
big = [[0]*N for _ in range(N)]
uni = [0]*N
tot_pairs = 0
for fn in CORP_FILES:
    p = os.path.join(DATA, fn)
    if not os.path.exists(p):
        continue
    txt = open(p, encoding="utf-8", errors="ignore").read()
    for run in english_to_gp_indices(txt):
        for a in run:
            uni[a] += 1
        for a, b in zip(run, run[1:]):
            big[a][b] += 1
            tot_pairs += 1
print(f"english reference pairs = {tot_pairs}")

# LEGAL set: bigrams that appear with decent frequency in English (robust,
# not the tiny 77-pair PARABLE set). Threshold = pairs seen often enough to be
# structural, tuned so |LEGAL| ~ realistic English coverage.
THRESH = max(1, tot_pairs // 20000)   # frequency floor
LEGAL = {(a, b) for a in range(N) for b in range(N) if big[a][b] >= THRESH}
print(f"LEGAL bigrams = {len(LEGAL)} (thresh {THRESH})")

# log-fitness table with add-one smoothing
FLOOR = math.log(1.0 / (tot_pairs + N*N))
LOGP = [[0.0]*N for _ in range(N)]
for a in range(N):
    row_tot = sum(big[a]) + N
    for b in range(N):
        LOGP[a][b] = math.log((big[a][b] + 1) / row_tot)

# ------------------------------------------------------------------ scorers
def P_score(seq):
    if len(seq) < 2: return float("nan")
    hit = sum(1 for a, b in zip(seq, seq[1:]) if (a, b) in LEGAL)
    return hit / (len(seq) - 1)

def F_score(seq):
    if len(seq) < 2: return float("nan")
    return sum(LOGP[a][b] for a, b in zip(seq, seq[1:])) / (len(seq) - 1)

def remap(seq, perm):
    """perm[symbol] = new index. Read raw glyphs under a new alphabet order."""
    return [perm[c] for c in seq]

# ---------------------------------------------------------- candidate orders
# A "candidate order" is a permutation perm where perm[old_gp_index] = new_index.
IDENT = list(range(N))

# canonical Anglo-Saxon futhorc order (the historical rune row). GP is already a
# futhorc subset in the traditional order, so this equals identity — but build it
# explicitly from rune list to be honest.
FUTHORC = IDENT[:]  # GP table IS the futhorc order

# prime-VALUE order: sort symbols by their prime, assign new index by rank
prime_rank = sorted(range(N), key=lambda i: gp.PRIMES[i])   # already ascending
PRIME_ORDER = [0]*N
for newidx, old in enumerate(prime_rank):
    PRIME_ORDER[old] = newidx   # == identity since primes already ascending

REVERSE = [(N-1)-i for i in range(N)]
ATBASH = REVERSE[:]  # same as reverse for index reflection

# frequency-matched: sort raw-stream symbols by descending freq, map to the
# English index freq rank (most common raw symbol -> most common English rune).
from collections import Counter
raw_freq = Counter(UNSOLVED)
raw_by_freq = [s for s, _ in raw_freq.most_common()]      # raw symbols, desc freq
for s in range(N):
    if s not in raw_freq:
        raw_by_freq.append(s)
eng_by_freq = sorted(range(N), key=lambda i: -uni[i])     # english idx, desc freq
FREQ_MATCH = [0]*N
for rank, raw_sym in enumerate(raw_by_freq):
    FREQ_MATCH[raw_sym] = eng_by_freq[rank]

CANDIDATES = {
    "standard GP (identity)": IDENT,
    "futhorc canonical":      FUTHORC,
    "prime-value order":      PRIME_ORDER,
    "reverse":                REVERSE,
    "atbash reflect":         ATBASH,
    "freq-match to English":  FREQ_MATCH,
}

# ------------------------------------------------------ hill-climb (the real b-test)
# Best-case for premise b: search the FULL permutation space for the pi that
# maximizes English bigram fitness of the remapped raw stream. If the stream is
# English-under-a-permutation, this MUST find it (monosub bigram climb is the
# textbook solver). Multi-restart to avoid local optima.
def climb(seq, restarts=40, seed=0):
    rng = random.Random(seed)
    best_perm, best_f = None, -1e18
    for r in range(restarts):
        perm = list(range(N)); rng.shuffle(perm)
        cur = F_score(remap(seq, perm))
        improved = True
        while improved:
            improved = False
            for i in range(N):
                for j in range(i+1, N):
                    perm[i], perm[j] = perm[j], perm[i]
                    f = F_score(remap(seq, perm))
                    if f > cur + 1e-12:
                        cur = f; improved = True
                    else:
                        perm[i], perm[j] = perm[j], perm[i]
        if cur > best_f:
            best_f, best_perm = cur, perm[:]
    return best_perm, best_f

# ----------------------------------------------------------- control: random perms
def random_perm_null(seq, n=500, seed=3301):
    rng = random.Random(seed)
    Ps, Fs = [], []
    for _ in range(n):
        perm = list(range(N)); rng.shuffle(perm)
        r = remap(seq, perm)
        Ps.append(P_score(r)); Fs.append(F_score(r))
    return Ps, Fs

def pct(val, dist):
    return 100.0 * sum(1 for x in dist if x <= val) / len(dist)

# =================================================================== RUN
if __name__ == "__main__":
    report = {}

    # anchors on the scorers themselves (sanity of instrument scale)
    eng_stream = [i for run in english_to_gp_indices(
        open(os.path.join(DATA,"pride.txt"),encoding="utf-8",errors="ignore").read()[:60000])
        for i in run]
    print("\n=== INSTRUMENT ANCHORS ===")
    print(f"  English-in-GP (pride)  P={P_score(eng_stream):.3f}  F={F_score(eng_stream):.3f}")
    print(f"  raw 0-54 (identity)    P={P_score(UNSOLVED):.3f}  F={F_score(UNSOLVED):.3f}")
    rng = random.Random(7)
    rnd = [rng.randrange(N) for _ in range(len(UNSOLVED))]
    print(f"  random stream          P={P_score(rnd):.3f}  F={F_score(rnd):.3f}")
    report["anchors"] = {
        "english_P": P_score(eng_stream), "english_F": F_score(eng_stream),
        "raw_identity_P": P_score(UNSOLVED), "raw_identity_F": F_score(UNSOLVED),
        "random_P": P_score(rnd), "random_F": F_score(rnd),
    }

    # control null
    print("\n=== RANDOM-PERMUTATION CONTROL (null band) ===")
    Ps, Fs = random_perm_null(UNSOLVED, n=500)
    Ps.sort(); Fs.sort()
    def q(d,f): return d[int(f*(len(d)-1))]
    print(f"  P null: min={Ps[0]:.3f} med={q(Ps,.5):.3f} p95={q(Ps,.95):.3f} p99={q(Ps,.99):.3f} max={Ps[-1]:.3f}")
    print(f"  F null: min={Fs[0]:.3f} med={q(Fs,.5):.3f} p95={q(Fs,.95):.3f} p99={q(Fs,.99):.3f} max={Fs[-1]:.3f}")
    report["null"] = {"P_p95": q(Ps,.95), "P_p99": q(Ps,.99), "P_max": Ps[-1],
                      "F_p95": q(Fs,.95), "F_p99": q(Fs,.99), "F_max": Fs[-1]}

    print("\n=== CANDIDATE ORDERINGS (no decryption) ===")
    cand_report = {}
    for name, perm in CANDIDATES.items():
        r = remap(UNSOLVED, perm)
        p, f = P_score(r), F_score(r)
        cand_report[name] = {"P": p, "F": f, "P_pct": pct(p, Ps), "F_pct": pct(f, Fs)}
        print(f"  {name:24s} P={p:.3f} (pctl {pct(p,Ps):5.1f})  F={f:.3f} (pctl {pct(f,Fs):5.1f})")
    report["candidates"] = cand_report

    print("\n=== FULL MONOALPHABETIC HILL-CLIMB (best-case premise-b test) ===")
    bp, bf = climb(UNSOLVED, restarts=40, seed=11)
    br = remap(UNSOLVED, bp)
    bpP = P_score(br)
    print(f"  best hill-climb  F={bf:.3f} (pctl {pct(bf,Fs):5.1f})  P={bpP:.3f} (pctl {pct(bpP,Ps):5.1f})")
    print(f"  best perm decodes first 80 remapped runes as:")
    print("    " + gp.indices_to_translit(br[:80]))
    report["hillclimb"] = {"F": bf, "F_pct": pct(bf, Fs), "P": bpP, "P_pct": pct(bpP, Ps),
                           "perm": bp, "sample_translit": gp.indices_to_translit(br[:120])}

    # CONTROL for the hill-climb: climb a RANDOM stream the same way. If the climb
    # can push random noise to a similar F, then a high climb-F on the raw stream
    # is NOT evidence of hidden English.
    print("\n=== HILL-CLIMB CONTROL (climb on random noise) ===")
    cbp, cbf = climb(rnd, restarts=40, seed=11)
    cbr = remap(rnd, cbp)
    print(f"  best climb on RANDOM  F={cbf:.3f}  P={P_score(cbr):.3f}")
    report["hillclimb_control_random"] = {"F": cbf, "P": P_score(cbr)}

    # verdict
    hit = (bf > q(Fs,.99)) and (bf > cbf + 0.10) and (bpP > q(Ps,.99))
    print(f"\n  ==> hill-climb beats F-p99 AND random-noise-climb AND P-p99: {hit}")
    report["structural_signal"] = bool(hit)

    json.dump(report, open(os.path.join(HERE, "i8_results.json"), "w"), indent=2)
    print("\nwrote i8_results.json")
