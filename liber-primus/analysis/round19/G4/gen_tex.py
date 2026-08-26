"""ROUND 19 / G4 — TeX/LaTeX-internal pseudo-random generators, reimplemented exactly.

Four generators that live *inside* a TeX document, i.e. the ones an author who was
already typesetting a 6x9-inch runic PDF (round18/L1-toolchain/RESULTS.md, F4+F5)
would have reached for without leaving the document:

  pgf        pgf/pgfmath's \\pgfmathgeneratepseudorandomnumber
             Lehmer, a=69621 q=30845 r=23902 m=2^31-1  (Schrage)
             source: vendor/pgf_2.00src/.../pgfmathrnd.code.tex  (TeX Live 2009)
                     vendor/pgf_2.10/.../pgfmathfunctions.random.code.tex
             NOTE the multiplier is 69621, NOT the 16807 the file's comment mentions.

  lcg        the `lcg' package (Erich Janka), \\rand
             Lehmer, a=16807 q=127773 r=2836 m=2^31-1  (Schrage) + REJECTION
             source: vendor/lcg.dtx.ctan  (v1.3, 2013/08/09)

  randomtex  random.tex (Donald Arseneau v0.2), \\nextrandom / \\setrannum
             same Lehmer core as lcg, but a DIVISION-scaled reduction + rejection
             source: vendor/random.tex.ctan

  pdftex     pdfTeX's \\pdfuniformdeviate / \\pdfsetrandomseed
             Knuth's 55-lag subtractive generator on 28-bit fractions, inherited
             from METAFONT/MetaPost (init_randoms/new_randoms/unif_rand/take_fraction)

Everything here reproduces TeX's *integer* arithmetic, not a mathematician's: TeX's
\\divide truncates toward zero, counts are bounded by +/-(2^31-1), and the rejection
loops are the packages' own.  `python3 gen_tex.py --validate` asserts element-for-element
equality against sequences emitted by the real binaries (see make_vectors.sh) and writes
validation.json.

Sign / direction / atbash / offset conventions follow round13/B04/PREREG.md 3.4-3.5.

THE HOLD: this module produces keystreams.  It does NOT score anything.  Round 19's
Phase 0 (I1 driftbeam, I2 adjudicator, I3 thresholds) must pass before any decode from
these generators is adjudicated -- see PREREG.md 2/Q1 and READY.md.
"""
from __future__ import annotations

import json
import os
import sys

N = 29
M31 = 2147483647            # 2^31 - 1, the modulus of all three Lehmer generators
HERE = os.path.dirname(os.path.abspath(__file__))
TEXDIR = os.path.join(HERE, "tex")


