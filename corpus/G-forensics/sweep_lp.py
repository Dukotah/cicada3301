import json, hashlib, os, collections
import gcore as G
from jpegdeep import parse_jpeg
T=json.load(open("TARGETS.json"))
pages=[t for t in T if t["class"]=="lp_page"]
pages.sort(key=lambda t:int(os.path.basename(t["path"])[1:-4]))
allp={}
for t in pages:
    p=t["path"]; n=os.path.basename(p)
    r=parse_jpeg(p); allp[n]=r
    # --- container/metadata parse
    G.emit({"artifact_path":p,"artifact_sha256":t["sha256"],"tool":"jpegdeep.py (this lane, pure python)",
      "tool_version":"G-1.0","command":f"python3 jpegdeep.py {n}","params":{},"exit_code":0,
      "finding":"NEGATIVE" if not r["com"] and not any(a["ident"] not in ("JFIF","ICC_PROFILE") for a in r["appn"]) else "HIT",
      "output_excerpt":json.dumps({"appn":[a["ident"] for a in r["appn"]],"com":r["com"],
         "sof":r["sof"],"ndqt":len(r["dqt"]),"nhuff":r["huff_count"],"dri":r["dri"]}),
      "output_file":"raw/lp_jpeg_segments.json",
      "note":"Enumerates every JPEG marker segment. Would detect any EXIF(APP1), XMP, Photoshop(APP13), Adobe(APPE), COM comment, or non-standard APPn payload."})
    # --- appended data
    G.emit({"artifact_path":p,"artifact_sha256":t["sha256"],"tool":"appended-data check (pure python)",
      "tool_version":"G-1.0","command":"scan for FFD9 EOI, measure bytes after","params":{},"exit_code":0,
      "finding":"HIT" if r["trailing"]>0 else "NEGATIVE",
      "output_excerpt":json.dumps({"eoi_offset":r["eoi_offset"],"trailing_bytes":r["trailing"],
        "trailing_sha256":r["trailing_sha256"],"trailing_head_hex":r.get("trailing_head_hex")}),
      "output_file":"raw/lp_jpeg_segments.json",
      "note":"Byte-exact. Would detect any appended archive/text/blob after the JPEG terminal marker, incl. a single byte."})
    # --- ICC interior
    icc=r["icc"]
    if icc:
        gaps=[g for g in icc.get("uncovered_gaps",[]) if g["len"]>3]
        G.emit({"artifact_path":p,"artifact_sha256":t["sha256"],"tool":"ICC profile interior parse (pure python)",
         "tool_version":"G-1.0","command":"parse ICC header+tag table, hash every tag, find uncovered slack",
         "params":{},"exit_code":0,
         "finding":"HIT" if gaps else "NEGATIVE",
         "output_excerpt":json.dumps({"icc_sha256":icc["sha256"],"len":icc["len"],"created":icc["created"],
            "cmm":icc["cmm"],"version":icc["version"],"manufacturer":icc["manufacturer"],"model":icc["model"],
            "creator":icc["creator"],"profile_id":icc["profile_id"],"reserved_100_128":icc["reserved_bytes_100_128"],
            "tag_count":icc["tag_count"],"tags":[t2["sig"] for t2 in icc["tags"]],
            "uncovered_gaps":icc.get("uncovered_gaps"),"trailing_after_size_field":icc.get("trailing_after_size_field")}),
         "output_file":"raw/lp_jpeg_segments.json",
         "note":"Parses the ICC beyond exiftool's tag view: header reserved bytes, profile ID, per-tag SHA1, and any byte range NOT covered by the tag table (classic slack-space hiding spot)."})
json.dump(allp, open("raw/lp_jpeg_segments.json","w"), indent=1)

# ---- clustering
dqtsig=collections.defaultdict(list); iccsig=collections.defaultdict(list)
huffsig=collections.defaultdict(list); sofsig=collections.defaultdict(list); jfifsig=collections.defaultdict(list)
for n,r in allp.items():
    dqtsig["|".join(d["sha1"][:12] for d in r["dqt"])].append(n)
    iccsig[r["icc"]["sha256"][:16] if r["icc"] else "none"].append(n)
    hs=hashlib.sha1(json.dumps([s for s in r["segments"] if s["marker"]=="FFC4"]).encode()).hexdigest()[:12]
    huffsig[str(r["huff_count"])].append(n)
    sofsig[json.dumps(r["sof"])].append(n)
    j=[a.get("jfif") for a in r["appn"] if a["ident"]=="JFIF"]
    jfifsig[json.dumps(j)].append(n)
clusters={"dqt":{k:sorted(v,key=lambda x:int(x[1:-4])) for k,v in dqtsig.items()},
 "icc":{k:len(v) for k,v in iccsig.items()},
 "icc_members":{k:sorted(v,key=lambda x:int(x[1:-4])) for k,v in iccsig.items()},
 "sof":{k:sorted(v,key=lambda x:int(x[1:-4])) for k,v in sofsig.items()},
 "jfif":{k:len(v) for k,v in jfifsig.items()},
 "huff_count":{k:len(v) for k,v in huffsig.items()}}
json.dump(clusters, open("raw/lp_clusters.json","w"), indent=1)
print("DQT clusters:", {k[:12]:len(v) for k,v in dqtsig.items()})
for k,v in dqtsig.items(): print("  ",k[:12], sorted(v,key=lambda x:int(x[1:-4])))
print("ICC clusters:", {k:len(v) for k,v in iccsig.items()})
print("SOF variants:", {k:len(v) for k,v in sofsig.items()})
print("JFIF variants:", {k:len(v) for k,v in jfifsig.items()})
print("trailing bytes nonzero:", [n for n,r in allp.items() if r["trailing"]>0])
print("COM present:", [n for n,r in allp.items() if r["com"]])
print("APPn idents seen:", set(a["ident"] for r in allp.values() for a in r["appn"]))
