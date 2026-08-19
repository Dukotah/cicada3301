"""Round 15 / KDF — the key-stretching sweep. Executes PREREG.md exactly.

    K1  replicate round12/D3's expander control
    K2  plant-and-recover a PBKDF2-derived keystream through THIS harness
    A   broad screen: secrets x 27 KDFs x 3 salts x 2 reductions x sign x atbash x dir
    B   salt expansion over the KDF families that survive A, plus the offset ladder
    C   escalate survivors to page 0 full, then all 12,956 runes

Both gates must PASS before any null is reported as NEGATIVE (PREREG s5).
Each stage checkpoints to results_<stage>.json.

    python3 sweep.py [--nproc N] [--stages K1,K2,A,B,C]
"""
import argparse, json, os, random, sys, time, heapq
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis", "round11"))
sys.path.insert(0, os.path.join(LP, "analysis", "campaign18_skip"))
sys.path.insert(0, os.path.join(LP, "analysis", "round13", "B04"))

import kdf
import lib_numchannel as nc
import skipdecode as sk
import seeds as B04_SEEDS          # reuse B-04's validated dictionary builder

N = 29
HEAD_L = 120
BEAM_W = 400
MAX_SKIP = 3
BAR = -5.5
TOPK = 300

STAGE_A_SALTS = ["empty", "3301", "self"]      # PREREG s4.5
REDUCTIONS = ["mod29", "rej29"]


def log(m):
    print(m, flush=True)
    with open(os.path.join(HERE, "sweep.log"), "a", encoding="utf-8") as f:
        f.write(m + "\n")


