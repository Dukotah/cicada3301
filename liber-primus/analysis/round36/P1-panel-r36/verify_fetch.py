"""P1: re-fetch every network-obtained corpus into refetch/ (never touching data/ or I1/corpora) and compare sha256 to what is on disk.
Welsh substitute: calls data/fetch_sources.ensure_welsh_substitute with WELSH_DST redirected into refetch/. Writes verify_fetch.json."""
import hashlib, json, os, sys, time, urllib.request
LANE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(LANE, "..", "..", ".."))
I1 = os.path.join(LANE, "..", "I1-new-registers")
RF = os.path.join(LANE, "refetch"); os.makedirs(RF, exist_ok=True)
sys.path.insert(0, os.path.join(LP, "data")); import fetch_sources as fs
sha = lambda b: hashlib.sha256(b).hexdigest()
res = {"when": time.strftime("%Y-%m-%dT%H:%M:%S"), "items": []}
def get(url):
    for a in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "cicada3301-rig"}), timeout=90).read()
        except Exception as e:
            err = repr(e); time.sleep(3)
    return err
# Welsh substitute via the repo's own function
fs.WELSH_DST = os.path.join(RF, "welsh_mabinogion.txt")
try:
    fs.ensure_welsh_substitute(force=True, verbose=False)
    b = open(fs.WELSH_DST, "rb").read(); disk = open(os.path.join(LP, "data/keys/welsh/welsh_mabinogion.txt"), "rb").read()
    res["items"].append({"what": "CY welsh substitute (fetch_sources --welsh)", "refetch_sha": sha(b), "refetch_bytes": len(b), "disk_sha": sha(disk), "disk_bytes": len(disk), "match": sha(b) == sha(disk)})
except Exception as e:
    res["items"].append({"what": "CY welsh substitute (fetch_sources --welsh)", "error": repr(e)})
for rel, (url, want, n) in fs.R19_CORPORA.items():
    b = get(url)
    if isinstance(b, str): res["items"].append({"what": rel, "url": url, "error": b}); continue
    disk = open(os.path.join(LP, "data", rel), "rb").read()
    res["items"].append({"what": "data/" + rel.replace("\\", "/"), "url": url, "refetch_sha": sha(b), "disk_sha": sha(disk), "recorded_sha": want, "match": sha(b) == sha(disk) == want})
log = json.load(open(os.path.join(I1, "fetch_log.json"), encoding="utf-8"))
for e in log["files"]:
    if e.get("status") != "ok": continue
    b = get(e["url"])
    if isinstance(b, str): res["items"].append({"what": e["register_dir"] + "/" + e["file"], "url": e["url"], "error": b}); continue
    disk = open(os.path.join(I1, "corpora", e["register_dir"], e["file"]), "rb").read()
    res["items"].append({"what": e["register_dir"] + "/" + e["file"], "url": e["url"], "logged_sha": e["sha256"], "refetch_sha": sha(b), "disk_sha": sha(disk), "match": sha(b) == sha(disk) == e["sha256"]})
    time.sleep(1.0 if "heimskringla" in e["url"] else 0.1)
res["n_match"] = sum(1 for i in res["items"] if i.get("match")); res["n_total"] = len(res["items"])
json.dump(res, open(os.path.join(LANE, "verify_fetch.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(res["n_match"], "/", res["n_total"], "match")
for i in res["items"]:
    if not i.get("match"): print("NOMATCH", i)
