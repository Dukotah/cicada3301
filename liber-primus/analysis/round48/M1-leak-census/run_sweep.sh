#!/bin/bash
# Arm B full sweep: all 2^32 seeds per generator, highest toolchain prior first. Appends to sweep.log.
cd "$(dirname "$0")"
for g in drand48 bash42 bash42_32 glibc py27 msvc ansi minstd; do
  echo "START $g $(date -u +%FT%TZ)" >> sweep.log
  ./repro stream.txt $g 0 4294967296 >> sweep.log 2>&1
  echo "END $g $(date -u +%FT%TZ)" >> sweep.log
done
echo "ALL-DONE $(date -u +%FT%TZ)" >> sweep.log