def save(name, obj):
    with open(os.path.join(HERE, f"results_{name}.json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, default=str)
    log(f"  -> wrote results_{name}.json")


# ---------------------------------------------------------------- secrets
PASSPHRASES = [
    "THE PRIMES ARE SACRED", "THE TOTIENT FUNCTION IS SACRED",
    "ALL THINGS SHOULD BE ENCRYPTED", "A WARNING", "AN END",
    "THE INSTAR EMERGENCE", "WITHIN THE DEEP WEB THERE EXISTS A PAGE",
    "THEIR NUMBERS ARE THE DIRECTION", "EITHER THE WORDS OR THEIR NUMBERS",
    "KNOW THIS", "SEEK WITHIN", "THE JOURNEY TOWARD THE END OF ALL THINGS",
    "LIBER PRIMUS", "CICADA 3301", "PILGRIM", "INSTAR EMERGENCE",
    "BELIEVE NOTHING FROM THIS BOOK", "FIND YOUR TRUTH", "EXPERIENCE",
    "THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED",
    "WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS",
    "SOME WISDOM", "THE LOSS OF DIVINITY", "MOBIUS", "ADHERE", "DIVINITY",
    "CIRCUMFERENCE", "TOTIENT", "SHADOWS", "AN END WITHIN", "PARABLE",
]


def build_secrets():
    """B-04's `core` subset, plus multi-word passphrases a bare-hash sweep had no reason
    to carry but a KDF sweep must (PREREG s4.1)."""
    ents = B04_SEEDS.build()
    core = B04_SEEDS.core(ents)
    out = list(core)
    for p in PASSPHRASES:
        for form in (p, p.lower(), p.replace(" ", ""), p.replace(" ", "").lower()):
            out.append(("passphrase", form.encode()))
    seen, uniq = set(), []
    for lab, b in out:
        if b in seen:
            continue
        seen.add(b)
        uniq.append((lab, b))
    return uniq


# ---------------------------------------------------------------- workers
_G = {}


def _init(seg, kdfs, salts, reds):
    _G["seg"] = seg
    _G["kdfs"] = kdfs
    _G["salts"] = salts
    _G["reds"] = reds


def _work(chunk):
    seg, kdfs, salts, reds = _G["seg"], _G["kdfs"], _G["salts"], _G["reds"]
    L = len(seg)
    heap, ndec = [], 0
    scores = []
    for lab, secret in chunk:
        for salt in salts:
            for kname in kdfs:
                try:
                    block = kdf.derive(secret, salt, kname)
                except Exception:
                    continue
                for red in reds:
                    K = kdf.expand(block, L + 64, red)
                    Krev = K[::-1]
                    for dname, KK in (("fwd", K), ("rev", Krev)):
                        for sign in (-1, 1):
                            for ab in (0, 1):
                                S = [(N - 1 - c) % N for c in seg] if ab else seg
                                bd = sk.beam_decode(S, KK, sign=sign, o=0,
                                                    beam_w=BEAM_W, max_skip=MAX_SKIP)
                                s = bd["score"]
                                ndec += 1
                                scores.append(s)
                                row = (s, lab, secret.hex(), kname, salt, red,
                                       sign, ab, dname, bd["translit"][:64])
                                if len(heap) < TOPK:
                                    heapq.heappush(heap, row)
                                elif s > heap[0][0]:
                                    heapq.heapreplace(heap, row)
    return heap, ndec, scores


def _row(r):
    s, lab, shex, kname, salt, red, sign, ab, dname, head = r
    return {"score": s, "label": lab, "secret_hex": shex,
            "secret": bytes.fromhex(shex).decode("utf-8", "replace")[:64],
            "kdf": kname, "salt": salt, "reduction": red, "sign": sign,
            "atbash": ab, "dir": dname, "head": head}


def run_stage(seg, secrets, kdfs, salts, reds, nproc, label):
    per = len(kdfs) * len(salts) * len(reds) * 2 * 2 * 2
    log(f"[{label}] secrets={len(secrets)} kdfs={len(kdfs)} salts={len(salts)} "
        f"reds={len(reds)} -> {per * len(secrets):,} decodes on {nproc} procs")
    chunks = [secrets[i:i + 4] for i in range(0, len(secrets), 4)]
    heap, ndec, allsc = [], 0, []
    t0 = time.time()
    with Pool(nproc, initializer=_init, initargs=(seg, kdfs, salts, reds)) as pool:
        for i, (h, nd, sc) in enumerate(pool.imap_unordered(_work, chunks), 1):
            for row in h:
                if len(heap) < TOPK:
                    heapq.heappush(heap, row)
                elif row[0] > heap[0][0]:
                    heapq.heapreplace(heap, row)
            ndec += nd
            allsc.extend(sc[::37])       # subsample for the distribution summary
            if i % 10 == 0 or i == len(chunks):
                el = time.time() - t0
                log(f"    [{label}] {i}/{len(chunks)} chunks  {ndec:,} decodes  "
                    f"{el:.0f}s  ({ndec / max(el, 1e-9):,.0f}/s)  "
                    f"best={max(heap)[0]:.3f}")
    rows = sorted((_row(r) for r in heap), key=lambda d: -d["score"])
    m = sum(allsc) / len(allsc) if allsc else 0
    sd = (sum((x - m) ** 2 for x in allsc) / len(allsc)) ** .5 if allsc else 0
    return {"stage": label, "n_decodes": ndec, "elapsed_s": round(time.time() - t0, 1),
            "best_score": rows[0]["score"] if rows else None, "bar": BAR,
            "hit": bool(rows and rows[0]["score"] >= BAR),
            "over_bar": [d for d in rows if d["score"] >= BAR],
            "sample_mean": m, "sample_sd": sd, "sample_n": len(allsc),
            "top50": rows[:50]}


# ---------------------------------------------------------------- gates
def gate_k1():
    log("\n=== K1 — replicate round12/D3 expander control ===")
    import subprocess
    d3 = os.path.join(LP, "analysis", "round12", "D3")
    p = subprocess.run([sys.executable, os.path.join(d3, "pc_derivedkey.py")],
                       capture_output=True, text=True, timeout=3600)
    got = json.load(open(os.path.join(d3, "results.json"), encoding="utf-8"))
    pc = got.get("positive_control", {})
    ok = (pc.get("beam_correct_seed", 0) >= BAR
          and pc.get("char_recovery", 0) >= 0.90
          and pc.get("rigid_correct_seed", 0) < -6.0)
    log(f"K1 beam={pc.get('beam_correct_seed')} rigid={pc.get('rigid_correct_seed')} "
        f"recovery={pc.get('char_recovery')} -> {'PASS' if ok else 'FAIL'}")
    return {"gate": "K1", "passed": bool(ok), **pc}


def gate_k2(secrets, nproc):
    """PREREG s5 K2: plant a PBKDF2-derived keystream from a secret resident in the
    dictionary, then run the full Stage-A cross product against it."""
    log("\n=== K2 — plant-and-recover through this harness ===")
    secret = b"THE PRIMES ARE SACRED"
    assert any(b == secret for _, b in secrets), "plant secret must be in the dictionary"
    kname, salt, red = "pbkdf2_sha256_10000", "3301", "mod29"

    plain = ("THEPRIMESARESACREDANDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBE"
             "ENCRYPTEDKNOWTHISSHADOWSTHEJOURNEYTOWARDTHEENDOFALLTHINGSISNOT"
             "ANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAY")
    P = sk.eng_to_idx(plain)[:HEAD_L]
    K = kdf.keystream(secret, salt, kname, len(P) + 64, red)
    C, nskip, _ = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301)
    dr = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / (len(C) - 1)
    log(f"K2 plant: kdf={kname} salt={salt} red={red} len={len(C)} "
        f"doublet_rate={dr:.4f} (LP2 is 0.0066)")

    st = run_stage(C, secrets, kdf.KDF_NAMES, STAGE_A_SALTS, REDUCTIONS, nproc, "K2")
    top = st["top50"][0] if st["top50"] else {}
    match = (top.get("secret_hex") == secret.hex() and top.get("kdf") == kname
             and top.get("salt") == salt)
    ok = bool(match and top.get("score", -99) >= BAR)
    log(f"K2 rank#1: {top.get('score'):.3f} secret={top.get('secret')!r} "
        f"kdf={top.get('kdf')} salt={top.get('salt')} red={top.get('reduction')}")
    log(f"K2 planted config ranked #1 = {match}; clears bar = "
        f"{top.get('score', -99) >= BAR} -> {'PASS' if ok else 'FAIL'}")
    return {"gate": "K2", "passed": ok, "planted": {
        "secret": secret.decode(), "kdf": kname, "salt": salt, "reduction": red,
        "n_skips": int(sum(nskip)) if hasattr(nskip, "__iter__") else int(nskip),
        "doublet_rate": round(dr, 6)}, "rank1": top, "top10": st["top50"][:10]}


def null_band(seg, n=200, seed0=3301):
    """PREREG s6: size-matched shuffle null, decoded exactly as the sweep decodes."""
    K = kdf.keystream(b"NULLCONTROL", "3301", "pbkdf2_sha256_1000", len(seg) + 64)
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(seg)
        r.shuffle(s)
        vals.append(sk.beam_decode(s, K, sign=-1, o=0,
                                   beam_w=BEAM_W, max_skip=MAX_SKIP)["score"])
    return sum(vals) / len(vals), max(vals)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nproc", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--stages", default="K1,K2,A,B,C")
    ap.add_argument("--limit", type=int, default=0,
                    help="cap the secret list (smoke runs only; a capped run is NOT a "
                         "valid negative and is labelled SMOKE in the summary)")
    a = ap.parse_args()
    want = [s.strip().upper() for s in a.stages.split(",") if s.strip()]

    t0 = time.time()
    log("=" * 78)
    log("ROUND 15 / KDF — key-stretching keystreams (B-04's declared not-covered region)")
    log(f"stages={want} nproc={a.nproc} beam_w={BEAM_W} max_skip={MAX_SKIP} bar={BAR}")
    log("=" * 78)

    secrets = build_secrets()
    if a.limit:
        # keep the K2 plant secret resident even when capped, or the gate is meaningless
        plant = [e for e in secrets if e[1] == b"THE PRIMES ARE SACRED"]
        secrets = plant + [e for e in secrets if e[1] != b"THE PRIMES ARE SACRED"][:a.limit]
        log(f"*** SMOKE RUN: secret list capped to {len(secrets)}. Not a valid negative. ***")
    UNS = nc.unsolved()
    head = UNS[:HEAD_L]
    log(f"secrets: {len(secrets)}   KDFs: {len(kdf.KDF_NAMES)}   "
        f"salts(A): {STAGE_A_SALTS}   unsolved runes: {len(UNS)}")

    nmean, nmax = null_band(head)
    bar = max(BAR, nmax + 0.5)
    log(f"null(L={HEAD_L}, n=200): mean={nmean:.3f} max={nmax:.3f}  -> HIT bar {bar:.3f}")

    gates = {}
    if "K1" in want:
        gates["K1"] = gate_k1()
        save("gates", gates)
    if "K2" in want:
        gates["K2"] = gate_k2(secrets, a.nproc)
        save("gates", gates)
    gated = all(g.get("passed") for g in gates.values()) if gates else None
    if gates and not gated:
        log("\n*** A GATE FAILED — results below are INCONCLUSIVE, not NEGATIVE (PREREG s5)")

    done = []
    if "A" in want:
        st = run_stage(head, secrets, kdf.KDF_NAMES, STAGE_A_SALTS,
                       REDUCTIONS, a.nproc, "A")
        done.append(st)
        save("A", st)

    if "B" in want and done:
        # Stage B: expand the salt list over the KDF families that scored best in A.
        fams = []
        for d in done[0]["top50"]:
            f = d["kdf"]
            if f not in fams:
                fams.append(f)
            if len(fams) >= 8:
                break
        log(f"\n=== STAGE B — salt expansion over {len(fams)} families surviving A ===")
        log(f"    families: {fams}")
        st = run_stage(head, secrets, fams, list(kdf.SALTS.keys()),
                       REDUCTIONS, a.nproc, "B")
        done.append(st)
        save("B", st)

    best = max((s["best_score"] for s in done if s.get("best_score") is not None),
               default=None)
    over = [h for s in done for h in s.get("over_bar", [])]
    verdict = ("SMOKE" if a.limit
               else "INCONCLUSIVE" if (gates and not gated)
               else "NO-STAGES-RUN" if not done
               else "HIT" if over else "NEGATIVE")
    summary = {
        "verdict": verdict, "smoke_limit": a.limit or None,
        "gates": gates, "gates_passed": gated,
        "best_score": best, "bar": bar, "null_mean": nmean, "null_max": nmax,
        "n_over_bar": len(over), "over_bar": over[:50],
        "secrets": len(secrets), "kdfs": len(kdf.KDF_NAMES),
        "stages": [{k: s[k] for k in ("stage", "n_decodes", "elapsed_s",
                                      "best_score", "sample_mean", "sample_sd", "hit")}
                   for s in done],
        "total_decodes": sum(s["n_decodes"] for s in done),
        "elapsed_s": round(time.time() - t0, 1),
    }
    save("summary", summary)
    log("\n" + "=" * 78)
    log(f"VERDICT: {verdict}   best={best} vs bar={bar:.3f}   "
        f"decodes={summary['total_decodes']:,}   "
        f"elapsed={summary['elapsed_s'] / 60:.1f} min")
    log("=" * 78)


if __name__ == "__main__":
    main()
