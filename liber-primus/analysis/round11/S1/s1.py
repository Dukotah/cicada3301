"""LENS S1 — the interrupter-POSITION channel.

The ~458 F-runes (rune index 0 = nc.INTERRUPTER_IDX) are treated as NOISE in every
letter-stream proof. This lens reads their POSITIONS instead. On the unsolved LP2
stream we:

  (a) gaps between consecutive index-0 occurrences -> base-29 / ASCII -> text
  (b) gaps mod small n -> directions / bits
  (c) the binary is-interrupter indicator (per position) -> bytes -> printable text

Honest caveat: not every F is a true interrupter. We test ALL F-runes as the
candidate channel (that is the only literal, transcription-free reading available).

Positive control: plant a KNOWN gap-encoded message into a synthetic interrupter
position set and show the machinery recovers it (score jumps from noise toward English).

Null: shuffle the interrupter POSITIONS while preserving their COUNT (seed 3301),
>=200 draws. This is the pre-registered, count-preserving surrogate for a position set.

HIT bar (PREREG): score_norm >= -5.5 AND >= null_max + 0.5.
Refute by default; anything in-band = NEGATIVE.
"""
import os, sys, json, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import lib_numchannel as nc

N = nc.N  # 29
RESULTS = {}


# ----------------------------------------------------------------- position ops
def interrupter_positions(stream):
    """Indices (0-based) where the F-rune (idx 0) occurs."""
    return [i for i, v in enumerate(stream) if v == nc.INTERRUPTER_IDX]


def gaps(positions):
    """Gap sequence between consecutive interrupter positions."""
    return [positions[k + 1] - positions[k] for k in range(len(positions) - 1)]


# --------------------------------------------------------------- interpretations
def interp_gap_mod29(gp_stream):
    """(a) gaps mod 29 -> rune indices -> translit -> English score."""
    idxs = [g % N for g in gp_stream]
    return nc.eng_norm(idxs), idxs


def interp_gap_ascii(gp_stream):
    """(a) gaps as raw ASCII codes; keep printable, score printable text.
    Returns (score, text, printable_ratio)."""
    chars = []
    printable = 0
    for g in gp_stream:
        c = g % 256
        if 32 <= c < 127:
            chars.append(chr(c))
            printable += 1
        else:
            chars.append(" ")
    text = "".join(chars)
    ratio = printable / max(1, len(gp_stream))
    return nc.eng_norm_text(text), text, ratio


def interp_gap_base29(gp_stream, ndig=2):
    """(a) gaps read as base-29 digits, grouped ndig at a time -> rune index."""
    digs = [g % N for g in gp_stream]
    out = []
    for j in range(0, len(digs) - ndig + 1, ndig):
        val = 0
        for k in range(ndig):
            val = val * N + digs[j + k]
        out.append(val % N)
    if not out:
        return -12.0, out
    return nc.eng_norm(out), out


def interp_gap_mod_n(gp_stream, n):
    """(b) gaps mod small n -> directions/symbols. Score by mapping into rune
    space (mod 29) so the shared scorer applies; also return the raw residues."""
    res = [g % n for g in gp_stream]
    # Map residues into rune indices for scoring (best-effort English readout).
    idxs = [r % N for r in res]
    return nc.eng_norm(idxs), res, idxs


def bits_from_gaps(gp_stream, mod=2):
    """(b) gaps mod 2 -> bitstream -> bytes -> printable text."""
    bits = [g % mod for g in gp_stream]
    return bits_to_text(bits)


def indicator_bits(stream):
    """(c) per-position is-interrupter indicator over the WHOLE stream."""
    return [1 if v == nc.INTERRUPTER_IDX else 0 for v in stream]


def bits_to_text(bits, msb_first=True):
    """Pack a bitstream into bytes, score printable text. Returns (score,text,ratio)."""
    chars = []
    printable = 0
    nbytes = len(bits) // 8
    for b in range(nbytes):
        byte = 0
        chunk = bits[b * 8:(b + 1) * 8]
        if msb_first:
            for bit in chunk:
                byte = (byte << 1) | (bit & 1)
        else:
            for k, bit in enumerate(chunk):
                byte |= (bit & 1) << k
        if 32 <= byte < 127:
            chars.append(chr(byte))
            printable += 1
        else:
            chars.append(" ")
    text = "".join(chars)
    ratio = printable / max(1, nbytes)
    return nc.eng_norm_text(text), text, ratio


