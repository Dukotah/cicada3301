#!/bin/bash
E=/c/Users/dukot/projects/cicada3301/corpus/E-tooling
V=$E/vendor
export GIT_TERMINAL_PROMPT=0
while IFS='|' read -r d u; do
  [ -z "$d" ] && continue
  [ -d "$V/$d/.git" ] && continue
  rm -rf "$V/$d" 2>/dev/null
  timeout 150 git clone --quiet --depth 50 "$u" "$V/$d" >>"$E/clone.log" 2>&1
  if [ -d "$V/$d/.git" ]; then
    echo "$(date -u +%FT%TZ) C3-OK $d $(git --git-dir=$V/$d/.git rev-parse HEAD) $(git --git-dir=$V/$d/.git log -1 --format=%cI)" >> "$E/clone.log"
  else
    echo "$(date -u +%FT%TZ) C3-FAIL $d $u" >> "$E/clone.log"
  fi
done <<'LIST'
krisyotam__cicada3301|https://github.com/krisyotam/cicada3301.git
mortlach__Liber-Primus-Crib-Assist|https://github.com/mortlach/Liber-Primus-Crib-Assist.git
mortlach__Liber-Primus-Rune-Decrypting|https://github.com/mortlach/Liber-Primus-Rune-Decrypting.git
mortlach__runeglish-lm|https://github.com/mortlach/runeglish-language-model-transition-probabilty-matrices.git
yo-yo-yo-jbo__cicada_tools|https://github.com/yo-yo-yo-jbo/cicada_tools.git
rtkd__idclip|https://github.com/rtkd/idclip.git
sgroveman__cicada3301_lp|https://github.com/sgroveman/cicada3301_lp.git
iBotPeaches__cicada_3301|https://github.com/iBotPeaches/cicada_3301.git
cmbsolver__cmbcidada3301|https://github.com/cmbsolver/cmbcidada3301.git
cicada-solvers__solving-3301-code-2013|https://github.com/cicada-solvers/solving-3301-code-2013.git
localavaster__cadrypt|https://github.com/localavaster/cadrypt.git
thomasandfriends__Cicada3301Runes|https://github.com/thomasandfriends/Cicada3301Runes.git
cijhho123__cicada3301|https://github.com/cijhho123/cicada3301.git
neuroretransmit__cicada|https://github.com/neuroretransmit/cicada.git
LIST
echo "C3 PASS DONE $(date -u +%FT%TZ)" >> "$E/clone.log"
