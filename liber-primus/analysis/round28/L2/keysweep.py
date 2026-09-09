#!/usr/bin/env python3
"""Round 28 L2 — variant-enumerated direct-key battery over the pp49-51 payload.

Anti-repeat position (PREREG Amendment 1): pp49_51/keytest.py's additive/Beaufort/atbash
battery has only ever been run on the `maj` and `decpref` streams; B-05 ran the 64
contested-cell combination masks only through its PRF-EXPANSION grid; C1's propagation
re-ran the B-05 PRF grid on payload_resolved.bin. Nobody has run the DIRECT-key battery
over the contested-cell Cartesian product nor over payload_resolved.bin.

Family swept here: 2 bases (canon majority; payload_resolved ie 45/50/246 corrected)
x 2^6 contested-cell masks (cells 25/175/182/199/215/237, each tok-vs-decimal reading)
= 128 payload variants. canon_256_decpref.bin is the all-decimal corner of base 0;
payload_resolved.bin is the zero mask of base 1.

Order of operations (doctrine mechanic 2):
  1. PLANT control through the real code path (variant enum -> battery -> leaderboard):
     English page enciphered with variant #37 at offset 42; must be recovered top-1 with
     >=0.90 rune recovery. Hard stop otherwise.
  2. NULL calibration: 12 shuffled payloads through the identical battery; Gumbel fit
     from order statistics (benchmark/null.py doctrine: extreme values, never bulk sd).
  3. Family-wise bar at alpha=0.01 for the full family size.
  4. Real sweep, R3 stats persisted per row (variant x target, best config).

Outputs: plant_control.json, null_calibration.json, sweep_rows.jsonl, sweep_summary.json
"""
import json, math, os, random, sys, time, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis"))
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))

from lp import gematria as gp, ciphers, score as _score
from run_stats import load_pages, english_baseline
import adjudicate as adj

N = gp.N
SC = _score.default()
HIST_BAR = -5.2          # historical single-battery bar, reported not used
ALPHA = 0.01
EULER_GAMMA = 0.5772156649015329
NULL_RUNS = 12
CONTESTED = [(25, 198, 224), (175, 18, 44), (182, 167, 141),
             (199, 47, 21), (215, 84, 5), (237, 32, 58)]
RESOLVED_FIX = {45: 107, 50: 47, 246: 198}   # A-04 / round19-C1 payload_resolved.bin

canon = list(open(os.path.join(LP, "analysis", "pp49_51", "canon_256.bin"), "rb").read())
resolved_ref = list(open(os.path.join(LP, "analysis", "round19", "C1",
                                      "payload_resolved.bin"), "rb").read())
decpref_ref = list(open(os.path.join(LP, "analysis", "pp49_51",
                                     "canon_256_decpref.bin"), "rb").read())

def make_variant(base_id, mask):
    p = list(canon)
    if base_id == 1:
        for i, v in RESOLVED_FIX.items(): p[i] = v
    for j, (i, tok, dec) in enumerate(CONTESTED):
        p[i] = dec if (mask >> j) & 1 else tok
    return p

# sanity: corners reproduce the reference streams exactly
assert make_variant(1, 0) == resolved_ref
assert make_variant(0, 63) == decpref_ref
assert make_variant(0, 0) == canon

VARIANTS = [(f"b{b}m{m:02d}", make_variant(b, m)) for b in (0, 1) for m in range(64)]
# mod-29 distinctness (additive family only sees key mod 29)
seen = {}
for vid, p in VARIANTS:
    k = tuple(x % N for x in p)
    if k in seen: raise SystemExit(f"mod-29 collision {vid} == {seen[k]}")
    seen[k] = vid

pages = load_pages()
unsolved = pages[:-2]
corpus = [i for p in unsolved for i in p]
TARGETS = [(f"page{i}(len{len(p)})", p, len(p) <= 400) for i, p in enumerate(unsolved)]
TARGETS.append(("CORPUS", corpus, False))

