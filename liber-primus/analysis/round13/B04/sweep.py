"""ROUND 13 / B-04 — the derived-key dictionary sweep driver.

Executes the pre-registered plan in PREREG.md exactly:

    G1  replicate round12/D3's control verbatim
    G2  plant-recover through THIS harness at real Stage-A settings
    A   broad screen   2165 seeds x 16 gens x 5 reds x sign x atbash x dir, offset 0
    B   offsets        504 core seeds x 16 x 2 reds x ... x 10 offsets
    C   per-page       504 core seeds x 16 x 2 reds x ... x 55 page heads
    D   deepen         top configs of A/B/C re-decoded on page 0 full, then all 12,956

Both gates must PASS before any stage result is reported as NEGATIVE (PREREG s4).
Each stage checkpoints to results_<stage>.json as it finishes, so a kill mid-run
still leaves every completed stage on disk.

Run:  python3 sweep.py [--nproc N] [--stages G1,G2,A,B,C,D]
"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import harness as H
import seeds as S
import ks

OUT = HERE
BAR = -5.5                      # PREREG s5, the -5.5 floor binds at L=120 and L=100
TOPK = 300


def log(msg):
    print(msg, flush=True)
    with open(os.path.join(OUT, "sweep.log"), "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def save(name, obj):
    p = os.path.join(OUT, f"results_{name}.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, default=str)
    log(f"  -> wrote {os.path.relpath(p, OUT)}")


def stage_summary(name, r):
    """Condense a stage result for the checkpoint file (drop the bulky rows tail)."""
    rows = sorted(r["rows"], key=lambda d: -d["score"])
    return {
        "stage": name,
        "n_decodes": r["n_decodes"],
        "elapsed_s": round(r["elapsed_s"], 1),
        "rate_per_s": round(r["n_decodes"] / max(r["elapsed_s"], 1e-9), 1),
        "best_score": rows[0]["score"] if rows else None,
        "bar": BAR,
        "hit": bool(rows and rows[0]["score"] >= BAR),
        "over_bar": [d for d in rows if d["score"] >= BAR],
        "top50": rows[:50],
        "hist": r["hist"],
        "hist_stats": H.hist_stats(r["hist"]),
        "axis_best": r.get("axis_best", {}),
    }


# ---------------------------------------------------------------- gates
def gate_g1():
    """PREREG s4 G1 — replicate D3's published control verbatim."""
    log("\n=== G1 — replicate round12/D3/pc_derivedkey.py ===")
    d3 = os.path.abspath(os.path.join(HERE, "..", "..", "round12", "D3"))
    sys.path.insert(0, d3)
    import subprocess
    t0 = time.time()
    p = subprocess.run([sys.executable, os.path.join(d3, "pc_derivedkey.py")],
                       capture_output=True, text=True, timeout=3600)
    log(p.stdout[-3000:])
    if p.returncode != 0:
        log("G1 FAILED to execute:\n" + p.stderr[-2000:])
        return {"gate": "G1", "passed": False, "why": "execution error",
                "stderr": p.stderr[-2000:]}

    # D3 writes its own results.json; read the published numbers back
    rp = os.path.join(d3, "results.json")
    got = {}
    if os.path.exists(rp):
        got = json.load(open(rp, encoding="utf-8"))
    beam_c = _dig(got, "beam_correct_seed", "beam_correct", "beam", "beam_score")
    rigid_c = _dig(got, "rigid_correct_seed", "rigid_correct", "rigid", "rigid_score")
    beam_w = _dig(got, "beam_wrong_seed", "beam_wrong", "wrong")
    rec = _dig(got, "char_recovery", "recovery")
    ok = (beam_c is not None and beam_c >= BAR
          and (rec is None or rec >= 0.90)
          and (beam_w is None or beam_c - beam_w > 1.0)
          and (rigid_c is None or rigid_c < -6.0))
    log(f"G1 beam(correct)={beam_c} rigid(correct)={rigid_c} "
        f"beam(wrong)={beam_w} recovery={rec}  -> {'PASS' if ok else 'FAIL'}")
    return {"gate": "G1", "passed": bool(ok), "beam_correct": beam_c,
            "rigid_correct": rigid_c, "beam_wrong": beam_w, "char_recovery": rec,
            "elapsed_s": round(time.time() - t0, 1)}


def _dig(d, *keys):
    """Pull the first matching key out of a possibly-nested results dict."""
    if not isinstance(d, dict):
        return None
    for k in keys:
        if k in d and isinstance(d[k], (int, float)):
            return d[k]
    for v in d.values():
        if isinstance(v, dict):
            r = _dig(v, *keys)
            if r is not None:
                return r
        elif isinstance(v, list):
            for it in v:
                r = _dig(it, *keys)
                if r is not None:
                    return r
    return None


