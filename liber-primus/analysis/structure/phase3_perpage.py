"""Phase 3 per-page polymorphic attack on pages 14-27.
For each page, throw the full known-Cicada toolkit and record the single best
(method, score, readable). Flag any page < -5.5 with readable fragments."""
import sys, json, itertools
sys.path.insert(0, 'src'); sys.path.insert(0, 'analysis')
from lp import gematria as gp, ciphers, autokey, solve, score
from run_stats import load_pages

sc = score.default()
N = gp.N
pages = load_pages()


def sscore(idxs):
    return sc.score_norm(gp.indices_to_translit(idxs))


def fragments(idxs):
    """Return readable English words found in the translit (length>=4)."""
    t = gp.indices_to_translit(idxs)
    words = ["THE", "AND", "THAT", "WITHIN", "YOU", "ARE", "FOR", "WITH",
             "THIS", "WHICH", "FROM", "HAVE", "NOT", "ALL", "YOUR", "WILL",
             "SHALL", "TRUTH", "DIVINITY", "WISDOM", "PRIMUS", "LIBER",
             "CIRCUMFERENCE", "INSTAR", "KNOW", "SACRED", "MOBIUS", "TUNNEL",
             "REALITY", "CONSCIOUSNESS", "PILGRIM", "ENLIGHTEN", "BELIEVE",
             "MASTER", "PARABLE", "LOSS", "BUFFERS", "COMMAND", "DECEPTION"]
    hits = [w for w in words if w in t]
    return hits, t


best = {}  # page -> rec
per_page_log = {}


def consider(pi, sval, method, idxs):
    frags, t = fragments(idxs)
    rec = {"page": pi, "score": round(sval, 4), "method": method,
           "fragments": frags, "n_frag": len(frags)}
    cur = best.get(pi)
    # prefer higher score; tie-break by fragments
    if cur is None or sval > cur["score"] or (
            abs(sval - cur["score"]) < 1e-9 and len(frags) > cur["n_frag"]):
        rec["translit"] = t[:200]
        best[pi] = rec


for pi in range(14, 28):
    idxs = pages[pi]
    runes_text = gp.indices_to_runes(idxs)
    base_variants = [("plain", idxs), ("atbash", ciphers.atbash_indices(idxs))]

    # 1+2: Atbash, plain shift (all 29), both via stream sign, on plain & atbash
    for name, base in base_variants:
        for sh in range(N):
            shifted_dec = [(x - sh) % N for x in base]
            consider(pi, sscore(shifted_dec), f"{name}+shift-{sh}", shifted_dec)
            shifted_enc = [(x + sh) % N for x in base]
            consider(pi, sscore(shifted_enc), f"{name}+shift+{sh}", shifted_enc)

    # 3: Vigenere short keys length 1-4 over 29 alphabet, both signs, +atbash
    for keylen in range(1, 5):
        # exhaustive only feasible: 29^4 = 707281 * pages — too big for L4.
        # Do L1,L2 exhaustive both signs/atbash; L3,L4 via column hill (vigauto).
        if keylen <= 2:
            for key in itertools.product(range(N), repeat=keylen):
                for sign in (-1, 1):
                    for atb in (False, True):
                        b = ciphers.atbash_indices(idxs) if atb else idxs
                        stream = [key[i % keylen] for i in range(len(b))]
                        dec = ciphers.apply_stream_to_indices(b, stream, sign=sign)
                        consider(pi, sscore(dec),
                                 f"vig L{keylen} key{key} s{sign:+d} atb{atb}", dec)

    # 3b: vigauto column-optimal keys length 1-12 (finds any periodic key)
    for sign in (-1, 1):
        for atb in (False, True):
            b = ciphers.atbash_indices(idxs) if atb else idxs
            for L in range(1, 13):
                # for each column position find shift maximizing per-column English
                # approximate: pick shift minimizing chi via monogram -> but use
                # full quadgram on whole-page after choosing greedy columns is hard;
                # instead brute single-shift per column using monogram freq proxy.
                key = []
                for c in range(L):
                    col = b[c::L]
                    bestsh, bestv = 0, -1e9
                    for sh in range(N):
                        dec = [(x - sh) % N for x in col] if sign == -1 else [(x + sh) % N for x in col]
                        v = sscore(dec) if len(dec) >= 5 else -1e9
                        if v > bestv:
                            bestv, bestsh = v, sh
                    key.append(bestsh)
                stream = [key[i % L] for i in range(len(b))]
                dec = ciphers.apply_stream_to_indices(b, stream, sign=sign)
                consider(pi, sscore(dec), f"vigauto L{L} s{sign:+d} atb{atb}", dec)

    # 4: prime / totient / prime-1 keystreams with per-page offset search
    for sign in (-1, 1):
        for atb in (False, True):
            b = ciphers.atbash_indices(idxs) if atb else idxs
            nlen = len(b)
            for off in range(0, 60):
                ps = ciphers.prime_stream(nlen + off)[off:off + nlen]
                ts = ciphers.totient_stream(nlen + off, start=2)[off:off + nlen]
                pts = ciphers.prime_totient_stream(nlen + off)[off:off + nlen]
                pm1 = [(p - 1) % N for p in ciphers.prime_stream(nlen + off)[off:off + nlen]]
                for nm, stream in (("prime", ps), ("totient", ts),
                                   ("primetot", pts), ("prime-1", pm1)):
                    if len(stream) != nlen:
                        continue
                    dec = ciphers.apply_stream_to_indices(b, stream, sign=sign)
                    consider(pi, sscore(dec),
                             f"key {nm} off{off} s{sign:+d} atb{atb}", dec)

    # 5: autokey (ciphertext + plaintext) per page, seeds + K + sign + atbash
    for atb in (False, True):
        for sign in (-1, 1):
            for seed in range(N):
                d1 = autokey.decrypt_ciphertext_autokey(idxs, seed=seed, sign=sign, atbash=atb)
                consider(pi, sscore(d1), f"autokey-CT seed{seed} s{sign:+d} atb{atb}", d1)
                d2 = autokey.decrypt_plaintext_autokey(idxs, seed=seed, sign=sign, atbash=atb)
                consider(pi, sscore(d2), f"autokey-PT seed{seed} s{sign:+d} atb{atb}", d2)

    print(f"page {pi}: best {best[pi]['score']} {best[pi]['method']} frags={best[pi]['fragments']}", flush=True)

# overall
allrecs = [best[p] for p in sorted(best)]
out = {"range": "14-27", "perPageBest": allrecs}
with open('analysis/structure/phase3_results.json', 'w') as f:
    json.dump(out, f, indent=2)
print("\n=== SUMMARY ===")
gbest = max(allrecs, key=lambda r: r["score"])
print("global best:", gbest["page"], gbest["score"], gbest["method"])
flagged = [r for r in allrecs if r["score"] > -5.5 and r["fragments"]]
print("flagged (<-5.5 + readable):", [(r["page"], r["score"], r["fragments"]) for r in flagged])
