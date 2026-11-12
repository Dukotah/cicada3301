"""R44/P2 — the p15 4x4 Arabic grid as key schedule over the 55 unsolved LP2 pages.

Exactly as pre-registered in PREREG.md (dated 2026-11-09, before any sweep output):
  (a)  repeating keystreams: 16 cell orders x 5 value maps x 6 configs x all rotations
  (a') one-shot digit keystreams (decode >= 60)
  (b)  period-16 rank-permutation block transposition (8 perms x atbash)
  (c)  grid-seeded prime/totient ladder streams (44 x 6 configs)
  (d)  index-map census (measured-only, no bar claim)
N = 12,184 adjudicated cells per page; bars fixed in PREREG: 12.9560 (L_cap 120),
17.3303 (L_cap 240).  Three positive controls planted through THIS glue run first;
any plant failure kills the lane.  Standing instrument: panel-R36 adjudicate/
adjudicate_batch + bars_v3 free bar of record.  Pure python3, no network, no git.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis", "src", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))

from run_stats import load_pages      # noqa
from lp import gematria as gp         # noqa
import adjudicate as A                # noqa
import bars_v3 as B                   # noqa

N = 29
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
BARS = {120: float(B.bar_v3(12184, 120, "free")),
        240: float(B.bar_v3(12184, 240, "free"))}

# ------------------------------------------------------------- the verified grid (PREREG)
G16 = [3258, 3222, 3152, 3038,
       3278, 3299, 3298, 2838,
       3288, 3294, 3296, 2472,
       4516, 1206, 708, 1820]
RED = 5                      # row-major index of the red 3299 cell
D16 = [3301 - g for g in G16]

# ---- primes / totients (pure sieve; verified against sympy in prereg arithmetic)
LIMIT = 7000
sieve = np.ones(LIMIT, bool); sieve[:2] = False
for i in range(2, int(LIMIT ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i::i] = False
PRIMES = np.nonzero(sieve)[0]                       # PRIMES[0] = 2 (0-based array)
PSET = set(PRIMES.tolist())
PHI = np.arange(LIMIT)
for i in range(2, LIMIT):
    if sieve[i]:
        PHI[i::i] -= PHI[i::i] // i


def primepi(n):
    """1-based prime index: primepi(2) = 1."""
    return int(np.searchsorted(PRIMES, n, side="right"))


# ------------------------------------------------------------- cell orders (16, PREREG)
RM = list(range(16))
CM = [r * 4 + c for c in range(4) for r in range(4)]
TRAVERSALS = {"RM": RM, "CM": CM, "RMr": RM[::-1], "CMr": CM[::-1]}


def red_treat(seq, mode):
    s = list(seq)
    if mode == "asis":
        return s
    s.remove(RED)
    if mode == "drop":
        return s
    return [RED] + s if mode == "first" else s + [RED]


ORDERS = {f"{t}-{r}": red_treat(seq, r)
          for t, seq in TRAVERSALS.items()
          for r in ("asis", "drop", "first", "last")}

# ------------------------------------------------------------- value maps (5, PREREG)


def map_values(order, vmap):
    cells = [G16[i] for i in order]
    if vmap == "v1":
        return [g % N for g in cells]
    if vmap == "v2":
        return [(3301 - g) % N for g in cells]
    if vmap == "v3":
        return [(3301 - g) % N for g in cells if (3301 - g) in PSET]
    if vmap == "v4":
        return [primepi(3301 - g) % N for g in cells if (3301 - g) in PSET]
    if vmap == "v5":
        return [int(d) for g in cells for d in str(g)]
    raise ValueError(vmap)


KEYS = [(f"{oname}/{v}", np.array(map_values(order, v), dtype=np.int64))
        for oname, order in ORDERS.items() for v in ("v1", "v2", "v3", "v4", "v5")]

CONFIGS = ["vigm", "vigp", "beau", "vigm_atb", "vigp_atb", "beau_atb"]


def decode_rows(c_row, kk):
    """c_row (L,), kk (B, L) -> decode matrix (6B, L), config-major order CONFIGS."""
    c = c_row[None, :]
    ca = (N - 1) - c
    return np.concatenate([(c - kk) % N, (c + kk) % N, (kk - c) % N,
                           (ca - kk) % N, (ca + kk) % N, (kk - ca) % N], axis=0)


# ------------------------------------------------------------- (b) permutations (PREREG)
def perms():
    out = []
    for rd in ("RM", "CM"):
        vals = np.array([G16[i] for i in TRAVERSALS[rd][:16]]) if rd == "CM" \
            else np.array(G16)
        # (for CM the traversal IS the reading order of the 16 values)
        for dname, v in (("asc", vals), ("desc", -vals)):
            pa = np.argsort(v, kind="stable")
            inv = np.empty(16, dtype=np.int64)
            inv[pa] = np.arange(16)
            out.append((f"perm/{rd}-{dname}", pa))
            out.append((f"perm/{rd}-{dname}-inv", inv))
    return out


PERMS = perms()


def transpose_page(c, P):
    out = c.copy()
    nb = len(c) // 16
    blk = c[:nb * 16].reshape(nb, 16)
    out[:nb * 16] = blk[:, P].reshape(-1)
    return out


# ------------------------------------------------------------- (c) generator streams
LMAX = 300


def gen_streams():
    out = []
    for gi, d in enumerate(D16):
        if d in PSET:
            s = primepi(d)                     # 1-based; PRIMES[s-1] == d
            run = PRIMES[s - 1: s - 1 + LMAX].astype(np.int64)
            out.append((f"gen/t1-pi{s}", run % N))
            out.append((f"gen/t2-pi{s}", (run - 1) % N))
    for g in G16:
        out.append((f"gen/phi-{g}", PHI[g: g + LMAX].astype(np.int64) % N))
    return out


GENS = gen_streams()


def l_cap(L):
    return 240 if L >= 240 else 120


# ------------------------------------------------------------- the per-page sweep
def sweep_page(c):
    """c: np.int64 array. Returns (rows_meta, X) lazily evaluated in chunks; yields
    (meta_list, decode_matrix) groups of equal row length."""
    L = len(c)
    # (a) repeating
    for kname, K in KEYS:
        Lk = len(K)
        idx = (np.arange(Lk)[:, None] + np.arange(L)[None, :]) % Lk
        kk = K[idx]                                              # (Lk, L)
        X = decode_rows(c, kk)
        meta = [(f"a:{kname}:{cfg}:rot{r}", L)
                for cfg in CONFIGS for r in range(Lk)]
        yield meta, X
    # (a') one-shot digits (non-drop orders, Lk=63, r 0..3)
    for kname, K in KEYS:
        if not kname.endswith("/v5") or len(K) != 63:
            continue
        for r in range(4):
            Ld = min(63 - r, L)
            if Ld < 60:
                continue
            kk = K[r:r + Ld][None, :]
            X = decode_rows(c[:Ld], kk)
            meta = [(f"o:{kname}:{cfg}:r{r}", Ld) for cfg in CONFIGS]
            yield meta, X
    # (b) transposition
    rows, meta = [], []
    for pname, P in PERMS:
        t = transpose_page(c, P)
        rows.append(t); meta.append((f"b:{pname}:plain", L))
        rows.append((N - 1) - t); meta.append((f"b:{pname}:atb", L))
    yield meta, np.stack(rows)
    # (c) generators
    for gname, S in GENS:
        kk = S[:L][None, :]
        X = decode_rows(c, kk)
        yield [(f"c:{gname}:{cfg}", L) for cfg in CONFIGS], X


def run_page(c, tag):
    """Full fixed grid over one page. Returns dict with best cell + crossers."""
    c = np.asarray(c, dtype=np.int64)
    n_cells = 0
    cand = []                                    # (pmax, kid, L, decode) candidates
    for meta, X in sweep_page(c):
        r = A.adjudicate_batch(X, pan=PAN)
        n_cells += len(meta)
        pm = r["pmax"]
        bar_here = BARS[l_cap(meta[0][1])]
        take = set(np.nonzero(pm >= bar_here)[0].tolist())
        take.add(int(pm.argmax()))
        for i in sorted(take):
            cand.append((float(pm[i]), meta[i][0], meta[i][1], X[i].copy()))
    cand.sort(key=lambda t: -t[0])
    best, crossers = None, []
    for pmax, kid, Ld, dec in cand[:64]:
        full = A.adjudicate(dec, pan=PAN)
        row = {"kid": kid, "L": int(Ld), "pmax": round(float(full["pmax"]), 3),
               "preg": int(full["preg"]), "pmax_ne": round(float(full["pmax_ne"]), 3),
               "ioc": round(float(full["ioc"]), 4), "mds": int(full["mds"]),
               "h2": round(float(full["h2"]), 4), "zl": round(float(full["zl"]), 4),
               "degenerate": bool(full["degenerate"]),
               "bar": round(BARS[l_cap(Ld)], 4)}
        if full["pmax"] >= BARS[l_cap(Ld)] and not full["degenerate"]:
            row["decode_head"] = A.idx_to_trans(dec[:96])
            crossers.append(row)
        if best is None and not full["degenerate"]:
            best = row
    if best is None and cand:            # every candidate degenerate: record the top anyway
        pmax, kid, Ld, dec = cand[0]
        best = {"kid": kid, "L": int(Ld), "pmax": round(pmax, 3),
                "degenerate": True, "bar": round(BARS[l_cap(Ld)], 4)}
    return {"page": tag, "L": int(len(c)), "n_cells": n_cells,
            "bar": round(BARS[l_cap(len(c))], 4), "best": best,
            "crossers": crossers}


# ------------------------------------------------------------- positive controls (PREREG)
def to_idx(text):
    out = []
    for w in text.split():
        try:
            out.extend(gp.keyword_to_indices(w))
        except Exception:
            pass
    return out


PT1 = ("A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE "
       "KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE "
       "MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED SOME WISDOM "
       "THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS")
PT2 = ("WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP "
       "BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN "
       "END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR "
       "REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF")
PT3 = ("SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO "
       "DESTROY ALL THAT YOU OWN AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY A KOAN DURING A "
       "LESSON THE MASTER EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID WHEN "
       "ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID IT IS A VOICE INSIDE YOUR HEAD")


def build_plants():
    plants = []
    # PA: v2 / RM-asis keystream, encrypt c=(p+K_rot7)%29 -> decoded by a:RM-asis/v2:vigm:rot7
    p = np.array(to_idx(PT1)[:240], dtype=np.int64)
    K = np.array(map_values(ORDERS["RM-asis"], "v2"), dtype=np.int64)
    kk = K[(7 + np.arange(len(p))) % len(K)]
    plants.append(("PA", (p + kk) % N, "a:RM-asis/v2:vigm:rot7", p))
    # PB: transposition, encrypt with inverse of perm/RM-asc -> decoded by b:perm/RM-asc:plain
    p = np.array(to_idx(PT2)[:224], dtype=np.int64)
    P = dict(PERMS)["perm/RM-asc"]
    enc = p.copy()
    blk = p.reshape(-1, 16)
    e = np.empty_like(blk)
    e[:, P] = blk
    enc = e.reshape(-1)
    plants.append(("PB", enc, "b:perm/RM-asc:plain", p))
    # PC: phi-of-prime ladder at s=pi(2593)=378, encrypt c=28-((p-K)%29) -> c:gen/t2-pi378:vigp_atb
    p = np.array(to_idx(PT3)[:240], dtype=np.int64)
    s = primepi(2593)
    K = ((PRIMES[s - 1: s - 1 + len(p)] - 1) % N).astype(np.int64)
    plants.append(("PC", ((N - 1) - ((p - K) % N)) % N, f"c:gen/t2-pi{s}:vigp_atb", p))
    return plants


def run_plants():
    out, ok = [], True
    for name, cipher, cell, p in build_plants():
        res = run_page(cipher, f"plant-{name}")
        best = res["best"]
        # recompute the planted cell's decode for recovery check
        hit = best is not None and best["kid"] == cell
        rec = None
        if hit:
            # recover: find the decode again through the sweep candidates was consumed;
            # re-derive directly from the kid for the recovery fraction
            dec = decode_from_kid(np.asarray(cipher, dtype=np.int64), cell)
            rec = float((dec[:len(p)] == p[:len(dec)]).mean())
        passed = bool(hit and best["pmax"] >= best["bar"] and not best["degenerate"]
                      and rec is not None and rec >= 0.99)
        out.append({"plant": name, "planted_cell": cell, "grid_best": best,
                    "found_planted_cell": hit, "recovery": rec, "passed": passed})
        ok &= passed
        print(f"  plant {name}: best={best['kid']} pmax={best['pmax']} "
              f"bar={best['bar']} hit={hit} rec={rec} -> "
              f"{'PASS' if passed else 'FAIL'}", flush=True)
    return ok, out


def decode_from_kid(c, kid):
    """Re-execute a single named cell (used only for plant recovery verification)."""
    kind = kid.split(":")[0]
    if kind == "a":
        _, kname, cfg, rot = kid.split(":")
        K = dict(KEYS)[kname]
        r = int(rot[3:])
        kk = K[(r + np.arange(len(c))) % len(K)][None, :]
        return decode_rows(c, kk)[CONFIGS.index(cfg)]
    if kind == "b":
        _, pname, mode = kid.split(":")
        t = transpose_page(c, dict(PERMS)[pname])
        return t if mode == "plain" else (N - 1) - t
    _, gname, cfg = kid.split(":")
    S = dict(GENS)[gname]
    kk = S[:len(c)][None, :]
    return decode_rows(c, kk)[CONFIGS.index(cfg)]


# ------------------------------------------------------------- (d) index-map census
def census(pages):
    stream = np.concatenate([np.asarray(p, dtype=np.int64) for p in pages])
    posD = [d for d in D16 if d > 0]
    def extract(idxs):
        sel = [int(stream[i]) for i in idxs if 0 <= i < len(stream)]
        return {"indices": list(map(int, idxs)), "runes": A.idx_to_trans(sel)}
    return {
        "note": "measured-only census (PREREG d); n=16 is below any adjudication floor — "
                "no verdict is claimed from these strings",
        "stream_len": int(len(stream)),
        "page_select_G_mod55": [g % 55 for g in G16],
        "page_select_D_mod55": [d % 55 for d in posD],
        "rune_at_G_rowmajor": extract(G16),
        "rune_at_G_sorted": extract(sorted(G16)),
        "rune_at_posD_rowmajor": extract(posD),
        "rune_at_posD_sorted": extract(sorted(posD)),
    }


# ------------------------------------------------------------- main
def main():
    t0 = time.time()
    print(f"bars of record: {BARS}", flush=True)
    assert primepi(2593) == 378 and primepi(2) == 1
    # grid-arithmetic self-check against PREREG N
    probe = np.zeros(240, dtype=np.int64)
    n_probe = sum(len(m) for m, _ in sweep_page(probe))
    assert n_probe == 12184, f"grid N mismatch: {n_probe} != 12184 (PREREG)"
    print(f"grid N per page verified = {n_probe}", flush=True)

    print("plants (gate — lane killed on any failure):", flush=True)
    ok, plant_rows = run_plants()
    out = {"bars": {str(k): round(v, 4) for k, v in BARS.items()},
           "grid_per_page": 12184, "plants": plant_rows, "plants_passed": ok}
    if not ok:
        out["verdict"] = "KILLED — positive control failed; no keystream verdict issued"
        json.dump(out, open(os.path.join(HERE, "p2_results.json"), "w"), indent=1)
        print("PLANT FAILURE — lane killed."); return

    pages = load_pages()[:-2]
    per_page, crossers, gbest = [], [], None
    for pi, c in enumerate(pages):
        r = run_page(c, pi)
        per_page.append(r)
        crossers.extend(r["crossers"])
        b = r["best"]
        if b and not b.get("degenerate") and (gbest is None or b["pmax"] > gbest["pmax"]):
            gbest = dict(b, page=pi)
        if pi % 10 == 0:
            print(f"  page {pi}/{len(pages)} gbest "
                  f"{gbest['pmax'] if gbest else '-'} {time.time()-t0:.0f}s", flush=True)

    out.update({
        "n_pages": len(pages),
        "n_decodes_total": 12184 * len(pages),
        "observed_global_best": gbest,
        "n_crossers": len(crossers), "crossers": crossers,
        "verdict": "NEGATIVE" if not crossers else "CROSSER(S) — FLAGGED-FOR-ORACLE",
        "per_page_best": [{"page": r["page"], "L": r["L"], "bar": r["bar"],
                           "best": r["best"]} for r in per_page],
        "elapsed_s": round(time.time() - t0, 1)})
    json.dump(out, open(os.path.join(HERE, "p2_results.json"), "w"), indent=1)
    json.dump(census(pages), open(os.path.join(HERE, "p2_census.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("grid_per_page", "n_decodes_total",
          "observed_global_best", "n_crossers", "verdict", "elapsed_s")}, indent=1))


if __name__ == "__main__":
    main()
