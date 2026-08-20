import json, os, sys, hashlib
import gcore as G
CLS=sys.argv[1]
LIMIT=int(sys.argv[2]) if len(sys.argv)>2 else 10**9
SKIP=int(sys.argv[3]) if len(sys.argv)>3 else 0
T=[t for t in json.load(open("TARGETS.json")) if t["class"]==CLS][SKIP:SKIP+LIMIT]
TERM={'JPEG':b'\xff\xd9','PNG':b'IEND\xaeB`\x82','GIF':b'\x00\x3b'}
summ=[]
for t in T:
    p=t["path"]; rel=os.path.relpath(p,"/mnt/c/Users/dukot/projects/cicada3301")
    base=rel.replace("/","__")
    typ=G.sniff(p)
    G.emit({"artifact_path":p,"artifact_sha256":t["sha256"],"tool":"magic sniff (pure python)",
      "tool_version":"G-1.0","command":"read first 4096B, match signature table","params":{"size":t["size"]},
      "exit_code":0,"finding":"HIT" if typ not in ("DATA/unknown",) else "NEGATIVE",
      "output_excerpt":json.dumps({"type":typ,"size":t["size"]}),"output_file":None,
      "note":"Identifies container format from magic bytes. Would detect a mislabelled/renamed container. Cannot detect a format with no magic."})
    # appended data for known containers
    if typ in ('JPEG','PNG','GIF'):
        d=open(p,'rb').read()
        term=TERM[typ]; idx=d.rfind(term)
        trail=len(d)-(idx+len(term)) if idx>=0 else None
        G.emit({"artifact_path":p,"artifact_sha256":t["sha256"],"tool":"appended-data check (pure python)",
          "tool_version":"G-1.0","command":f"rfind terminal marker {term.hex()}; count bytes after","params":{"type":typ},
          "exit_code":0,"finding":"HIT" if trail else ("ERROR" if trail is None else "NEGATIVE"),
          "output_excerpt":json.dumps({"terminal_offset":idx,"trailing_bytes":trail,
             "trailing_head_hex":d[idx+len(term):idx+len(term)+64].hex() if trail else None,
             "trailing_sha256":hashlib.sha256(d[idx+len(term):]).hexdigest() if trail else None}),
          "output_file":None,
          "note":"Byte-exact. Detects any data appended past the container's terminal marker, incl. 1 byte."})
    # entropy profile
    mean,prof,anom=G.entropy_profile(p)
    G.emit({"artifact_path":p,"artifact_sha256":t["sha256"],"tool":"entropy profile (pure python, 64KiB window)",
      "tool_version":"G-1.0","command":"Shannon entropy per 64KiB block; flag |e-mean|>3sigma","params":{"window":65536},
      "exit_code":0,"finding":"HIT" if anom else "NEGATIVE",
      "output_excerpt":json.dumps({"mean_entropy":mean,"blocks":len(prof),"anomalies":anom[:20],
        "min":min([e for _,e in prof] or [0]),"max":max([e for _,e in prof] or [0])}),
      "output_file":f"raw/entropy/{base}.json" if len(prof)>1 else None,
      "note":"Localised entropy anomaly = carve candidate. Detects an embedded compressed/encrypted region inside low-entropy data, or a plaintext region inside high-entropy data. Blind to a payload whose entropy matches its surroundings."})
    if len(prof)>1:
        G.savraw(f"entropy/{base}.json", json.dumps({"mean":mean,"profile":prof,"anomalies":anom}))
    # strings
    a,le,be,trunc=G.strings_all(p)
    interesting=[s for s in a if any(k in s.lower() for k in
       ('cicada','3301','instar','divinity','circumference','pilgrim','totient','mobius','adhere','welcome','shadow','onion','pgp','gpg','begin ','key','primus','liber','wisdom','folly','prime'))]
    G.emit({"artifact_path":p,"artifact_sha256":t["sha256"],"tool":"strings (pure python, ASCII+UTF-16LE+UTF-16BE, minlen 6)",
      "tool_version":"G-1.0","command":"regex [\x20-\x7e]{6,} plus UTF-16 LE/BE variants","params":{"minlen":6,"truncated_at_4MB":trunc},
      "exit_code":0,"finding":"HIT" if interesting else ("NEGATIVE" if not a else "NEGATIVE"),
      "output_excerpt":json.dumps({"n_ascii":len(a),"n_utf16le":len(le),"n_utf16be":len(be),
        "keyword_hits":interesting[:40],"longest":sorted(a,key=len,reverse=True)[:5]}),
      "output_file":f"raw/strings/{base}.txt",
      "note":"Both endiannesses covered. Would detect plaintext or UTF-16 text anywhere in the file. Blind to encrypted/compressed text and to non-Latin encodings."})
    G.savraw(f"strings/{base}.txt","\n".join(["==ASCII=="]+a+["==UTF16LE=="]+le+["==UTF16BE=="]+be))
    summ.append({"path":rel,"type":typ,"size":t["size"],"mean_entropy":mean,"n_anom":len(anom),
                 "n_strings":len(a),"kw":len(interesting)})
json.dump(summ, open(f"raw/summary_{CLS}_{SKIP}.json","w"), indent=1)
print(f"{CLS}: {len(T)} artifacts processed (skip={SKIP})")
for s in summ[:60]: print(f"  {s['type']:14s} ent={s['mean_entropy']:6.3f} anom={s['n_anom']:2d} str={s['n_strings']:6d} kw={s['kw']:3d}  {s['path']}")
