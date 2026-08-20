import io,sys,os,json,time,hashlib,datetime,urllib.request,urllib.parse
B='C:/Users/dukot/projects/cicada3301/corpus/C-community/'
API='https://uncovering-cicada.fandom.com/api.php'
titles=[l.rstrip('\n') for l in io.open(B+'_logs/wiki_titles.txt',encoding='utf-8',errors='replace') if l.strip()]
keep=[t for t in titles if not t.startswith('File:')]
start=int(sys.argv[1]); count=int(sys.argv[2]); batch=20
man=io.open(B+'_logs/manifest.jsonl','a',encoding='utf-8',newline='\n')
for i in range(start,min(start+count,len(keep)),batch):
    chunk=keep[i:i+batch]
    out=f"wikis/uncovering-cicada/export_cur_{i:05d}.xml"
    if os.path.exists(B+out) and os.path.getsize(B+out)>500: print('SKIP',out); continue
    q={'action':'query','export':'1','exportnowrap':'1','format':'json','titles':'|'.join(chunk)}
    u=API+'?'+urllib.parse.urlencode(q)
    req=urllib.request.Request(u,headers={'User-Agent':'cicada-corpus-research/1.0'})
    ts=datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    try:
        r=urllib.request.urlopen(req,timeout=60); body=r.read(); code=r.status
    except Exception as e:
        print('ERR',i,e); time.sleep(2); continue
    os.makedirs(os.path.dirname(B+out),exist_ok=True)
    io.open(B+out,'wb').write(body)
    man.write(json.dumps({'path':out,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),
        'source_url':u,'retrieved_utc':ts,'http_status':code,'method':'API',
        'notes':'Uncovering Cicada Wiki (Fandom) api.php action=query&export (current revision wikitext), '+str(len(chunk))+' titles'},ensure_ascii=False)+'\n')
    man.flush(); print('OK',out,len(body)); time.sleep(0.2)
print('TOTAL',len(keep))
