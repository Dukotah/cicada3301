"""English-likeness scoring via quadgram log-probabilities.

Used to (a) rank candidate decryptions and (b) drive the interrupter search.
Model built from a public-domain corpus weighted toward archaic English (KJV),
which matches the Liber Primus plaintext register far better than modern prose.

The scorer also doubles as an honest BS-detector: high quadgram fitness on real
English is ~ -2.2 per quadgram; random text scores far lower (~ -4.5). An LLM or
a human staring at runes will see patterns everywhere — this gives a number.
"""
import math
import os
import re

HERE = os.path.dirname(__file__)
QGRAM = os.path.normpath(os.path.join(HERE, "..", "..", "data", "english_quadgrams.txt"))

_NONALPHA = re.compile(r"[^A-Z]")


class Quadgram:
    def __init__(self, path=QGRAM):
        self.d = {}
        total = 0
        with open(path, encoding="ascii") as f:
            for line in f:
                q, c = line.split()
                c = int(c)
                self.d[q] = c
                total += c
        self.total = total
        self.logtotal = math.log10(total)
        for q in self.d:
            self.d[q] = math.log10(self.d[q]) - self.logtotal
        # floor for unseen quadgrams
        self.floor = math.log10(0.01) - self.logtotal

    def score(self, text):
        """Total log10 prob. Higher (less negative) = more English."""
        t = _NONALPHA.sub("", text.upper())
        if len(t) < 4:
            return -999.0
        s = 0.0
        for i in range(len(t) - 3):
            s += self.d.get(t[i:i + 4], self.floor)
        return s

    def score_norm(self, text):
        """Per-quadgram average; ~ -2.2 = solid English, < -4 = noise."""
        t = _NONALPHA.sub("", text.upper())
        n = len(t) - 3
        if n <= 0:
            return -999.0
        return self.score(t) / n


_DEFAULT = None


def default():
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = Quadgram()
    return _DEFAULT


if __name__ == "__main__":
    q = default()
    for s in ["WELCOMEPILGRIMTOTHEGREATJOURNEY",
              "BELIEVENOTHINGFROMTHISBOOK",
              "QXZJKVWPQXZJKVWPQXZJKVWP",
              "AOEUIDHTNSAOEUIDHTNS"]:
        print(f"{q.score_norm(s):7.3f}  {s}")
