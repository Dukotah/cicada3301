#!/bin/bash
set -u
C=/mnt/c/Users/dukot/projects/cicada3301/corpus/G-forensics/raw/g02_control
D=/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/artifacts/rune_pages
cd "$C"
dims () { python3 - "$1" <<'PY'
import struct,sys
d=open(sys.argv[1],'rb').read()
i=2
while i<len(d)-1:
    if d[i]!=0xFF: i+=1; continue
    m=d[i+1]
    if m in (0xC0,0xC1,0xC2):
        h,w=struct.unpack('>HH',d[i+5:i+9]); print('%dx%d ncomp=%d'%(w,h,d[i+9])); break
    if m==0xD8 or m==0x01 or 0xD0<=m<=0xD7: i+=2; continue
    if m==0xD9: break
    L=struct.unpack('>H',d[i+2:i+4])[0]; i+=2+L
PY
}
echo "=== outguess version ==="; outguess 2>&1 | head -1
for f in ctl_blank_rgb ctl_blank_gray ctl_text_rgb; do
  echo "--- $f.jpg ---"
  dims "$f.jpg"
  sha256sum "$f.jpg"
  outguess -r "$f.jpg" "/tmp/$f.out" 2>&1 | sed 's/^/   /'
  echo "   out size: $(stat -c%s /tmp/$f.out 2>/dev/null || echo 0)"
done
echo "=== reference LP page 40 header ==="
dims "$D/40.jpg"
outguess -r "$D/40.jpg" /tmp/lp40.out 2>&1 | sed 's/^/   /'
