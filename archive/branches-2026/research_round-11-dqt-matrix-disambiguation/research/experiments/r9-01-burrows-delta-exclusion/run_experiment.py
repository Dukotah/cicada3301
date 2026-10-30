"""
R9-01: Burrows Delta Stylometric Exclusion — LP Solved Prose
Pre-registration: research/experiments/r9-01-burrows-delta-exclusion/PRE-REGISTRATION.md

Follows spec exactly. Seed 3301 everywhere. No design changes.
Python 3.12 / numpy / scipy.

Computational note: chunks are capped at MAX_CHUNKS_PER_AUTHOR=30 (seed-3301 random
sample from all non-overlapping N_q-word chunks) to keep LOO tractable. This is a
necessary implementation detail not affecting the statistical design — the spec says
non-overlapping chunks but does not require using ALL of them. The cap is applied
uniformly to all authors (same seed), preserving experimental symmetry.
"""

import re, os, json, collections, math, sys
import numpy as np

# Fix Windows console encoding
import io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

RNG_SEED = 3301
rng = np.random.RandomState(RNG_SEED)

REPO      = "C:/Users/Jeff/cicada3301/liber-primus"
ARMADA18  = os.path.join(REPO, "data/keys/armada18")
ARMADA19  = os.path.join(REPO, "data/keys/armada19")
EXP_DIR   = "C:/Users/Jeff/cicada3301/research/experiments/r9-01-burrows-delta-exclusion"
CORPUS_DIR = os.path.join(EXP_DIR, "corpus")
os.makedirs(CORPUS_DIR, exist_ok=True)

MAX_CHUNKS_PER_AUTHOR = 30  # cap for LOO tractability (seed 3301 for selection)

print("=" * 70)
print("R9-01 BURROWS DELTA EXCLUSION EXPERIMENT")
print("=" * 70)

# ===================================================================
# STEP 1: Assemble LP prose query — word-segmented, de-contaminated
# ===================================================================
# Source: lp1_english_forward.txt (armada18) — best spaced community transcription.
# This file covers all LP1 (17 pages) + LP2 p56-57 (AN END, PARABLE).
# It matches scream314's liber_primus.md word-by-word structure.
# De-contamination: the file is already clean (no PGP noise, no jpg annotations).
# We only need to strip the hex hash in AN END.

LP1_SRC = os.path.join(ARMADA18, "lp1_english_forward.txt")
lp1_raw = open(LP1_SRC, encoding="utf-8", errors="ignore").read()

print("\n--- LP Source File (lp1_english_forward.txt) ---")
print(lp1_raw)

def tokenise(text):
    """Extract lowercase alphabetic words."""
    return re.findall(r"[a-z]+", text.lower())

# Strip the hex hash stub in AN END
# "THIRTYSIXTHREESIX..." — this is the spelled-out hash, not prose; keep it
# Actually: "HASHES TO\nTHIRTYSIXTHREE..." — per spec, strip "garbage" not this.
# The spelled-out hash IS the prose content of AN END (the hash-spelled string).
# Per spec: strip "garbage output", "jpg", etc. — not the hash spelling.
# We include all of lp1_english_forward.txt as-is (it's already clean).
lp1_clean = lp1_raw

# Define sections by content (from the file we just read):
# A WARNING (p01) + WELCOME (p03-04) + WISDOM/INSTRUCTION (bridging) +
# SOME WISDOM (p05, aphorism) + KOAN1 (p06-09) + AN INSTRUCTION (p after koan1) +
# LOSS OF DIVINITY (p10-13) + SOME WISDOM2 + AN INSTRUCTION2 +
# KOAN2 CIRCUMFERENCE (p14-15) + AN INSTRUCTION3 + AN END (p73) + PARABLE (p74)

