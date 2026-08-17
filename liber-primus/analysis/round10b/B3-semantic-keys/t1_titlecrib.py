"""T1 -- TITLE CRIB at LP2 section / sentence starts, with the key READ OUT of the ciphertext.

Rationale (PREREG G-b/G-c): every solved keyed page opens with a short TITLE enciphered under
the same key from offset 0 (03.jpg 'WELCOME' -> key DIUINIT..., 14.jpg 'A KOAN' -> key FIRFU...).
GATE-2 proved the readout arithmetic reproduces both exactly.  On LP2 the titles are inline and
terminated by '.', exactly as the one readable LP2 page shows ('PARABLE.').  So: crib a title at
every plausible title position and ask whether the recovered keystream fragment READS AS A WORD.

This does not assume the key is in any word list -- it recovers whatever the keystream is.

NULLS:
  A) length-matched pseudo-titles cut from the repo's English generator, same positions
  B) the real titles against per-page SHUFFLED ciphertext
Both are run at identical scale so the comparison is apples to apples.

Run: PYTHONUTF8=1 python3 t1_titlecrib.py
"""
import json
import random
import sys

import b3lib
import screen
from b3lib import gp
from lp import solve
from run_stats import english_baseline

SC = b3lib.scorer()
N = gp.N
MINLEN, MAXLEN = 5, 20


# ------------------------------------------------------------------ positions
def crib_positions():
    """(seg, offset_in_seg, kind) for page starts, ornament-section starts, sentence starts."""
    raws = b3lib.lp2_segments_raw()
    pos = []
    for si, raw in enumerate(raws):
        n = 0
        started = False
        pos.append((si, 0, "pagestart"))
        pending = None
        for ch in raw:
            if ch in gp.RUNE_TO_IDX:
                if pending is not None:
                    pos.append((si, n, pending))
                    pending = None
                n += 1
            elif ch == ".":
                pending = "sentence"
            elif ch in "&$":
                pending = "ornament"
        started = started  # noqa
    return pos


# ------------------------------------------------------------------ readout
def readout(ct, start, crib, sign):
    """keystream fragment implied by plaintext `crib` sitting at ct[start:]."""
    if start + len(crib) > len(ct):
        return None
    return [(sign * (ct[start + j] - crib[j])) % N for j in range(len(crib))]


def title_keys():
    ks = []
    seen = set()
    for w in b3lib.TITLES:
        for t in b3lib.orbit(w):
            if MINLEN <= len(t) <= MAXLEN and t not in seen:
                seen.add(t)
                ks.append((w, t))
    return ks


def pseudo_titles(lengths, count, rng):
    eng = english_baseline()
    out = []
    for _ in range(count):
        L = rng.choice(lengths)
        s = rng.randrange(0, len(eng) - L - 1)
        out.append(("<null>", tuple(eng[s:s + L])))
    return out


def sweep(segs, positions, keys, tag):
    best = []
    for si, off, kind in positions:
        ct = segs[si]
        for lat, t in keys:
            for sign in (-1, +1):
                k = readout(ct, off, t, sign)
                if k is None:
                    continue
                txt = gp.indices_to_translit(k)
                s = SC.score_norm(txt)
                best.append((s, si, off, kind, lat, gp.indices_to_translit(t), sign, txt))
    best.sort(key=lambda r: -r[0])
    return best


def positive_control(keys):
    """Run the EXACT T1 procedure blind on the two solved keyed pages.
    The instrument must rank the true (position, title) readout near the top."""
    print("== T1 POSITIVE CONTROL (solved pages, run blind) ==")
    ok = True
    for label, want_key_prefix in (("03.jpg", "DIUINIT"), ("14.jpg", "FIRFU")):
        idxs, page = b3lib.solved_page(label)
        rows = sweep([idxs], [(0, 0, "pagestart")], keys, "pc")
        rank = next((i for i, r in enumerate(rows) if r[7].startswith(want_key_prefix)), None)
        top = rows[0]
        print(f"  {label}: best readout {top[0]:7.3f} title={top[4]} -> {top[7]}")
        if rank is None:
            print(f"        true key {want_key_prefix} NOT PRODUCED -> FAIL")
            ok = False
            continue
        r = rows[rank]
        pct = 100.0 * rank / len(rows)
        print(f"        true key {want_key_prefix}: rank {rank}/{len(rows)} "
              f"(top {pct:.2f}%), score {r[0]:.3f}, via title {r[4]!r} spelled {r[5]}")
        ok &= (pct <= 5.0)
    print(f"  POSITIVE CONTROL: {'PASS' if ok else 'WEAK'}\n")
    return ok


