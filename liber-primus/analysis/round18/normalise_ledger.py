#!/usr/bin/env python3
"""Normalise Round 18's merged entries to the ledger's controlled vocabulary.

The lanes invented ad-hoc statuses ("resolved", "run", "resolved-negative-for-the-worry")
and wrote prose into `positive_control` where the validator expects the literal token
`passed`.  Neither is a soundness problem -- every one of those lanes ran and reported a
passing control -- but the validator cannot see that, and a validator that cannot see a
control is the whole thing this ledger exists to prevent.

Two statuses are ADDED to the vocabulary rather than forcing square pegs into `negative`:

  * `measured` - the lane produced a definite quantitative determination that is not a
    null (which stream the filter acts on; the drift constant; the six payload bytes).
    Calling those "negative" would be false.
  * `audit`    - a recomputation, file audit or coverage restatement.  These have no null
    and no threshold, so holding them to the positive-control bar is a category error --
    and letting them sit as `negative` would let a non-test wear a test's authority.

`negative` and `eliminated` remain the only statuses the positive-control gate applies to,
so the gate keeps exactly the force it had.
"""
import json, pathlib

LEDGER = pathlib.Path("liber-primus/LEDGER.json")
led = json.loads(LEDGER.read_text(encoding="utf-8"))

for s in ("measured", "audit"):
    if s not in led["statuses"]:
        led["statuses"].append(s)

STATUS = {
    "A-04": "measured", "G-02": "measured", "G-09": "measured",
    "R18-L2-A-LOCUS": "measured", "R18-L2-B-DRIFT": "measured",
    "R18-L2-SKIP-CHANNEL": "measured",
    "I-01": "inconclusive",                      # the lane's own verdict was INDECISIVE
    "R18-L2-BEAM-LENGTH-POWER": "eliminated",    # the worry was tested and killed
    "R18-L2-INFO-BUDGET": "eliminated",          # the SAT/BP route is proved dead
    "L7-C-HEADLINE-STATS": "audit", "L7-C-G3-FLOOR-EXTENDED": "audit",
    "L7-C-B17-TALLY": "audit", "L7-A-HANDOFF-NONCOMPLIANCE": "audit",
    "RESTATE-B-04": "audit", "RESTATE-R16-KDF": "audit", "RESTATE-R16-PRNG": "audit",
    "RESTATE-R17-PUBLIC-PAD": "audit", "RESTATE-B-21-ROUND8-BAR": "audit",
}

changed = []
for e in led["entries"]:
    eid = e.get("id")
    if eid in STATUS and e.get("status") != STATUS[eid]:
        e["status_before_normalisation"] = e.get("status")
        e["status"] = STATUS[eid]
        changed.append(f"{eid}->{STATUS[eid]}")
    pc = e.get("positive_control")
    # prose control -> the literal token, prose preserved in control_detail
    if isinstance(pc, str) and pc.lower().startswith("passed") and pc.strip().lower() != "passed":
        e.setdefault("control_detail", pc)
        e["positive_control"] = "passed"
        changed.append(f"{eid}:pc-text")
    elif pc is True:
        e["positive_control"] = "passed"
        if not e.get("control_detail"):
            e["control_detail"] = "lane recorded a passing control; see the lane RESULTS.md"
        changed.append(f"{eid}:pc-bool")
    elif isinstance(pc, str) and pc.lower().startswith("n/a"):
        e.setdefault("control_detail", pc)
        e["positive_control"] = None      # honest: there was no scored control
        changed.append(f"{eid}:pc-na")

counts = {}
for e in led["entries"]:
    counts[e.get("status", "unknown")] = counts.get(e.get("status", "unknown"), 0) + 1
led["counts"]["by_status"] = dict(sorted(counts.items()))
led["counts"]["total"] = len(led["entries"])
led["counts"]["note"] += (
    " Two statuses were added in the Round 18 merge: `measured` (a definite non-null "
    "determination) and `audit` (a recomputation or coverage restatement, which has no null "
    "and no threshold). The positive-control gate still applies to `negative`/`eliminated` "
    "only, so it retains exactly its former force.")

LEDGER.write_text(json.dumps(led, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("changed:", len(changed))
for c in changed: print("  ", c)
print("counts:", led["counts"]["by_status"])
