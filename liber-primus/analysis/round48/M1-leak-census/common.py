"""Shared loader for Round 48 / M1. Unsolved LP2 = segments 0-54 of data/krisyotam_runes.txt."""
import os
R = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
LAT = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
IDX = {r: i for i, r in enumerate(R)}
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
def stream():
    raw = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf8").read()
    return [IDX[c] for p in raw.split("%")[:55] for c in p if c in IDX]
if __name__ == "__main__":
    s = stream(); assert len(s) == 12956
    open(os.path.join(HERE, "stream.txt"), "w").write("\n".join(map(str, s)) + "\n")
    print("stream.txt", len(s), "doublets", sum(a == b for a, b in zip(s, s[1:])))
