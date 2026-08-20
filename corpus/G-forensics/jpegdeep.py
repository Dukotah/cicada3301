import struct, hashlib, json, os, sys
def parse_jpeg(path):
    d=open(path,'rb').read()
    out={"size":len(d),"segments":[],"dqt":[],"icc":None,"appn":[],"com":[],"trailing":0,
         "trailing_sha256":None,"sof":None,"dri":None,"huff_count":0,"eoi_offset":None}
    if not d.startswith(b'\xff\xd8'): out["error"]="not JPEG"; return out
    i=2; icc_chunks={}
    while i < len(d)-1:
        if d[i]!=0xFF: 
            i+=1; continue
        m=d[i+1]
        if m in (0xD8,0x01) or 0xD0<=m<=0xD7: i+=2; continue
        if m==0xD9:
            out["eoi_offset"]=i; i+=2; break
        if i+4>len(d): break
        L=struct.unpack('>H', d[i+2:i+4])[0]
        seg=d[i+4:i+2+L]
        name=f"FF{m:02X}"
        out["segments"].append({"marker":name,"offset":i,"length":L})
        if m==0xDB:  # DQT
            p=0
            while p < len(seg):
                pq=seg[p]>>4; tq=seg[p]&0xF; p+=1
                n=64*(2 if pq else 1)
                tbl=seg[p:p+n]; p+=n
                vals=list(struct.unpack('>64H',tbl)) if pq else list(tbl)
                out["dqt"].append({"tq":tq,"prec":pq,"sha1":hashlib.sha1(tbl).hexdigest(),"vals":vals})
        elif m==0xC4: out["huff_count"]+=1
        elif m==0xDD: out["dri"]=struct.unpack('>H',seg[:2])[0]
        elif 0xC0<=m<=0xCF and m not in (0xC4,0xC8,0xCC):
            out["sof"]={"marker":name,"prec":seg[0],"h":struct.unpack('>H',seg[1:3])[0],
                        "w":struct.unpack('>H',seg[3:5])[0],"ncomp":seg[5]}
        elif m==0xFE: out["com"].append(seg.decode('latin-1'))
        elif 0xE0<=m<=0xEF:
            ident=seg.split(b'\x00',1)[0][:32].decode('latin-1','replace')
            rec={"marker":name,"ident":ident,"len":L,"sha1":hashlib.sha1(seg).hexdigest()}
            if ident=='ICC_PROFILE' and len(seg)>14:
                sn=seg[12]; tot=seg[13]; icc_chunks[sn]=seg[14:]
                rec["icc_chunk"]=[sn,tot]
            elif ident=='JFIF' and len(seg)>=14:
                rec["jfif"]={"ver":f"{seg[5]}.{seg[6]:02d}","units":seg[7],
                             "xd":struct.unpack('>H',seg[8:10])[0],"yd":struct.unpack('>H',seg[10:12])[0],
                             "thumb":[seg[12],seg[13]]}
            else:
                rec["head_hex"]=seg[:48].hex()
            out["appn"].append(rec)
        if m==0xDA:  # SOS -> scan to EOI
            j=i+2+L
            while j<len(d)-1:
                if d[j]==0xFF and d[j+1]==0xD9: break
                j+=1
            out["eoi_offset"]=j
            out["trailing"]=len(d)-(j+2)
            if out["trailing"]>0:
                t=d[j+2:]
                out["trailing_sha256"]=hashlib.sha256(t).hexdigest()
                out["trailing_head_hex"]=t[:64].hex()
            break
        i=i+2+L
    if icc_chunks:
        blob=b''.join(icc_chunks[k] for k in sorted(icc_chunks))
        out["icc"]=parse_icc(blob)
    return out

def parse_icc(b):
    r={"len":len(b),"sha256":hashlib.sha256(b).hexdigest()}
    if len(b)<132: r["error"]="short"; return r
    r["size_field"]=struct.unpack('>I',b[0:4])[0]
    r["cmm"]=b[4:8].decode('latin-1'); r["version"]=b[8:12].hex()
    r["class"]=b[12:16].decode('latin-1'); r["colorspace"]=b[16:20].decode('latin-1')
    r["pcs"]=b[20:24].decode('latin-1')
    y,mo,da,ho,mi,se=struct.unpack('>6H', b[24:36])
    r["created"]=f"{y:04d}-{mo:02d}-{da:02d}T{ho:02d}:{mi:02d}:{se:02d}Z"
    r["sig"]=b[36:40].decode('latin-1'); r["platform"]=b[40:44].decode('latin-1')
    r["flags"]=b[44:48].hex(); r["manufacturer"]=b[48:52].decode('latin-1')
    r["model"]=b[52:56].decode('latin-1'); r["rendering_intent"]=struct.unpack('>I',b[64:68])[0]
    r["creator"]=b[80:84].decode('latin-1')
    r["profile_id"]=b[84:100].hex()
    r["reserved_bytes_100_128"]=b[100:128].hex()
    n=struct.unpack('>I',b[128:132])[0]
    r["tag_count"]=n
    tags=[]; consumed=132+12*n
    for i in range(n):
        o=132+12*i
        if o+12>len(b): break
        sig=b[o:o+4].decode('latin-1'); off,sz=struct.unpack('>II', b[o+4:o+12])
        t={"sig":sig,"off":off,"size":sz}
        data=b[off:off+sz] if off+sz<=len(b) else b''
        t["sha1"]=hashlib.sha1(data).hexdigest()
        if data[:4] in (b'desc',b'text',b'mluc',b'cprt'):
            try: t["text"]=data[8:sz].decode('latin-1','replace').strip('\x00')[:200]
            except Exception: pass
        consumed=max(consumed, off+sz)
        tags.append(t)
    r["tags"]=tags
    # gap/slack bytes inside profile not covered by any tag = candidate hiding place
    covered=bytearray(len(b))
    for i in range(132+12*n): covered[i]=1
    for t in tags:
        for i in range(t["off"], min(t["off"]+t["size"], len(b))): covered[i]=1
    gaps=[]
    st=None
    for i in range(len(b)):
        if not covered[i]:
            if st is None: st=i
        else:
            if st is not None: gaps.append((st,i-st)); st=None
    if st is not None: gaps.append((st,len(b)-st))
    r["uncovered_gaps"]=[{"off":o,"len":l,"hex":b[o:o+min(l,32)].hex()} for o,l in gaps if l>0]
    r["trailing_after_size_field"]=len(b)-r["size_field"] if r["size_field"]<=len(b) else None
    return r
if __name__=="__main__":
    print(json.dumps(parse_jpeg(sys.argv[1]), indent=1)[:4000])
