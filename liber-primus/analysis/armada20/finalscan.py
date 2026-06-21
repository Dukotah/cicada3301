#!/usr/bin/env python3
import os, glob, re

ROOTS=["/mnt/c/Users/dukot/projects/cicada3301/puzzles/2012",
       "/mnt/c/Users/dukot/projects/cicada3301/puzzles/2013",
       "/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014",
       "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd"]

def jpeg_eoi_end(d):
    if d[:2]!=b"\xff\xd8": return None
    i=2;n=len(d)
    while i<n-1:
        if d[i]!=0xff: i+=1;continue
        m=d[i+1]
        if m==0xff: i+=1;continue
        if m==0xd9: return i+2
        if 0xd0<=m<=0xd7 or m==0x01: i+=2;continue
        if m==0xda:
            seglen=(d[i+2]<<8)|d[i+3]; i+=2+seglen
            while i<n-1:
                if d[i]==0xff:
                    nb=d[i+1]
                    if nb==0x00 or 0xd0<=nb<=0xd7: i+=2;continue
                    break
                i+=1
            continue
        seglen=(d[i+2]<<8)|d[i+3]; i+=2+seglen
    return None

def png_end(d):
    idx=d.rfind(b"IEND\xae\x42\x60\x82")
    return idx+8 if idx>=0 else None

results=[]
for root in ROOTS:
    for p in sorted(glob.glob(os.path.join(root,"**","*"),recursive=True)):
        if not os.path.isfile(p):continue
        ext=p.lower().rsplit(".",1)[-1]
        if ext not in ("jpg","jpeg","png"):continue
        d=open(p,"rb").read()
        end=jpeg_eoi_end(d) if ext in("jpg","jpeg") else png_end(d)
        if end is None:continue
        tail=d[end:]
        if len(tail)<2:continue
        printable=sum(1 for c in tail if 32<=c<127 or c in(9,10,13))/len(tail)
        # high-printability tails = candidate text payloads
        strs=re.findall(rb"[\x20-\x7e]{6,}",tail)
        results.append((p,len(tail),round(printable,2),strs[:8]))

# Sort: high printable ratio first (most likely real text)
results.sort(key=lambda x:-x[2])
print("=== POST-EOI/IEND TAILS (structural parse) ===")
for p,ln,pr,strs in results:
    flag="<<<HIGH-TEXT" if pr>0.6 else ""
    print(f"{pr:.2f} len={ln:>7} {flag} {p}")
    if pr>0.6:
        for s in strs:
            print("     ",s.decode('latin1'))