A_WARNING = """A WARNING
BELIEVE NOTHING FROM THIS BOOK
EXCEPT WHAT YOU KNOW TO BE TRUE
TEST THE KNOWLEDGE
FIND YOUR TRUTH
EXPERIENCE YOUR DEATH
DO NOT EDIT OR CHANGE THIS BOOK
OR THE MESSAGE CONTAINED WITHIN
EITHER THE WORDS OR THEIR NUMBERS
FOR ALL IS SACRED"""

WELCOME = """WELCOME
WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS
IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE
ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE
YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY
ULTIMATELY YOU WILL DISCOVER AN END TO SELF
IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES
JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE
LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE"""

WISDOM_CMD = """WISDOM
YOU ARE A BEING UNTO YOURSELF
YOU ARE A LAW UNTO YOURSELF
EACH INTELLIGENCE IS HOLY
FOR ALL THAT LIVES IS HOLY
AN INSTRUCTION COMMAND YOUR OWN SELF"""

SOME_WISDOM = """SOME WISDOM
THE PRIMES ARE SACRED
THE TOTIENT FUNCTION IS SACRED
ALL THINGS SHOULD BE ENCRYPTED
KNOW THIS"""

KOAN1 = """A KOAN
A MAN DECIDED TO GO AND STUDY WITH A MASTER
HE WENT TO THE DOOR OF THE MASTER
WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER
THE STUDENT TOLD THE MASTER HIS NAME
THAT IS NOT WHO YOU ARE THAT IS ONLY WHAT YOU ARE CALLED
WHO ARE YOU WHO WISHES TO STUDY HERE HE ASKED AGAIN
THE MAN THOUGHT FOR A MOMENT AND REPLIED I AM A PROFESSOR
THAT IS WHAT YOU DO NOT WHO YOU ARE REPLIED THE MASTER
WHO ARE YOU WHO WISHES TO STUDY HERE
CONFUSED THE MAN THOUGHT SOME MORE
FINALLY HE ANSWERED I AM A HUMAN BEING
THAT IS ONLY YOUR SPECIES NOT WHO YOU ARE
WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER AGAIN
AFTER A MOMENT OF THOUGHT THE PROFESSOR REPLIED
I AM A CONSCIOUSNESS INHABITING AN ARBITRARY BODY
THAT IS MERELY WHAT YOU ARE NOT WHO YOU ARE
WHO ARE YOU WHO WISHES TO STUDY HERE
THE MAN WAS GETTING IRRITATED
I AM HE STARTED BUT HE COULD NOT THINK OF ANYTHING ELSE TO SAY SO HE TRAILED OFF
AFTER A LONG PAUSE THE MASTER REPLIED THEN YOU ARE WELCOME TO COME STUDY"""

AN_INSTRUCTION1 = """AN INSTRUCTION
DO FOUR UNREASONABLE THINGS EACH DAY"""

LOSS_OF_DIVINITY = """THE LOSS OF DIVINITY
THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY
CONSUMPTION
WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS WITHIN THE DECEPTION
ONE WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH
TWO WE HAVE WHAT WE HAVE NOW BY LUCK AND WE WILL NOT BE STRONG ENOUGH LATER
TO OBTAIN WHAT WE NEED
MOST THINGS ARE NOT WORTH CONSUMING
PRESERVATION
WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK
IF WE LOSE THEM WE WILL NOT BE STRONG ENOUGH TO GAIN THEM AGAIN
THIS IS THE DECEPTION
MOST THINGS ARE NOT WORTH PRESERVING
ADHERENCE
WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT
OR WE FOLLOW REASON SO WE CAN BELONG AND BE RIGHT
THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH
IT IS THE BEHAVIORS OF CONSUMPTION PRESERVATION AND ADHERENCE
THAT HAVE US LOSE OUR PRIMALITY AND THUS OUR DIVINITY"""

SOME_WISDOM2 = """SOME WISDOM
AMASS GREAT WEALTH
NEVER BECOME ATTACHED TO WHAT YOU OWN
BE PREPARED TO DESTROY ALL THAT YOU OWN"""

AN_INSTRUCTION2 = """AN INSTRUCTION
PROGRAM YOUR MIND
PROGRAM REALITY"""

