# T4: word-length ORDER grammar (adjacent-length MI vs within-chapter shuffle) on unsolved LP2, with English + solved-LP controls.
# T5: is T7 (doublet-gap lag-1 autocorrelation) what PLAINTEXT-coupled rare events look like? English rare-rune / plaintext-doublet gap autocorr.
import sys,os,json,random,math,collections,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import load2
random.seed(5252)
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','data')  # R46-A1: repo-relative
TR=['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
DG={'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
SG={c:i for i,c in enumerate(TR) if len(c)==1}; SG.update({'K':5,'Q':5,'V':1,'Z':15})
def to_runes(word):
    w=word.upper(); out=[]; i=0
    while i<len(w):
        if w[i:i+3]=='ING': out.append(21); i+=3; continue
        if w[i:i+2] in DG: out.append(DG[w[i:i+2]]); i+=2; continue
        if w[i] in SG: out.append(SG[w[i]])
        i+=1
    return out
def load_text(fn):
    t=open(os.path.join(D,fn),encoding='utf8',errors='ignore').read()
    t=t[len(t)//20:]  # skip front matter
    words=[to_runes(w) for w in re.findall(r"[A-Za-z]+",t)]
    return [w for w in words if w]
