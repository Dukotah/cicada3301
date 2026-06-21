#!/usr/bin/env python3
"""Pure-python pgpdump-style OpenPGP packet parser for Cicada 3301 forensics."""
import base64, sys, struct, datetime, glob, os, hashlib

PKT_NAMES = {
    1:"PKESK",2:"Signature",3:"SKESK",4:"OnePassSig",5:"SecretKey",
    6:"PublicKey",7:"SecretSubkey",8:"CompressedData",9:"SymEncData",
    10:"Marker",11:"LiteralData",12:"Trust",13:"UserID",14:"PublicSubkey",
    17:"UserAttr",18:"SymEncIntegrity",19:"MDC",
}
PUBKEY_ALGO={1:"RSA(E+S)",2:"RSA-E",3:"RSA-S",16:"ElGamal",17:"DSA",18:"ECDH",19:"ECDSA",22:"EdDSA"}
HASH_ALGO={1:"MD5",2:"SHA1",3:"RIPEMD160",8:"SHA256",9:"SHA384",10:"SHA512",11:"SHA224"}
SYM_ALGO={0:"plain",1:"IDEA",2:"3DES",3:"CAST5",4:"Blowfish",7:"AES128",8:"AES192",9:"AES256",10:"Twofish"}
COMP_ALGO={0:"uncompressed",1:"ZIP",2:"ZLIB",3:"BZIP2"}
SIGTYPE={0x00:"binary",0x01:"text",0x10:"generic-cert",0x13:"positive-cert",0x18:"subkey-binding",0x19:"primary-binding",0x1F:"directkey",0x20:"keyrevoke",0x28:"subkeyrevoke"}
SUBPKT={2:"sig-creation-time",3:"sig-expiry",9:"key-expiry",11:"pref-sym",16:"issuer-keyid",20:"notation",21:"pref-hash",22:"pref-comp",23:"keyserver-prefs",25:"primary-uid",26:"policy-uri",27:"key-flags",30:"features",33:"issuer-fpr"}

def unarmor(text):
    lines=text.splitlines()
    out=[];inblock=False
    for ln in lines:
        if ln.startswith("-----BEGIN"):
            inblock=True;out=[];continue
        if ln.startswith("-----END"):
            break
        if inblock:
            if ln.startswith("=") or ln.strip()=="" or ":" in ln.split(" ")[0]:
                # blank line ends headers; '=' starts CRC
                if ln.startswith("="): break
                if ln.strip()=="": out=[];continue  # reset after header blank? no
                continue
            out.append(ln.strip())
    # simpler: collect base64 region between blank line and crc
    return None

def get_b64(text, want_sig=False):
    """Extract base64 from the relevant armor block.
    Returns (bytes, version_header). If want_sig, prefer the SIGNATURE block."""
    lines=text.splitlines()
    blocks=[];cur=None;version=None
    for ln in lines:
        if "-----BEGIN" in ln:
            cur={"kind":ln,"body":[],"headers":{},"past":False,"version":None}
        elif "-----END" in ln:
            if cur: blocks.append(cur);cur=None
        elif cur is not None:
            if not cur["past"]:
                if ln.strip()=="":
                    cur["past"]=True
                elif ":" in ln:
                    k,_,v=ln.partition(":")
                    cur["headers"][k.strip()]=v.strip()
                    if k.strip()=="Version": cur["version"]=v.strip()
                else:
                    cur["past"]=True
                    if ln.strip(): cur["body"].append(ln.strip())
            else:
                if ln.startswith("="):
                    continue
                if ln.strip(): cur["body"].append(ln.strip())
    # choose block
    chosen=None
    for b in blocks:
        if "SIGNATURE" in b["kind"] and "SIGNED MESSAGE" not in b["kind"]:
            chosen=b
        if not want_sig and ("PUBLIC KEY" in b["kind"] or "MESSAGE" in b["kind"]) and "SIGNED MESSAGE" not in b["kind"]:
            chosen=b;break
    if chosen is None:
        for b in blocks:
            if b["body"]: chosen=b;break
    if chosen is None: return b"", None
    return base64.b64decode("".join(chosen["body"])), chosen.get("version")

def mpi_len(data,off):
    bits=(data[off]<<8)|data[off+1]
    nbytes=(bits+7)//8
    return off+2+nbytes, nbytes, bits

def read_packets(data):
    pkts=[];i=0;n=len(data)
    while i<n:
        tag=data[i]
        if not (tag&0x80):
            break
        newfmt=bool(tag&0x40)
        if newfmt:
            ptype=tag&0x3f
            i+=1
            l1=data[i]
            if l1<192:
                length=l1;i+=1
            elif l1<224:
                length=((l1-192)<<8)+data[i+1]+192;i+=2
            elif l1==255:
                length=struct.unpack(">I",data[i+1:i+5])[0];i+=5
            else:
                length=1<<(l1&0x1f);i+=1
        else:
            ptype=(tag>>2)&0x0f
            ltype=tag&0x03
            i+=1
            if ltype==0: length=data[i];i+=1
            elif ltype==1: length=struct.unpack(">H",data[i:i+2])[0];i+=2
            elif ltype==2: length=struct.unpack(">I",data[i:i+4])[0];i+=4
            else: length=n-i
        body=data[i:i+length]
        pkts.append((ptype,newfmt,body))
        i+=length
    return pkts

