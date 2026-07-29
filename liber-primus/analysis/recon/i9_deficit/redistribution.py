"""i9 — Where does the missing doublet mass GO? Redistribution fingerprint.

The merge test showed no single pair explains the deficit (need 8 merges ->
inventory 21, absurd). But it revealed that ALL cross-pairs sit at ~1.0-1.6x
independence while self-pairs sit at 0.18x. This script characterizes that
redistribution precisely and builds a proper random CONTROL BAND so we know
whether 'cross-pairs mildly elevated' is signal or noise, and pins the
construction class.

Constructions and their off-diagonal signature on the adjacency matrix M[a,b]:
  * pure additive OTP (memoryless): M ~ independence -> diagonal AND off-diag at 1.0x
  * anti-repeat rewrite (reject c_i==c_{i-1}, resample): diagonal -> ~0, off-diag
    inflated UNIFORMLY by factor 1/(1-1/29) ~= 1.036 ... too small to see alone,
    BUT the observed deficit is stronger (0.18x not 0), so partial.
  * ciphertext-autokey c_i = p_i + c_{i-1} + K: doublet <=> p_i = -K (one fixed
    plaintext rune's freq). Off-diagonal M[a,b] = freq of plaintext rune (b-a-K).
    -> each DIAGONAL of the matrix (constant b-a) is CONSTANT = a plaintext freq.
    This is the DECISIVE test: is M constant along lines of constant (b-a)?
"""
import sys, collections, itertools, random, statistics
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
adj=[]; freq=collections.Counter()
for pi in range(55):
    recs=PAGES[pi]
    for r in recs: freq[r['idx']]+=1
    for j in range(1,len(recs)):
        if recs[j]['prec'] is None: adj.append((recs[j-1]['idx'],recs[j]['idx']))
Nadj=len(adj); Nr=sum(freq.values())
M=collections.Counter(adj)

# ---------- (A) Diagonal-sum fingerprint: is M constant along b-a = const? ----
# Under ciphertext-autokey, M[a,b] depends ONLY on (b-a) mod 29 (== plaintext
# rune -K's distribution shifted). So the 29 "difference diagonals" would carry
# ALL structure and each diagonal would be ~flat. Under memoryless OTP, diagonals
# are also ~flat but the d=0 diagonal is NOT special. Under anti-repeat, ONLY
# d=0 is depressed and the rest are ~uniform.
print("=== (A) Difference-diagonal profile  d=(b-a) mod 29 ===")
diag=collections.Counter()
for (a,b),c in M.items(): diag[(b-a)%N]+=c
tot=sum(diag.values())
print(f"total adj={tot}  uniform-per-diagonal={tot/N:.1f}")
rows=sorted(diag.items(),key=lambda x:x[1])
print("d   count   vs_uniform")
for d,c in rows[:4]+rows[-3:]:
    print(f"{d:>2}  {c:>5}   {c/(tot/N):.3f}")
d0=diag[0]
print(f"\nd=0 (doublets) = {d0}  ratio to uniform = {d0/(tot/N):.3f}")
others=[c for d,c in diag.items() if d!=0]
print(f"d!=0 diagonals: mean={statistics.mean(others):.1f} std={statistics.pstdev(others):.1f} "
      f"cv={statistics.pstdev(others)/statistics.mean(others):.3f}")
print("-> if ONLY d=0 is an outlier and d!=0 are flat (low cv): anti-repeat / OTP-with-hole.")
print("-> if many diagonals are outliers: autokey (each diagonal = a plaintext freq).")

# chi-square of the 28 nonzero diagonals vs flat
exp=statistics.mean(others)
chi=sum((c-exp)**2/exp for c in others)
print(f"chi-sq(28 nonzero diagonals vs flat)={chi:.1f}  dof=27  (crit~40 @p.05)")

# ---------- (B) Control band: shuffle preserving freq, measure doublet rate ----
print("\n=== (B) Random control band (freq-preserving shuffle) ===")
flat_stream=[]
for i,c in freq.items(): flat_stream+=[i]*c
rng=random.Random(3301); rates=[]
for _ in range(500):
    rng.shuffle(flat_stream)
    dd=sum(1 for k in range(1,len(flat_stream)) if flat_stream[k]==flat_stream[k-1])
    rates.append(dd)
mu=statistics.mean(rates); sd=statistics.pstdev(rates)
# scale: shuffle counts over full stream vs our intra-word adj count
scale=Nadj/(len(flat_stream)-1)
print(f"shuffle doublets: mean={mu*scale:.1f} sd={sd*scale:.1f} (scaled to {Nadj} adj pairs)")
print(f"observed doublets=60  -> z={(60-mu*scale)/(sd*scale):.2f}")
print("(z very negative => deficit is real & far outside random; not an inventory/count fluke)")

# ---------- (C) off-diagonal elevation: is it uniform (anti-repeat) or lumpy? --
print("\n=== (C) Off-diagonal cell elevation vs independence ===")
ratios=[]
for a,b in itertools.permutations(range(N),2):
    exp_ab=Nadj*(freq[a]/Nr)*(freq[b]/Nr)
    if exp_ab>=5:
        ratios.append(M[(a,b)]/exp_ab)
print(f"off-diag cells (exp>=5): n={len(ratios)} mean={statistics.mean(ratios):.3f} "
      f"sd={statistics.pstdev(ratios):.3f} min={min(ratios):.2f} max={max(ratios):.2f}")
# expected uniform inflation if the ONLY effect is removing the diagonal:
inflate=1/(1-1/N)
print(f"predicted uniform off-diag inflation from a perfect anti-repeat = {inflate:.3f}")
print("-> off-diag mean near this value + low sd = pure uniform anti-repeat redistribution.")
print("-> off-diag mean ~1.0 with the diagonal merely SOFT = memoryless w/ weak diag hole.")
