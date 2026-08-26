#!/usr/bin/env bash
# Round 19 / G4 — run the REAL TeX binaries to produce reference vectors.
# Rebuildable: everything it writes lives under tex/ and tex/out210 (gitignored).
#
#   bash make_vectors.sh          # needs pdflatex + pgf + lcg + random.tex
#
# Install prerequisites (Ubuntu/WSL):
#   sudo apt-get install -y --no-install-recommends \
#        texlive-latex-base texlive-pictures texlive-latex-extra \
#        texlive-plain-generic texlive-luatex texlive-binaries
# and run ./fetch_sources.sh first for the era-correct pgf 2.10 tree.
set -u
cd "$(dirname "$0")/tex"

run () { # jobname
  echo "== $1"
  pdflatex -interaction=nonstopmode -halt-on-error "$1.tex" >"$1.log" 2>&1
  echo "   exit=$? out=$(wc -l < "$1.txt" 2>/dev/null || echo MISSING)"
}

run ref_pgf
run ref_lcg
run ref_random
run ref_pdf

# the era-correct pgf 2.10 tree, for the version-invariance gate (V3)
PGF210=../vendor/pgf_2.10/tex
if [ -d "$PGF210" ]; then
  mkdir -p out210 && cp ref_pgf.tex out210/
  ( cd out210 && TEXINPUTS="$(cd ../$PGF210 && pwd)//:" \
      pdflatex -interaction=nonstopmode ref_pgf.tex >ref_pgf.log 2>&1
    echo "== ref_pgf @ pgf2.10  exit=$? out=$(wc -l < ref_pgf.txt 2>/dev/null || echo MISSING)" )
fi

ls -la *.txt out210/*.txt 2>/dev/null