KOAN2 = """A KOAN
DURING A LESSON THE MASTER EXPLAINED THE I
THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID
WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT
THE MASTER SAID IT IS A VOICE INSIDE YOUR HEAD
I DONT HAVE A VOICE IN MY HEAD THOUGHT THE STUDENT
AND HE RAISED HIS HAND TO TELL THE MASTER
THE MASTER STOPPED THE STUDENT AND SAID
THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I
AND THE STUDENTS WERE ENLIGHTENED"""

AN_INSTRUCTION3 = """AN INSTRUCTION
KWESTION ALL THINGS
DISCOVER TRUTH INSIDE YOURSELF
FOLLOW YOUR TRUTH
IMPOSE NOTHING ON OTHERS
KNOW THIS"""

AN_END = """AN END
WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO
THIRTYSIXTHREESIXSEVENSIXTHREETWOABSEVENTYTHREESEVENEIGHTTHREECEEIGHTTHREEF
IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE"""

PARABLE = """PARABLE
LIKE THE INSTAR TUNNELING TO THE SURFACE
WE MUST SHED OUR OWN CIRCUMFERENCES
FIND THE DIVINITY WITHIN AND EMERGE"""

# --- ARM 1: connected-authorial-prose only ---
# EXCLUDE: two koans (KOAN1, KOAN2), pure-aphorism pages (SOME WISDOM)
# INCLUDE: A WARNING, WELCOME, WISDOM_CMD, AN_INSTRUCTION1, LOSS_OF_DIVINITY,
#          SOME_WISDOM2 (borderline but shorter aphoristic counsel, included),
#          AN_INSTRUCTION2, AN_INSTRUCTION3, AN_END, PARABLE
arm1_sections = [
    A_WARNING, WELCOME, WISDOM_CMD, AN_INSTRUCTION1,
    LOSS_OF_DIVINITY, SOME_WISDOM2, AN_INSTRUCTION2,
    AN_INSTRUCTION3, AN_END, PARABLE,
]

# --- ARM 2: all solved prose ---
arm2_sections = arm1_sections + [SOME_WISDOM, KOAN1, KOAN2]

arm1_tokens = tokenise(" ".join(arm1_sections))
arm2_tokens = tokenise(" ".join(arm2_sections))
N_q_arm1 = len(arm1_tokens)
N_q_arm2 = len(arm2_tokens)

# Function-word density
FUNC_WORDS = set(("the of and to a in that it is was for on are as with his they at be this "
                  "have from or had by but not what all were we when there can an your which "
                  "their said if do will each about how up out them then she many some so these "
                  "would other into has more her two like him no could than first been who its "
                  "now my over such our down only may after little very just where most know "
                  "while should through both those before shall").split())

def fw_density(tokens):
    n = len(tokens)
    return sum(1 for t in tokens if t in FUNC_WORDS) / n if n else 0

print(f"\n=== ARM 1 (connected authorial prose, no koans/aphorisms): N_q = {N_q_arm1} words")
print(f"=== ARM 2 (all solved prose):                              N_q = {N_q_arm2} words")
print(f"\nFunction-word density -- Arm 1: {fw_density(arm1_tokens):.3f}")
print(f"Function-word density -- Arm 2: {fw_density(arm2_tokens):.3f}")

# ===================================================================
# STEP 2: Reference corpora (in-repo PD + Cyphernomicon fetch)
# ===================================================================

def read_text(path):
    return open(path, encoding="utf-8", errors="ignore").read()

CYPHERNOMICON_CACHE = os.path.join(CORPUS_DIR, "cyphernomicon_may_1994.txt")
cyphernomicon_available = False

if os.path.exists(CYPHERNOMICON_CACHE):
    cyphernomicon_available = True
    print("\nCyphernomicon: using cached copy")
