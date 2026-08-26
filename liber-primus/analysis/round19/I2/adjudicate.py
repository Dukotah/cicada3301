"""I2 — THE MULTI-REGISTER ADJUDICATOR.  One call, one record.

    from adjudicate import adjudicate, to_row, validate_row
    res = adjudicate(plain_idx)            # plain_idx = the decode's RUNE INDICES
    row = to_row(res, kid="seed=12345")    # the SWEEPROW every Phase 2 sweep persists

Why this exists
---------------
`round18/L7-redteam/RESULTS.md` §A: handed the CORRECT key the beam recovers 100 % of runes
for Latin, Old English, German, Welsh and half-vowel English, and the English quadgram
scorer then reports the result as noise, so the sweep records a miss.  Measured power at the
−5.5 bar: 0.33 Latin, 0.00 Welsh, 0.00 vowel-dropped English (where the correct key scores
BELOW a deliberately wrong one).  Doctrine R3 additionally makes four language-agnostic
statistics mandatory per sweep row; compliance was 0/15 and ~10^10 decodes are permanently
un-reinterpretable as a result.

What it computes
----------------
* `en`      the legacy `lp.score.Quadgram.score_norm`, UNCHANGED, so every Phase 2 number
            stays directly comparable with every published number in this repository
* `z[9]`    a nine-register rune-space trigram panel, each standardised against a
            pre-computed uniform-random-rune null at the decode's own length:
            EN_MODERN EN_KJV LP1_REAL LATIN OE DE CY EN_HALFVOWEL EN_NOVOWEL
* `pmax`    max over the panel;  `preg` its argmax register
* `pmax_ne` best NON-English panel z            <- doctrine R3 statistic (3)
* `pcon`    the SELECTION-CORRECTED statistic: max over non-English registers of the
            null-whitened English residual
                r_M = (z_M − rho_M·z_EN) / sqrt(1 − rho_M²)
            with rho_M taken from the pre-computed null, NOT from the sample.  See
            PREREG.md §2.3 for why this beats L7-A §A.4's archive-standardised contrast.
* `ioc`     decrypt IoC·N                       <- R3 statistic (1)
* `mds`     min distinct symbols over any sliding 32-rune window   <- R3 statistic (2)
* `h2`,`zl` compressibility                     <- R3 statistic (4)

Everything is computed on RUNE INDICES, never on the transliteration string (doctrine §4 r5:
7 of 29 runes are two characters).

Models are built by `build_models.py` into `models/panel.npz` (gitignored, rebuildable).
"""
import json
import os
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (os.path.join(LP, "src"), os.path.join(LP, "analysis", "campaign18_skip")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from lp import score as _score      # noqa: E402  (the legacy English quadgram scorer)

N = 29
TRANSLIT = ["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J", "EO", "P",
            "X", "S", "T", "B", "E", "M", "L", "NG", "OE", "D", "A", "AE", "Y",
            "IA", "EA"]

SCHEMA_VERSION = "SWEEPROW/1"
WINDOW = 32                     # the 32-rune window doctrine R3 names for `mds`

#: fixed field order of a SWEEPROW.  See SWEEPROW.md.  NEVER reorder; append only.
ROW_FIELDS = ["kid", "n", "en", "pmax", "preg", "pmax_ne", "pcon", "pcreg",
              "ioc", "mds", "h2", "zl", "z"]
ROW_PRECISION = {"en": 4, "pmax": 3, "pmax_ne": 3, "pcon": 3,
                 "ioc": 4, "h2": 4, "zl": 4, "z": 2}


# ---------------------------------------------------------------- the panel
class Panel:
    """The nine-register panel plus its null calibration.  Load once, call many times."""

    def __init__(self, path=None):
        path = path or os.path.join(HERE, "models", "panel.npz")
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{path} not found — run `python3 build_models.py` first "
                "(models/ is gitignored and rebuildable).")
        d = np.load(path, allow_pickle=False)
        self.registers = [str(s) for s in d["registers"]]
        self.R = len(self.registers)
        self.LMF = np.ascontiguousarray(
            d["LM"].reshape(self.R, -1).astype(np.float32))
        # (29^3, R) C-contiguous: gathering whole rows of R floats is a contiguous copy,
        # where LMF[:, f] would gather R strided columns.  ~3x faster at n = 240.
        self.LMT = np.ascontiguousarray(self.LMF.T)
        self.LP1_LOO = d["LP1_LOO"] if "LP1_LOO" in d else None
        self.len_grid = d["len_grid"].astype(np.int64)
        self.mu = d["mu"].astype(np.float64)              # (nL, R)
        self.sd = d["sd"].astype(np.float64)              # (nL, R)
        self.corr = d["corr"].astype(np.float64)          # (nL, R, R)
        self.lambdas = d["lambdas"].tolist()
        self.null_draws = int(d["null_draws"][0])
        self.null_seed = int(d["null_seed"][0])

        self.i_en = self.registers.index("EN_MODERN")
        self.ne_idx = np.array([i for i, r in enumerate(self.registers)
                                if r not in ("EN_MODERN", "EN_KJV")], dtype=np.int64)
        # per-grid-length whitening coefficients for pcon
        rho = self.corr[:, self.i_en, :]                                  # (nL, R)
        rho = np.clip(rho, -0.999, 0.999)
        self.rho = rho
        self.wden = 1.0 / np.sqrt(1.0 - rho ** 2)                          # (nL, R)
        self._cache = {}

    # -- calibration lookup -------------------------------------------------
    def cal(self, n):
        """(mu, sd, rho, wden) for length n.

        mu is flat in n; sd scales ~ n**-1/2.  Interpolate log(sd) linearly in log(n)
        between bracketing grid points, mu linearly in 1/n, rho at the nearest grid point.
        Outside the grid, clamp to the end point (and say so via `cal_clamped`).
        """
        hit = self._cache.get(n)
        if hit is not None:
            return hit
        g = self.len_grid
        if n <= g[0]:
            i = j = 0
            t = 0.0
        elif n >= g[-1]:
            i = j = len(g) - 1
            t = 0.0
        else:
            j = int(np.searchsorted(g, n))
            i = j - 1
            t = (np.log(n) - np.log(g[i])) / (np.log(g[j]) - np.log(g[i]))
        mu = self.mu[i] + t * (self.mu[j] - self.mu[i])
        sd = np.exp(np.log(self.sd[i]) + t * (np.log(self.sd[j]) - np.log(self.sd[i])))
        k = j if t >= 0.5 else i
        out = (mu, sd, self.rho[k], self.wden[k])
        if len(self._cache) < 4096:
            self._cache[n] = out
        return out

    # -- raw panel score ----------------------------------------------------
    def raw(self, x):
        """x: (n,) int array of rune indices -> (R,) mean log10 trigram score."""
        if len(x) < 3:
            return np.full(self.R, -9.9)
        f = (x[:-2] * (N * N) + x[1:-1] * N + x[2:])
        return self.LMT[f].mean(axis=0, dtype=np.float64)


