"""i9 CONTRARIAN-SKEPTIC — DOUBT THE UNIT OF ANALYSIS (inventory cardinality).

Premise (b'): the 29-rune inventory cardinality has NEVER been tested. The
alphabet-ORDER attack relabels 29 fixed symbols and cannot detect that the TRUE
inventory is 28 (two visually-distinct glyphs are one underlying symbol) or 30
(one glyph is two).

KEY INSIGHT: if two ciphertext glyphs A,B are actually ONE symbol (scribal
variant), then every "AB" or "BA" adjacency is a GENUINE doublet that our
29-symbol counter MISSES. Merging that pair would lift the doublet rate toward
the ~3.4% baseline. So an inventory error and the doublet deficit could be the
SAME thing.

TEST (forward, model-free, NOT key-search):
  For every unordered pair (A,B) of the 29 runes, MERGE them (treat as one
  symbol) and recompute the adjacent-doublet rate over pages 0-54. A true merge
  candidate is a pair whose merge lifts the rate SIGNIFICANTLY above the 60
  baseline doublets AND beyond a random control band.

  Control: the EXPECTED extra doublets from merging A,B under independence is
  2 * n_A * n_B / n_pairs (cross-adjacencies AB + BA). If observed extra >> that,
  the two glyphs avoid each other MORE than chance -> anti-correlation, the
  OPPOSITE of a merge signature (a real merge would show AB/BA adjacencies at or
  ABOVE the independence rate, contributing real doublets).

  A merge that EXPLAINS the deficit must (i) add many doublets and (ii) the
  AB/BA cross rate must be at least the independence expectation (not suppressed).
"""
import sys, collections, itertools, math, random
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus/src')
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS, RUNES, N

RAW = open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt', encoding='utf-8').read()
WORD_SEP=set('-'); SENT_SEP=set('.'); LINE_SEP=set(['\n','/'])

def build_pages():
    pages=RAW.split('%'); out=[]
    for pg in pages:
        recs=[]; pending='start'
        for ch in pg:
            if ch in RUNE_TO_IDX:
                recs.append({'idx':RUNE_TO_IDX[ch],'prec':pending}); pending=None
            elif ch in LINE_SEP: pending='line' if pending in (None,'start') else pending
            elif ch in WORD_SEP: pending='word'
            elif ch in SENT_SEP: pending='sent'
        out.append(recs)
    return out

PAGES=build_pages()
SCOPE=range(0,55)

# Build the list of ADJACENT (intra-word) ordered pairs over scope.
adj=[]      # (a,b) index pairs that are truly adjacent (no separator between)
freq=collections.Counter()
for pi in SCOPE:
    recs=PAGES[pi]
    for r in recs: freq[r['idx']]+=1
    for j in range(1,len(recs)):
        if recs[j]['prec'] is None:
            adj.append((recs[j-1]['idx'], recs[j]['idx']))

Nadj=len(adj)
Nrune=sum(freq.values())
base_doublets=sum(1 for a,b in adj if a==b)
print(f"scope pages 0-54: runes={Nrune} adj_pairs={Nadj}")
print(f"baseline doublets={base_doublets} = {100*base_doublets/Nadj:.3f}%")
exp_rate=sum((freq[i]/Nrune)**2 for i in freq)
print(f"expected (indep) doublet rate={100*exp_rate:.3f}%  -> deficit ratio={base_doublets/(exp_rate*Nadj):.3f}\n")

# ---- cross-adjacency matrix M[a][b] = count of adjacency a->b
M=collections.Counter()
for a,b in adj: M[(a,b)]+=1

# ---- MERGE test over all 406 unordered pairs
print("=== INVENTORY MERGE TEST (all 406 pairs) ===")
print("If glyphs A,B are one symbol, merging adds their AB+BA adjacencies as")
print("doublets. Report pairs whose cross-adjacency (AB+BA) is HIGHEST, and")
print("compare observed cross-count to the independence expectation.\n")
results=[]
for a,b in itertools.combinations(range(N),2):
    cross = M[(a,b)] + M[(b,a)]          # AB + BA adjacencies (become doublets if merged)
    # independence expectation for cross adjacencies among the Nadj pairs
    pa=freq[a]/Nrune; pb=freq[b]/Nrune
    exp_cross = Nadj * 2*pa*pb
    ratio = cross/exp_cross if exp_cross>0 else float('nan')
    results.append((a,b,cross,exp_cross,ratio))

