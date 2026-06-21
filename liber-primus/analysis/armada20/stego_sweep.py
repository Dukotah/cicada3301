#!/usr/bin/env python3
import os, sys, glob, struct, math, hashlib, re
from collections import Counter
import numpy as np
from PIL import Image

OUT = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20"

def gather():
    files = []
    files += glob.glob("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/*.jpg")
    for ext in ("jpg","jpeg","png"):
        files += glob.glob(f"/mnt/c/Users/dukot/projects/cicada3301/puzzles/**/*.{ext}", recursive=True)
    return sorted(set(files))

PRINTABLE = set(range(32,127)) | {9,10,13}
def ascii_runs(b, minlen=8):
    out=[]; cur=bytearray()
    for ch in b:
        if ch in PRINTABLE:
            cur.append(ch)
        else:
            if len(cur)>=minlen: out.append(cur.decode('latin1'))
            cur=bytearray()
    if len(cur)>=minlen: out.append(cur.decode('latin1'))
    return out

# Heuristic: is a run "interesting" (not just repeated chars / jpeg fluff)
JPEG_FLUFF = re.compile(r'(Adobe|JFIF|Photoshop|Exif|ICC_PROFILE|http://ns.adobe|xmlns|XMP|Ducky|MicrosoftWord|<?xpacket|GIMP|Compressed)', re.I)
def interesting(s):
    if JPEG_FLUFF.search(s): return False
    uniq=len(set(s))
    if uniq<4: return False
    # entropy-ish: must contain letters
    if not re.search(r'[A-Za-z]{4}', s): return False
    return True

KEYWORDS = re.compile(r'(BEGIN PGP|PGP MESSAGE|PUBLIC KEY|cipher|gematria|primus|divinit|sacred|prime|onion|3301|cicada|instar|circumf|key is|magic square|William|Blake|welcome|wisdom)', re.I)

def scan_bytes(path):
    with open(path,'rb') as f: data=f.read()
    res={}
    # trailing after last EOI (FFD9) for jpeg
    if data[:2]==b'\xff\xd8':
        idx=data.rfind(b'\xff\xd9')
        if idx!=-1 and idx+2 < len(data):
            trail=data[idx+2:]
            res['trailing_len']=len(trail)
            runs=[r for r in ascii_runs(trail,6) if interesting(r)]
            if runs: res['trailing_ascii']=runs[:20]
    # full-file ascii hits matching keywords
    runs=ascii_runs(data,6)
    kw=[r for r in runs if KEYWORDS.search(r)]
    if kw: res['keyword_hits']=kw[:30]
    return res

def lsb_extract(arr, bit=0, channels=None, order='C'):
    """Extract LSB plane bits, pack to bytes."""
    if channels is not None:
        arr=arr[...,channels]
    flat=arr.reshape(-1) if order=='C' else arr.reshape(-1,order='F')
    bits=((flat>>bit)&1).astype(np.uint8)
    n=(len(bits)//8)*8
    bits=bits[:n].reshape(-1,8)
    # MSB-first
    by=np.packbits(bits,axis=1).reshape(-1).tobytes()
    return by

def analyze_lsb(path):
    try:
        im=Image.open(path)
        im.load()
    except Exception as e:
        return {'err':str(e)}
    res={}
    modes=[im]
    if im.mode!='L':
        modes.append(im.convert('L'))
    seen=set()
    for m in modes:
        arr=np.asarray(m)
        if arr.ndim==2: arr=arr[...,None]
        nch=arr.shape[2]
        configs=[]
        # all channels interleaved
        configs.append(('all',None))
        for c in range(nch):
            configs.append((f'ch{c}',c))
        for name,ch in configs:
            for order in ('C','F'):
                by=lsb_extract(arr,0,ch,order)
                h=hashlib.md5(by[:4096]).hexdigest()
                if h in seen: continue
                seen.add(h)
                runs=[r for r in ascii_runs(by,8) if interesting(r)]
                kw=[r for r in ascii_runs(by,5) if KEYWORDS.search(r)]
                if runs or kw:
                    key=f"{m.mode}.{name}.{order}"
                    rec={}
                    if runs: rec['runs']=runs[:15]
                    if kw: rec['kw']=kw[:15]
                    res[key]=rec
    return res

def main():
    files=gather()
    print(f"# {len(files)} files")
    byte_hits={}; lsb_hits={}
    for p in files:
        b=scan_bytes(p)
        if b and (b.get('trailing_ascii') or b.get('keyword_hits') or (b.get('trailing_len',0)>32)):
            byte_hits[p]=b
        l=analyze_lsb(p)
        if l and not l.get('err') and l:
            # filter empties
            l={k:v for k,v in l.items() if v}
            if l: lsb_hits[p]=l
    print("="*40,"BYTE/TRAILING HITS")
    for p,b in byte_hits.items():
        print(p, b)
    print("="*40,"LSB HITS")
    for p,l in lsb_hits.items():
        print(p)
        for k,v in l.items(): print("   ",k,v)
    print("DONE byte_hits=%d lsb_hits=%d"%(len(byte_hits),len(lsb_hits)))

if __name__=='__main__':
    main()
