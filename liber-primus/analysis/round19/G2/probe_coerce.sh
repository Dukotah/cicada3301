#!/usr/bin/env bash
# ROUND 19 / G2 -- probe how the real perl coerces an srand() argument.
# Emits: ARG <TAB> srand-return <TAB> first-8 int(rand(29))
cd "$(dirname "$0")" || exit 1
echo "--- shell sanity ---"
for a in x y; do echo "A=[$a]"; done
perl -e 'print "argc=", scalar(@ARGV), " argv=@ARGV\n"' one two three
echo "--- srand coercion ---"
while IFS= read -r arg; do
  printf '%-16s\t' "[$arg]"
  perl ref_perl.pl coerce "$arg" 2>&1 | head -1
done <<'ARGS'
3301
CICADA3301
3301CICADA
0x0CE5
3.7
-1
1e3
4294967297
0

3301.9
 42
+3301
ARGS
