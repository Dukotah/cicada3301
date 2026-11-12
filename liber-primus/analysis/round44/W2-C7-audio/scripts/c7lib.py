"""R44 W2-C7 shared glue — audio reductions beyond literal bytes, F5b-T harness pattern.

Standing instrument throughout: panel-R36 via round19/I2 adjudicate (Panel + adjudicate_batch),
bars_v3 'free' at the PREREG-fixed battery family sizes.  Pure python/numpy downstream of the
raw PCM bytes; ffmpeg (local, no network) is the declared PCM decoder (PREREG section 0).
"""
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.abspath(os.path.join(HERE, ".."))
LP = os.path.abspath(os.path.join(CELL, "..", "..", ".."))
REPO = os.path.abspath(os.path.join(LP, ".."))
for p in ("analysis", "src", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))
from lp import gematria as gp                      # noqa: E402
from run_stats import load_pages                   # noqa: E402
import adjudicate as A                             # noqa: E402
import bars_v3 as B                                # noqa: E402

N = gp.N                                           # 29
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
FREE_LS = (120, 240, 400, 729)
MIN_ONESHOT = 60
STRIDE = 4096                                      # PREREG battery-P offset stride
LADDER = list(range(8))

# PREREG section 6 — fixed battery family sizes
N_BAR_S = 6e7
N_BAR_P = 2e7

ART = {
    "761": os.path.join(REPO, "puzzles", "2013", "artifacts", "761_The-Instar-Emergence.mp3"),
    "onion5": os.path.join(REPO, "corpus", "A-primary-artifacts", "2014", "ia_onion5_data.mp3"),
}
SHA = {
    "761": "83008217439110c3b824898af73b99cb2cf0657dda88cb363c3aa34a4ec0a460",
    "onion5": "1ce3839b4a62462d9009c4469acc189b523e1bdcf338cb49cda1cd7bb4efffc6",
}

MAPPINGS = {"m1": lambda k: int(k) % N,
            "m2": lambda k: (5 * int(k)) % N,
            "m3": lambda k: gp.PRIMES[int(k) % N] % N}
CFGS = ["vigm", "vigp", "beau", "vigm_atb", "vigp_atb", "beau_atb"]


def sha256(path_or_bytes):
    h = hashlib.sha256()
    if isinstance(path_or_bytes, bytes):
        h.update(path_or_bytes)
    else:
        with open(path_or_bytes, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    return h.hexdigest()


def ffmpeg_pcm(path, fmt):
    """Decode MP3 -> mono 44.1k raw PCM bytes via the declared local decoder (PREREG section 0)."""
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "44100", "-f", fmt, "-"]
    out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout
    return cmd, out


def decode(c, K, cfg):
    """c, K broadcastable int arrays -> plaintext rune indices."""
    x = (N - 1) - c if cfg.endswith("_atb") else c
    base = cfg.split("_")[0]
    if base == "vigm":
        return (x - K) % N
    if base == "vigp":
        return (x + K) % N
    return (K - x) % N


def encipher(p, K, cfg):
    """Inverse of decode for the plants."""
    base = cfg.split("_")[0]
    if base == "vigm":
        x = (p + K) % N
    elif base == "vigp":
        x = (p - K) % N
    else:
        x = (K - p) % N
    return ((N - 1) - x) % N if cfg.endswith("_atb") else x


def free_bar(Nbar, L):
    cand = [x for x in FREE_LS if x <= L] or [120]
    return B.bar_v3(Nbar, max(cand), "free")


def minimal_period(a):
    """Smallest divisor-period p of array a (rotation dedup for mode R)."""
    a = np.asarray(a)
    n = len(a)
    for p in range(1, n):
        if n % p == 0 and np.array_equal(a[: n - p], a[p:]):
            return p
    return n


def to_idx(text):
    out = []
    for w in text.split():
        try:
            out.extend(gp.keyword_to_indices(w))
        except Exception:
            pass
    return out


PT1 = ("A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE "
       "FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED "
       "WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED SOME WISDOM THE PRIMES ARE SACRED "
       "THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS")
PT2 = ("WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR "
       "THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL "
       "STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY "
       "YOU WILL DISCOVER AN END TO SELF")
PT3 = ("SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL "
       "THAT YOU OWN AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY A KOAN DURING A LESSON THE MASTER "
       "EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID WHEN ASKED BY A STUDENT TO "
       "EXPLAIN WHAT THAT MEANT THE MASTER SAID IT IS A VOICE INSIDE YOUR HEAD")


# ---------------------------------------------------------------- battery S (short streams, dense)
def key_variants(seq):
    out = []
    for dname, s in (("fwd", list(seq)), ("rev", list(seq)[::-1])):
        for mname, fn in MAPPINGS.items():
            out.append((dname, mname, np.array([fn(k) for k in s], dtype=np.int64)))
    return out


