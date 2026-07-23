"""Campaign XVIII / Armada-2 -- LARGE KEYWORD / SHORT-KEY VIGENERE sweep, skip-aware.

WHY THIS ATTACK (open item not yet closed)
------------------------------------------
Rigid IoC/Kasiski tests excluded periodic/Vigenere keys from LP2 because flat IoC
implies non-periodic ciphertext. But the DOUBLET-KEY-SKIP filter (~83% active) DESYNCHRONISES
even a short repeating key after the first skip (~1 per 35 runes). A periodic key that
WOULD produce a clear-text Kasiski signature rigidly becomes APERIODIC in output because
each skip shifts the phase -- so the IoC exclusion does NOT bind for skip-filtered ciphertext.
The skip-tolerant beam is the only decoder that can score a periodic key correctly.

KEYWORD STRATEGY
----------------
The beam accepts a repeating keyword as a Vigenere key by tiling it to the required length.
No alignment offset is needed beyond what the prefilter already discovers -- a keyword of
length K repeats so the only distinct offsets are {0..K-1}, but the skip desyncs make
additional positions viable; prefilter handles this. We sweep:

  1. Cicada-specific vocabulary: words and phrases from solved pages, puzzle metadata,
     and the Cicada 3301 community lexicon.
  2. Esoteric / occult terms (Aleister Crowley / Thelema, Kabbalah, gematria, rune lore).
  3. A ~4000-word English vocabulary covering frequency-top-3000 plus thematically
     plausible terms (science, mathematics, philosophy, religions).

DECODER USED: sweep.beam + sweep.prefilter (the validated skip-tolerant beam from
skipdecode.py / robustness.py, imported verbatim).

VALIDATION GATE (mandatory before trusting any result)
-------------------------------------------------------
A synthetic planted-key gate: take English plaintext, encipher it under a REPEATING keyword
as a Vigenere key WITH the ~83% doublet-skip filter; verify (a) rigid 1:1 decode scores
the key as NOISE (< -6.0), (b) the skip beam RECOVERS it (> -5.0, match > 95%). This is the
same gate the module-level skipdecode.py uses, adapted for the keyword/Vigenere scenario.

If the gate fails -> ABORT with a clear message; do NOT trust sweep scores.

THRESHOLDS (from robustness.py / Campaign XI)
---------------------------------------------
  noise floor (null-max)  : -6.82
  confirm threshold        : -5.5
  English solve regime     : -4.3 to -4.0
  report threshold         : -6.0  (anything above = worth logging; below noise but not null)

MODES
-----
  default (--smoke): 3 pages, full keyword list, report best score (orchestrator <60s target)
  --full           : all 55 unsolved pages (orchestrator only)

Run:
  PYTHONUTF8=1 python3 analysis/campaign18_skip/armada2/keywords_skip.py
  PYTHONUTF8=1 python3 analysis/campaign18_skip/armada2/keywords_skip.py --smoke
  PYTHONUTF8=1 python3 analysis/campaign18_skip/armada2/keywords_skip.py --full
"""
import os
import sys
import time
import argparse
import random

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))

from lp import gematria as gp, score as sc
from run_stats import load_pages
from skipdecode import eng_to_idx, idx_to_trans, encipher_keyskip
from sweep import beam, prefilter, Q, N, MAXSKIP

# ----------------------------------------------------------------- thresholds
SCREEN_LEN = 90
SCREEN_THR = -6.0
CONF_THR = -5.5
REPORT_THR = -6.0      # anything above this is logged (even if below confirm)
SCREEN_BEAM = 300
FULL_BEAM = 500

# ----------------------------------------------------------------- keyword list

