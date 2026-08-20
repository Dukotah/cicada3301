import json,io,re,collections,glob,os,datetime
base='liber-primus/analysis/round10/L6-archives/fetched/reddit/'
stats={}
irc=[]
urlc=collections.Counter()
for fn in sorted(os.listdir(base)):
    p=base+fn
    if os.path.getsize(p)==0:
        stats[fn]={'records':0,'note':'EMPTY FILE'}; continue
    n=0; mn=None; mx=None
    for line in io.open(p,encoding='utf-8',errors='replace'):
        line=line.strip()
        if not line: continue
        try: d=json.loads(line)
        except: continue
        n+=1
        c=d.get('created_utc')
        if isinstance(c,str):
            try: c=int(c)
            except: c=None
        if c:
            mn=c if mn is None or c<mn else mn
            mx=c if mx is None or c>mx else mx
        blob=(d.get('selftext') or '')+' '+(d.get('body') or '')+' '+(d.get('url') or '')+' '+(d.get('title') or '')
        for u in re.findall(r'https?://[^\s\)\]\>"\']+',blob):
            urlc[u]+=1
        if re.search(r'\birc\b|freenode|#cicadasolvers|#33012013|3301hackers|botbot|echelog|glob\.uno|irclog',blob,re.I):
            irc.append({'file':fn,'id':d.get('id'),'created_utc':c,'author':d.get('author'),
                        'permalink':d.get('permalink'),'link_id':d.get('link_id'),
                        'text':blob[:1500]})
    stats[fn]={'records':n,'created_utc_min':mn,'created_utc_max':mx,
               'min_iso':datetime.datetime.utcfromtimestamp(mn).isoformat()+'Z' if mn else None,
               'max_iso':datetime.datetime.utcfromtimestamp(mx).isoformat()+'Z' if mx else None}
o='corpus/C-community/reddit/'
json.dump(stats,io.open(o+'HELD_DUMPS_STATS.json','w',encoding='utf-8'),indent=2)
io.open(o+'irc_mentions_in_reddit.jsonl','w',encoding='utf-8',newline='\n').write('\n'.join(json.dumps(x,ensure_ascii=False) for x in irc))
with io.open('corpus/C-community/_logs/reddit_urls.tsv','w',encoding='utf-8',newline='\n') as f:
    for u,c in urlc.most_common(): f.write(f"{c}\t{u}\n")
print(json.dumps(stats,indent=2))
print('irc-mentioning records:',len(irc))
print('distinct urls:',len(urlc))