else:
    print("\nAttempting to fetch Cyphernomicon (Timothy May, 1994)...")
    try:
        import urllib.request
        urls = [
            "https://nakamotoinstitute.org/static/docs/cyphernomicon.txt",
            "https://www.cypherpunks.to/faq/cyphernomicron/cyphernomicon.txt",
        ]
        fetched = False
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = r.read().decode("utf-8", errors="ignore")
                if len(data) > 50000:
                    with open(CYPHERNOMICON_CACHE, "w", encoding="utf-8") as f:
                        f.write(data)
                    cyphernomicon_available = True
                    print(f"  Fetched from {url} ({len(data):,} chars)")
                    fetched = True
                    break
            except Exception as e:
                print(f"  {url}: {e}")
        if not fetched:
            print("  Cyphernomicon unavailable -- proceeding without it")
    except Exception as e:
        print(f"  Fetch error: {e}")

AUTHOR_FILES = {
    "Blavatsky": [os.path.join(ARMADA18, "blavatsky_secret_doctrine_v1.txt")],
    "Agrippa":   [os.path.join(ARMADA18, "agrippa_occult_philosophy_book1_1651jf.txt"),
                  os.path.join(ARMADA18, "agrippa_occult_philosophy_book2_1651jf.txt"),
                  os.path.join(ARMADA18, "agrippa_occult_philosophy_book3_1651jf.txt")],
    "Levi":      [os.path.join(ARMADA18, "levi_history_of_magic.txt")],
    "ManlyHall": [os.path.join(ARMADA18, "manly_hall_initiates_flame.txt")],
    "KJB":       [os.path.join(ARMADA18, "kjb_genesis.txt"),
                  os.path.join(ARMADA18, "kjb_psalms.txt"),
                  os.path.join(ARMADA18, "kjb_revelation.txt"),
                  os.path.join(ARMADA18, "kjb_gospel_john.txt"),
                  os.path.join(ARMADA18, "kjb_ecclesiastes.txt")],
    "Emerson":   [os.path.join(ARMADA18, "emerson_essays_first_series.txt"),
                  os.path.join(ARMADA18, "emerson_essays_second_series.txt")],
    "Poe":       [os.path.join(ARMADA18, "poe_tales_vol2.txt")],
    "Lovecraft": [os.path.join(ARMADA18, "lovecraft_charles_dexter_ward.txt"),
                  os.path.join(ARMADA18, "lovecraft_mountains_madness.txt"),
                  os.path.join(ARMADA18, "lovecraft_dunwich_horror.txt"),
                  os.path.join(ARMADA18, "lovecraft_call_of_cthulhu.txt")],
    "GospelBuddha": [os.path.join(ARMADA19, "gospel_of_buddha_carus.txt")],
}
if cyphernomicon_available:
    AUTHOR_FILES["TimothyMay"] = [CYPHERNOMICON_CACHE]

print("\n--- Loading reference corpora ---")
AUTHOR_WORDS = {}
for author, files in AUTHOR_FILES.items():
    wds = []
    for fpath in files:
        if os.path.exists(fpath):
            wds.extend(tokenise(read_text(fpath)))
        else:
            print(f"  MISSING: {fpath}")
    AUTHOR_WORDS[author] = wds
    print(f"  {author}: {len(wds):,} words")

# ===================================================================
# STEP 3: MFW derivation from reference corpora only (no LP leak)
# ===================================================================

def get_mfw_list(author_words_dict, cap=150):
    """Frequency-ranked words present in ALL reference corpora, capped at cap."""
    pool = []
    for wds in author_words_dict.values():
        pool.extend(wds)
    freq = collections.Counter(pool)
    author_sets = {a: set(w) for a, w in author_words_dict.items()}
    intersection = set.intersection(*author_sets.values())
    ranked = [w for w, _ in freq.most_common() if w in intersection]
    return ranked[:cap]

MFW_ALL = get_mfw_list(AUTHOR_WORDS, cap=150)
K_actual = len(MFW_ALL)
K_SWEEP = [k for k in [50, 100, 150] if k <= K_actual]
if not K_SWEEP:
    K_SWEEP = [K_actual]
