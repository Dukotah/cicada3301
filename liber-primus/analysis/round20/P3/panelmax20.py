"""panelmax20 -- the ONE bar every Round-20 Phase-S lane calls.

This is the P3a deliverable as a callable: a thin, self-documenting wrapper over I3's
directly-fitted panel-max null (calib19.json `I19:...+I2|pmax|L120`). It exists so that no
S-lane has to re-derive a multiplicity correction, and so that the doctrine's forbidden moves
(quoting -5.5, quoting a scalar k_eff, adjudicating `en` on a permissive decode) are impossible
to make by accident: this function ONLY returns the panel-max bar, and it refuses an unknown
preset rather than silently substituting the English one.

    from panelmax20 import panelmax_bar, panelmax_contract
    bar = panelmax_bar(preset="drift", n_round_adjudicated=N_ADJ, alpha=0.01)
    con = panelmax_contract(preset="drift", n_round_adjudicated=N_ADJ)   # both tiers + cell

Store `panelmax_contract(...)` in the SWEEPROW header. A number without its cell is not a bar.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
I3 = os.path.abspath(os.path.join(HERE, "..", "..", "round19", "I3"))
if I3 not in sys.path:
    sys.path.insert(0, I3)

import nullcurve19 as NC  # noqa: E402

# preset -> the calib19 panel-max cell fitted DIRECTLY on wrong-key beam decodes.
PRESET_CELLS = {
    "exact":     "I19:vecbeam.keyskip1+I2|pmax|L120",
    "pair":      "I19:driftbeam.pair+I2|pmax|L120",
    "exact_ms8": "I19:driftbeam.exact_ms8+I2|pmax|L120",
    "drift":     "I19:driftbeam.drift+I2|pmax|L120",
}
# L=31 variant (short-window screens) -- keyskip1 only, per I3 S10.0
PRESET_CELLS_L31 = {"exact": "I19:vecbeam.keyskip1+I2|pmax|L31"}

ALPHA_CLAIM = NC.ALPHA_ROUND19    # 0.01
ALPHA_ESC = NC.ALPHA_ESCALATE     # 0.05


def _cell(preset, L=120):
    key = (PRESET_CELLS_L31 if L == 31 else PRESET_CELLS).get(preset)
    if key is None:
        raise KeyError(
            f"no panel-max cell for preset={preset!r} at L={L}. "
            f"Known presets: {sorted((PRESET_CELLS_L31 if L==31 else PRESET_CELLS))}. "
            f"Refusing to substitute another preset's bar (that substitution is the L7-C.3 error).")
    c = NC.calib()["cells"].get(key)
    if c is None:
        raise KeyError(f"cell {key} not in calib19.json")
    return key, c


def panelmax_bar(preset="exact", n_round_adjudicated=10 ** 6, alpha=ALPHA_CLAIM, L=120):
    """The panel-max (`pmax`) family-wise bar at `n_round_adjudicated`, level `alpha`.

    ALWAYS the panel-max statistic. There is no `en` path and no -5.5 floor here by design."""
    _, c = _cell(preset, L)
    return NC._fw(n_round_adjudicated, c["mu"], c["beta"], alpha)


def panelmax_contract(preset="exact", n_round_adjudicated=10 ** 6, L=120):
    """Both tiers + every conditional, as a dict to store in the SWEEPROW header."""
    key, c = _cell(preset, L)
    return {
        "statistic": "pmax",
        "preset": preset, "segment_len": L,
        "n_round_adjudicated": n_round_adjudicated,
        "claim_alpha": ALPHA_CLAIM,
        "claim_bar": NC._fw(n_round_adjudicated, c["mu"], c["beta"], ALPHA_CLAIM),
        "escalate_alpha": ALPHA_ESC,
        "escalate_bar": NC._fw(n_round_adjudicated, c["mu"], c["beta"], ALPHA_ESC),
        "cell": key, "mu": c["mu"], "beta": c["beta"],
        "cell_M": c["M"], "cell_status": c.get("status", "UNMEASURED"),
        "extrapolated": bool(n_round_adjudicated > c["M"] / 50),
        "conditionals": {
            "null_generator": "uniform ciphertext x uniform keystream, wrong-key beam decode",
            "decoder_relation": preset,
            "adjudicator_register": "I2 9-register panel max (pmax); EN_NOVOWEL=detection-only"},
    }


if __name__ == "__main__":
    print("panel-max bars, claim (a=0.01), per preset @ N_round:")
    print(f"{'preset':10s} {'cell_M':>10s} {'status':>12s}  {'1e4':>8s} {'1e6':>8s} {'1e8':>8s}")
    for p in PRESET_CELLS:
        try:
            k, c = _cell(p)
            row = "  ".join(f"{panelmax_bar(p, n):.3f}" for n in (10**4, 10**6, 10**8))
            print(f"{p:10s} {c['M']:>10,} {c.get('status',''):>12s}  {row}")
        except KeyError as e:
            print(f"{p:10s} ERR {e}")
