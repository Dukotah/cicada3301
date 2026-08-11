#!/usr/bin/env bash
# Track SKELETON — candidate-plaintext corpus.
# Texts chosen for the Cicada canon (Blake, Emerson, hermetic/gnostic, Norse,
# Old English, eastern scripture) plus controls. Run from analysis/skeleton.
set -u
cd "$(dirname "$0")/corpus" || exit 1
fetch() { # id name
  [ -s "$2.txt" ] && { echo "have $2"; return; }
  for u in "https://www.gutenberg.org/cache/epub/$1/pg$1.txt" \
           "https://www.gutenberg.org/files/$1/$1-0.txt" \
           "https://www.gutenberg.org/ebooks/$1.txt.utf-8"; do
    if curl -sfL -m 60 -o "$2.txt" "$u" && [ -s "$2.txt" ]; then
      echo "ok   $2 ($(wc -c < "$2.txt") bytes)"; return
    fi
  done
  echo "FAIL $2"
}
fetch 574   blake_marriage_heaven_hell
fetch 1934  blake_songs_innocence_experience
fetch 45315 blake_poems
fetch 26   emerson_essays_first
fetch 2945 emerson_essays_second
fetch 205  thoreau_walden
fetch 26839 milton_paradise_lost
fetch 131  bunyan_pilgrims_progress
fetch 2680 aurelius_meditations
fetch 216  laotzu_tao_te_ching
fetch 2388 bhagavad_gita
fetch 30894 kybalion
fetch 44186 corpus_hermeticum_pymander
fetch 1998 nietzsche_zarathustra
fetch 1497 plato_republic
fetch 16328 beowulf
fetch 14833 poetic_edda
fetch 33385 elder_edda
fetch 2383 chaucer_canterbury
fetch 1727 homer_odyssey
fetch 6130 homer_iliad
fetch 10 kjv_bible
fetch 2800 quran
fetch 2010 diary_anne_frank_ctrl
fetch 2701 melville_moby
fetch 84   shelley_frankenstein
fetch 1661 doyle_sherlock
fetch 76   twain_huck
fetch 5200 kafka_metamorphosis
fetch 4363 stoker_dracula
fetch 2554 dostoyevsky_crime
fetch 100  shakespeare_complete
fetch 3207 leviathan_hobbes
fetch 1232 machiavelli_prince
fetch 7370 second_treatise_locke
fetch 3800 apocrypha
fetch 8800 dante_divine_comedy
fetch 1946 dhammapada
fetch 3283 upanishads
fetch 15784 book_of_enoch
echo "--- corpus ---"; ls -la | tail -5; du -sh .
