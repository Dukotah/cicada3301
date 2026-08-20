import json, os, hashlib
import gcore as G
P="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round12/A1/pads"
T={t["path"]:t["sha256"] for t in json.load(open("TARGETS.json")) if t["class"]=="cicadaos_pad"}
big=os.path.join(P,"DATA_560.13")
d=open(big,'rb').read()
print("len",len(d))
res={}
for nm in ("DATA_560.17","DATA__560.00","DATA__560.00.iso-authoritative","tmp_folly","tmp_wisdom"):
    o=open(os.path.join(P,nm),'rb').read()
    probe=o[:8192] if len(o)>=8192 else o
    idx=d.find(probe)
    res[nm]={"probe_len":len(probe),"found_at":idx,"is_substring_head":idx>=0}
    print(nm,"probe8k found at",idx)
# also: is the big file self-repeating? check for repeated 4KiB blocks
import collections
c=collections.Counter()
for i in range(0,len(d)-4096,4096):
    c[hashlib.sha1(d[i:i+4096]).digest()]+=1
dup=[(k.hex(),v) for k,v in c.items() if v>1]
print("dup 4KiB blocks:",len(dup), dup[:5])
res["dup_4k_blocks"]=len(dup)
res["total_4k_blocks"]=len(d)//4096
# byte histogram chi-square vs uniform
h=[0]*256
for x in d: h[x]+=1
exp=len(d)/256
chi=sum((v-exp)**2/exp for v in h)
res["chi2"]=round(chi,2); res["chi2_df"]=255
print("chi2",round(chi,2),"(df=255; ~255 expected for uniform random)")
res["min_byte_count"]=min(h); res["max_byte_count"]=max(h)
G.emit({"artifact_path":big,"artifact_sha256":T[big],"tool":"large-pad structural scan (pure python)",
 "tool_version":"G-1.0","command":"substring probe of every other pad; duplicate-4KiB-block census; byte chi-square",
 "params":{},"exit_code":0,"finding":"NEGATIVE" if not dup and all(v["found_at"]<0 for k,v in res.items() if isinstance(v,dict)) else "HIT",
 "output_excerpt":json.dumps(res),"output_file":None,
 "note":"Detects (a) any other pad embedded as a contiguous run inside the 118MB pad, (b) any internally repeated 4KiB block (keystream cycle / padding), (c) byte-frequency bias vs uniform. Blind to a relationship requiring transformation (XOR-with-constant, reordering, bit-rotation)."})
json.dump(res, open("raw/pad_big_scan.json","w"), indent=1)
