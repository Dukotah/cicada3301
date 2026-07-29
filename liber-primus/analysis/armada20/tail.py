#!/usr/bin/env python3
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "..", ".."))

p=_REPO + "/puzzles/2014/images/liber_primus_pages/lp_page_05.jpg"
d=open(p,"rb").read()
tail=d[336353:]
print("tail len",len(tail))
print("first 300 chars repr:")
print(repr(tail[:300]))
print("\nlast 200 chars repr:")
print(repr(tail[-200:]))
# save
open(_REPO + "/liber-primus/analysis/armada20/page05_tail.bin","wb").write(tail)
# char histogram
from collections import Counter
c=Counter(tail)
print("\ndistinct bytes:",len(c))
print("top:",c.most_common(20))