_PANEL = None


def panel():
    global _PANEL
    if _PANEL is None:
        _PANEL = Panel()
    return _PANEL


_Q = None


def quad():
    global _Q
    if _Q is None:
        _Q = _score.default()
    return _Q


# ------------------------------------------------- language-agnostic statistics
def ioc_n(x):
    """decrypt IoC * N.  1.0 = flat/random, > 1 = structured.  R3 statistic (1)."""
    n = len(x)
    if n < 2:
        return 0.0
    c = np.bincount(x, minlength=N).astype(np.float64)
    return float(N * (c * (c - 1.0)).sum() / (n * (n - 1.0)))


def min_distinct_ref(x, w=WINDOW):
    """Reference (obvious, slow) implementation of `min_distinct`.  Kept as the oracle the
    fast path is tested against — the fast path is an optimisation, not a redefinition."""
    n = len(x)
    if n == 0:
        return 0
    if n <= w:
        return int(np.bincount(x, minlength=N).astype(bool).sum())
    oh = np.zeros((n + 1, N), dtype=np.int16)
    oh[np.arange(1, n + 1), x] = 1
    cum = oh.cumsum(axis=0)
    cnt = cum[w:] - cum[:-w]                        # (n-w+1, N)
    return int((cnt > 0).sum(axis=1).min())


