#!/bin/bash
set -u
for u in \
  "https://lists.cpunks.org/pipermail/cypherpunks/" \
  "https://cpunks.org/pipermail/cypherpunks/" \
  "https://lists.cpunks.org/archives/list/cypherpunks@lists.cpunks.org/" \
  "https://al-qaeda.net/pipermail/cypherpunks/" \
  "https://cypherpunks.venona.com/date/" \
  "https://mailing-list-archive.cryptoanarchy.wiki/archive/cypherpunks/" \
  "https://mailing-list-archive.cryptoanarchy.wiki/" \
  "https://bitcointalk.org/index.php" \
  "https://web.archive.org/web/2012/https://cpunks.org/pipermail/cypherpunks/"
do
  code=$(curl -sL -m 25 -o /tmp/probe.out -w '%{http_code}' "$u")
  sz=$(stat -c%s /tmp/probe.out 2>/dev/null || echo 0)
  echo "$code $sz  $u"
done
echo "retrieved_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
