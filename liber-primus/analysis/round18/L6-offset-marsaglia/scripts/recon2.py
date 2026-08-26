import os, sys, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "round11"))
import lib_numchannel as nc

d = json.load(open(os.path.join(ROOT, "SOLVED-PAGES.json")))
print("reading_note:", str(d.get("reading_note"))[:300])
print("unsolved:", str(d.get("unsolved"))[:400])
pg = d["pages"]
print("n solved pages:", len(pg))
tot = 0
for k in (pg if isinstance(pg, dict) else range(len(pg))):
    p = pg[k]
    keys = list(p.keys()) if isinstance(p, dict) else None
    ct = p.get("ciphertext_runes") or p.get("runes") or p.get("ciphertext") or ""
    n = p.get("n_runes")
    print("  page", k, keys, "n_runes=", n, "len(ct)=", len(ct) if isinstance(ct, str) else "-")
    if n:
        tot += n
print("total solved runes:", tot)

segs = nc.segments()
print("n segments:", len(segs), "lens:", [len(s) for s in segs][:60])
print("cumulative page starts:", nc.cumulative()[:60] if hasattr(nc, "cumulative") else None)
