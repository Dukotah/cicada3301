"""Campaign XV -- P4  DOUBLET FORENSICS.

LP2 is OTP-class with a SOFT no-repeat filter (~83% doublet suppression, Campaign XI).
~86 doublets SURVIVE the filter. Treat those survivors as a fingerprint / side-channel.

If the filter is memoryless rejection-sampling (Campaign XI's model), the survivors are
i.i.d. accidents: positions ~ uniform, doubled VALUES ~ uniform, inter-doublet GAPS ~
geometric, and no readable decode. Any departure is HIDDEN STRUCTURE.

GATE (declared before run):
  * distribution test p < 0.001 non-uniform  => HIDDEN STRUCTURE (signal fires)
  * any decode score_norm > -5.2             => SIDE-CHANNEL MESSAGE (signal fires)
  * else positions-uniform / values-uniform / gaps-geometric = NULL
    => filter is memoryless rejection sampling (refines Campaign XI).

Cheap, all-measurement. Reproduce:
  PYTHONUTF8=1 python analysis/campaign15/P4-doublet-forensics.py
"""
import os, sys, math
import numpy as np
from scipy import stats as sps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SRC = os.path.join(os.path.dirname(ROOT), "src")
sys.path.insert(0, SRC)
from lp import gematria as gp, score as scoremod

N = gp.N                       # 29
RUNE = gp.RUNE_TO_IDX
INT = gp.RUNE_TO_IDX[gp.INTERRUPTER]   # F-rune index (0)
SCORER = scoremod.default()
DATA = os.path.join(os.path.dirname(ROOT), "data", "krisyotam_runes.txt")
PAYLOAD = os.path.join(ROOT, "pp49_51", "canon_256.bin")

# ---------------------------------------------------------------- build stream
raw = open(DATA, encoding="utf-8").read()
pages_raw = [p for p in raw.split("%") if any(ch in RUNE for ch in p)]
body_pages = pages_raw[:-2] if len(pages_raw) > 2 else pages_raw

stream = []            # rune indices
pg_of = []             # page index per rune
off_of = []            # offset within page per rune
word_start = []        # True if a '-' (word sep) or stronger preceded this rune
line_start = []        # True if '/' or newline preceded this rune
WORD_SEPS = set("-./")
LINE_SEPS = set("/\n")
for pi, p in enumerate(body_pages):
    off = 0
    pend_word = True   # first rune of page starts a word/line
    pend_line = True
    for ch in p:
        if ch in RUNE:
            stream.append(RUNE[ch]); pg_of.append(pi); off_of.append(off)
            word_start.append(pend_word); line_start.append(pend_line)
            off += 1; pend_word = False; pend_line = False
        else:
            if ch in WORD_SEPS: pend_word = True
            if ch in LINE_SEPS: pend_line = True

stream = np.array(stream); pg_of = np.array(pg_of); off_of = np.array(off_of)
word_start = np.array(word_start); line_start = np.array(line_start)
L = len(stream)

# ---------------------------------------------------------------- doublets
# doublet at index i (second of the pair) where stream[i] == stream[i-1]
dpos = np.array([i for i in range(1, L) if stream[i] == stream[i-1]])
dval = stream[dpos]            # the repeated rune value
Ndb = len(dpos)

print("="*72)
print(f"P4 DOUBLET FORENSICS  --  {len(body_pages)} pages, {L} runes")
print(f"doublet count = {Ndb}   rate = {100*Ndb/(L-1):.3f}%   (random 3.448%)")
print("="*72)

results = {}

# ============================================================= (a) POSITIONS
print("\n(a) POSITIONS vs uniform  +  GAP distribution vs geometric")
# KS: positions normalized to [0,1] against uniform
u = dpos / (L - 1)
ks_pos = sps.kstest(u, "uniform")
print(f"  KS positions vs Uniform(0,1):  D={ks_pos.statistic:.4f}  p={ks_pos.pvalue:.4g}")
results["ks_pos_p"] = ks_pos.pvalue

# inter-doublet gaps
gaps = np.diff(dpos)
mean_gap = gaps.mean()
print(f"  gaps: n={len(gaps)}  mean={mean_gap:.1f}  min={gaps.min()}  max={gaps.max()}")
# geometric MLE: p_hat = 1/mean(gap)  (gaps >=1). Fit geometric on support k>=1.
p_hat = 1.0 / mean_gap
# KS of gaps vs fitted geometric CDF (discrete -> use as continuous approx + exact chi2)
def geom_cdf(k, p):    # P(X<=k), X>=1
    return 1.0 - (1.0 - p) ** np.floor(k)
