"""Confusable-tolerant substring match (H1').

Justified by the C-2 positive control: the band reader recovers a PLANTED
'THEPRIMESARESACRED' at 93.8% per-glyph, but emits 'THEPRLMESARESACRE' -- one I->L
substitution inside the shape-confusable family R9 named (U<->Y, O/A/AE, L<->W, C<->I,
I<->L).  An EXACT-substring detector therefore fails on a correctly recovered plant, so an
exact detector cannot be used to declare a negative.  This is the confusable-tolerant form:
a hit is a known string of length >= 8 matched with at most  substitutions, each of
which must lie inside a named confusable family.
"""
FAMILIES = [set('UY'), set('OA'), {'AE', 'A', 'O'}, set('LW'), set('CI'), set('IL'),
            set('EF'), set('BP'), set('MN'), set('SZ'), set('CK')]


def _confusable(a, b):
    if a == b:
        return True
    for f in FAMILIES:
        if a in f and b in f:
            return True
    return False


def fuzzy_find(hay, needle, maxsub=1):
    n, m = len(hay), len(needle)
    if m > n:
        return None
    for i in range(n - m + 1):
        bad = 0
        ok = True
        for j in range(m):
            if hay[i + j] != needle[j]:
                if bad >= maxsub or not _confusable(hay[i + j], needle[j]):
                    ok = False
                    break
                bad += 1
        if ok:
            return (i, bad, hay[i:i + m])
    return None
