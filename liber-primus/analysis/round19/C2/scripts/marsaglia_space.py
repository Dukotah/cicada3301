"""C2 — exactly how big is the Marsaglia offset space, and exactly what does it cost?

Round 17 called the CDROM "the cheapest live item in this branch" without ever costing it.
This turns that into a number, so Round 19 Phase 2 can schedule it instead of debating it.

Counts the offsets analytically from the hash-verified manifest and L6's own builder table
(no scanning), and measures realised throughput from the checkpoints `sweep_marsaglia.py`
has actually written (file mtimes + each unit's own `n_offsets`).

    python3 marsaglia_space.py   ->  ../out_marsaglia_space.json
"""
import os, sys, json, glob, time

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, ".."))
ANALYSIS = os.path.abspath(os.path.join(C2, "..", ".."))
L6 = os.path.join(ANALYSIS, "round18", "L6-offset-marsaglia")

# L6 lib_l6.BUILDERS: name -> symbols per byte.  `hexchars` is EXCLUDED by L6 §2.1
# (it drops the digits 0-9 and sweeps the A-F subsequence); `nibbles` replaces it.
SPB = {"mod29": 1, "hi_nibble": 1, "lo_nibble": 1, "byte_scaled": 1,
       "prime_to_idx": 1, "nibbles": 2}
PLEN = 24          # dense_scan prefilter window; offsets = symbols - PLEN
SIGNS = 2
ORDERS = 2         # forward + reversed byte order
ISO_BYTES = 634_124_288


def main():
    v = json.load(open(os.path.join(C2, "out_verify.json")))
    assert v["all_gates_pass"]
    pads = v["random_data_pads"]
    pad_bytes = 10_000_000

    per_pad = sum(pad_bytes * spb - PLEN for spb in SPB.values()) * ORDERS * SIGNS
    pads_total = per_pad * len(pads)
    iso_total = sum(ISO_BYTES * spb - PLEN for spb in SPB.values()) * ORDERS * SIGNS

    # --- realised throughput, from the checkpoints on disk ------------------------
    ck = sorted(glob.glob(os.path.join(L6, "out", "ckpt_M", "*.json")),
                key=os.path.getmtime)
    done_off = sum(int(json.load(open(p)).get("n_offsets", 0)) for p in ck)
    if len(ck) >= 3:
        span = os.path.getmtime(ck[-1]) - os.path.getmtime(ck[0])
        per_unit_wall = span / max(1, len(ck) - 1)
    else:
        span, per_unit_wall = 0.0, None
    # the units observed were run at nproc=3 (out/sweep_M.log); report CPU-seconds/unit
    NPROC_OBSERVED = 3
    cpu_s_per_unit = per_unit_wall * NPROC_OBSERVED if per_unit_wall else None

    units_pads = len(SPB) * ORDERS * len(pads)
    units_iso = len(SPB) * ORDERS
    out = {
        "lane": "round19/C2",
        "item": "Marsaglia CDROM — exact offset space and measured cost",
        "verified_pads": len(pads), "pad_bytes_each": pad_bytes,
        "random_data_bytes": pad_bytes * len(pads),
        "iso_bytes": ISO_BYTES,
        "builders": sorted(SPB), "builders_excluded": ["hexchars (L6 §2.1)"],
        "byte_orders": ORDERS, "signs": SIGNS, "prefilter_window": PLEN,
        "offsets_per_pad_full_cross_product": per_pad,
        "offsets_all_63_pads": pads_total,
        "offsets_whole_iso_as_one_pad": iso_total,
        "offsets_pads_plus_iso": pads_total + iso_total,
        "units_pads": units_pads, "units_iso": units_iso,
        "units_total_pads_only": units_pads,
        "checkpointed_units": len(ck),
        "checkpointed_offsets": done_off,
        "fraction_of_pad_space_done": done_off / pads_total,
        "observed_wall_s_per_unit": per_unit_wall,
        "observed_nproc": NPROC_OBSERVED,
        "cpu_s_per_unit": cpu_s_per_unit,
        "est_cpu_hours_pads_only": (cpu_s_per_unit * units_pads / 3600.0)
                                   if cpu_s_per_unit else None,
        "est_cpu_hours_with_iso": (cpu_s_per_unit * (units_pads + units_iso * 63.4) / 3600.0)
                                  if cpu_s_per_unit else None,
        "resume": "cd liber-primus/analysis/round18/L6-offset-marsaglia/scripts && "
                  "python3 sweep_marsaglia.py --nproc 6 --budget <seconds>   "
                  "(checkpointed per (pad, builder, byte-order) in out/ckpt_M; "
                  "never recomputes a finished unit)",
        "comparison": {
            "round17_offsets_scored": 14_522_916_046,
            "note": "The Marsaglia pads alone are ~1.2x the entire Round 17 public-pad round.",
        },
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(os.path.join(C2, "out_marsaglia_space.json"), "w") as f:
        json.dump(out, f, indent=1)
    for k in ("verified_pads", "offsets_all_63_pads", "offsets_whole_iso_as_one_pad",
              "units_total_pads_only", "checkpointed_units", "checkpointed_offsets",
              "fraction_of_pad_space_done", "observed_wall_s_per_unit",
              "est_cpu_hours_pads_only", "est_cpu_hours_with_iso"):
        print(f"  {k:<34} {out[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
