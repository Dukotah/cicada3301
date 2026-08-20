import hashlib, json, os, re, math, struct, datetime, subprocess, sys
ROOT="/mnt/c/Users/dukot/projects/cicada3301"
GD=f"{ROOT}/corpus/G-forensics"
RAW=f"{GD}/raw"
os.makedirs(RAW, exist_ok=True)
RES=f"{GD}/RESULTS.jsonl"

def utc(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def emit(row):
    row.setdefault("run_utc", utc())
    with open(RES,"a",encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False)+"\n")

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as fh:
        for c in iter(lambda: fh.read(1<<20), b''): h.update(c)
    return h.hexdigest()

def savraw(name, data):
    p=os.path.join(RAW,name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    mode='wb' if isinstance(data,(bytes,bytearray)) else 'w'
    with open(p,mode, **({} if mode=='wb' else {'encoding':'utf-8'})) as f: f.write(data)
    return p

def run(cmd, timeout=180):
    try:
        r=subprocess.run(cmd, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout.decode('utf-8','replace'), r.stderr.decode('utf-8','replace')
    except FileNotFoundError as e:
        return -127, "", f"TOOL_NOT_FOUND: {e}"
    except subprocess.TimeoutExpired:
        return -9, "", "TIMEOUT"

def entropy(b):
    if not b: return 0.0
    c=[0]*256
    for x in b: c[x]+=1
    n=len(b); e=0.0
    for v in c:
        if v:
            p=v/n; e-=p*math.log2(p)
    return e

def entropy_profile(path, window=65536):
    """Returns (global_entropy, [(offset, entropy)], anomalies)"""
    prof=[]
    with open(path,'rb') as f:
        off=0
        while True:
            b=f.read(window)
            if not b: break
            prof.append((off, round(entropy(b),4)))
            off+=len(b)
    if not prof: return 0.0, [], []
    vals=[e for _,e in prof]
    mean=sum(vals)/len(vals)
    sd=(sum((v-mean)**2 for v in vals)/len(vals))**0.5
    anom=[(o,e) for o,e in prof if sd>0.01 and abs(e-mean)>3*sd]
    return round(mean,4), prof, anom

STR_RE=re.compile(rb'[\x20-\x7e]{6,}')
def strings_all(path, minlen=6, cap=4_000_000):
    with open(path,'rb') as f: data=f.read(cap)
    a=[m.decode('ascii') for m in STR_RE.findall(data)]
    # UTF-16LE: ascii bytes separated by \x00
    le=re.findall(rb'(?:[\x20-\x7e]\x00){6,}', data)
    be=re.findall(rb'(?:\x00[\x20-\x7e]){6,}', data)
    lel=[x.decode('utf-16-le','replace') for x in le]
    bel=[x.decode('utf-16-be','replace') for x in be]
    return a, lel, bel, len(data)>=cap

MAGIC=[(b'\xff\xd8\xff','JPEG'),(b'\x89PNG\r\n\x1a\n','PNG'),(b'GIF8','GIF'),(b'BM','BMP'),
 (b'%PDF','PDF'),(b'PK\x03\x04','ZIP'),(b'\x1f\x8b','GZIP'),(b'ID3','MP3/ID3'),(b'\xff\xfb','MP3'),
 (b'\x7fELF','ELF'),(b'CD001','ISO9660@?'),(b'-----BEGIN','PEM/ASCII-ARMOR'),(b'<!DOCTYPE','HTML'),
 (b'<html','HTML'),(b'BZh','BZIP2'),(b'\xfd7zXZ','XZ'),(b'Rar!','RAR'),(b'\x00\x00\x01\xba','MPEG-PS')]
def sniff(path):
    with open(path,'rb') as f: head=f.read(4096)
    for sig,name in MAGIC:
        if head.startswith(sig): return name
    if b'CD001' in head[:40000]: return 'ISO9660?'
    try:
        head.decode('utf-8'); return 'TEXT/UTF-8'
    except Exception: pass
    return 'DATA/unknown'