ks_gap = sps.kstest(gaps, lambda k: geom_cdf(k, p_hat))
print(f"  geometric MLE p_hat={p_hat:.4f} (=> mean {1/p_hat:.1f})")
print(f"  KS gaps vs Geometric(p_hat):   D={ks_gap.statistic:.4f}  p={ks_gap.pvalue:.4g}")
results["ks_gap_p"] = ks_gap.pvalue
# chi2 gaps binned vs geometric expectation
edges = [1, 30, 60, 100, 150, 250, int(gaps.max())+1]
obs, _ = np.histogram(gaps, bins=edges)
cdf_e = geom_cdf(np.array(edges, float), p_hat)
exp = (np.diff(cdf_e)) * len(gaps)
# renormalize expected to sum to observed total (cover tail)
exp = exp * (obs.sum() / exp.sum())
chi2_gap = sps.chisquare(obs, exp)
print(f"  chi2 gaps (binned) vs geometric: chi2={chi2_gap.statistic:.2f}  p={chi2_gap.pvalue:.4g}")
results["chi2_gap_p"] = chi2_gap.pvalue

# ============================================================= (b) VALUES
print("\n(b) DOUBLED VALUES vs uniform (chi-square, 29 symbols)")
obsv = np.bincount(dval, minlength=N)
expv = np.full(N, Ndb / N)
chi2_val = sps.chisquare(obsv, expv)
print(f"  chi2={chi2_val.statistic:.2f}  df={N-1}  p={chi2_val.pvalue:.4g}")
top = np.argsort(-obsv)[:5]
print("  most-doubled runes:", [(gp.IDX_TO_TRANS[i], int(obsv[i])) for i in top])
results["chi2_val_p"] = chi2_val.pvalue

# ============================================================= (c) CROSS-REF
print("\n(c) CROSS-REFERENCE positions with structure")
# word-boundary / line-start enrichment  (binomial vs stream base rate)
base_ws = word_start.mean(); base_ls = line_start.mean()
db_ws = word_start[dpos].mean(); db_ls = line_start[dpos].mean()
# second-of-pair at a word start is impossible-ish? test the FIRST of pair too
first = dpos - 1
b_ws_hits = int(word_start[dpos].sum())
p_ws = sps.binomtest(b_ws_hits, Ndb, base_ws).pvalue
b_ls_hits = int(line_start[dpos].sum())
p_ls = sps.binomtest(b_ls_hits, Ndb, base_ls).pvalue
print(f"  base word-start rate {base_ws:.3f}; doublet-pos {db_ws:.3f}  binom p={p_ws:.3g}")
print(f"  base line-start rate {base_ls:.3f}; doublet-pos {db_ls:.3f}  binom p={p_ls:.3g}")
# F-rune (interrupter) adjacency: is F over-represented among doubled values,
# or adjacent to doublets?
f_doubled = int((dval == INT).sum())
p_fdbl = sps.binomtest(f_doubled, Ndb, 1.0/N).pvalue
print(f"  F-rune as the DOUBLED value: {f_doubled}/{Ndb} (exp {Ndb/N:.1f})  binom p={p_fdbl:.3g}")
adj = 0
for i in dpos:
    nb = []
    if i-2 >= 0: nb.append(stream[i-2])
    if i+1 < L: nb.append(stream[i+1])
    if INT in nb: adj += 1
# expected prob a given neighbor is F ~ base freq of F
fbase = (stream == INT).mean()
exp_adj_p = 1 - (1-fbase)**2
p_adj = sps.binomtest(adj, Ndb, exp_adj_p).pvalue
print(f"  F adjacent to doublet (i-2/i+1): {adj}/{Ndb} (exp {exp_adj_p*Ndb:.1f})  binom p={p_adj:.3g}")
# page distribution of doublets vs page sizes (chi2)
pg_sizes = np.bincount(pg_of, minlength=len(body_pages))
pg_db = np.bincount(pg_of[dpos], minlength=len(body_pages))
exp_pg = pg_sizes / pg_sizes.sum() * Ndb
mask = exp_pg > 0
chi2_pg = sps.chisquare(pg_db[mask], exp_pg[mask] * (pg_db[mask].sum()/exp_pg[mask].sum()))
print(f"  doublets-per-page vs page sizes: chi2={chi2_pg.statistic:.1f} df={mask.sum()-1} p={chi2_pg.pvalue:.4g}")
results["binom_ws_p"] = p_ws; results["binom_ls_p"] = p_ls
results["binom_fdbl_p"] = p_fdbl; results["chi2_page_p"] = chi2_pg.pvalue

# ============================================================= (d) MOD read
print("\n(d) GAPS / POSITIONS mod n  read as rune indices, quadgram-scored")
best_d = (-99.0, None)
for name, seq in [("gaps", gaps), ("positions", dpos), ("dval", dval)]:
    for m in [N, 26, 24, 13, 5, 7]:
        idxs = (seq % m) % N
        txt = gp.indices_to_translit([int(x) for x in idxs])
        sc = SCORER.score_norm(txt)
        if sc > best_d[0]: best_d = (sc, f"{name} mod {m}")