print(f"\n--- MFW derivation ---")
print(f"K_intersection (words in all {len(AUTHOR_WORDS)} corpora): {K_actual}")
print(f"MFW top-30: {MFW_ALL[:30]}")
print(f"K sweep: {K_SWEEP}")

# ===================================================================
# STEP 4: Chunk authors, cap per author, feature vectors
# ===================================================================

def chunk_and_cap(words, chunk_size, rng_state, min_chunks=3, max_chunks=MAX_CHUNKS_PER_AUTHOR):
    """Non-overlapping chunks, then random-cap at max_chunks (seed 3301)."""
    all_chunks = []
    for i in range(0, len(words) - chunk_size + 1, chunk_size):
        ch = words[i:i+chunk_size]
        if len(ch) == chunk_size:
            all_chunks.append(ch)
    if len(all_chunks) < min_chunks:
        return None  # drop
    if len(all_chunks) > max_chunks:
        # Sample max_chunks uniformly (seeded)
        idxs = rng_state.choice(len(all_chunks), max_chunks, replace=False)
        idxs = sorted(idxs)
        all_chunks = [all_chunks[i] for i in idxs]
    return all_chunks

def build_all_chunks(author_words, chunk_size, rng_state, min_chunks=3):
    result = {}
    for a, wds in author_words.items():
        chs = chunk_and_cap(wds, chunk_size, rng_state, min_chunks)
        if chs is not None:
            result[a] = chs
            print(f"  {a}: {len(chs)} chunks (N_q={chunk_size})")
        else:
            n = len(wds) // chunk_size if chunk_size else 0
            print(f"  DROP {a}: only {n} chunks at N_q={chunk_size} (need >={min_chunks})")
    return result

def freq_vector(tokens, mfw):
    n = max(1, len(tokens))
    c = collections.Counter(tokens)
    return np.array([c.get(w, 0) / n for w in mfw], dtype=float)

def build_matrix(author_chunks, mfw):
    """dict: author -> np.array of shape (n_chunks, K)"""
    return {a: np.vstack([freq_vector(ch, mfw) for ch in chs])
            for a, chs in author_chunks.items()}

# ===================================================================
# Delta metrics
# ===================================================================

def burrows_delta(zq, zc):
    return float(np.abs(zq - zc).mean())

def cosine_delta(zq, zc):
    d = np.linalg.norm(zq) * np.linalg.norm(zc)
    if d < 1e-9:
        return 1.0
    return float(1.0 - np.dot(zq, zc) / d)

def global_zscore_params(matrix_dict):
    """Compute mu/sd over all chunks in the matrix."""
    all_vecs = np.vstack(list(matrix_dict.values()))
    mu = all_vecs.mean(axis=0)
    sd = all_vecs.std(axis=0) + 1e-9
    return mu, sd

def zscore(vecs, mu, sd):
    return (vecs - mu) / sd

# ===================================================================
# Wilson CI
# ===================================================================

def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2*n)) / denom
    margin = z * math.sqrt(max(0, p*(1-p)/n + z**2/(4*n**2))) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))

# ===================================================================
# Control A — closed-set LOO attribution power (vectorised)
# ===================================================================

