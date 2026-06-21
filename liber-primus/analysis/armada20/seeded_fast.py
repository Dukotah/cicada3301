import glob, hashlib, re
import numpy as np
from PIL import Image
KW=re.compile(rb'(BEGIN PGP|PGP MESSAGE|cipher|gematria|primus|divinit|sacred|prime|cicada|instar|circumf|William|Blake|welcome|wisdom|the key|KEY IS)',re.I)
WORDY=re.compile(rb'(the |and |key |cipher|prime|cicada|liber|sacred|divin| is | of )',re.I)
def runs(b,n=8): return re.findall(rb'[ -~]{%d,}'%n,b)
def seeded(flat, seed, nbits=2048*8):
    rng=np.random.default_rng(int.from_bytes(hashlib.sha256(seed).digest()[:8],'little'))
    n=min(nbits,len(flat)); idx=rng.permutation(len(flat))[:n]
    bits=(flat[idx]&1).astype(np.uint8); m=(len(bits)//8)*8
    return np.packbits(bits[:m].reshape(-1,8),axis=1).reshape(-1).tobytes()
seeds=[b'DIVINITY',b'SACRED',b'PRIMES',b'CICADA',b'3301',b'WISDOM',b'INSTAR',b'WELCOME',b'CIRCUMFERENCE',b'A WARNING']
files=sorted(glob.glob("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p*.jpg"))
files+=sorted(glob.glob("/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014/images/liber_primus_pages/*.jpg"))
# also sequential LSB head (no seed)
hits=0
for p in files:
    im=Image.open(p); im.load()
    flat=np.asarray(im.convert('L')).reshape(-1)[:400000].copy()
    # sequential head
    for off in (0,):
        bits=(flat&1).astype(np.uint8); m=(len(bits)//8)*8
        by=np.packbits(bits[:m].reshape(-1,8),axis=1).reshape(-1).tobytes()
        if KW.search(by) or any(WORDY.search(r) for r in runs(by)):
            print("SEQ-HIT",p.split('/')[-1]); hits+=1
    for s in seeds:
        by=seeded(flat,s)
        if KW.search(by) or any(WORDY.search(r) for r in runs(by)):
            print("SEED-HIT",p.split('/')[-1],s,[r[:50] for r in runs(by) if WORDY.search(r) or KW.search(r)][:3]); hits+=1
print("fast seeded/seq hits:",hits,"over",len(files),"files")