# --------------------------------------------------------------- null (positions)
def null_positions(stream_len, count, score_fn, n=200, seed0=3301):
    """Draw n count-preserving random interrupter position sets; score each.
    Returns (mean, max, vals). score_fn takes a sorted positions list."""
    vals = []
    universe = list(range(stream_len))
    for k in range(n):
        r = random.Random(seed0 + k)
        pos = sorted(r.sample(universe, count))
        vals.append(score_fn(pos))
    return sum(vals) / len(vals), max(vals), vals


# =================================================================== MAIN
def main():
    stream = nc.unsolved()
    L = len(stream)
    pos = interrupter_positions(stream)
    gp_stream = gaps(pos)
    RESULTS["stream_len"] = L
    RESULTS["interrupter_count"] = len(pos)
    RESULTS["n_gaps"] = len(gp_stream)
    RESULTS["gap_min"] = min(gp_stream)
    RESULTS["gap_max"] = max(gp_stream)
    RESULTS["gap_mean"] = round(sum(gp_stream) / len(gp_stream), 3)

    # ---------------- POSITIVE CONTROL FIRST ----------------
    # Plant a known message by CONSTRUCTING an interrupter position set whose gaps
    # mod 29 spell a runeglish message, then run the SAME (a)-mod29 machinery on it.
    msg = "THEPRIMESARESACREDANDTHISISATRUESIGNAL"
    # translit chars -> rune indices via the gematria table's transliteration map.
    # Build reverse map from IDX_TO_TRANS (single-letter entries first-match).
    from lp import gematria as gp_mod
    trans_to_idx = {}
    for i in range(N):
        t = gp_mod.IDX_TO_TRANS[i]
        # prefer single-char keys; store first idx that yields this translit-char
        if len(t) == 1 and t not in trans_to_idx:
            trans_to_idx[t] = i
    planted_idx = []
    for ch in msg:
        if ch in trans_to_idx:
            planted_idx.append(trans_to_idx[ch])
    # Turn those target rune indices into gaps: gap = idx + 29*q (q>=1 so gaps
    # are realistic multi-rune spacings), then cumulative-sum into positions.
    planted_gaps = [gi + 29 * (2 + (k % 3)) for k, gi in enumerate(planted_idx)]
    ppos = [0]
    for g in planted_gaps:
        ppos.append(ppos[-1] + g)
    ctrl_score, ctrl_idx = interp_gap_mod29(gaps(ppos))
    ctrl_text = "".join(gp_mod.IDX_TO_TRANS[i] for i in ctrl_idx)
    # Null for the control: same #positions, random, over same span.
    span = ppos[-1] + 1
    cmean, cmax, _ = null_positions(
        span, len(ppos), lambda P: interp_gap_mod29(gaps(P))[0], n=200)
    control_passed = (ctrl_score >= -5.5) and (ctrl_score >= cmax + 0.5)
    RESULTS["control"] = {
        "planted_msg": msg,
        "recovered_text_head": ctrl_text[:60],
        "score": round(ctrl_score, 3),
        "null_mean": round(cmean, 3),
        "null_max": round(cmax, 3),
        "passed": control_passed,
    }

    # ---------------- REAL CHANNEL: score every route on the true stream ----------------
    routes = {}

    # (a) gaps mod29 -> runes
    s, _ = interp_gap_mod29(gp_stream)
    m, mx, _ = null_positions(L, len(pos),
                              lambda P: interp_gap_mod29(gaps(P))[0], n=200)
    routes["a_gap_mod29"] = {"score": round(s, 3), "null_mean": round(m, 3),
                             "null_max": round(mx, 3)}

    # (a) gaps as base-29 digits, groups of 2 and 3
    for nd in (2, 3):
        s, _ = interp_gap_base29(gp_stream, ndig=nd)
        m, mx, _ = null_positions(L, len(pos),
                                  lambda P, nd=nd: interp_gap_base29(gaps(P), ndig=nd)[0], n=200)
        routes[f"a_gap_base29_g{nd}"] = {"score": round(s, 3),
                                         "null_mean": round(m, 3), "null_max": round(mx, 3)}

    # (a) gaps as ASCII printable
    s, txt, ratio = interp_gap_ascii(gp_stream)
    m, mx, _ = null_positions(L, len(pos),
                              lambda P: interp_gap_ascii(gaps(P))[0], n=200)
    routes["a_gap_ascii"] = {"score": round(s, 3), "printable_ratio": round(ratio, 3),
                             "text_head": txt[:60], "null_mean": round(m, 3),
                             "null_max": round(mx, 3)}

    # (b) gaps mod small n -> directions/bits (n in 2,3,4,5,8)
    for n_ in (2, 3, 4, 5, 8):
        s, res, idxs = interp_gap_mod_n(gp_stream, n_)
        m, mx, _ = null_positions(L, len(pos),
                                  lambda P, n_=n_: interp_gap_mod_n(gaps(P), n_)[0], n=200)
        routes[f"b_gap_mod{n_}"] = {"score": round(s, 3), "null_mean": round(m, 3),
                                    "null_max": round(mx, 3)}

    # (b) gaps mod2 -> bitstream -> bytes -> printable
    s, txt, ratio = bits_from_gaps(gp_stream, mod=2)
    m, mx, _ = null_positions(L, len(pos),
                              lambda P: bits_from_gaps(gaps(P), mod=2)[0], n=200)
    routes["b_gap_bits_msb"] = {"score": round(s, 3), "printable_ratio": round(ratio, 3),
                                "text_head": txt[:60], "null_mean": round(m, 3),
                                "null_max": round(mx, 3)}

    # (c) indicator bitstream over whole stream -> bytes -> printable (msb & lsb)
    ind = indicator_bits(stream)

    def ind_score(P, msb):
        # rebuild an indicator array from a position set of the same count
        arr = [0] * L
        for p in P:
            arr[p] = 1
        return bits_to_text(arr, msb_first=msb)[0]

    for msb in (True, False):
        s, txt, ratio = bits_to_text(ind, msb_first=msb)
        m, mx, _ = null_positions(L, len(pos),
                                  lambda P, msb=msb: ind_score(P, msb), n=200)
        tag = "msb" if msb else "lsb"
        routes[f"c_indicator_{tag}"] = {"score": round(s, 3),
                                        "printable_ratio": round(ratio, 3),
                                        "text_head": txt[:60],
                                        "null_mean": round(m, 3), "null_max": round(mx, 3)}

    RESULTS["routes"] = routes

    # ---------------- VERDICT ----------------
    # Best real-channel score and the matching null_max for THAT route.
    best_route, best = None, None
    for name, r in routes.items():
        if best is None or r["score"] > best["score"]:
            best, best_route = r, name
    best_score = best["score"]
    best_null_max = best["null_max"]
    hit = (best_score >= -5.5) and (best_score >= best_null_max + 0.5)

    RESULTS["best_route"] = best_route
    RESULTS["best_score"] = best_score
    RESULTS["best_null_max"] = best_null_max
    RESULTS["hit"] = hit
    if not control_passed:
        RESULTS["verdict"] = "INCONCLUSIVE"
    elif hit:
        RESULTS["verdict"] = "HIT"
    else:
        RESULTS["verdict"] = "NEGATIVE"

    with open(os.path.join(os.path.dirname(__file__), "results.json"), "w") as f:
        json.dump(RESULTS, f, indent=2)

    # Console summary
    print("=== S1 interrupter-position channel ===")
    print(f"stream_len={L} interrupters={len(pos)} gaps={len(gp_stream)} "
          f"gap[min/mean/max]={min(gp_stream)}/{RESULTS['gap_mean']}/{max(gp_stream)}")
    print(f"CONTROL: planted='{msg[:30]}...' recovered='{ctrl_text[:30]}...' "
          f"score={ctrl_score:.3f} null_max={cmax:.3f} passed={control_passed}")
    print("ROUTES (real channel):")
    for name, r in routes.items():
        print(f"  {name:22s} score={r['score']:.3f}  null_max={r['null_max']:.3f}")
    print(f"BEST: {best_route} score={best_score:.3f} null_max={best_null_max:.3f}")
    print(f"VERDICT: {RESULTS['verdict']}")


if __name__ == "__main__":
    main()
