import re, zlib, bz2, lzma, itertools
p="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/0_wisdom.jpg"
d=open(p,'rb').read()
app=d[336353:]

def runs(b,n=6): return re.findall(rb'[ -~]{%d,}'%n,b)

# 1. decompress attempts at various offsets
for name,fn in [('zlib',zlib.decompress),('bz2',bz2.decompress),('lzma',lzma.decompress)]:
    for off in range(0,64):
        try:
            out=fn(app[off:])
            print(f"DECOMP {name} off{off} -> {len(out)} bytes:", out[:80]); break
        except Exception: pass

# 2. XOR whole blob with keyword-derived keystreams, look for English
keys=[b'DIVINITY',b'SACRED',b'PRIMES',b'PRIME',b'CICADA',b'3301',b'WISDOM',b'CIRCUMFERENCE',b'INSTAR',b'WELCOME']
def english_score(b):
    # crude: fraction of common english bytes
    common=sum(1 for c in b if c in b' etaoinshrdlucETAOINSHRDLU')
    letters=sum(1 for c in b if 65<=c<=90 or 97<=c<=122 or c==32)
    return letters/max(1,len(b))
best=None
for k in keys:
    x=bytes(app[i]^k[i%len(k)] for i in range(min(len(app),4096)))
    rr=[r for r in runs(x,8)]
    sc=english_score(x)
    wordy=[r for r in rr if re.search(rb'(the|and|key|THE|AND|KEY|cipher|prime)',r)]
    if wordy: print("XOR",k,"WORDS:",wordy[:5])
    if best is None or sc>best[0]: best=(sc,k)
print("best XOR english frac:", round(best[0],3), best[1])

# 3. The 360-byte head: decode nibbles. chars are mostly 0,1,2,3 -> maybe base-4 / 2-bit
head=app[:360].replace(b'\n',b'').replace(b'a',b'')
print("head digits:", head[:60])
# treat each digit pair? or map digit->2bits and pack
digs=[c-48 for c in head if 48<=c<=57]
print("digit values sample:", digs[:40], "max", max(digs))
# pack 2-bit (base4) -> bytes
bits=''.join(format(min(dd,3),'02b') for dd in digs)
nb=bytes(int(bits[i:i+8],2) for i in range(0,len(bits)-7,8))
print("base4-packed:", repr(nb[:60]))
