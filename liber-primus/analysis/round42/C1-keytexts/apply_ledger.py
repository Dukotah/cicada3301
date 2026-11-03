"""Apply R42 S1/S3 ledger changes to LEDGER.json (coordinator step; idempotent).
Adds new_rows if absent, sets statuses, appends notes. Run from anywhere."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LEDGER = os.path.join(LP, "LEDGER.json")

doc = json.load(open(LEDGER, encoding="utf-8"))
by_id = {e["id"]: e for e in doc["entries"]}
spec = json.load(open(os.path.join(HERE, "ledger_patches.json"), encoding="utf-8"))

added = changed = 0
for row in spec["new_rows"]:
    if row["id"] in by_id:
        print("exists   ", row["id"])
        continue
    doc["entries"].append(row)
    by_id[row["id"]] = row
    added += 1
    print("added    ", row["id"])

for p in spec["patches"]:
    e = by_id[p["id"]]
    if "set_status" in p and e.get("status") != p["set_status"]:
        print(f"status   {p['id']}: {e.get('status')} -> {p['set_status']}")
        e["status"] = p["set_status"]; changed += 1
    if "notes_add" in p:
        cur = e.get("notes") or ""
        if p["notes_add"] in cur:
            print("note-skip", p["id"])
        else:
            e["notes"] = (cur.rstrip() + " " + p["notes_add"]).strip()
            changed += 1
            print("note-add ", p["id"])

json.dump(doc, open(LEDGER, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"rows added {added}, fields changed {changed}, total entries {len(doc['entries'])}")
