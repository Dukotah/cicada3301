#!/usr/bin/env python3
"""Extract encoder fingerprint from JPEG: marker order, DQT tables, Huffman table
class/id list, SOF component subsampling, APP segment identities. Cluster by signature."""
import sys, os, json, hashlib

def parse_jpeg(path):
    with open(path,'rb') as f:
        data = f.read()
    if data[:2] != b'\xff\xd8':
        return {'file':os.path.basename(path),'jpeg':False,'note':'not a JPEG (SOI missing)'}
    i = 2
    markers = []       # ordered list of marker names
    dqt_tables = {}    # id -> tuple of 64 ints (zigzag order as stored)
    dht = []           # list of (class,id)
    apps = []          # app segment identifiers
    sof = None
    n = len(data)
    while i < n-1:
        if data[i] != 0xFF:
            i += 1; continue
        # skip fill bytes
        marker = data[i+1]
        if marker in (0xD8,0xD9) or (0xD0<=marker<=0xD7) or marker==0x01:
            markers.append(f"{marker:02X}")
            i += 2
            if marker == 0xD9: break
            continue
        # segment with length
        if i+3 >= n: break
        seglen = (data[i+2]<<8)|data[i+3]
        seg = data[i+4:i+2+seglen]
        mname = f"{marker:02X}"
        if marker == 0xDB:  # DQT
            mname='DQT'
            p = 0
            while p < len(seg):
                pq_tq = seg[p]; p+=1
                pq = pq_tq>>4; tq = pq_tq&0xF
                if pq==0:
                    tbl = tuple(seg[p:p+64]); p+=64
                else:
                    tbl = tuple((seg[p+2*k]<<8)|seg[p+2*k+1] for k in range(64)); p+=128
                dqt_tables[tq]=tbl
        elif marker == 0xC4:  # DHT
            mname='DHT'
            p=0
            while p < len(seg):
                tc_th = seg[p]; p+=1
                tc = tc_th>>4; th=tc_th&0xF
                counts = seg[p:p+16]; p+=16
                total=sum(counts)
                p+=total
                dht.append((tc,th,total))
        elif marker in (0xC0,0xC1,0xC2):  # SOF0 baseline, SOF1, SOF2 progressive
            mname={0xC0:'SOF0',0xC1:'SOF1',0xC2:'SOF2'}[marker]
            prec=seg[0]; h=(seg[1]<<8)|seg[2]; w=(seg[3]<<8)|seg[4]; nc=seg[5]
            comps=[]
            for c in range(nc):
                cid=seg[6+3*c]; samp=seg[7+3*c]; qt=seg[8+3*c]
                comps.append((cid, samp>>4, samp&0xF, qt))
            sof={'type':mname,'prec':prec,'w':w,'h':h,'nc':nc,'comps':comps}
        elif 0xE0<=marker<=0xEF:  # APPn
            ident = seg.split(b'\x00',1)[0][:16]
            try: ids=ident.decode('latin-1')
            except: ids=repr(ident)
            mname=f'APP{marker-0xE0}'
            apps.append((mname, ids, seglen))
        elif marker == 0xFE:
            mname='COM'
            apps.append(('COM', seg[:32].decode('latin-1','replace'), seglen))
        elif marker == 0xDA:  # SOS -> scan data follows, stop structured parse
            markers.append('SOS')
            break
        markers.append(mname)
        i += 2+seglen
    # signature: quant tables hashed + subsampling + marker order + huffman layout
    dqt_sig = hashlib.md5(json.dumps({str(k):v for k,v in sorted(dqt_tables.items())}).encode()).hexdigest()[:12]
    sof_sig = None
    if sof:
        sof_sig = '|'.join(f"{c[0]}:{c[1]}x{c[2]}:q{c[3]}" for c in sof['comps'])
    return {
        'file':os.path.basename(path),'jpeg':True,
        'markers':'>'.join(markers),
        'dqt_ids':sorted(dqt_tables.keys()),
        'dqt_sig':dqt_sig,
        'dqt_tables':{str(k):list(v) for k,v in sorted(dqt_tables.items())},
        'dht':dht,
        'apps':apps,
        'sof':sof,
        'sof_sig':sof_sig,
    }

if __name__=='__main__':
    out=[]
    for p in sys.argv[1:]:
        try:
            out.append(parse_jpeg(p))
        except Exception as e:
            out.append({'file':os.path.basename(p),'error':str(e)})
    json.dump(out, open('fingerprints.json','w'), indent=1)
    # print compact summary
    for r in out:
        if not r.get('jpeg'):
            print(f"{r['file']}: NOT-JPEG ({r.get('note') or r.get('error')})"); continue
        print(f"{r['file']}: dqt_sig={r['dqt_sig']} ids={r['dqt_ids']} sof={r['sof_sig']} apps={[a[0]+':'+a[1] for a in r['apps']]}")
