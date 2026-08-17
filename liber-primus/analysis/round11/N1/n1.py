"""LENS N1 — cumulative-gematria FEEDBACK autokey.

key[i] = f(running_sum of gematria PRIMES recovered so far) mod 29,
for f in {identity-mod29, totient(=sum-1), digit-sum-of-sum}.

Two feedback sources:
  - PLAINTEXT-feedback: running sum accumulates PRIMES[p_recovered]. Self-keying:
    decoder recovers p[i] using key from prior plaintext, then adds PRIMES[p[i]].
  - CIPHERTEXT-feedback: running sum accumulates PRIMES[c[i]] (known ciphertext).
Configs: f in {mod29, totient, digitsum}; sign +/-; forward/reversed stream;
continuous vs per-segment reset. Score decode vs shuffled null (seed 3301).

Run: cd .../round11/N1 && PYTHONUTF8=1 python3 n1.py
"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import lib_numchannel as nc

N = nc.N
PRIMES = nc.PRIMES

# ---- feedback functions f(running_sum) -> key value ----
def f_mod29(s):     return s % N
def f_totient(s):   return (s - 1) % N if s > 0 else 0   # phi of the running sum proxy
def f_digitsum(s):
    while s >= 10:
        s = sum(int(d) for d in str(s))
    return s % N
FUNCS = {"mod29": f_mod29, "totient": f_totient, "digitsum": f_digitsum}

# ---- PLAINTEXT-feedback decrypt (self-keying, left-to-right) ----
def decrypt_pt_feedback(cipher, f, sign):
    """p[i] = (c[i] - sign*f(run)) % N ; then run += PRIMES[p[i]]."""
    p, run = [], 0
    for ci in cipher:
        k = f(run)
        pi = (ci - sign * k) % N
        p.append(pi)
        run += PRIMES[pi]
    return p

# ---- CIPHERTEXT-feedback decrypt (key from known ciphertext prefix) ----
def decrypt_ct_feedback(cipher, f, sign):
    """key[i] = f(sum PRIMES[c[0..i-1]]); p[i]=(c[i]-sign*key[i])%N."""
    p, run = [], 0
    for ci in cipher:
        k = f(run)
        p.append((ci - sign * k) % N)
        run += PRIMES[ci]
    return p

def score_decode(cipher, source, fname, sign):
    f = FUNCS[fname]
    if source == "pt":
        dec = decrypt_pt_feedback(cipher, f, sign)
    else:
        dec = decrypt_ct_feedback(cipher, f, sign)
    return nc.eng_norm(dec), dec

# =====================================================================
# POSITIVE CONTROL FIRST — plant, then recover with the matching config.
# =====================================================================
print("=== POSITIVE CONTROL ===")
parable = nc.segments()[-1]
plant = (parable * 40)[:2000]
s_plant = nc.eng_norm(plant)

# ---- plaintext-feedback encrypt with f_mod29, sign +1 ----
def encrypt_pt(plain, f, sign):
    c, run = [], 0
    for pi in plain:
        c.append((pi + sign * f(run)) % N)
        run += PRIMES[pi]
    return c

ct_pt = encrypt_pt(plant, f_mod29, +1)
s_ct_pt = nc.eng_norm(ct_pt)
s_rec_pt, rec_pt = score_decode(ct_pt, "pt", "mod29", +1)
ctrl_pt_ok = (rec_pt == plant) and (s_ct_pt < s_plant - 1.0)
print(f"PT-feedback  plant={s_plant:.3f}  ct={s_ct_pt:.3f}  recovered={s_rec_pt:.3f}  exact={rec_pt==plant}")

# ---- ciphertext-feedback encrypt with f_mod29, sign +1 ----
def encrypt_ct(plain, f, sign):
    """Inverse of decrypt_ct_feedback: c[i]=(p[i]+sign*f(run))%N; run+=PRIMES[c[i]]."""
    c, run = [], 0
    for pi in plain:
        ci = (pi + sign * f(run)) % N
        c.append(ci)
        run += PRIMES[ci]
    return c

ct_ct = encrypt_ct(plant, f_mod29, +1)
s_ct_ct = nc.eng_norm(ct_ct)
s_rec_ct, rec_ct = score_decode(ct_ct, "ct", "mod29", +1)
ctrl_ct_ok = (rec_ct == plant) and (s_ct_ct < s_plant - 1.0)
print(f"CT-feedback  plant={s_plant:.3f}  ct={s_ct_ct:.3f}  recovered={s_rec_ct:.3f}  exact={rec_ct==plant}")

control_passed = ctrl_pt_ok and ctrl_ct_ok
print(f"CONTROL PASSED = {control_passed}")

# digit-sum / totient sanity: they must also invert cleanly (self-consistency)
for fname in ("totient", "digitsum"):
    ctp = encrypt_pt(plant, FUNCS[fname], +1)
    _, recp = score_decode(ctp, "pt", fname, +1)
    print(f"  self-invert {fname} pt: exact={recp==plant}")

# =====================================================================
# REAL RUN — 12,956 unsolved stream across all configs.
# =====================================================================
print("\n=== REAL RUN: 12,956-rune stream ===")
u = nc.unsolved()
u_rev = u[::-1]

configs = []
for source in ("pt", "ct"):
    for fname in FUNCS:
        for sign in (+1, -1):
            for direction, stream in (("fwd", u), ("rev", u_rev)):
                configs.append((source, fname, sign, direction, stream))

# continuous configs
results = []
for source, fname, sign, direction, stream in configs:
    s, _ = score_decode(stream, source, fname, sign)
    results.append({"mode": "continuous", "source": source, "f": fname,
                    "sign": sign, "dir": direction, "score": s})

# per-segment reset configs (segments()[:-2] = unsolved pages)
segs = nc.segments()[:-2]
for source in ("pt", "ct"):
    for fname in FUNCS:
        for sign in (+1, -1):
            for direction in ("fwd", "rev"):
                dec_all = []
                for seg in segs:
                    st = seg[::-1] if direction == "rev" else seg
                    _, dec = score_decode(st, source, fname, sign)
                    dec_all.extend(dec)
                s = nc.eng_norm(dec_all)
                results.append({"mode": "reset", "source": source, "f": fname,
                                "sign": sign, "dir": direction, "score": s})

results.sort(key=lambda r: r["score"], reverse=True)
print(f"Total configs: {len(results)}")
print("Top 8 configs by score:")
for r in results[:8]:
    print(f"  {r['score']:.3f}  {r['mode']:10s} src={r['source']} f={r['f']:8s} "
          f"sign={r['sign']:+d} dir={r['dir']}")

best = results[0]

# =====================================================================
# NULL — shuffled surrogate scored through the SAME best config.
# Null = apply the winning decode config to shuffled ciphertexts.
# =====================================================================
print("\n=== NULL BAND (best config, 200 shuffles, seed 3301) ===")
def best_score_fn(seq):
    if best["mode"] == "reset":
        # apply per-segment on the shuffled full stream chunked to seg lengths
        dec_all, i = [], 0
        for seg in segs:
            chunk = seq[i:i+len(seg)]; i += len(seg)
            st = chunk[::-1] if best["dir"] == "rev" else chunk
            _, dec = score_decode(st, best["source"], best["f"], best["sign"])
            dec_all.extend(dec)
        return nc.eng_norm(dec_all)
    st = seq[::-1] if best["dir"] == "rev" else seq
    s, _ = score_decode(st, best["source"], best["f"], best["sign"])
    return s

nmean, nmax, nvals = nc.null_band(best_score_fn, u, n=200)
print(f"best_score={best['score']:.3f}  null_mean={nmean:.3f}  null_max={nmax:.3f}")

# ---- decision rule ----
hit = (best["score"] >= -5.5) and (best["score"] >= nmax + 0.5)
verdict = "HIT" if hit else ("INCONCLUSIVE" if not control_passed else "NEGATIVE")
print(f"\nHIT bar: score>=-5.5 AND >=null_max+0.5 ({nmax+0.5:.3f})  -> hit={hit}")
print(f"VERDICT = {verdict}")

out = {
    "lens": "N1",
    "control_passed": control_passed,
    "control_pt_score": round(s_rec_pt, 3),
    "control_ct_score": round(s_rec_ct, 3),
    "best": best,
    "best_score": round(best["score"], 3),
    "null_mean": round(nmean, 3),
    "null_max": round(nmax, 3),
    "hit": hit,
    "verdict": verdict,
    "n_configs": len(results),
    "top8": results[:8],
}
with open(os.path.join(os.path.dirname(__file__), "results.json"), "w") as fh:
    json.dump(out, fh, indent=2)
print("wrote results.json")
