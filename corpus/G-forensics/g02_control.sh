#!/bin/bash
set -u
REPO=/mnt/c/Users/dukot/projects/cicada3301
G=$REPO/corpus/G-forensics
C=$G/raw/g02_control
mkdir -p "$C"
cd "$C"
echo "=== gs version ==="; gs --version
# 6in x 9in at 400dpi = 2400 x 3600 px, matching the LP pages exactly
cat > blank.ps <<'PS'
<< /PageSize [432 648] >> setpagedevice
showpage
PS
cat > text.ps <<'PS'
<< /PageSize [432 648] >> setpagedevice
/Helvetica findfont 24 scalefont setfont
72 500 moveto (CONTROL PAGE - NOT CICADA) show
72 460 moveto (the quick brown fox jumps over the lazy dog) show
showpage
PS
echo "=== render blank control (colour, DeviceRGB) ==="
gs -q -dNOPAUSE -dBATCH -sDEVICE=jpeg -r400 -dJPEGQ=95 -sOutputFile=ctl_blank_rgb.jpg blank.ps 2>&1 | head -3
echo "=== render blank control (grayscale) ==="
gs -q -dNOPAUSE -dBATCH -sDEVICE=jpeggray -r400 -dJPEGQ=95 -sOutputFile=ctl_blank_gray.jpg blank.ps 2>&1 | head -3
echo "=== render text control ==="
gs -q -dNOPAUSE -dBATCH -sDEVICE=jpeg -r400 -dJPEGQ=95 -sOutputFile=ctl_text_rgb.jpg text.ps 2>&1 | head -3
echo
for f in ctl_blank_rgb.jpg ctl_blank_gray.jpg ctl_text_rgb.jpg; do
  [ -f "$f" ] || { echo "$f NOT PRODUCED"; continue; }
  echo "--- $f ---"
  identify "$f" 2>/dev/null | head -1
  sha256sum "$f"
  outguess -r "$f" "${f%.jpg}.out" 2>&1 | sed 's/^/   /'
  if [ -s "${f%.jpg}.out" ]; then
    echo "   OUTPUT SIZE: $(stat -c%s "${f%.jpg}.out")"
    echo "   FIRST 32 BYTES: $(head -c 32 "${f%.jpg}.out" | xxd -p | tr -d '\n')"
  else echo "   OUTPUT: EMPTY (no extraction)"; fi
done
echo
echo "=== reference: the shared prefix head from the 16 LP pages ==="
echo "c0a128e346d23572fe62822e50f70d8aed61d93bc607ca31e7c6f64ed9d3c20f"
