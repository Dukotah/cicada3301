import struct, json, hashlib, os, re
import gcore as G
P="/mnt/c/Users/dukot/projects/cicada3301/puzzles/2013/artifacts/761_The-Instar-Emergence.mp3"
T={t["path"]:t["sha256"] for t in json.load(open("TARGETS.json")) if t["class"]=="audio_2013"}
d=open(P,'rb').read()
out={"size":len(d)}
# --- ID3v2
frames_id3=[]
pos=0
if d[:3]==b'ID3':
    ver=(d[3],d[4]); flags=d[5]
    sz=((d[6]&0x7f)<<21)|((d[7]&0x7f)<<14)|((d[8]&0x7f)<<7)|(d[9]&0x7f)
    out["id3v2"]={"version":f"2.{ver[0]}.{ver[1]}","flags":f"0x{flags:02x}","declared_size":sz,"header":10}
    p=10; end=10+sz
    while p+10<=end:
        fid=d[p:p+4]
        if fid==b'\x00\x00\x00\x00': break
        if ver[0]>=4:
            fs=((d[p+4]&0x7f)<<21)|((d[p+5]&0x7f)<<14)|((d[p+6]&0x7f)<<7)|(d[p+7]&0x7f)
        else:
            fs=struct.unpack('>I', d[p+4:p+8])[0]
        ffl=d[p+8:p+10]
        body=d[p+10:p+10+fs]
        frames_id3.append({"id":fid.decode('latin-1'),"size":fs,"flags":ffl.hex(),
          "sha1":hashlib.sha1(body).hexdigest(),
          "text":body[:400].decode('latin-1','replace'),
          "entropy":round(G.entropy(body),4) if body else 0})
        p+=10+fs
    out["id3v2"]["frames"]=frames_id3
    out["id3v2"]["consumed"]=p-10
    out["id3v2"]["padding_bytes"]=sz-(p-10)
    pad=d[p:end]
    out["id3v2"]["padding_all_zero"]=all(x==0 for x in pad)
    out["id3v2"]["padding_nonzero_sample"]=pad[:64].hex() if not all(x==0 for x in pad) else None
    pos=end
# --- MPEG frame walk
BR={1:[0,32,40,48,56,64,80,96,112,128,160,192,224,256,320,0]}
SR={1:[44100,48000,32000,0]}
i=pos; nfr=0; first=None; gaps=[]; lastend=None
while i < len(d)-4:
    if d[i]==0xFF and (d[i+1]&0xE0)==0xE0:
        h=struct.unpack('>I', d[i:i+4])[0]
        ver=(h>>19)&3; lay=(h>>17)&3; bri=(h>>12)&0xF; sri=(h>>10)&3; pad=(h>>9)&1
        if ver==3 and lay==1 and bri not in (0,15) and sri!=3:
            br=BR[1][bri]*1000; sr=SR[1][sri]
            fl=int(144*br/sr)+pad
            if fl>4:
                if first is None:
                    first={"offset":i,"bitrate":br,"samplerate":sr,"mode":(h>>6)&3,"crc":not((h>>16)&1)}
                if lastend is not None and i!=lastend:
                    gaps.append({"gap_at":lastend,"len":i-lastend,"hex":d[lastend:lastend+32].hex()})
                nfr+=1; lastend=i+fl; i+=fl; continue
    i+=1
out["mpeg"]={"first_frame":first,"frame_count":nfr,"last_frame_end":lastend,
  "inter_frame_gaps":gaps[:20],"n_gaps":len(gaps)}
# --- data after last frame
if lastend:
    tail=d[lastend:]
    out["after_last_frame"]={"len":len(tail),"head_hex":tail[:64].hex(),
      "sha256":hashlib.sha256(tail).hexdigest() if tail else None,
      "is_id3v1":tail[:3]==b'TAG',"entropy":round(G.entropy(tail),4) if tail else 0,
      "ascii":re.findall(rb'[\x20-\x7e]{6,}', tail)[:20].__len__(),
      "text":tail[:300].decode('latin-1','replace')}
    if tail: G.savraw("mp3_after_last_frame.bin", tail)
json.dump(out, open("raw/mp3_deep.json","w"), indent=1)
print(json.dumps({k:v for k,v in out.items() if k!="id3v2"}, indent=1)[:2500])
print("--- ID3 ---")
print(json.dumps(out.get("id3v2",{}), indent=1)[:3000])
