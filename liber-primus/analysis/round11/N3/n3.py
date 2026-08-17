"""LENS N3 — the whole book (and each segment) as one large integer.

Structure probe, NOT an English-score probe. We concatenate the prime-value
stream nc.v_prime(u) into big integers (per-segment and whole-book), and also
build the mod-29 value stream integer, then ask: is any of these a "round"
number-theoretic object?

Tests per integer:
  - digit count / bit length (does it land on 512-bit / hash-ish / RSA-modulus shapes?)
  - primality (Miller-Rabin, deterministic-ish with many bases + BPSW-lite)
  - small-factor structure (trial division + Pollard-rho for the segment-sized ones)
  - perfect power  n == a**k
  - Mersenne-ish   n == 2**k +/- 1
  - embedded ASCII (bytes of the integer / of the digit string as printable text)
  - base structure (is the concatenation itself base-B ASCII, base64-ish?)

Because "structure" here is categorical, the pre-registered English scorer is the
wrong yardstick. We instead report an OBSERVED structure count vs a size-matched
SHUFFLED-value control: how many segment integers are prime / perfect-power /
Mersenne-ish / land on a notable bit-length, in the real stream vs shuffles.
The English-score decision rule is still computed (for the concatenated-digit text)
so the harness has a score_norm/null_max to log, but the verdict is driven by
whether real structure exceeds the shuffle control.

Positive control: verify primality + factor code on KNOWN inputs (Mersenne primes,
known composites with known factors, a known RSA-shape semiprime, perfect powers).
"""
import os, sys, math, random, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import lib_numchannel as nc

# CPython 3.11+ caps int<->str at 4300 digits; the whole-book prime concat is
# ~26k digits. Raise the limit so concat_int / str() work on the big integers.
try:
    sys.set_int_max_str_digits(200000)
except AttributeError:
    pass

random.seed(3301)

# ------------------------------------------------------------ number theory
def is_prime(n):
    """Deterministic Miller-Rabin for n < 3.3e24 via fixed bases; strong for larger."""
    if n < 2:
        return False
    # Size guard (round-11 bound): primality of the ~100k-bit whole-book concatenation
    # is not a meaningful cryptographic test and is out of compute scope. Skip > 20k bits.
    if n.bit_length() > 20000:
        return None
    small = [2,3,5,7,11,13,17,19,23,29,31,37]
    for p in small:
        if n % p == 0:
            return n == p
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    # bases: deterministic set covers < 3.3e24; add random bases for big n
    bases = list(small)
    for _ in range(8):
        bases.append(random.randrange(2, min(n - 2, 1 << 40)))
    for a in bases:
        a %= n
        if a == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True

def pollard_rho(n, max_iter=200_000):
    """Bounded Pollard-rho; returns a nontrivial factor or None if max_iter hit."""
    if n % 2 == 0:
        return 2
    if n == 1:
        return 1
    for _ in range(6):  # a few restarts with fresh c
        x = random.randrange(2, n)
        y = x
        c = random.randrange(1, n)
        d = 1
        it = 0
        while d == 1 and it < max_iter:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = math.gcd(abs(x - y), n)
            it += 1
        if 1 < d < n:
            return d
    return None

