#!/usr/bin/env bash
# L5-seed32 HARNESS GATE for the new generators 10-13.
# Pre-registered rule: a generator is swept only if it reproduces a REAL reference
# implementation exactly on >= 3 seeds x >= 500 draws. Anything that fails here is
# NOT swept, because an unvalidated generator produces a meaningless null.
set -u
cd "$(dirname "$0")"
export LP_CT=../../seed_sweep/ct.bin LP_NGRAM=../../seed_sweep/ngram.bin
NDRAW=2000
SEEDS="1 12345 1399079190 2147483647 3141592653"
FAIL=0

echo "### gen 10 — Perl  srand(S); int(rand(29))     reference: /usr/bin/perl"
for S in $SEEDS; do
  perl -e "srand($S); print join(qq{\n}, map { int(rand(29)) } 1..$NDRAW), qq{\n};" > /tmp/ref10.txt
  ./sweep32x dumpn 10 "$S" "$NDRAW" > /tmp/got10.txt
  if cmp -s /tmp/ref10.txt /tmp/got10.txt; then echo "  seed $S  OK ($NDRAW draws)"; else echo "  seed $S  MISMATCH"; FAIL=1; fi
done

echo "### gen 11 — POSIX srand48(S); lrand48()%29    reference: glibc"
cat > /tmp/ref11.c <<'EOF'
#include <stdio.h>
#include <stdlib.h>
int main(int c, char **v){ srand48(strtol(v[1],0,0)); int n=atoi(v[2]);
  for(int i=0;i<n;i++) printf("%ld\n", lrand48()%29); return 0; }
EOF
gcc -O2 -o /tmp/ref11 /tmp/ref11.c
for S in $SEEDS; do
  /tmp/ref11 "$S" "$NDRAW" > /tmp/ref11.txt
  ./sweep32x dumpn 11 "$S" "$NDRAW" > /tmp/got11.txt
  if cmp -s /tmp/ref11.txt /tmp/got11.txt; then echo "  seed $S  OK ($NDRAW draws)"; else echo "  seed $S  MISMATCH"; FAIL=1; fi
done

echo "### gen 12 — Ruby  srand(S); rand(29)          reference: $(ruby -v 2>/dev/null | cut -d' ' -f1-2)"
for S in $SEEDS; do
  ruby -e "srand($S); puts((1..$NDRAW).map{ rand(29) })" > /tmp/ref12.txt
  ./sweep32x dumpn 12 "$S" "$NDRAW" > /tmp/got12.txt
  if cmp -s /tmp/ref12.txt /tmp/got12.txt; then echo "  seed $S  OK ($NDRAW draws)"; else echo "  seed $S  MISMATCH"; FAIL=1; fi
done

echo "### gen 13 — xorshift32 (13,17,5) % 29"
echo "  NOTE: xorshift32 has no canonical library binding. The reference here is an"
echo "  INDEPENDENT re-implementation of Marsaglia's published recurrence in Python,"
echo "  not a second vendor implementation. Validation basis is weaker than 10-12."
cat > /tmp/ref13.py <<'EOF'
import sys
s = int(sys.argv[1]) & 0xffffffff
if s == 0: s = 1
n = int(sys.argv[2])
out = []
for _ in range(n):
    s ^= (s << 13) & 0xffffffff
    s ^= s >> 17
    s ^= (s << 5) & 0xffffffff
    out.append(s % 29)
print("\n".join(map(str, out)))
EOF
for S in $SEEDS; do
  python3 /tmp/ref13.py "$S" "$NDRAW" > /tmp/ref13.txt
  ./sweep32x dumpn 13 "$S" "$NDRAW" > /tmp/got13.txt
  if cmp -s /tmp/ref13.txt /tmp/got13.txt; then echo "  seed $S  OK ($NDRAW draws)"; else echo "  seed $S  MISMATCH"; FAIL=1; fi
done

echo "### regression: generators 0-9 must be byte-identical to Round 8's sweep.c"
./sweep32x selftest | tail -1

echo
[ "$FAIL" -eq 0 ] && echo "HARNESS GATE: PASS" || echo "HARNESS GATE: FAIL — do not sweep the failing generator"