# --------------------------------------------------------------------------- #
# TeX arithmetic primitives
# --------------------------------------------------------------------------- #
def tex_div(a: int, b: int) -> int:
    """TeX's \\divide: integer division TRUNCATED TOWARD ZERO (not floored)."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


# --------------------------------------------------------------------------- #
# T1 -- pgf / pgfmath
# --------------------------------------------------------------------------- #
PGF_A, PGF_Q, PGF_R = 69621, 30845, 23902


def pgf_next(z: int) -> int:
    """One \\pgfmathgeneratepseudorandomnumber step, macro-for-macro.

        counta = z ; countb = z ; countc = q
        counta = counta div countc            -> hi
        counta = counta * -countc             -> -q*hi
        counta = counta + countb              -> z - q*hi  = z mod q  (= lo)
        counta = counta * a                   -> a*lo
        countb = countb div q                 -> hi
        countb = countb * r                   -> r*hi
        counta = counta - countb
        if counta < 0: counta += m
    """
    hi = tex_div(z, PGF_Q)
    lo = z - PGF_Q * hi
    zz = PGF_A * lo - PGF_R * hi
    if zz < 0:
        zz += M31
    return zz


def pgf_raw(seed: int, n: int):
    z = seed
    out = []
    for _ in range(n):
        z = pgf_next(z)
        out.append(z)
    return out


def pgf_randominteger(seed: int, n: int, lo: int = 0, hi: int = 28):
    """\\pgfmathrandominteger{\\x}{lo}{hi}: one draw per output, result = lo + z mod R."""
    R = hi - lo + 1
    return [lo + (z - R * tex_div(z, R)) for z in pgf_raw(seed, n)]


def pgf_rnd29(seed: int, n: int):
    """\\pgfmathparse{int(rnd*29)}.

    `rnd` is built as a 5-decimal fixed-point number from (z mod 100001), stored in a
    TeX dimen (so quantised to 1/65536 pt), then multiplied by 29 and truncated by
    pgfmath's own fixed-point multiply.  Modelled here as the dimen round-trip; this
    mapping is validated separately and is dropped rather than assumed if it fails.
    """
    out = []
    for z in pgf_raw(seed, n):
        t = z - 100001 * tex_div(z, 100001)          # z mod 100001
        sp = (t * 65536 + 50000) // 100000           # \dimen = value pt, rounded to sp
        v = (sp * 29) // 65536                       # pgfmath int(x*29)
        out.append(min(v, 28))
    return out


# --------------------------------------------------------------------------- #
# T2 -- the `lcg' package
# --------------------------------------------------------------------------- #
PM_A, PM_Q, PM_R = 16807, 127773, 2836              # Park-Miller "minimal standard"


def pm_next(z: int) -> int:
    """One \\r@nd / \\nextrandom step (Schrage).  Shared by lcg and random.tex."""
    hi = tex_div(z, PM_Q)
    lo = z - PM_Q * hi
    zz = PM_A * lo - PM_R * hi
    if zz < 0:
        zz += M31
    return zz


def pm_raw(seed: int, n: int):
    z = seed
    out = []
    for _ in range(n):
        z = pm_next(z)
        out.append(z)
    return out


def lcg_rand(seed: int, n: int, first: int = 0, last: int = 28):
    """\\rand: rejection-sample the raw stream, then first + (z mod R)."""
    R = last - first + 1
    lim = R * tex_div(M31, R)                        # 2147459628 for R=29
    out, z = [], seed
    while len(out) < n:
        z = pm_next(z)
        if z > lim:
            continue                                  # \rand recurses = redraw
        out.append(first + (z - R * tex_div(z, R)))
    return out


# --------------------------------------------------------------------------- #
# T3 -- random.tex
# --------------------------------------------------------------------------- #
def randomtex_default_seed(time_: int, year: int, month: int, day: int) -> int:
    """random.tex's date initialisation, BEFORE its three discarded warm-up draws."""
    r = time_
    r = r * 388 + year
    r = r * 31 + day
    r = r * 97 + month
    return r


def randomtex_setrannum(seed: int, n: int, lo: int = 0, hi: int = 28):
    """\\setrannum{\\c}{lo}{hi}: v = (z-1) div B, rejected unless v < R, then + lo."""
    R = hi - lo + 1
    B = tex_div(2147483645, R)                        # 74051160 for R=29
    out, z = [], seed
    while len(out) < n:
        z = pm_next(z)
        v = tex_div(z - 1, B)
        if v < R:
            out.append(v + lo)
    return out


# --------------------------------------------------------------------------- #
# T4 -- pdfTeX \pdfuniformdeviate  (Knuth's 55-lag subtractive generator)
# --------------------------------------------------------------------------- #
FRACTION_ONE = 1 << 28


def take_fraction(p: int, q: int) -> int:
    """METAFONT take_fraction(p,q) = round(p*q / 2^28)."""
    return (p * q + (1 << 27)) >> 28


