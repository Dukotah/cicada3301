#!/usr/bin/env python3
import io
from PIL import Image

tail=open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20/page05_tail.bin","rb").read()

# Try word-swap starting at each offset 0 and 1 to align
for start in (0,1):
    t=tail[start:]
    sw=bytearray(len(t))
    for i in range(0,len(t)-1,2):
        sw[i]=t[i+1]; sw[i+1]=t[i]
    sw=bytes(sw)
    # find ffd8
    idx=sw.find(b"\xff\xd8\xff")
    print(f"start={start} ffd8ff at {idx}")
    if idx>=0:
        blob=sw[idx:]
        try:
            im=Image.open(io.BytesIO(blob)); im.load()
            print("  OPENS",im.format,im.size,im.mode)
            im.save("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20/tail_recovered.png")
        except Exception as e:
            print("  fail",str(e)[:80])

# Also: maybe the WHOLE FILE is word-swapped and contains 2 images. Compare to main image size
from PIL import Image as I2
m=I2.open("/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014/images/liber_primus_pages/lp_page_05.jpg")
print("main image:",m.format,m.size,m.mode)