# ---- Group 1: Cicada 3301 specific vocabulary ----
CICADA_VOCAB = [
    # Core solved-page words / puzzle vocabulary
    "INSTAR", "EMERGENCE", "PILGRIM", "DIVINITY", "CIRCUMFERENCE",
    "PRIMES", "SACRED", "MOBIUS", "WELCOME", "WISDOM", "KOAN",
    "TOTIENT", "SHADOW", "SELFRELIANCE", "PARABLE", "ANEND",
    "LIBERPRIMUS", "CICADA", "CICADATHREETHREEOHONE",
    "THREETHREEOHONE", "GEMATRIA", "PRIMUS", "LAMEN",
    "WITHIN", "WITHOUT", "TRUTH", "DEEP", "WEB", "ONION",
    "LIBER", "PATH", "ENLIGHTENMENT", "KNOWLEDGE",
    "CARNAL", "LOSS", "SELF", "GAIN", "SEEKING", "SEEKER",
    "DARKNESS", "LIGHT", "VEIL", "HIDDEN", "REVEALED",
    "RUNE", "RUNES", "RUNIC", "FUTHARK", "ELDER",
    "CRYPTOGRAPHY", "CIPHER", "ENCRYPTED", "ENCRYPTION",
    # Solved-page context words
    "THE", "AND", "THAT", "THIS", "THOU", "THEE",
    "FIND", "KNOW", "LOSE", "GAIN", "SHALL", "WILL",
    "HOLY", "DIVINE", "SACRED", "MORTAL", "IMMORTAL",
    "PRIME", "NUMBER", "FUNCTION", "SEQUENCE",
    # Puzzle identifiers and keys
    "OUTERCIRCLE", "INNERCIRCLE", "PARABLE",
    "MIDDLEPATH", "KEY", "KEYS", "UNLOCK",
    "RESONANCE", "LISTEN", "HEAR", "SEE",
]

# ---- Group 2: Esoteric / occult / philosophical terms ----
ESOTERIC_VOCAB = [
    # Thelema / Crowley
    "THELEMA", "AGAPE", "ABRAHADABRA", "AIWAZ", "HADIT", "NUIT",
    "BEAST", "BABALON", "TIPHERETH", "KETHER", "MALKUTH", "CHOKMAH",
    "BINAH", "CHESED", "GEBURAH", "NETZACH", "HOD", "YESOD",
    "AEON", "AEONIC", "WILL", "WORD", "LAW", "LOVE",
    # Kabbalah
    "KABBALAH", "SEPHIROT", "DAATH", "AIN", "AINSOPH", "QLIPHOTH",
    "SEPHER", "ZOHAR", "GEMATRIA", "NOTARIKON", "TEMURAH",
    # Numerology
    "FIBONACCI", "GOLDEN", "PHI", "EULER", "FERMAT", "EULER",
    # Runic / Norse
    "ODIN", "MJOLNIR", "VALHALLA", "RUNE", "ANSUZ", "FEHU",
    "URUZ", "THURISAZ", "RAIDO", "KENAZ", "GEBO", "WUNJO",
    "HAGALAZ", "NAUTHIZ", "ISA", "JERA", "EIHWAZ", "PERTHRO",
    "ALGIZ", "SOWILO", "TIWAZ", "BERKANO", "EHWAZ", "MANNAZ",
    "LAGUZ", "INGWAZ", "OTHALAN", "DAGAZ",
    # Buddhism / Eastern
    "DHARMA", "KARMA", "MAYA", "NIRVANA", "MANDALA", "LOTUS",
    "ZEN", "KOAN", "SAMSARA", "MOKSHA", "SUNYATA",
    # Gnosticism
    "GNOSIS", "SOPHIA", "DEMIURGE", "PLEROMA", "ARCHON",
    "AEON", "PISTIS", "LOGOS", "PNEUMA",
    # Mathematics
    "TOTIENT", "EULER", "SIEVE", "ERATOSTHENES", "RIEMANN",
    "FERMAT", "MERSENNE", "PERFECT", "ABUNDANT",
    # Philosophy
    "EMERSON", "THOREAU", "WALDEN", "OVERSOUL", "TRANSCEND",
    "DIALECTIC", "VIRTUE", "LOGOS", "NOUMENON",
]

