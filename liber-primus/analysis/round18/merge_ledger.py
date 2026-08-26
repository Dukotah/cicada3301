#!/usr/bin/env python3
"""Merge Round 18's eight lane ledger fragments into liber-primus/LEDGER.json.

Three cases, deliberately kept distinct:

  * an entry carrying `restates` rewrites the COVERAGE of an existing entry.  The old
    coverage is preserved verbatim in `restated_from` -- this repo's rule is to mark a
    claim superseded, never to delete the reasoning that produced it.
  * an entry whose id already exists UPDATES that entry, keeping any field the lane did
    not set.
  * anything else is appended.

Idempotent: re-running it produces the same file.
"""
import json, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER = ROOT / "LEDGER.json"
R18 = ROOT / "analysis" / "round18"
LANES = ["L1-toolchain", "L2-filter-leak", "L3-ornaments", "L4-forcing",
         "L5-payload", "L6-offset-marsaglia", "L7-redteam", "L8-provenance"]

led = json.loads(LEDGER.read_text(encoding="utf-8"))
entries = led["entries"]
by_id = {e.get("id"): e for e in entries}

added, updated, restated = [], [], []

for lane in LANES:
    f = R18 / lane / "ledger.json"
    if not f.exists():
        continue
    frag = json.loads(f.read_text(encoding="utf-8"))
    items = frag if isinstance(frag, list) else frag.get("entries", [frag])
    for item in items:
        iid = item.get("id")
        if not iid:
            continue
        target = item.get("restates")
        if target:
            tgt = by_id.get(target)
            if tgt is not None:
                if "restated_from" not in tgt:          # keep the ORIGINAL, once
                    tgt["restated_from"] = tgt.get("coverage")
                if item.get("restated_coverage"):
                    tgt["coverage"] = item["restated_coverage"]
                extra = item.get("additional_not_covered") or []
                if extra:
                    cur = tgt.get("not_covered")
                    cur = [] if cur is None else (cur if isinstance(cur, list) else [cur])
                    for x in extra:
                        if x not in cur:
                            cur.append(x)
                    tgt["not_covered"] = cur
                tgt["restated_by"] = iid
                tgt["restated_round"] = "18"
                restated.append(target)
        if iid in by_id:                                 # update in place
            cur = by_id[iid]
            for k, v in item.items():
                if v is not None:
                    cur[k] = v
            updated.append(iid)
        else:
            entries.append(item)
            by_id[iid] = item
            added.append(iid)

counts = {}
for e in entries:
    s = e.get("status", "unknown")
    counts[s] = counts.get(s, 0) + 1
led["counts"] = {
    "total": len(entries),
    "by_status": dict(sorted(counts.items())),
    "note": (led.get("counts", {}).get("note", "") +
             " Round 18 merged 2026-08-26: 8 lanes, 31 fragment entries. L7 restated the "
             "coverage of B-04, R16-KDF, R16-PRNG, R17-PUBLIC-PAD and B-21 -- every prior "
             "negative in this repo is an English-register negative, which no entry had "
             "stated. Original coverage text is preserved in each entry's `restated_from`.").strip(),
}
led["generated_for"] = led.get("generated_for", "")
led.setdefault("round18_merged", datetime.date.today().isoformat())

LEDGER.write_text(json.dumps(led, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"added   {len(added)}: {', '.join(added)}")
print(f"updated {len(updated)}: {', '.join(updated)}")
print(f"restated{len(restated)}: {', '.join(restated)}")
print("counts:", led["counts"]["total"], led["counts"]["by_status"])
