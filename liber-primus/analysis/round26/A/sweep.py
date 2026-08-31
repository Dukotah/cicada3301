#!/usr/bin/env python3
"""Round 26 - Lane A: fire the built-but-never-swept derived-key generators.

Sweeps the PRIOR-DENSE seed slice of three byte-exact validated generators through
the repo skip-aware decoder (keyskip1 AND keyskip2) and certifies with hitfn20.

  (1) Perl rand      -- gen_perl.make_ks(red, seed, nsym)      [R19-G2: ZERO swept]
  (2) TeX RNG        -- gen_tex.make_ks(gen, seed, nsym)       [G4-TEX-RNG: ZERO swept]
  (3) Py2.7 reducers -- gen_py27.keystream(seed, mode, n, wordsize, jump)
                        DISTINCT axis vs R21-L3: wordsize=64 (amd64 2-word init_by_array,
                        NC-2), non-zero offsets (jump ladder), keyskip2 (NC-4).

Each generator passes a plant-and-recover CONTROL (>=0.90) BEFORE its sweep counts.

Run:  python3 sweep.py            # writes control.json, sweep.jsonl, RESULTS.md scaffold data
"""
import os, sys, json, random, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "benchmark",
          os.path.join("analysis", "campaign18_skip"),
          os.path.join("analysis", "round19", "I1"),
          os.path.join("analysis", "round19", "G2"),
          os.path.join("analysis", "round19", "G3"),
          os.path.join("analysis", "round19", "G4"),
          os.path.join("analysis", "round20", "HITFN")):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

from lp import corpus, gematria as gp        # noqa
import skipdecode as sk                       # noqa  (eng_to_idx, encipher_keyskip)
import driftbeam as DB                        # noqa
import hitfn20 as HF                          # noqa
import gen_perl, gen_tex, gen_py27            # noqa

N = gp.N
RECOVERY_BAR = 0.90
L_CONTROL = 240
CONTROL_SEEDS = 7

# ------------------------------------------------------------------ generators
# Each entry: (label, keystream_fn(seed, n) -> list[int] in Z_29, axis_meta)
# Perl reductions actually used (Perl-reachable set).
PERL_REDS = ["r29", "r29_nodup", "r32_rej", "r256_mod", "r2p32_mod",
             "r26_lat", "raw48_mod", "lrand48_mod"]
# TeX generators (doctrine names -> actual GEN_NAMES).
TEX_GENS = ["pgf_rnd29", "lcg_mod29", "randomtex_div29", "pdftex_u29"]
# Py2.7 reducers, DISTINCT axis (wordsize=64, offsets); i386/offset0/keyskip1 excluded.
PY27_MODES = ["grb5_mod", "grb5_rej", "shuffle29"]
PY27_OFFSETS = [0, 1, 2, 3, 5, 7, 13]        # non-zero offsets = NEW vs R21-L3
PY27_WORDSIZE = 64                           # amd64 2-word init_by_array = NC-2

DECODE_PRESETS = ["exact", "pair"]           # keyskip1 (repo) + keyskip2 (skip_by_two)


