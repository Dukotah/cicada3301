"""The last genuinely-untried structural probes on the unsolved LP2 pages.

Closes the three things prior rounds only argued "by logic" or never ran, so the
one-time-pad-class verdict is airtight and the community needn't re-run them:

  A. F-rune run-length histogram  (recon "Idea 3" gate, never computed).
     If the ciphertext encodes fixed-length blocks/permutations delimited by the
     F interrupter, the gaps between F runes peak sharply at one length. A
     geometric/flat distribution kills the block/permutation-decode family.

  B. Transposition-validity check  (completeness-critic's load-bearing doubt).
     Is the delta=0 hole (no equal neighbours) a real generative rule, or an
     artifact of reading runes in file order? De-transpose at every plausible
     columnar width and re-measure the doublet rate + delta=0 fraction. If the
     hole survives all widths it is structural; if a width erases it, adjacency
     isn't native and the whole "no-repeat" conclusion would need re-deriving.

  C. No-repeat / collision inversion decode  (the delta!=0 family, never run).
     Parameter-free decodes that EXPLOIT c[i]!=c[i-1], scored by IoC (flat=1.0;
     English-class ~1.7). Any decode that lifts IoC decisively is a real lead.

Run: python analysis/crypto_rigor.py
"""
import os, sys
from collections import Counter

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp           # noqa: E402
from lp.stats import ioc_norm, doublet_rate  # noqa: E402

KRIS = os.path.join(ROOT, "data", "krisyotam_runes.txt")
N = 29
F = 0  # the ᚠ interrupter index


def load_pages():
    segs = open(KRIS, encoding="utf-8").read().split("%")
    return [gp.runes_to_indices(s) for s in segs if gp.runes_to_indices(s)]


def delta_zero_frac(idxs):
    if len(idxs) < 2:
        return 0.0
    d = [(idxs[i] - idxs[i-1]) % N for i in range(1, len(idxs))]
    return d.count(0) / len(d)


# ---- A. F-rune run-length histogram --------------------------------------
def probe_A(pages):
    gaps = []
    for p in pages:
        last = -1
        for i, v in enumerate(p):
            if v == F:
                if last >= 0:
                    gaps.append(i - last)
                last = i
    if not gaps:
        print("A. F-run: no F runes"); return
    c = Counter(gaps)
    top = c.most_common(8)
    import statistics as st
    mean = sum(gaps) / len(gaps)
    mode_n = top[0][1]
    print(f"A. F-rune run-length histogram: {len(gaps)} gaps, mean={mean:.2f}, "
          f"median={st.median(gaps)}, max={max(gaps)}")
    print(f"   top gap lengths: {top}")
    peakiness = mode_n / len(gaps)
    print(f"   modal-gap share = {peakiness:.3f} "
          f"({'SHARP PEAK -> block structure plausible' if peakiness > 0.25 else 'no sharp peak -> block/permutation decode unsupported'})")


# ---- B. transposition-validity -------------------------------------------
def columnar(idxs, w):
    rows = [idxs[i:i+w] for i in range(0, len(idxs), w)]
    out = []
    for c in range(w):
        for r in rows:
            if c < len(r):
                out.append(r[c])
    return out


def probe_B(pages):
    base_d0 = sum(delta_zero_frac(p) * (len(p)-1) for p in pages) / sum(len(p)-1 for p in pages)
    base_db = sum(doublet_rate(p) * len(p) for p in pages) / sum(len(p) for p in pages)
    print(f"B. transposition-validity: native delta0={base_d0:.4f} doublet={base_db:.4f}")
    worst = []
    for w in range(2, 41):
        d0s, dbs, wlen = 0, 0, 0
        for p in pages:
            t = columnar(p, w)
            d0s += delta_zero_frac(t) * (len(t)-1)
            dbs += doublet_rate(t) * len(t)
            wlen += len(t)
        d0 = d0s / sum(len(p)-1 for p in pages)
        db = dbs / wlen
        worst.append((w, d0, db))
    # report the widths that most RESTORE doublets toward 3.45% (would mean native order != file order)
    mindb = min(db for _, _, db in worst)
    worst.sort(key=lambda x: x[2])  # lowest doublet first
    print("   widths with LOWEST doublet (closest to native suppression):")
    for w, d0, db in worst[:5]:
        print(f"     w={w:>2}: doublet={db:.4f}")
    print(f"   native(file-order) doublet={base_db:.4f}; min over all transposition widths={mindb:.4f}")
    if base_db < mindb - 1e-6:
        print("   => file-order is the UNIQUE minimum; every transposition RESTORES doublets "
              "toward random (~0.0345). The suppression is specific to file-order adjacency "
              "=> reading order IS native and the no-repeat rule is STRUCTURAL.")
    else:
        print("   => a transposition matches/beats native suppression -> native order in doubt.")


# ---- C. no-repeat / collision inversion decodes --------------------------
def best_rotation_ioc(seq):
    # IoC is rotation-invariant for additive shifts; report as-is
    return ioc_norm(seq)


def probe_C(pages):
    pooled = [i for p in pages for i in p]
    results = {}
    # C1: rank of c[i] in the 28-symbol allowed set (all but previous) -> 0..27
    rank = []
    for i in range(1, len(pooled)):
        prev = pooled[i-1]
        v = pooled[i]
        allowed = [x for x in range(N) if x != prev]
        rank.append(allowed.index(v) if v in allowed else 0)  # rare real doublet -> 0
    results["C1 rank-in-allowed(28)"] = ioc_norm(rank)
    # C2: forward difference (delta), known flat — control
    delta = [(pooled[i]-pooled[i-1]) % N for i in range(1, len(pooled))]
    results["C2 first-difference (control)"] = ioc_norm(delta)
    # C3: cumulative sum / integral (inverts a difference cipher) — control
    cum, s = [], 0
    for v in pooled:
        s = (s + v) % N; cum.append(s)
    results["C3 cumulative-sum (control)"] = ioc_norm(cum)
    # C4: collision-skip un-bump: if c[i] came from p by +1-on-equal, undo:
    #     guess p[i] = c[i] unless c[i]==c[i-1]+1 region; approximate by mapping
    #     each c[i] to (c[i] - count_of_prev_equal) — cheap proxy, scored by IoC
    unbump = []
    for i, v in enumerate(pooled):
        if i and pooled[i-1] == (v - 1) % N:
            unbump.append((v - 1) % N)
        else:
            unbump.append(v)
    results["C4 collision-unbump(+1)"] = ioc_norm(unbump)
    print("C. no-repeat inversion decodes (IoC_norm; flat=1.00, English-class ~1.70):")
    for k, v in results.items():
        flag = "  <-- LANGUAGE SIGNAL" if v > 1.30 else ""
        print(f"   {k:<32}: {v:.4f}{flag}")
    print(f"   (reference: raw ciphertext IoC_norm = {ioc_norm(pooled):.4f})")


if __name__ == "__main__":
    pages = load_pages()[:-2]  # drop solved AN END + PARABLE
    nrunes = sum(len(p) for p in pages)
    print(f"unsolved LP2: {len(pages)} pages, {nrunes} runes\n")
    probe_A(pages); print()
    probe_B(pages); print()
    probe_C(pages)