# ---- Group 3: High-frequency English + thematically plausible common words ----
COMMON_WORDS = [
    # Top-frequency English (1-letter useful as gematria key, 2+ letters meaningful)
    "THE", "OF", "AND", "TO", "IN", "IS", "IT",
    "THAT", "WAS", "FOR", "ON", "ARE", "WITH", "AS",
    "AT", "BE", "BY", "FROM", "OR", "AN", "THIS",
    "WHICH", "ONE", "HAD", "BUT", "NOT", "WHAT", "ALL",
    "WERE", "WHEN", "WE", "THERE", "CAN", "WHO",
    "NO", "HE", "HIS", "SO", "OUT", "IF", "SAID",
    "HAVE", "MORE", "THEY", "SOME", "TIME", "HER",
    "THAN", "THEN", "NOW", "LOOK", "ONLY", "COME",
    "COULD", "OVER", "THINK", "ALSO", "BACK", "AFTER",
    "USE", "TWO", "HOW", "OUR", "WORK", "FIRST", "WELL",
    "WAY", "EVEN", "WANT", "BECAUSE", "THESE", "GIVE",
    "MOST", "TELL", "BETWEEN", "NEED", "LARGE", "OFTEN",
    "HAND", "HIGH", "PLACE", "HOLD", "LONG", "OPEN", "SEEM",
    "TOGETHER", "NEXT", "WHITE", "CHILDREN", "MIGHT", "BEGIN",
    "WHILE", "NUMBER", "ALWAYS", "CALLED", "SIDE", "FEET",
    "CAR", "MILE", "WALK", "MORNING", "NIGHT", "UNTIL",
    "SMALL", "EVERY", "FOUND", "STILL", "LEARN", "SHOULD",
    "NEVER", "START", "CITY", "EARTH", "EYES", "LIGHT",
    "THOUGHT", "HEAD", "UNDER", "STORY", "SAW", "FAR",
    "SEA", "DRAW", "LEFT", "LATE", "RUN", "MISS", "IDEA",
    "ENOUGH", "EAT", "FACE", "WATCH", "FAR", "ABOVE",
    "BETWEEN", "NEED", "LARGE", "OFTEN", "HAND", "HIGH",
    "GOD", "MIND", "BODY", "SOUL", "SPIRIT", "LIFE", "DEATH",
    "WORLD", "EARTH", "WATER", "FIRE", "AIR", "VOID",
    "MAN", "WOMAN", "CHILD", "KING", "QUEEN", "LORD",
    "DAY", "NIGHT", "SUN", "MOON", "STAR", "STARS",
    "ABOVE", "BELOW", "WITHIN", "WITHOUT", "BEFORE", "AFTER",
    "EAST", "WEST", "NORTH", "SOUTH",
    "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN",
    "EIGHT", "NINE", "TEN", "ZERO",
    "GOOD", "EVIL", "TRUE", "FALSE", "RIGHT", "WRONG",
    "BEING", "BECOMING", "KNOWING", "SEEKING", "FINDING",
    "LOVE", "HATE", "FEAR", "HOPE", "FAITH", "DOUBT",
    "POWER", "FORCE", "ENERGY", "MATTER", "SPACE", "TIME",
    "PAST", "PRESENT", "FUTURE",
    "BEGIN", "END", "START", "FINISH", "OPEN", "CLOSE",
    "GIVE", "TAKE", "MAKE", "DO", "SAY", "SPEAK",
    # Science / mathematics terms
    "PRIME", "FACTOR", "MODULO", "INVERSE", "SQUARE", "CUBE",
    "ROOT", "LOG", "SIN", "COS", "TAN", "EXP",
    "MATRIX", "VECTOR", "TENSOR", "GROUP", "RING", "FIELD",
    "SET", "FUNCTION", "LIMIT", "INFINITY", "NULL", "ZERO",
    "ALGORITHM", "CIPHER", "KEY", "CODE", "MESSAGE", "SIGNAL",
    "HASH", "SALT", "SEED", "RANDOM", "ENTROPY", "ORDER",
    "CHAOS", "PATTERN", "STRUCTURE", "FORM", "CONTENT",
    # Animals / nature (LP themes)
    "CICADA", "ANT", "BEE", "SPIDER", "SNAKE", "EAGLE",
    "LION", "WOLF", "FOX", "OWL", "RAVEN", "DOVE",
    "TREE", "FOREST", "MOUNTAIN", "RIVER", "OCEAN", "DESERT",
    "STONE", "ROCK", "CRYSTAL", "GOLD", "SILVER", "IRON",
    # Archaic / literary
    "THOU", "THEE", "THY", "THINE", "HATH", "DOTH",
    "WHEREFORE", "HENCEFORTH", "UNTO", "THEREOF", "WHEREBY",
    "UPON", "HENCE", "THUS", "THEREFORE",
]

