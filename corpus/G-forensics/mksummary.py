#!/usr/bin/env python3
"""Lane G — build RESULTS-SUMMARY.json.

RESULTS.jsonl is ~50 MB and gitignored. This distils it into a committable artifact:
  * counts by (tool x finding) and by (tool x artifact class x finding)
  * per-artifact-class coverage: which instruments actually examined that class
  * EVERY row with finding == HIT, with its evidence excerpt
  * EVERY row with finding == ERROR
  * EVERY row with finding == NOT_APPLICABLE, grouped
so the findings survive in git even though the raw output does not.
"""
import json, os, collections, time, hashlib

G = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(G, "RESULTS.jsonl")
targets = {t["path"]: t for t in json.load(open(os.path.join(G, "TARGETS.json")))}

rows = []
malformed = 0
for l in open(SRC, encoding="utf-8"):
    l = l.strip()
    if not l:
        continue
    try:
        rows.append(json.loads(l))
    except Exception:
        malformed += 1


def klass(r):
    return r.get("artifact_class") or (targets.get(r.get("artifact_path") or "", {}) or {}).get("class") or "(other/derived)"


tool_finding = collections.Counter()
tool_class_finding = collections.Counter()
class_tools = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
for r in rows:
    t, f, k = r.get("tool"), r.get("finding"), klass(r)
    tool_finding[(t, f)] += 1
    tool_class_finding[(t, k, f)] += 1
    class_tools[k][t][f] += 1

hits, errors, nas = [], [], []
for r in rows:
    f = r.get("finding")
    rec = {
        "artifact_path": r.get("artifact_path"),
        "artifact_sha256": r.get("artifact_sha256"),
        "artifact_class": klass(r),
        "tool": r.get("tool"),
        "tool_version": r.get("tool_version"),
        "command": r.get("command"),
        "exit_code": r.get("exit_code"),
        "finding": f,
        "evidence": (r.get("output_excerpt") or "")[:1200],
        "note": r.get("note"),
        "output_file": r.get("output_file"),
        "run_utc": r.get("run_utc"),
    }
    if f == "HIT":
        hits.append(rec)
    elif f == "ERROR":
        errors.append(rec)
    elif f == "NOT_APPLICABLE":
        nas.append(rec)

# NOT_APPLICABLE is grouped rather than listed per-artifact (338 identical steghide rows)
na_groups = collections.Counter((r["tool"], r["artifact_class"], (r["note"] or "")[:160]) for r in nas)

# artifact-class coverage: which instruments touched each class at all
coverage = {}
class_totals = collections.Counter(t["class"] for t in targets.values())
for k, tools in class_tools.items():
    coverage[k] = {
        "artifacts_in_class": class_totals.get(k),
        "instruments": {tool: dict(fc) for tool, fc in sorted(tools.items())},
    }

src_stat = os.stat(SRC)
out = {
    "lane": "G-forensics",
    "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "purpose": ("Committable distillation of RESULTS.jsonl, which is gitignored at ~%.1f MB. "
                "Counts by tool x finding, full HIT list with evidence, full ERROR list, "
                "grouped NOT_APPLICABLE, and per-class instrument coverage."
                % (src_stat.st_size / 1e6)),
    "source": {
        "file": "corpus/G-forensics/RESULTS.jsonl",
        "bytes": src_stat.st_size,
        "rows": len(rows),
        "malformed_rows_skipped": malformed,
        "sha256": hashlib.sha256(open(SRC, "rb").read()).hexdigest(),
    },
    "finding_vocabulary": {
        "HIT": "the instrument reported something. NOT automatically a payload - see each row's note; several HITs are known instrument false positives and are adjudicated in REPORT-G.md.",
        "NEGATIVE": "the instrument examined the artifact and reported nothing.",
        "NOT_APPLICABLE": "the instrument could NOT examine this artifact (unsupported container etc). Contributes no evidence either way. Never to be read as NEGATIVE.",
        "ERROR": "the instrument failed or was killed. Contributes no evidence either way.",
    },
    "totals_by_finding": dict(collections.Counter(r.get("finding") for r in rows)),
    "artifact_classes": dict(class_totals),
    "counts_by_tool_and_finding": [
        {"tool": t, "finding": f, "count": c} for (t, f), c in sorted(tool_finding.items(), key=lambda kv: (kv[0][0] or "", kv[0][1] or ""))
    ],
    "counts_by_tool_class_finding": [
        {"tool": t, "artifact_class": k, "finding": f, "count": c}
        for (t, k, f), c in sorted(tool_class_finding.items(), key=lambda kv: (kv[0][0] or "", kv[0][1] or "", kv[0][2] or ""))
    ],
    "coverage_by_artifact_class": coverage,
    "hits": hits,
    "errors": errors,
    "not_applicable_grouped": [
        {"tool": t, "artifact_class": k, "count": c, "note": n}
        for (t, k, n), c in sorted(na_groups.items())
    ],
}
p = os.path.join(G, "RESULTS-SUMMARY.json")
json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
print("wrote", p, os.path.getsize(p), "bytes |", len(rows), "rows |",
      len(hits), "HIT |", len(errors), "ERROR |", len(nas), "NOT_APPLICABLE")
