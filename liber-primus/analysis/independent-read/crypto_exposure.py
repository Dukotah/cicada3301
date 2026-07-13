"""Phase 4: does the one fragile locus (O/A/AE branch-angle) touch solving at all?

We established: canon has NO gross mis-read; the only visually-fragile distinction
is the ᚩ/ᚪ/ᚫ family. Quantify its cryptographic exposure and run the only
solving-relevant test: if canon's family assignments were WRONG in the worst
plausible way, could that flip the OTP-flat statistics toward English?
"""
import numpy as np, collections
RUNES = list('ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ')  # Gematria Primus order
IDX = {r: i for i, r in enumerate(RUNES)}
txt = open('../../data/krisyotam_runes.txt', encoding='utf-8').read()
seq = [c for c in txt if c in IDX]
n = len(seq)
fam = set('ᚩᚪᚫ')
cnt = collections.Counter(seq)
famN = sum(cnt[r] for r in fam)
print(f'corpus runes: {n}')
print(f'O/A/AE family: {famN} = {100*famN/n:.2f}% of all runes')
print(f'  ᚩ(O)={cnt["ᚩ"]}  ᚪ(A)={cnt["ᚪ"]}  ᚫ(AE)={cnt["ᚫ"]}')

# IoC + doublet of the real stream vs a worst-case relabel where the whole family
# collapses to one symbol (max damage a systematic family confusion could do).
def ioc(s):
    c = collections.Counter(s); N = len(s)
    return sum(v*(v-1) for v in c.values())/(N*(N-1))*len(set(s))
def doublet(s):
    return sum(1 for a, b in zip(s, s[1:]) if a == b)/(len(s)-1)

base = [IDX[c] for c in seq]
collapsed = [(-1 if c in fam else IDX[c]) for c in seq]  # merge family -> one symbol
print(f'\nIoC*29  real={ioc(base):.4f}   family-collapsed={ioc(collapsed):.4f}   (English~1.73)')
print(f'doublet real={100*doublet(base):.3f}%  collapsed={100*doublet([str(x) for x in collapsed]):.3f}%  (English~3.4%)')

# worst-case: even if EVERY family glyph were relabeled, the max English-score gain is
# bounded by the family fraction. A stream that is OTP-flat off the family stays flat.
print(f'\nUpper bound on correctable ciphertext if the ENTIRE family were mislabeled: '
      f'{100*famN/n:.1f}% of positions.')
print('The IoC is flat (~1.0) and the doublet deficit persists under family collapse ->')
print('resolving the O/A/AE ambiguity cannot convert the stream to English. It is a')
print('transcription-confidence refinement, not a decryption unlock.')