print(f"  best mod-read score_norm = {best_d[0]:.3f}  ({best_d[1]})   [English ~ -4.0..-4.4]")
results["best_mod_score"] = best_d[0]

# ============================================================= (e) VALUE STRING
print("\n(e) 86 DOUBLED RUNES as a string  (identity / Atbash / all shifts)")
best_e = (-99.0, None)
def score_idx(idxs):
    return SCORER.score_norm(gp.indices_to_translit([int(x) for x in idxs]))
ident = list(dval)
atbash = [(N-1-x) for x in dval]
for name, seq in [("identity", ident), ("atbash", atbash)]:
    sc = score_idx(seq)
    if sc > best_e[0]: best_e = (sc, name)
for sh in range(1, N):
    sc = score_idx([(x+sh) % N for x in dval])
    if sc > best_e[0]: best_e = (sc, f"caesar+{sh}")
    sc = score_idx([(sh-x) % N for x in dval])  # affine-ish reflections
    if sc > best_e[0]: best_e = (sc, f"reflect{sh}")
print(f"  identity: {score_idx(ident):.3f}   atbash: {score_idx(atbash):.3f}")
print(f"  best over identity/atbash/29 shifts/reflections = {best_e[0]:.3f}  ({best_e[1]})")
print("  identity translit:", gp.indices_to_translit(ident)[:80])
results["best_valstr_score"] = best_e[0]

# ============================================================= (f) PRIMES + payload
print("\n(f) POSITIONS vs primes  +  gaps vs pp49-51 payload gap-table")
# sieve primes up to L
def primes_upto(n):
    s = np.ones(n+1, bool); s[:2] = False
    for i in range(2, int(n**0.5)+1):
        if s[i]: s[i*i::i] = False
    return np.nonzero(s)[0]
pr = primes_upto(L)
prime_set = set(int(x) for x in pr)
hits = sum(1 for i in dpos if int(i) in prime_set)
prime_density = len(pr) / L
p_prime = sps.binomtest(hits, Ndb, prime_density).pvalue
print(f"  doublet positions that are prime: {hits}/{Ndb} (exp {prime_density*Ndb:.1f})  binom p={p_prime:.3g}")
# payload as gap table: spearman between first len(gaps) payload bytes and gaps
payload = np.frombuffer(open(PAYLOAD, "rb").read(), dtype=np.uint8).astype(int)
m = min(len(gaps), len(payload))
sp = sps.spearmanr(gaps[:m], payload[:m])
print(f"  spearman(gaps, payload[:{m}]): rho={sp.statistic:+.4f}  p={sp.pvalue:.4g}")
# also payload gaps (diffs) vs doublet gaps
pg_diff = np.diff(payload)
m2 = min(len(gaps), len(pg_diff))
sp2 = sps.spearmanr(gaps[:m2], pg_diff[:m2])
print(f"  spearman(gaps, diff(payload)[:{m2}]): rho={sp2.statistic:+.4f}  p={sp2.pvalue:.4g}")
results["binom_prime_p"] = p_prime
results["spearman_payload_p"] = sp.pvalue

# ============================================================= VERDICT
print("\n" + "="*72)
print("GATE EVALUATION")
dist_ps = {
    "KS positions": results["ks_pos_p"],
    "KS gaps~geom": results["ks_gap_p"],
    "chi2 gaps~geom": results["chi2_gap_p"],
    "chi2 values": results["chi2_val_p"],
    "chi2 page-uniform": results["chi2_page_p"],
    "binom word-start": results["binom_ws_p"],
    "binom line-start": results["binom_ls_p"],
    "binom F-doubled": results["binom_fdbl_p"],
    "binom prime-pos": results["binom_prime_p"],
    "spearman payload": results["spearman_payload_p"],
}
decode_scores = {
    "mod-read": results["best_mod_score"],
    "value-string": results["best_valstr_score"],
}
struct_hits = {k: v for k, v in dist_ps.items() if v is not None and v < 0.001}
decode_hits = {k: v for k, v in decode_scores.items() if v > -5.2}
print("  distribution p-values (gate: any < 0.001 = HIDDEN STRUCTURE):")
for k, v in dist_ps.items():
    flag = "  <-- FIRES" if (v is not None and v < 0.001) else ""
    print(f"    {k:20s}: p = {v:.4g}{flag}")
print("  decode scores (gate: any > -5.2 = SIDE-CHANNEL):")
for k, v in decode_scores.items():
    flag = "  <-- FIRES" if v > -5.2 else ""
    print(f"    {k:20s}: score_norm = {v:.3f}{flag}")

fired = bool(struct_hits) or bool(decode_hits)
if decode_hits:
    verdict = "break"
elif struct_hits:
    verdict = "inconclusive"  # structure but no message -> needs interpretation
else:
    verdict = "null-closed"
print("\n  SIGNAL_FIRED:", fired)
print("  VERDICT:", verdict)
print("="*72)