def run_control_a(author_chunks, mfw):
    """Vectorised LOO NN attribution."""
    mat = build_matrix(author_chunks, mfw)
    authors = list(mat.keys())
    n_authors = len(authors)
    K = len(mfw)

    correct = total = 0

    for held_author in authors:
        held_mat  = mat[held_author]   # (n_held, K)
        n_held    = held_mat.shape[0]

        for i in range(n_held):
            held_vec = held_mat[i]     # (K,)

            # Build pool excluding held chunk (i) of held_author
            rows_for_zscore = []
            for a, m in mat.items():
                if a == held_author:
                    keep = np.delete(m, i, axis=0)
                    rows_for_zscore.append(keep)
                else:
                    rows_for_zscore.append(m)
            all_vecs = np.vstack(rows_for_zscore)
            mu = all_vecs.mean(axis=0)
            sd = all_vecs.std(axis=0) + 1e-9

            zq = (held_vec - mu) / sd

            best_d = 1e9
            best_a = None
            for a, m in mat.items():
                if a == held_author:
                    pool_m = np.delete(m, i, axis=0)
                else:
                    pool_m = m
                if pool_m.shape[0] == 0:
                    continue
                zpool = (pool_m - mu) / sd
                cent  = zpool.mean(axis=0)
                d = burrows_delta(zq, cent)
                if d < best_d:
                    best_d, best_a = d, a

            total  += 1
            if best_a == held_author:
                correct += 1

    acc = correct / total if total else 0.0
    ci  = wilson_ci(correct, total)
    chance = 1.0 / n_authors
    passes = ci[0] > chance
    print(f"    LOO accuracy: {correct}/{total} = {acc:.4f} "
          f"[Wilson 95% CI: {ci[0]:.4f}-{ci[1]:.4f}]  chance=1/{n_authors}={chance:.4f}  "
          f"{'PASS' if passes else 'FAIL'}")
    return {
        "correct": correct, "total": total, "accuracy": acc,
        "ci_95_wilson": list(ci), "chance": chance,
        "n_authors": n_authors, "passes": passes,
    }

# ===================================================================
# Control B — FER (OPERATIVE gate)
# ===================================================================

def run_control_b(author_chunks, mfw, m_candidates):
    """FER on held-out genuine same-author chunks."""
    mat = build_matrix(author_chunks, mfw)
    authors = list(mat.keys())
    pctile = (1 - 0.05 / m_candidates) * 100

    false_ex = total = 0

    for held_author in authors:
        held_mat = mat[held_author]
        n_held   = held_mat.shape[0]

        # Within-author distribution (we need at least 2 chunks to compute)
        if n_held < 3:
            continue

        for i in range(n_held):
            remaining = np.delete(held_mat, i, axis=0)
            if remaining.shape[0] < 2:
                continue

            # Z-score params from all vecs excl. held
            rows = [remaining if a == held_author else mat[a]
                    for a in authors]
            all_vecs = np.vstack(rows)
            mu = all_vecs.mean(axis=0)
            sd = all_vecs.std(axis=0) + 1e-9

            held_z  = (held_mat[i] - mu) / sd
            rem_z   = (remaining - mu) / sd
            cent    = rem_z.mean(axis=0)

            # Within-author Burrows deltas for other chunks
            wa_b_deltas = []
            wa_c_deltas = []
            for j in range(remaining.shape[0]):
                others_z = np.delete(rem_z, j, axis=0)
                oc = others_z.mean(axis=0)
                wa_b_deltas.append(burrows_delta(rem_z[j], oc))
                wa_c_deltas.append(cosine_delta(rem_z[j], oc))

            if len(wa_b_deltas) < 2:
                continue

            thr_b = float(np.percentile(wa_b_deltas, pctile))
            thr_c = float(np.percentile(wa_c_deltas, pctile))

            d_b = burrows_delta(held_z, cent)
            d_c = cosine_delta(held_z, cent)

            exc = (d_b > thr_b) and (d_c > thr_c)  # concordance required
            total += 1
            if exc:
                false_ex += 1

    FER     = false_ex / total if total else 0.0
    ci      = wilson_ci(false_ex, total)
    gate_ok = ci[1] <= 0.10
    print(f"    FER: {false_ex}/{total} = {FER:.4f} "
          f"[Wilson 95% upper: {ci[1]:.4f}]  "
          f"gate_passes={'YES' if gate_ok else 'NO (NEGATIVE)'}")
    return {
        "false_exclusions": false_ex, "total_held": total,
        "FER": FER, "FER_wilson_ci_95": list(ci),
        "holm_bonferroni_m": m_candidates,
        "percentile_used": pctile, "gate_passes": gate_ok,
    }

