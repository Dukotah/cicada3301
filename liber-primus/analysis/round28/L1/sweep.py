#!/usr/bin/env python3
"""R28-L1 SWEEP -- dense-offset + pair-relation sweep of the authoritative author pads.

Grid (PREREG Q3 + Addendum 2026-09-08):
  pads     : DATA__560.00.iso-authoritative (3,992,970 B, stride 16,384 -> 244 offsets)
             DATA_560.13                    (118,818,811 B, stride 331,777 -> 359 offsets)
  per offset: 5 reductions x {fwd, rev} x sign {-1,+1} x relation {exact(keyskip1), pair(keyskip2)}
  anti-repeat: at offset 0 the exact/keyskip1 cells are SKIPPED (R12-A1 covered all of them);
             pair at o=0 runs (new axis, not a repeat).
  screen   : L=400 head, beam_w=120, I2 adjudicate pmax; candidate bar 5.0.
  claim    : panelmax_bar('pair',1e6,.01)=7.384 / ('exact',1e6,.01)=7.634 (conservative for N~2.4e4).
  stage B  : any pmax>=5.0 -> hitfn20 (L=240) + full-stream re-decode -> FLAGGED-FOR-ORACLE.
  R3 stats : every row persists the full SWEEPROW (en, pmax, preg, pmax_ne, pcon, ioc, mds, h2, zl).
  null     : lane-local shuffled-ciphertext null, n=200 per relation, seed 3301.

Single-threaded; run under nice -n 15. Appends rows to sweep_rows.jsonl (resumable by row
count), writes results.json at the end.
"""
import hashlib
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis/round11", "analysis/campaign18_skip",
          "analysis/round19/I1", "analysis/round19/I2",
          "analysis/round20/P3", "analysis/round20/HITFN"):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

from lp import gematria as gp        # noqa: E402
import lib_numchannel as nc          # noqa: E402
import driftbeam as DB               # noqa: E402
import adjudicate as AD              # noqa: E402
import hitfn20 as H                  # noqa: E402
import panelmax20 as PM              # noqa: E402

N = gp.N
PADDIR = os.path.join(LP, "analysis", "round12", "A1", "pads")
PADS = [
    # label, filename, sha256, length, stride
    ("560.00auth", "DATA__560.00.iso-authoritative",
     "a24051a87f0eb25ca21accbd3158fdf7b4911243e5ee1b9778b81182f0d36573",
     3992970, 16384),
    ("560.13", "DATA_560.13",
     "db79072ce580efa54acf5f31f3ef0eb00aef867871a051d04e27ee5e7fbc112f",
     118818811, 331777),
]

HEAD = 400
BEAM_W = 120
NEED = HEAD * 6 + 64            # keystream bytes needed per screen decode
SCREEN_BAR = 5.0                # candidate/promotion bar (round27 cand_bar)
CLAIM = {"pair": PM.panelmax_bar("pair", 10 ** 6, 0.01),
         "exact": PM.panelmax_bar("exact", 10 ** 6, 0.01)}
RELATIONS = ("exact", "pair")
NULL_N = 200

_P2I = {p: i for i, p in enumerate(gp.PRIMES)}
REDUCERS = {
    "mod29":        lambda x: x % N,
    "prime_to_idx": lambda x: _P2I.get(x, x % N),
    "hi_nibble":    lambda x: (x >> 4) % N,
    "lo_nibble":    lambda x: (x & 0xF) % N,
    "byte_scaled":  lambda x: (x * N) // 256,
}

ROWS_PATH = os.path.join(HERE, "sweep_rows.jsonl")
LOG_PATH = os.path.join(HERE, "sweep.log")


