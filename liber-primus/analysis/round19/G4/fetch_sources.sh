#!/usr/bin/env bash
# Round 19 / G4 — fetch era-correct TeX package sources into vendor/ (gitignored).
# Everything this script writes is rebuildable; nothing under vendor/ is committed.
#
# Era target (see RESULTS.md §2): Ubuntu 11.04 / 11.10 / 12.04 LTS all shipped
# TeX Live 2009 (source package texlive-base 2009-*), so the era-correct pgf is
# pgf 2.00 (TL2009's bundled version) with pgf 2.10 (Oct 2010, what a user who
# installed from CTAN in 2011-2013 would have) as the alternative.
set -u
cd "$(dirname "$0")"
mkdir -p vendor
cd vendor

get () { # url outfile
  if [ -s "$2" ]; then echo "have $2"; return 0; fi
  echo "GET $1 -> $2"
  curl -sSL --retry 3 -o "$2" "$1" -w '  http=%{http_code} bytes=%{size_download}\n' || echo "  FAILED $1"
}

# --- historic pgf (SourceForge release archive) --------------------------------
get "https://sourceforge.net/projects/pgf/files/pgf/version%202.10/pgf_2.10.tds.zip/download" pgf_2.10.tds.zip

# --- current CTAN copies of the three generators (for diffing) -----------------
get "https://mirrors.ctan.org/graphics/pgf/base/tex/generic/pgf/math/pgfmathfunctions.random.code.tex" pgfmathfunctions.random.code.tex.ctan
get "https://mirrors.ctan.org/macros/latex/contrib/lcg/lcg.dtx" lcg.dtx.ctan
get "https://mirrors.ctan.org/macros/latex/contrib/lcg/lcg.ins" lcg.ins.ctan
get "https://mirrors.ctan.org/macros/generic/random/random.tex" random.tex.ctan

# pgf 2.00 (the version bundled with TeX Live 2009 = the Ubuntu 11.04/11.10/12.04 stack)
# is only published as a tarball, not a .tds.zip.
get "https://sourceforge.net/projects/pgf/files/pgf/version%202.00/pgf-2.00.tar.gz/download" pgf-2.00.tar.gz
if [ -s pgf-2.00.tar.gz ]; then
  mkdir -p pgf_2.00src && tar xzf pgf-2.00.tar.gz -C pgf_2.00src && echo "unpacked pgf-2.00.tar.gz"
fi

# lcg.dtx / random.tex need a plain-http CTAN mirror redirect (-k: the WSL trust
# store does not carry every mirror's issuer).
for u in \
  "http://mirrors.ctan.org/macros/latex/contrib/lcg/lcg.dtx" \
  "http://mirrors.ctan.org/macros/generic/misc/random.tex" \
  "http://mirrors.ctan.org/macros/generic/random/random.tex" ; do
  o="$(basename "$u").ctan"
  [ -s "$o" ] || curl -sSLk -o "$o" "$u" -w "$u -> %{http_code} %{size_download}\n"
done

for z in pgf_2.10.tds.zip; do
  [ -s "$z" ] || continue
  d="${z%.tds.zip}"
  mkdir -p "$d" && (cd "$d" && unzip -oq "../$z" 2>/dev/null) && echo "unpacked $z -> $d"
done

ls -la