def min_distinct(x, w=WINDOW):
    """Minimum number of distinct symbols over any sliding w-rune window.  R3 statistic (2).

    A restricted alphabet anywhere in the decode drives this down; uniform random runes over
    a 32-window sit near 29*(1-(28/29)^32) = 19.4.  Whole string if n < w.

    O(n) via previous-occurrence + difference array: position j is the FIRST occurrence of
    its symbol inside exactly the windows starting in (prev[j], j], so each j contributes 1
    to a contiguous run of window-start indices and the whole profile is one cumsum.
    """
    n = len(x)
    if n == 0:
        return 0
    if n <= w:
        return int(np.bincount(x, minlength=N).astype(bool).sum())
    idx = np.arange(n)
    order = np.argsort(x, kind="stable")            # groups equal symbols, indices ascending
    xs = x[order]
    prev = np.empty(n, dtype=np.int64)
    prev[order[0]] = -1
    same = xs[1:] == xs[:-1]
    prev[order[1:]] = np.where(same, order[:-1], -1)
    lo = np.maximum(prev + 1, idx - w + 1)
    D = np.bincount(lo, minlength=n + 1).astype(np.int64)
    D[1:n + 1] -= 1                                 # each j stops contributing after i = j
    return int(np.cumsum(D)[:n - w + 1].min())


def h2_cond(x):
    """Plug-in order-2 conditional entropy H(X_i | X_{i-1}, X_{i-2}) in bits/rune.

    R3 statistic (4), primary form.  PREREG.md §2.2 worried that at n ~ 120-400 there are
    only n-2 trigrams against 29^3 contexts, so the estimator would be too undersampled to
    discriminate.  That was pre-registered as a concern to be MEASURED, and the measurement
    (RESULTS.md §5) does not bear it out: at L=240 the wrong-key null sits at 0.262 bits and
    planted natural language at 0.70-0.96 bits, a separation of roughly 20 null SD.  The
    undersampling biases both H3 and H2 downward but not equally — structured text repeats
    bigram contexts far more than trigram contexts — and the difference is what survives.
    """
    n = len(x)
    if n < 3:
        return 0.0
    tri = np.sort(x[:-2] * (N * N) + x[1:-1] * N + x[2:])
    # bi == tri // N exactly, and // N is monotone, so ONE sort run-length-encodes both.
    # (np.bincount would allocate 29^3 = 24,389 bins to hold at most n-2 non-zero counts;
    # two np.unique calls would sort twice.)
    bi = tri // N
    ct = np.diff(np.flatnonzero(
        np.concatenate(([True], tri[1:] != tri[:-1], [True])))).astype(np.float64)
    cb = np.diff(np.flatnonzero(
        np.concatenate(([True], bi[1:] != bi[:-1], [True])))).astype(np.float64)
    m = float(len(tri))
    pt, pb = ct / m, cb / m
    return float(-(pt * np.log2(pt)).sum() + (pb * np.log2(pb)).sum())


def zlib_ratio(x):
    """len(zlib.compress(bytes, 9)) / n.  R3 statistic (4), secondary form."""
    n = len(x)
    if n == 0:
        return 0.0
    return len(zlib.compress(x.astype(np.uint8).tobytes(), 9)) / float(n)


def idx_to_trans(x):
    # .tolist() first: iterating a numpy array yields boxed scalars and is ~3x slower than
    # iterating the equivalent Python list.
    return "".join(map(TRANSLIT.__getitem__,
                       x.tolist() if isinstance(x, np.ndarray) else x))


# ------------------------------------------------------------------ THE CALL
def adjudicate(plain_idx, translit=None, pan=None, lm_override=None):
    """Adjudicate ONE decode.  Returns a full SWEEPROW as a dict.

    plain_idx : sequence of rune indices 0..28 (the decode).  This is the ONLY required
                argument.  Doctrine §4 r5 — never pass the transliteration string as the
                thing to be scored.
    translit  : optional pre-computed transliteration, purely to save the join when the
                caller already has it.  It is used ONLY for the legacy `en` field.
    lm_override : optional (R, 29^3) float32 panel replacing the default, used by the power
                lane for leave-one-page-out LP1 models.  Calibration is reused.

    Returned keys
        v n en  z pmax preg pmax_ne pcon pcreg  ioc mds h2 zl
    """
    pan = pan or panel()
    x = plain_idx if (type(plain_idx) is np.ndarray
                      and plain_idx.dtype == np.int64) else np.asarray(plain_idx,
                                                                       dtype=np.int64)
    n = x.shape[0]

    en = quad().score_norm(translit if translit is not None else idx_to_trans(x))

    if lm_override is None:
        s = pan.raw(x)
    elif n < 3:
        s = np.full(pan.R, -9.9)
    else:
        f = (x[:-2] * (N * N) + x[1:-1] * N + x[2:])
        s = np.asarray(lm_override)[:, f].mean(axis=1, dtype=np.float64)

    mu, sd, rho, wden = pan.cal(n)
    z = (s - mu) / sd
    ne = pan.ne_idx
    zne = z[ne]
    r_ne = (zne - rho[ne] * z[pan.i_en]) * wden[ne]
    ip = z.argmax()
    ine = zne.argmax()
    ipc = r_ne.argmax()

    return {
        "v": SCHEMA_VERSION,
        "n": int(n),
        "en": en,
        "z": z.tolist(),
        "pmax": z[ip], "preg": int(ip),
        "pmax_ne": zne[ine], "ne_reg": int(ne[ine]),
        "pcon": r_ne[ipc], "pcreg": int(ne[ipc]),
        "ioc": ioc_n(x),
        "mds": min_distinct(x),
        "h2": h2_cond(x),
        "zl": zlib_ratio(x),
    }


