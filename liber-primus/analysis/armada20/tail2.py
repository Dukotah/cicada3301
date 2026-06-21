#!/usr/bin/env python3
import io
from PIL import Image

tail=open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20/page05_tail.bin","rb").read()

# byte-swap (swap adjacent bytes)
sw=bytearray(len(tail))
for i in range(0,len(tail)-1,2):
    sw[i]=tail[i+1]; sw[i+1]=tail[i]
sw=bytes(sw)
print("swapped head:",repr(sw[:40]))
print("swapped tail:",repr(sw[-40:]))
# try open as image
for name,blob in [("swapped",sw),("raw",tail)]:
    try:
        im=Image.open(io.BytesIO(blob))
        im.load()
        print(name,"OPENS as",im.format,im.size,im.mode)
        im.save(f"/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20/extracted_{name}.png")
    except Exception as e:
        print(name,"fail:",str(e)[:80])

# Look at the ASCII text region at start (before binary). Extract leading ascii lines
import re
# the leading region looked like '\n\na0237...' - decimal/space columns
head=tail[:5000]
ascii_run=b""
for c in head:
    if 32<=c<127 or c in (10,13):
        ascii_run+=bytes([c])
    else:
        break
print("\nLeading ASCII run len:",len(ascii_run))
print(repr(ascii_run[:500]))
