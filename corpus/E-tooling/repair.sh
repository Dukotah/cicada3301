#!/bin/bash
E=/c/Users/dukot/projects/cicada3301/corpus/E-tooling
V=$E/vendor
cd "$E" || exit 1
export GIT_TERMINAL_PROMPT=0
valid() {
  d="$V/$1"
  [ -d "$d/.git" ] || return 1
  git --git-dir="$d/.git" rev-parse HEAD >/dev/null 2>&1 || return 1
  [ "$(ls -A "$d" | grep -v '^\.git$' | head -1)" != "" ] || return 1
  return 0
}
cat targets.txt targets2.txt retry2.txt 2>/dev/null | tr -d '\r' | sort -u -t'|' -k1,1 \
| while IFS='|' read -r d u dep; do
  [ -z "$d" ] && continue
  case "$d" in \#*) continue;; esac
  if valid "$d"; then continue; fi
  echo "$(date -u +%FT%TZ) REPAIR $d" >> "$E/clone.log"
  rm -rf "$V/$d" 2>/dev/null
  if [ "$dep" = "full" ]; then
    timeout 150 git clone --quiet "$u" "$V/$d" >>"$E/clone.log" 2>&1
  else
    timeout 150 git clone --quiet --depth "${dep:-50}" "$u" "$V/$d" >>"$E/clone.log" 2>&1
  fi
  if valid "$d"; then
    echo "$(date -u +%FT%TZ) OK $d $(git --git-dir="$V/$d/.git" rev-parse HEAD) $(git --git-dir="$V/$d/.git" log -1 --format=%cI)" >> "$E/clone.log"
  else
    echo "$(date -u +%FT%TZ) STILLBAD $d $u" >> "$E/clone.log"
  fi
done
echo "REPAIR PASS DONE $(date -u +%FT%TZ)" >> "$E/clone.log"
