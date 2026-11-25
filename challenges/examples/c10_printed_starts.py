"""C10 example submission: baseline (ii). Tries EVERY key of the family with the jumps at the PRINTED word
starts (the R46-L1 battery's U2b rule), ranks by a rune-bigram score, re-scores the top 64 with the quadgram
score and returns the best decode. Under shuffled lengths it recovers about a third of the runes and passes no
plant (~2.5 s per unit). The same search with the TRUE lengths recovers every plant (baseline (i)).

    python challenges/c10_shuffled_lengths.py challenges/examples/c10_printed_starts.py --n 20
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import c10_shuffled_lengths as C10  # noqa: E402


def attack(C, printed):
    return C10.exhaustive(C, [l for s in printed for l in s])[1]
