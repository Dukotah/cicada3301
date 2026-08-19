#!/bin/bash
# FRESH esoteric/philosophical/mystical corpus (NOT in campaign12/13, armada18/19).
set -u
D="/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round12/C2/texts"
mkdir -p "$D"
UA="Mozilla/5.0 (research)"
pg(){ # name id
  local name="$1.txt" id="$2"
  [ -s "$D/$name" ] && { echo "skip $name"; return; }
  curl -sL --max-time 90 -A "$UA" "https://www.gutenberg.org/cache/epub/$id/pg$id.txt" -o "$D/$name"
  local sz=$(stat -c%s "$D/$name" 2>/dev/null||echo 0)
  [ "$sz" -lt 3000 ] && { echo "FAIL $name ($sz)"; rm -f "$D/$name"; } || echo "ok   $name ($sz)"
}
url(){ # name fullurl
  local name="$1.txt"
  [ -s "$D/$name" ] && { echo "skip $name"; return; }
  curl -sL --max-time 90 -A "$UA" "$2" -o "$D/$name"
  local sz=$(stat -c%s "$D/$name" 2>/dev/null||echo 0)
  [ "$sz" -lt 3000 ] && { echo "FAIL $name ($sz)"; rm -f "$D/$name"; } || echo "ok   $name ($sz)"
}

# --- Neoplatonism / late antiquity ---
pg plotinus_enneads_mackenna 71455
pg plotinus_select_works 16929
pg apuleius_golden_ass 1666
pg epictetus_discourses 10661
pg seneca_letters 56075
pg plato_phaedo 1658
pg plato_phaedrus 1636

# --- Christian mysticism (fresh; not Eckhart/Kempis1/Cloud/DarkNight already tried) ---
pg swedenborg_heaven_hell 33443
pg swedenborg_divine_love_wisdom 32020
pg swedenborg_new_jerusalem 33244
pg boehme_aurora 49582
pg kempis_imitation_alt 1653
pg william_law_serious_call 41453
pg inge_christian_mysticism 43477
pg underhill_mysticism 45332
pg underhill_practical_mysticism 24459
pg james_varieties_religious 621
pg augustine_city_of_god 45304
pg aquinas_summa_part1 17611

# --- Renaissance esoterica / Hermetic-adjacent (fresh) ---
pg bruno_heroic_enthusiasts 19833

# --- Kabbalah (Ginsburg -- fresh, prior had Bahir/Zohar/Yetzirah/Mathers) ---
pg ginsburg_kabbalah 69243

# --- Apocalyptic / apocryphal (Charles Enoch -- fresh vs Laurence) ---
pg enoch_charles 77935

# --- Comparative religion / myth (fresh) ---
pg frazer_golden_bough 3623

# --- archive.org / globalgrey fallbacks for esoterica w/o clean PG txt ---
url alghazali_alchemy_happiness "https://www.globalgreyebooks.com/content/books/ebooks/alchemy-of-happiness.txt"
url theologia_germanica "https://archive.org/stream/theologiagermani00winkuoft/theologiagermani00winkuoft_djvu.txt"
url waite_holy_kabbalah "https://archive.org/stream/holykabbalah00awai/holykabbalah00awai_djvu.txt"
url achad_qbl "https://www.globalgreyebooks.com/content/books/ebooks/qbl-bride-formula.txt"
url iamblichus_mysteries "https://archive.org/stream/iamblichusonmyst00iamb/iamblichusonmyst00iamb_djvu.txt"
url dee_hieroglyphic_monad "https://archive.org/stream/johndeeshierogly00deejuoft/johndeeshierogly00deejuoft_djvu.txt"
url sepher_yetzirah_westcott "https://www.globalgreyebooks.com/content/books/ebooks/sepher-yetzirah.txt"
url emerald_tablet_hermetic "https://www.globalgreyebooks.com/content/books/ebooks/hermetic-and-alchemical-writings-of-paracelsus-vol1.txt"
url meister_eckhart_pfeiffer "https://archive.org/stream/meistereckhartfr00eckh/meistereckhartfr00eckh_djvu.txt"
url porphyry_life_plotinus "https://archive.org/stream/selectworksofplo00plot/selectworksofplo00plot_djvu.txt"
