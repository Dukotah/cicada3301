import numpy as np, json, zlib, hashlib, re, math
from PIL import Image
import gcore as G
P="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/onions_ibotpeaches/onions__imgur.com__hkdgl.png"
d=open(P,'rb').read()
print("sha256",hashlib.sha256(d).hexdigest(),"size",len(d))
# PNG chunk walk
i=8; chunks=[]
while i<len(d):
    ln=int.from_bytes(d[i:i+4],'big'); typ=d[i+4:i+8].decode('latin-1')
    chunks.append({"type":typ,"len":ln,"off":i,"sha1":hashlib.sha1(d[i+8:i+8+ln]).hexdigest()[:16]})
    if typ in ('tEXt','iTXt','zTXt','tIME','pHYs','gAMA','sRGB','bKGD'):
        chunks[-1]["data"]=d[i+8:i+8+ln][:200].decode('latin-1','replace')
    i+=12+ln
    if typ=='IEND': break
print("chunks:",json.dumps(chunks,indent=1))
print("bytes after IEND:", len(d)-i)
im=Image.open(P); a=np.array(im); print("mode",im.mode,"shape",a.shape)
if a.ndim==2: a=a[:,:,None]
# how many distinct colours? photographic vs synthetic
flat=a.reshape(-1,a.shape[2])
uniq=len(np.unique(flat,axis=0))
print("distinct pixel values:",uniq,"of",flat.shape[0],"pixels")
# per-channel value histogram spread
for ch in range(a.shape[2]):
    v=a[:,:,ch]
    print(f" ch{ch}: min={v.min()} max={v.max()} mean={v.mean():.2f} std={v.std():.2f} nuniq={len(np.unique(v))}")
# is bit0 random because image is photographic? compare bit0 entropy vs bit1..3
for ch in range(min(3,a.shape[2])):
    es=[]
    for b in range(8):
        bp=((a[:,:,ch]>>b)&1); p=bp.mean()
        es.append(round(0.0 if p in (0,1) else -(p*math.log2(p)+(1-p)*math.log2(1-p)),5))
    print(f" ch{ch} bitplane entropies bit0..7:",es)
# extract LSB payload attempts
for order,arr in (("row",a),("col",np.transpose(a,(1,0,2)))):
    for mode,sel in (("rgb_interleaved",None),):
        bits=(arr[:,:,:3]&1).reshape(-1)
        by=np.packbits(bits).tobytes()
        G.savraw(f"lsb_extract/hkdgl_{order}_{mode}.bin", by)
        head=by[:64]
        print(f" {order}/{mode}: len={len(by)} head={head[:24].hex()} printable={sum(1 for x in by[:4096] if 32<=x<127)/4096:.3f}")
        # try zlib/gzip
        for nm,fn in (("zlib",lambda x: zlib.decompress(x)),("raw-deflate",lambda x: zlib.decompress(x,-15))):
            try:
                out=fn(by); print(f"   {nm} DECOMPRESSED {len(out)} bytes: {out[:120]!r}")
            except Exception as e: pass
        runs=re.findall(rb'[\x20-\x7e]{8,}', by)
        print("   ascii runs>=8:",len(runs), runs[:5])