def main():
    rng = random.Random(3301)
    segs = b3lib.lp2_segments()
    unsolved = list(range(55))
    positions = [p for p in crib_positions() if p[0] in unsolved]
    keys = title_keys()
    lengths = sorted({len(t) for _, t in keys})
    print(f"crib positions: {len(positions)}  "
          f"(pagestart {sum(1 for p in positions if p[2]=='pagestart')}, "
          f"ornament {sum(1 for p in positions if p[2]=='ornament')}, "
          f"sentence {sum(1 for p in positions if p[2]=='sentence')})")
    print(f"title key variants: {len(keys)}   lengths {lengths}")
    print(f"readouts to score: {len(positions)*len(keys)*2}\n")

    pc_ok = positive_control(keys)

    real = sweep(segs, positions, keys, "real")
    print(f"\nREAL best readout score: {real[0][0]:.3f}")
    for r in real[:15]:
        print(f"  {r[0]:7.3f} seg{r[1]:<3d} off{r[2]:<4d} {r[3]:<9s} "
              f"title={r[4]:<20s} spelled={r[5]:<18s} sign{r[6]:+d}  KEYREADOUT={r[7]}")

    # ---------------------------------------------------------------- NULL A
    nkeys = pseudo_titles(lengths, len(keys), rng)
    nullA = sweep(segs, positions, nkeys, "nullA")
    # ---------------------------------------------------------------- NULL B
    shuf = []
    for i, s in enumerate(segs):
        c = list(s)
        rng.shuffle(c)
        shuf.append(c)
    nullB = sweep(shuf, positions, keys, "nullB")

    import statistics
    def stat(rows):
        v = [r[0] for r in rows]
        return max(v), statistics.mean(v), statistics.pstdev(v), sorted(v)[int(0.99 * len(v))]

    for nm, rows in (("REAL", real), ("NULL-A pseudo-titles", nullA),
                     ("NULL-B shuffled ct", nullB)):
        mx, mu, sd, p99 = stat(rows)
        print(f"\n{nm:<24s} n={len(rows):<8d} max={mx:.3f} mean={mu:.3f} "
              f"sd={sd:.3f} p99={p99:.3f}")

    mxA = max(r[0] for r in nullA)
    mxB = max(r[0] for r in nullB)
    nullmax = max(mxA, mxB)
    margin = real[0][0] - nullmax
    print(f"\nreal_best - null_max = {real[0][0]:.3f} - {nullmax:.3f} = {margin:+.3f}"
          f"   (PREREG PASS needs >= +1.000)")

    # ------------------------------------------- promote: readout as repeating key
    print("\n== promotion: top-25 readouts used as a repeating key on their own page ==")
    raws = b3lib.lp2_segments_raw()
    promoted = []
    for r in real[:25]:
        s0, si, off, kind, lat, spelled, sign, ro = r
        # rebuild readout indices exactly
        pass
        # rebuild readout indices exactly
        t = next(tt for ll, tt in keys if ll == lat and gp.indices_to_translit(tt) == spelled)
        kk = readout(segs[si], off, t, sign)
        sc, _, _ = screen.phase_flexible_score(segs[si], kk, -1, False, SC)
        sc2, _, _ = screen.phase_flexible_score(segs[si], kk, +1, False, SC)
        promoted.append((max(sc, sc2), si, lat, ro))
    promoted.sort(key=lambda x: -x[0])
    for p in promoted[:10]:
        print(f"  page-decode {p[0]:7.3f}  seg{p[1]:<3d} title={p[2]:<20s} key={p[3]}")
    print(f"\nbest page decode from any title readout: {promoted[0][0]:.3f} "
          f"(PREREG PASS needs > -5.200)")

    json.dump({
        "n_positions": len(positions), "n_title_variants": len(keys),
        "real_top": [list(r) for r in real[:50]],
        "real_best": real[0][0], "nullA_max": mxA, "nullB_max": mxB,
        "margin_vs_nullmax": margin,
        "promoted_best_page_decode": promoted[0][0],
        "promoted_top": [list(p) for p in promoted[:15]],
    }, open("T1-RESULTS.json", "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
