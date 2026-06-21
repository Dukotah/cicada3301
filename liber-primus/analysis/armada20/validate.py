#!/usr/bin/env python3
import json, zlib, gzip, io

data = json.load(open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20/forensics_full.json"))

# 1) Real trailing data (post-EOI / post-IEND) with length > 2
print("=== TRAILING DATA (len>2) ===")
trail = [r for r in data if r.get("trailing_len",0) > 2]
for r in sorted(trail, key=lambda x:-x.get("trailing_len",0)):
    print(f"\n{r['path']}")
    print(f"  trailing_len={r['trailing_len']} printable_ratio={r.get('trailing_printable_ratio')}")
    if r.get("trailing_strings"):
        print("  strings:", r["trailing_strings"])
    else:
        print("  hex:", r.get("trailing_hex"))

# 2) Validate GZIP magics by attempting decompression
print("\n\n=== VALIDATING GZIP MAGIC HITS (attempt real decompress) ===")
valid_gzip = []
for r in data:
    if "embedded_magics" not in r:
        continue
    gz = [m for m in r["embedded_magics"] if m["magic"]=="GZIP"]
    if not gz:
        continue
    path = r["path"]
    with open(path,"rb") as f:
        blob = f.read()
    for m in gz:
        off = m["off"]
        chunk = blob[off:off+4096]
        try:
            d = zlib.decompressobj(16+zlib.MAX_WBITS)
            out = d.decompress(chunk)
            if len(out) > 8:
                valid_gzip.append((path, off, out[:80]))
        except Exception:
            pass
        # also raw deflate from offset+? unlikely
if valid_gzip:
    for p,o,out in valid_gzip:
        print(p, o, out)
else:
    print("NONE -- all GZIP magic hits are spurious 1F8B byte coincidences inside image data")
