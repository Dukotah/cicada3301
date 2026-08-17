import os,sys; sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..'))
import lib_numchannel as nc
import random, json, math
from collections import Counter

RAW = os.path.join(nc.ROOT, "data", "krisyotam_runes.txt")

def isrune(ch): return 0x16A0 <= ord(ch) <= 0x16FF

# ---------------------------------------------------------------- parse
# Walk the RAW file. Ignore newlines (they are line-wrap, not content).
# Record the sequence of tokens: each token is either a rune, or an inline
# separator among '-','/','.'. We also track run-length: how many runes
# occur between consecutive separators.
def parse():
    data = open(RAW, encoding="utf-8").read()
    tokens = []          # ('R', idx) or ('S', sepchar)
    for ch in data:
        if isrune(ch):
            tokens.append(('R', ch))
        elif ch in '-/.':
            tokens.append(('S', ch))
        # else (newline, %, &, $, digits, section signs) -> metadata, skip
    return tokens

def sep_sequence(tokens):
    """The ordered sequence of separator TYPES."""
    return [t[1] for t in tokens if t[0] == 'S']

def run_lengths(tokens):
    """Number of runes between consecutive separators (leading/trailing runs incl)."""
    runs = []
    cur = 0
    for kind, val in tokens:
        if kind == 'R':
            cur += 1
        else:
            runs.append(cur)
            cur = 0
    runs.append(cur)
    return runs

# ---------------------------------------------------------------- scorers
SEP_ORDER = ['-', '/', '.']   # ternary alphabet
SEP_TO_INT = {c: i for i, c in enumerate(SEP_ORDER)}

def seps_to_bits_binary(seps, group='dash_vs_rest'):
    """Map sep types to bits.  Several sensible binarizations."""
    if group == 'dash_vs_rest':
        return [0 if s == '-' else 1 for s in seps]
    if group == 'dot_vs_rest':
        return [1 if s == '.' else 0 for s in seps]
    if group == 'slash_vs_rest':
        return [1 if s == '/' else 0 for s in seps]
    raise ValueError(group)

def bits_to_bytes_text(bits, msb_first=True, offset=0):
    b = bits[offset:]
    chars = []
    for i in range(0, len(b) - 7, 8):
        byte = b[i:i+8]
        if not msb_first:
            byte = byte[::-1]
        v = 0
        for x in byte:
            v = (v << 1) | x
        chars.append(v)
    return chars

def printable_frac(bytelist):
    if not bytelist: return 0.0
    p = sum(1 for v in bytelist if 32 <= v <= 126)
    return p / len(bytelist)

def bytes_as_str(bytelist):
    return "".join(chr(v) if 32 <= v <= 126 else '.' for v in bytelist)

def score_text(s):
    return nc.eng_norm_text(s)

# ternary -> base3 -> bytes
def seps_to_ternary_bytes(seps, digits_per=5):
    """Group ternary digits (0,1,2) into chunks; interpret in base3 as a value.
    5 base-3 digits -> 0..242, fits a byte-ish range."""
    vals = [SEP_TO_INT[s] for s in seps]
    out = []
    for i in range(0, len(vals) - digits_per + 1, digits_per):
        v = 0
        for d in vals[i:i+digits_per]:
            v = v*3 + d
        out.append(v)
    return out

# run-length integer stream decoders
def runs_mod29_text(runs):
    return "".join(nc.gp.IDX_TO_TRANS[v % nc.N] for v in runs)

def runs_ascii_text(runs):
    return "".join(chr(v) if 32 <= v <= 126 else '.' for v in runs)

# ================================================================ MAIN
report = {"lens": "S2", "channels": {}}

tokens = parse()
seps = sep_sequence(tokens)
runs = run_lengths(tokens)
nrunes = sum(1 for t in tokens if t[0] == 'R')

print(f"parsed: {nrunes} runes, {len(seps)} separators")
print("sep hist:", Counter(seps))
print(f"run-length stream len={len(runs)} min={min(runs)} max={max(runs)} mean={sum(runs)/len(runs):.2f}")

# ---------------------------------------------------------------- POSITIVE CONTROL
# Encode a short English message as a separator-TYPE (ternary) sequence and
# recover it through the SAME ternary-decode machinery.
def encode_msg_ternary(msg, digits_per=5):
    """Each char -> its byte value -> base3 digits (5 of them) -> sep chars."""
    seq = []
    for ch in msg:
        v = ord(ch)
        ds = []
        for _ in range(digits_per):
            ds.append(v % 3); v //= 3
        ds = ds[::-1]
        seq.extend(SEP_ORDER[d] for d in ds)
    return seq

