cd "$(dirname "$0")"
for L in 150 240 300; do for k in CICADA-R36I3a-x CICADA-R36I3b-zzz; do
python gen.py $L $k EN_HALFVOWEL 100 feat/${k}_${L}_EN_HALFVOWEL.json
for s in LATIN DE OE EN_KJV; do python gen.py $L $k $s 60 feat/${k}_${L}_$s.json; done
python gen.py $L $k EN_NOVOWEL 1100 feat/${k}_${L}_EN_NOVOWEL.json
done; done
