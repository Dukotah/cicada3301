# Minimal baseline-JPEG entropy decoder -> quantized DCT coefficient LSB stream (OutGuess-class)
import glob, re, struct, sys
import numpy as np

KW=re.compile(rb'(BEGIN PGP|PGP MESSAGE|cipher|gematria|primus|divinit|sacred|prime|onion|3301|cicada|instar|circumf|magic|William|Blake|welcome|wisdom|the key|KEY IS)',re.I)
WORDY=re.compile(rb'(the |and |key |cipher|prime|cicada|liber|sacred|divin| is | of )',re.I)
def runs(b,n=8): return re.findall(rb'[ -~]{%d,}'%n,b)

class BitReader:
    def __init__(self,data): self.d=data; self.i=0; self.bit=0
    def read(self):
        if self.i>=len(self.d): raise EOFError
        b=(self.d[self.i]>>(7-self.bit))&1
        self.bit+=1
        if self.bit==8:
            self.bit=0; self.i+=1
            # skip stuffed 0x00 after 0xFF
            if self.i<len(self.d) and self.d[self.i-1]==0xFF and self.d[self.i]==0x00:
                self.i+=1
        return b
    def recv(self,n):
        v=0
        for _ in range(n): v=(v<<1)|self.read()
        return v

def build_huff(counts, symbols):
    # counts: 16 ints. returns dict {(length,code):symbol}
    codes={}; code=0; k=0
    for l in range(1,17):
        for _ in range(counts[l-1]):
            codes[(l,code)]=symbols[k]; k+=1; code+=1
        code<<=1
    return codes

def huff_decode(br,table):
    code=0
    for l in range(1,17):
        code=(code<<1)|br.read()
        if (l,code) in table: return table[(l,code)]
    raise ValueError("bad huff")

def extend(v,t):
    return v if v>= (1<<(t-1)) else v-(1<<t)+1

def decode_jpeg_coeffs(path,maxblocks=200000):
    d=open(path,'rb').read()
    i=2; qt={}; huff_dc={}; huff_ac={}
    comps=[]; restart=0; W=H=0
    while i<len(d):
        if d[i]!=0xFF: i+=1; continue
        m=d[i+1]; 
        if m==0xD9: break
        if m in (0xD8,0x01) or 0xD0<=m<=0xD7: i+=2; continue
        L=(d[i+2]<<8)|d[i+3]; seg=d[i+4:i+2+L]
        if m==0xC0 or m==0xC2:  # SOF0 baseline / SOF2 progressive
            prog = (m==0xC2)
            H=(seg[1]<<8)|seg[2]; W=(seg[3]<<8)|seg[4]; nc=seg[5]
            comps=[]
            for c in range(nc):
                cid=seg[6+c*3]; hv=seg[7+c*3]; tq=seg[8+c*3]
                comps.append({'id':cid,'h':hv>>4,'v':hv&15,'tq':tq})
            if prog: return None  # progressive: skip (too complex)
        elif m==0xC4:
            p=0
            while p<len(seg):
                tc_th=seg[p]; tc=tc_th>>4; th=tc_th&15
                counts=list(seg[p+1:p+17]); ns=sum(counts)
                syms=list(seg[p+17:p+17+ns])
                tab=build_huff(counts,syms)
                (huff_dc if tc==0 else huff_ac)[th]=tab
                p+=17+ns
        elif m==0xDB:
            p=0
            while p<len(seg):
                pq_tq=seg[p]; tq=pq_tq&15; prec=pq_tq>>4
                p+=1
                if prec==0: qt[tq]=list(seg[p:p+64]); p+=64
                else: p+=128
        elif m==0xDD:
            restart=(seg[0]<<8)|seg[1]
        elif m==0xDA:
            ns=seg[0]; scomp=[]
            for s in range(ns):
                cs=seg[1+s*2]; td_ta=seg[2+s*2]
                scomp.append((cs,td_ta>>4,td_ta&15))
            # scan data starts after this segment
            sos_end=i+2+L
            j=sos_end
            while j<len(d)-1:
                if d[j]==0xFF and d[j+1]!=0 and not(0xD0<=d[j+1]<=0xD7): break
                j+=1
            scan=d[sos_end:j]
            # decode MCUs (baseline interleaved)
            br=BitReader(scan)
            hmax=max(c['h'] for c in comps); vmax=max(c['v'] for c in comps)
            mcux=(W+8*hmax-1)//(8*hmax); mcuy=(H+8*vmax-1)//(8*vmax)
            pred={c['id']:0 for c in comps}
            coeffs=[]  # list of all coefficient values in decode order
            cnt=0
            try:
                for my in range(mcuy):
                    for mx in range(mcux):
                        for c in comps:
                            cid=c['id']
                            td=[x for x in scomp if x[0]==cid][0][1]
                            ta=[x for x in scomp if x[0]==cid][0][2]
                            for by in range(c['v']):
                                for bx in range(c['h']):
                                    blk=[0]*64
                                    t=huff_decode(br,huff_dc[td])
                                    diff=extend(br.recv(t),t) if t else 0
                                    pred[cid]+=diff; blk[0]=pred[cid]
                                    k=1
                                    while k<64:
                                        rs=huff_decode(br,huff_ac[ta])
                                        r=rs>>4; s=rs&15
                                        if s==0:
                                            if r==15: k+=16; continue
                                            else: break
                                        k+=r
                                        if k>=64: break
                                        blk[k]=extend(br.recv(s),s); k+=1
                                    coeffs.extend(blk)
                                    cnt+=1
                                    if cnt>=maxblocks: raise StopIteration
            except (StopIteration,EOFError,ValueError):
                pass
            return np.array(coeffs,dtype=np.int32)
        i=i+2+L
    return None

def lsb_stream(coeffs):
    # OutGuess: skip 0 and 1 coefficients (DC and 0s carry no payload in classic), read LSB of nonzero AC
    nz=coeffs[(coeffs!=0)&(coeffs!=1)&(coeffs!=-1)] if False else coeffs[coeffs!=0]
    bits=(np.abs(nz)&1).astype(np.uint8)
    m=(len(bits)//8)*8
    return np.packbits(bits[:m].reshape(-1,8),axis=1).reshape(-1).tobytes()

def lsb_all(coeffs):
    bits=(np.abs(coeffs)&1).astype(np.uint8)
    m=(len(bits)//8)*8
    return np.packbits(bits[:m].reshape(-1,8),axis=1).reshape(-1).tobytes()

files=sorted(glob.glob("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/p*.jpg"))
files+=sorted(glob.glob("/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014/images/liber_primus_pages/*.jpg"))
print(f"# {len(files)} files for DCT-coeff LSB")
hits=0; ok=0; prog=0; fail=0
for p in files:
    try:
        co=decode_jpeg_coeffs(p)
    except Exception as e:
        co=None
    if co is None: prog+=1; continue
    ok+=1
    for label,by in [('nz',lsb_stream(co)),('all',lsb_all(co))]:
        for stream in [by, bytes((~x)&0xFF for x in by[:8192])]:
            if KW.search(stream) or any(WORDY.search(r) for r in runs(stream,8)):
                ww=[r[:60] for r in runs(stream,8) if WORDY.search(r)][:5]
                print("DCT-HIT",p.split('/')[-1],label,ww,KW.findall(stream)[:3])
                hits+=1
print(f"decoded={ok} skipped(prog/fail)={prog} dct_hits={hits}")
