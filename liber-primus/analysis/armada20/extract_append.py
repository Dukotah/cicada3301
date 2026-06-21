import collections, math, hashlib, re
p="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/0_wisdom.jpg"
d=open(p,'rb').read()
EOI=336351  # from marker parse, real EOI position
app=d[EOI+2:]
print("appended len", len(app))
c=collections.Counter(app); ent=-sum((n/len(app))*math.log2(n/len(app)) for n in c.values())
print("entropy", round(ent,4), "bits/byte")
print("first 64 hex:", app[:64].hex())
print("first 64 repr:", repr(app[:64]))
# any known headers anywhere?
for sig,name in [(b'\x89PNG','PNG'),(b'\xff\xd8\xff','JPEG'),(b'PK\x03\x04','ZIP'),(b'BZh','BZIP2'),(b'\x1f\x8b','GZIP'),(b'7z\xbc','7Z'),(b'Rar!','RAR'),(b'-----BEGIN','PGP/PEM'),(b'\x37\x7a','x'),(b'GIF8','GIF'),(b'%PDF','PDF'),(b'OggS','OGG'),(b'ID3','MP3')]:
    idx=app.find(sig)
    if idx!=-1: print(f"  found {name} sig at offset {idx}")
# is it just the same image repeated? compare to start of file
print("appended==start of file?", app[:1000]==d[:1000])
# Check histogram uniformity - chi2 vs uniform
import numpy as np
a=np.frombuffer(app,dtype=np.uint8)
hist=np.bincount(a,minlength=256)
exp=len(app)/256
chi2=((hist-exp)**2/exp).sum()
print("chi2 vs uniform (df=255):", round(chi2,1), " (random~255, low=uniform)")
# zlib try
import zlib
for off in [0,1,2]:
    try:
        z=zlib.decompress(app[off:]); print("zlib ok at",off,len(z)); break
    except: pass
# Print first printable runs
runs=re.findall(rb'[ -~]{6,}', app)
print("num ascii runs>=6:", len(runs))
for r in runs[:20]: print("   ", r[:60])