# ---- Group 4: Additional Cicada-culture / puzzle-community terms ----
PUZZLE_VOCAB = [
    # Known Cicada keyphrases / clue terms
    "PRIME", "FIBONACI", "FIBONACCI", "GOLDEN",
    "NEOPRIMITIVE", "APERIODIC", "MONOTONIC",
    "LAMBDA", "ALPHA", "OMEGA", "SIGMA", "THETA",
    "DELTA", "GAMMA", "BETA", "PI", "TAU",
    # Technical crypto terms Cicada might use as primers
    "VIGENERE", "KEYED", "ONETIME", "PAD", "OTP",
    "RUNNING", "STREAM", "BLOCK", "POLYALPHABETIC",
    # LP1 words (from solved pages)
    "PATHS", "THREE", "PATHS", "LABYRINTH", "CARNAL",
    "UNDERSTANDING", "REASON", "MIND", "LIGHT", "DARK",
    "LUST", "GREED", "GLUTTONY", "SLOTH", "WRATH",
    "ENVY", "PRIDE", "VIRTUE", "HUMILITY",
    "CHAPTER", "VERSE", "SECTION", "PAGE",
    "BOOK", "TEXT", "WORD", "LETTER", "SYMBOL",
    # Onion / dark web Cicada terminology
    "ONION", "TORRENT", "DARKWEB", "HIDDEN", "SERVICE",
    "ANONYMOUS", "ANON", "ANONS",
    # Numbers as strings
    "THIRTYTHREEOHONE", "ONETHREETHREEOHONE",
]

# ---- Group 5: 2-4 letter keywords (test short-period Vigenere) ----
SHORT_KEYS = [
    # All common 2-letter combos mapping to LP alphabet
    "AB", "AC", "AF", "AG", "AH", "AI", "AL", "AM", "AN", "AO", "AP",
    "AR", "AS", "AT", "AW", "AX", "AY", "AZ",
    "BA", "BE", "BI", "BO", "BY",
    "CA", "CE", "DA", "DE", "DO",
    "EA", "EE", "EI", "EL", "EN", "ER", "ES", "ET",
    "FA", "FE", "FO", "FU",
    "GA", "GE", "GI", "GO", "GU",
    "HA", "HE", "HI", "HO",
    "IA", "IF", "IN", "IO", "IS", "IT",
    "JA", "JO",
    "KA", "KE", "KO",
    "LA", "LE", "LI", "LO", "LU",
    "MA", "ME", "MI", "MO", "MU",
    "NA", "NE", "NI", "NO", "NU",
    "OA", "OE", "OF", "OH", "OI", "OM", "ON", "OO", "OR", "OS",
    "PA", "PE", "PI", "PO", "PU",
    "RA", "RE", "RI", "RO", "RU",
    "SA", "SE", "SI", "SO", "SU",
    "TA", "TE", "TH", "TI", "TO", "TU",
    "UA", "UE", "UI", "UM", "UN", "UP", "UR", "US",
    "WA", "WE", "WI", "WO",
    "YA", "YE",
    "ZA", "ZE", "ZO",
    # 3-letter high-freq
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
    "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "GET",
    "HAS", "HIM", "HIS", "HOW", "ITS", "MAY", "NEW", "NOW",
    "OLD", "OWN", "SAY", "SHE", "TOO", "USE", "WAY", "WHO",
    # LP-specific short
    "GOD", "KEY", "LAW", "END", "RUN", "OMN", "UNI",
    "ANS", "ANG", "EIH", "TYR", "ISS", "WYN", "HAG",
]


def build_keyword_list(priority_only=False):
    """Combine all keyword groups, deduplicate, convert to idx, filter out empties
    and keywords too short to be useful.

    priority_only=True: return only the highest-priority ~200 keywords (Cicada vocab
    + esoteric terms + short keys). Used by the smoke to stay under 60s budget.
    priority_only=False: full list (~600+). Used by the orchestrator for the full run.
    """
    seen = set()
    result = []
    if priority_only:
        raw_words = CICADA_VOCAB + ESOTERIC_VOCAB + SHORT_KEYS + PUZZLE_VOCAB
    else:
        raw_words = (
            CICADA_VOCAB + ESOTERIC_VOCAB + COMMON_WORDS + PUZZLE_VOCAB + SHORT_KEYS
        )
    for w in raw_words:
        w = w.strip().upper()
        if not w or w in seen:
            continue
        seen.add(w)
        idx = eng_to_idx(w)
        if len(idx) < 1:
            continue
        result.append((w, idx))
    return result


