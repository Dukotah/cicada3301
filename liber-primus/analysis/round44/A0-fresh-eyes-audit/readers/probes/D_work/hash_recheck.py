# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork D verification: corrected pp49-51 payload vs the page-56 512-bit target under the hash families
the R34-P1 promotion did NOT re-run (Whirlpool, Skein-512, Streebog-512, BLAKE-512, Keccak-512) plus hashlib 512s.
Exact test (FP 2^-512). Read-only on the repo; no bytecode written."""
import sys, os, json, hashlib, itertools
sys.dont_write_bytecode = True
A=_ROOT+'/liber-primus/analysis'
sys.path.insert(0, os.path.join(A,'pp49_51')); sys.path.insert(0, os.path.join(A,'pp49_51','blake_closure'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),'pylib'))
import whirlpool_ref, skein_ref, blake_ref, gostcrypto
from Crypto.Hash import keccak
TARGET=("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
        "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")
# --- KAT gates
for m,e in whirlpool_ref.TEST_VECTORS.items(): assert whirlpool_ref.whirlpool(m)==e
for m,e in skein_ref.TEST_VECTORS.items(): assert skein_ref.skein512_512(m)==e
for m,e in blake_ref.TEST_VECTORS_512.items(): assert blake_ref.blake512(m)==e
def streebog(b):
    h=gostcrypto.gosthash.new('streebog512'); h.update(b); return h.digest().hex()
assert streebog(b"").startswith("8e945da209aa869f0455928529bcae46")
def kecc(b):
    h=keccak.new(digest_bits=512); h.update(b); return h.hexdigest()
assert kecc(b"")=="0eab42de4c3ceb9235fc91acffe746b29c29a8c366b7c60e4e67c466f36a4304c00fa9caf9d87976ba469bcbe06713b435f091ef2769fb160cdab33d3670680e"
ALG={'whirlpool':whirlpool_ref.whirlpool,'skein512':skein_ref.skein512_512,'blake512':blake_ref.blake512,
     'streebog512':streebog,'streebog512_rev':lambda b: bytes.fromhex(streebog(b))[::-1].hex(),'keccak512':kecc,
     'sha512':lambda b:hashlib.sha512(b).hexdigest(),'sha3_512':lambda b:hashlib.sha3_512(b).hexdigest(),
     'blake2b':lambda b:hashlib.blake2b(b).hexdigest(),'shake256_64':lambda b:hashlib.shake_256(b).hexdigest(64)}
canon=open(os.path.join(A,'pp49_51','canon_256.bin'),'rb').read()
res=open(os.path.join(A,'round18','L5-payload','payload_resolved.bin'),'rb').read()
assert canon==res and len(res)==256
old=open(os.path.join(A,'pp49_51','canon_256_superseded.bin'),'rb').read()
nr=json.load(open(os.path.join(A,'round18','L3-ornaments','nonrunic.json')))
pages=nr['pages']
C={}
def binv(label,b):
    C[label+':raw']=b; C[label+':rev']=b[::-1]; C[label+':+nl']=b+b'\n'; C[label+':hex']=b.hex().encode()
    C[label+':HEX']=b.hex().upper().encode(); C[label+':hex+nl']=(b.hex()+'\n').encode()
    C[label+':bitrev']=bytes(int(f'{x:08b}'[::-1],2) for x in b); C[label+':b64']=__import__('base64').b64encode(b)
    C[label+':dec_sp']=' '.join(str(x) for x in b).encode(); C[label+':dec_nl']='\n'.join(str(x) for x in b).encode()
    C[label+':int_dec']=str(int.from_bytes(b,'big')).encode(); C[label+':int_dec_le']=str(int.from_bytes(b,'little')).encode()
binv('resolved',res)
n=256
for nm,sl in (('q0',res[:64]),('q1',res[64:128]),('q2',res[128:192]),('q3',res[192:]),('h0',res[:128]),('h1',res[128:]),
              ('p49',res[:80]),('p50',res[80:184]),('p51',res[184:])):
    binv('resolved.'+nm,sl)
# token-text forms of the printed table
def lines_of(p):
    v=pages[p]
    if isinstance(v,dict):
        for k in ('lines','tokens','text'):
            if k in v: v=v[k]; break
    out=[]
    for ln in v:
        out.append(ln if isinstance(ln,str) else ' '.join(ln))
    return out
try:
    L49,L50,L51=lines_of('49'),lines_of('50'),lines_of('51')
    allL=L49+L50+L51
    forms={}
    for nm,LL in (('all',allL),('p49',L49),('p50',L50),('p51',L51)):
        forms[nm+':nl']='\n'.join(LL); forms[nm+':nl+']='\n'.join(LL)+'\n'; forms[nm+':crlf']='\r\n'.join(LL); forms[nm+':crlf+']='\r\n'.join(LL)+'\r\n'
        forms[nm+':sp']=' '.join(LL); forms[nm+':nosp']=''.join(LL).replace(' ','')
        forms[nm+':nosp_nl']='\n'.join(l.replace(' ','') for l in LL); forms[nm+':nosp_nl+']='\n'.join(l.replace(' ','') for l in LL)+'\n'
    forms['pages:nlnl']='\n\n'.join('\n'.join(x) for x in (L49,L50,L51)); forms['pages:nlnl+']=forms['pages:nlnl']+'\n'
    for k,v in forms.items():
        C['tokens.'+k]=v.encode(); C['tokens.'+k+':upper']=v.upper().encode(); C['tokens.'+k+':lower']=v.lower().encode()
    print('token lines:',len(allL),'first:',allL[0])
except Exception as e:
    print('token forms skipped:',repr(e), type(pages['49']), str(pages['49'])[:200])
hits=[];tested=0
for lab,b in C.items():
    for an,f in ALG.items():
        tested+=1
        h=f(b)
        if h==TARGET or h==TARGET[::-1] or bytes.fromhex(h)[::-1].hex()==TARGET: hits.append((lab,an,'FULL'))
        elif h[:16]==TARGET[:16] or h[-16:]==TARGET[-16:]: hits.append((lab,an,'PARTIAL16'))
# plant: prove the comparator fires
assert whirlpool_ref.whirlpool(res)==ALG['whirlpool'](C['resolved:raw'])
print('candidates',len(C),'algos',len(ALG),'tested',tested,'HITS',hits)
# also: does the OLD payload differ under these (sanity that the 3 bytes matter)
print('old!=new whirlpool:', whirlpool_ref.whirlpool(old)!=whirlpool_ref.whirlpool(res))
