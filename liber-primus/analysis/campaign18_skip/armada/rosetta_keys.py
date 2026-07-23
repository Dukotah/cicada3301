"""ROSETTA key GENERATORS -- LP2 key hypotheses that obey the LP1 author's
proven keying discipline, each returning a keystream (list of Gematria indices
0..28) ready to feed the Campaign-XVIII skip-tolerant beam decoder.

WHY THIS FILE EXISTS
--------------------
LP1 (the SOLVED pages) is our only ground truth for how Cicada 3301 chose keys.
Characterised precisely from data/scream314_lp.md + tests/validate.py:

  DECODE RELATION (all solved pages)   p = (c - k) mod 29     i.e. sign=-1.
    - Vigenere pages call it "Shift UP forward Gematria" (key ADDED at
      encipher, so SUBTRACTED at decode -> sign=-1).      [verified pg03]
    - phi(prime) page calls it "Shift DOWN forward Gematria"; the phi stream
      itself is what changes, not the sign -> still sign=-1.  [verified pg73]
    - Atbash/"reversed Gematria" pages reflect the rune BEFORE the shift:
      c -> (28 - c), then p = (c' - k).                    [pg01, pg06-09]

  KEYS USED, in author's own words:
    pg03/04  Vigenere keyword  DIVINITY, "shift up forward Gematria",
             CONTINUOUS across the two pages ("Continuation of key").
    pg14/15  Vigenere keyword  FIRFUMFERENFE (= CIRCUMFERENCE with C/K->F and
             U->nothing quirk), continuous across the two pages.
    pg06-09  Atbash then Caesar SHIFT 3 DOWN, continuous over 4 pages.
    pg73     phi(prime) keystream = (prime_i - 1) mod 29, prime index from 0
             (prime=2 -> phi=1). "Shift down forward Gematria."   VERIFIED:
             decodes AEJOESR -> ANEND exactly.
    pg01/05/74 plain Atbash / default-Gematria substitution (period-1 key=0).

  INTERRUPTER RULE (the load-bearing crossover to LP2):
    the rune  F / ᚠ  (index 0) can be a NULL: removed from plaintext AND it does
    NOT advance the key. On pg73 the note is explicit -- "Every clear text F is
    an ᚠ and needs to be skipped." This is a KEY-SKIP mechanic, exactly the
    desync the Campaign-XVIII decoder tracks. The LP2 doublet-suppression filter
    is the SAME family of mechanic (a plaintext-conditioned key skip), so LP2
    keys plausibly come from the SAME generators, just decoded skip-aware.

DISCIPLINE SUMMARY (what a valid LP2 key hypothesis must respect)
  1. sign = -1 always (never flip the decode direction).
  2. keys are THEMATIC English words/phrases OR number-theoretic streams over
     the primes / totient -- never arbitrary bytes.
  3. keys run CONTINUOUSLY across consecutive pages (do not reset per page
     unless the page has its own **Key:** note).
  4. atbash is an OPTIONAL pre-shift reflection, applied by the CALLER on the
     ciphertext, not baked into the key.
  5. a small constant Caesar shift (the "+3") may be stacked on top of any key.

HOW TO USE (all generators return list[int], mod 29)
  from rosetta_keys import KEYSTREAMS, key_divinity_run, key_phi_prime, ...
  K = key_phi_prime(4000)                 # a long keystream
  import numpy as np
  from sweep import beam                  # skip-aware beam
  pi = beam(np.array(page_ct, np.int64), np.array(K, np.int64), -1, offset, L, 400)
  # or, for a running-key text: idx_to_trans, beam_decode from skipdecode

Every generator is deterministic and length-parametrised so the orchestrator can
size it to (offset + page_len + max_skip*page_len) for worst-case skipping.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp            # noqa: E402

N = gp.N  # 29


# --------------------------------------------------------------------------
# number-theoretic primitives (mirror lp.ciphers but self-contained + longer)
# --------------------------------------------------------------------------
def _primes(count):
    out, cand = [], 2
    while len(out) < count:
        if all(cand % p for p in out if p * p <= cand):
            out.append(cand)
        cand += 1
    return out


def _totient(n):
    r, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r


def _kw(word):
    """Latin keyword -> Gematria indices (greedy multi-letter runes)."""
    return gp.keyword_to_indices(word)


def _repeat(key, length):
    return [key[i % len(key)] for i in range(length)] if key else [0] * length


# --------------------------------------------------------------------------
# A. NUMBER-THEORETIC KEYSTREAMS  (LP1 pg73 discipline: phi(prime) shift)
#    NB: these were tried RIGID before and died; the point here is they were
#    NEVER tried SKIP-AWARE. A deterministic stream desyncs from the plaintext
#    under key-skip exactly like a running key, so a rigid null is UNSOUND.
# --------------------------------------------------------------------------
def key_phi_prime(length, start=0):
    """pg73's exact key: (prime_i - 1) mod 29 = phi(prime_i). The single most
    author-authentic number-theoretic stream."""
    ps = _primes(length + start)
    return [(ps[i + start] - 1) % N for i in range(length)]


def key_primes(length, start=0):
    """Consecutive primes mod 29 ('the primes are sacred')."""
    ps = _primes(length + start)
    return [ps[i + start] % N for i in range(length)]


def key_totient_int(length, start=2):
    """Euler totient of consecutive INTEGERS mod 29 (the 'totient function is
    sacred' variant, distinct from totient-of-primes)."""
    out, n = [], start
    while len(out) < length:
        out.append(_totient(n) % N)
        n += 1
    return out


def key_phi_prime_minus1(length, start=0):
    """(phi(prime_i) - 1) = (prime_i - 2) mod 29 -- the 'A KOAN' 0x page is
    documented with a (totient(p)-1) flavour; expose it explicitly."""
    ps = _primes(length + start)
    return [(ps[i + start] - 2) % N for i in range(length)]


# --------------------------------------------------------------------------
# B. THEMATIC-KEYWORD KEYSTREAMS  (LP1 pg03/14 discipline: Vigenere keyword)
#    Continuous repeating keyword. These follow the EXACT mechanic of the two
#    solved Vigenere runs; only the WORD is the hypothesis.
# --------------------------------------------------------------------------
# thematic words in the author's demonstrated vocabulary (LP1 plaintext +
# data/keys/thematic.txt). Multi-word phrases are concatenated (no spaces),
# matching how DIVINITY / CIRCUMFERENCE were keyed.
THEMATIC_WORDS = [
    "DIVINITY", "CIRCUMFERENCE", "INSTAR", "EMERGENCE", "INSTAREMERGENCE",
    "PILGRIM", "PILGRIMAGE", "SACRED", "PRIMES", "PRIME", "TOTIENT", "WISDOM",
    "KOAN", "PARABLE", "MOBIUS", "CICADA", "LIBERPRIMUS", "WELCOME", "ADHERE",
    "PRESERVE", "ENLIGHTENMENT", "CONSUMPTION", "PRESERVATION", "ADHERENCE",
    "DECEPTION", "SHADOWS", "SELFRELIANCE", "EPIPHANY", "TRUTH", "REALITY",
    "ILLUSION", "CONSCIOUSNESS", "WITHIN", "SACRIFICE", "DISCOVER", "JOURNEY",
    "ANEND", "AWAKENING", "THEPRIMESARESACRED", "THETOTIENTFUNCTIONISSACRED",
    "DIVINITYWITHIN", "SEEKWITHIN", "FINDTHETRUTH", "ALLTHINGSTHREE",
    "THEINSTAR", "ANINSTRUCTION", "AKOAN", "LOSSOFDIVINITY",
]


def key_thematic(word, length):
    """Repeating thematic keyword, LP1 Vigenere mechanic. `word` may be any
    THEMATIC_WORDS entry or a novel thematic guess."""
    return _repeat(_kw(word), length)


def all_thematic_keystreams(length):
    """dict name -> keystream for every thematic word."""
    return {f"kw:{w}": key_thematic(w, length) for w in THEMATIC_WORDS}


# --------------------------------------------------------------------------
# C. PER-PAGE KEY SCHEDULES DERIVED FROM PAGE NUMBER
#    LP1 never numbered its keys, BUT the totient/prime theme invites a
#    page-indexed schedule: key for page p = phi(p)-th thematic word, or a
#    Caesar shift of phi(page)/prime(page). This is the 'thematic schedule'
#    hypothesis, expressed as a callable of page index.
# --------------------------------------------------------------------------
def key_page_caesar(page_num, length, base_key=None, mode="phi"):
    """A base key (default phi(prime)) with a per-page CONSTANT Caesar offset
    derived from the page number: shift = phi(page)  or  prime(page)  mod 29.
    Mirrors the LP1 '+3' constant-shift stack but makes the constant page-aware.
    """
    if base_key is None:
        base = key_phi_prime(length)
    else:
        base = _repeat(base_key, length) if len(base_key) < length else base_key[:length]
    if mode == "phi":
        shift = _totient(max(page_num, 1)) % N
    elif mode == "prime":
        shift = _primes(page_num + 1)[page_num] % N
    else:  # linear page number
        shift = page_num % N
    return [(k + shift) % N for k in base]


def key_page_thematic(page_num, length):
    """Thematic-word SCHEDULE: page p uses THEMATIC_WORDS[phi-ish(p)]. Lets a
    single sweep assign a different-but-principled keyword to each page."""
    w = THEMATIC_WORDS[(_totient(max(page_num, 1))) % len(THEMATIC_WORDS)]
    return key_thematic(w, length)


# --------------------------------------------------------------------------
# D. CAESAR-CONSTANT + STACK  (LP1 pg06-09 discipline: shift 3, atbash pre)
#    A pure constant keystream. Atbash is applied by the CALLER to the CT.
# --------------------------------------------------------------------------
def key_constant(shift, length):
    """Every position = `shift`. Reproduces the LP1 '+3' Caesar pages when the
    caller atbash-reflects the ciphertext first."""
    return [shift % N] * length


def all_constant_keystreams(length):
    return {f"caesar:{s}": key_constant(s, length) for s in range(1, N)}


# --------------------------------------------------------------------------
# E. RUNNING KEY FROM A SOLVED-PAGE TEXT  (self-referential, LP-thematic)
#    LP1 solved plaintext is a natural 'text the solver already has'. Use the
#    decoded LP1 English as a running key over LP2. (page-on-page RUNIC keying
#    is dead per ledger; this is the decoded-ENGLISH-as-running-key variant,
#    which is distinct and thematically on-brand.)
# --------------------------------------------------------------------------
def _solved_plaintext_english():
    """Reconstruct the LP1 decoded English we hold as ground truth. Pulled from
    the koan + welcome + circumference solves documented in scream314_lp.md."""
    return (
        "AWARNINGBELIEVENOTHINGFROMTHISBOOKEXCEPTWHATYOUKNOWTOBETRUE"
        "TESTTHEKNOWLEDGEFINDYOURTRUTHEXPERIENCEYOURDEATH"
        "AKOANAMANDECIDEDTOGOANDSTUDYWITHAMASTERHEWENTTOTHEDOOROFTHEMASTER"
        "WHOAREYOUWHOWISHESTOSTUDYHEREASKEDTHEMASTER"
        "WELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALLTHINGS"
        "ITISNOTANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHEREITISANECESSARYONE"
        "THELOSSOFDIVINITYTHECIRCUMFERENCEPRACTICESTHREEBEHAVIOURS"
        "THEPRIMESARESACREDTHETOTIENTFUNCTIONISSACRED"
        "ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTOITISTHEDUTYOFEVERYPILGRIM"
    )


def key_running_solved(length, offset=0):
    """LP1 decoded English as a running key (cycled to length)."""
    idx = gp.keyword_to_indices(_solved_plaintext_english())
    if not idx:
        return [0] * length
    return [idx[(offset + i) % len(idx)] for i in range(length)]


# --------------------------------------------------------------------------
# REGISTRY -- everything the orchestrator can sweep. Values are (kind, fn):
#   kind 'stream'  : fn(length) -> keystream, feed straight to beam as key.
#   kind 'atbash'  : same, but caller must atbash the ciphertext first.
# Thematic keywords are expanded by all_thematic_keystreams at call time.
# --------------------------------------------------------------------------
def build_registry(length):
    reg = {}
    # A. number theory (skip-aware is the novel part)
    reg["phi_prime"] = ("stream", key_phi_prime(length))
    reg["phi_prime_atbash"] = ("atbash", key_phi_prime(length))
    reg["primes"] = ("stream", key_primes(length))
    reg["totient_int"] = ("stream", key_totient_int(length))
    reg["phi_prime_minus1"] = ("stream", key_phi_prime_minus1(length))
    # B. thematic keywords (both plain and atbash pre-reflection)
    for name, ks in all_thematic_keystreams(length).items():
        reg[name] = ("stream", ks)
        reg[name + "|atbash"] = ("atbash", ks)
    # D. constant Caesar (atbash variant = the pg06-09 mechanic)
    for name, ks in all_constant_keystreams(length).items():
        reg[name + "|atbash"] = ("atbash", ks)
    # E. running key from solved LP1 English
    reg["running_solved"] = ("stream", key_running_solved(length))
    return reg


# convenient flat dict of the highest-prior hypotheses only (for a fast pass)
def high_prior(length):
    reg = {}
    reg["phi_prime"] = key_phi_prime(length)
    reg["primes"] = key_primes(length)
    reg["totient_int"] = key_totient_int(length)
    reg["running_solved"] = key_running_solved(length)
    for w in ("DIVINITY", "CIRCUMFERENCE", "INSTAR", "EMERGENCE",
              "THEPRIMESARESACRED", "DIVINITYWITHIN", "PILGRIM", "MOBIUS"):
        reg[f"kw:{w}"] = key_thematic(w, length)
    return reg


if __name__ == "__main__":
    # tiny self-test: pg73 phi(prime) must reproduce 'ANEND'
    ct = gp.runes_to_indices("ᚫᛄᛟᛋᚱ")          # AEJOESR
    K = key_phi_prime(len(ct))
    out = [(c - K[i]) % N for i, c in enumerate(ct)]
    got = gp.indices_to_translit(out)
    print("pg73 phi(prime) self-test:", got, "OK" if got == "ANEND" else "FAIL")
    print("registry size @L=200:", len(build_registry(200)))
    print("high_prior keys:", list(high_prior(50).keys()))
