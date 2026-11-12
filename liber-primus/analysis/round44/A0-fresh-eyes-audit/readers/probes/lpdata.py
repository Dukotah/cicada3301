"""Loader the audit readers' probes were written against (same parse as ../../lp2.py, older field names)."""
import hashlib, os
REPO=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','..','..'))
RUNES="ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
TR=["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
PRIMES=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
R2I={r:i for i,r in enumerate(RUNES)}
def load(path=os.path.join(REPO,'data','krisyotam_runes.txt')):
    """Return list of pages; each page = list of tokens (idx, meta) where meta = dict(word, line, sent, pos_in_word)
    plus the raw separator that FOLLOWS/PRECEDES. We record for each rune: page, line no, word no, sentence no,
    and the set of separators between it and the previous rune."""
    txt=open(path,encoding='utf-8').read()
    pages=[]
    for seg in txt.split('%'):
        runes=[]; seps=''
        line=0; word=0; sent=0
        for ch in seg:
            if ch in R2I:
                runes.append(dict(i=R2I[ch], line=line, word=word, sent=sent, pre=seps))
                seps=''
            else:
                seps+=ch
                if ch=='/': line+=1
                elif ch=='-': word+=1
                elif ch=='.': sent+=1; word+=1
        if runes: pages.append(runes)
    return pages
def unsolved_pages(): return load()[:-2]
def flat(pages): return [r['i'] for p in pages for r in p]
if __name__=='__main__':
    P=load(); print(len(P),'segments', [len(p) for p in P][:10])
    U=flat(P[:-2]); print(len(U))
    print(hashlib.sha256(','.join(map(str,U)).encode()).hexdigest())
