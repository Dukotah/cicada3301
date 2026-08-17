"""L5-seed32 — authoritative coverage statement for the seeded-PRNG hypothesis.

Reads every seed-sweep log in the repo (Round 8's two plus this lane's chunk logs and
new-generator log) and prints exactly what fraction of what space has been searched.
Writes coverage.txt.

Run:  python3 coverage.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SS = os.path.normpath(os.path.join(HERE, '..', '..', 'seed_sweep'))
FULL = 2 ** 32
TIMESLICE = 1420070400 - 1293840000        # 2011-01-01 .. 2015-01-01, unix seconds

GENS = {
    0: 'glibc random()%29', 1: 'glibc random() scaled', 2: 'glibc random()%29 +norepeat',
    3: 'MSVC rand()%29', 4: 'MSVC rand() scaled', 5: 'mt19937 init_genrand %29',
    6: 'mt19937 init_genrand double', 7: 'py3 seed(int) randrange(29)',
    8: 'py3 seed(int) int(random()*29)', 9: 'java Random.nextInt(29)',
    10: 'perl int(rand(29)) drand48', 11: 'POSIX lrand48()%29',
    12: 'ruby rand(29) MT mask', 13: 'xorshift32(13,17,5)%29',
}


def merge(ivs):
    """Union of [lo,hi) intervals -> total covered length."""
    ivs = sorted(ivs)
    tot, cur_lo, cur_hi = 0, None, None
    for lo, hi in ivs:
        if cur_lo is None:
            cur_lo, cur_hi = lo, hi
        elif lo <= cur_hi:
            cur_hi = max(cur_hi, hi)
        else:
            tot += cur_hi - cur_lo
            cur_lo, cur_hi = lo, hi
    if cur_lo is not None:
        tot += cur_hi - cur_lo
    return tot


def main():
    cov = {}      # gen -> list of (lo,hi)
    best = {}     # gen -> best score seen
    hits = 0

    def add(g, lo, hi, b):
        cov.setdefault(g, []).append((lo, hi))
        if g not in best or b > best[g]:
            best[g] = b

    for path in (os.path.join(SS, 'results_timeseed.txt'),
                 os.path.join(SS, 'results_full32.txt'),
                 os.path.join(HERE, 'results_newgens.txt')):
        if not os.path.exists(path):
            continue
        for ln in open(path, encoding='utf-8'):
            m = re.search(r'gen=(\d+).*seeds=(\d+)\.\.(\d+)\s+best=([-0-9.]+).*hits>[-0-9.]+=(\d+)', ln)
            if m:
                add(int(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4)))
                hits += int(m.group(5))

    for tag in ('real',):
        p = os.path.join(HERE, f'chunks_{tag}.tsv')
        if not os.path.exists(p):
            continue
        for ln in open(p, encoding='utf-8'):
            f = ln.rstrip('\n').split('\t')
            if len(f) < 7 or f[0] == 'gen':
                continue
            add(int(f[0]), int(f[1]), int(f[2]), float(f[3]))
            hits += int(f[5])

    out = []
    out.append('SEEDED-PRNG COVERAGE — every seed actually searched against LP2 pages 0-54')
    out.append('(decodes = seeds x 2 directions; window 48 runes; interrupter branching on)')
    out.append('')
    out.append(f'{"gen":>3}  {"generator":32s} {"seeds covered":>15} {"of 2^32":>9}  {"best":>9}')
    out.append('-' * 76)
    tot_seeds = 0
    for g in sorted(GENS):
        c = merge(cov.get(g, []))
        tot_seeds += c
        pct = 100.0 * c / FULL
        b = f'{best[g]:.4f}' if g in best else '   -'
        out.append(f'{g:>3}  {GENS[g]:32s} {c:>15,} {pct:>8.3f}%  {b:>9}')
    out.append('-' * 76)
    out.append(f'{"":3}  {"TOTAL":32s} {tot_seeds:>15,} '
               f'{100.0*tot_seeds/(len(GENS)*FULL):>8.3f}% of the 14-generator space')
    out.append(f'{"":3}  {"":32s} {tot_seeds*2:>15,} decodes')
    out.append('')
    out.append(f'HITS above the (now superseded) -12.5 threshold, all logs: {hits}')
    out.append('')
    out.append('Context for the denominator: the 14-generator x 2^32 space is itself a')
    out.append('vanishing slice of the hypothesis. See CENSUS.md — PHP mt_rand, .NET')
    out.append('System.Random, BBS as a real seed space, ISAAC, LFSRs, keystream offsets')
    out.append('!= 0, seeds wider than 32 bits, and the no-seed case (/dev/urandom, dice)')
    out.append('are all outside it.')
    txt = '\n'.join(out)
    print(txt)
    open(os.path.join(HERE, 'coverage.txt'), 'w', encoding='utf-8').write(txt + '\n')


if __name__ == '__main__':
    main()
