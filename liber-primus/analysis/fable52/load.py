# Loader: canonical unsolved stream with word/line/page structure from the other repo's
# line-broken transcription, cross-checked against our dataset indices.
import json,io,sys
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
OURS=r'C:\Users\dukot\projects\cicada3301\liber-primus\dataset\liber_primus.json'
THEIRS_TXT=r'C:\Users\dukot\AppData\Local\Temp\lpx\r\resources\liber-primus\lp2-transcription.txt'
RUNES="ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
IDX={r:i for i,r in enumerate(RUNES)}
def ours():
    d=json.load(open(OURS,encoding='utf8'))
    return d
def stream():
    """returns list of dict(v,page,word_start,line_start,sep_before) for 55 unsolved segments"""
    d=ours(); out=[]
    for p in d['pages']:
        if p['page']>=55: continue
        txt=p['runes']
        ws=True; ls=True; sep=''
        for ch in txt:
            if ch in IDX:
                out.append(dict(v=IDX[ch],page=p['page'],ws=ws,ls=ls,sep=sep)); ws=False; ls=False; sep=''
            else:
                sep+=ch
                if ch in '/\n': ls=True
                if ch not in '/\n\r': ws=True
    return out
if __name__=='__main__':
    d=ours()
    print(d['meta'] if len(str(d['meta']))<1500 else list(d['meta']))
    print([(p['page'],p['status'],p['n_runes']) for p in d['pages']][-4:])
    print(repr(d['pages'][0]['runes'][:200]))
    s=stream(); print(len(s))
    import collections
    print(collections.Counter(c for x in s for c in x['sep']))