# Sort by observed cross count (a real merge would ADD the most doublets)
results.sort(key=lambda x:-x[2])
print("TOP-15 by observed cross-adjacency (merge would add these doublets):")
print("  A    B    cross  exp_indep  obs/exp")
for a,b,cross,exp,ratio in results[:15]:
    print(f"  {IDX_TO_TRANS[a]:<3} {IDX_TO_TRANS[b]:<3}  {cross:>4}   {exp:>6.1f}   {ratio:.2f}")

print("\nTOP-15 by obs/exp (pairs most OVER-adjacent vs chance):")
valid=[r for r in results if r[3]>=3]
valid.sort(key=lambda x:-x[4])
print("  A    B    cross  exp_indep  obs/exp")
for a,b,cross,exp,ratio in valid[:15]:
    print(f"  {IDX_TO_TRANS[a]:<3} {IDX_TO_TRANS[b]:<3}  {cross:>4}   {exp:>6.1f}   {ratio:.2f}")

# ---- Does merging the single best pair fix the deficit?
best=max(results,key=lambda x:x[2])
a,b,cross,exp,ratio=best
new_doublets=base_doublets+cross
new_adj=Nadj  # merging reduces symbol count but adjacency count unchanged
# after merge, the merged symbol frequency = fa+fb, recompute exp
newfreq=dict(freq); newfreq[a]=freq[a]+freq[b]; del newfreq[b]
newNr=sum(newfreq.values())
new_exp_rate=sum((v/newNr)**2 for v in newfreq.values())
print(f"\n=== Merging single best pair ({IDX_TO_TRANS[a]},{IDX_TO_TRANS[b]}) ===")
print(f"  adds {cross} doublets -> {new_doublets} = {100*new_doublets/new_adj:.3f}%")
print(f"  new expected rate (28 symbols) = {100*new_exp_rate:.3f}%")
print(f"  deficit ratio after merge = {new_doublets/(new_exp_rate*new_adj):.3f} (was {base_doublets/(exp_rate*Nadj):.3f})")

# ---- How many merges to reach baseline 3.4%?
target=int(round(exp_rate*Nadj))
print(f"\n=== Cumulative merge to reach baseline (~{target} doublets) ===")
# greedily merge highest-cross pairs (disjoint), see how many needed & how absurd
used=set(); cum=base_doublets; nmerge=0
for a,b,cross,exp,ratio in results:
    if a in used or b in used: continue
    used.add(a); used.add(b); cum+=cross; nmerge+=1
    if cum>=target:
        print(f"  need {nmerge} disjoint merges (=> inventory would be {N-nmerge}) to reach {cum} doublets")
        break
else:
    print(f"  even merging all {nmerge} disjoint pairs only reaches {cum} doublets (target {target})")
    print(f"  => inventory-merge CANNOT reconstruct the baseline. Deficit is NOT a merge artifact.")

# ---- Verdict logic
print("\n=== VERDICT ===")
maxratio=max((r[4] for r in results if r[3]>=3))
if maxratio < 1.5:
    print(f"No pair is over-adjacent (max obs/exp={maxratio:.2f}); all cross-adjacencies")
    print("are AT or BELOW chance. A hidden merge would require AB/BA adjacencies at")
    print(">= chance. They are NOT. -> 29-inventory is consistent; deficit is NOT an")
    print("under-counting (merge) artifact. The anti-repeat rule suppresses cross-")
    print("adjacency for ALL pairs uniformly, not just self-pairs.")
else:
    print(f"CANDIDATE: some pair over-adjacent (max obs/exp={maxratio:.2f}) — inspect above.")
