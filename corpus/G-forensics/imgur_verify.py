import hashlib, os, json
import gcore as G
D="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/onions_ibotpeaches"
tbl={"DFQGJAN.jpeg":("04b2dbd746ddce1e93610feac92abce7","January 5th, 2016 Tweet"),
"KXLOP.jpeg":("2414c8fbd2c2041e34eeb5bb4601b220","January 4, 2012 Welcome Reddit"),
"8D7hN.jpeg":("53d0bb15b235aeeff62a2f77a0a40f75","January 7, 2012 Problems? Reddit"),
"hkdgl.png":("df991ade67ee90a3fabf445fa3530ae5","2012 Round 2 Book Hint"),
"m9sYK.jpeg":("9cae1c1fc3427bee81da858814d7e4f6","Decoy duck from 2012 Puzzle"),
"zN4h51m.jpeg":("ea0cab3fa95d51ab6de798d61f1d5490","January 6th, 2014 Tweet"),
"vjuNp.jpeg":("d0c92cc050b9e1ed649d965eb801234d","February 6, 2012 Valete! Ending")}
res=[]
for fn,(md5,desc) in tbl.items():
    p=f"{D}/onions__imgur.com__{fn}"
    if not os.path.exists(p): res.append({"file":fn,"status":"ABSENT","desc":desc}); continue
    d=open(p,'rb').read()
    m=hashlib.md5(d).hexdigest(); s=hashlib.sha256(d).hexdigest()
    ok = m==md5
    res.append({"file":fn,"desc":desc,"claimed_md5":md5,"actual_md5":m,"match":ok,"sha256":s,"size":len(d)})
    G.emit({"artifact_path":p,"artifact_sha256":s,"tool":"manifest hash verification (md5 vs onions__imgur.com__README.md)",
      "tool_version":"G-1.0","command":"md5sum; compare to the hash table published in the iBotPeaches onion mirror README",
      "params":{"artifact_description":desc},"exit_code":0,"finding":"NEGATIVE" if ok else "HIT",
      "output_excerpt":json.dumps({"claimed_md5":md5,"actual_md5":m,"match":ok,"size":len(d)}),
      "output_file":"raw/imgur_manifest_verify.json",
      "note":"Binds our copy of each 2012/2014/2016 primary image to the hash published by the mirror we sourced it from. NEGATIVE = matches (no tampering / no re-encode between mirror and us). This is NOT a Cicada-signed hash: it proves fidelity to the iBotPeaches capture only, not to the original upload."})
for r in res: print(json.dumps(r))
json.dump(res, open("raw/imgur_manifest_verify.json","w"), indent=1)
print("\nall match:", all(r.get("match") for r in res))