# ------------------------------------------------------------ prior-dense seeds
def build_seed_dictionary():
    """ALL corpus-derived candidate seeds FIRST (doctrine R5). Returns list of
    (seed_value, kind) where seed_value is int OR str (str -> py27 hash path)."""
    seeds = []
    seen = set()

    def add(v, kind):
        key = (repr(v), kind)
        if key not in seen:
            seen.add(key)
            seeds.append((v, kind))

    # -- Cicada / 3301 motifs (ints)
    for v in [3301, 1033, 761, 845145127, 29, 3, 7, 13, 1595277641,
              1, 0, 42, 2, 5, 11, 17, 19, 23, 31, 37, 41, 43, 47, 53, 59]:
        add(v, "int_motif")

    # -- primes (first 200) : Cicada's central motif
    def primes(n):
        out, c = [], 2
        while len(out) < n:
            if all(c % p for p in out if p * p <= c):
                out.append(c)
            c += 1
        return out
    for p in primes(200):
        add(p, "int_prime")

    # -- dates (era-plausible srand(time) literals, day granularity 2011-2015)
    #    plus the four canonical Cicada year-anchors as small ints
    for y in (2011, 2012, 2013, 2014, 2015):
        add(y, "int_year")
    # unix-day epochs across the era, sparse (1 per ~30 days) -> bounded
    t0, t1 = 1293840000, 1420070400          # 2011-01-01 .. 2015-01-01
    for t in range(t0, t1, 30 * 86400):
        add(t, "int_epoch_day")

    # -- gematria (prime sums) of solved-LP thematic words + string seeds themselves
    THEMATIC = ["CICADA", "CICADA3301", "3301", "DIVINITY", "PRIMES",
                "THEPRIMESARESACRED", "WELCOME", "PILGRIM", "INSTAR",
                "EMERGENCE", "WISDOM", "CIRCUMFERENCE", "CONSUMPTION",
                "PRESERVATION", "ADHERENCE", "TOTIENT", "MOBIUS", "SHADOW",
                "KOAN", "PARABLE", "COMMAND", "TUNNEL", "AWAKENING",
                "ANEND", "TRUTH", "LOSS", "MOURNFUL", "PROGRESS",
                "REALITY", "DECEPTION", "ENLIGHTENMENT", "SACRED",
                "THELOSSOFDIVINITY", "ANINSTRUCTION", "AKOAN"]
    for w in THEMATIC:
        # gematria prime-sum value as an int seed
        try:
            idxs = gp.keyword_to_indices(w) if hasattr(gp, "keyword_to_indices") else None
        except Exception:
            idxs = None
        if idxs is None:
            idxs = sk.eng_to_idx(w)
        gsum = sum(gp.RUNE_TO_PRIME.get(gp.IDX_TO_RUNE[i % N], 0) for i in idxs)
        add(gsum, "int_gematria")
        # the WORD itself as a Python-2 string seed (hash path; wordsize matters)
        add(w, "str_word")

    return seeds


SEED_DICT = build_seed_dictionary()

# small stated dense-from-0 baseline (AFTER prior-dense) -- bounded slice
DENSE_BASELINE = list(range(0, 400))         # 400 seeds / 2^32 = 9.3e-8 per space (small stated slice)


# ------------------------------------------------------------------ real target
def load_real_target():
    pages = corpus.parse()
    pg = pages[19]                            # unsolved '23.jpg,24.jpg', 333 runes, 0-54 band
    C = gp.runes_to_indices(pg["runes"])
    return C, pg.get("label", "idx19")


REAL_C, REAL_LABEL = load_real_target()


# -------------------------------------------------------------------- controls
def english_stream():
    p = os.path.join(LP, "data", "keys", "self_reliance.txt")
    with open(p, encoding="utf-8", errors="ignore") as f:
        return sk.eng_to_idx(f.read())[5000:]


ENG = english_stream()


def take_plain(Ln, seed):
    r = random.Random(9000 + seed)
    s = r.randrange(0, len(ENG) - Ln - 1)
    return ENG[s:s + Ln]


