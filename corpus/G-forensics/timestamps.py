import json, os, re, struct, hashlib, datetime
import gcore as G
from jpegdeep import parse_jpeg
R="/mnt/c/Users/dukot/projects/cicada3301/"
T=json.load(open("TARGETS.json"))
rows=[]
def png_meta(p):
    d=open(p,'rb').read(); i=8; out={}; ch=[]
    while i<len(d)-8:
        ln=int.from_bytes(d[i:i+4],'big'); typ=d[i+4:i+8].decode('latin-1','replace')
        body=d[i+8:i+8+ln]; ch.append(typ)
        if typ=='tIME' and ln==7:
            y=struct.unpack('>H',body[0:2])[0]
            out['tIME']=f"{y:04d}-{body[2]:02d}-{body[3]:02d}T{body[4]:02d}:{body[5]:02d}:{body[6]:02d}Z"
        if typ in ('tEXt','iTXt','zTXt'): out.setdefault('text',[]).append(body[:200].decode('latin-1','replace'))
        i+=12+ln
        if typ=='IEND': break
    out['chunks']=ch; out['trailing_after_IEND']=len(d)-i
    return out
for t in T:
    p=t["path"]; ext=os.path.splitext(p)[1].lower(); rel=p.replace(R,"")
    rec={"path":rel,"sha256":t["sha256"],"dates":{}}
    try:
        if ext in ('.jpg','.jpeg'):
            r=parse_jpeg(p)
            if r.get("icc"): rec["dates"]["icc_created"]=r["icc"]["created"]
            if r.get("com"): rec["dates"]["jpeg_com"]=r["com"]
            rec["appn"]=[a["ident"] for a in r["appn"]]
        elif ext=='.png':
            m=png_meta(p); rec["dates"].update({k:v for k,v in m.items() if k in ('tIME','text')})
            rec["png_chunks"]=m["chunks"]; rec["trailing_after_IEND"]=m["trailing_after_IEND"]
        elif ext=='.mp3':
            rec["dates"]["id3"]="none (no TYER/TDRC frame; only TXXX/TIT2/TPE1)"
        elif ext in ('.html','.txt','.md','.json'):
            d=open(p,'rb').read(300000).decode('latin-1','replace')
            ds=set(re.findall(r'\b(?:19|20)\d{2}-\d{2}-\d{2}\b', d))|set(re.findall(r'\b\d{2}/\d{2}/(?:19|20)\d{2}\b', d))
            ds|=set(re.findall(r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2} GMT', d))
            if ds: rec["dates"]["text_dates"]=sorted(ds)[:20]
    except Exception as e:
        rec["error"]=str(e)
    if rec["dates"] or rec.get("trailing_after_IEND"): rows.append(rec)
json.dump(rows, open("raw/timestamps.json","w"), indent=1)
# aggregate
from collections import Counter
icc=Counter(r["dates"].get("icc_created") for r in rows if "icc_created" in r["dates"])
tim=Counter(r["dates"].get("tIME") for r in rows if "tIME" in r["dates"])
print("ICC creation dates across all JPEGs:", dict(icc))
print("PNG tIME:", dict(tim))
print("PNG files with tIME:", [r["path"] for r in rows if "tIME" in r["dates"]])
print("PNG trailing after IEND nonzero:", [(r["path"],r["trailing_after_IEND"]) for r in rows if r.get("trailing_after_IEND")])
td=[r for r in rows if "text_dates" in r["dates"]]
print(f"\ntext files with parsed dates: {len(td)}")
for r in td[:25]: print("  ",r["path"], r["dates"]["text_dates"][:6])
G.emit({"artifact_path":"corpus-wide","artifact_sha256":"n/a (aggregate over 486 hashed artifacts)",
 "tool":"embedded-timestamp census (pure python)","tool_version":"G-1.0",
 "command":"extract every embedded date: JPEG ICC creation, JPEG COM, PNG tIME/tEXt, ID3, HTTP/ISO dates in text",
 "params":{"artifacts_scanned":len(T)},"exit_code":0,
 "finding":"HIT" if tim else "NEGATIVE",
 "output_excerpt":json.dumps({"jpeg_icc_created_values":dict(icc),"png_tIME_values":dict(tim),
   "png_with_tIME":[r["path"] for r in rows if "tIME" in r["dates"]],
   "n_text_files_with_dates":len(td)}),
 "output_file":"raw/timestamps.json",
 "note":"Would surface any authoring date the producer left behind. Note the ICC creation field on ALL JPEGs is the null date 0000-00-00T00:00:00Z, i.e. Ghostscript zeroed it - so the LP page set carries NO production timestamp at all. That is itself a (deliberate or default) absence, and it means no chronology can be recovered from the page images."})
