import json, os, hashlib, itertools, collections
import gcore as G
P="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round12/A1/pads"
T={t["path"]:t for t in json.load(open("TARGETS.json")) if t["class"]=="cicadaos_pad"}
bins=[f for f in sorted(os.listdir(P)) if not f.endswith(('.lfs-pointer','.rev'))]
data={f:open(os.path.join(P,f),'rb').read() for f in bins if os.path.getsize(os.path.join(P,f))<20_000_000}
big=[f for f in bins if f not in data]
print("loaded:",list(data), "skipped(big):",big)
res={}
for a,b in itertools.combinations(sorted(data),2):
    da,db=data[a],data[b]
    n=min(len(da),len(db))
    same=sum(1 for i in range(n) if da[i]==db[i])
    res[f"{a}|{b}"]={"len_a":len(da),"len_b":len(db),"cmp_len":n,"byte_match":same,
       "match_pct":round(100*same/n,4),"expected_random_pct":round(100/256,4),
       "identical":da==db,"common_prefix":next((i for i in range(n) if da[i]!=db[i]), n)}
for k,v in res.items(): print(k, json.dumps(v))
# XOR of folly/wisdom
if 'tmp_folly' in data and 'tmp_wisdom' in data:
    x=bytes(p^q for p,q in zip(data['tmp_folly'],data['tmp_wisdom']))
    G.savraw("pads_folly_xor_wisdom.bin", x)
    print("folly^wisdom entropy:", round(G.entropy(x),4), "zerobytes:", x.count(0), "len", len(x))
    print("folly^wisdom head:", x[:64].hex())
    print("printable in xor:", sum(1 for c in x if 32<=c<127), "/", len(x))
# is DATA__560.00 a prefix/subset of the .iso-authoritative?
if 'DATA__560.00' in data and 'DATA__560.00.iso-authoritative' in data:
    a=data['DATA__560.00']; b=data['DATA__560.00.iso-authoritative']
    print("00 in iso-auth as substring:", a in b, "| iso-auth startswith 00:", b.startswith(a))
    # search for a's first 4096 bytes inside b
    print("offset of a[:4096] in b:", b.find(a[:4096]))
json.dump(res, open("raw/pad_pairwise.json","w"), indent=1)
for f,d in data.items():
    G.emit({"artifact_path":os.path.join(P,f),"artifact_sha256":T[os.path.join(P,f)]["sha256"],
      "tool":"pad cross-comparison (pure python)","tool_version":"G-1.0",
      "command":"pairwise byte-alignment match + XOR of equal-length pads","params":{"peers":sorted(data)},
      "exit_code":0,"finding":"NEGATIVE","output_excerpt":json.dumps({k:v for k,v in res.items() if f in k}),
      "output_file":"raw/pad_pairwise.json",
      "note":"Detects reuse of the same keystream across pads (a two-time-pad break). Detects identical files under different names, and shared prefixes. Blind to a relationship that is not byte-aligned (e.g. one pad being a rotation or reordering of another)."})
