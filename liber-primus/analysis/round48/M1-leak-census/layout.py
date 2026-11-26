"""Write layout.txt for Arm B2: page-start positions and a word-start flag per rune."""
import os
from common import IDX, LP, HERE
raw = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf8").read()
starts, flags, sep = [], [], True
for seg in raw.split("%")[:55]:
    starts.append(len(flags))
    for c in seg:
        if c in IDX: flags.append(1 if sep else 0); sep = False
        elif c in "-.&$§0123456789": sep = True          # '/' and newline do not break words
assert len(flags) == 12956
open(os.path.join(HERE, "layout.txt"), "w").write(" ".join(map(str, starts)) + "\n" + "\n".join(map(str, flags)) + "\n")
print("pages", len(starts), "word starts", sum(flags))
