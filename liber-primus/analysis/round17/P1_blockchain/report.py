"""Render the RESULTS.md tables from results.json (so the numbers in the write-up are
generated, never typed).

  python report.py
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))

print("### coverage\n")
print("| pad | bytes | builders | variants (builders x fwd/rev) | offsets scored (all variants x 2 signs) | best score |")
print("|---|---:|---|---:|---:|---:|")
for p in R["pads"]:
    print("| `%s` | %s | %s | %d | %s | %.3f |" % (
        p["pad"], format(p["bytes"], ","), p.get("builders_label", ""),
        len(p.get("builders", [])) * 2,
        format(p["n_offsets_total"], ","), p["best"]["score"]))
print("\ntotal offsets scored: **%s**" % format(R["n_offsets_total"], ","))
print("\n### top 20 (all pads, all builders, both signs, both skip budgets)\n")
print("| # | pad | builder | sign | max_skip | offset | score_norm | bar | beam head |")
print("|---:|---|---|---:|---:|---:|---:|---:|---|")
for i, r in enumerate(R["top20"], 1):
    print("| %d | `%s` | %s | %+d | %d | %s | **%.3f** | %.3f | `%s` |" % (
        i, r["pad"], r["variant"], r["sign"], r["max_skip"],
        format(r["offset"], ","), r["score"], r["bar"], r["head"][:28]))