class PdfTexRandom:
    """pdfTeX's random_seed state.  \\pdfsetrandomseed{n} == PdfTexRandom(n)."""

    __slots__ = ("randoms", "j_random")

    def __init__(self, seed: int):
        self.randoms = [0] * 55
        self.j_random = 0
        self._init_randoms(seed)

    def _new_randoms(self):
        r = self.randoms
        for k in range(0, 24):
            x = r[k] - r[k + 31]
            if x < 0:
                x += FRACTION_ONE
            r[k] = x
        for k in range(24, 55):
            x = r[k] - r[k - 24]
            if x < 0:
                x += FRACTION_ONE
            r[k] = x
        self.j_random = 54

    def _init_randoms(self, seed: int):
        j = abs(seed)
        while j >= FRACTION_ONE:
            j //= 2                                   # METAFONT `half'
        k = 1
        for i in range(55):
            jj = k
            k = j - k
            j = jj
            if k < 0:
                k += FRACTION_ONE
            self.randoms[(i * 21) % 55] = j
        self._new_randoms()
        self._new_randoms()
        self._new_randoms()

    def next_random(self) -> int:
        if self.j_random == 0:
            self._new_randoms()
        else:
            self.j_random -= 1
        return self.randoms[self.j_random]

    def unif_rand(self, x: int) -> int:
        y = take_fraction(abs(x), self.next_random())
        if y == abs(x):
            return 0
        return y if x > 0 else -y


def pdftex_uniformdeviate(seed: int, n: int, modulus: int = 29):
    g = PdfTexRandom(seed)
    return [g.unif_rand(modulus) for _ in range(n)]


# --------------------------------------------------------------------------- #
# Keystream interface -- the thing S1 consumes (B-04 ks.py shape)
# --------------------------------------------------------------------------- #
#   name -> (fn(seed, nsym) -> list[int] in Z_29, "stream family", era note)
GENERATORS = {
    # T1 pgf
    "pgf_mod29":       lambda s, n: pgf_randominteger(s, n, 0, 28),
    "pgf_mod29_c1":    lambda s, n: [(v + 1) % N for v in pgf_randominteger(s, n, 0, 28)],
    "pgf_rnd29":       lambda s, n: pgf_rnd29(s, n),
    # T2 lcg
    "lcg_mod29":       lambda s, n: lcg_rand(s, n, 0, 28),
    "lcg_mod29_c1":    lambda s, n: [(v + 1) % N for v in lcg_rand(s, n, 0, 28)],
    # T3 random.tex
    "randomtex_div29":    lambda s, n: randomtex_setrannum(s, n, 0, 28),
    "randomtex_div29_c1": lambda s, n: [(v + 1) % N for v in randomtex_setrannum(s, n, 0, 28)],
    # T4 pdfTeX
    "pdftex_u29":      lambda s, n: pdftex_uniformdeviate(s, n, 29),
    "pdftex_u29_c1":   lambda s, n: [(v + 1) % N for v in pdftex_uniformdeviate(s, n, 29)],
}
GEN_NAMES = list(GENERATORS)

# which generators live on which single Lehmer cycle (see PREREG 3.7 / Q3)
CYCLE = {
    "pgf_mod29": "pgf", "pgf_mod29_c1": "pgf", "pgf_rnd29": "pgf",
    "lcg_mod29": "pm", "lcg_mod29_c1": "pm",
    "randomtex_div29": "pm", "randomtex_div29_c1": "pm",
    "pdftex_u29": None, "pdftex_u29_c1": None,     # 55-word state, not a single cycle
}
MULTIPLIER = {"pgf": PGF_A, "pm": PM_A}


def make_ks(gen: str, seed: int, nsym: int, direction: str = "fwd"):
    """>= nsym keystream symbols in Z_29.  `direction` follows B-04 3.4."""
    ks = GENERATORS[gen](seed, nsym)
    return ks if direction == "fwd" else ks[::-1]


def advance(cycle: str, z: int, k: int) -> int:
    """State after k steps of a Lehmer cycle -- offsets are phase shifts (PREREG Q3)."""
    return (pow(MULTIPLIER[cycle], k, M31) * z) % M31


# --------------------------------------------------------------------------- #
# Seed sets (PREREG 3.1-3.4)
# --------------------------------------------------------------------------- #
def pgf_default_seeds(years=range(2010, 2016)):
    """pgf's unset-seed default: \\time x \\year, \\time in [0,1439]."""
    return sorted({t * y for y in years for t in range(1440)})


def randomtex_default_seeds(years=range(2010, 2016)):
    """random.tex's date init (before its 3 warm-up draws)."""
    return sorted({randomtex_default_seed(t, y, mo, d)
                   for y in years for mo in range(1, 13)
                   for d in range(1, 32) for t in range(1440)})


