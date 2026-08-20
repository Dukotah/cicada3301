import json,urllib.request,urllib.parse,time,sys
API="https://uncovering-cicada.fandom.com/api.php"
def get(u):
    r=urllib.request.Request(u,headers={'User-Agent':'cicada-corpus-research/1.0'})
    return json.load(urllib.request.urlopen(r,timeout=45))
titles=[]
for ns in [0,1,2,3,4,6,10,14,110,500,502,828,1200,1201,2000]:
    cont=None
    while True:
        u=f"{API}?action=query&list=allpages&apnamespace={ns}&aplimit=500&format=json"
        if cont: u+=f"&apcontinue={urllib.parse.quote(cont)}"
        try: d=get(u)
        except Exception as e: print('ERR',ns,e); break
        ps=d.get('query',{}).get('allpages',[])
        titles+=[p['title'] for p in ps]
        c=d.get('continue',{}).get('apcontinue')
        if not c: break
        cont=c; time.sleep(0.3)
    print('ns',ns,len(titles))
open('_logs/wiki_titles.txt','w',newline='\n').write('\n'.join(sorted(set(titles))))
print('TOTAL',len(set(titles)))
