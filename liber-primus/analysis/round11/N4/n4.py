"""LENS N4 — digit-plane separation.

Represent nc.v_prime(u) in bases {3,5,7,10}, extract each digit place
(nc.digit_plane). Treat each plane two ways:
  (a) as a mod-29 keystream to decrypt the runes, then score English;
  (b) as its own symbol stream to read directly (map digit-values to text,
      score English).
A message might hide in one plane, invisible to symbol stats.

POSITIVE CONTROL: plant an English message in one digit plane of a synthetic
stream and show the machinery recovers it (score jumps from noise toward
English). NULL via nc.shuffled / nc.null_band, seed 3301, >=200 draws.
HIT bar (PREREG): score_norm >= -5.5 AND >= null_max + 0.5.
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import lib_numchannel as nc
from lp import gematria as gp

N = nc.N  # 29
BASES = [3, 5, 7, 10]

# --------------------------------------------------------------------------
# Mode (b) helper: turn a digit-plane stream (values in 0..base-1) into a
# rune-index stream so we can score it as English with the shared scorer.
# For base <= 29 we map digit value -> rune index directly (0..base-1).
def plane_as_text_score(plane):
    return nc.eng_norm([v % N for v in plane])

# Mode (a) helper: use the plane as a mod-29 keystream to decrypt runes.
def plane_as_keystream_score(cipher_idxs, plane, sign=-1):
    dec = nc.apply_keystream(cipher_idxs, plane, sign=sign)
    return nc.eng_norm(dec)

# --------------------------------------------------------------------------
def planes_for(values, base):
    """All digit planes (places) for a value stream in the given base."""
    mx = max(values)
    places = 0
    v = mx
    while v > 0:
        places += 1
        v //= base
    if places == 0:
        places = 1
    return [(place, nc.digit_plane(values, base=base, place=place))
            for place in range(places)]

# ==========================================================================
# POSITIVE CONTROL
# ==========================================================================
def positive_control():
    """Plant an English message into ONE digit plane of a synthetic stream,
    then show mode-(b) recovery scores like English while other planes / the
    shuffled null stay at noise."""
    # English plaintext -> rune indices (0..28)
    parable = nc.segments()[-1]
    msg = parable[:400]  # real runeglish English, indices 0..28

    base = 10
    # Build synthetic prime-magnitude-like integers whose UNITS digit (place 0)
    # encodes the message (mod 10 -> we plant msg%10 there so digit==msg_idx%10),
    # actually plant the full index by using a plane that can hold 0..28:
    # simplest faithful test: base large enough. Use base 29 so one plane holds
    # the whole index; then also test base-10 units carrying (idx % 10) which
    # still injects order/structure a scorer should catch partially.
    import random
    rng = random.Random(3301)

    results = {}

    # --- Control A: base-29, plane 0 carries the message index exactly ---
    baseA = 31  # >29 so digit range covers all indices, ternary-safe
    valsA = []
    for i in range(len(msg)):
        higher = rng.randrange(0, 5)  # random higher digits (noise)
        valsA.append(higher * baseA + msg[i])
    planeA = nc.digit_plane(valsA, base=baseA, place=0)
    recA = nc.eng_norm([v % N for v in planeA])
    # other (noise) plane
    planeA_hi = nc.digit_plane(valsA, base=baseA, place=1)
    noiseA = nc.eng_norm([v % N for v in planeA_hi])
    results['control_exact_plane'] = recA
    results['control_noise_plane'] = noiseA

    # --- Control B: keystream recovery. Plant by ENCRYPTING English with a
    # known plane keystream, then recovering by decrypting with same plane. ---
    baseB = 10
    # random prime-magnitude-ish values
    valsB = [rng.randrange(2, 110) for _ in range(len(msg))]
    ksB = nc.digit_plane(valsB, base=baseB, place=0)  # units-digit keystream
    cipher = nc.apply_keystream(msg, ksB, sign=+1)     # encrypt
    dec = nc.apply_keystream(cipher, ksB, sign=-1)      # decrypt w/ right plane
    recB = nc.eng_norm(dec)
    # wrong plane (tens digit) should stay noise
    ksB_wrong = nc.digit_plane(valsB, base=baseB, place=1)
    dec_wrong = nc.apply_keystream(cipher, ksB_wrong, sign=-1)
    wrongB = nc.eng_norm(dec_wrong)
    results['control_ks_recovered'] = recB
    results['control_ks_wrongplane'] = wrongB
    results['plaintext_score'] = nc.eng_norm(msg)

    return results

# ==========================================================================
# MAIN SWEEP on the real unsolved stream
# ==========================================================================
def run():
    u = nc.unsolved()
    values = nc.v_prime(u)

    trials = []  # (label, score, n_used_for_null)

    for base in BASES:
        for place, plane in planes_for(values, base):
            # Mode (b): read plane directly as text
            sb = plane_as_text_score(plane)
            trials.append({
                'mode': 'read', 'base': base, 'place': place,
                'score': sb, 'stream': plane,
            })
            # Mode (a): plane as mod-29 keystream (both signs)
            for sign in (-1, +1):
                sa = plane_as_keystream_score(u, plane, sign=sign)
                trials.append({
                    'mode': f'keystream{"-" if sign<0 else "+"}',
                    'base': base, 'place': place,
                    'score': sa, 'stream': None, 'sign': sign,
                })

    # best trial
    best = max(trials, key=lambda t: t['score'])

    # Null: recompute at the best trial's config. For a fair null we shuffle
    # the SAME input that produced the best score.
    if best['mode'] == 'read':
        # shuffle the plane stream, score as text
        plane = None
        for base in BASES:
            for place, p in planes_for(values, base):
                if base == best['base'] and place == best['place']:
                    plane = p
        score_fn = lambda s: nc.eng_norm([v % N for v in s])
        nmean, nmax, nvals = nc.null_band(score_fn, plane, n=200)
    else:
        # keystream mode: shuffle the ciphertext (u), decrypt with the fixed
        # plane keystream. This tests whether ORDER of the real stream matters.
        plane = None
        for base in BASES:
            for place, p in planes_for(values, base):
                if base == best['base'] and place == best['place']:
                    plane = p
        sign = best['sign']
        score_fn = lambda s: nc.eng_norm(nc.apply_keystream(s, plane, sign=sign))
        nmean, nmax, nvals = nc.null_band(score_fn, u, n=200)

    return trials, best, (nmean, nmax, nvals)

# ==========================================================================
if __name__ == '__main__':
    print("=== POSITIVE CONTROL ===")
    ctrl = positive_control()
    for k, v in ctrl.items():
        print(f"  {k:26s} {v:8.3f}")
    # control passes if exact-plane read AND keystream recovery jump toward English
    ctrl_pass = (ctrl['control_exact_plane'] > -5.5
                 and ctrl['control_exact_plane'] > ctrl['control_noise_plane'] + 0.5
                 and ctrl['control_ks_recovered'] > -5.5
                 and ctrl['control_ks_recovered'] > ctrl['control_ks_wrongplane'] + 0.5)
    print(f"  CONTROL PASS: {ctrl_pass}")

    print("\n=== REAL STREAM SWEEP ===")
    trials, best, (nmean, nmax, nvals) = run()
    # print all trials sorted
    for t in sorted(trials, key=lambda x: -x['score'])[:12]:
        print(f"  {t['mode']:11s} base={t['base']:2d} place={t['place']}  {t['score']:8.3f}")
    print(f"\n  BEST: {best['mode']} base={best['base']} place={best['place']} "
          f"score={best['score']:.3f}")
    print(f"  NULL (n=200): mean={nmean:.3f} max={nmax:.3f}")
    print(f"  bar: score>=-5.5 AND >= null_max+0.5 ({nmax+0.5:.3f})")

    hit = best['score'] >= -5.5 and best['score'] >= nmax + 0.5
    verdict = 'INCONCLUSIVE'
    if not ctrl_pass:
        verdict = 'INCONCLUSIVE'
    elif hit:
        verdict = 'HIT'
    else:
        verdict = 'NEGATIVE'
    print(f"\n  HIT: {hit}   VERDICT: {verdict}")

    out = {
        'lens': 'N4-digit-plane-separation',
        'control': ctrl,
        'control_pass': ctrl_pass,
        'best': {k: best[k] for k in best if k != 'stream'},
        'null_mean': nmean, 'null_max': nmax,
        'hit': hit, 'verdict': verdict,
        'all_trials': [{k: t[k] for k in t if k != 'stream'} for t in trials],
    }
    with open('results.json', 'w') as f:
        json.dump(out, f, indent=2)
    print("\nwrote results.json")