def battery(payload, targets, keep_top=0):
    """Identical construction set to pp49_51/keytest.py, one payload (+reverse).
    Returns per-target best (score, mode, plain) and count; optional global top list."""
    base = [b % N for b in payload]
    streams = [("f", base), ("r", base[::-1])]
    best = {}
    nconf = 0
    top = []
    for tname, idxs, sweep_off in targets:
        L = len(idxs)
        offsets = range(256) if sweep_off else (0,)
        tb = (-1e9, None, None)
        for sname, key in streams:
            for sign in (-1, +1):
                for atbash in (False, True):
                    src = ciphers.atbash_indices(idxs) if atbash else idxs
                    for beaufort in (False, True):
                        if beaufort and sign == +1: continue
                        for off in offsets:
                            stream = [key[(off + i) % 256] for i in range(L)]
                            if beaufort:
                                p = [(stream[i] - c) % N for i, c in enumerate(src)]
                            else:
                                p = [(c + sign * stream[i]) % N for i, c in enumerate(src)]
                            sc = SC.score_norm(gp.indices_to_translit(p))
                            nconf += 1
                            if sc > tb[0]:
                                tb = (sc, f"{sname} sign{sign:+d}"
                                          f"{' atbash' if atbash else ''}"
                                          f"{' beaufort' if beaufort else ''} off{off}", p)
                            if keep_top:
                                top.append((sc, tname))
        best[tname] = tb
    if keep_top:
        top.sort(reverse=True); top = top[:keep_top]
    return best, nconf, top

# ------------------------------------------------------------------ 1. PLANT CONTROL
def plant_control():
    plain = english_baseline()[:131]
    kvid, kpay = VARIANTS[37]
    key = [b % N for b in kpay]
    # OFF=160: the 131-rune key window {160..290 mod 256} covers ALL 6 contested cells
    # (25/175/182/199/215/237) and resolved cell 246, so the planted variant is uniquely
    # identifiable. (First attempt used OFF=42, whose window covers none of the 6 — all
    # 64 masks tie and the control rightly failed; recorded in RESULTS.)
    OFF = 160
    cipher = [(p + key[(OFF + i) % 256]) % N for i, p in enumerate(plain)]
    tgt = [("PLANT(len131)", cipher, True)]
    rows = []
    for vid, pay in VARIANTS:
        best, _, _ = battery(pay, tgt)
        sc, mode, dec = best["PLANT(len131)"]
        rows.append((sc, vid, mode, dec))
    rows.sort(reverse=True, key=lambda r: r[0])
    sc, vid, mode, dec = rows[0]
    rec = sum(1 for a, b in zip(dec, plain) if a == b) / len(plain)
    out = {"planted": {"variant": kvid, "offset": OFF, "config": f"f sign-1 off{OFF}"},
           "top1": {"variant": vid, "mode": mode, "score": sc, "recovery": rec},
           "runner_up": {"variant": rows[1][1], "score": rows[1][0]},
           "english_baseline_score": SC.score_norm(gp.indices_to_translit(plain)),
           "hit": bool(vid == kvid and f"sign-1 off{OFF}" in mode and rec >= 0.90)}
    json.dump(out, open(os.path.join(HERE, "plant_control.json"), "w"), indent=1)
    print(f"PLANT: top1={vid} {mode} score={sc:.3f} recovery={rec:.3f} "
          f"runner-up {rows[1][1]} {rows[1][0]:.3f}  HIT={out['hit']}")
    if not out["hit"]:
        raise SystemExit("PLANT CONTROL FAILED — sweep must not run.")

