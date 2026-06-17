"""Interrupter-aware decryption + automatic interrupter search.

The Liber Primus interrupter rule (confirmed against the solved pages):
  - only ᚠ (index 0) is ever a null;
  - NOT every ᚠ is — it's a per-page subset the solver must discover;
  - a null ᚠ is removed (does not appear in readable plaintext) and does NOT
    advance the keystream; a non-null ᚠ is enciphered like any other rune.

`find_interrupters` runs a beam search over the ᚠ skip/keep decisions, scoring
partial plaintext with the quadgram model. Scales to any number of ᚠ (unlike
2^n brute force). This is the exact tool needed for unsolved pages once a key
hypothesis exists.
"""
from . import gematria as gp
from . import score as _score

N = gp.N


def _runes_only(text):
    return [c for c in text if c in gp.RUNE_TO_IDX]


def decode(runes_text, stream, sign=-1, atbash=False, interrupter_idx=frozenset()):
    """Decode using a precomputed positional `stream` (list of key values),
    skipping the ᚠ occurrences whose occurrence-index is in `interrupter_idx`.
    Returns (plaintext_letters, interrupter_positions_in_rune_stream).
    """
    runes = _runes_only(runes_text)
    out, j, f_seen, pos = [], 0, 0, []
    for n, ch in enumerate(runes):
        if ch == gp.INTERRUPTER:
            if f_seen in interrupter_idx:
                pos.append(n)
                f_seen += 1
                continue  # null: skip, do not advance key
            f_seen += 1
        c = gp.RUNE_TO_IDX[ch]
        if atbash:
            c = (N - 1) - c
        p = (c + sign * stream[j]) % N
        out.append(gp.IDX_TO_TRANS[p])
        j += 1
    return "".join(out), pos


def find_interrupters(runes_text, stream, sign=-1, atbash=False,
                     beam_width=400, scorer=None):
    """Beam search over ᚠ skip/keep decisions. Returns dict with best result."""
    scorer = scorer or _score.default()
    runes = _runes_only(runes_text)
    # Beam entries: (interrupter_set, j, decoded_list)
    beams = [(frozenset(), 0, [])]
    f_seen = 0
    for ch in runes:
        if ch == gp.INTERRUPTER:
            new = []
            for iset, j, dec in beams:
                # option A: null (skip, don't advance key, don't emit)
                new.append((iset | {f_seen}, j, dec))
                # option B: real rune (encipher)
                c = (N - 1) - 0 if atbash else 0
                p = (c + sign * stream[j]) % N
                new.append((iset, j + 1, dec + [gp.IDX_TO_TRANS[p]]))
            f_seen += 1
            # prune
            new.sort(key=lambda b: scorer.score("".join(b[2])), reverse=True)
            beams = new[:beam_width]
        else:
            c = gp.RUNE_TO_IDX[ch]
            if atbash:
                c = (N - 1) - c
            upd = []
            for iset, j, dec in beams:
                p = (c + sign * stream[j]) % N
                upd.append((iset, j + 1, dec + [gp.IDX_TO_TRANS[p]]))
            beams = upd
    beams.sort(key=lambda b: scorer.score("".join(b[2])), reverse=True)
    iset, j, dec = beams[0]
    text = "".join(dec)
    return {"interrupters": sorted(iset), "plaintext": text,
            "score_norm": scorer.score_norm(text), "n_interrupters": len(iset)}