# ===================================================================
# LP exclusion step (only if both controls pass)
# ===================================================================

def run_lp_exclusion(arm_tokens, author_chunks, mfw, m_candidates, arm_label):
    mat = build_matrix(author_chunks, mfw)
    all_vecs = np.vstack(list(mat.values()))
    mu = all_vecs.mean(axis=0)
    sd = all_vecs.std(axis=0) + 1e-9

    lp_z = (freq_vector(arm_tokens, mfw) - mu) / sd
    pctile = (1 - 0.05 / m_candidates) * 100

    rows = []
    for a, m in mat.items():
        zm = (m - mu) / sd
        cent = zm.mean(axis=0)
        d_b = burrows_delta(lp_z, cent)
        d_c = cosine_delta(lp_z, cent)

        # Within-author distribution
        wa_b, wa_c = [], []
        for i in range(zm.shape[0]):
            others = np.delete(zm, i, axis=0)
            if others.shape[0] == 0:
                continue
            oc = others.mean(axis=0)
            wa_b.append(burrows_delta(zm[i], oc))
            wa_c.append(cosine_delta(zm[i], oc))

        thr_b = float(np.percentile(wa_b, pctile)) if len(wa_b) >= 2 else float("inf")
        thr_c = float(np.percentile(wa_c, pctile)) if len(wa_c) >= 2 else float("inf")

        exc_b  = d_b > thr_b
        exc_c  = d_c > thr_c
        exc    = exc_b and exc_c

        rows.append({
            "author": a, "delta_burrows": float(d_b), "delta_cosine": float(d_c),
            "threshold_burrows": float(thr_b), "threshold_cosine": float(thr_c),
            "excluded_burrows": bool(exc_b), "excluded_cosine": bool(exc_c),
            "excluded_concordant": bool(exc),
            "n_chunks": int(m.shape[0]),
        })
        flag = "EXCLUDED" if exc else "not-excluded"
        print(f"    {a:15s} Burrows={d_b:.4f}(thr={thr_b:.4f}) "
              f"Cosine={d_c:.4f}(thr={thr_c:.4f})  => {flag}")

    rows.sort(key=lambda x: x["delta_burrows"])
    print(f"  Nearest (Burrows): {rows[0]['author']} Delta={rows[0]['delta_burrows']:.4f}")
    return rows

# ===================================================================
# MAIN LOOP: arm x K
# ===================================================================

ARMS = {
    "arm1_connected_prose": arm1_tokens,
    "arm2_all_prose":       arm2_tokens,
}
N_Q = {
    "arm1_connected_prose": N_q_arm1,
    "arm2_all_prose":       N_q_arm2,
}

all_results = {
    "pre_registration": "r9-01-burrows-delta-exclusion/PRE-REGISTRATION.md",
    "seed":     RNG_SEED,
    "max_chunks_per_author": MAX_CHUNKS_PER_AUTHOR,
    "N_q":      {"arm1_connected_prose": N_q_arm1, "arm2_all_prose": N_q_arm2},
    "fw_density": {
        "arm1": float(fw_density(arm1_tokens)),
        "arm2": float(fw_density(arm2_tokens)),
    },
    "MFW_basis": {
        "n_authors_in_reference": len(AUTHOR_WORDS),
        "K_intersection": K_actual,
        "K_sweep": K_SWEEP,
        "mfw_list_top50": MFW_ALL[:50],
        "cyphernomicon_included": cyphernomicon_available,
    },
    "arms": {},
}

m_candidates = len(AUTHOR_WORDS)  # Holm-Bonferroni m

