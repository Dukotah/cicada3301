import sys; sys.path.insert(0,'src')
from lp import gematria as gp, score as sc
N=gp.N
Q=sc.default()
pages=open('data/krisyotam_runes.txt',encoding='utf-8').read().split('%')

def page_idxs(p, drop_f=True):
    out=[]
    for c in p:
        if c in gp.RUNE_TO_IDX:
            if drop_f and c=='ᚠ': continue
            out.append(gp.RUNE_TO_IDX[c])
    return out

def tl(idxs): return gp.indices_to_translit(idxs)
def best_over_pages(transform):
    """transform(idxs)->idxs. Score per page, return (best_score, page, snippet, avg)."""
    best=(-999,None,'')
    tot=0;n=0
    for pi,p in enumerate(pages):
        idxs=page_idxs(p)
        if len(idxs)<20: continue
        out=transform(idxs)
        s=Q.score_norm(tl(out))
        tot+=s; n+=1
        if s>best[0]:
            best=(s,pi,tl(out)[:60])
    return best, tot/max(n,1)

def sieve(n):
    pr=[];c=2
    while len(pr)<n:
        if all(c%x for x in pr if x*x<=c): pr.append(c)
        c+=1
    return pr

def primepi_upto(limit):
    # pi(k) for k=1..limit
    sieve_b=[True]*(limit+1); sieve_b[0]=sieve_b[1]=False
    for i in range(2,int(limit**.5)+1):
        if sieve_b[i]:
            for j in range(i*i,limit+1,i): sieve_b[j]=False
    pi=[0]*(limit+1); c=0
    for k in range(2,limit+1):
        if sieve_b[k]: c+=1
        pi[k]=c
    return pi

# A061474: alternating digit sum == 5
def a061474(count):
    out=[];n=1
    while len(out)<count:
        ds=[int(d) for d in str(n)]
        if sum(d*(1 if i%2==0 else -1) for i,d in enumerate(ds))==5:
            out.append(n)
        n+=1
    return out

results=[]

# 1. Beaufort: P = K - C  (use prime stream and totient stream as K)
ps=sieve(20000)
ts_prime=[(p-1) for p in ps]  # totient(prime)
def beaufort_prime(idxs):
    return [(ps[i]%N - c)%N for i,c in enumerate(idxs)]
def beaufort_totient(idxs):
    return [((ps[i]-1)%N - c)%N for i,c in enumerate(idxs)]
results.append(('Beaufort prime stream K-C', best_over_pages(beaufort_prime)))
results.append(('Beaufort totient(prime) K-C', best_over_pages(beaufort_totient)))

# 2. A061474 as additive (both signs) -- principled doublet exclusion but test anyway
a=a061474(20000); am=[x%N for x in a]
results.append(('A061474 subtract C-K', best_over_pages(lambda ix:[(c-am[i])%N for i,c in enumerate(ix)])))
results.append(('A061474 add C+K', best_over_pages(lambda ix:[(c+am[i])%N for i,c in enumerate(ix)])))
results.append(('A061474 Beaufort K-C', best_over_pages(lambda ix:[(am[i]-c)%N for i,c in enumerate(ix)])))

# 3. pi(p): prime-counting on the gematria prime of each ciphertext rune; subtract from 59 mod 29
PI=primepi_upto(200)
def pi_of_rune_59(idxs):
    out=[]
    for c in idxs:
        prime=gp.PRIMES[c]
        out.append((59 - PI[prime])%N)  # the wiki "subtract from 59 mod29" idea as key, then C-K
    return [(c-out[i])%N for i,c in enumerate(idxs)]
results.append(('pi(prime_of_C) key, 59-pi mod29, C-K', best_over_pages(pi_of_rune_59)))
# variant: key = pi(prime) mod29 directly
def pi_key(idxs):
    k=[PI[gp.PRIMES[c]]%N for c in idxs]
    return [(c-k[i])%N for i,c in enumerate(idxs)]
results.append(('pi(prime_of_C) key C-K', best_over_pages(pi_key)))

# 4. Gematria position-dependent (ciphertext feedback): shift_i = value of previous CIPHER rune
def cfeedback_sub(idxs, init=0):
    out=[]; prev=init
    for c in idxs:
        out.append((c-prev)%N); prev=c
    return out
def cfeedback_add(idxs, init=0):
    out=[]; prev=init
    for c in idxs:
        out.append((c+prev)%N); prev=c
    return out
results.append(('CipherFeedback shift=prevCipher C-prev', best_over_pages(cfeedback_sub)))
results.append(('CipherFeedback shift=prevCipher C+prev', best_over_pages(cfeedback_add)))

for name,(best,avg) in results:
    s,pi,snip=best
    print(f"{s:7.3f} avg={avg:6.2f}  {name}")
    print(f"          p{pi}: {snip}")
