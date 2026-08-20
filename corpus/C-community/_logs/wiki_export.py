import io,sys,json,time,hashlib,datetime,urllib.request,urllib.parse
B='C:/Users/dukot/projects/cicada3301/corpus/C-community/'
API='https://uncovering-cicada.fandom.com/wiki/Special:Export'
titles=[l.rstrip('\n') for l in io.open(B+'_logs/wiki_titles.txt',encoding='utf-8',errors='replace') if l.strip()]
# skip File: (media desc pages, low value here) but keep everything else
keep=[t for t in titles if not t.startswith('File:')]
hist = sys.argv[1]=='hist' if len(sys.argv)>1 else False
start=int(sys.argv[2]); count=int(sys.argv[3])
batch=25
man=io.open(B+'_logs/manifest.jsonl','a',encoding='utf-8',newline='\n')
for i in range(start,min(start+count,len(keep)),batch):
    chunk=keep[i:i+batch]
    out=f"wikis/uncovering-cicada/export_{'hist' if hist else 'cur'}_{i:05d}.xml"
    import os
    if os.path.exists(B+out) and os.path.getsize(B+out)>500: print('SKIP',out); continue
    data=urllib.parse.urlencode({'pages':'\n'.join(chunk),'curonly':'0' if hist else '1','wpDownload':'1','action':'submit'}).encode()
    req=urllib.request.Request(API,data=data,headers={'User-Agent':'cicada-corpus-research/1.0','Content-Type':'application/x-www-form-urlencoded'})
    ts=datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    try:
        r=urllib.request.urlopen(req,timeout=90); body=r.read(); code=r.status
    except Exception as e:
        print('ERR',i,e); continue
    os.makedirs(os.path.dirname(B+out),exist_ok=True)
    io.open(B+out,'wb').write(body)
    man.write(json.dumps({'path':out,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),
        'source_url':API+' (POST pages='+str(len(chunk))+' titles, curonly='+('0' if hist else '1')+')',
        'retrieved_utc':ts,'http_status':code,'method':'API',
        'notes':'Uncovering Cicada Wiki (Fandom) Special:Export, '+('FULL HISTORY' if hist else 'current only')+'; titles '+chunk[0]+' .. '+chunk[-1]})+'\n')
    man.flush()
    print('OK',out,len(body))
    time.sleep(0.5)
print('TOTAL_TITLES',len(keep))