def control_for(genlabel, ks_fn):
    """Plant a keystream from THIS generator, encipher held-out English under the
    keyskip1 encipher relation, prove hitfn20 recovers >=0.90 (HIT on plant).
    Returns (validated, median_recovery, detail_rows)."""
    recs, rows = [], []
    for s in range(CONTROL_SEEDS):
        P = take_plain(L_CONTROL, s)
        need = L_CONTROL * 12 + 64
        K = ks_fn(need)                       # keystream from generator-under-test
        # encipher under repo keyskip1 relation (the plant the panel is built for)
        C, skips, used = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301 + s)
        dec = HF.HitDecode(C=C, K=K, o=0, preset="exact",
                           n_round_adjudicated=SWEEP_N, truth_idx=P)
        v = HF.evaluate(dec)
        recs.append(v.recovery)
        rows.append({"seed": 3301 + s, "recovery": v.recovery, "hit": v.hit,
                     "pmax": v.pmax, "bar": v.bar, "heldout": v.heldout_recovery})
    recs.sort()
    med = recs[len(recs) // 2]
    validated = med >= RECOVERY_BAR
    return validated, med, rows


# --------------------------------------------------------------------- the sweep
# N THIS lane adjudicates: bounds the panel-max bar. Count all decodes we run.
def count_decodes():
    n_perl = len(PERL_REDS) * (len(SEED_DICT) + len(DENSE_BASELINE)) * len(DECODE_PRESETS)
    n_tex = len(TEX_GENS) * (len(SEED_DICT) + len(DENSE_BASELINE)) * len(DECODE_PRESETS)
    # py27: str seeds only take the wordsize path meaningfully; int seeds ignore wordsize
    # but we still exercise offsets. We sweep the full dict + baseline over offsets.
    n_py = (len(PY27_MODES) * (len(SEED_DICT) + len(DENSE_BASELINE))
            * len(PY27_OFFSETS) * len(DECODE_PRESETS))
    return n_perl + n_tex + n_py


SWEEP_N = 10 ** 6   # conservative bar-N (>= actual decode count); fixed in advance


def decode_row(C_real, K, preset, gen, axis, seed, kind, offset, wordsize):
    """Run one real-target decode, persist R3 language-agnostic stats, return row."""
    dec = HF.HitDecode(C=C_real, K=K, o=0, preset=preset, n_round_adjudicated=SWEEP_N)
    v = HF.evaluate(dec)
    d = HF._full_decode(dec)
    plain = d["plain_idx"]
    # R3 stats
    distinct = len(set(plain))
    # min distinct symbols over any 32-rune window
    win = 32
    if len(plain) >= win:
        mind = min(len(set(plain[i:i + win])) for i in range(0, len(plain) - win + 1))
    else:
        mind = distinct
    # IoC * N
    from collections import Counter
    cnt = Counter(plain)
    Ln = len(plain)
    ioc = (sum(f * (f - 1) for f in cnt.values()) / (Ln * (Ln - 1))) * N if Ln > 1 else 0.0
    row = {
        "gen": gen, "axis": axis, "seed": repr(seed), "kind": kind,
        "offset": offset, "wordsize": wordsize, "preset": preset,
        "pmax": round(v.pmax, 4), "bar": round(v.bar, 4),
        "clears_bar": bool(v.pmax >= v.bar),
        "recovery": round(v.recovery, 4), "heldout": round(v.heldout_recovery, 4),
        "hit": bool(v.hit), "preg": v.preg, "preg_name": v.preg_name,
        "score": round(v.score, 4), "ioc_x_N": round(ioc, 4),
        "min_distinct_32": mind, "distinct": distinct, "n": len(plain),
    }
    return row


def run_sweep(fh, max_rows=None):
    """Sweep prior-dense dict FIRST, then dense baseline. Persist every row."""
    n_target = len(REAL_C)
    need = n_target * 12 + 64
    best = {"pmax": -1e9}
    n = 0
    clears = []

    def emit(gen, axis, seed, kind, offset, wordsize, ks):
        nonlocal n, best
        for preset in DECODE_PRESETS:
            row = decode_row(REAL_C, ks, preset, gen, axis, seed, kind, offset, wordsize)
            fh.write(json.dumps(row) + "\n")
            n += 1
            if row["pmax"] > best["pmax"]:
                best = row
            if row["clears_bar"]:
                clears.append(row)
            if max_rows and n >= max_rows:
                return True
        return False

    ordered = [("prior_dense", SEED_DICT)] + [("dense_baseline", [(v, "dense0") for v in DENSE_BASELINE])]
    for axis, seedset in ordered:
        for seed, kind in seedset:
            # (1) Perl -- int seeds only (make_ks masks to 32-bit)
            if isinstance(seed, int):
                for red in PERL_REDS:
                    ks = gen_perl.make_ks(red, seed, need)
                    if emit("perl:" + red, axis, seed, kind, 0, 32, ks):
                        return n, best, clears
            # (2) TeX -- int seeds only
            if isinstance(seed, int):
                for g in TEX_GENS:
                    ks = gen_tex.make_ks(g, seed, need)
                    if emit("tex:" + g, axis, seed, kind, 0, 32, ks):
                        return n, best, clears
            # (3) Py2.7 -- wordsize=64 + offset ladder (DISTINCT vs R21-L3)
            for mode in PY27_MODES:
                for off in PY27_OFFSETS:
                    jump = None if off == 0 else off
                    ks = gen_py27.keystream(seed, mode, need,
                                            wordsize=PY27_WORDSIZE, jump=jump)
                    if emit("py27:" + mode, axis, seed, kind, off, PY27_WORDSIZE, ks):
                        return n, best, clears
    return n, best, clears


# ------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    out = {"lane": "round26/A", "date": "2026-08-31",
           "real_target": REAL_LABEL, "real_len": len(REAL_C),
           "recovery_bar": RECOVERY_BAR, "sweep_N": SWEEP_N,
           "seed_dict_size": len(SEED_DICT), "dense_baseline": len(DENSE_BASELINE),
           "planned_decodes": count_decodes()}

    # ---- CONTROLS (mandatory, before any null counts) ----
    need = len(REAL_C) * 12 + 64
    controls = {}
    # Perl control on a representative reduction
    ok_p, med_p, rows_p = control_for(
        "perl:r29", lambda n: gen_perl.make_ks("r29", 3301, n))
    controls["perl"] = {"validated": ok_p, "median_recovery": med_p, "rows": rows_p}
    # TeX control
    ok_t, med_t, rows_t = control_for(
        "tex:pgf_rnd29", lambda n: gen_tex.make_ks("pgf_rnd29", 3301, n))
    controls["tex"] = {"validated": ok_t, "median_recovery": med_t, "rows": rows_t}
    # Py2.7 control (wordsize=64 string seed, the distinct axis)
    ok_y, med_y, rows_y = control_for(
        "py27:grb5_mod", lambda n: gen_py27.keystream("CICADA3301", "grb5_mod", n,
                                                      wordsize=64))
    controls["py27"] = {"validated": ok_y, "median_recovery": med_y, "rows": rows_y}
    out["controls"] = controls
    out["control_min_recovery"] = min(med_p, med_t, med_y)
    out["all_controls_validated"] = bool(ok_p and ok_t and ok_y)

    json.dump(out, open(os.path.join(HERE, "control.json"), "w"), indent=1)
    print("CONTROLS: perl %.3f  tex %.3f  py27 %.3f  (bar %.2f)  all_ok=%s"
          % (med_p, med_t, med_y, RECOVERY_BAR, out["all_controls_validated"]))

    if not out["all_controls_validated"]:
        print("STOP: a generator control did not recover its plant >=0.90; its null is void.")
        # still write partial; sweep only counts for validated gens, but we abort for honesty
        return out

    # ---- SWEEP ----
    sweep_path = os.path.join(HERE, "sweep.jsonl")
    with open(sweep_path, "w") as fh:
        n, best, clears = run_sweep(fh)
    out["decodes_run"] = n
    out["best_pmax_row"] = best
    out["n_clears_bar"] = len(clears)
    out["clears_bar_rows"] = clears
    out["hits"] = [r for r in clears if r["hit"]]
    out["elapsed_sec"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "control.json"), "w"), indent=1)
    print("SWEEP: %d decodes, best pmax %.4f (bar %.4f) reg=%s, clears=%d, hits=%d, %.1fs"
          % (n, best["pmax"], best["bar"], best.get("preg_name"),
             len(clears), len(out["hits"]), out["elapsed_sec"]))
    return out


if __name__ == "__main__":
    main()
