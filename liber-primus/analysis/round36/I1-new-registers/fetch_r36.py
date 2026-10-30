"""I1 fetch: save each new-register corpus into its own empty dir, log URL/sha256/bytes. Data only; never executed."""
import hashlib, json, os, sys, time, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
NT = ["Matthew","Mark","Luke","John","Acts","Romans","1-Corinthians","2-Corinthians","Galatians","Ephesians","Philippians",
      "Colossians","1-Thessalonians","2-Thessalonians","1-Timothy","2-Timothy","Titus","Philemon","Hebrews","James",
      "1-Peter","2-Peter","1-John","2-John","3-John","Jude","Revelation"]
HEB = ["Gen","Exod","Lev","Num","Deut","Josh","Judg"]
NOR = ["Egils_saga_Skalla-Grímssonar","Eyrbyggja_saga","Völsunga_saga","Ynglinga_saga","Gunnlaugs_saga_ormstungu",
       "Hrafnkels_saga_Freysgoða","Gísla_saga_Súrssonar","Fóstbræðra_saga","Laxdœla_saga"]
JOBS = {
 "greek_nestle1904": [(f"https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/{b}-ap.xhtml", f"{b}-ap.xhtml") for b in NT],
 "hebrew_wlc": [(f"https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/{b}.xml", f"{b}.xml") for b in HEB],
 "norse_heimskringla": [("https://heimskringla.no/wiki/" + urllib.parse.quote(t), t + ".html") for t in NOR],
}
log = {"fetched": time.strftime("%Y-%m-%d"), "note": "data only; never executed; each corpus in its own dir", "files": []}
for d, items in JOBS.items():
    p = os.path.join(HERE, "corpora", d); os.makedirs(p, exist_ok=True)
    for url, fn in items:
        dst = os.path.join(p, fn); data = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "cicada3301-rig"})
                with urllib.request.urlopen(req, timeout=60) as r: data = r.read()
                break
            except Exception as e:
                err = repr(e); time.sleep(3)
        if data is None:
            log["files"].append({"register_dir": d, "url": url, "status": "FAILED", "error": err}); print("FAIL", fn, err); continue
        open(dst, "wb").write(data)
        log["files"].append({"register_dir": d, "file": fn, "url": url, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "status": "ok"})
        print("ok", d, fn, len(data), flush=True); time.sleep(1.0 if "heimskringla" in url else 0.2)
json.dump(log, open(os.path.join(HERE, "fetch_log.json"), "w"), indent=1, ensure_ascii=False)
