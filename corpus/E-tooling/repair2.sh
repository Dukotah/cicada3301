#!/bin/bash
E=/c/Users/dukot/projects/cicada3301/corpus/E-tooling
V=$E/vendor
export GIT_TERMINAL_PROMPT=0
LOG=$E/clone.log
valid() {
  local d="$V/$1"
  [ -d "$d/.git" ] || return 1
  git --git-dir="$d/.git" rev-parse HEAD >/dev/null 2>&1 || return 1
  [ -n "$(ls -A "$d" 2>/dev/null | grep -v '^\.git$' | head -1)" ] || return 1
  return 0
}
cat "$E/targets.txt" "$E/targets2.txt" "$E/retry2.txt" 2>/dev/null | tr -d '\r' | sort -u -t'|' -k1,1 > "$E/all_targets.txt"
while IFS='|' read -r d u dep; do
  [ -z "$d" ] && continue
  case "$d" in \#*|/*) continue;; esac
  if valid "$d"; then continue; fi
  echo "$(date -u +%FT%TZ) R2-TRY $d" >> "$LOG"
  rm -rf "$V/$d" 2>/dev/null
  if [ "$dep" = "full" ]; then
    timeout 200 git clone --quiet "$u" "$V/$d" >>"$LOG" 2>&1
  else
    timeout 200 git clone --quiet --depth "${dep:-50}" "$u" "$V/$d" >>"$LOG" 2>&1
  fi
  if valid "$d"; then
    echo "$(date -u +%FT%TZ) R2-OK $d $(git --git-dir="$V/$d/.git" rev-parse HEAD) $(git --git-dir="$V/$d/.git" log -1 --format=%cI)" >> "$LOG"
  else
    echo "$(date -u +%FT%TZ) R2-FAIL $d $u" >> "$LOG"
  fi
done < "$E/all_targets.txt"
echo "R2 PASS DONE $(date -u +%FT%TZ)" >> "$LOG"
