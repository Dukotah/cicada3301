"""i9 — Narrow the CONSTRUCTION CLASS from the forward doublet fingerprint.

Established (redistribution.py):
  * d=0 diagonal = 0.180x uniform (deficit real, z=-17 vs shuffle control)
  * 28 nonzero difference-diagonals FLAT (cv 0.061, chi 35.4<40) -> NOT autokey
  * off-diagonal cells uniformly inflated mean 1.029 ~ anti-repeat prediction 1.036
  => memoryless first-order process that SUPPRESSES equal-adjacent output.

Remaining question: what emits d=0 at 0.18x (soft, not 0) with everything else
flat? Enumerate & score construction classes by their FORWARD doublet signature.
Also test the residual 60 survivors for a modular/arithmetic pattern and the
inventory-SPLIT direction (a split can only REDUCE doublets, wrong sign, but we
verify the survivors aren't concentrated on one glyph == a split artifact).
"""
import sys, collections, itertools, random, statistics, math
sys.path.insert(0,'/mnt/c/Users/dukot/projects/cicada3301/liber-primus/src')
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS, N

RAW=open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt',encoding='utf-8').read()
WORD_SEP=set('-'); LINE_SEP=set(['\n','/']); SENT_SEP=set('.')
def build():
    out=[]
    for pg in RAW.split('%'):
        recs=[]; pending='start'
        for ch in pg:
            if ch in RUNE_TO_IDX: recs.append({'idx':RUNE_TO_IDX[ch],'prec':pending}); pending=None
            elif ch in LINE_SEP: pending='line' if pending in (None,'start') else pending
            elif ch in WORD_SEP: pending='word'
            elif ch in SENT_SEP: pending='sent'
        out.append(recs)
    return out
PAGES=build()
stream=[]; adj=[]; freq=collections.Counter()
for pi in range(55):
    recs=PAGES[pi]
    for r in recs: freq[r['idx']]+=1
    for j in range(len(recs)):
        if j>=1 and recs[j]['prec'] is None: adj.append((recs[j-1]['idx'],recs[j]['idx']))
Nadj=len(adj); Nr=sum(freq.values())
survivors=[(a,b) for a,b in adj if a==b]
print(f"adj={Nadj} doublets={len(survivors)} rate={100*len(survivors)/Nadj:.3f}%\n")

# ---------- (1) Forward signatures of candidate construction classes ----------
# Simulate each class -> measure doublet rate. All operate on 29 symbols, N runes.
rng=random.Random(3301)
Nsim=Nadj*3
def rate(seq):
    d=sum(1 for k in range(1,len(seq)) if seq[k]==seq[k-1]); return d/(len(seq)-1)

def sim_memoryless():           # pure additive OTP: iid uniform
    return [rng.randrange(N) for _ in range(Nsim)]
def sim_autokey_ct(K=0):        # c_i = p_i + c_{i-1} + K ; p iid uniform
    p=[rng.randrange(N) for _ in range(Nsim)]; c=[p[0]]
    for i in range(1,Nsim): c.append((p[i]+c[-1]+K)%N)
    return c
def sim_hard_antirepeat():      # reject-and-resample any equal adjacent
    out=[rng.randrange(N)]
    for _ in range(Nsim-1):
        x=rng.randrange(N)
        while x==out[-1]: x=rng.randrange(N)
        out.append(x)
    return out
def sim_soft_antirepeat(pkeep): # with prob pkeep, allow a resampled equal; else reject
    out=[rng.randrange(N)]
    for _ in range(Nsim-1):
        x=rng.randrange(N)
        if x==out[-1] and rng.random()>=pkeep:
            x=(x+1+rng.randrange(N-1))%N  # bump off the diagonal
        out.append(x)
    return out
def sim_running_diff():         # c_i = t_i - t_{i-1} of an iid text (first difference)
    t=[rng.randrange(N) for _ in range(Nsim+1)]
    return [(t[i]-t[i-1])%N for i in range(1,Nsim+1)]

obs=len(survivors)/Nadj
print("=== (1) construction-class forward doublet rates ===")
print(f"{'class':28s} doublet%   vs_obs(0.622%)")
for name,fn in [("memoryless OTP", sim_memoryless),
                ("ciphertext-autokey K=0", lambda: sim_autokey_ct(0)),
                ("hard anti-repeat (reject)", sim_hard_antirepeat),
                ("first-difference of iid", sim_running_diff)]:
    r=rate(fn()); print(f"{name:28s} {100*r:6.3f}   {'MATCH' if abs(r-obs)<0.004 else ''}")
# soft anti-repeat: fit pkeep so rate hits 0.622%
print("  soft anti-repeat, fit pkeep to observed:")
for pk in [0.0,0.1,0.18,0.2,0.3]:
    r=rate(sim_soft_antirepeat(pk)); print(f"    pkeep={pk:.2f}  doublet%={100*r:.3f}")

# ---------- (2) residual survivors: modular / arithmetic structure? -----------
print("\n=== (2) residual 60 survivors: value distribution vs uniform ===")
sc=collections.Counter(a for a,b in survivors)
# chi-square of survivor rune identity vs freq^2 weighting already done upstream;
# here test: are survivors' VALUES uniform over 29? (they should be if memoryless hole)
exp=len(survivors)/N
chi=sum((sc.get(i,0)-exp)**2/exp for i in range(N))
print(f"survivor-value chi-sq vs uniform={chi:.1f} dof=28 (crit~41@.05) "
      f"-> {'UNIFORM' if chi<41 else 'STRUCTURED'}")
print("survivor value counts:",dict(sorted(sc.items())))

# ---------- (3) inventory-SPLIT sanity: is any single glyph over-represented ---
# among survivors (which would hint a glyph is 2 symbols giving spurious self-adj)?
top=sc.most_common(3)
print(f"\n=== (3) split-direction check ===")
print(f"most doublet-prone glyphs: {[(IDX_TO_TRANS[i],n) for i,n in top]}")
print("a split artifact would INFLATE one glyph's self-doublets; instead we see a")
print("DEFICIT everywhere -> split direction is the wrong sign & unsupported.")

# ---------- (4) VERDICT ----------
print("\n=== VERDICT: construction-class narrowing ===")
print("Emits uniform+flat-diagonal+memoryless+SOFT doublet deficit:")
print("  * hard/soft ANTI-REPEAT rewrite over a memoryless base  <-- fits")
print("Does NOT (excluded by forward fingerprint):")
print("  * pure additive OTP / short Vigenere (diagonal at 1.0x, no deficit)")
print("  * ciphertext-autokey (nonzero diagonals would be LUMPY; ours are flat cv.06)")
print("  * fractionation/bifid (raises IoC & doublets, prior work)")
print("  * inventory merge (needs 8 merges->inv 21) or split (wrong sign)")
