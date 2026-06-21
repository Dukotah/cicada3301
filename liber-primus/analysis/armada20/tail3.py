#!/usr/bin/env python3
import binascii, hashlib

tail=open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20/page05_tail.bin","rb").read()

# The leading ascii is hex chars. Strip the leading \n\n
h=tail.lstrip(b"\n")
# take only hex chars [0-9a-fA-F]
hexchars=bytearray()
for c in h:
    if c in b"0123456789abcdefABCDEF":
        hexchars.append(c)
    else:
        break
print("hexchar run len:",len(hexchars))
hs=bytes(hexchars)
if len(hs)%2: hs=hs[:-1]
try:
    decoded=binascii.unhexlify(hs)
    print("decoded len:",len(decoded))
    print("decoded repr:",repr(decoded[:200]))
except Exception as e:
    print("unhex fail",e)

# Even/odd byte deinterleave of whole tail
even=tail[0::2]
odd=tail[1::2]
print("\neven head:",repr(even[:30]))
print("odd head:",repr(odd[:30]))
print("even tail:",repr(even[-20:]))
print("odd tail:",repr(odd[-20:]))

# whole file analysis: is the page05 file == 0_wisdom?
import os
a=open("/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014/images/liber_primus_pages/lp_page_05.jpg","rb").read()
b=open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/0_wisdom.jpg","rb").read()
print("\nlp_page_05 sha:",hashlib.sha256(a).hexdigest()[:16])
print("0_wisdom   sha:",hashlib.sha256(b).hexdigest()[:16])
print("identical:",a==b)
