from PIL import Image
import io
p="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/0_wisdom.jpg"
d=open(p,'rb').read()
# PIL opens which image? size
im=Image.open(p); print("PIL sees:", im.size, im.mode, im.format)
# Find ALL jpeg SOI..EOI candidate segments
import re
sois=[m.start() for m in re.finditer(b'\xff\xd8\xff', d)]
print("SOI(ffd8ff) positions:", sois)
# Try to open from the JPEG sig near end (offset 336710 within app -> file offset 336353+336710)
off=336353+336710
print("late jpeg sig at file offset", off, "remaining", len(d)-off)
try:
    im2=Image.open(io.BytesIO(d[off:])); im2.load(); print("late jpeg:", im2.size, im2.mode)
except Exception as e: print("late jpeg fail:", e)
# Compare relikd 0_wisdom vs other relikd pages: are p0..p55 ALSO double-size like this?
import glob, os
for f in sorted(glob.glob("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p*.jpg"))[:6]:
    dd=open(f,'rb').read()
    # find real EOI via marker walk quick: just check trailing after structurally — use PIL size vs filesize ratio
    print(os.path.basename(f), "filesize", len(dd), "ffd8count", dd.count(b'\xff\xd8'), "ffd9count", dd.count(b'\xff\xd9'))
