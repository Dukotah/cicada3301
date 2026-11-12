"""Round 44 lane D1 - joint two-plaintext (depth-2) decoder. See PREREG.md.

A cell fixes a plaintext encoding: its symbols, the value each symbol takes in Z_29, and how an
English word is spelled in it. The decoder walks the aligned pair of pages; at each position a
candidate symbol a for the first page forces b with val[b] = val[a] - D (mod 29) on the second.
Paths are scored by one 5-gram character model per cell that carries the word boundary as a symbol.
"""
import glob
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "A0-fresh-eyes-audit"))
import lp2  # noqa: E402

TR = lp2.TR
ORDER = 5
HELD_OUT = ("melville_moby_dick", "emerson_essays_first_series", "ovid_metamorphoses",
            "ovid_metamorphoses_viii_xv")
NOT_ENGLISH = ("virgil_aeneid_latin",)
_SINGLE = {t: i for i, t in enumerate(TR) if len(t) == 1}
_FOLD = {"K": "C", "V": "U", "Z": "S", "Q": "C"}
_MULTI = sorted(((t, i) for i, t in enumerate(TR)), key=lambda x: -len(x[0]))


class Cell:
    """A plaintext encoding: nsym symbols, val[sym] in Z_29, spell(word) -> list of symbol ids."""

    def __init__(self, name):
        self.name = name
        if name == "G-LW":
            letters = sorted(_SINGLE, key=_SINGLE.get)
            self.val = [_SINGLE[c] for c in letters]
            lut = {c: k for k, c in enumerate(letters)}
            self.spell = lambda w: [lut[_FOLD.get(c, c)] for c in w]
        elif name == "A-LW":
            self.val = list(range(26))
            self.spell = lambda w: [ord(c) - 65 for c in w]
        elif name == "G-MG":
            self.val = list(range(29))
            self.spell = _spell_multigraph
        else:
            raise ValueError(name)
        self.nsym = len(self.val)
        self.V = self.nsym + 1          # + word boundary
        self.SP = self.nsym
        self.sym_of_val = {v: s for s, v in enumerate(self.val)}

    def encode_text(self, text):
        """Upper-case A-Z text with spaces -> (symbol ids, word-start flags)."""
        syms, starts = [], []
        for w in text.split():
            s = self.spell(w)
            for k, x in enumerate(s):
                syms.append(x)
                starts.append(k == 0)
        return syms, starts


def _spell_multigraph(w):
    w = "".join(_FOLD.get(c, c) for c in w)
    out, i = [], 0
    while i < len(w):
        if w.startswith("ING", i):
            out.append(TR.index("NG")); i += 3; continue
        if w.startswith("IO", i):
            out.append(TR.index("IA")); i += 2; continue
        for t, k in _MULTI:
            if w.startswith(t, i):
                out.append(k); i += len(t); break
        else:
            i += 1
    return out


def clean(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    t = t[int(len(t) * 0.15):int(len(t) * 0.85)].upper()      # drop licence head and tail
    return re.sub(r"[^A-Z]+", " ", t).strip()


def corpus_files():
    keys = os.path.join(lp2.LP, "data", "keys")
    fs = sorted(glob.glob(os.path.join(keys, "armada18", "*.txt")) + glob.glob(os.path.join(keys, "armada19", "*.txt")))
    name = lambda f: os.path.basename(f)[:-4]
    train = [f for f in fs if name(f) not in HELD_OUT and name(f) not in NOT_ENGLISH]
    held = [f for f in fs if name(f) in HELD_OUT[:3]]
    return train, held


def train_lm(cell, files, max_chars=30_000_000):
    """Interpolated Witten-Bell 5-gram over the cell's symbols + word boundary. Returns log P[ctx, sym]."""
    V, SP = cell.V, cell.SP
    stream = [SP] * (ORDER - 1)
    for f in files:
        for w in clean(f).split():
            stream.extend(cell.spell(w)); stream.append(SP)
        if len(stream) > max_chars:
            break
    s = np.asarray(stream, dtype=np.int64)
    p = np.full((1, V), 1.0 / V)
    for o in range(1, ORDER + 1):
        code = np.zeros(len(s) - o + 1, dtype=np.int64)
        for k in range(o):
            code = code * V + s[k:len(s) - o + 1 + k]
        cnt = np.bincount(code, minlength=V ** o).reshape(V ** (o - 1), V).astype(np.float64)
        tot = cnt.sum(axis=1, keepdims=True)
        typ = (cnt > 0).sum(axis=1, keepdims=True)
        lower = p[np.arange(V ** (o - 1)) % p.shape[0]]
        denom = tot + typ
        p = np.where(denom > 0, (cnt + typ * lower) / np.maximum(denom, 1), lower)
    return np.log(p).astype(np.float32), len(s)


def decode(cell, lm, D, startA, startB, beam=50_000, want_path=True):
    """Joint beam decode. D[i] = (A_i - B_i) mod 29 on values. Returns (score per position, symsA, symsB)."""
    V, SP, S = cell.V, cell.SP, cell.nsym
    M = V ** (ORDER - 1)
    val = np.asarray(cell.val)
    sym_of_val = np.full(29, -1, dtype=np.int64)
    for v, k in cell.sym_of_val.items():
        sym_of_val[v] = k
    start_code = 0
    for _ in range(ORDER - 1):
        start_code = start_code * V + SP
    cA = np.array([start_code], dtype=np.int64); cB = cA.copy(); sc = np.zeros(1, dtype=np.float32)
    back, picks = [], []
    n = len(D)
    for i in range(n):
        if startA[i] and i > 0:
            sc = sc + lm[cA, SP]; cA = (cA * V + SP) % M
        if startB[i] and i > 0:
            sc = sc + lm[cB, SP]; cB = (cB * V + SP) % M
        bs = sym_of_val[(val - D[i]) % 29]                  # symbol forced on page B by each a
        ok = bs >= 0
        cand = sc[:, None] + lm[cA][:, :S] + np.where(ok[None, :], lm[cB][:, np.where(ok, bs, 0)], -1e9)
        flat = cand.ravel()
        if flat.size > beam:
            keep = np.argpartition(flat, -beam)[-beam:]
        else:
            keep = np.arange(flat.size)
        keep = keep[flat[keep] > -1e8]
        par, a = keep // S, keep % S
        sc = flat[keep]
        cA = (cA[par] * V + a) % M
        cB = (cB[par] * V + bs[a]) % M
        if want_path:
            back.append(par.astype(np.int32)); picks.append(a.astype(np.int8))
    best = int(np.argmax(sc))
    score = float(sc[best]) / n
    if not want_path:
        return score, None, None
    symsA = [0] * n
    k = best
    for i in range(n - 1, -1, -1):
        symsA[i] = int(picks[i][k]); k = int(back[i][k])
    symsB = [cell.sym_of_val[(cell.val[a] - int(D[i])) % 29] for i, a in enumerate(symsA)]
    return score, symsA, symsB


def render(cell, syms, starts):
    """Symbols -> readable text with word breaks."""
    if cell.name == "A-LW":
        name = lambda s: chr(65 + s)
    elif cell.name == "G-LW":
        letters = sorted(_SINGLE, key=_SINGLE.get); name = lambda s: letters[s]
    else:
        name = lambda s: TR[s]
    out = []
    for s, st in zip(syms, starts):
        if st and out:
            out.append(" ")
        out.append(name(s))
    return "".join(out)