def log(m):
    print(m, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(m + "\n")


def sha_check(path, want_sha, want_len):
    h, n = hashlib.sha256(), 0
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
            n += len(ch)
    return h.hexdigest() == want_sha and n == want_len


def decode_and_adjudicate(C, K, sign, preset):
    d = DB.beam_decode(C, K, sign=sign, o=0, beam_w=BEAM_W, **DB.PRESETS[preset])
    a = AD.adjudicate(d["plain_idx"])
    return d, a


def run_null(C, pad_bytes):
    """Lane-local shuffled-ciphertext null: n=200 per relation, seed 3301, real
    mod29 keystream from the authoritative _560.00 at rolling offsets (A1's pattern)."""
    out = {}
    for preset in RELATIONS:
        vals = []
        for k in range(NULL_N):
            r = random.Random(3301 + k)
            s = list(C)
            r.shuffle(s)
            o = (k * 37) % 10000
            K = [x % N for x in pad_bytes[o:o + NEED]]
            _, a = decode_and_adjudicate(s, K, -1, preset)
            vals.append(float(a["pmax"]))
        out[preset] = {"n": NULL_N, "mean": sum(vals) / len(vals), "max": max(vals)}
        log(f"null[{preset}]: mean pmax {out[preset]['mean']:.3f}  "
            f"max {out[preset]['max']:.3f}  (cand bar {SCREEN_BAR}, "
            f"claim bar {CLAIM[preset]:.3f})")
    return out


def stage_b(label, pad_bytes, rev, red_name, sign, o, preset, UNS):
    """Survivor escalation: hitfn20 on L=240 + full-stream re-decode."""
    src = pad_bytes[::-1] if rev else pad_bytes
    fn = REDUCERS[red_name]
    K240 = [fn(x) for x in src[o:o + 240 * 6 + 64]]
    dec = H.HitDecode(C=list(UNS[:240]), K=K240, o=0, sign=sign, preset=preset,
                      n_round_adjudicated=10 ** 6)
    v = H.evaluate(dec)
    full = {}
    kfull = [fn(x) for x in src[o:o + len(UNS) * 6 + 64]]
    if len(kfull) >= len(UNS) + 64:
        d = DB.beam_decode(list(UNS), kfull, sign=sign, o=0, beam_w=BEAM_W,
                           **DB.PRESETS[preset])
        a = AD.adjudicate(d["plain_idx"])
        full = {"full_score": round(d["score"], 3), "full_pmax": round(float(a["pmax"]), 3),
                "full_head": d["translit"][:120]}
    return dict(hit=bool(v.hit), reason=v.reason, pmax=round(v.pmax, 3),
                bar=round(v.bar, 3), recovery=round(v.recovery, 4),
                heldout=round(v.heldout_recovery, 4), preg=v.preg_name,
                score=round(v.score, 3), **full)


def main():
    t0 = time.time()
    UNS = list(nc.unsolved())
    C = UNS[:HEAD]
    log("=" * 74)
    log("R28-L1 sweep -- dense offsets x {exact,pair} on the authoritative pads")
    log("=" * 74)

    pads = {}
    for label, fname, sha, ln, stride in PADS:
        path = os.path.join(PADDIR, fname)
        if not sha_check(path, sha, ln):
            log(f"FATAL: {fname} drifted from receipt; refusing to run.")
            sys.exit(2)
        b = open(path, "rb").read()
        pads[label] = (b, b[::-1], stride)
        log(f"pad {label}: {ln:,} B sha-OK  stride {stride:,}  "
            f"offsets {((ln - NEED - 1) // stride) + 1}")

    done = 0
    if os.path.exists(ROWS_PATH):
        with open(ROWS_PATH) as f:
            done = sum(1 for _ in f)
        log(f"resume: {done} rows already present")

    null = run_null(C, pads["560.00auth"][0]) if done == 0 else None

    rows_f = open(ROWS_PATH, "a", encoding="utf-8")
    n_rows = done
    best = {"pmax": -1e9}
    survivors = []
    idx = 0
    s2_note = []

    def s2_cpu():
        try:
            pid = open(os.path.join(LP, "analysis", "round27", "sweep.pid")).read().split()[0]
            return os.popen(f"ps -o pcpu= -p {pid}").read().strip()
        except Exception:
            return "?"

    s2_note.append(("start", s2_cpu()))

    total_planned = sum((((ln - NEED - 1) // st) + 1) for _, _, _, ln, st in PADS) * 40 - 40
    checkpoint = max(1, total_planned // 10)

    for label, fname, sha, ln, stride in PADS:
        b_fwd, b_rev, _ = pads[label]
        n_off = ((ln - NEED - 1) // stride) + 1
        for oi in range(n_off):
            o = oi * stride
            for rev in (False, True):
                src = b_rev if rev else b_fwd
                chunk = src[o:o + NEED]
                for red_name, fn in REDUCERS.items():
                    K = [fn(x) for x in chunk]
                    for sign in (-1, +1):
                        for preset in RELATIONS:
                            if o == 0 and preset == "exact":
                                continue      # R12-A1 covered keyskip1 at o=0 exactly
                            idx += 1
                            if idx <= done:
                                continue      # resume skip
                            d, a = decode_and_adjudicate(C, K, sign, preset)
                            kid = (f"{label}:{red_name}{'_rev' if rev else ''}:"
                                   f"s{sign:+d}:o{o}:{preset}")
                            # SWEEPROW/1 fixed-order array (doctrine R3) + beam score
                            row = {"sweeprow": AD.to_row(a, kid),
                                   "beam_score": round(d["score"], 3)}
                            rows_f.write(json.dumps(row) + "\n")
                            n_rows += 1
                            pm = float(a["pmax"])
                            if pm > best["pmax"]:
                                best = {"kid": kid, "pmax": pm,
                                        "beam_score": round(d["score"], 3),
                                        "preg": int(a["preg"]),
                                        "head": d["translit"][:60]}
                                log(f"  new best {pm:.3f}  {kid}  {best['head'][:48]}")
                            if pm >= SCREEN_BAR:
                                log(f"  CANDIDATE pmax={pm:.3f} {kid} -> stage B")
                                sb = stage_b(label, b_fwd, rev, red_name, sign, o,
                                             preset, UNS)
                                survivors.append({"kid": kid, "screen_pmax": pm, **sb})
                                log(f"    stage B: {json.dumps(sb)[:200]}")
                            if n_rows % checkpoint == 0:
                                el = time.time() - t0
                                rate = el / max(1, n_rows - done)
                                log(f"[ckpt] {n_rows}/{total_planned} rows  "
                                    f"{rate:.3f}s/decode  elapsed {el/60:.1f}m  "
                                    f"S2 pcpu={s2_cpu()}")
                                rows_f.flush()
            if oi % 25 == 0:
                rows_f.flush()
        log(f"pad {label} complete: {n_rows} cumulative rows "
            f"({time.time() - t0:.0f}s)")

    rows_f.close()
    s2_note.append(("end", s2_cpu()))

    if null is None:
        null = run_null(C, pads["560.00auth"][0])

    hits = [s for s in survivors if s.get("hit")]
    out = {
        "lane": "round28/L1/sweep",
        "grid": {"pads": [{"label": l, "bytes": ln, "stride": st,
                           "offsets": ((ln - NEED - 1) // st) + 1}
                          for l, _, _, ln, st in PADS],
                 "reductions": list(REDUCERS), "dirs": ["fwd", "rev"],
                 "signs": [-1, 1], "relations": list(RELATIONS),
                 "head": HEAD, "beam_w": BEAM_W,
                 "anti_repeat": "keyskip1 cells at o=0 skipped (R12-A1 coverage)"},
        "rows_persisted": n_rows,
        "rows_planned": total_planned,
        "screen_bar": SCREEN_BAR,
        "claim_bars_1e6": {k: round(v, 4) for k, v in CLAIM.items()},
        "claim_bars_at_true_N": {k: round(PM.panelmax_bar(k, max(1, n_rows), 0.01), 4)
                                 for k in RELATIONS},
        "null": null,
        "best": best,
        "candidates": survivors,
        "hits": hits,
        "s2_pcpu_samples": s2_note,
        "elapsed_s": round(time.time() - t0, 1),
        "verdict": ("FLAGGED-FOR-ORACLE" if hits else
                    ("CANDIDATES-BELOW-GATE" if survivors else "NEGATIVE")),
    }
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    log(f"\nVERDICT: {out['verdict']}  rows={n_rows}  best pmax={best['pmax']:.3f} "
        f"({best.get('kid')})  elapsed {out['elapsed_s']/60:.1f}m")


if __name__ == "__main__":
    main()