def _collect(pm, preg, X, meta, L, bar, best, crossers):
    i = int(pm.argmax())
    if pm[i] > best["pmax"]:
        best.update(pmax=float(pm[i]), preg=int(preg[i]), L=int(L), bar=round(float(bar), 4),
                    decode=X[i].tolist(), **meta[i])
    for i in np.nonzero(pm >= bar)[0]:
        full = A.adjudicate(X[int(i)], pan=PAN)
        if not full["degenerate"] and full["pmax"] >= bar:
            crossers.append(dict(pmax=float(full["pmax"]), preg=full["preg"], L=int(L),
                                 bar=round(float(bar), 4), decode=X[int(i)].tolist(),
                                 **meta[int(i)]))


class _OneShotBuf:
    """Buffered one-shot accumulator: groups rows by decode length, flushes in big batches."""

    def __init__(self, nbar, best, crossers, max_elems=2.4e7):
        self.g = {}
        self.elems = 0
        self.nbar, self.best, self.crossers = nbar, best, crossers
        self.max_elems = max_elems
        self.count = 0

    def add(self, row, meta):
        rows, metas = self.g.setdefault(len(row), ([], []))
        rows.append(row)
        metas.append(meta)
        self.elems += len(row)
        if self.elems > self.max_elems:
            self.flush()

    def flush(self):
        for Lr, (rows, metas) in self.g.items():
            X = np.stack(rows, axis=0)
            barO = free_bar(self.nbar, Lr)
            for r0 in range(0, X.shape[0], 4096):
                sl = slice(r0, r0 + 4096)
                res = A.adjudicate_batch(X[sl], pan=PAN)
                self.count += X[sl].shape[0]
                _collect(res["pmax"], res["preg"], X[sl], metas[sl], Lr, barO,
                         self.best, self.crossers)
        self.g = {}
        self.elems = 0


def sweep_page_S(c, streams, nbar=N_BAR_S, chunk=1024):
    """Dense battery-S matrix over one page.  streams: dict name -> list[int]."""
    c = np.asarray(c, dtype=np.int64)
    Lp = len(c)
    best = {"pmax": -99.0}
    crossers = []
    count = 0
    buf = _OneShotBuf(nbar, best, crossers)
    for sname, seq in streams.items():
        if len(seq) == 0:
            continue
        for dname, mname, K in key_variants(seq):
            Lk = len(K)
            P = minimal_period(K)
            # mode R: every distinct rotation (minimal-period dedup), full page
            barR = free_bar(nbar, Lp)
            for r0 in range(0, P, chunk):
                rots = np.arange(r0, min(r0 + chunk, P))
                idx = (rots[:, None] + np.arange(Lp)[None, :]) % Lk
                Kmat = K[idx]
                rows, meta = [], []
                for cfg in CFGS:
                    rows.append(decode(c[None, :], Kmat, cfg))
                    meta.extend(dict(stream=sname, dir=dname, map=mname, cfg=cfg,
                                     mode="R", rot=int(r)) for r in rots)
                X = np.concatenate(rows, axis=0)
                res = A.adjudicate_batch(X, pan=PAN)
                count += X.shape[0]
                _collect(res["pmax"], res["preg"], X, meta, Lp, barR, best, crossers)
            # mode O: one-shot page-start aligned, only where the key runs out mid-page
            # (suffixes with Lk-rot >= Lp duplicate the mode-R decode -- PREREG section 8)
            for rot in range(max(0, Lk - Lp + 1), Lk - MIN_ONESHOT + 1):
                kk = K[rot:]
                for cfg in CFGS:
                    buf.add(decode(c[: Lk - rot], kk, cfg),
                            dict(stream=sname, dir=dname, map=mname, cfg=cfg,
                                 mode="O", rot=int(rot)))
    buf.flush()
    return count + buf.count, best, crossers


# ---------------------------------------------------------------- battery P (PCM pads, sampled)
def pad_offsets(Lk, Lp):
    offs = sorted(set(LADDER) | set(range(0, Lk, STRIDE)))
    return [o for o in offs if Lk - o >= Lp]        # full-page one-shot only (PREREG Q3)


def sweep_page_P(c, pads, nbar=N_BAR_P, chunk=256):
    """Sampled-offset battery-P matrix over one page.  pads: dict name -> int8 mod-29 array."""
    c = np.asarray(c, dtype=np.int64)
    Lp = len(c)
    bar = free_bar(nbar, Lp)
    best = {"pmax": -99.0}
    crossers = []
    count = 0
    for pname, pad in pads.items():
        for dname, Kfull in (("fwd", pad), ("rev", pad[::-1])):
            offs = pad_offsets(len(Kfull), Lp)
            for o0 in range(0, len(offs), chunk):
                ob = np.array(offs[o0:o0 + chunk], dtype=np.int64)
                idx = ob[:, None] + np.arange(Lp)[None, :]
                Kmat = Kfull[idx].astype(np.int64)
                rows, meta = [], []
                for cfg in CFGS:
                    rows.append(decode(c[None, :], Kmat, cfg))
                    meta.extend(dict(stream=pname, dir=dname, map="id", cfg=cfg,
                                     mode="O", rot=int(o)) for o in ob)
                X = np.concatenate(rows, axis=0)
                res = A.adjudicate_batch(X, pan=PAN)
                count += X.shape[0]
                _collect(res["pmax"], res["preg"], X, meta, Lp, bar, best, crossers)
    return count, best, crossers


def unsolved_pages():
    pages = load_pages()[:-2]
    assert len(pages) == 55
    return pages
