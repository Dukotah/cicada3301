import json,sys,collections,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
import load
TXT=load.THEIRS_TXT
def parse():
    raw=open(TXT,encoding='utf8').read()
    return raw
def stream():
    """Structured unsolved stream. Returns list of dicts: v,page,line,ws(word start),ls(line start),sep(str before)"""
    raw=parse(); canon=[x['v'] for x in load.stream()]
    out=[]; page=0; line=0; sep=''
    for ch in raw:
        if ch in load.IDX:
            out.append(dict(v=load.IDX[ch],page=page,line=line,sep=sep)); sep=''
        else:
            sep+=ch
            if ch=='\n': line+=1
            if ch in '%&$§': pass
    return out,canon
if __name__=='__main__':
    raw=parse()
    print(collections.Counter(c for c in raw if c not in load.IDX).most_common())
    out,canon=stream()
    print(len(out),len(canon),[x['v'] for x in out[:12956]]==canon)
    i=raw.find('%'); print(repr(raw[i-30:i+30]))
    for m in '&$§':
        i=raw.find(m); print(m, repr(raw[max(0,i-40):i+40]) if i>=0 else None)