def gate_g2(entries, nproc):
    """PREREG s4 G2 — plant a dictionary-resident seed, run the FULL Stage-A cross
    product against the synthetic ciphertext, require the planted config ranks #1."""
    log("\n=== G2 — plant-recover through this harness at Stage-A settings ===")
    plant = H.build_plant() if hasattr(H, "build_plant") else None
    if plant is None:
        plant = _default_plant()
    C, truth = plant["C"], plant["truth"]
    log(f"G2 plant: seed={truth['seed']!r} gen={truth['gen']} red={truth['red']} "
        f"sign={truth['sign']} atbash={truth['atbash']} dir={truth['dir']} "
        f"len={len(C)} doublet_rate={truth.get('doublet_rate')}")

    bundle = {"entries": entries, "gens": list(ks.GEN_NAMES),
              "reds": list(ks.RED_NAMES), "signs": (-1, 1), "atbs": (0, 1),
              "dirs": ("fwd", "rev"), "offs": (0,)}
    r = H.run_configs(C, bundle, nproc=nproc, topk=TOPK)
    rows = sorted(r["rows"], key=lambda d: -d["score"])
    top = rows[0] if rows else {}
    hit = bool(rows and top["score"] >= BAR)
    match = (str(top.get("seed_label", "")).find(truth["seed_label"]) >= 0
             or top.get("seed_hex") == truth["seed_hex"])
    ok = hit and match
    log(f"G2 rank#1: score={top.get('score')} seed={top.get('seed_label')} "
        f"gen={top.get('gen')} red={top.get('red')}")
    log(f"G2 planted config ranked #1 = {match}; clears bar = {hit}  "
        f"-> {'PASS' if ok else 'FAIL'}")
    return {"gate": "G2", "passed": bool(ok), "planted": truth,
            "rank1": _clean(top), "top10": [_clean(d) for d in rows[:10]],
            "n_decodes": r["n_decodes"], "elapsed_s": round(r["elapsed_s"], 1)}


def _clean(d):
    """Drop the raw-bytes field run_configs attaches, so the row is JSON-safe."""
    return {k: v for k, v in d.items() if k != "seed_bytes"}


def _default_plant():
    """Plant per PREREG s4 G2: seed b'THE PRIMES ARE SACRED' (family `slogan`, and so
    genuinely resident in the dictionary), sha256_ctr/mod29, applied under the repo's
    pinned soft key-skip filter at supp=0.83."""
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "campaign18_skip")))
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "round11")))
    import skipdecode as sk
    import lib_numchannel as nc

    seed = b"THE PRIMES ARE SACRED"
    plain = ("THEPRIMESARESACREDANDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBE"
             "ENCRYPTEDKNOWTHISSHADOWSTHEJOURNEYTOWARDTHEENDOFALLTHINGSISNOT"
             "ANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAY")
    P = sk.eng_to_idx(plain)[:H.HEAD_L]
    K = ks.make_ks("sha256_ctr", "mod29", seed, len(P) + 64)
    C, nskip, _used = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301)
    dr = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / max(len(C) - 1, 1)
    return {"C": C,
            "truth": {"seed": seed.decode(), "seed_label": "THE PRIMES ARE SACRED",
                      "seed_hex": seed.hex(), "gen": "sha256_ctr", "red": "mod29",
                      "sign": -1, "atbash": 0, "dir": "fwd",
                      "n_skips": int(sum(nskip)) if hasattr(nskip, "__iter__") else int(nskip),
                      "doublet_rate": round(dr, 6)}}


# ---------------------------------------------------------------- stages
def stage_a(entries, nproc):
    log("\n=== STAGE A — broad screen (PREREG s3.6) ===")
    r = H.run_stage([H.head_segment()], entries, nproc=nproc, topk=TOPK, label="A")
    return stage_summary("A", r)


def stage_b(core, nproc):
    log("\n=== STAGE B — keystream offsets ===")
    r = H.run_stage([H.head_segment()], core, reds=["mod29", "rej29"],
                    offs=(1, 4, 16, 29, 64, 128, 256, 512, 1024, 3301),
                    nproc=nproc, topk=TOPK, label="B")
    return stage_summary("B", r)


def stage_c(core, nproc):
    log("\n=== STAGE C — per-page keystream restarts ===")
    r = H.run_stage(H.page_segments(), core, reds=["mod29", "rej29"],
                    dirs=("fwd",), nproc=nproc, topk=TOPK, label="C")
    return stage_summary("C", r)