CTRL_MSG = "THE PRIMES ARE SACRED"
ctrl_seps = encode_msg_ternary(CTRL_MSG)
ctrl_bytes = seps_to_ternary_bytes(ctrl_seps)
ctrl_str = bytes_as_str(ctrl_bytes)
ctrl_score = score_text(ctrl_str)
ctrl_ok = (CTRL_MSG in ctrl_str) and (ctrl_score >= -5.5)
print(f"\n[CONTROL] planted='{CTRL_MSG}' recovered='{ctrl_str}' score={ctrl_score:.3f} recovered_exact={CTRL_MSG in ctrl_str}")
report["control"] = {"planted": CTRL_MSG, "recovered": ctrl_str,
                     "score": ctrl_score, "exact": CTRL_MSG in ctrl_str, "ok": bool(ctrl_ok)}

# also verify a binary-channel control: encode msg as dash/slash bits and recover
def encode_msg_binary(msg):
    bits = []
    for ch in msg:
        v = ord(ch)
        for k in range(7, -1, -1):
            bits.append((v >> k) & 1)
    return ['-' if b == 0 else '/' for b in bits]
cb_seps = encode_msg_binary(CTRL_MSG)
cb_bits = seps_to_bits_binary(cb_seps, 'dash_vs_rest')
cb_bytes = bits_to_bytes_text(cb_bits, msb_first=True)
cb_str = bytes_as_str(cb_bytes)
cb_ok = CTRL_MSG in cb_str
print(f"[CONTROL-bin] recovered='{cb_str}' exact={cb_ok}")
report["control_bin"] = {"recovered": cb_str, "exact": bool(cb_ok)}

CONTROL_PASSED = bool(ctrl_ok and cb_ok)

# ---------------------------------------------------------------- CHANNEL (a) sep-type -> bits/bytes/text
def channel_binary(seps, group, msb_first, offset):
    bits = seps_to_bits_binary(seps, group)
    byts = bits_to_bytes_text(bits, msb_first, offset)
    s = bytes_as_str(byts)
    return score_text(s), printable_frac(byts), s

best_a = None
for group in ['dash_vs_rest', 'dot_vs_rest', 'slash_vs_rest']:
    for msb in (True, False):
        for off in range(8):
            sc, pf, s = channel_binary(seps, group, msb, off)
            cand = (sc, group, msb, off, pf, s)
            if best_a is None or sc > best_a[0]:
                best_a = cand
print(f"\n[a binary] best score={best_a[0]:.3f} group={best_a[1]} msb={best_a[2]} off={best_a[3]} printable={best_a[4]:.2f}")
print("   text:", best_a[5][:80])

# null for channel (a): shuffle sep types, rerun best config
def null_a(seps, n=200):
    vals = []
    r = random.Random(3301)
    base = list(seps)
    for k in range(n):
        r2 = random.Random(3301 + k)
        sh = base[:]; r2.shuffle(sh)
        sc, pf, s = channel_binary(sh, best_a[1], best_a[2], best_a[3])
        vals.append(sc)
    return sum(vals)/len(vals), max(vals), vals
mean_a, max_a, _ = null_a(seps)
print(f"[a binary] null mean={mean_a:.3f} max={max_a:.3f}")
report["channels"]["a_binary"] = {"best": best_a[0], "config": {"group": best_a[1], "msb": best_a[2], "off": best_a[3]},
                                  "printable": best_a[4], "text": best_a[5][:120],
                                  "null_mean": mean_a, "null_max": max_a}

# ternary variant of (a)
best_at = None
for dpp in (4, 5):
    byts = seps_to_ternary_bytes(seps, dpp)
    s = bytes_as_str(byts)
    sc = score_text(s)
    if best_at is None or sc > best_at[0]:
        best_at = (sc, dpp, printable_frac(byts), s)
def null_at(seps, dpp, n=200):
    vals = []; base = list(seps)
    for k in range(n):
        r2 = random.Random(3301+k); sh = base[:]; r2.shuffle(sh)
        byts = seps_to_ternary_bytes(sh, dpp)
        vals.append(score_text(bytes_as_str(byts)))
    return sum(vals)/len(vals), max(vals)
mean_at, max_at = null_at(seps, best_at[1])
print(f"[a ternary] best score={best_at[0]:.3f} dpp={best_at[1]} null mean={mean_at:.3f} max={max_at:.3f}")
report["channels"]["a_ternary"] = {"best": best_at[0], "dpp": best_at[1], "printable": best_at[2],
                                   "text": best_at[3][:120], "null_mean": mean_at, "null_max": max_at}

