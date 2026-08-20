#!/bin/bash
E=/c/Users/dukot/projects/cicada3301/corpus/E-tooling
cd $E || exit 1
: > gitmeta.tsv
for d in $(ls vendor); do
  g=vendor/$d/.git
  [ -d "$g" ] || { echo -e "$d\t\t\t\t\tNO_GIT" >> gitmeta.tsv; continue; }
  sha=$(git --git-dir=$g rev-parse HEAD 2>/dev/null)
  first=$(git --git-dir=$g log --reverse --format=%cI 2>/dev/null | head -1)
  last=$(git --git-dir=$g log -1 --format=%cI 2>/dev/null)
  n=$(git --git-dir=$g rev-list --count HEAD 2>/dev/null)
  auth=$(git --git-dir=$g log --format=%ae 2>/dev/null | sort -u | paste -sd, - | cut -c1-160)
  rem=$(git --git-dir=$g config --get remote.origin.url 2>/dev/null)
  echo -e "$d\t$sha\t$first\t$last\t$n\t$auth\t$rem" >> gitmeta.tsv
done
echo "GITMETA DONE $(date -u +%FT%TZ)" >> $E/clone.log