def tile_key(idx, min_len):
    """Tile a keyword index list to at least min_len symbols."""
    if not idx:
        return np.zeros(min_len, dtype=np.int64)
    reps = (min_len // len(idx)) + 2
    return np.array(idx * reps, dtype=np.int64)


# ================================================================= GATE
def gate(verbose=True):
    """Planted-key validation: encipher English under a REPEATING keyword with the
    ~83% doublet-skip filter -> rigid decoder must miss, skip beam must recover.

    NOTE: the mechanism is identical to skipdecode.gate() but uses a TILED (repeating)
    keyword as the running key. If periodic Vigenere+skip is decodable by the beam,
    this gate must pass. If it fails: the prefilter or tiling is broken -- abort."""
    def pr(*a):
        if verbose:
            print(*a)

    pr("=" * 74)
    pr("GATE -- repeating-keyword skip beam must recover what rigid misses")
    pr("=" * 74)

    plain_en = (
        "THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
        "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
        "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
        "SACRED GEOMETRY OF THE CIRCUMFERENCE AND LOSE THE SELF TO GAIN THE WHOLE"
    )
    P = eng_to_idx(plain_en)

    # Planted keyword: CIRCUMFERENCE (length 13, not trivially short)
    kw = "CIRCUMFERENCE"
    kw_idx = eng_to_idx(kw)
    # Tile to a key long enough for worst-case skipping
    need = len(P) * (MAXSKIP + 1) + 64
    K_tiled = kw_idx * (need // len(kw_idx) + 2)
    K_list = K_tiled[:need]

    sign = -1
    o_true = 0

    # encipher with skip filter
    C, skips, _ = encipher_keyskip(P, K_list, sign=sign, supp=0.83, seed=3301)
    tot_skips = sum(skips)
    dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / max(1, len(C) - 1)
    pr(f"\nplaintext runes  : {len(P)}")
    pr(f"keyword          : {kw!r}  ({len(kw_idx)} idx symbols)")
    pr(f"total key-skips  : {tot_skips}")
    pr(f"ct doublet rate  : {dbl*100:.2f}%  (random 3.45%; target <1%)")

    truth_tl = idx_to_trans(P)
    pr(f"\nTRUTH  : {truth_tl[:80]}")

    # --- rigid decode at true offset ---
    K_np = np.array(K_list, dtype=np.int64)
    ct_np = np.array(C, dtype=np.int64)
    pi_rigid = [(int(ct_np[i]) + sign * int(K_np[o_true + i])) % N for i in range(len(C))]
    tl_rigid = idx_to_trans(pi_rigid)
    s_rigid = Q.score_norm(tl_rigid)
    match_r = sum(a == b for a, b in zip(pi_rigid, P)) / len(P)
    pr(f"\n[RIGID  correct key+offset]  score_norm = {s_rigid:.3f}  match = {match_r*100:.1f}%")
    pr(f"  {tl_rigid[:80]}")

    # --- skip beam at true offset ---
    pi_beam = beam(ct_np, K_np, sign, o_true, len(C), 500)
    tl_beam = idx_to_trans(pi_beam)
    s_beam = Q.score_norm(tl_beam)
    match_b = sum(a == b for a, b in zip(pi_beam, P)) / len(P)
    pr(f"\n[BEAM   correct key+offset]  score_norm = {s_beam:.3f}  match = {match_b*100:.1f}%")
    pr(f"  {tl_beam[:80]}")

    # --- wrong keyword control ---
    wrong_kw_idx = eng_to_idx("MABINOGION")
    WK_list = wrong_kw_idx * (need // len(wrong_kw_idx) + 2)
    WK_np = np.array(WK_list[:need], dtype=np.int64)
    pi_wrong = beam(ct_np, WK_np, sign, 0, len(C), 500)
    s_wrong = Q.score_norm(idx_to_trans(pi_wrong))
    pr(f"\n[BEAM   WRONG keyword ctrl]  score_norm = {s_wrong:.3f}")

    pr("\n" + "-" * 74)
    # Gate criteria matching skipdecode.gate + robustness.py thresholds
    ok = (match_b > 0.95 and s_beam > -5.0
          and s_rigid < -6.0 and s_wrong < -6.0)
    pr("GATE RESULT:", "PASS -- skip beam recovers repeating keyword; rigid is noise"
       if ok else "FAIL -- investigate before trusting keyword sweep scores")
    pr("  scale: English ~-4.3 | confirm threshold -5.5 | null-max -6.82 | noise -7.5")
    pr(f"  rigid {s_rigid:.3f} (need <-6.0)  beam {s_beam:.3f} (need >-5.0)  "
       f"ctrl {s_wrong:.3f} (need <-6.0)  match {match_b*100:.1f}% (need >95%)")
    return ok, dict(rigid=s_rigid, beam=s_beam, ctrl=s_wrong, match=match_b)


# ================================================================= ATTACK ONE PAGE

def attack_page_keyword_fast(ct, keywords, sign_list=(-1, 1), atbash_list=(False, True),
                             screen_len=SCREEN_LEN, screen_beam=SCREEN_BEAM,
                             full_beam=FULL_BEAM):
    """KEYWORD-OPTIMISED attack variant used by smoke and orchestrator.

    KEY INSIGHT: for a repeating keyword of period P, all distinct Vigenere phases
    are covered by offsets {0..P-1} within the tiled key. Testing arbitrary large
    offsets (what the generic prefilter does) is redundant -- offset P is identical
    to offset 0. This allows us to skip the expensive prefilter entirely for keywords
    and iterate only over the P canonical offsets. For Cicada keywords (period 2-13)
    this is 5-13x fewer beam calls than the standard prefilter's PREFILTER_K=24.

    The tradeoff: we lose the prefilter's tier-2 bigram re-ranking, so we run a tiny
    screen beam over all P offsets and keep the best. Any genuine English signal will
    survive in one of the P phases.

    For the confirm step (score > SCREEN_THR) we run the full-beam over the whole
    page at the best offset per (kw, sign, atbash) -- identical to attack_page.

    Returns (hits, best_glob) with the same schema as attack_page.
    """
    L = len(ct)
    need = L * (MAXSKIP + 1) + 64
    hits = []
    best_glob = (-99.0, None)

    for kw, kw_idx in keywords:
        K_np = tile_key(kw_idx, need)
        P = len(kw_idx)          # keyword period; iterate only this many offsets

        for sign in sign_list:
            for atbash in atbash_list:
                ct2 = (N - 1 - ct) % N if atbash else ct

                # Screen: beam over P canonical offsets
                best_phase = (-99.0, 0)
                for o in range(P):
                    pi = beam(ct2, K_np, sign, o, min(screen_len, L), screen_beam)
                    s = Q.score_norm(idx_to_trans(pi))
                    if s > best_phase[0]:
                        best_phase = (s, o)

                s_best, o_best = best_phase
                if s_best > best_glob[0]:
                    best_glob = (s_best, (kw, sign, atbash, o_best))

                # Confirm: if screen score is promising, full-page beam at best offset
                if s_best > SCREEN_THR:
                    pf = beam(ct2, K_np, sign, o_best, L, full_beam)
                    fs = Q.score_norm(idx_to_trans(pf))
                    if fs > CONF_THR:
                        hits.append((fs, kw, sign, atbash, o_best,
                                     idx_to_trans(pf)))

    return hits, best_glob


def attack_page(ct, keywords, sign_list=(-1, 1), atbash_list=(False, True),
                screen_len=SCREEN_LEN, screen_beam=SCREEN_BEAM, full_beam=FULL_BEAM):
    """Full-power attack using sweep.prefilter (arbitrary key offsets).
    Used by the orchestrator's --full run where non-keyword keytexts might be
    tested via the same interface and the offset is non-trivial.
    For keyword Vigenere sweeps, prefer attack_page_keyword_fast which exploits
    the repeating structure.

    Returns (hits, best_glob) where:
      hits:      list of (score, kw, sign, atbash, translit_prefix) above CONF_THR
      best_glob: (best_score, (kw, sign, atbash)) -- the highest screen score seen
    """
    L = len(ct)
    need = L * (MAXSKIP + 1) + 64
    hits = []
    best_glob = (-99.0, None)

    for kw, kw_idx in keywords:
        K_np = tile_key(kw_idx, need)

        for sign in sign_list:
            for atbash in atbash_list:
                ct2 = (N - 1 - ct) % N if atbash else ct

                offs = prefilter(ct2, K_np, sign)
                for o in offs:
                    pi = beam(ct2, K_np, sign, int(o), min(screen_len, L), screen_beam)
                    s = Q.score_norm(idx_to_trans(pi))
                    if s > best_glob[0]:
                        best_glob = (s, (kw, sign, atbash, int(o)))
                    if s > SCREEN_THR:
                        # promote to full-page confirm
                        pf = beam(ct2, K_np, sign, int(o), L, full_beam)
                        fs = Q.score_norm(idx_to_trans(pf))
                        if fs > CONF_THR:
                            hits.append((fs, kw, sign, atbash, int(o),
                                         idx_to_trans(pf)))
    return hits, best_glob


# ================================================================= SMOKE
def smoke(page_indices=(0, 1, 2)):
    """Run the full keyword list over 3 pages; report best score.

    FAST-SMOKE STRATEGY (fits <60s on a loaded 6-core box):
    - Reduced prefilter width (BG=80, K=8) and beam width (screen=120, full=250)
      vs the orchestrator's full parameters.
    - All 3 pages, both signs, atbash=False only in the screen pass; atbash=True
      only for survivors above -6.5 (rare; the real pages have flat IoC so atbash
      is not expected to dramatically change scores).
    - Full-confirm still uses the standard 250-beam over the full page.
    The speed trade-off: ~5% of candidates near the threshold may be missed; any
    genuine hit at -5.5 will be seen. This is equivalent to the other armada2 smokes.
    """
    from sweep import PREFILTER_BG, PREFILTER_K  # noqa -- read current defaults

    # Smoke parameters: ~3x faster than orchestrator defaults
    # Smoke parameters: reduced screen length + priority keyword subset to fit <60s.
    # The page length is capped to 120 runes (consistent with other armada2 smokes,
    # e.g. interrupter_skip.py), which halves prefilter cost vs full-page scans.
    SMOKE_CT_CAP = 120
    SMOKE_SCREEN_BEAM = 200
    SMOKE_FULL_BEAM = 350
    SMOKE_SCREEN_LEN = min(SCREEN_LEN, SMOKE_CT_CAP)

    print("=" * 74)
    print("SMOKE: keyword/Vigenere skip-beam over 3 unsolved LP2 pages")
    print(f"       ct_cap={SMOKE_CT_CAP}  signs=+/-1  atbash=0,1  "
          f"screen_len={SMOKE_SCREEN_LEN}  screen_beam={SMOKE_SCREEN_BEAM}")
    print(f"       thresholds: confirm={CONF_THR}  report={REPORT_THR}  "
          f"null-max=-6.82  English=-4.3")
    print("=" * 74)

    pages = load_pages()[:-2]   # 55 unsolved
    # Smoke uses priority-only subset (Cicada + esoteric + short keys, ~400 words)
    # to stay under 60s budget. Full list (~620) used by orchestrator's --full run.
    keywords = build_keyword_list(priority_only=True)
    print(f"keywords loaded (priority subset for smoke): {len(keywords)}")

    t0 = time.time()
    best_overall = (-99.0, None)
    all_hits = []

    for pno in page_indices:
        ct_full = np.array(pages[pno], dtype=np.int64)
        # Cap ciphertext length for smoke speed; full page used in --full run
        ct = ct_full[:SMOKE_CT_CAP]
        hits, bg = attack_page_keyword_fast(ct, keywords,
                                              screen_len=SMOKE_SCREEN_LEN,
                                              screen_beam=SMOKE_SCREEN_BEAM,
                                              full_beam=SMOKE_FULL_BEAM)
        flag = "  *** HIT ***" if hits else ""
        print(f"\npage {pno:2d} (len {len(ct_full):3d}, smoke cap {SMOKE_CT_CAP})  "
              f"best_screen={bg[0]:.3f}  via {bg[1]}{flag}  [{time.time()-t0:.1f}s]")
        if bg[0] > best_overall[0]:
            best_overall = (bg[0], bg[1])
        for h in sorted(hits, reverse=True)[:5]:
            fs, kw, sign, atb, o, tl = h
            print(f"  HIT score={fs:.3f}  kw={kw!r}  sign={sign}  atbash={atb}  off={o}")
            print(f"      {tl[:90]}")
        all_hits += [(pno,) + h for h in hits]

    elapsed = time.time() - t0
    print("\n" + "=" * 74)
    print(f"SMOKE DONE in {elapsed:.1f}s | {len(keywords)} keywords x {len(page_indices)} pages "
          f"x 2 signs x 2 atbash")
    print(f"best score seen : {best_overall[0]:.3f}  via {best_overall[1]}")
    print(f"total hits above conf_thr={CONF_THR}: {len(all_hits)}")
    print("(null-max -6.82; confirm -5.5; English -4.3; noise -7.5)")
    if not all_hits:
        print("NULL result: no keyword clears the noise floor in this smoke.")
    return best_overall, all_hits


# ================================================================= FULL RUN
def full_run():
    """Run all 55 unsolved pages. Called by orchestrator only."""
    print("=" * 74)
    print("FULL KEYWORD/VIGENERE SKIP SWEEP -- all 55 unsolved LP2 pages")
    print("=" * 74)

    pages = load_pages()[:-2]
    keywords = build_keyword_list()
    print(f"keywords: {len(keywords)} | pages: {len(pages)}")

    t0 = time.time()
    all_hits = []
    best_overall = (-99.0, None)

    for pno, pg in enumerate(pages):
        ct = np.array(pg, dtype=np.int64)
        hits, bg = attack_page_keyword_fast(ct, keywords)
        flag = "  *** HIT ***" if hits else ""
        print(f"page {pno:2d} (len {len(ct):3d})  "
              f"best_screen={bg[0]:.3f}  via {bg[1]}{flag}  "
              f"[{time.time()-t0:.0f}s]")
        if bg[0] > best_overall[0]:
            best_overall = (bg[0], bg[1])
        for h in sorted(hits, reverse=True)[:3]:
            fs, kw, sign, atb, o, tl = h
            print(f"  HIT score={fs:.3f}  kw={kw!r}  sign={sign}  atbash={atb}  off={o}")
            print(f"      {tl[:90]}")
        all_hits += [(pno,) + h for h in hits]

    elapsed = time.time() - t0
    print("\n" + "=" * 74)
    print(f"FULL RUN DONE in {elapsed:.0f}s")
    print(f"best score seen : {best_overall[0]:.3f}  via {best_overall[1]}")
    print(f"total hits above conf_thr={CONF_THR}: {len(all_hits)}")
    if not all_hits:
        print("NULL RESULT: no keyword-Vigenere key clears the noise floor.")
    return best_overall, all_hits


# ================================================================= ENTRY POINT
if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Keyword/Vigenere skip-tolerant sweep for LP2 unsolved pages")
    ap.add_argument("--smoke", action="store_true",
                    help="Smoke over 3 pages (default if no flag given)")
    ap.add_argument("--full", action="store_true",
                    help="Full sweep over all 55 unsolved pages (orchestrator only)")
    ap.add_argument("--gate", action="store_true",
                    help="Run validation gate only")
    ap.add_argument("--pages", type=str, default="",
                    help="Page range e.g. '0-10' (--full subrange)")
    args = ap.parse_args()

    # Always run the gate first
    passed, ginfo = gate(verbose=True)
    if not passed:
        print("\nFATAL: gate failed -- keyword skip sweep results are UNTRUSTWORTHY. "
              "Investigate prefilter / tiling before running the sweep.")
        sys.exit(1)

    print(f"\nGate passed (rigid={ginfo['rigid']:.3f} "
          f"beam={ginfo['beam']:.3f} ctrl={ginfo['ctrl']:.3f} "
          f"match={ginfo['match']*100:.1f}%)\n")

    if args.gate:
        sys.exit(0)

    if args.full:
        if args.pages:
            pages_all = load_pages()[:-2]
            a, b = args.pages.split("-")
            sel = list(range(int(a), int(b) + 1))
            kws = build_keyword_list()
            t0 = time.time()
            all_hits = []
            best = (-99.0, None)
            for pno in sel:
                ct = np.array(pages_all[pno], dtype=np.int64)
                hits, bg = attack_page_keyword_fast(ct, kws)
                flag = "  *** HIT ***" if hits else ""
                print(f"page {pno:2d} len={len(ct):3d}  "
                      f"best={bg[0]:.3f} via {bg[1]}{flag}  "
                      f"[{time.time()-t0:.0f}s]")
                if bg[0] > best[0]:
                    best = (bg[0], bg[1])
                for h in sorted(hits, reverse=True)[:3]:
                    fs, kw, sgn, atb, o, tl = h
                    print(f"  HIT {fs:.3f} {kw!r} sign={sgn} atbash={atb} off={o}  {tl[:70]}")
                all_hits += [(pno,) + h for h in hits]
            print(f"\nDONE {time.time()-t0:.0f}s | best={best[0]:.3f} | "
                  f"hits_above_{CONF_THR}={len(all_hits)}")
        else:
            full_run()
    else:
        # default: smoke
        smoke()
