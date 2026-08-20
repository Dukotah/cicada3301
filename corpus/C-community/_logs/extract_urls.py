import json,io,glob,re,sys,collections
txt=''
for f in sys.argv[1:]:
    for g in glob.glob(f):
        txt+=io.open(g,encoding='utf-8',errors='replace').read()
txt=txt.replace('\/','/')
urls=set(re.findall(r'https?://[A-Za-z0-9\-\._~:/\?#\[\]@!\$&\'\(\)\*\+,;=%]+',txt))
c=collections.Counter(re.sub(r'^https?://','',u).split('/')[0] for u in urls)
for k,v in c.most_common(50): print(v,k)
open('_logs/found_urls.txt','a',newline='\n').write('\n'.join(sorted(urls))+'\n')