def factor(n, budget=200, td_limit=100_000):
    """Return prime factors (with multiplicity). Bounded: trial-divide to td_limit,
    then a capped number of Pollard-rho attempts. Large cofactors are returned as
    ('COMPOSITE_UNFACTORED', m) rather than burning unbounded time."""
    factors = []
    d = 2
    while d * d <= n and d < td_limit:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1 if d == 2 else 2
    stack = [n] if n > 1 else []
    calls = 0
    while stack:
        m = stack.pop()
        if m == 1:
            continue
        if is_prime(m):
            factors.append(m)
            continue
        calls += 1
        if calls > budget:
            factors.append(('COMPOSITE_UNFACTORED', m))
            continue
        # Size guard (round-11 bound): Pollard-rho only finds small factors; on a
        # cofactor this large it cannot succeed and would burn the whole budget.
        # Marking it unfactored is the honest, fast outcome (no signal lost).
        if m.bit_length() > 200:
            factors.append(('COMPOSITE_UNFACTORED', m))
            continue
        f = pollard_rho(m)
        if f is None or f == m or f == 1:
            factors.append(('COMPOSITE_UNFACTORED', m))
            continue
        stack.append(f)
        stack.append(m // f)
    return factors

def is_perfect_power(n):
    if n < 4:
        return None
    for k in range(2, n.bit_length() + 1):
        lo, hi = 1, 1 << ((n.bit_length() // k) + 2)
        while lo <= hi:
            mid = (lo + hi) // 2
            p = mid ** k
            if p == n:
                return (mid, k)
            if p < n:
                lo = mid + 1
            else:
                hi = mid - 1
    return None

def mersenne_ish(n):
    """Return ('2^k-1'|'2^k+1', k) if n is within 1 of a power of two."""
    b = (n + 1).bit_length() - 1
    if (1 << b) - 1 == n:
        return ('2^%d-1' % b, b)
    b2 = n.bit_length() - 1
    if (1 << b2) + 1 == n:
        return ('2^%d+1' % b2, b2)
    return None

# ------------------------------------------------------------ integer builders
def concat_int(values):
    """Concatenate decimal representations of a value stream into one integer."""
    return int("".join(str(v) for v in values))

def digit_string(values):
    return "".join(str(v) for v in values)

def bytes_from_int(n):
    length = (n.bit_length() + 7) // 8
    return n.to_bytes(length, 'big')

def printable_ratio(bs):
    if not bs:
        return 0.0
    p = sum(1 for b in bs if 32 <= b < 127)
    return p / len(bs)

# notable bit lengths to watch for
NOTABLE_BITS = {128:'128', 160:'SHA1/160', 224:'SHA224', 256:'SHA256', 384:'SHA384',
                512:'SHA512/512-bit', 1024:'RSA-1024', 2048:'RSA-2048', 4096:'RSA-4096'}

def bit_note(bl):
    # exact hit or within 4 bits (concat is decimal so exact is rare; report nearest)
    best = None
    for b in NOTABLE_BITS:
        if abs(bl - b) <= 4:
            if best is None or abs(bl - b) < abs(bl - best):
                best = b
    return NOTABLE_BITS.get(best) if best is not None else None

# ------------------------------------------------------------ structure scan
def scan_integer(name, values, deep_factor=False):
    n = concat_int(values)
    ds = digit_string(values)
    bl = n.bit_length()
    rec = {
        'name': name,
        'n_values': len(values),
        'digits': len(ds),
        'bits': bl,
        'bit_note': bit_note(bl),
        'is_prime': None,
        'perfect_power': is_perfect_power(n) if len(ds) < 60 else 'skip(too big)',
        'mersenne_ish': mersenne_ish(n),
    }
    # primality: cheap for segment-sized, expensive for whole-book but MR is fast
    rec['is_prime'] = is_prime(n)
    # ASCII embedding of the integer's raw bytes
    bs = bytes_from_int(n)
    rec['byte_printable_ratio'] = round(printable_ratio(bs), 3)
    if deep_factor and not rec['is_prime']:
        f = factor(n, budget=2000)
        rec['factors'] = [x if not isinstance(x, tuple) else list(x) for x in f]
        # RSA-shape = exactly two large prime factors of similar size
        primes = [x for x in f if isinstance(x, int)]
        rec['rsa_shape'] = (len(primes) == 2 and len(f) == 2 and
                            all(is_prime(p) for p in primes) and
                            0.4 < math.log(primes[0]) / math.log(primes[1]) < 2.5
                            if len(primes) == 2 else False)
    return rec

# ------------------------------------------------------------ POSITIVE CONTROL
def positive_control():
    checks = []
    # 1. Mersenne primes
    m31 = 2**31 - 1  # prime
    m67 = 2**67 - 1  # composite (Cole 1903): 193707721 * 761838257287
    checks.append(('is_prime(2^31-1)=True', is_prime(m31) is True))
    checks.append(('is_prime(2^67-1)=False', is_prime(m67) is False))
    checks.append(('is_prime(2^61-1)=True', is_prime(2**61-1) is True))
    # 2. known factorization
    f67 = sorted([x for x in factor(m67) if isinstance(x, int)])
    checks.append(('factor(2^67-1)=[193707721, 761838257287]',
                   f67 == [193707721, 761838257287]))
    # 3. RSA-ish semiprime factors recovered
    p, q = 1000003, 1000033
    n = p * q
    fpq = sorted([x for x in factor(n) if isinstance(x, int)])
    checks.append(('factor(1000003*1000033) recovered', fpq == [p, q]))
    # 4. perfect power
    checks.append(('perfect_power(2^90)=(2,90)?',
                   is_perfect_power(2**90) is not None))
    checks.append(('perfect_power(7^13)', is_perfect_power(7**13) == (7, 13)))
    checks.append(('perfect_power(prime) is None', is_perfect_power(1000003) is None))
    # 5. mersenne_ish detector
    checks.append(('mersenne_ish(2^127-1)', mersenne_ish(2**127-1) == ('2^127-1', 127)))
    checks.append(('mersenne_ish(2^64+1)', mersenne_ish(2**64+1) == ('2^64+1', 64)))
    # 6. PLANT: known prime concatenation recovers as prime
    #    build a value stream whose concat is a known prime, confirm we detect it.
    known_prime = 2**89 - 1  # Mersenne prime
    # (direct detection already covered; this asserts the scanner path)
    rec = scan_integer('control_plant_M89', list(map(int, str(known_prime))))
    checks.append(('scan concat of M89 digits: prime detected',
                   rec['is_prime'] is True))
    ok = all(v for _, v in checks)
    return ok, checks

# ------------------------------------------------------------ null control
def structure_vector(seq_values_list):
    """Given a list of segment value-streams, count structural hits."""
    n_prime = 0
    n_ppow = 0
    n_mers = 0
    n_bitnote = 0
    for vals in seq_values_list:
        n = concat_int(vals)
        if is_prime(n):
            n_prime += 1
        if len(digit_string(vals)) < 60 and is_perfect_power(n):
            n_ppow += 1
        if mersenne_ish(n):
            n_mers += 1
        if bit_note(n.bit_length()):
            n_bitnote += 1
    return {'prime': n_prime, 'perfect_power': n_ppow,
            'mersenne_ish': n_mers, 'bit_note': n_bitnote,
            'total': n_prime + n_ppow + n_mers}

def main():
    out = {'lens': 'N3', 'title': 'whole book as one integer / number-theoretic structure'}

    # ---- positive control
    ok, checks = positive_control()
    out['control_passed'] = ok
    out['control_checks'] = [{'check': c, 'ok': v} for c, v in checks]
    print("POSITIVE CONTROL:", "PASS" if ok else "FAIL")
    for c, v in checks:
        print(f"  [{'ok' if v else 'XX'}] {c}")
    if not ok:
        out['verdict'] = 'INCONCLUSIVE'
        json.dump(out, open(os.path.join(os.path.dirname(__file__), 'results.json'), 'w'), indent=2)
        return out

    # ---- REAL DATA ----
    segs = nc.segments()
    unsolved_segs = segs[:-2]           # 0..54 unsolved
    u = nc.unsolved()

    # per-segment integers (prime-value concatenation)
    seg_records = []
    print("\nPER-SEGMENT prime-value concatenation integers:")
    for i, s in enumerate(unsolved_segs):
        vals = nc.v_prime(s)
        rec = scan_integer('seg%02d' % i, vals, deep_factor=True)
        seg_records.append(rec)
    # summarize notable segment hits
    notable = [r for r in seg_records
               if r['is_prime'] or r['perfect_power'] not in (None, 'skip(too big)')
               or r['mersenne_ish'] or r['bit_note'] or r.get('rsa_shape')]
    out['segment_records'] = seg_records
    out['segment_notable'] = notable
    print(f"  segments scanned: {len(seg_records)}")
    print(f"  primes among segment integers: {sum(1 for r in seg_records if r['is_prime'])}")
    print(f"  perfect powers: {sum(1 for r in seg_records if r['perfect_power'] not in (None,'skip(too big)'))}")
    print(f"  mersenne-ish: {sum(1 for r in seg_records if r['mersenne_ish'])}")
    print(f"  bit-note (near hash/RSA length): {sum(1 for r in seg_records if r['bit_note'])}")
    print(f"  rsa-shape semiprime: {sum(1 for r in seg_records if r.get('rsa_shape'))}")
    for r in notable:
        print("   NOTABLE", r['name'], 'prime' if r['is_prime'] else '',
              r['perfect_power'] if r['perfect_power'] not in (None,'skip(too big)') else '',
              r['mersenne_ish'] or '', r['bit_note'] or '', 'RSA' if r.get('rsa_shape') else '')

    # whole-book integers
    print("\nWHOLE-BOOK integers:")
    whole_prime = scan_integer('WHOLE_prime_concat', nc.v_prime(u))
    whole_idx   = scan_integer('WHOLE_primeindex_concat', nc.v_prime_index(u))
    whole_tot   = scan_integer('WHOLE_totient_concat', nc.v_totient(u))
    # mod-29 value stream as one integer
    mod29_vals = [i % nc.N for i in u]
    whole_mod29 = scan_integer('WHOLE_mod29_concat', mod29_vals)
    for r in (whole_prime, whole_idx, whole_tot, whole_mod29):
        print(f"  {r['name']}: digits={r['digits']} bits={r['bits']} "
              f"prime={r['is_prime']} bit_note={r['bit_note']} "
              f"mersenne={r['mersenne_ish']} ppow={r['perfect_power']} "
              f"byte_printable={r['byte_printable_ratio']}")
    out['whole_book'] = {'prime': whole_prime, 'prime_index': whole_idx,
                         'totient': whole_tot, 'mod29': whole_mod29}

    # ASCII / base embedding check on whole-book digit string
    ds = digit_string(nc.v_prime(u))
    out['whole_digit_len'] = len(ds)
    # try reading the raw big-int bytes as text
    bs = bytes_from_int(concat_int(nc.v_prime(u)))
    out['whole_byte_printable_ratio'] = round(printable_ratio(bs), 3)

    # ------------- NULL CONTROL: shuffle the whole value stream, re-segment ----
    print("\nNULL CONTROL (shuffled value stream, size-matched):")
    real_vec = structure_vector([nc.v_prime(s) for s in unsolved_segs])
    print("  REAL:", real_vec)
    seg_lens = [len(s) for s in unsolved_segs]
    null_totals = []
    null_primes = []
    NDRAW = 200
    for k in range(NDRAW):
        sh = nc.shuffled(u, 3301 + k)
        # re-segment shuffled stream to same segment sizes
        chunks = []
        pos = 0
        for L in seg_lens:
            chunks.append(nc.v_prime(sh[pos:pos+L]))
            pos += L
        v = structure_vector(chunks)
        null_totals.append(v['total'])
        null_primes.append(v['prime'])
    import statistics
    out['null'] = {
        'draws': NDRAW,
        'real_total': real_vec['total'],
        'real_prime': real_vec['prime'],
        'null_total_mean': round(statistics.mean(null_totals), 3),
        'null_total_max': max(null_totals),
        'null_prime_mean': round(statistics.mean(null_primes), 3),
        'null_prime_max': max(null_primes),
    }
    print("  null total  mean=%.2f max=%d  (real=%d)" %
          (statistics.mean(null_totals), max(null_totals), real_vec['total']))
    print("  null primes mean=%.2f max=%d  (real=%d)" %
          (statistics.mean(null_primes), max(null_primes), real_vec['prime']))

    # ------------- English-scorer bookkeeping (per decision rule) -------------
    # score the concatenated-digit text of the whole prime stream, and its null.
    def digit_text_score(seq):
        # map digits 0-9 into rune index space cyclically then english-score
        return nc.eng_norm([int(c) for c in digit_string(nc.v_prime(seq)) if False] or [0])
    # digits aren't runes; the honest English yardstick is the mod-29 letter text.
    real_score = nc.eng_norm(u)
    nmean, nmax, _ = nc.null_band(nc.eng_norm, u, n=200)
    out['english_bookkeeping'] = {
        'real_letter_score': round(real_score, 3),
        'null_mean': round(nmean, 3),
        'null_max': round(nmax, 3),
        'note': 'N3 is a structure probe; letter-score included only for the harness log',
    }
    print("\nENGLISH bookkeeping (letter stream): real=%.3f null_mean=%.3f null_max=%.3f"
          % (real_score, nmean, nmax))

    # ------------- VERDICT -------------
    # Structure verdict: real structure count must EXCEED null_max+0.5 to be a HIT.
    struct_hit = real_vec['total'] >= out['null']['null_total_max'] + 1 and real_vec['total'] > 0
    # Also require a whole-book landmark (prime, notable bit-length, RSA/Mersenne).
    landmark = any([whole_prime['is_prime'], whole_prime['bit_note'],
                    whole_prime['mersenne_ish'], whole_prime['perfect_power'] not in (None,'skip(too big)')])
    # English decision rule (for logging): never expected to fire here.
    eng_hit = real_score >= -5.5 and real_score >= nmax + 0.5

    out['best_score'] = round(real_score, 3)
    out['null_max'] = round(nmax, 3)
    out['hit_flag'] = bool(eng_hit)

    if struct_hit or landmark:
        out['verdict'] = 'HIT'
    else:
        out['verdict'] = 'NEGATIVE'
    out['structure_hit'] = struct_hit
    out['whole_book_landmark'] = bool(landmark)

    print("\nVERDICT:", out['verdict'])
    print("  structure_hit:", struct_hit, " whole_book_landmark:", landmark,
          " english_hit:", eng_hit)

    json.dump(out, open(os.path.join(os.path.dirname(__file__), 'results.json'), 'w'), indent=2)
    return out

if __name__ == '__main__':
    main()