def ts(t): return datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S UTC")

def parse_pubkey(body):
    ver=body[0];out={"version":ver}
    if ver==4:
        ctime=struct.unpack(">I",body[1:5])[0]
        algo=body[5]
        out["creation"]=ts(ctime);out["creation_raw"]=ctime
        out["algo"]=PUBKEY_ALGO.get(algo,algo)
        off=6
        if algo in (1,2,3):
            off,nbytes,bits=mpi_len(body,off)
            out["n_bits"]=bits
            off,ebytes,ebits=mpi_len(body,off)
            out["e_bits"]=ebits
            out["e_bytes"]=body[off-ebytes:off]
        # v4 fingerprint
        fpr_data=b"\x99"+struct.pack(">H",len(body))+body
        out["fingerprint"]=hashlib.sha1(fpr_data).hexdigest().upper()
        out["keyid"]=out["fingerprint"][-16:]
    return out

def parse_signature(body):
    ver=body[0];out={"version":ver}
    if ver==4:
        out["sigtype"]=SIGTYPE.get(body[1],hex(body[1]))
        out["pubalgo"]=PUBKEY_ALGO.get(body[2],body[2])
        out["hashalgo"]=HASH_ALGO.get(body[3],body[3])
        off=4
        hashed_len=struct.unpack(">H",body[off:off+2])[0];off+=2
        hashed=body[off:off+hashed_len];off+=hashed_len
        out["hashed_subpkts"]=parse_subpkts(hashed)
        unh_len=struct.unpack(">H",body[off:off+2])[0];off+=2
        unh=body[off:off+unh_len];off+=unh_len
        out["unhashed_subpkts"]=parse_subpkts(unh)
        out["left16"]=body[off:off+2].hex();off+=2
    elif ver==3:
        out["hashed_len"]=body[1]
        out["sigtype"]=SIGTYPE.get(body[2],hex(body[2]))
        ctime=struct.unpack(">I",body[3:7])[0]
        out["creation"]=ts(ctime)
        out["keyid"]=body[7:15].hex().upper()
        out["pubalgo"]=PUBKEY_ALGO.get(body[15],body[15])
        out["hashalgo"]=HASH_ALGO.get(body[16],body[16])
    return out

def parse_subpkts(data):
    out=[];i=0;n=len(data)
    while i<n:
        l1=data[i]
        if l1<192: length=l1;i+=1
        elif l1<255: length=((l1-192)<<8)+data[i+1]+192;i+=2
        else: length=struct.unpack(">I",data[i+1:i+5])[0];i+=5
        stype=data[i];sbody=data[i+1:i+length]
        name=SUBPKT.get(stype&0x7f,stype&0x7f)
        crit=bool(stype&0x80)
        val=None
        t=stype&0x7f
        if t==2 or t==3 or t==9:
            val=ts(struct.unpack(">I",sbody[:4])[0])
        elif t==16:
            val=sbody.hex().upper()
        elif t==33:
            val=sbody.hex().upper()
        elif t in (11,21,22):
            val=list(sbody)
        elif t==27:
            val="flags="+sbody.hex()
        else:
            val=sbody.hex()
        out.append({"type":name,"crit":crit,"val":val})
        i+=length
    return out

def parse_userid(body):
    return body.decode("utf-8","replace")

def analyze(path):
    with open(path) as f: text=f.read()
    is_clearsign="SIGNED MESSAGE" in text
    try:
        data,version=get_b64(text, want_sig=is_clearsign)
    except Exception as e:
        return {"file":os.path.basename(path),"error":str(e)}
    pkts=read_packets(data)
    res={"file":os.path.basename(path),"armor_version":version,"clearsigned":is_clearsign,"packets":[]}
    for ptype,newfmt,body in pkts:
        p={"tag":ptype,"name":PKT_NAMES.get(ptype,ptype),"newfmt":newfmt,"len":len(body)}
        if ptype in (6,14):
            p.update(parse_pubkey(body))
        elif ptype==2:
            p.update(parse_signature(body))
        elif ptype==13:
            p["uid"]=parse_userid(body)
        elif ptype==8:
            p["comp_algo"]=COMP_ALGO.get(body[0],body[0]) if body else None
        elif ptype==11:
            if body:
                fmt=chr(body[0]);fnlen=body[1]
                fn=body[2:2+fnlen]
                mtime=struct.unpack(">I",body[2+fnlen:6+fnlen])[0] if len(body)>=6+fnlen else 0
                p["literal_format"]=fmt;p["literal_filename"]=fn.decode("latin1");p["literal_mtime"]=ts(mtime) if mtime else 0
        res["packets"].append(p)
    return res

if __name__=="__main__":
    import json
    files=sorted(glob.glob(sys.argv[1]))
    for f in files:
        print("="*70)
        r=analyze(f)
        print(json.dumps(r,indent=1,default=str))
