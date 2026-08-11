#!/usr/bin/env bash
# Non-English references for the word-length channel.
# LP2's rune-word lengths are longer than English can explain even with all 458
# interrupters counted as nulls, so the plaintext language is a live question.
# Latin and Old English are the two candidates the Cicada canon points at.
set -u
cd "$(dirname "$0")/lang" || exit 1
get() { # id name
  [ -s "$2.txt" ] && { echo "have $2"; return; }
  if curl -sfL -m 60 -o "$2.txt" "https://www.gutenberg.org/cache/epub/$1/pg$1.txt" \
     && [ -s "$2.txt" ]; then
    echo "ok   $2 ($(wc -c < "$2.txt") bytes)"
  else
    rm -f "$2.txt"; echo "FAIL $2 ($1)"
  fi
}
# Latin
get 10657 latin_caesar_gallic
get 218   latin_maybe_218
get 12800 latin_maybe_12800
get 8194  latin_vulgate_maybe
get 28    latin_maybe_28
get 21765 misc_21765
# Old English / Anglo-Saxon originals
get 9701  oe_maybe_9701
get 16451 oe_maybe_16451
get 17381 oe_maybe_17381
# Welsh (Mabinogion source language)
get 47015 welsh_maybe
echo "--- have ---"; ls -la