# ---------------------------------------------------------------- CHANNEL (b) run-lengths as ints
b_mod29 = runs_mod29_text(runs)
b_ascii = runs_ascii_text(runs)
sc_b29 = score_text(b_mod29)
sc_basc = score_text(b_ascii)
best_b = max((sc_b29, 'mod29', b_mod29), (sc_basc, 'ascii', b_ascii), key=lambda x: x[0])
print(f"\n[b runlen] mod29 score={sc_b29:.3f}  ascii score={sc_basc:.3f}")
print("   mod29 text:", b_mod29[:80])

def null_b(runs, kind, n=200):
    vals = []; base = list(runs)
    for k in range(n):
        r2 = random.Random(3301+k); sh = base[:]; r2.shuffle(sh)
        if kind == 'mod29':
            vals.append(score_text(runs_mod29_text(sh)))
        else:
            vals.append(score_text(runs_ascii_text(sh)))
    return sum(vals)/len(vals), max(vals)
mean_b, max_b = null_b(runs, best_b[1])
print(f"[b runlen] best kind={best_b[1]} null mean={mean_b:.3f} max={max_b:.3f}")
report["channels"]["b_runlen"] = {"mod29": sc_b29, "ascii": sc_basc, "best": best_b[0],
                                  "best_kind": best_b[1], "null_mean": mean_b, "null_max": max_b,
                                  "mod29_text": b_mod29[:120]}

# ---------------------------------------------------------------- CHANNEL (c) placement vs structure
# Does separator placement correlate with word/segment structure vs random?
# Test: chi-square of run-length histogram vs geometric (random placement),
# and whether '.' and '/' cluster at line/segment boundaries.
# Also: mutual information between sep-type and position-in-line is not directly
# accessible post-newline-strip; instead measure run-length regularity.
rl = Counter(runs)
mean_rl = sum(runs)/len(runs)
# variance ratio vs geometric (random sep placement would give ~geometric runs)
var = sum((x-mean_rl)**2 for x in runs)/len(runs)
# geometric with same mean has var = mean*(mean+... ) ; for run-lengths >=0, geom var = (1-p)/p^2, mean=(1-p)/p
p = 1/(mean_rl+1)
geo_var = (1-p)/(p*p)
print(f"\n[c placement] run-len mean={mean_rl:.3f} var={var:.3f} geo_var(sameMean)={geo_var:.3f} ratio={var/geo_var:.3f}")
# distinct-per-type run lengths: are runs before '.' longer (word/sentence end)?
runs_before = {'-': [], '/': [], '.': []}
cur = 0
for kind, val in tokens:
    if kind == 'R':
        cur += 1
    else:
        runs_before[val].append(cur); cur = 0
for c in SEP_ORDER:
    arr = runs_before[c]
    if arr:
        print(f"   runs before '{c}': n={len(arr)} mean={sum(arr)/len(arr):.2f}")
report["channels"]["c_placement"] = {
    "run_mean": mean_rl, "run_var": var, "geo_var": geo_var, "var_ratio": var/geo_var,
    "mean_run_before": {c: (sum(runs_before[c])/len(runs_before[c]) if runs_before[c] else None) for c in SEP_ORDER}
}

# ---------------------------------------------------------------- verdict
all_best = [
    ("a_binary", best_a[0], max_a),
    ("a_ternary", best_at[0], max_at),
    ("b_runlen", best_b[0], max_b),
]
overall = max(all_best, key=lambda x: x[1])
best_score = overall[1]
null_max = overall[2]
HIT = bool(CONTROL_PASSED and best_score >= -5.5 and best_score >= null_max + 0.5)
if not CONTROL_PASSED:
    verdict = "INCONCLUSIVE"
elif HIT:
    verdict = "HIT"
else:
    verdict = "NEGATIVE"

report["overall"] = {"best_channel": overall[0], "best_score": best_score,
                     "null_max": null_max, "control_passed": CONTROL_PASSED,
                     "hit": HIT, "verdict": verdict}

print(f"\n==== S2 VERDICT: {verdict} ====")
print(f"control_passed={CONTROL_PASSED} best={overall[0]} score={best_score:.3f} null_max={null_max:.3f} bar>=-5.5 and >=null_max+0.5")

json.dump(report, open(os.path.join(os.path.dirname(__file__), "results.json"), "w"), indent=2)
print("wrote results.json")