def adjudicate_batch(X, pan=None):
    """Vectorised panel z for a stack of EQUAL-LENGTH decodes.  X: (B, n) -> dict of arrays.

    The per-row agnostic statistics and the legacy `en` are NOT computed here — this is the
    fast path Phase 2 uses to compute the panel over a block of decodes; call `adjudicate`
    for the rows that matter.  Returned keys: z (B,R), pmax, preg, pmax_ne, pcon, pcreg.
    """
    pan = pan or panel()
    X = np.asarray(X, dtype=np.int64)
    B, n = X.shape
    mu, sd, rho, wden = pan.cal(n)
    out_s = np.empty((B, pan.R))
    for st in range(0, B, 400):
        blk = X[st:st + 400]
        f = blk[:, :-2] * (N * N) + blk[:, 1:-1] * N + blk[:, 2:]
        out_s[st:st + 400] = pan.LMF[:, f].mean(axis=2, dtype=np.float64).T
    z = (out_s - mu) / sd
    ne = pan.ne_idx
    zen = z[:, pan.i_en][:, None]
    r = (z - rho[None, :] * zen) * wden[None, :]
    return {"z": z,
            "pmax": z.max(axis=1), "preg": z.argmax(axis=1),
            "pmax_ne": z[:, ne].max(axis=1), "ne_reg": ne[z[:, ne].argmax(axis=1)],
            "pcon": r[:, ne].max(axis=1), "pcreg": ne[r[:, ne].argmax(axis=1)]}


# ------------------------------------------------------------------ the record
def to_row(res, kid):
    """Full SWEEPROW as a fixed-order JSON array.  See SWEEPROW.md."""
    p = ROW_PRECISION
    return [kid, res["n"],
            round(res["en"], p["en"]),
            round(res["pmax"], p["pmax"]), int(res["preg"]),
            round(res["pmax_ne"], p["pmax_ne"]),
            round(res["pcon"], p["pcon"]), int(res["pcreg"]),
            round(res["ioc"], p["ioc"]), int(res["mds"]),
            round(res["h2"], p["h2"]), round(res["zl"], p["zl"]),
            [round(v, p["z"]) for v in res["z"]]]


ROW_DTYPE = np.dtype([("kid", "<u8"), ("n", "<u2"), ("en", "<f4"),
                      ("pmax", "<f4"), ("preg", "u1"), ("pmax_ne", "<f4"),
                      ("pcon", "<f4"), ("pcreg", "u1"),
                      ("ioc", "<f4"), ("mds", "u1"), ("h2", "<f4"), ("zl", "<f4"),
                      ("z", "<f4", (9,))])   # 77 bytes/row -> 10^7 rows = 770 MB


def to_record(res, kid_int):
    """Binary SWEEPROW, for the bulk store.  `kid_int` must index the sweep's own key table."""
    return np.array([(kid_int, res["n"], res["en"], res["pmax"], res["preg"],
                      res["pmax_ne"], res["pcon"], res["pcreg"], res["ioc"],
                      min(res["mds"], 255), res["h2"], res["zl"],
                      tuple(res["z"]))], dtype=ROW_DTYPE)[0]


def header(sweep_id, pan=None, **extra):
    """The once-per-sweep header a SWEEPROW store MUST carry.  See SWEEPROW.md §2."""
    pan = pan or panel()
    b = os.path.join(HERE, "out_build.json")
    build = json.load(open(b, encoding="utf-8")) if os.path.exists(b) else {}
    h = {"v": SCHEMA_VERSION, "sweep": sweep_id,
         "fields": ROW_FIELDS, "registers": pan.registers,
         "english_ref": "EN_MODERN", "window": WINDOW,
         "panel_build": build.get("built"), "lambdas": pan.lambdas,
         "null": {"draws": pan.null_draws, "seed": pan.null_seed,
                  "len_grid": pan.len_grid.tolist()},
         "corpora_sha256": {k: [c["sha256"] for c in v]
                            for k, v in build.get("corpora", {}).items()},
         "precision": ROW_PRECISION}
    h.update(extra)
    return h