# Cicada integers an author would actually type (B-04 PREREG 3.1 num_* / primes_*)
CICADA_SEEDS = [3301, 1033, 761, 29, 845145127, 1595277641, 13, 1595277641 % M31,
                2013, 2012, 2014, 3, 7, 33, 301, 3301 * 3301 % M31, 133, 3031]


# --------------------------------------------------------------------------- #
# Master-cycle builder (Phase 2 plumbing; cost stated in READY.md 3)
# --------------------------------------------------------------------------- #
def build_master(cycle: str, mapping, out_path: str, lanes: int = 1 << 20,
                 total: int = M31 - 1, progress=None):
    """Write the whole 2^31-2 phase cycle, reduced to Z_29, as a uint8 file.

    Because a=69621 and a=16807 are both primitive roots mod 2^31-1, the state space
    is ONE cycle; every seed and every offset is a phase of this single stream, so the
    entire T1/T2/T3 space is a sliding window over this array.  ~2.1 GB per family.
    """
    import numpy as np
    a = MULTIPLIER[cycle]
    per = total // lanes
    tail = total - per * lanes
    step = pow(a, per, M31)
    starts = np.empty(lanes, dtype=np.int64)
    z = 1
    for i in range(lanes):
        starts[i] = z
        z = (z * step) % M31
    with open(out_path, "wb") as fh:
        cur = starts.copy()
        block = np.empty((lanes, per), dtype=np.int64)
        for t in range(per):
            cur = (a * cur) % M31
            block[:, t] = cur
        fh.write(mapping(block).astype(np.uint8).tobytes())
        if tail:
            z = int(cur[-1])
            rest = np.empty(tail, dtype=np.int64)
            for t in range(tail):
                z = (a * z) % M31
                rest[t] = z
            fh.write(mapping(rest).astype(np.uint8).tobytes())
    return out_path


# --------------------------------------------------------------------------- #
# Validation against the real TeX binaries
# --------------------------------------------------------------------------- #
def _parse(path):
    """tex/ref_*.txt -> {(seed, label): [ints]} plus {'_meta': {...}}."""
    rows, meta = {}, {}
    if not os.path.exists(path):
        return rows, meta
    for line in open(path, encoding="utf-8", errors="replace"):
        parts = line.split()
        if not parts:
            continue
        if len(parts) >= 2 and parts[0].endswith("VERSION"):
            meta[parts[0]] = " ".join(parts[1:])
            continue
        if len(parts) >= 3 and parts[1] == "DEFAULT":
            meta["DEFAULT"] = [int(x) for x in parts[2:]]
            continue
        if len(parts) >= 3 and parts[2] == "SEEDACCEPT":
            meta.setdefault("SEEDACCEPT", {})[parts[1]] = parts[3] if len(parts) > 3 else ""
            continue
        try:
            seed = int(parts[1])
        except ValueError:
            continue
        label = parts[2]
        rows[(seed, label)] = [int(x) for x in parts[3:]]
    return rows, meta


def _cmp(name, got, want):
    if got == want:
        return {"check": name, "status": "PASS", "n": len(want)}
    first = next((i for i, (g, w) in enumerate(zip(got, want)) if g != w), min(len(got), len(want)))
    return {"check": name, "status": "FAIL", "n": len(want), "first_mismatch_index": first,
            "got": got[max(0, first - 2):first + 3], "want": want[max(0, first - 2):first + 3]}


