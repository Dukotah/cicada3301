#!/bin/sh
# Round 19 / G1 -- fetch the GNU bash release sources this lane's reference is built
# from, and build a REAL bash 4.2 (the Ubuntu 11.04-12.04 shell, per L1 F6/F7).
#
# Nothing here is committed: the tarballs are ~60 MB and every byte of them is
# re-derivable by running this script. See CLAUDE.md "What to commit".
#
# Run:  sh fetch_bash_src.sh        (writes to /tmp/g1src)
set -e
DIR=${1:-/tmp/g1src}
mkdir -p "$DIR"; cd "$DIR"

for v in 3.2 4.0 4.1 4.2 4.3 5.0 5.1 5.2; do
  [ -s "b-$v.tgz" ] || curl -sS "https://ftp.gnu.org/gnu/bash/bash-$v.tar.gz" -o "b-$v.tgz"
  tar -xzOf "b-$v.tgz" "bash-$v/variables.c" > "variables-$v.c" 2>/dev/null || true
  tar -xzOf "b-$v.tgz" "bash-$v/lib/sh/random.c" > "random-$v.c" 2>/dev/null || true
  printf '%-5s variables.c %8s bytes  random.c %8s bytes\n' "$v" \
      "$(wc -c < variables-$v.c 2>/dev/null || echo 0)" \
      "$(wc -c < random-$v.c 2>/dev/null || echo 0)"
done

# --- build a real bash 4.2 -------------------------------------------------------
# gcc >= 14 rejects several 2011-era constructs.  -std=gnu89 restores them.  Do NOT
# pass --enable-minimal-config: bash 4.2's expr.c references `ind` outside the
# ARRAY_VARS guard and will not compile without arrays.
if [ ! -x bash-4.2/bash ]; then
  rm -rf bash-4.2; tar -xzf b-4.2.tgz; cd bash-4.2
  F="-O1 -w -std=gnu89 -fcommon"
  CFLAGS="$F" ./configure --without-bash-malloc --disable-nls > ../conf42.log 2>&1
  make -j8 CFLAGS="$F" CFLAGS_FOR_BUILD="$F" > ../make42.log 2>&1
  cd ..
fi
./bash-4.2/bash --version | head -1
echo "bash 4.2 binary: $DIR/bash-4.2/bash   (validate.py finds it there automatically)"
