#!/bin/bash
# L8 / I-01 base-rate control: are 3301's OpenPGP algorithm preferences distinctive,
# or are they the era default that every GnuPG of the period emitted?
#
# Sample = PUBLIC PROJECT / ORGANISATION release-signing keys of the 2009-2014 era.
# These are published expressly to be fetched and checked. No private individual is
# being profiled: only the algorithm-preference subpackets are read, and only to
# establish a base rate.
set -u
D="$(dirname "$0")/evidence/baserate"
mkdir -p "$D"
KEYS="
4E2C6E8793298290:tor-browser-developers
ABAF11C65A2970B130ABE3C479BE3E4300411886:linux-kernel-torvalds
90C8019E36C2E964:bitcoin-core-laan
2071B08A33BD3F06:gnupg-release-2011
D8FC66D2:debian-archive-7
DC6DC026:tails-2011
E1B39B6F:apache-release
"
for line in $KEYS; do
  id="${line%%:*}"; name="${line##*:}"
  code=$(curl -s -m 25 -o "$D/$name.asc" -w '%{http_code}' \
    "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x$id&options=mr")
  size=$(stat -c%s "$D/$name.asc" 2>/dev/null || echo 0)
  echo "$name ($id) http=$code bytes=$size"
done
echo "retrieved_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
