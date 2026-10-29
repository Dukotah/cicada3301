#!/usr/bin/env python3
"""R33-B1 row B-04: re-feed the 7 payload-derived seeds (corrected payload) to the round13/B04 engine."""
import os, sys, json, time, binascii
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "B04")
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
B04 = os.path.join(LP, "analysis", "round13", "B04")
sys.path.insert(0, B04)
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I1"))
sys.path.insert(0, os.path.join(LP, "analysis", "round32", "I2-multiregister-readjudication"))
sys.path.insert(0, os.path.join(LP, "benchmark"))
import harness as H, ks, seeds as S, control as CT
import skipdecode as sk, driftbeam as DB, adjudicate as AD, null as NU
import numpy as np
assert os.path.dirname(os.path.abspath(AD.__file__)).endswith("I2-multiregister-readjudication")
BAR_LEGACY, BAR_EXACT, BAR_PAIR = -5.5, 7.6342, 7.3835
PP = os.path.join(LP, "analysis", "pp49_51")
canon = open(os.path.join(PP, "canon_256.bin"), "rb").read()
res = open(os.path.join(LP, "analysis", "round19", "C1", "payload_resolved.bin"), "rb").read()
decc = open(os.path.join(PP, "canon_256_decpref.bin"), "rb").read()
dec = bytearray(decc)
for i in (45, 50, 246):
    dec[i] = res[i]
dec = bytes(dec)


def pseeds(b, d):
    return [("canon256_raw", b), ("canon256_rev", b[::-1]), ("canon256_head32", b[:32]), ("canon256_tail32", b[-32:]),
            ("canon256_hex", binascii.hexlify(b).decode().encode()),
            ("canon256_hex", binascii.hexlify(b).decode().upper().encode()),
            ("canon256_decpref", d)]


orig = [(l, s if isinstance(s, bytes) else s.encode()) for l, s in S.build() if l.startswith("canon256")]
mine = pseeds(canon, decc)
assert orig == mine, "seed reconstruction != seeds.py"
E_RES, E_CAN = pseeds(res, dec), mine
changed = [i for i in range(7) if E_RES[i][1] != E_CAN[i][1]]
print("payload-derived seeds: %d; changed by correction: %d %s" % (len(E_RES), len(changed), [E_RES[i][0] for i in changed]), flush=True)


def cross(entries, segs, gens, reds, signs, atbs, dirs, offs):
    nsym = max(offs) + max(len(s[1]) for s in segs) * (H.MAX_SKIP + 2) + 128
    for label, seed in entries:
        for g in gens:
            raw = ks.make_bytes(g, seed, int(nsym * 1.35) + 256)
            for rd in reds:
                base = ks.make_ks(g, rd, seed, nsym, raw=raw)
                for dr in dirs:
                    K = base if dr == "fwd" else base[::-1]
                    for (sn, C0, C1) in segs:
                        for ab in atbs:
                            C = C0 if ab == 0 else C1
                            for sg in signs:
                                for off in offs:
                                    yield label, seed, g, rd, sg, ab, dr, off, sn, K, C


def control():
    out = {}
    P = sk.eng_to_idx(CT.PLAIN)[:H.HEAD_L]
    plants = {"slogan_THE_PRIMES_ARE_SACRED": (b"THE PRIMES ARE SACRED", "sha256_ctr", "mod29"),
              "payload_resolved_tail32": (res[-32:], "sha256_ctr", "mod29")}
    for pn, (pseed, pg, pr) in plants.items():
        K = ks.make_ks(pg, pr, pseed, H.HEAD_L * (H.MAX_SKIP + 2) + 128)
        C, skips, _ = sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301)
        ents = E_RES + ([("slogan", pseed)] if pn.startswith("slogan") else [])
        rows = []
        for (label, seed, g, rd, sg, ab, dr, off, sn, K2, C2) in cross(ents, [H.make_segment("plant", C)], ks.GEN_NAMES, ks.RED_NAMES, (-1, 1), (0, 1), ("fwd", "rev"), (0,)):
            bd = sk.beam_decode(C2, K2, sign=sg, o=off, beam_w=H.BEAM_W, max_skip=H.MAX_SKIP)
            rows.append((bd["score"], seed == pseed and g == pg and rd == pr and sg == -1 and ab == 0 and dr == "fwd", label, bd))
        rows.sort(key=lambda r: -r[0])
        rank = next(i + 1 for i, r in enumerate(rows) if r[1]); hit = rows[rank - 1]
        rec = float(np.mean([a == b for a, b in zip(hit[3]["plain_idx"], P)]))
        out[pn] = {"n_configs": len(rows), "planted_rank": rank, "planted_score": hit[0],
                   "best_other": next(r[0] for r in rows if not r[1]), "recovery": rec,
                   "skips_injected": int(sum(skips)), "PASS": bool(rank == 1 and hit[0] >= BAR_LEGACY and rec >= 0.9)}
        print("control", pn, out[pn], flush=True)
    out["ALL_PASS"] = all(v["PASS"] for v in out.values())
    json.dump(out, open(os.path.join(OUT, "control.json"), "w"), indent=1)
    return out["ALL_PASS"]


