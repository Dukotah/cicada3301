#!/bin/bash
# R47-H1: every baseline number in RESULTS.md. Run from anywhere; logs land next to this file. ~15 min.
H=$(cd "$(dirname "$0")" && pwd); R=$(cd "$H/../../../.." && pwd); cd "$R"
export PYTHONUTF8=1
python -u challenges/c7_corpus_forge.py --self-test > "$H/out_c7_selftest.txt" 2>&1; echo "c7 $?" >> "$H/run.log"
python -u challenges/c10_shuffled_lengths.py --self-test --seed 4702 > "$H/out_c10_selftest_4702.txt" 2>&1; echo "c10a $?" >> "$H/run.log"
python -u challenges/c10_shuffled_lengths.py --self-test --seed 4704 > "$H/out_c10_selftest_4704.txt" 2>&1; echo "c10b $?" >> "$H/run.log"
python -u challenges/c10_shuffled_lengths.py challenges/examples/c10_printed_starts.py --n 100 --seed 4702 > "$H/out_c10_example.txt" 2>&1; echo "c10ex $?" >> "$H/run.log"
python -u challenges/c9_rejection_loops.py --self-test --v3 --plants 40 --seed 4701 > "$H/out_c9_selftest_40.txt" 2>&1; echo "c9 $?" >> "$H/run.log"
python -u challenges/c9_rejection_loops.py challenges/examples/c9_reference_decoder.py --plants 12 --seed 4706 > "$H/out_c9_example.txt" 2>&1; echo "c9ex $?" >> "$H/run.log"
python -u challenges/c8_register_scorer.py --self-test --seed 4703 > "$H/out_c8_selftest.txt" 2>&1; echo "c8 $?" >> "$H/run.log"
python -u challenges/c8_register_scorer.py challenges/examples/c8_example_scorer.py --heldout data/keys/armada19/stoker_dracula.txt --pos 50 --null 500 --beam-null 100 --seed 4707 > "$H/out_c8_example.txt" 2>&1; echo "c8ex $?" >> "$H/run.log"
python -u -I "$H/baseline_extra.py" > "$H/out_c8_extra.txt" 2>&1; echo "c8extra $?" >> "$H/run.log"
echo "baselines done $(date -Iseconds)" >> "$H/run.log"
