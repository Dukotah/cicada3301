"""ROUND 19 / LANE G2 -- MANDATORY VALIDATION GATE.

Three gates.  A generator that does not pass all three does not enter the sweep.

  GATE A  gen_perl.py  ==  the real `perl` binary on this box, element for
          element, over a seed panel x a draw count, for every Perl-reachable
          reduction and for the raw Drand01() double at 17 significant digits.

  GATE B  the real `perl` binary  ==  glibc `srand48`/`drand48` called directly
          from C.  This is the leg that retires the 5.40-vs-5.14 version risk:
          Perl 5.14.2's `config_h.SH` defines `Drand01()` as `drand48()` and
          `seedDrand01(x)` as `srand48((long)x)`, so glibc IS the era generator.
          If 5.40 == glibc and mine == 5.40, then mine == 5.14.

  GATE C  structural checks that do not need a runtime:
            C1 seed folding -- srand(S) == srand(S + 2**32)  (measured in perl)
            C2 the exact-integer identity int(rand(M)) == (M*x)>>48 holds for
               every M where gen_perl takes the integer fast path
            C3 srand() argument coercion, 5.14 rule vs 5.40 rule, with the
               divergences enumerated rather than hidden

Writes validation.json.

Run:  python3 validate.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gen_perl as G  # noqa: E402

PERL = "perl"
REF = os.path.join(HERE, "ref_perl.pl")
CREF = "/tmp/g2_d48"
CSRC = os.path.join(HERE, "ref_drand48.c")

# The standard Round 8 / L5-seed32 seed panel, plus the era-relevant additions.
SEEDS = [
    0, 1, 42, 12345, 3301, 1033,
    1399079190,          # L5-seed32's panel
    2147483647,          # 2**31 - 1
    3141592653,          # L5-seed32's panel
    4294967295,          # 2**32 - 1
    1293840000,          # 2011-01-01, the low end of the era band
    1420070400,          # 2015-01-01, the high end
    845145127,           # the 3301 phone-number constant
]
NDRAW = 2000


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{cmd} -> rc={r.returncode}\n{r.stderr}")
    return r.stdout


def perl_r29(seed, n, m=29):
    out = sh([PERL, REF, "rN", str(seed), str(n), str(m)]).strip()
    return [int(v) for v in out.split(",")]


def perl_raw(seed, n):
    return [ln.strip() for ln in sh([PERL, REF, "raw", str(seed), str(n)]).splitlines() if ln.strip()]


# --------------------------------------------------------------------------
# GATE A
# --------------------------------------------------------------------------

def gate_a():
    """gen_perl.py == real perl, element for element."""
    rows = []
    ok = True

    # A0 -- the raw Drand01() double, at full precision.
    for seed in SEEDS[:6]:
        got = perl_raw(seed, 64)
        r = G.Drand48(seed)
        mine = ["%.17g" % r.drand48() for _ in range(64)]
        m = (got == mine)
        ok &= m
        rows.append({"gate": "A0", "what": "Drand01() %.17g", "seed": seed,
                     "n": 64, "match": m,
                     "first3_perl": got[:3], "first3_mine": mine[:3]})

    # A1 -- int(rand(M)) for every M gen_perl uses.
    for m_arg in (29, 32, 256, 255, 100, 1000, 26, 1 << 32):
        for seed in SEEDS:
            got = perl_r29(seed, NDRAW, m_arg)
            mine = G.int_rand_stream(seed, m_arg, NDRAW)
            match = (got == mine)
            ok &= match
            rows.append({"gate": "A1", "what": f"int(rand({m_arg}))", "seed": seed,
                         "n": NDRAW, "match": match,
                         "first8_perl": got[:8], "first8_mine": mine[:8],
                         "first_mismatch": None if match else
                         next(i for i in range(NDRAW) if got[i] != mine[i])})

    # A2 -- the full reduction set, driven through real perl loops.
    for red in G.PERL_REACHABLE:
        for seed in SEEDS[:6]:
            got = perl_reduction(red, seed, 512)
            mine = G.make_ks(red, seed, 512)
            match = (got == mine)
            ok &= match
            rows.append({"gate": "A2", "what": red, "seed": seed, "n": 512,
                         "match": match, "first8_perl": got[:8],
                         "first8_mine": mine[:8],
                         "first_mismatch": None if match else
                         next(i for i in range(512) if got[i] != mine[i])})
    return ok, rows


def perl_reduction(red, seed, n):
    """Symbols as the REAL perl produces them.

    `r26_lat` is the one reduction whose last step is not Perl: perl emits a
    letter index 0..25 and the Latin->futhorc mapping is the repo's
    `skipdecode.eng_to_idx` table.  Applying it here keeps the comparison
    against `gen_perl.make_ks` like-for-like without pushing repo internals into
    the Perl reference.
    """
    out = sh([PERL, os.path.join(HERE, "ref_reduce.pl"), red, str(seed), str(n)]).strip()
    vals = [int(v) for v in out.split(",")]
    if red == "r26_lat":
        t = G._lat()
        vals = [t[v] for v in vals]
    return vals


# --------------------------------------------------------------------------
# GATE B -- real perl vs glibc drand48
# --------------------------------------------------------------------------

def gate_b():
    if not os.path.exists(CREF):
        sh(["gcc", "-O2", "-o", CREF, CSRC])
    rows = []
    ok = True
    for seed in SEEDS:
        c_out = [ln.strip() for ln in sh([CREF, str(seed), "1024"]).splitlines() if ln.strip()]
        p_out = perl_raw(seed, 1024)
        match = (c_out == p_out)
        ok &= match
        rows.append({"gate": "B", "what": "perl rand() vs glibc drand48()",
                     "seed": seed, "n": 1024, "match": match,
                     "first2_glibc": c_out[:2], "first2_perl": p_out[:2],
                     "first_mismatch": None if match else
                     next(i for i in range(1024) if c_out[i] != p_out[i])})
    return ok, rows


# --------------------------------------------------------------------------
# GATE C -- structural
# --------------------------------------------------------------------------

def gate_c():
    rows = []
    ok = True

    # C1 -- srand folds mod 2**32, measured in perl, not asserted.
    for base in (1, 3301, 1293840000):
        a = perl_r29(base, 64)
        b = perl_r29(base + (1 << 32), 64)
        c = perl_r29(base + (1 << 33), 64)
        match = (a == b == c)
        ok &= match
        rows.append({"gate": "C1", "what": "srand(S) == srand(S+2**32) == srand(S+2**33)",
                     "seed": base, "match": match, "first6": a[:6]})

    # C2 -- integer fast path == the C double expression, for every M where
    # gen_perl claims exactness.
    for m_arg in (26, 29, 32, 256, 1 << 32):
        bad = 0
        for seed in SEEDS:
            r = G.Drand48(seed)
            for _ in range(4000):
                x = r.step()
                if ((m_arg * x) >> 48) != int(float(m_arg) * (x / G._TWO48)):
                    bad += 1
        match = (bad == 0)
        ok &= match
        rows.append({"gate": "C2", "what": f"(M*x)>>48 == int(M*(x/2**48)) for M={m_arg}",
                     "n": len(SEEDS) * 4000, "mismatches": bad, "match": match})

    # C3 -- srand() argument coercion, both era rules, measured against 5.40.
    args = ["3301", "CICADA3301", "3301CICADA", "0x0CE5", "3.7", "-1", "1e3",
            "4294967297", "0", "", "3301.9", " 42", "+3301"]
    coerce = []
    for a in args:
        out = sh([PERL, REF, "coerce", a]).strip().split("\t")
        ret, stream = out[0], [int(v) for v in out[1].split(",")]
        s514, uv514, div = G.srand_arg_to_seed(a, era="5.14")
        s540, uv540, _ = G.srand_arg_to_seed(a, era="5.40")
        mine540 = G.make_ks("r29", s540, 8)
        m540 = (mine540 == stream)
        ok &= m540
        coerce.append({"arg": a, "perl540_srand_ret": ret,
                       "perl540_first8": stream,
                       "my_5.40_seed32": s540, "my_5.40_first8": mine540,
                       "model_matches_running_perl": m540,
                       "my_5.14_seed32": s514, "my_5.14_uv": uv514,
                       "eras_diverge": div})
    rows.append({"gate": "C3", "what": "srand() argument coercion",
                 "match": ok, "detail": coerce})
    return ok, rows


def main():
    t0 = time.time()
    print("=" * 76)
    print("ROUND 19 / G2 -- Perl 5.14 rand/srand VALIDATION GATE")
    print("=" * 76)

    perl_v = sh([PERL, "-e", "printf('%vd', $^V)"]).strip()
    cfg = {k: sh([PERL, f"-V:{k}"]).strip() for k in
           ("randfunc", "drand01", "randbits", "nvtype", "nvsize", "ivsize")}
    print(f"installed perl: v{perl_v}")
    for k, v in cfg.items():
        print(f"  {v}")
    print()

    results = {}
    all_ok = True
    for name, fn in (("A", gate_a), ("B", gate_b), ("C", gate_c)):
        ok, rows = fn()
        all_ok &= ok
        nrow = len(rows)
        nbad = sum(1 for r in rows if r.get("match") is False)
        print(f"GATE {name}: {'PASS' if ok else 'FAIL'}   ({nrow} checks, {nbad} failing)")
        results[f"gate_{name}"] = {"pass": ok, "rows": rows}

    print()
    print(f"OVERALL: {'PASS' if all_ok else 'FAIL'}   ({time.time()-t0:.1f}s)")

    doc = {
        "lane": "round19/G2",
        "purpose": "Byte-exact reproduction of Perl 5.14.2 rand/srand before any keystream is swept.",
        "installed_perl": perl_v,
        "installed_perl_config": cfg,
        "era_target": "perl 5.14.2 as shipped by Ubuntu 12.04 LTS",
        "era_source_evidence": {
            "tarball": "https://www.cpan.org/src/5.0/perl-5.14.2.tar.gz",
            "md5": "3306fbaf976dcebdcd49b2ac0be00eb9",
            "Configure_L19280": "drand48 is the first choice whenever the libc exposes it; glibc does",
            "config_h.SH_L2131": "#define Drand01() drand48()",
            "config_h.SH_L2133": "#define seedDrand01(x) srand48((Rand_seed_t)x)  [Rand_seed_t=long, RANDBITS=48]",
            "pp.c_pp_rand": "value = POPn (or 1.0); value *= Drand01();",
            "pp.c_pp_srand": "const UV anum = (MAXARG < 1) ? seed() : POPu; seedDrand01((Rand_seed_t)anum);",
            "util.c_Perl_seed": "reads sizeof(U32) bytes from /dev/urandom; fallback mixes gettimeofday/getpid/stack ptrs into a U32",
        },
        "seed_panel": SEEDS,
        "draws_per_seed": NDRAW,
        "overall_pass": all_ok,
        **results,
    }
    with open(os.path.join(HERE, "validation.json"), "w") as f:
        json.dump(doc, f, indent=1)
    print("wrote validation.json")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