STAGES = [("A", dict(segs=lambda: [H.head_segment()], reds=ks.RED_NAMES, dirs=("fwd", "rev"), offs=(0,), L=120)),
          ("B", dict(segs=lambda: [H.head_segment()], reds=["mod29", "rej29"], dirs=("fwd", "rev"),
                     offs=(1, 4, 16, 29, 64, 128, 256, 512, 1024, 3301), L=120)),
          ("C", dict(segs=lambda: H.page_segments(), reds=["mod29", "rej29"], dirs=("fwd",), offs=(0,), L=100))]


def run(tag, entries, stages, rowsfn, do_pair):
    hdr = AD.header("round33/B1/B04-payload-resolved/" + tag,
                    key_space="B-04 payload-derived seeds only (%d), 16 gens x reductions x sign x atbash x dir x offsets/pages per stage" % len(entries),
                    decoder="round13/B04 engine sk.beam_decode beam 400 max_skip 3 (keyskip1) [+ driftbeam pair beam 64 at stage A for resolved]",
                    register_panel="round32/I2 nine-register panel", n_round_adjudicated_reference=10 ** 6)
    f = open(rowsfn, "w"); f.write(json.dumps(hdr) + "\n")
    summ = {}
    for sname, cfg in stages:
        t0 = time.time(); segs = cfg["segs"](); n = 0; best = {"score": -99}; bestp = {"pmax": -99}
        flagged = []; per_seed = {}; rel_best = {}
        for (label, seed, g, rd, sg, ab, dr, off, sn, K, C) in cross(entries, segs, ks.GEN_NAMES, cfg["reds"], (-1, 1), (0, 1), cfg["dirs"], cfg["offs"]):
            for rel in (("exact", "pair") if (do_pair and sname == "A") else ("exact",)):
                if rel == "exact":
                    bd = sk.beam_decode(C, K, sign=sg, o=off, beam_w=H.BEAM_W, max_skip=H.MAX_SKIP)
                else:
                    bd = DB.beam_decode(C, K, sign=sg, o=off, beam_w=64, **DB.PRESETS["pair"])
                a = AD.adjudicate(bd["plain_idx"], translit=bd.get("translit"))
                cfgs = "%s|%s|%s|%s|%s|s%+d|a%d|%s|o%d|%s" % (sname, label, seed.hex()[:16], g, rd, sg, ab, dr, off, sn)
                f.write(json.dumps(AD.to_row(a, "b04:%s:%s" % (rel, cfgs))) + "\n"); n += 1
                sc, pm = float(bd["score"]), float(a["pmax"])
                rec = {"cfg": cfgs, "rel": rel, "score": sc, "pmax": pm, "head": bd["translit"][:48]}
                if sc > best["score"]: best = rec
                if pm > bestp["pmax"]: bestp = rec
                rb = rel_best.setdefault(rel, {"score": -99, "pmax": -99})
                rb["score"] = max(rb["score"], sc); rb["pmax"] = max(rb["pmax"], pm)
                ps = per_seed.setdefault(label + ":" + seed.hex()[:8], {"score": -99, "pmax": -99})
                ps["score"] = max(ps["score"], sc); ps["pmax"] = max(ps["pmax"], pm)
                pbar = BAR_PAIR if rel == "pair" else BAR_EXACT
                if sc >= BAR_LEGACY or pm >= pbar:
                    flagged.append(dict(rec, FLAGGED_FOR_ORACLE=True))
        f.flush()
        summ[sname] = {"n_decodes": n, "elapsed_s": round(time.time() - t0, 1), "L": cfg["L"],
                       "bar_legacy_floor": BAR_LEGACY,
                       "bar_L_aware_threshold_for_N": NU.threshold_for(max(n, 2), segment_len=cfg["L"]),
                       "bar_hitfn20_panelmax": {"exact": BAR_EXACT, "pair": BAR_PAIR},
                       "best_score": best, "best_pmax": bestp, "best_by_relation": rel_best,
                       "flagged": flagged, "per_seed_best": per_seed}
        print(tag, sname, n, "best score %.3f best pmax %.3f flagged %d  %.0fs" % (best["score"], bestp["pmax"], len(flagged), time.time() - t0), flush=True)
    f.close()
    v = AD.validate_store(rowsfn); summ["validate_store"] = {"rows_validated": v["rows_validated"], "ok": True}
    return summ


if __name__ == "__main__":
    t0 = time.time()
    ok = control()
    if not ok:
        json.dump({"INCONCLUSIVE": "control failed"}, open(os.path.join(OUT, "summary.json"), "w")); sys.exit(2)
    out = {"subset": {"n_payload_seeds": 7, "labels": [l for l, _ in E_RES],
                      "changed_by_correction": [E_RES[i][0] for i in changed],
                      "head32_identical": E_RES[2][1] == E_CAN[2][1]}}
    out["resolved"] = run("resolved", E_RES, STAGES, os.path.join(OUT, "sweep_rows.jsonl"), True)
    ch = [E_CAN[i] for i in changed]
    out["canon_comparator"] = run("canon_comparator", ch, STAGES[:2], os.path.join(OUT, "sweep_rows_canon_comparator.jsonl"), False)
    try:
        out["published_lane"] = {s: {"best_score": json.load(open(os.path.join(B04, "results_%s.json" % s)))["best_score"]} for s in "ABC"}
    except Exception as e:
        out["published_lane"] = str(e)
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=str)
    print("DONE", out["elapsed_s"])
