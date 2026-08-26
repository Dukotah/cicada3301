"""Emit the RESULTS.md tables straight from the out_*.json files (no transcription)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(n):
    p = os.path.join(HERE, n)
    return json.load(open(p)) if os.path.exists(p) else None


def allfix():
    a = load("out_fix.json")
    b = load("out_fix2.json")
    if not a:
        return None
    if b:
        a = dict(a)
        a["summary"] = a["summary"] + b["summary"]
        a["modes"] = {**a["modes"], **b["modes"]}
    return a


def fixtable(cols, lengths=(240, 400), only_gate=None):
    fx = allfix()
    if not fx:
        return "(out_fix.json missing)"
    S = fx["summary"]
    labels = []
    for s in S:
        if s["label"] not in labels:
            labels.append(s["label"])
    out = []
    for L in lengths:
        out.append(f"\n**L = {L}**\n")
        out.append("| construction | " + " | ".join(cols) + " |")
        out.append("|---|" + "---|" * len(cols))
        for lab in labels:
            rows = {s["mode"]: s for s in S if s["label"] == lab and s["L"] == L}
            if not rows:
                continue
            g = list(rows.values())[0]["in_gate"]
            if only_gate is not None and g != only_gate:
                continue
            cells = []
            for c in cols:
                r = rows.get(c)
                if r is None:
                    cells.append("—")
                else:
                    mark = "" if r["PASS"] else " ✗"
                    cells.append(f"{r['median_score']:.3f} / {r['median_recovery']*100:.1f}%{mark}")
            star = " **[GATE]**" if g else ""
            out.append(f"| {lab}{star} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def basetable():
    b = load("out_base.json")
    if not b:
        return "(out_base.json missing)"
    S = b["summary"]
    modes = []
    for s in S:
        if s["mode"] not in modes:
            modes.append(s["mode"])
    labels = []
    for s in S:
        k = (s["label"], s["L"])
        if k not in labels:
            labels.append(k)
    out = ["| baseline construction | L | " + " | ".join(modes) + " |",
           "|---|---|" + "---|" * len(modes)]
    for (lab, L) in labels:
        cells = []
        for m in modes:
            r = next((s for s in S if s["label"] == lab and s["L"] == L
                      and s["mode"] == m), None)
            cells.append("—" if r is None else
                         f"{r['median_score']:.3f} / {r['median_recovery']*100:.1f}%")
        out.append(f"| {lab} | {L} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def fptable(stage="deep"):
    f = load(f"out_fp_{stage}.json")
    if not f:
        return f"(out_fp_{stage}.json missing)"
    out = ["| null | mode | n | mean | sd | median | p90 | p99 | max | frac >= -5.5 | mean inferred skips |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in f["summary"]:
        out.append("| {null} | {mode} | {n} | {mean:.3f} | {sd:.3f} | {median:.3f} | "
                   "{p90:.3f} | {p99:.3f} | {max:.3f} | {fo:.4f} | {sk:.0f} |".format(
                       null=s["null"], mode=s["mode"], n=s["n"], mean=s["mean"],
                       sd=s["sd"], median=s["median"], p90=s["p90"], p99=s["p99"],
                       max=s["max"], fo=s["frac_over_-5.5"], sk=s["mean_n_skips"]))
    return "\n".join(out)


def gate_verdicts():
    fx = allfix()
    if not fx:
        return "(missing)"
    S = fx["summary"]
    modes = list(fx["modes"].keys())
    out = ["| mode | gate constructions passed (L=240) | (L=400) | all 20 cells |",
           "|---|---|---|---|"]
    for m in modes:
        n240 = [s for s in S if s["mode"] == m and s["L"] == 240 and s["in_gate"]]
        n400 = [s for s in S if s["mode"] == m and s["L"] == 400 and s["in_gate"]]
        a = sum(1 for s in n240 if s["PASS"])
        b = sum(1 for s in n400 if s["PASS"])
        ok = (a == len(n240) and b == len(n400))
        out.append(f"| `{m}` | {a}/{len(n240)} | {b}/{len(n400)} | "
                   f"{'**PASS**' if ok else 'FAIL'} |")
    return "\n".join(out)


def costnum():
    b = load("out_base.json")
    if not b:
        return "(missing)"
    S = b["summary"]
    lines = []
    for L in (240, 400):
        for lab in sorted({s["label"] for s in S}):
            a = next((s for s in S if s["mode"] == "repo_ms3" and s["L"] == L
                      and s["label"] == lab), None)
            c = next((s for s in S if s["mode"] == "drift_l8" and s["L"] == L
                      and s["label"] == lab), None)
            if a and c:
                lines.append((lab, L, c["median_score"] - a["median_score"],
                              c["median_recovery"] - a["median_recovery"]))
    out = ["| baseline construction | L | delta score (drift_l8 - repo) | delta recovery |",
           "|---|---|---|---|"]
    for lab, L, ds, dr in lines:
        out.append(f"| {lab} | {L} | {ds:+.3f} | {dr*100:+.1f} pp |")
    worst_s = min(x[2] for x in lines)
    worst_r = min(x[3] for x in lines)
    out.append("")
    out.append(f"**Worst-case G-COST on the baseline construction: "
               f"score {worst_s:+.3f}, recovery {worst_r*100:+.1f} pp.**")
    return "\n".join(out)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "verdicts"):
        print("### gate verdicts\n" + gate_verdicts() + "\n")
    if what in ("all", "base"):
        print("### G-BASE\n" + basetable() + "\n")
        print("### G-COST\n" + costnum() + "\n")
    if what in ("all", "fix"):
        print("### G-FIX (gate rows only)\n" + fixtable(
            ["repo_ms3", "exact_auto", "pair_ms8", "drift_l0", "drift_l4",
             "drift_l8", "drift_l16"], only_gate=True) + "\n")
        print("### non-gate rows\n" + fixtable(
            ["repo_ms3", "exact_auto", "pair_ms8", "drift_l4", "drift_l8"],
            only_gate=False) + "\n")
        print("### mf sweep\n" + fixtable(
            ["drift_mf1", "drift_l8", "drift_mf3"], only_gate=True) + "\n")
    if what in ("all", "fp"):
        print("### G-FP deep\n" + fptable("deep") + "\n")
        print("### G-FP curve\n" + fptable("curve") + "\n")
