"""Apply ledger_patches_b.json to LEDGER.json (coordinator step; idempotent).
notes_add / not_covered_add append with a space separator if the text is not already present."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LEDGER = os.path.join(LP, "LEDGER.json")

doc = json.load(open(LEDGER, encoding="utf-8"))
ids = {e["id"]: e for e in doc["entries"]}
pats = json.load(open(os.path.join(HERE, "ledger_patches_b.json"), encoding="utf-8"))["patches"]

changed = 0
for p in pats:
    e = ids.get(p["id"])
    if e is None:
        print("MISSING ROW", p["id"]); sys.exit(1)
    for k, v in p.items():
        if k == "id":
            continue
        assert k.endswith("_add"), k
        fld = k[: -len("_add")]
        cur = e.get(fld) or ""
        if v in cur:
            print("already   ", p["id"], fld)
            continue
        e[fld] = (cur.rstrip() + " " + v).strip()
        changed += 1
        print("patched   ", p["id"], fld)

json.dump(doc, open(LEDGER, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("fields changed:", changed)
