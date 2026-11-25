"""C8 example submission: the interface only. It wraps the repo's English quadgram scorer, so it scores
ENGLISH; a real submission models a register panel-R36 does not have.

    python challenges/c8_register_scorer.py challenges/examples/c8_example_scorer.py \
        --heldout data/keys/armada19/stoker_dracula.txt --direct
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import _heavy as H  # noqa: E402

REGISTER = "EN_MODERN"     # a label: the checker flags panel names; maintainers check the real register by hand


def score(idx):
    return H.english_score(idx)
