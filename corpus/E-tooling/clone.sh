#!/bin/bash
# usage: clone.sh <dirname> <url> [depth|full]
# NOTE: validity is tested with `git -C d --git-dir=d/.git`, NOT plain `git -C d`,
# because an EMPTY dir inside a git work tree makes `git -C d rev-parse HEAD`
# resolve against the PARENT repo and silently report success.
set -u
export GIT_TERMINAL_PROMPT=0
V=/c/Users/dukot/projects/cicada3301/corpus/E-tooling/vendor
L=/c/Users/dukot/projects/cicada3301/corpus/E-tooling/clone.log
d=$1; u=$2; depth=${3:-full}
mkdir -p "$V"; cd "$V" || exit 1

ok() { [ -d "$1/.git" ] && git --git-dir="$1/.git" rev-parse HEAD >/dev/null 2>&1; }

if ok "$d"; then echo "$(date -u +%FT%TZ) SKIP $d" >> "$L"; exit 0; fi
rm -rf "$d" 2>/dev/null
if [ "$depth" = "full" ]; then git clone --quiet "$u" "$d" >> "$L" 2>&1
else git clone --quiet --depth "$depth" "$u" "$d" >> "$L" 2>&1; fi
rc=$?
if ok "$d"; then
  echo "$(date -u +%FT%TZ) OK $d $(git --git-dir="$d/.git" rev-parse HEAD) $(git --git-dir="$d/.git" log -1 --format=%cI)" >> "$L"
else
  echo "$(date -u +%FT%TZ) FAIL($rc) $d $u" >> "$L"
fi
