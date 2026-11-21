#!/usr/bin/env python3
"""R44 W2-C4 — closeout: compile summary.json from both arm TSVs, gzip the raw rows."""
import csv, gzip, json, os, shutil, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(CELL, "results")

def summarize(path):
    rows = list(csv.DictReader(open(path), delimiter="\t"))
    og = [r for r in rows if r["tool"] == "og"]
    sh = [r for r in rows if r["tool"] == "sh"]
    ne = [r for r in og if int(r["out_len"]) > 0]
    return dict(
        rows=len(rows), og=len(og), sh=len(sh),
        og_nonempty=len(ne),
        flags=sum(int(r["flag"]) for r in rows),
        f1=sum(int(r["f1"]) for r in rows),
        f2=sum(int(r["f2"]) for r in rows),
        f3=sum(int(r["f3"]) for r in rows),
        naive=sum(int(r["naive"]) for r in rows),
        sh_success=sum(int(r["flag"]) for r in sh),
        og_nonempty_median_entropy=round(statistics.median(
            float(r["entropy"]) for r in ne), 4) if ne else None,
        pages=len({r["page"] for r in rows}),
        keys=len({r["key"] for r in rows}),
    )

out = {}
for name, f in [("ARM_D", "sweep_stats_derived.tsv"),
                ("ARM_G", "sweep_stats_global_0_56.tsv")]:
    p = os.path.join(RES, f)
    out[name] = summarize(p)
    with open(p, "rb") as src, gzip.open(p + ".gz", "wb") as dst:
        shutil.copyfileobj(src, dst)
    os.unlink(p)

out["controls"] = json.load(open(os.path.join(RES, "controls.json")))
out["calibration"] = json.load(open(os.path.join(RES, "calibration.json")))
out["total_extractions"] = out["ARM_D"]["rows"] + out["ARM_G"]["rows"]
json.dump(out, open(os.path.join(RES, "summary.json"), "w"), indent=1, default=str)
print(json.dumps({k: out[k] for k in ("ARM_D", "ARM_G", "total_extractions")}, indent=1))
