import sys, math
sys.path.insert(0,'/mnt/c/Users/dukot/projects/cicada3301/liber-primus/src')
from lp.gematria import RUNES, RUNE_TO_IDX, RUNE_TO_TRANS, IDX_TO_RUNE

RSET=set(RUNES)
raw=open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt',encoding='utf-8').read()
parts=raw.split('%')
# keep only parts that have runes; record their index
pages=[]
for p in parts:
    rs=[c for c in p if c in RSET]
    if rs:
        pages.append((p,rs))
print('non-empty pages:',len(pages))

# In-scope = first 55 rune-pages (0-54). krisyotam segment 55 = AN END (solved).
# We'll use all rune-pages but note scope.
scope=pages  # treat all; report count

def idx_stream(runes):
    return [RUNE_TO_IDX[c] for c in runes]

def ioc(seq, n):
    from collections import Counter
    c=Counter(seq); L=len(seq)
    if L<2: return 0
    return sum(v*(v-1) for v in c.values())/(L*(L-1))*n

def doublets(seq):
    if len(seq)<2: return 0
    return sum(1 for a,b in zip(seq,seq[1:]) if a==b)/(len(seq)-1)

def period_test(seq,n,maxlag=120):
    # autocorrelation: prob seq[i]==seq[i+lag]
    res=[]
    for lag in range(1,maxlag+1):
        m=sum(1 for i in range(len(seq)-lag) if seq[i]==seq[i+lag])
        d=len(seq)-lag
        if d>0: res.append((lag,m/d))
    base=1.0/n
    # find biggest spike
    res.sort(key=lambda x:-x[1])
    return res[:8], base

# ===== Baseline: 29-rune index stream =====
allrunes=[c for (_,rs) in scope for c in rs]
S=idx_stream(allrunes)
print('\n=== BASELINE 29-rune index stream ===')
print('len',len(S),'IoC*29=%.4f'%ioc(S,29),'doublet%%=%.4f'%(doublets(S)*100))
spikes,base=period_test(S,29)
print('expected match prob %.4f; top period spikes:'%base, [(l,round(p,4)) for l,p in spikes])

# ===== (a) LATIN MULTIGRAPH EXPANSION =====
# Expand each rune to its latin translit; produce a stream over A-Z letters.
print('\n=== (a) LATIN MULTIGRAPH EXPANSION ===')
latin=''.join(RUNE_TO_TRANS[c] for c in allrunes)
print('latin char stream len',len(latin))
# map to 26 alphabet indices
def letidx(s):
    return [ord(c)-65 for c in s if 'A'<=c<='Z']
L26=letidx(latin)
print('A-Z stream len',len(L26),'IoC*26=%.4f'%ioc(L26,26),'doublet%%=%.4f'%(doublets(L26)*100))
spikes,base=period_test(L26,26)
print('expected %.4f; top spikes:'%base,[(l,round(p,4)) for l,p in spikes])
# Also collapse multigraphs as single tokens but over reduced 26-ish? Already index does 29.
# letter frequency
from collections import Counter
cc=Counter(latin)
print('letter freq top:',cc.most_common(8))

# ===== (b) PAGE CONCATENATION ORDERINGS =====
print('\n=== (b) PAGE ORDERING VARIANTS (look for running-key period) ===')
def report(name,seq):
    sp,b=period_test(seq,29,maxlag=120)
    print('%-22s len=%d IoC*29=%.4f dbl%%=%.4f topspike=%s'%(name,len(seq),ioc(seq,29),doublets(seq)*100,(sp[0][0],round(sp[0][1],4))))
# sequential (baseline)
report('sequential', S)
# reverse page order
rev=[c for (_,rs) in reversed(scope) for c in rs]
report('reverse-page', idx_stream(rev))
# reverse rune order (whole)
report('reverse-all', S[::-1])
# sort pages by first rune (title-ish)
byfirst=sorted(scope,key=lambda pr: RUNE_TO_IDX[pr[1][0]])
report('sort-by-firstrune', idx_stream([c for (_,rs) in byfirst for c in rs]))
# sort by page length
bylen=sorted(scope,key=lambda pr: len(pr[1]))
report('sort-by-length', idx_stream([c for (_,rs) in bylen for c in rs]))
# interleave: take rune i from each page round-robin
maxlen=max(len(rs) for _,rs in scope)
inter=[]
for i in range(maxlen):
    for _,rs in scope:
        if i<len(rs): inter.append(rs[i])
report('interleave-rrobin', idx_stream(inter))
# even pages then odd pages
ep=[c for k,(_,rs) in enumerate(scope) if k%2==0 for c in rs]
op=[c for k,(_,rs) in enumerate(scope) if k%2==1 for c in rs]
report('even-then-odd', idx_stream(ep+op))

# ===== (c) COUNT SEQUENCE as number stream =====
print('\n=== (c) COUNT SEQUENCES vs known integer sequences ===')
page_counts=[len(rs) for _,rs in scope]
print('runes-per-page (%d pages):'%len(page_counts))
print(page_counts)
# lines per page rune counts
line_counts=[]
for p,rs in scope:
    for ln in p.split('\n'):
        c=[x for x in ln if x in RSET]
        if c: line_counts.append(len(c))
print('\nruns-per-line count (%d lines), first 40:'%len(line_counts))
print(line_counts[:40])

# compare to primes
def primes_upto(n):
    out=[];x=2
    while len(out)<n:
        if all(x%p for p in out if p*p<=x): out.append(x)
        x+=1
    return out
P=primes_upto(max(len(page_counts),len(line_counts))+5)
def totient(n):
    r=n;p=2;m=n
    while p*p<=m:
        if m%p==0:
            while m%p==0:m//=p
            r-=r//p
        p+=1
    if m>1:r-=r//m
    return r
print('\nprimes start:',P[:15])
print('page_counts match primes?', page_counts[:15]==P[:15])
# is any count prime?
def isprime(n):
    if n<2:return False
    return all(n%i for i in range(2,int(n**.5)+1))
print('page_counts all prime?', all(isprime(c) for c in page_counts))
print('line_counts all prime?', all(isprime(c) for c in line_counts))
print('num prime page_counts:',sum(isprime(c) for c in page_counts),'/',len(page_counts))
print('num prime line_counts:',sum(isprime(c) for c in line_counts),'/',len(line_counts))
# diffs
diffs=[page_counts[i+1]-page_counts[i] for i in range(len(page_counts)-1)]
print('page count diffs:',diffs)
