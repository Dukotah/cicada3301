#!/usr/bin/env python3
"""L1 Round-29 FAST parallel key sweep. Same strict adjudication as sweep.py but
parallelised over cores and with a per-worker scratch file. OutGuess default
mode + steghide across keys_big.txt on onion1/2/3 (+onion5portrait). Legacy `-t`
retrieval was proven byte-identical to default on the keyless control, so bulk
uses default; a small `-t` spot-check runs separately.

STRICT: OutGuess never fails, so a non-empty blob is NOT a hit. Only a real magic
header or clean English ASCII counts. Everything else = wrong-key artifact.
"""
import os, subprocess, sys, hashlib, collections
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUTGUESS = "/usr/local/bin/outguess"
STEGHIDE = "/usr/bin/steghide"
TMP = os.path.join(HERE, "_scratch")
os.makedirs(TMP, exist_ok=True)

MAGIC = {b"-----BEGIN":"pgp/asc", b"\x1f\x8b":"gzip", b"\xff\xd8\xff":"jpeg",
    b"\x89PNG":"png", b"PK\x03\x04":"zip", b"BZh":"bzip2", b"\x37\x7a\xbc\xaf":"7z",
    b"Rar!":"rar", b"%PDF":"pdf", b"OggS":"ogg", b"SQLite":"sqlite", b"\xfd7zXZ":"xz"}
ENGLISH = set("ETAOINSHRDLUCMWFGYPBVKJXQZ etaoinshrdlucmwfgypbvkjxqz")

def classify(data):
    if not data: return "EMPTY",""
    for m,name in MAGIC.items():
        if data.startswith(m): return "HIT",f"magic:{name}"
    printable = sum(1 for b in data if 32<=b<127 or b in (9,10,13))
    frac = printable/len(data)
    if frac>0.90 and len(data)>=16:
        txt = data.decode("latin-1")
        if any(c.isalpha() for c in txt):
            eng = sum(1 for c in txt if c in ENGLISH)/len(txt)
            if eng>0.70: return "MAYBE",f"ascii eng={eng:.2f}"
    return "ARTIFACT",f"bin frac={frac:.2f}"

def og(img, key, wid):
    out = os.path.join(TMP, f"og{wid}.bin")
    try: os.remove(out)
    except OSError: pass
    cmd = [OUTGUESS, "-k", key, "-r", img, out]
    try:
        subprocess.run(cmd, capture_output=True, timeout=20)
    except subprocess.TimeoutExpired:
        return b""
    except Exception:
        return b""
    try:
        return open(out,"rb").read() if os.path.exists(out) else b""
    except OSError:
        return b""

def sh(img, key, wid):
    out = os.path.join(TMP, f"sh{wid}.bin")
    try: os.remove(out)
    except OSError: pass
    cmd = [STEGHIDE,"extract","-sf",img,"-p",key,"-xf",out,"-f"]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=20)
    except Exception:
        return b""
    if r.returncode==0 and os.path.exists(out):
        try: return open(out,"rb").read()
        except OSError: return b""
    return b""

_IMAGES = None
def worker(args):
    idx, key = args
    wid = os.getpid()
    rows = []            # (image, tool, key, verdict, note, len, sha8, data_if_candidate)
    c = collections.Counter()
    for img in _IMAGES:
        name = os.path.basename(img)
        d = og(img, key, wid)
        v,note = classify(d)
        c[("outguess",v)] += 1
        if v in ("HIT","MAYBE"):
            rows.append((name,"outguess",key,v,note,len(d),hashlib.sha256(d).hexdigest()[:8],d))
        d2 = sh(img, key, wid)
        v2,note2 = classify(d2)
        c[("steghide",v2)] += 1
        if v2 in ("HIT","MAYBE"):
            rows.append((name,"steghide",key,v2,note2,len(d2),hashlib.sha256(d2).hexdigest()[:8],d2))
    return rows, c

def init(images):
    global _IMAGES
    _IMAGES = images

def positive_control():
    img = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/artifacts/dl_1033.jpg"
    out = os.path.join(TMP,"ctrl.bin")
    subprocess.run([OUTGUESS,"-r",img,out],capture_output=True,timeout=30)
    d = open(out,"rb").read() if os.path.exists(out) else b""
    ok = d.startswith(b"-----BEGIN PGP SIGNED MESSAGE") and b"Welcome" in d
    print(f"[POS-CONTROL] {'PASS' if ok else 'FAIL'} len={len(d)}", flush=True)
    return ok

def main():
    if not positive_control():
        print("ABORT control"); sys.exit(1)
    keys = [l.rstrip("\n") for l in open(os.path.join(HERE,"keys_big.txt")) if l.strip()]
    CANON = os.path.join(HERE,"canonical")
    images = [os.path.join(CANON,f) for f in ("onion1.jpg","onion2.jpg","onion3.jpg")]
    art = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/artifacts"
    p = os.path.join(art,"onion5portrait.jpg")
    if os.path.exists(p) and os.path.getsize(p)>1000: images.append(p)
    print(f"[keys] {len(keys)}  [images] {[os.path.basename(i) for i in images]}", flush=True)

    stats = collections.Counter()
    candidates = []
    done = 0
    with ProcessPoolExecutor(max_workers=6, initializer=init, initargs=(images,)) as ex:
        for rows, c in ex.map(worker, list(enumerate(keys)), chunksize=8):
            stats.update(c)
            candidates.extend(rows)
            done += 1
            if done % 500 == 0:
                print(f"  {done}/{len(keys)} keys  cand={len(candidates)}", flush=True)

    log = open(os.path.join(HERE,"sweep_log.tsv"),"w")
    log.write("image\ttool\tkey\tverdict\tnote\tlen\tsha8\n")
    for name,tool,key,v,note,ln,sha8,data in candidates:
        log.write(f"{name}\t{tool}\t{key}\t{v}\t{note}\t{ln}\t{sha8}\n")
        safe = "".join(ch if ch.isalnum() else "_" for ch in key)[:24]
        open(os.path.join(HERE,f"cand_{name}_{tool}_{safe}.bin"),"wb").write(data)
    log.close()

    print("\n=== SWEEP STATS ===", flush=True)
    for (tool,v),n in sorted(stats.items()):
        print(f"  {tool:9s} {v:9s} {n}")
    print(f"\n=== CANDIDATES (HIT/MAYBE): {len(candidates)} ===")
    for name,tool,key,v,note,ln,sha8,data in candidates:
        print(f"  [{v}] {name} {tool} key={key!r} :: {note} len={ln}")
    if not candidates:
        print("  (none — clean NULL)")

if __name__ == "__main__":
    main()
