#!/bin/bash
for t in exiftool binwalk steghide sox convert ffmpeg gem zsteg outguess stegdetect ruby foremost python3 gs xxd openssl jsteg stegsolve; do
  p=$(command -v "$t")
  if [ -n "$p" ]; then
    printf '%-12s OK       %-24s ' "$t" "$p"
    case "$t" in
      exiftool) exiftool -ver;;
      binwalk) binwalk --version 2>&1 | head -1;;
      steghide) steghide --version 2>&1 | head -1;;
      sox) sox --version 2>&1 | head -1;;
      ffmpeg) ffmpeg -version 2>&1 | head -1 | cut -c1-60;;
      convert) convert --version 2>&1 | head -1 | cut -c1-60;;
      gs) gs --version;;
      python3) python3 -V;;
      openssl) openssl version;;
      ruby) ruby -v | cut -c1-40;;
      outguess) outguess 2>&1 | head -1;;
      *) echo "";;
    esac
  else
    printf '%-12s MISSING\n' "$t"
  fi
done
echo "--- python modules ---"
python3 -c 'import PIL,numpy;print("Pillow",PIL.__version__,"| numpy",numpy.__version__)' 2>&1
python3 -c 'import scipy;print("scipy",scipy.__version__)' 2>&1 | head -1
echo "--- binwalk background job ---"
tail -2 /tmp/bw.log 2>&1
echo "--- outguess build provenance ---"
ls -la /usr/local/bin/outguess
