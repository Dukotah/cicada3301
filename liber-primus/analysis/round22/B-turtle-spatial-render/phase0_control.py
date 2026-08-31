"""Phase-0 positive control: plant KNOWN shapes as value streams, push them through
the IDENTICAL turtle+detector pipeline, and prove the detector separates them from
their shuffled nulls. If this fails, the LP2 null is uninterpretable (Q5 kill)."""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import turtle_engine as te


def planted_square(reps=800):
    """A closed unit square, walked 'reps' times. Value stream chosen so that
    (value % 4) cycles 0,1,2,3 -> headings 0,90,180,270 under absolute/M=4."""
    return [0, 1, 2, 3] * reps


def planted_blockword():
    """A square-wave 'comb': alternating up/right strokes forming a repeating
    rectangular pattern (a stand-in for block-letter text). Under absolute M=4."""
    # right, up, right, down repeated -> crenellation
    pat = [1, 0, 3, 0]  # up, right, down, right  (mod4 headings)
    return pat * 500


def run_control(name, values, modulus=4, turn="absolute", step="unit"):
    xs, ys = te.walk(values, modulus, turn, step)
    real = te.detect(xs, ys)
    null = te.null_band(values, modulus, turn, step, n=200)
    ps = {s: te.two_sided_p(real[s], null[s]) for s in te.STATS}
    fired = [s for s, p in ps.items() if p < 0.01]
    art = os.path.join(HERE, "artifacts", f"phase0_{name}.png")
    te.save_png(xs, ys, art)
    return {
        "name": name, "modulus": modulus, "turn": turn, "step": step,
        "real": real,
        "null_mean": {s: float(np.mean(null[s])) for s in te.STATS},
        "p": ps, "fired_stats": fired, "png": art,
        "detector_fires": len(fired) >= 2,
    }


if __name__ == "__main__":
    results = []
    results.append(run_control("square", planted_square()))
    results.append(run_control("blockcomb", planted_blockword()))
    ok = all(r["detector_fires"] for r in results)
    out = {"phase0_pass": ok, "controls": results}
    with open(os.path.join(HERE, "phase0_results.json"), "w") as f:
        json.dump(out, f, indent=2, default=float)
    for r in results:
        print(f"{r['name']:12} fired={r['fired_stats']} -> "
              f"detector_fires={r['detector_fires']}")
        for s in te.STATS:
            print(f"    {s:20} real={r['real'][s]:.5g}  null_mean={r['null_mean'][s]:.5g}  p={r['p'][s]:.4g}")
    print("\nPHASE0_PASS =", ok)
