#!/usr/bin/env python3
p="/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014/images/liber_primus_pages/lp_page_05.jpg"
d=open(p,"rb").read()
tail=d[336353:]
print("tail len",len(tail))
print("first 300 chars repr:")
print(repr(tail[:300]))
print("\nlast 200 chars repr:")
print(repr(tail[-200:]))
# save
open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20/page05_tail.bin","wb").write(tail)
# char histogram
from collections import Counter
c=Counter(tail)
print("\ndistinct bytes:",len(c))
print("top:",c.most_common(20))