# ------------------------------------------------------------------ 2. NULL CALIBRATION
def null_calibration():
    per_run_max, pooled_scores_max, nconf1 = [], -1e9, None
    for s in range(NULL_RUNS):
        rng = random.Random(20260908 + s)
        pay = list(canon); rng.shuffle(pay)
        best, nconf, _ = battery(pay, TARGETS)
        mx = max(v[0] for v in best.values())
        per_run_max.append(mx)
        pooled_scores_max = max(pooled_scores_max, mx)
        nconf1 = nconf
        print(f"  null {s}: max {mx:.3f} over {nconf} configs")
    m1 = sum(per_run_max) / len(per_run_max)
    m2 = pooled_scores_max
    N1, N2 = nconf1, nconf1 * NULL_RUNS
    beta = max((m2 - m1) / math.log(NULL_RUNS), 1e-4)
    mu = m1 - beta * (math.log(N1) + EULER_GAMMA)
    fam = len(VARIANTS) * nconf1
    bar = mu + beta * (math.log(fam) - math.log(-math.log(1 - ALPHA)))
    out = {"per_run_max": per_run_max, "pooled_max": m2, "configs_per_run": nconf1,
           "gumbel": {"mu": mu, "beta": beta, "fit": "two order statistics, "
                      f"E[max@{N1}]≈{m1:.4f} (mean of {NULL_RUNS}) and max@{N2}={m2:.4f}"},
           "family_size": fam, "alpha": ALPHA, "family_bar": bar,
           "historical_bar": HIST_BAR}
    json.dump(out, open(os.path.join(HERE, "null_calibration.json"), "w"), indent=1)
    print(f"NULL: E[max]per-run={m1:.3f} pooled max={m2:.3f} -> mu={mu:.3f} beta={beta:.4f}")
    print(f"FAMILY BAR (N={fam:,}, alpha={ALPHA}): {bar:.3f}   (historical {HIST_BAR})")
    return bar

# ------------------------------------------------------------------ 3. REAL SWEEP
def sweep(bar):
    pan = adj.panel()
    t0 = time.time()
    fout = open(os.path.join(HERE, "sweep_rows.jsonl"), "w")
    leaderboard, total = [], 0
    for k, (vid, pay) in enumerate(VARIANTS):
        best, nconf, _ = battery(pay, TARGETS)
        total += nconf
        for tname, (sc, mode, dec) in best.items():
            a = adj.adjudicate(dec, pan=pan)
            row = {"variant": vid, "target": tname, "score": round(sc, 4), "config": mode,
                   "ioc_n": round(float(a["ioc"]), 4), "min_distinct32": int(a["mds"]),
                   "panel_en": round(float(a["en"]), 4),
                   "best_ne_z": round(float(a["pmax_ne"]), 4), "ne_reg": pan.registers[a["ne_reg"]],
                   "zlib_ratio": round(len(zlib.compress(bytes(dec), 9)) / len(dec), 4),
                   "above_family_bar": bool(sc >= bar),
                   "near_bar": bool(bar > sc >= bar - 0.15)}
            fout.write(json.dumps(row) + "\n")
            leaderboard.append((sc, vid, tname, mode))
        if (k + 1) % 16 == 0:
            el = time.time() - t0
            print(f"  {k+1}/{len(VARIANTS)} variants, {total:,} configs, "
                  f"{el:.0f}s elapsed, ETA {el / (k + 1) * (len(VARIANTS) - k - 1):.0f}s")
    fout.close()
    leaderboard.sort(reverse=True, key=lambda r: r[0])
    hits = [r for r in leaderboard if r[0] >= bar]
    near = [r for r in leaderboard if bar > r[0] >= bar - 0.15]
    summary = {"variants": len(VARIANTS), "targets": len(TARGETS),
               "total_configs": total, "family_bar": bar,
               "hits_above_bar": [dict(zip(("score", "variant", "target", "config"), r))
                                  for r in hits],
               "near_bar_within_0.15": [dict(zip(("score", "variant", "target", "config"), r))
                                        for r in near],
               "top20": [dict(zip(("score", "variant", "target", "config"), r))
                         for r in leaderboard[:20]],
               "wall_seconds": round(time.time() - t0, 1)}
    json.dump(summary, open(os.path.join(HERE, "sweep_summary.json"), "w"), indent=1)
    print(f"\nSWEEP DONE: {total:,} configs across {len(VARIANTS)} variants; "
          f"{len(hits)} above family bar {bar:.3f}; {len(near)} near-bar.")
    for r in leaderboard[:10]:
        print(f"  {r[0]:7.3f}  {r[1]}  {r[2]:16s}  {r[3]}")
    return hits, near

if __name__ == "__main__":
    print(f"targets: {len(TARGETS)} ({len(unsolved)} unsolved pages + corpus); "
          f"variants: {len(VARIANTS)}")
    plant_control()
    bar = null_calibration()
    hits, near = sweep(bar)
    if hits:
        print("\n*** CANDIDATES ABOVE FAMILY BAR — FLAGGED-FOR-ORACLE, do not certify ***")
