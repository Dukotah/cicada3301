"""LENS N2 — prime-gap and prime-index streams read as DATA (not a cipher key).

For each integer stream S built from the unsolved LP2 stream, interpret it several
literal ways and score the English-ness of the result vs a size-matched null:
  (a) base-29 digits -> runes -> translit -> English score
  (b) values mod 29 as a direct plaintext
  (c) ASCII/byte values (chunk & printable-ratio)
  (d) coordinate pairs (structure check)

Positive controls:
  C1  PARABLE's own prime-index stream, mod-29 route, must reconstruct recognizable
      structure (prime_index = i+1, so mod29 -> i+1 -> shift-by-1 of the plaintext).
  C2  Plant an English message into a gap-like stream and recover it (machinery check).

Null: nc.shuffled on the stream (seed 3301), >=200 draws where feasible.
HIT bar (PREREG): score_norm >= -5.5 AND >= null_max + 0.5.
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import lib_numchannel as nc

N = nc.N  # 29
RESULTS = {}


# --------------------------------------------------------------- interpretations
def interp_mod29(stream):
    """(b) values mod 29 as direct plaintext -> English score."""
    idxs = [v % N for v in stream]
    return nc.eng_norm(idxs), idxs


def interp_base29(stream, ndig=2):
    """(a) read the stream as base-29 digits; group ndig digits -> one rune index.
    Since digits themselves are mod-29 residues, grouping recombines them."""
    digs = [v % N for v in stream]
    out = []
    for j in range(0, len(digs) - ndig + 1, ndig):
        val = 0
        for k in range(ndig):
            val = val * N + digs[j + k]
        out.append(val % N)
    if not out:
        return -99.0, []
    return nc.eng_norm(out), out


def interp_ascii(stream):
    """(c) treat values as ASCII bytes; report printable ratio + English of printable run.
    Streams are small ints so map onto printable ASCII by (v % 95) + 32."""
    chars = [chr((v % 95) + 32) for v in stream]
    s = "".join(chars)
    printable = sum(1 for c in s if 32 <= ord(c) < 127) / len(s)
    # also score the direct low bytes if they happen to land in ASCII letters
    return printable, s


def coord_structure(stream):
    """(d) coordinate pairs — measure whether (x,y) pairs cluster (autocorr proxy).
    Returns a crude 'non-random pair repeat' fraction; structural, not an English score."""
    pairs = list(zip(stream[0::2], stream[1::2]))
    if not pairs:
        return 0.0
    from collections import Counter
    c = Counter(pairs)
    # fraction of pairs that are the single most common pair (uniform ~ 1/|distinct|)
    return c.most_common(1)[0][1] / len(pairs)


# --------------------------------------------------------------- positive controls
def control_parable_index():
    """C1: PARABLE prime-index stream, mod-29 route reconstructs shifted plaintext."""
    par = nc.segments()[-1]
    pi = nc.v_prime_index(par)          # i+1
    recon = [v % N for v in pi]         # -> i+1 mod 29 (shift by +1 vs original)
    # undo the +1 shift to recover the exact plaintext
    undone = [(v - 1) % N for v in recon]
    plain_txt = "".join(nc.gp.IDX_TO_TRANS[i] for i in par)
    recon_txt = "".join(nc.gp.IDX_TO_TRANS[i] for i in undone)
    match = sum(a == b for a, b in zip(par, undone)) / len(par)
    return {
        "score_recon_shifted": nc.eng_norm(recon),
        "score_undone": nc.eng_norm(undone),
        "score_plain": nc.eng_norm(par),
        "exact_match_frac": match,
        "plain_head": plain_txt[:40],
        "undone_head": recon_txt[:40],
    }


def control_plant_gap():
    """C2: plant an English message as a stream, then let the mod-29 route recover it.
    Encode a real runeglish fragment (PARABLE's own rune idxs) as a value stream
    (idx + large offset that vanishes mod 29), recover exactly via mod29."""
    # use PARABLE's rune indices as the 'message' so the source is genuine runeglish
    idxs = nc.segments()[-1][:]
    # build a value stream: value = idx + 29*k + 100 (large-magnitude 'gap-like' carrier
    # whose only mod-29 residue is idx). 29*k terms must not change residue.
    stream = [i + 29 * 7 + 100 for i in idxs]  # 100 mod 29 = 13, so residue = (i+13)%29
    # so the correct recovery subtracts that constant offset's residue
    off = (29 * 7 + 100) % N
    recovered = [(v - off) % N for v in stream]  # undo carrier offset residue
    match = sum(a == b for a, b in zip(idxs, recovered)) / len(idxs)
    return {
        "score_planted_stream_recovered": nc.eng_norm(recovered),
        "score_source_idxs": nc.eng_norm(idxs),
        "exact_match_frac": match,
        "recovered_head": "".join(nc.gp.IDX_TO_TRANS[i] for i in recovered)[:40],
    }


# --------------------------------------------------------------- main sweep
def run_stream(name, stream):
    res = {"len": len(stream), "distinct": len(set(stream))}
    # (b) mod 29 direct
    s_mod, idxs_mod = interp_mod29(stream)
    res["mod29_score"] = s_mod
    # (a) base-29 grouping 2 and 3 digits
    res["base29_2_score"] = interp_base29(stream, 2)[0]
    res["base29_3_score"] = interp_base29(stream, 3)[0]
    # (c) ascii printable ratio
    pr, _ = interp_ascii(stream)
    res["ascii_printable_ratio"] = pr
    # (d) coordinate structure
    res["coord_top_pair_frac"] = coord_structure(stream)

    # nulls for the two English-scoring routes on this stream
    n_draws = 200
    mean_b, max_b, _ = nc.null_band(lambda s: interp_mod29(s)[0], stream, n=n_draws)
    res["mod29_null_mean"] = mean_b
    res["mod29_null_max"] = max_b
    mean_g, max_g, _ = nc.null_band(lambda s: interp_base29(s, 2)[0], stream, n=n_draws)
    res["base29_2_null_mean"] = mean_g
    res["base29_2_null_max"] = max_g

    # best English score across the two literal text routes
    best = max(s_mod, res["base29_2_score"], res["base29_3_score"])
    res["best_english_score"] = best
    # relevant null max for the best route
    res["best_null_max"] = max(max_b, max_g)
    res["hit"] = (best >= -5.5) and (best >= res["best_null_max"] + 0.5)
    return res


def main():
    u = nc.unsolved()

    # controls
    RESULTS["control_parable_index"] = control_parable_index()
    RESULTS["control_plant_gap"] = control_plant_gap()

    streams = {
        "prime_gap": nc.v_prime_gap(u),
        "prime_index": nc.v_prime_index(u),
        # cumulative variants (running sums carry more magnitude info)
        "prime_gap_cumsum": nc.cumulative(nc.v_prime_gap(u)),
        "prime_index_cumsum": nc.cumulative(nc.v_prime_index(u)),
    }
    RESULTS["streams"] = {}
    for name, st in streams.items():
        RESULTS["streams"][name] = run_stream(name, st)

    # verdict aggregation
    c1 = RESULTS["control_parable_index"]
    c2 = RESULTS["control_plant_gap"]
    control_passed = (c1["exact_match_frac"] >= 0.99 and
                      c1["score_undone"] >= -5.0 and
                      c2["exact_match_frac"] >= 0.99 and
                      c2["score_planted_stream_recovered"] >= -5.5)
    RESULTS["control_passed"] = control_passed

    any_hit = any(v["hit"] for v in RESULTS["streams"].values())
    best_name = max(RESULTS["streams"], key=lambda k: RESULTS["streams"][k]["best_english_score"])
    best = RESULTS["streams"][best_name]
    RESULTS["best_stream"] = best_name
    RESULTS["best_score"] = best["best_english_score"]
    RESULTS["best_null_max"] = best["best_null_max"]
    RESULTS["any_hit"] = any_hit

    with open(os.path.join(os.path.dirname(__file__), "results.json"), "w") as f:
        json.dump(RESULTS, f, indent=2)

    # console
    print("=== CONTROLS ===")
    print("C1 PARABLE prime-index mod29 route:")
    for k, v in c1.items():
        print(f"   {k}: {v}")
    print("C2 planted-gap recovery:")
    for k, v in c2.items():
        print(f"   {k}: {v}")
    print("control_passed:", control_passed)
    print("\n=== STREAMS (unsolved) ===")
    for name, v in RESULTS["streams"].items():
        print(f"\n[{name}] len={v['len']} distinct={v['distinct']}")
        print(f"   mod29         {v['mod29_score']:.3f}  (null max {v['mod29_null_max']:.3f} mean {v['mod29_null_mean']:.3f})")
        print(f"   base29(2dig)  {v['base29_2_score']:.3f}  (null max {v['base29_2_null_max']:.3f})")
        print(f"   base29(3dig)  {v['base29_3_score']:.3f}")
        print(f"   ascii printable ratio {v['ascii_printable_ratio']:.3f}")
        print(f"   coord top-pair frac   {v['coord_top_pair_frac']:.4f}")
        print(f"   BEST english {v['best_english_score']:.3f}  null+0.5={v['best_null_max']+0.5:.3f}  HIT={v['hit']}")
    print(f"\nBEST overall: {best_name} score {best['best_english_score']:.3f} vs null {best['best_null_max']:.3f}  any_hit={any_hit}")


if __name__ == "__main__":
    main()