for arm_label, arm_tokens in ARMS.items():
    N_q = N_Q[arm_label]
    print(f"\n{'='*70}")
    print(f"ARM: {arm_label}  (N_q = {N_q})")
    print(f"{'='*70}")

    arm_res = {"N_q": N_q, "fw_density": float(fw_density(arm_tokens)), "K_results": {}}

    for K in K_SWEEP:
        mfw = MFW_ALL[:K]
        print(f"\n--- K = {K} ---")

        # Reseed rng for reproducibility
        rng_k = np.random.RandomState(RNG_SEED + K)

        author_chunks = build_all_chunks(AUTHOR_WORDS, N_q, rng_k, min_chunks=3)

        if len(author_chunks) < 4:
            msg = f"Only {len(author_chunks)} authors with >=3 chunks at N_q={N_q}; need >=4"
            print(f"  INSUFFICIENT: {msg}")
            arm_res["K_results"][str(K)] = {
                "error": msg, "authors_available": list(author_chunks.keys()),
            }
            continue

        print(f"  Using {len(author_chunks)} authors for controls")

        print(f"\n  [Control A] K={K}")
        ctrl_a = run_control_a(author_chunks, mfw)

        print(f"\n  [Control B] K={K}, m={m_candidates}")
        ctrl_b = run_control_b(author_chunks, mfw, m_candidates)

        ctrl_a_ok = ctrl_a["passes"]
        ctrl_b_ok = ctrl_b["gate_passes"]

        print(f"\n  DECISION RULE:")
        print(f"    Ctrl A (CI_lo > chance):   {'PASS' if ctrl_a_ok else 'FAIL'}")
        print(f"    Ctrl B (FER_upper <= 0.10): {'PASS' if ctrl_b_ok else 'FAIL (NEGATIVE)'}")

        lp_exc = None
        if not ctrl_b_ok:
            branch = "NEGATIVE_FER_GATE"
            print(f"  >> VERDICT: NEGATIVE (FER gate failed; exclusion uninterpretable at N_q={N_q})")
        elif not ctrl_a_ok:
            branch = "NEGATIVE_CONTROL_A"
            print(f"  >> VERDICT: NEGATIVE (Control A fails)")
        else:
            branch = "LP_EXCLUSION_REACHED"
            print(f"  >> BOTH PASS -- LP exclusion step (EXPLORATORY)")
            lp_exc = run_lp_exclusion(arm_tokens, author_chunks, mfw, m_candidates, arm_label)

        arm_res["K_results"][str(K)] = {
            "mfw_K": K,
            "n_authors_used": len(author_chunks),
            "authors": list(author_chunks.keys()),
            "control_A": ctrl_a,
            "control_B": ctrl_b,
            "decision_branch": branch,
            "lp_exclusion": lp_exc,
        }

    all_results["arms"][arm_label] = arm_res

# ===================================================================
# Save results
# ===================================================================

results_path = os.path.join(EXP_DIR, "results.json")
with open(results_path, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
print(f"\nResults saved: {results_path}")

# Save frequency tables (derived, not raw)
freq_tables = {}
for author, wds in AUTHOR_WORDS.items():
    c  = collections.Counter(wds)
    n  = len(wds)
    freq_tables[author] = {
        "total_words": n,
        "mfw_relative_freqs": {w: round(c.get(w,0)/n, 8) for w in MFW_ALL},
    }
with open(os.path.join(CORPUS_DIR, "freq_tables.json"), "w", encoding="utf-8") as f:
    json.dump(freq_tables, f, indent=2)

print(f"\n{'='*70}")
print("EXPERIMENT COMPLETE")
print(f"{'='*70}")
print(f"\nSUMMARY:")
print(f"  N_q arm1 (connected prose): {N_q_arm1}")
print(f"  N_q arm2 (all prose):       {N_q_arm2}")
print(f"  FW density arm1 / arm2:     {fw_density(arm1_tokens):.3f} / {fw_density(arm2_tokens):.3f}")
print(f"  K_intersection:             {K_actual}")
print(f"  K sweep:                    {K_SWEEP}")
print(f"  Cyphernomicon included:     {cyphernomicon_available}")
for arm_label, arm_res in all_results["arms"].items():
    for K, kr in arm_res.get("K_results", {}).items():
        if "error" not in kr:
            print(f"  [{arm_label} K={K}] branch={kr['decision_branch']}")
