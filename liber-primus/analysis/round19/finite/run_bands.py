"""LANE 4 (finite) — RUN phase.

Reads the ONE finite object named in PREREG.md to completion: the 74 already-extracted RUNIC
ornament-band rune-index strings (round18/L3-ornaments/bands.json), re-scored over the I2
nine-register adjudicator panel, closing the ledger's own reopen condition for A-06
("Any band content in a non-English register (H1 only)").

Two measured products:
  1. RECOGNIZER-PLANT GATE (the kill gate, PREREG Q5): plant held-out in-register text at the
     band lengths actually present, corrupted at the band-reader's measured 4.4% per-glyph error
     (95.6% recall, C3/A-06), and measure panel recovery vs the length's matched-FP bar. If the
     panel cannot recognize its own planted hit at a given length, that length/register cell is
     declared UNDERPOWERED and its real-band silence carries no information.
  2. The per-band pmax / winning-register table over all 74 RUNIC bands, with a full R3 SWEEPROW
     per band (CI-enforced by I2 validate_row / handoff validate_ledger.py).

No decryption key is applied (ornaments-as-plaintext-in-themselves). Scored on RUNE INDICES.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
I2 = os.path.abspath(os.path.join(HERE, "..", "I2"))
L3 = os.path.abspath(os.path.join(HERE, "..", "..", "round18", "L3-ornaments"))
sys.path.insert(0, I2)

import adjudicate as A  # noqa: E402

N = 29
pan = A.panel()
REG = pan.registers
NE_SET = {"LATIN", "OE", "DE", "CY", "EN_HALFVOWEL", "EN_NOVOWEL"}  # the non-English panel
EN_SET = {"EN_MODERN", "EN_KJV", "LP1_REAL"}

# ------------------------------------------------------------------ matched-FP bar per length
# From round19/I2 out_gates.json G-POWER: t_pmax at alpha_ref=0.001, anchored at the grid
# lengths it was measured on. For a band of length n we use the bar at the nearest measured
# length at or below n (conservative: a shorter calibration gives a HIGHER false-positive rate,
# so we recompute the bar at the band's own length from the stored null below instead).
def bar_pmax(n, alpha=0.001):
    """alpha-level max-over-9-registers bar at length n, from the panel's own uniform-rune null.

    This is the honest per-length bar: draw uniform random rune strings of length n, panel-score
    each, take the max over the 9 registers, and report the (1-alpha) quantile. A real band
    clears this only if it is less rune-random than 999/1000 random strings in SOME register.
    """
    rng = np.random.default_rng(3301 + n)
    draws = 2000
    if n < 3:
        return 99.0
    X = rng.integers(0, N, size=(draws, n))
    res = A.adjudicate_batch(X, pan=pan)
    return float(np.quantile(res["pmax"], 1.0 - alpha))


_BAR_CACHE = {}
def bar_for(n):
    if n not in _BAR_CACHE:
        _BAR_CACHE[n] = bar_pmax(n)
    return _BAR_CACHE[n]


# ------------------------------------------------------------------ band-reader noise model
# C3/A-06: per-glyph recall 0.956 on the LP2 typeface. Model end-to-end band-read corruption as:
# with prob p_err the read glyph is wrong (uniform substitution over the other 28). This is the
# charitable model (pure substitution); it does NOT add deletions, so it OVER-states recovery
# slightly, which only makes a kill verdict stronger.
P_ERR = 1.0 - 0.956

def corrupt(x, rng, p=P_ERR):
    x = np.array(x, dtype=np.int64)
    mask = rng.random(len(x)) < p
    if mask.any():
        wrong = rng.integers(1, N, size=mask.sum())  # 1..28 offset -> never identity
        x[mask] = (x[mask] + wrong) % N
    return x


def plant_recovery(reg, L, trials=200, seed=0):
    """Draw `trials` held-out in-register windows of length L, corrupt at the reader's error
    rate, panel-score, and return recovery = fraction clearing the length-L bar with `reg` as
    the panel argmax register. Recovery on CLEAN windows is also returned for reference."""
    d = np.load(os.path.join(I2, "models", "testhalves.npz"), allow_pickle=True)
    corpus = np.asarray(d[reg], dtype=np.int64)
    rng = np.random.default_rng(1000 + seed + hash(reg) % 10000)
    if len(corpus) < L + 1:
        return None
    starts = rng.integers(0, len(corpus) - L, size=trials)
    bar = bar_for(L)
    ri = REG.index(reg)
    hit_noisy = hit_clean = 0
    for s in starts:
        w = corpus[s:s + L]
        rc = A.adjudicate(w, pan=pan)
        if rc["pmax"] >= bar and rc["preg"] == ri:
            hit_clean += 1
        wn = corrupt(w, rng)
        rn = A.adjudicate(wn, pan=pan)
        if rn["pmax"] >= bar and rn["preg"] == ri:
            hit_noisy += 1
    return {"register": reg, "L": int(L), "bar": round(bar, 3),
            "recovery_clean": hit_clean / trials,
            "recovery_noisy": hit_noisy / trials, "trials": trials}


# ------------------------------------------------------------------ run
def main():
    bands = json.load(open(os.path.join(L3, "bands.json")))
    runic = [r for r in bands if r.get("call") == "RUNIC"]

    out = {"lane": "round19/finite", "object": "round18/L3-ornaments/bands.json RUNIC bands",
           "n_runic_bands": len(runic), "p_err_model": P_ERR,
           "registers": REG, "alpha": 0.001}

    # --- 1. RECOGNIZER-PLANT GATE -------------------------------------------------------------
    plant_lengths = [8, 16, 32, 48, 89, 128]
    gate = []
    for reg in REG:
        for L in plant_lengths:
            pr = plant_recovery(reg, L)
            if pr:
                gate.append(pr)
    out["recognizer_plant"] = gate

    # Usable-length floor per register: smallest L whose NOISY recovery >= 0.80
    floor = {}
    for reg in REG:
        cells = sorted([g for g in gate if g["register"] == reg], key=lambda c: c["L"])
        f = None
        for c in cells:
            if c["recovery_noisy"] >= 0.80:
                f = c["L"]
                break
        floor[reg] = f
    out["usable_length_floor_noisy80"] = floor

    # --- 2. SCORE THE 74 REAL BANDS -----------------------------------------------------------
    hdr = A.header("round19-finite-ornament-bands")
    rows = []
    band_tbl = []
    for r in runic:
        runes = [v for v in r["runes"] if v >= 0]   # strip unreadable -1
        x = np.asarray(runes, dtype=np.int64)
        res = A.adjudicate(x, pan=pan)
        kid = r["id"]
        row = A.to_row(res, kid)
        A.validate_row(row, hdr)       # CI gate, per PREREG deliverable 2
        rows.append(row)
        preg_name = REG[res["preg"]]
        ne_name = REG[res["ne_reg"]]
        band_tbl.append({
            "id": kid, "page": r.get("page"),
            "n_full": len(r["runes"]), "n_readable": len(runes),
            "pmax": round(float(res["pmax"]), 3), "preg": preg_name,
            "bar": round(bar_for(len(runes)), 3) if len(runes) >= 3 else None,
            "clears_bar": bool(len(runes) >= 3 and res["pmax"] >= bar_for(len(runes))),
            "preg_is_nat_lang": bool(preg_name in (EN_SET | NE_SET)),
            "pmax_ne": round(float(res["pmax_ne"]), 3), "ne_reg": ne_name,
            "pcon": round(float(res["pcon"]), 3), "pcreg": REG[res["pcreg"]],
            "ioc": round(float(res["ioc"]), 4), "mds": int(res["mds"]),
            "h2": round(float(res["h2"]), 4), "zl": round(float(res["zl"]), 4),
        })
    out["band_table"] = band_tbl

    # --- 3. HITS: bands clearing their own-length bar in a NATURAL-LANGUAGE register ----------
    hits = [b for b in band_tbl if b["clears_bar"] and b["preg_is_nat_lang"]]
    # and specifically in a NON-ENGLISH register (the gap the reopen names)
    ne_hits = [b for b in band_tbl if b["clears_bar"] and b["preg"] in NE_SET]
    out["hits_natural_language"] = hits
    out["hits_non_english"] = ne_hits
    out["n_hits_nat_lang"] = len(hits)
    out["n_hits_non_english"] = len(ne_hits)

    json.dump(out, open(os.path.join(HERE, "out_bands.json"), "w"), indent=1)

    # SWEEPROW store: header line + one row per band (CI-validatable)
    with open(os.path.join(HERE, "sweeprows.jsonl"), "w") as f:
        f.write(json.dumps(hdr) + "\n")
        for row in rows:
            f.write(json.dumps(row) + "\n")

    # Console summary
    print("=== RECOGNIZER-PLANT GATE (noisy recovery, 4.4% per-glyph error) ===")
    print(f"{'reg':13s} " + " ".join(f"L{L:>3}" for L in plant_lengths))
    for reg in REG:
        cells = {g["L"]: g for g in gate if g["register"] == reg}
        print(f"{reg:13s} " + " ".join(
            (f"{cells[L]['recovery_noisy']:.2f}" if L in cells else "  - ")
            for L in plant_lengths))
    print("\nusable length floor (noisy recovery>=0.80):", floor)
    print(f"\n=== REAL BANDS: {len(runic)} RUNIC bands scored ===")
    print(f"bands clearing own-length bar in ANY natural-language register: {len(hits)}")
    print(f"bands clearing own-length bar in a NON-ENGLISH register:        {len(ne_hits)}")
    if hits:
        for b in sorted(hits, key=lambda z: -z["pmax"])[:10]:
            print(f"  {b['id']} n={b['n_readable']:4d} pmax={b['pmax']:6.2f} "
                  f"bar={b['bar']:5.2f} reg={b['preg']}")
    # top pmax regardless of bar, for context
    print("\ntop-8 bands by pmax (context):")
    for b in sorted(band_tbl, key=lambda z: -z["pmax"])[:8]:
        print(f"  {b['id']} n={b['n_readable']:4d} pmax={b['pmax']:6.2f} "
              f"bar={b['bar']} reg={b['preg']} ne={b['pmax_ne']:5.2f}/{b['ne_reg']}")
    print("\nwrote out_bands.json + sweeprows.jsonl")


if __name__ == "__main__":
    main()
