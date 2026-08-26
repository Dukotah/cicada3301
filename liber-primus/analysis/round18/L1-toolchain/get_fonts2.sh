#!/usr/bin/env bash
# second pass of the font bank: Junicode (the standard scholarly Anglo-Saxon
# face) and a few more period candidates.
set -u
D="$(cd "$(dirname "$0")" && pwd)/fonts"
mkdir -p "$D"; cd "$D"
rm -f Caslon-Antique.ttf          # first-pass URL was wrong (fetched NotoSerif, no Runic block)

try () { # outname url...
  out="$1"; shift
  [ -s "$out" ] && { echo "have   $out"; return; }
  for u in "$@"; do
    if timeout 90 curl -sSLf -o "$out.tmp" "$u" && [ -s "$out.tmp" ]; then
      mv "$out.tmp" "$out"; echo "got    $out <- $u ($(stat -c%s "$out"))"; return
    fi
    rm -f "$out.tmp"
  done
  echo "FAILED $out"
}

try Junicode.ttf \
  "https://mirrors.ctan.org/fonts/junicode/ttf/Junicode.ttf" \
  "https://cdn.jsdelivr.net/gh/psb1558/Junicode-font@master/fonts/Junicode.ttf" \
  "https://github.com/psb1558/Junicode-font/raw/refs/heads/master/fonts/Junicode.ttf" \
  "https://github.com/psb1558/Junicode-font/releases/download/v2.211/Junicode-fonts.zip"

try junicode_ctan.zip "https://mirrors.ctan.org/fonts/junicode.zip"
if [ -s junicode_ctan.zip ] && [ ! -d junicode_ctan ]; then
  mkdir -p junicode_ctan && (cd junicode_ctan && unzip -oq ../junicode_ctan.zip)
fi

try EversonMono.ttf \
  "https://www.evertype.com/emono/EversonMono.ttf" \
  "https://raw.githubusercontent.com/hikikomorii/fonts/master/EversonMono.ttf"

try DalekFont.ttf "https://www.babelstone.co.uk/Fonts/Download/BabelStoneAngloSaxon.ttf"
try BabelStoneModern.ttf "https://www.babelstone.co.uk/Fonts/Download/BabelStoneModern.ttf"
try Symbola.ttf \
  "https://raw.githubusercontent.com/ChiefMikeK/ttf-symbola/master/Symbola-13.otf" \
  "https://dn-works.com/wp-content/uploads/2020/UFAS-Fonts/Symbola.zip"

echo "--- bank ---"
ls -la *.ttf *.otf 2>/dev/null
find junicode_ctan -iname '*.ttf' 2>/dev/null | head -10
