import sys, re
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus')
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus/src')
import numpy as np
from src.lp import gematria as gp, score as _score, solve
import attack

N = gp.N
scorer = _score.default()
pages = attack.unsolved_pages()

def idxs_to_runes(idxs):
    return ''.join(gp.IDX_TO_RUNE[i] for i in idxs)

# Stanza first-letter (rune name initial) of each of the 29 stanzas, in poem order.
# Poem order is canonical futhorc, so stanza i corresponds to rune i.
# The first letter of each stanza (the rune-name initial) mapped to a rune index:
stanza_initials = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
# (these ARE the futhorc translit, i.e. identity for canonical order)
sched_initial = [gp.keyword_to_indices(t)[0] for t in stanza_initials]

# Variant schedules to test as a per-position key (each rune i -> sched[i]):
# We treat the schedule as a length-29 repeating Vigenere-style key applied to each page.
schedules = {}
schedules['initial']  = sched_initial                      # identity-ish
# stanza position 1..29 as gematria value -> index mod N
schedules['position'] = [(i) % N for i in range(29)]
# reverse stanza order
schedules['revpos']   = [(28 - i) % N for i in range(29)]
# prime value of each rune (gematria prime) used as shift
schedules['prime']    = [gp.PRIMES[i] % N for i in range(29)]
# stanza word-count as shift (semantic): count words per stanza
poem = open('data/keys/runepoem_translit.txt', encoding='utf-8').read().strip().splitlines()
wc = [len(line.split()) % N for line in poem]
schedules['wordcount'] = wc
# stanza letter-count mod N
lc = [len(re.sub(r'[^A-Za-z]','',line)) % N for line in poem]
schedules['lettercount'] = lc

def repeat(key, L):
    return [key[i % len(key)] for i in range(L)]

best_overall = (-99, None)
for name, sched in schedules.items():
    best = (-99, None)
    for pi, idxs in enumerate(pages):
        c = np.array(idxs)
        L = len(c)
        k = np.array(repeat(sched, L))
        for sign in (+1, -1):
            for atb in (False, True):
                cc = (N-1)-c if atb else c
                for ph in range(29):  # phase of schedule
                    kk = np.array(repeat(sched[ph:]+sched[:ph], L))
                    p = (cc - sign*kk) % N
                    s = scorer.score_norm(gp.indices_to_translit(p.tolist()))
                    if s > best[0]:
                        best = (s, (pi, sign, atb, ph))
    print('schedule %-12s best score_norm=%.3f cfg=%s' % (name, best[0], best[1]))
    if best[0] > best_overall[0]:
        best_overall = (best[0], (name, best[1]))

print('\nBEST OVERALL schedule:', best_overall)
