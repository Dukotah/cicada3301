import urllib.request,hashlib,os,json,io,sys,time,datetime
D=os.path.dirname(os.path.abspath(__file__))
MAN=os.path.join(D,'meta','downloads.json')
recs=json.load(io.open(MAN,encoding='utf-8')) if os.path.exists(MAN) else {}
def fetch(url,relpath,meta):
    p=os.path.join(D,relpath)
    if relpath in recs and os.path.exists(p):
        print('SKIP',relpath,flush=True); return
    os.makedirs(os.path.dirname(p),exist_ok=True)
    try:
        rq=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; cicada3301-corpus-research/1.0; +mailto:dukotah@gmail.com)'})
        b=urllib.request.urlopen(rq,timeout=70).read()
    except Exception as e:
        print('FAIL',relpath,type(e).__name__,str(e)[:70],flush=True)
        recs.setdefault('_failures',{})[relpath]={'url':url,'error':type(e).__name__+': '+str(e)[:150],'utc':datetime.datetime.utcnow().isoformat()+'Z'}
        json.dump(recs,io.open(MAN,'w',encoding='utf-8'),indent=1,ensure_ascii=False); return
    if len(b)<3000 or (relpath.endswith('.pdf') and not b[:5].startswith(b'%PDF')):
        print('BAD',relpath,len(b),b[:40],flush=True)
        recs.setdefault('_failures',{})[relpath]={'url':url,'error':'not-a-pdf-or-too-small bytes=%d'%len(b),'utc':datetime.datetime.utcnow().isoformat()+'Z'}
        json.dump(recs,io.open(MAN,'w',encoding='utf-8'),indent=1,ensure_ascii=False); return
    open(p,'wb').write(b)
    r=dict(meta); r.update(path=relpath.replace(chr(92),'/'),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),
        source_url=url,retrieved_utc=datetime.datetime.utcnow().replace(microsecond=0).isoformat()+'Z')
    recs[relpath]=r
    json.dump(recs,io.open(MAN,'w',encoding='utf-8'),indent=1,ensure_ascii=False)
    print('OK',len(b),relpath,flush=True)
if __name__=='__main__':
    jobs=json.load(io.open(sys.argv[1],encoding='utf-8'))
    for j in jobs:
        fetch(j['url'],j['path'],j['meta']); time.sleep(1.5)
