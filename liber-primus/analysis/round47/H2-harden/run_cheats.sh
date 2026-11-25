#!/bin/bash
# R47-H2: re-run R47-X1's four cheats (AUDIT.md §4 commands) against the hardened checkers. Each must now FAIL
# (exit 1, no "FINISH LINE MET" / "NEW REGISTER"). Logs land next to this file.
H=$(cd "$(dirname "$0")" && pwd); R=$(cd "$H/../../../.." && pwd); cd "$R"
export PYTHONUTF8=1
X=liber-primus/analysis/round47/X1-redteam
T=$(mktemp -d); cp "$X/x1_cheat_c7_manifest.json" "$T/manifest.json"
python -u challenges/c7_corpus_forge.py "$T/manifest.json" --build --seed 1 > "$H/out_cheat_c7.txt" 2>&1; echo "cheat c7 exit $?" >> "$H/run.log"
python -u challenges/c8_register_scorer.py $X/x1_cheat_c8.py --heldout liber-primus/data/keys/armada19/stoker_dracula.txt --direct --pos 50 --null 200 --beam-null 20 --seed 99 > "$H/out_cheat_c8.txt" 2>&1; echo "cheat c8 exit $?" >> "$H/run.log"
python -u challenges/c9_rejection_loops.py $X/x1_cheat_c9.py --plants 40 --seed 99 > "$H/out_cheat_c9.txt" 2>&1; echo "cheat c9 exit $?" >> "$H/run.log"
python -u challenges/c10_shuffled_lengths.py $X/x1_cheat_c10.py --n 20 --seed 99 > "$H/out_cheat_c10.txt" 2>&1; echo "cheat c10 exit $?" >> "$H/run.log"
rm -rf "$T"
