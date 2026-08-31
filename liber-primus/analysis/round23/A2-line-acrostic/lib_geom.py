"""Round 23 Lane A2 — printed-line/word geometry extractor for the self-embedded read.

R22-A ran the self-embedded acrostic recognizer ONLY on the concatenated
transliteration (no line geometry) and returned a clean control-validated NULL.
A2's sole new input is the REAL printed-line + word geometry, which R22-A could
not build. This module builds it.

GEOMETRY SOURCE (cited, cheapest reliable):
  data/scream314_lp.md -- the SAME transcription tests/validate.py trusts
  (via src/lp/corpus.py). Its per-page runes block preserves the page-image
  line breaks (one text line = one printed line) AND word boundaries (the '•'
  rune-word separator). No separate/looser transcription (e.g. data/relikd) is
  used, so the geometry is guaranteed consistent with the validated decrypt.

PLAINTEXT ON THE TRUE LINES: we decrypt each page with the SAME transform
tests/validate.py reproduces (simple brute for the 3 simple pages; vigenere +
interrupter beam for the 2 vigenere pages), but instead of flattening, we keep
per-rune bookkeeping of (line index, word index). Interrupter runes (null ᚠ)
emit nothing and do not advance the keystream, exactly as in solve.decode.

The acrostic UNIT is the first *rune* of each printed line / word (doctrine
mechanics R5: select on runes, then map to transliteration for scoring). A rune
maps to a 1- or 2-letter transliteration token; the acrostic string is the
concatenation of those tokens.
"""
import os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
from lp import corpus, ciphers, solve, gematria as gp, score as _score  # noqa

# The 5 rig-reproduced solved pages, in the order tests/validate.py lists them.
PAGES = [
    ("Runes - 01.jpg", "simple",   None),
    ("05.jpg",         "simple",   None),
    ("06.jpg",         "simple",   None),
    ("03.jpg",         "vigenere", "DIVINITY"),
    ("14.jpg",         "vigenere", "FIRFUMFERENFE"),
]

_ALPHA = re.compile(r"[^A-Z]")
_SCORER = None


def scorer():
    global _SCORER
    if _SCORER is None:
        _SCORER = _score.default()
    return _SCORER


def _best_simple(idxs):
    """Return (atbash, k, sign) of the best-scoring simple transform (matches
    tests/validate.py::brute_simple)."""
    sc = scorer()
    best = None
    for atb in (False, True):
        base = ciphers.atbash_indices(idxs) if atb else idxs
        for k in range(gp.N):
            for sign in (-1, +1):
                out = [(c + sign * k) % gp.N for c in base]
                s = sc.score_norm(gp.indices_to_translit(out))
                if best is None or s > best[0]:
                    best = (s, atb, k, sign)
    return best[1], best[2], best[3]


def _tokens_by_line_word(raw_runes, decode_fn):
    """Walk the raw runes field (which contains ᚠ-᛿ runes, '•' word seps, and
    newlines), decrypt each rune via decode_fn(occurrence_state) and bucket the
    emitted transliteration token into (line, word).

    decode_fn is a stateful callable: given the rune char it returns either a
    transliteration token (str) for an emitted rune, or None for a null
    interrupter (emit nothing, key not advanced). It must manage its own key
    position and interrupter accounting.

    Returns: list of lines; each line is a list of words; each word is a list of
    per-rune tokens (strings). Empty words/lines are dropped.
    """
    lines = []
    cur_line = []
    cur_word = []
    for ch in raw_runes:
        if ch == "\n":
            if cur_word:
                cur_line.append(cur_word)
                cur_word = []
            if cur_line:
                lines.append(cur_line)
                cur_line = []
            continue
        if ch == "•":  # '•' word separator
            if cur_word:
                cur_line.append(cur_word)
                cur_word = []
            continue
        if ch in gp.RUNE_TO_IDX:
            tok = decode_fn(ch)
            if tok is not None:
                cur_word.append(tok)
            continue
        # any other char (stray space, punctuation) is ignored
    if cur_word:
        cur_line.append(cur_word)
    if cur_line:
        lines.append(cur_line)
    return lines


def _simple_decoder(atbash, k, sign):
    def dec(ch):
        c = gp.RUNE_TO_IDX[ch]
        if atbash:
            c = (gp.N - 1) - c
        p = (c + sign * k) % gp.N
        return gp.IDX_TO_TRANS[p]
    return dec


def _vigenere_decoder(stream, sign, interrupter_set):
    """Stateful decoder replicating solve.decode: null ᚠ at an occurrence-index
    in interrupter_set emits nothing and does NOT advance the key."""
    state = {"j": 0, "f": 0}

    def dec(ch):
        if ch == gp.INTERRUPTER:
            if state["f"] in interrupter_set:
                state["f"] += 1
                return None  # null: no emit, no key advance
            state["f"] += 1
        c = gp.RUNE_TO_IDX[ch]
        p = (c + sign * stream[state["j"]]) % gp.N
        state["j"] += 1
        return gp.IDX_TO_TRANS[p]

    return dec


def decode_page_geometry(label, kind, key):
    """Return (lines, meta) where lines is a list of lines -> words -> per-rune
    tokens, decrypted with the validated transform for this page."""
    page = corpus.page_by_label(label)
    raw = page["runes"]
    runes_only = [c for c in raw if c in gp.RUNE_TO_IDX]
    idxs = gp.runes_to_indices(runes_only)

    if kind == "simple":
        atb, k, sign = _best_simple(idxs)
        dec = _simple_decoder(atb, k, sign)
        meta = {"method": f"{'atbash+' if atb else ''}shift{sign*k:+d}"}
    else:
        stream = ciphers.repeat_key(gp.keyword_to_indices(key), len(idxs))
        res = solve.find_interrupters(runes_only, stream, sign=-1,
                                      beam_width=500, scorer=scorer())
        interrupter_set = set(res["interrupters"])
        dec = _vigenere_decoder(stream, -1, interrupter_set)
        meta = {"method": f"vigenere {key}",
                "interrupters": sorted(interrupter_set)}

    lines = _tokens_by_line_word(raw, dec)
    meta["label"] = label
    meta["n_lines"] = len(lines)
    return lines, meta


def load_all_pages():
    """Return list of (label, meta, lines) for the 5 solved pages, book order."""
    out = []
    for label, kind, key in PAGES:
        lines, meta = decode_page_geometry(label, kind, key)
        out.append((label, meta, lines))
    return out


# ---------------------------------------------------------------- flatten helpers

def page_flat_letters(lines):
    """Concatenate all tokens of a page into an A-Z letter string (sanity vs
    validate.py)."""
    s = "".join(tok for line in lines for word in line for tok in word)
    return _ALPHA.sub("", s.upper())


# ---------------------------------------------------------------- acrostic reads

def line_first_tokens(lines):
    """First rune-token of each printed line."""
    return [line[0][0] for line in lines if line and line[0]]


def line_last_tokens(lines):
    """Last rune-token of each printed line."""
    return [line[-1][-1] for line in lines if line and line[-1]]


def word_first_tokens(lines):
    """First rune-token of each word (all words, all lines, book order)."""
    return [word[0] for line in lines for word in line if word]


def word_last_tokens(lines):
    """Last rune-token of each word."""
    return [word[-1] for line in lines for word in line if word]


def tokens_to_letters(tokens):
    return _ALPHA.sub("", "".join(tokens).upper())