def _full_period_check(a):
    """V4: a is a primitive root mod 2^31-1  =>  one cycle of length 2^31-2."""
    m1 = M31 - 1
    factors, x, d = [], m1, 2
    while d * d <= x:
        if x % d == 0:
            factors.append(d)
            while x % d == 0:
                x //= d
        d += 1
    if x > 1:
        factors.append(x)
    ok = all(pow(a, m1 // p, M31) != 1 for p in factors)
    return {"multiplier": a, "m_minus_1_factors": factors,
            "primitive_root": ok, "period": m1 if ok else None}


def validate(verbose=True):
    res = {"lane": "round19/G4", "generators": {}, "gates": {}, "notes": []}

    pgf_rows, pgf_meta = _parse(os.path.join(TEXDIR, "ref_pgf.txt"))
    pgf210_rows, pgf210_meta = _parse(os.path.join(TEXDIR, "out210", "ref_pgf.txt"))
    lcg_rows, lcg_meta = _parse(os.path.join(TEXDIR, "ref_lcg.txt"))
    rnd_rows, rnd_meta = _parse(os.path.join(TEXDIR, "ref_random.txt"))
    pdf_rows, pdf_meta = _parse(os.path.join(TEXDIR, "ref_pdf.txt"))

    def block(gname, rows, meta, checks):
        out = {"reference_source": meta, "checks": [], "n_vectors": 0, "n_elements": 0}
        for (seed, label), want in sorted(rows.items()):
            fn = checks.get(label)
            if fn is None:
                continue
            got = fn(seed, len(want))
            c = _cmp(f"{gname}/{label}/seed={seed}", got, want)
            out["checks"].append(c)
            out["n_vectors"] += 1
            out["n_elements"] += len(want)
        fails = [c for c in out["checks"] if c["status"] == "FAIL"]
        out["status"] = "PASS" if (out["n_vectors"] and not fails) else ("FAIL" if fails else "NO-VECTORS")
        out["n_fail"] = len(fails)
        if len(out["checks"]) > 24:                    # keep validation.json readable
            out["checks"] = [c for c in out["checks"] if c["status"] == "FAIL"] or out["checks"][:6]
            out["checks_note"] = "only failures (or the first 6) are listed; counts above are complete"
        return out

    res["generators"]["pgf"] = block("pgf", pgf_rows, pgf_meta, {
        "RAW":  lambda s, n: pgf_raw(s, n),
        "R029": lambda s, n: pgf_randominteger(s, n, 0, 28),
        "R129": lambda s, n: pgf_randominteger(s, n, 1, 29),
        "RND29": lambda s, n: pgf_rnd29(s, n),
    })
    res["generators"]["lcg"] = block("lcg", lcg_rows, lcg_meta, {
        "RAW":  lambda s, n: pm_raw(s, n),
        "R029": lambda s, n: lcg_rand(s, n, 0, 28),
        "R129": lambda s, n: lcg_rand(s, n, 1, 29),
    })
    res["generators"]["randomtex"] = block("randomtex", rnd_rows, rnd_meta, {
        "RAW":  lambda s, n: pm_raw(s, n),
        "R029": lambda s, n: randomtex_setrannum(s, n, 0, 28),
        "R129": lambda s, n: randomtex_setrannum(s, n, 1, 29),
    })
    res["generators"]["pdftex"] = block("pdftex", pdf_rows, pdf_meta, {
        "RAW28": lambda s, n: pdftex_uniformdeviate(s, n, FRACTION_ONE),
        "U29":   lambda s, n: pdftex_uniformdeviate(s, n, 29),
        "U256":  lambda s, n: pdftex_uniformdeviate(s, n, 256),
    })

    # V1 / V2
    passed = [g for g, b in res["generators"].items() if b["status"] == "PASS"]
    res["gates"]["V1_byte_exact_vs_real_tex"] = {
        "per_generator": {g: b["status"] for g, b in res["generators"].items()},
        "status": "PASS" if len(passed) == 4 else "PARTIAL",
    }
    res["gates"]["V2_at_least_two_generators"] = {
        "n_passing": len(passed), "required": 2,
        "status": "PASS" if len(passed) >= 2 else "FAIL",
    }

    # V3 -- pgf 2.10 (era-correct, TeX Live 2009 / Ubuntu 11.04-12.04) vs pgf 3.1.x
    if pgf210_rows:
        same = {k: v for k, v in pgf_rows.items() if k in pgf210_rows}
        diffs = [k for k in same if pgf_rows[k] != pgf210_rows[k]]
        res["gates"]["V3_pgf_version_invariance"] = {
            "pgf_installed": pgf_meta.get("PGFVERSION"),
            "pgf_vendored": pgf210_meta.get("PGFVERSION"),
            "n_compared": len(same), "n_differing": len(diffs),
            "status": "PASS" if not diffs else "FAIL",
        }
    else:
        res["gates"]["V3_pgf_version_invariance"] = {"status": "NOT-RUN"}

    # V6 -- random.tex's date-initialised default seed, INCLUDING its 3 warm-up draws.
    # The .tex reference writes  RND DEFAULT <time> <year> <month> <day> <randomi>
    # after `\global\randomi=0 \nextrandom`, which runs the init, three nested
    # \nextrandom warm-ups, and then the outer call's own step: four steps in total.
    if "DEFAULT" in rnd_meta:
        t, y, mo, d, observed = rnd_meta["DEFAULT"]
        z = randomtex_default_seed(t, y, mo, d)
        for _ in range(4):
            z = pm_next(z)
        res["gates"]["V6_randomtex_default_seed"] = {
            "time": t, "year": y, "month": mo, "day": d,
            "seed_before_warmup": randomtex_default_seed(t, y, mo, d),
            "predicted_after_4_steps": z, "observed": observed,
            "status": "PASS" if z == observed else "FAIL",
        }
    else:
        res["gates"]["V6_randomtex_default_seed"] = {"status": "NOT-RUN"}

    # V4 -- single-cycle claim (this is what absorbs the offset ladder)
    v4 = {"pgf": _full_period_check(PGF_A), "pm": _full_period_check(PM_A)}
    for cyc, a in (("pgf", PGF_A), ("pm", PM_A)):
        z0 = 3301
        v4[cyc]["returns_to_seed_after_m_minus_1"] = (advance(cyc, z0, M31 - 1) == z0)
        v4[cyc]["not_earlier_at_half_period"] = (advance(cyc, z0, (M31 - 1) // 2) != z0)
    v4["status"] = "PASS" if all(v4[c]["primitive_root"] and
                                 v4[c]["returns_to_seed_after_m_minus_1"] and
                                 v4[c]["not_earlier_at_half_period"] for c in ("pgf", "pm")) else "FAIL"
    v4["consequence"] = ("single cycle of length 2^31-2 => every seed and every offset is a "
                         "phase of one master stream; B-04's offset ladder and B-02's "
                         "key-index-0 assumption are ABSORBED for pgf/lcg/random.tex")
    res["gates"]["V4_single_cycle"] = v4

    # space accounting, recomputed from the validated parameters
    res["space"] = {
        "pgf":       {"phases": M31 - 1, "streams": ["pgf_mod29(c=0,1)", "pgf_rnd29"],
                      "offsets_absorbed": True},
        "lcg":       {"phases": M31 - 1, "streams": ["lcg_mod29(c=0,1)"], "offsets_absorbed": True},
        "randomtex": {"phases": M31 - 1, "streams": ["randomtex_div29(c=0,1)"], "offsets_absorbed": True},
        "pdftex":    {"seeds": 1 << 28, "streams": ["pdftex_u29(c=0,1)"], "offsets_absorbed": False,
                      "why": "55-word state; trajectories from distinct seeds are disjoint"},
        "default_seed_spaces": {
            "pgf_time_x_year_2010_2015": len(pgf_default_seeds()),
            "randomtex_date_init_2010_2015": 1440 * 6 * 31 * 12,
            "lcg_default": "NOT ENUMERABLE in budget (depends on \\inputlineno and \\value{page})",
            "pdftex_default": "NOT ENUMERABLE (wall-clock microseconds)",
        },
    }

    if verbose:
        for g, b in res["generators"].items():
            print(f"{g:11s} {b['status']:10s} vectors={b['n_vectors']:3d} "
                  f"elements={b['n_elements']:6d} fails={b['n_fail']}")
        for k, v in res["gates"].items():
            print(f"  {k:34s} {v.get('status')}")
    return res


def main(argv):
    if "--validate" in argv:
        res = validate()
        out = os.path.join(HERE, "validation.json")
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1)
        print("wrote", out)
        return 0 if res["gates"]["V2_at_least_two_generators"]["status"] == "PASS" else 1
    for g in GEN_NAMES:
        print(f"{g:22s} {make_ks(g, 3301, 16)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
