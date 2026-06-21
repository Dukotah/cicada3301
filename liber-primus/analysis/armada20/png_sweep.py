import glob, re
import numpy as np
from PIL import Image
KW=re.compile(rb'(BEGIN PGP|PGP|cipher|gematria|primus|divinit|sacred|prime|onion|3301|cicada|instar|circumf|magic|William|Blake|welcome|wisdom|key)',re.I)
WORDY=re.compile(rb'(the |and |key |cipher|prime|cicada|liber| is | of )',re.I)
def runs(b,n=8): return re.findall(rb'[ -~]{%d,}'%n,b)
pngs=glob.glob("/mnt/c/Users/dukot/projects/cicada3301/puzzles/**/*.png",recursive=True)
print(f"# {len(pngs)} PNGs")
for p in pngs:
    # appended after IEND
    d=open(p,'rb').read()
    iend=d.rfind(b'IEND')
    if iend!=-1 and iend+8<len(d):
        trail=d[iend+8:]
        rr=[r for r in runs(trail,6)]
        if rr: print("PNG-TRAIL",p.split('/')[-1],len(trail),[r[:50] for r in rr[:5]])
    # tEXt/zTXt chunks
    for kw,off in [(b'tEXt',0),(b'iTXt',0),(b'zTXt',0)]:
        idx=d.find(kw)
        if idx!=-1:
            print("PNG-CHUNK",p.split('/')[-1],kw.decode(),repr(d[idx:idx+80]))
    # LSB planes
    try:
        im=Image.open(p); im.load(); arr=np.asarray(im)
    except Exception as e:
        print("skip",p,e); continue
    if arr.ndim==2: arr=arr[...,None]
    for c in range(arr.shape[2]):
        for order in ('C','F'):
            flat=arr[...,c].reshape(-1) if order=='C' else arr[...,c].reshape(-1,order='F')
            bits=(flat&1).astype(np.uint8); m=(len(bits)//8)*8
            by=np.packbits(bits[:m].reshape(-1,8),axis=1).reshape(-1).tobytes()
            for stream in (by, bytes((~x)&0xFF for x in by[:8192])):
                if KW.search(stream) or any(WORDY.search(r) for r in runs(stream,8)):
                    print("PNG-LSB",p.split('/')[-1],f"ch{c}",order,[r[:50] for r in runs(stream,8) if WORDY.search(r) or KW.search(r)][:5])
print("PNG done")
