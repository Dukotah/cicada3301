#!/usr/bin/env bash
# I4 support - assemble the candidate font bank for rune-face identification.
# Only faces that existed (or whose lineage existed) in 2012-2014 are wanted;
# modern releases of the same family are used as proxies where the period
# release is not downloadable, and that substitution is recorded in RESULTS.md.
set -u
D="$(cd "$(dirname "$0")" && pwd)/fonts"
mkdir -p "$D"
cd "$D"

get () { # name url
  if [ -s "$1" ]; then echo "have   $1"; return; fi
  if timeout 90 curl -sSL -f -o "$1.tmp" "$2" && [ -s "$1.tmp" ]; then
    mv "$1.tmp" "$1"; echo "got    $1  ($(stat -c%s "$1") bytes)"
  else
    rm -f "$1.tmp"; echo "FAILED $1  <- $2"
  fi
}

# --- local system faces with a Runic block -------------------------------
for f in /usr/share/fonts/truetype/freefont/FreeSerif.ttf \
         /usr/share/fonts/truetype/freefont/FreeSans.ttf \
         /usr/share/fonts/truetype/freefont/FreeMono.ttf \
         /usr/share/fonts/opentype/unifont/unifont.otf ; do
  [ -f "$f" ] && cp -n "$f" . && echo "local  $(basename "$f")"
done
# Windows Segoe UI Symbol (runic range; shipped with Windows 7/8, i.e. 2009+)
[ -f /mnt/c/Windows/Fonts/seguisym.ttf ] && cp -n /mnt/c/Windows/Fonts/seguisym.ttf . \
  && echo "local  seguisym.ttf"

# --- downloads -----------------------------------------------------------
get NotoSansRunic-Regular.ttf \
  "https://github.com/notofonts/notofonts.github.io/raw/main/fonts/NotoSansRunic/hinted/ttf/NotoSansRunic-Regular.ttf"
get Junicode.ttf \
  "https://github.com/psb1558/Junicode-font/raw/master/fonts/ttf/Junicode.ttf"
get JunicodeVF.ttf \
  "https://github.com/psb1558/Junicode-font/releases/download/v2.211/Junicode.ttf"
get Quivira.otf \
  "http://www.quivira-font.com/files/Quivira.otf"
get BabelStoneRunic.ttf \
  "https://www.babelstone.co.uk/Fonts/Download/BabelStoneRunic.ttf"
get BabelStoneRunicElderFuthark.ttf \
  "https://www.babelstone.co.uk/Fonts/Download/BabelStoneRunicElderFuthark.ttf"
get Caslon-Antique.ttf \
  "https://github.com/google/fonts/raw/main/ofl/notoserif/NotoSerif%5Bwdth%2Cwght%5D.ttf"
get Everson-Mono.ttf \
  "https://www.evertype.com/emono/EversonMono.ttf"
get Code2000.ttf \
  "https://raw.githubusercontent.com/lemonsqueeze/unicode-fonts/master/Code2000.ttf"
get Kelvinch.otf \
  "https://www.fontspace.com/download/font/kelvinch"

# --- allrunes (LaTeX) from CTAN -----------------------------------------
if [ ! -d allrunes ]; then
  if timeout 120 curl -sSL -f -o allrunes.zip "http://mirrors.ctan.org/fonts/allrunes.zip"; then
    mkdir -p allrunes && (cd allrunes && unzip -oq ../allrunes.zip) && echo "got    allrunes.zip"
  else
    echo "FAILED allrunes.zip"
  fi
fi

echo "--- bank ---"
ls -la *.ttf *.otf 2>/dev/null
find allrunes -name '*.pfb' -o -name '*.ttf' -o -name '*.otf' 2>/dev/null | head -30