# ------------------------------------------------------------------ validator
class RowError(ValueError):
    pass


def validate_row(row, hdr=None, n_registers=9):
    """Raise RowError unless `row` is a well-formed SWEEPROW.  CI-callable.

    This is the check doctrine R3 says must be enforced: a sweep that stores only
    (parameters, English score, head) is exactly what produced 10^10 un-reinterpretable
    decodes, and it must fail here rather than three rounds later.
    """
    if isinstance(row, dict):
        missing = [f for f in ROW_FIELDS if f != "kid" and f not in row]
        if missing:
            raise RowError(f"dict row missing fields: {missing}")
        row = to_row(row, row.get("kid", 0))
    if not isinstance(row, (list, tuple)):
        raise RowError(f"row must be a list/tuple/dict, got {type(row).__name__}")
    if len(row) != len(ROW_FIELDS):
        raise RowError(f"row has {len(row)} fields, schema {SCHEMA_VERSION} needs "
                       f"{len(ROW_FIELDS)}: {ROW_FIELDS}")
    d = dict(zip(ROW_FIELDS, row))
    if not isinstance(d["n"], int) or d["n"] < 0:
        raise RowError("n must be a non-negative int (rune length of the decode)")
    for f in ("en", "pmax", "pmax_ne", "pcon", "ioc", "h2", "zl"):
        if not isinstance(d[f], (int, float)) or d[f] != d[f]:
            raise RowError(f"{f} must be a finite number, got {d[f]!r}")
    for f in ("preg", "pcreg"):
        if not isinstance(d[f], int) or not (0 <= d[f] < n_registers):
            raise RowError(f"{f} must be a register index in [0,{n_registers})")
    if not isinstance(d["mds"], int) or not (0 <= d["mds"] <= N):
        raise RowError(f"mds must be an int in [0,{N}], got {d['mds']!r}")
    if not (0.0 <= d["ioc"] <= float(N)):
        raise RowError(f"ioc out of range [0,{N}]: {d['ioc']}")
    z = d["z"]
    if not isinstance(z, (list, tuple)) or len(z) != n_registers:
        raise RowError(f"z must be a {n_registers}-vector of per-register standardised "
                       f"scores; got {z!r}. Storing only the English score is precisely "
                       "the R3 violation that made 10^10 decodes un-reinterpretable.")
    if abs(max(z) - d["pmax"]) > 0.02:
        raise RowError(f"pmax {d['pmax']} disagrees with max(z) {max(z)}")
    if hdr is not None:
        if hdr.get("v") != SCHEMA_VERSION:
            raise RowError(f"header schema {hdr.get('v')} != {SCHEMA_VERSION}")
        if hdr.get("fields") != ROW_FIELDS:
            raise RowError("header field order does not match this schema version")
    return True


def validate_store(path, hdr=None, limit=None):
    """Validate a JSONL SWEEPROW store: line 1 = header object, rest = row arrays."""
    n = 0
    with open(path, encoding="utf-8") as f:
        first = f.readline()
        h = json.loads(first)
        if not isinstance(h, dict) or "fields" not in h:
            raise RowError("line 1 of a SWEEPROW store must be the header object")
        for line in f:
            line = line.strip()
            if not line:
                continue
            validate_row(json.loads(line), hdr or h)
            n += 1
            if limit and n >= limit:
                break
    return {"path": path, "header": h, "rows_validated": n}


if __name__ == "__main__":
    import time
    pan = panel()
    print("registers:", pan.registers)
    rng = np.random.default_rng(0)
    x = rng.integers(0, N, 240)
    t = time.perf_counter()
    r = adjudicate(x)
    print(f"random-rune decode ({time.perf_counter()-t:.4f}s first call):")
    for k in ("en", "pmax", "preg", "pmax_ne", "pcon", "pcreg", "ioc", "mds", "h2", "zl"):
        print(f"   {k:8s} {r[k]}")
    print("row:", json.dumps(to_row(r, "demo")))
    validate_row(to_row(r, "demo"))
    print("validate_row: OK")
