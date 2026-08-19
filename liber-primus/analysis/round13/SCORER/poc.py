"""POC: does a transliteration-MATCHED quadgram model widen the English/noise gap?

Every scorer in this repo is trained on raw English. The decoder emits the runic
TRANSLITERATION, in which 7 of 29 runes expand to 2 characters (TH EO NG OE AE IA EA)
and the alphabet is lossy (no K/Q/V/Z). Training on raw English and scoring
transliteration is a distribution mismatch, and mismatch costs detection power.

Test: build quadgrams over English PUSHED THROUGH the same rune round-trip, then compare
the English/noise separation of the two models on the SOLVED pages (known ground truth).
"""
import os, sys, math, random, collections
LP = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis", "round11"))
sys.path.insert(0, os.path.join(LP, "analysis", "campaign18_skip"))
import lib_numchannel as nc
import skipdecode as sk
from lp import gematria as gp
from lp import score as lpscore

N = 29
T = [gp.IDX_TO_TRANS[i] for i in range(N)]

def idx_to_translit(idxs):
    return "".join(T[i % N] for i in idxs)

def build_quadgrams(text):
    """Quadgram counts over a transliteration-space string."""
    c = collections.Counter()
    for i in range(len(text) - 3):
        c[text[i:i+4]] += 1
    tot = sum(c.values())
    lo = math.log10(0.01 / tot)
    return {k: math.log10(v / tot) for k, v in c.items()}, lo

def score_with(model, floor, s):
    if len(s) < 4:
        return floor
    return sum(model.get(s[i:i+4], floor) for i in range(len(s) - 3)) / (len(s) - 3)

# ---- training corpus: KJV, pushed through the rune round-trip
kjv = open(os.path.join(LP, "data", "kjv.txt"), encoding="utf-8", errors="ignore").read()
kjv = kjv[:3_000_000]
train_idx = sk.eng_to_idx(kjv)
train_translit = idx_to_translit(train_idx)
print(f"training: {len(kjv):,} chars English -> {len(train_idx):,} runes "
      f"-> {len(train_translit):,} transliteration chars")
matched, floor = build_quadgrams(train_translit)
print(f"matched model: {len(matched):,} distinct quadgrams, floor {floor:.3f}")

old = lpscore.default()

# ---- ground truth: the solved pages, as the decoder would emit them
solved = {
    "01 A WARNING": "AWARNNGBELIEUENOTHNGFROMTHISBOOCEXCEPTWHATYOUCNOWTOBETRUETESTTHECNOWLEDGEFINDYOURTRUTHEXPERIENCE",
    "05 SOME WISDOM": "SOMEWISDOMTHEPRIMESARESACREDTHETOTIENTFUNCTIANISSACREDALLTHNGSSHOULDBEENCRYPTEDCNOWTHISSHADOWSAE",
    "06 A KOAN": "ACOANAMANDECIDEDTOGOANDSTUDYWITHAMASTERHEWENTTOTHEDOOROFTHEMASTERWHOAREYOUWHOWISHESTOSTUDYHEREAS",
    "03 WELCOME": "WELCOMEWELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOALLTHNGSITISNOTANEASYTRIPBUTORTHOSEWHOINDTHEI",
    "14 CIRCUMFERENCE": "ACOANDURNGALESSONTHEMASTEREXPLAINEDTHEITHEIISTHEUOICEOTHECIRCUMERENCEHESAIDWHENASCEDBYASTUDENTTO",
}

# ---- noise: shuffled unsolved ciphertext, transliterated
UNS = nc.unsolved()
rng = random.Random(3301)
noise_old, noise_new = [], []
for k in range(200):
    s = UNS[:400][:]
    rng.shuffle(s)
    t = idx_to_translit(s)
    noise_old.append(old.score_norm(t))
    noise_new.append(score_with(matched, floor, t))

def mean(x): return sum(x) / len(x)

print(f"\n{'page':22s} {'OLD (English qgram)':>20s} {'NEW (matched)':>16s}")
eo, en = [], []
for name, txt in solved.items():
    a, b = old.score_norm(txt), score_with(matched, floor, txt)
    eo.append(a); en.append(b)
    print(f"{name:22s} {a:20.3f} {b:16.3f}")

print(f"\n{'noise mean':22s} {mean(noise_old):20.3f} {mean(noise_new):16.3f}")
print(f"{'noise max':22s} {max(noise_old):20.3f} {max(noise_new):16.3f}")
print(f"{'noise sd':22s} "
      f"{(sum((x-mean(noise_old))**2 for x in noise_old)/len(noise_old))**.5:20.3f} "
      f"{(sum((x-mean(noise_new))**2 for x in noise_new)/len(noise_new))**.5:16.3f}")

sd_o = (sum((x-mean(noise_old))**2 for x in noise_old)/len(noise_old))**.5
sd_n = (sum((x-mean(noise_new))**2 for x in noise_new)/len(noise_new))**.5
print(f"\nSEPARATION (mean solved - mean noise), in noise sigmas:")
print(f"  OLD: {mean(eo)-mean(noise_old):+.3f} raw  =  {(mean(eo)-mean(noise_old))/sd_o:.2f} sigma")
print(f"  NEW: {mean(en)-mean(noise_new):+.3f} raw  =  {(mean(en)-mean(noise_new))/sd_n:.2f} sigma")
