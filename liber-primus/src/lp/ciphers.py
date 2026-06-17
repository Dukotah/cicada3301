"""Cipher primitives for the Liber Primus, all over the 29-symbol Gematria Primus.

Everything works on indices 0..28. The two knobs that the validation gate tunes:
  - direction: decrypt = (C - K) mod 29  [default]  or  (C + K) mod 29
  - interrupters: the ᚠ rune can act as a NULL on some pages — passed through
    verbatim and NOT consumed by the keystream. We support both behaviours and
    let reproduction of known pages decide.

No cipher here assumes which key is "correct"; that is an empirical question
answered by tests/validate.py against the documented solved pages.
"""
from . import gematria as gp

N = gp.N


# ---------------------------------------------------------------- keystreams
def repeat_key(key_indices, length):
    """Vigenere: cycle a keyword's indices to `length`."""
    if not key_indices:
        return [0] * length
    return [key_indices[i % len(key_indices)] for i in range(length)]


def _sieve_primes(count):
    primes, cand = [], 2
    while len(primes) < count:
        if all(cand % p for p in primes if p * p <= cand):
            primes.append(cand)
        cand += 1
    return primes


def _totient(n):
    result, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            result -= result // p
        p += 1
    if m > 1:
        result -= result // m
    return result


def prime_stream(length, start=0):
    """Keystream of consecutive primes (mod 29). 'THE PRIMES ARE SACRED.'"""
    primes = _sieve_primes(length + start)
    return [primes[i + start] % N for i in range(length)]


def totient_stream(length, start=2):
    """Keystream from Euler's totient of consecutive integers (mod 29).
    The known 'A KOAN'/0x page solve uses (totient(p_i) - 1) on primes; we
    expose a few flavours and let the gate pick."""
    out, n = [], start
    while len(out) < length:
        out.append(_totient(n) % N)
        n += 1
    return out


def prime_totient_stream(length, start=0):
    """totient(prime_i) for consecutive primes — i.e. (prime_i - 1) mod 29.
    This is the documented keystream for several solved LP pages."""
    primes = _sieve_primes(length + start)
    return [(primes[i + start] - 1) % N for i in range(length)]


def running_key_indices(text):
    """Use another text's rune indices as a running key."""
    return gp.runes_to_indices(text)


# ---------------------------------------------------------------- core apply
def apply_stream_to_indices(idxs, stream, sign=-1):
    """sign=-1 decrypt (C-K), sign=+1 encrypt-style (C+K)."""
    return [(c + sign * stream[i]) % N for i, c in enumerate(idxs)]


def atbash_indices(idxs):
    """Reflect each index: i -> (N-1) - i."""
    return [(N - 1) - c for c in idxs]


# -------------------------------------------------- rune-level (interrupters)
def transform_runes(runes_text, stream_fn, sign=-1, interrupters=True,
                    atbash=False, interrupter_rune=gp.INTERRUPTER):
    """Decrypt a runic string, honouring interrupter runes.

    runes_text   : raw string; non-rune chars (•, whitespace, /) are preserved
                   as separators in the output transliteration.
    stream_fn    : callable(length)->list[int]; `length` is the number of
                   ENCIPHERED runes (interrupters excluded).
    interrupters : if True, `interrupter_rune` is passed through as its own
                   transliteration and does NOT advance the keystream.
    atbash       : apply Atbash reflection before the shift.

    Returns (plaintext_translit, plain_indices_only).
    """
    # First count enciphered runes to size the keystream.
    enc_positions = []
    for ch in runes_text:
        if ch in gp.RUNE_TO_IDX:
            if interrupters and ch == interrupter_rune:
                continue
            enc_positions.append(ch)
    stream = stream_fn(len(enc_positions))

    out_chars, plain_idx = [], []
    k = 0
    for ch in runes_text:
        if ch not in gp.RUNE_TO_IDX:
            out_chars.append(ch)  # keep separators
            continue
        if interrupters and ch == interrupter_rune:
            out_chars.append(gp.RUNE_TO_TRANS[ch])  # the literal F, uncounted
            continue
        c = gp.RUNE_TO_IDX[ch]
        if atbash:
            c = (N - 1) - c
        p = (c + sign * stream[k]) % N
        out_chars.append(gp.IDX_TO_TRANS[p])
        plain_idx.append(p)
        k += 1
    return "".join(out_chars), plain_idx


def vigenere_decrypt(runes_text, keyword, sign=-1, interrupters=True, atbash=False):
    key = gp.keyword_to_indices(keyword)
    return transform_runes(runes_text,
                           lambda L: repeat_key(key, L),
                           sign=sign, interrupters=interrupters, atbash=atbash)