def stage_d(prior, nproc):
    """PREREG s5 escalation: re-decode the top configs on page 0 full, then the
    whole 12,956-rune stream. Nothing here is a hit unless it survives both."""
    log("\n=== STAGE D — deepen survivors ===")
    rows = []
    for st in prior:
        rows.extend(st.get("top50", []))
    rows.sort(key=lambda d: -d["score"])
    seen, picks = set(), []
    for d in rows:
        k = (d.get("seed_hex"), d.get("gen"), d.get("red"), d.get("sign"),
             d.get("atbash"), d.get("dir"), d.get("offset"))
        if k in seen:
            continue
        seen.add(k)
        picks.append(d)
        if len(picks) >= 300:
            break
    log(f"escalating {len(picks)} distinct configs")
    out = []
    for seg_name, seg in (("page0_full", H.full_page0()),
                          ("unsolved_full", H.full_unsolved())):
        rr = H.run_stage([seg], _entries_from(picks), nproc=nproc, topk=50,
                         label=f"D:{seg_name}")
        s = stage_summary(f"D_{seg_name}", rr)
        log(f"  {seg_name}: best={s['best_score']} bar={BAR} hit={s['hit']}")
        out.append(s)
    return out


def _entries_from(picks):
    """Rebuild seed entries for the escalation set from their recorded hex."""
    ents = []
    for d in picks:
        h = d.get("seed_hex")
        if not h:
            continue
        ents.append((d.get("seed_label", "?"), bytes.fromhex(h)))
    # de-dup on the bytes, preserving order
    seen, out = set(), []
    for lab, b in ents:
        if b in seen:
            continue
        seen.add(b)
        out.append((lab, b))
    return out


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nproc", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--stages", default="G1,G2,A,B,C,D")
    a = ap.parse_args()
    want = [s.strip().upper() for s in a.stages.split(",") if s.strip()]

    t0 = time.time()
    log("=" * 78)
    log("ROUND 13 / B-04 — derived-key dictionary sweep")
    log(f"stages={want} nproc={a.nproc} bar={BAR} "
        f"beam_w={H.BEAM_W} max_skip={H.MAX_SKIP}")
    log("=" * 78)

    entries = S.build()
    core = S.core(entries)
    log(f"dictionary: {len(entries)} seeds ({len(core)} core), "
        f"{len(ks.GEN_NAMES)} generators, {len(ks.RED_NAMES)} reductions")

    gates = {}
    if "G1" in want:
        gates["G1"] = gate_g1()
        save("gates", gates)
    if "G2" in want:
        gates["G2"] = gate_g2(entries, a.nproc)
        save("gates", gates)

    gated = all(g.get("passed") for g in gates.values()) if gates else None
    if gates and not gated:
        log("\n*** A GATE FAILED — every stage below is INCONCLUSIVE, not NEGATIVE "
            "(PREREG s4). Running anyway so the numbers exist, but they may not be "
            "reported as a negative result. ***")

    done = []
    if "A" in want:
        s = stage_a(entries, a.nproc); done.append(s); save("A", s)
    if "B" in want:
        s = stage_b(core, a.nproc); done.append(s); save("B", s)
    if "C" in want:
        s = stage_c(core, a.nproc); done.append(s); save("C", s)
    if "D" in want and done:
        d = stage_d(done, a.nproc); save("D", d); done.extend(d)

    best = max([s["best_score"] for s in done if s.get("best_score") is not None],
               default=None)
    hits = [h for s in done for h in s.get("over_bar", [])]
    verdict = ("INCONCLUSIVE" if (gates and not gated)
               else "HIT" if hits else "NEGATIVE")
    summary = {"verdict": verdict, "gates": gates, "gates_passed": gated,
               "best_score": best, "bar": BAR, "n_over_bar": len(hits),
               "over_bar": hits[:50],
               "stages": [{k: s[k] for k in
                           ("stage", "n_decodes", "elapsed_s", "rate_per_s",
                            "best_score", "hit")} for s in done],
               "total_decodes": sum(s.get("n_decodes", 0) for s in done),
               "elapsed_s": round(time.time() - t0, 1)}
    save("summary", summary)
    log("\n" + "=" * 78)
    log(f"VERDICT: {verdict}   best={best} vs bar={BAR}   "
        f"decodes={summary['total_decodes']:,}   "
        f"elapsed={summary['elapsed_s'] / 3600:.2f}h")
    log("=" * 78)


if __name__ == "__main__":
    main()
