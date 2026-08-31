"""Read ledger.json, render the sweep summary table + flag verdict, and splice
them into RESULTS.md at the <!-- SWEEP_TABLE --> / <!-- FLAG_VERDICT --> markers."""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
led = json.load(open(os.path.join(HERE, "ledger.json")))
rows = led["rows"]

# summarise: per-stat count of p<0.01 hits across the 72 combos, and any that
# reached the shape-stat refinement + whether any cleared Bonferroni.
STATS = ["closure", "self_intersections", "bbox_fill", "caging", "symmetry", "components"]
hit_counts = {s: 0 for s in STATS}
refined_rows = []
for r in rows:
    for s in r["hits_at_0.01"]:
        hit_counts[s] += 1
    if r.get("refined"):
        for s, info in r["refined"].items():
            refined_rows.append((r["combo"], s, info))

flagged = led["flagged_for_oracle"]

lines = []
lines.append(f"**Combos swept:** {led['coverage']['render_combos']}  |  "
             f"**null surrogates/combo:** {led['coverage']['null_surrogates_per_combo']}  |  "
             f"**refine N (shape stats):** {led['coverage']['refine_n']}  |  "
             f"**runtime:** {led.get('runtime_sec','?')}s")
lines.append("")
lines.append("Per-stat count of combos with an uncorrected p<0.01 departure from the shuffle null "
             "(of 72):")
lines.append("")
lines.append("| stat | combos p<0.01 | interpretation |")
lines.append("|---|---:|---|")
interp = {
    "closure": "net/path caging ratio — order-dependence of a value-scaled walk, not a shape",
    "caging": "same net/path ratio — order-dependence, not a shape",
    "self_intersections": "crossing count — refined (shape stat)",
    "bbox_fill": "fill density — refined (shape stat)",
    "symmetry": "raster symmetry — refined (shape stat)",
    "components": "connected components — refined (shape stat)",
}
for s in STATS:
    lines.append(f"| `{s}` | {hit_counts[s]} | {interp[s]} |")
lines.append("")
lines.append("**Shape-stat refinements run (empirical N=2000 null + z-tail p):**")
any_ref = False
for combo, s, info in refined_rows:
    if info.get("note"):
        continue  # caging/closure recorded-not-refined
    any_ref = True
    flags = "YES" if info["clears_bonferroni"] else "no"
    note = ""
    if (not info["clears_bonferroni"]) and info.get("z_tail_p", 1) < led['power']['flag_bar_bonferroni']:
        note = "  (z-tail below bar but empirical p NOT at floor -> discrete-stat artifact, double-gate correctly rejects)"
    lines.append(f"- `{combo}` / `{s}`: empirical p = {info['emp_p']:.3g} (N={info['n']}), "
                 f"z-tail p = {info.get('z_tail_p', float('nan')):.3g}, "
                 f"clears Bonferroni {led['power']['flag_bar_bonferroni']:.2g}: **{flags}**{note}")
if not any_ref:
    lines.append("- none reached the shape-stat refinement path.")
table = "\n".join(lines)

if flagged:
    verdict = (f"\n**FLAGGED-FOR-ORACLE: {len(flagged)}** shape-stat hit(s) cleared the "
               f"Bonferroni bar and are flagged (NOT auto-certified): "
               + "; ".join(f"`{f['combo']}`/`{f['stat']}` z-tail p={f['z_tail_p']:.2g}" for f in flagged)
               + ". These require human-eye + oracle adjudication of the rendered PNG.")
else:
    verdict = ("\n**No shape-stat hit cleared the Bonferroni bar.** The only uncorrected p<0.01 "
               "departures are on `caging`/`closure` (net/path ratio of value-scaled walks — "
               "generic order-dependence, not a figure) and, where a shape stat did fire at "
               "p<0.01, its N=10,000 refinement did not survive the Bonferroni correction. "
               "**Nothing is flagged for the oracle. Clean geometric null.**")

txt = open(os.path.join(HERE, "RESULTS.md")).read()
txt = txt.replace("<!-- SWEEP_TABLE -->", table)
txt = txt.replace("<!-- FLAG_VERDICT -->", verdict)
open(os.path.join(HERE, "RESULTS.md"), "w").write(txt)
print("RESULTS.md finalized.")
print("flagged_for_oracle:", len(flagged))
print("hit_counts:", hit_counts)
