#!/usr/bin/env python3
"""R34-P1: persist SWEEPROW rows (round32/I2 panel) for the sweep-style readers: campaign18 payload_skip and R16-KDF stage A.
Same decoders / loops as the original harness (payload_skip.py source exec'd with sweep.beam wrapped; KDF _work loop in-process, nproc=1)."""
import os, sys, io, json, time, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
which, tag = sys.argv[1], sys.argv[2]
LIMIT = int(sys.argv[3]) if len(sys.argv) > 3 else 0
sys.path[:0] = [os.path.join(LP, "src"), os.path.join(LP, "analysis"), os.path.join(LP, "analysis", "campaign18_skip"),
                os.path.join(LP, "analysis", "round32", "I2-multiregister-readjudication"), os.path.join(LP, "benchmark")]
import numpy as np
import adjudicate as AD
assert os.path.dirname(os.path.abspath(AD.__file__)).endswith("I2-multiregister-readjudication")
INP = os.path.join(HERE, "inputs", tag)
if which == "skip":
    OUT = os.path.join(HERE, "c18-payload_skip"); fn = os.path.join(OUT, f"sweep_rows_{tag}.jsonl")
    f = open(fn, "w"); f.write(json.dumps(AD.header("round34/P1/c18-payload_skip/" + tag, key_space="payload (4 variants fwd/rev, canon+decpref) mod 29 as offset-0 key over each of 55 pages, sign x atbash",
        decoder="campaign18_skip/sweep.beam beam 320 (skip-aware)", register_panel="round32/I2 nine-register panel", n_round_adjudicated_reference=10 ** 6)) + "\n")
    import sweep as SW
    orig = SW.beam; cnt = [0]
    def wrapped(ct2, K, sign, o, length, beam_w):
        pi = orig(ct2, K, sign, o, length, beam_w)
        if LIMIT and cnt[0] >= LIMIT: return pi
        a = AD.adjudicate(pi); f.write(json.dumps(AD.to_row(a, "c18skip:%s:%d:s%+d:o%d:L%d" % (tag, cnt[0], sign, o, length))) + "\n"); cnt[0] += 1
        return pi
    SW.beam = wrapped
    spec_src = open(os.path.join(LP, "analysis", "campaign18_skip", "payload_skip.py"), encoding="utf-8").read()
    spec_src = spec_src.replace('os.path.join(ROOT,"analysis","pp49_51",name)', 'os.path.join(INPDIR,name)')
    if LIMIT: spec_src = spec_src.replace("pages=load_pages()[:-2]", "pages=load_pages()[:-2][:2]")
    buf = io.StringIO(); t0 = time.time()
    with contextlib.redirect_stdout(buf):
        exec(compile(spec_src, os.path.join(LP, "analysis", "campaign18_skip", "payload_skip.py"), "exec"),
             {"__file__": os.path.join(LP, "analysis", "campaign18_skip", "payload_skip.py"), "__name__": "__main__", "INPDIR": INP})
    f.close(); v = AD.validate_store(fn)
    best_pmax = None
    open(os.path.join(OUT, f"rows_stdout_{tag}.txt"), "w").write(buf.getvalue())
    print(which, tag, "rows", cnt[0], "validate", v["rows_validated"], "%.0fs" % (time.time() - t0)); print(buf.getvalue()[:400])
elif which == "kdf":
    sys.path[:0] = [os.path.join(LP, "analysis", "round15", "KDF"), os.path.join(LP, "analysis", "round13", "B04")]
    import binascii, kdf, sweep as KS, skipdecode as sk
    OUT = os.path.join(HERE, "R16-KDF"); fn = os.path.join(OUT, f"sweep_rows_A_{tag}.jsonl")
    b = open(os.path.join(INP, "canon_256.bin"), "rb").read(); d = open(os.path.join(INP, "canon_256_decpref.bin"), "rb").read()
    ents = [("canon256_raw", b), ("canon256_rev", b[::-1]), ("canon256_head32", b[:32]), ("canon256_tail32", b[-32:]),
            ("canon256_hex", binascii.hexlify(b)), ("canon256_hex", binascii.hexlify(b).decode().upper().encode()), ("canon256_decpref", d)]
    head = KS.nc.unsolved()[:KS.HEAD_L]; L = len(head)
    f = open(fn, "w"); f.write(json.dumps(AD.header("round34/P1/R16-KDF-stageA/" + tag, key_space="7 payload-derived secrets x 27 KDFs x 3 salts x 2 reductions x dir x sign x atbash, L=120 head of unsolved stream",
        decoder="round15/KDF sk.beam_decode beam 400 max_skip 3", register_panel="round32/I2 nine-register panel", n_round_adjudicated_reference=10 ** 6)) + "\n")
    n = 0; best = (-99, None); bestp = (-99, None); t0 = time.time()
    for lab, secret in ents:
        for salt in KS.STAGE_A_SALTS:
            for kname in kdf.KDF_NAMES:
                block = kdf.derive(secret, salt, kname)
                for red in KS.REDUCTIONS:
                    K = kdf.expand(block, L + 64, red)
                    for dname, KK in (("fwd", K), ("rev", K[::-1])):
                        for sign in (-1, 1):
                            for ab in (0, 1):
                                S = [(29 - 1 - c) % 29 for c in head] if ab else head
                                bd = sk.beam_decode(S, KK, sign=sign, o=0, beam_w=KS.BEAM_W, max_skip=KS.MAX_SKIP)
                                a = AD.adjudicate(bd["plain_idx"], translit=bd.get("translit"))
                                f.write(json.dumps(AD.to_row(a, "kdf:%s:%s:%s:%s:%s:s%+d:a%d:%s" % (lab, secret.hex()[:8], kname, salt, red, sign, ab, dname))) + "\n"); n += 1
                                if bd["score"] > best[0]: best = (bd["score"], (lab, kname, salt, red, sign, ab, dname))
                                if a["pmax"] > bestp[0]: bestp = (a["pmax"], (lab, kname, salt, red, sign, ab, dname))
                                if LIMIT and n >= LIMIT: break
                            if LIMIT and n >= LIMIT: break
                        if LIMIT and n >= LIMIT: break
                    if LIMIT and n >= LIMIT: break
                if LIMIT and n >= LIMIT: break
            if LIMIT and n >= LIMIT: break
        if LIMIT and n >= LIMIT: break
    f.close(); v = AD.validate_store(fn)
    res = {"tag": tag, "n": n, "best_score": best, "best_pmax": bestp, "validate_rows": v["rows_validated"], "elapsed_s": round(time.time() - t0, 1), "bars": {"legacy": -5.5, "hitfn20_exact": 7.6342, "hitfn20_pair": 7.3835}}
    json.dump(res, open(os.path.join(OUT, f"rows_summary_{tag}.json"), "w"), indent=1, default=str); print(res)
