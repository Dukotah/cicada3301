p="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/0_wisdom.jpg"
d=open(p,'rb').read()
app=d[336353:]
# The head is ASCII digit-ish. How long does that region last?
import re
# region of bytes in '0'-'9' plus space plus a/newline
i=0
while i<len(app) and (48<=app[i]<=57 or app[i] in (32,10,97,98,99,100,101,102)):
    i+=1
print("digit-ish head length:", i, "of", len(app))
head=app[:i]
print("head sample (repr):", repr(head[:120]))
# count char distribution in head
from collections import Counter
print("head char dist:", {chr(k):v for k,v in sorted(Counter(head).items())})
# It looks like rows separated by 'a'(0x61) maybe? split on 'a'
parts=head.split(b'a')
print("num parts split on 'a':", len(parts), "len of first few:", [len(x) for x in parts[:10]])
# Each part: numbers separated by spaces?
print("part1 repr:", repr(parts[1][:80]))
# autocorrelation of head to find period
import numpy as np
arr=np.frombuffer(head,dtype=np.uint8).astype(float)
arr-=arr.mean()
ac=np.correlate(arr,arr,'full')[len(arr)-1:]
ac/=ac[0]
peaks=[(lag,round(ac[lag],3)) for lag in range(1,80) if ac[lag]>0.3]
print("autocorr peaks (lag,val) >0.3:", peaks[:20])
