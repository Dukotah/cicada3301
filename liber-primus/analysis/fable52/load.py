# Loader: canonical unsolved stream with word/line/page structure from the other repo's
# line-broken transcription, cross-checked against our dataset indices.
import json,io,sys,os
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass
# R46-A1: repo-relative paths. THEIRS_TXT was an external clone (lpx\r\...\lp2-transcription.txt);
# data/krisyotam_runes.txt is rune-identical to it (13,136/13,136) and differs at exactly 2 separators
# ('-' in krisyotam vs '.' external, before unsolved runes 1886 and 9648). See analysis/round46/A1-hygiene/RESULTS.md.
HERE=os.path.dirname(os.path.abspath(__file__))
LPROOT=os.path.abspath(os.path.join(HERE,'..','..'))
OURS=os.path.join(LPROOT,'dataset','liber_primus.json')
THEIRS_TXT=os.path.join(LPROOT,'data','krisyotam_runes.txt')
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
