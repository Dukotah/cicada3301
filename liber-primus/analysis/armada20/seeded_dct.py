import glob, hashlib, re, sys
import numpy as np
from PIL import Image

KW=re.compile(rb'(BEGIN PGP|PGP MESSAGE|cipher|gematria|primus|divinit|sacred|prime|onion|3301|cicada|instar|circumf|magic|William|Blake|welcome|wisdom|the key|KEY IS)',re.I)
def runs(b,n=8): return re.findall(rb'[ -~]{%d,}'%n,b)
WORDY=re.compile(rb'(the|and|key|cipher|prime|cicada|liber|sacred|divin)',re.I)

def seeded_lsb(arr, seed, nbits=4096*8):
    flat=arr.reshape(-1)
    rng=np.random.default_rng(int.from_bytes(hashlib.sha256(seed).digest()[:8],'little'))
    n=min(nbits, len(flat))
    idx=rng.permutation(len(flat))[:n]
    bits=(flat[idx]&1).astype(np.uint8)
    m=(len(bits)//8)*8
    return np.packbits(bits[:m].reshape(-1,8),axis=1).reshape(-1).tobytes()

seeds=[b'DIVINITY',b'SACRED',b'PRIMES',b'PRIME',b'CICADA',b'3301',b'WISDOM',b'CIRCUMFERENCE',
       b'INSTAR',b'WELCOME',b'A WARNING',b'PARABLE',b'THE LOSS OF DIVINITY',b'an end',
       b'the primes are sacred', b'AN INSTRUCTION']

files=sorted(glob.glob("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p*.jpg"))
files+=sorted(glob.glob("/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014/images/liber_primus_pages/*.jpg"))
print(f"# {len(files)} clean page files, {len(seeds)} seeds")
hits=0
for p in files:
    im=Image.open(p); im.load()
    arr=np.asarray(im.convert('L'))
    for s in seeds:
        by=seeded_lsb(arr,s)
        if KW.search(by) or any(WORDY.search(r) for r in runs(by,8)):
            print("HIT",p,s,[r[:60] for r in runs(by,8) if WORDY.search(r)][:5], KW.findall(by)[:5])
            hits+=1
print("seeded LSB hits:",hits)
