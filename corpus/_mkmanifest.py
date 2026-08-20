import os,sys,json,hashlib,time,collections
LANE=sys.argv[1]
ROOT=os.path.abspath(LANE)
SKIP_DIRS={'__pycache__','.git'}
BS=chr(92)
def rel_norm(p): return os.path.normpath(p).replace(BS,'/')
prov={}
for pf in ('manifest.jsonl','bytediff_manifest.jsonl','meta/downloads.json','_logs/manifest.jsonl','_logs/provenance.jsonl','_logs/fetchlog.jsonl'):
    p=os.path.join(ROOT,pf)
    if not os.path.exists(p): continue
    try:
        if p.endswith('.jsonl'):
            for l in open(p,encoding='utf-8'):
                l=l.strip()
                if not l: continue
                try: r=json.loads(l)
                except Exception: continue
                if isinstance(r,dict) and r.get('path'): prov[rel_norm(r['path'])]=r
        else:
            data=json.load(open(p,encoding='utf-8'))
            it=data.values() if isinstance(data,dict) else data
            for r in it:
                if isinstance(r,dict) and r.get('path'): prov[rel_norm(r['path'])]=r
    except Exception as e:
        print('prov load fail',pf,e)
files=[];tot=0
byext=collections.Counter();bydir=collections.Counter()
for dp,dn,fn in os.walk(ROOT):
    dn[:]=[d for d in dn if d not in SKIP_DIRS]
    for f in fn:
        full=os.path.join(dp,f)
        rel=os.path.relpath(full,ROOT).replace(BS,'/')
        if rel=='MANIFEST.json': continue
        try: st=os.stat(full)
        except Exception: continue
        h=hashlib.sha256()
        try:
            with open(full,'rb') as fh:
                for chunk in iter(lambda: fh.read(1<<20), b''): h.update(chunk)
        except Exception: continue
        ext=os.path.splitext(f)[1].lower() or '(none)'
        byext[ext]+=1
        bydir[rel.split('/')[0] if '/' in rel else '(lane root)']+=1
        tot+=st.st_size
        row={'path':rel,'bytes':st.st_size,'sha256':h.hexdigest(),
             'mtime_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(st.st_mtime))}
        pr=prov.get(rel) or prov.get(LANE+'/'+rel)
        if pr:
            for k in ('original_url','archive_url','source_url','capture_timestamp','retrieved_utc','http_status','cdx_digest','target','group','content_type','sha256_at_fetch'):
                if k in pr and pr[k] not in (None,''): row[k if k!='sha256_at_fetch' else 'sha256_at_fetch']=pr[k]
            row['provenance']='recorded'
        else:
            row['provenance']='UNRECORDED'
        files.append(row)
files.sort(key=lambda r:r['path'])
out={'lane':LANE,'generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
     'hash_algorithm':'sha256 over exact file bytes as held on disk',
     'file_count':len(files),'total_bytes':tot,
     'files_with_recorded_provenance':sum(1 for f in files if f['provenance']=='recorded'),
     'files_without_recorded_provenance':sum(1 for f in files if f['provenance']!='recorded'),
     'by_extension':dict(byext.most_common()),'by_top_dir':dict(bydir.most_common()),
     'files':files}
json.dump(out,open(os.path.join(ROOT,'MANIFEST.json'),'w',encoding='utf-8'),indent=1)
print(LANE,'files',len(files),'bytes',tot,'prov',out['files_with_recorded_provenance'],'noprov',out['files_without_recorded_provenance'])
