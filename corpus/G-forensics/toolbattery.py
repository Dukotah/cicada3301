import json, os, sys, subprocess, hashlib
import gcore as G
R="/mnt/c/Users/dukot/projects/cicada3301/"
KEYS=["", "3301","cicada","CICADA","DIVINITY","CIRCUMFERENCE","FIRFUMFERENFE","INSTAR","MOBIUS",
      "ADHERE","WELCOME","PILGRIM","TOTIENT","SHADOWS","AN END","845145127","7A35090F","1033","761"]
def ver(cmd):
    for args in ([cmd,'-ver'],[cmd,'--version'],[cmd,'-version']):
        rc,o,e=G.run(args,30)
        if rc==0 and (o.strip() or e.strip()): return (o or e).strip().splitlines()[0][:80]
    return "unknown"
VERS={t:ver(t) for t in ("exiftool","binwalk","steghide","outguess")}
def battery(t):
    p=t["path"]; s=t["sha256"]; rel=p.replace(R,""); base=rel.replace("/","__")
    ext=os.path.splitext(p)[1].lower()
    # ---- file
    rc,o,e=G.run(["file","-b",p],60)
    G.emit({"artifact_path":p,"artifact_sha256":s,"tool":"file","tool_version":ver("file"),
      "command":f"file -b {rel}","params":{},"exit_code":rc,
      "finding":"NEGATIVE" if rc==0 else "ERROR","output_excerpt":o.strip()[:400],"output_file":None,
      "note":"libmagic container identification. Detects a renamed/mislabelled format. Cannot see inside a correctly-formed container."})
    # ---- exiftool (all tags incl. maker notes, unknown, binary flagged)
    rc,o,e=G.run(["exiftool","-a","-u","-g1","-U","-ee","-api","RequestAll=3","-s",p],240)
    tags=[l for l in o.splitlines() if l.strip()]
    interesting=[l for l in tags if any(k in l for k in ("Comment","MakerNote","XMP","UserComment","Software","Artist","Copyright","Creator","Author","Title","Description","Keywords","Warning","Trailer","Unknown","Padding","ImageUniqueID","DocumentName"))]
    G.emit({"artifact_path":p,"artifact_sha256":s,"tool":"exiftool","tool_version":VERS["exiftool"],
      "command":f"exiftool -a -u -g1 -U -ee -api RequestAll=3 -s {rel}","params":{"all_tags":True,"unknown":True,"duplicates":True,"embedded":True},
      "exit_code":rc,"finding":"HIT" if interesting else ("NEGATIVE" if rc==0 else "ERROR"),
      "output_excerpt":json.dumps({"n_tags":len(tags),"notable":interesting[:30]}),
      "output_file":f"raw/exiftool/{base}.txt",
      "note":"-a duplicates, -u unknown tags, -U unknown binary tags, -ee embedded/nested docs, RequestAll=3 forces every derivable tag incl. maker notes. This is the widest exiftool view available. Would detect any EXIF/IPTC/XMP/maker-note/comment field. Blind to data that is not in a tag structure exiftool models."})
    G.savraw(f"exiftool/{base}.txt", o+("\nSTDERR:\n"+e if e else ""))
    # ---- binwalk signature scan
    rc,o,e=G.run(["binwalk","--signature","--term",p],300)
    lines=[l for l in o.splitlines() if l and l[0].isdigit()]
    G.emit({"artifact_path":p,"artifact_sha256":s,"tool":"binwalk","tool_version":VERS["binwalk"],
      "command":f"binwalk --signature {rel}","params":{},"exit_code":rc,
      "finding":"HIT" if len(lines)>1 else ("NEGATIVE" if rc==0 else "ERROR"),
      "output_excerpt":json.dumps({"n_signature_matches":len(lines),"matches":lines[:25]}),
      "output_file":f"raw/binwalk/{base}.txt",
      "note":"Signature scan for embedded container headers at any offset. NOTE ON POWER: inside compressed/encrypted regions (JPEG DCT, high-entropy pads) random bytes reproduce short magic sequences by chance, so matches here require header validation before they mean anything; a bare match count >1 is flagged HIT for human review, not asserted as a finding."})
    G.savraw(f"binwalk/{base}.txt", o+("\nSTDERR:\n"+e if e else ""))
    # ---- steghide (JPEG/BMP/WAV/AU only)
    if ext in ('.jpg','.jpeg','.bmp','.wav','.au'):
        hits=[]; errs=0
        for k in KEYS:
            out=f"/tmp/sh_{base}_{abs(hash(k))}.bin"
            rc2,o2,e2=G.run(["steghide","extract","-sf",p,"-p",k,"-xf",out,"-f"],90)
            if rc2==0 and os.path.exists(out) and os.path.getsize(out)>0:
                d=open(out,'rb').read()
                hits.append({"key":k or "(empty)","size":len(d),"sha256":hashlib.sha256(d).hexdigest(),
                             "head":d[:64].hex()})
                G.savraw(f"steghide_hits/{base}_k{k or 'EMPTY'}.bin", d)
            if os.path.exists(out): os.remove(out)
        G.emit({"artifact_path":p,"artifact_sha256":s,"tool":"steghide","tool_version":VERS["steghide"],
          "command":f"steghide extract -sf {rel} -p <key> -xf - ; for each of {len(KEYS)} candidate keys",
          "params":{"keys":[k or "(empty)" for k in KEYS]},"exit_code":0,
          "finding":"HIT" if hits else "NEGATIVE","output_excerpt":json.dumps({"keys_tried":len(KEYS),"hits":hits}),
          "output_file":"raw/steghide_hits/" if hits else None,
          "note":"steghide verifies a checksum before emitting, so a success is a true positive, and a failure across all keys is a real negative FOR THESE KEYS ONLY. Blind to any passphrase not in the candidate list, and to every stego tool other than steghide."})
    else:
        G.emit({"artifact_path":p,"artifact_sha256":s,"tool":"steghide","tool_version":VERS["steghide"],
          "command":"n/a","params":{},"exit_code":0,"finding":"NOT_APPLICABLE",
          "output_excerpt":json.dumps({"reason":f"steghide supports JPEG/BMP/WAV/AU only; this artifact is {ext or 'extensionless'}"}),
          "output_file":None,
          "note":"NOT_APPLICABLE, not NEGATIVE: steghide was never able to examine this artifact, so it contributes no evidence either way."})
if __name__=="__main__":
    T=json.load(open("TARGETS.json"))
    cls=sys.argv[1]; lim=int(sys.argv[2]); skip=int(sys.argv[3])
    sel=[t for t in T if t["class"]==cls][skip:skip+lim]
    print("versions:",json.dumps(VERS))
    for i,t in enumerate(sel):
        battery(t); print(f"[{skip+i}] {t['path'].replace(R,'')}", flush=True)
