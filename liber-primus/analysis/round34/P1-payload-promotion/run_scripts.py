#!/usr/bin/env python3
"""R34-P1: run ORIGINAL scripts (h1_index, payload_skip, payload_ciphertext, numeric2_skip Part A-hex/B) on canon vs resolved inputs.
Usage: run_scripts.py <h1|skip|ct|num2> <canon|resolved|control>.  The original source is exec'd with __file__ = original path;
the only substitution is the input path string(s)."""
import os, sys, io, json, time, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
which, mode = sys.argv[1], sys.argv[2]
INP = lambda tag: os.path.join(HERE, "inputs", tag)
SPEC = {
 "h1":   ("analysis/recon/lp2h_index/h1_index.py", "recon-h1",
          [('os.path.join(ROOT, "analysis/pp49_51/canon_256.bin")', 'os.path.join(INPDIR, "canon_256.bin")')]),
 "skip": ("analysis/campaign18_skip/payload_skip.py", "c18-payload_skip",
          [('os.path.join(ROOT,"analysis","pp49_51",name)', 'os.path.join(INPDIR,name)')]),
 "ct":   ("analysis/campaign18_skip/armada/payload_ciphertext.py", "c18-payload_ciphertext",
          [('os.path.join(ROOT, "analysis", "pp49_51", "canon_256.bin")', 'os.path.join(INPDIR, "canon_256.bin")'),
           ('os.path.join(ROOT, "analysis", "pp49_51", "canon_256_decpref.bin")', 'os.path.join(INPDIR, "canon_256_decpref.bin")')]),
 "hh":   ("analysis/pp49_51/hash_hunt.py", "extra-hash_hunt",
          [('here = os.path.dirname(__file__)', 'here = INPDIR')]),
 "num2": ("analysis/campaign18_skip/armada2/numeric2_skip.py", "c18-numeric2",
          [('os.path.join(ROOT, "analysis", "pp49_51", "canon_256.bin")', 'os.path.join(INPDIR, "canon_256.bin")'),
           ('os.path.join(ROOT, "analysis", "pp49_51", "canon_256_decpref.bin")', 'os.path.join(INPDIR, "canon_256_decpref.bin")'),
           ('os.path.join(ROOT, "analysis", "pp49_51", "canon_256.hex")', 'os.path.join(INPDIR, "canon_256.hex")')]),
}
rel, outd, subs = SPEC[which]
orig = os.path.join(LP, *rel.split("/"))
OUT = os.path.join(HERE, outd)
src = open(orig, encoding="utf-8").read()
tag = "canon" if mode == "control" else mode      # controls use the resolved payload as the key
for a, b in subs:
    assert a in src, (which, a)
    src = src.replace(a, b)
ns = {"__file__": orig, "__name__": "__main__" if which != "num2" else "numeric2_skip", "INPDIR": INP("resolved" if mode == "control" else tag)}
sys.path.insert(0, os.path.dirname(orig))
t0 = time.time()
if mode in ("canon", "resolved") and which in ("h1", "skip", "ct", "hh"):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(src, orig, "exec"), ns)
    open(os.path.join(OUT, f"stdout_{mode}.txt"), "w", encoding="utf-8").write(buf.getvalue())
    print(which, mode, "done %.0fs" % (time.time() - t0)); print(buf.getvalue()[-1800:])
    sys.exit(0)
# ---- num2 and controls need the module namespace
for p in (os.path.join(LP, "src"), os.path.join(LP, "analysis"), os.path.join(LP, "analysis", "campaign18_skip")):
    sys.path.insert(0, p)
if which == "num2":
    exec(compile(src, orig, "exec"), ns)
import numpy as np
if which == "num2" and mode in ("canon", "resolved"):
    pages = [np.array(p, dtype=np.int64) for p in ns["load_pages"]()[:-2]]
    pv = ns["load_payload_bytes"]()
    h, best = ns["sweep_payload_all_offsets"](pv, pages)
    ks_len = max(len(p) for p in pages) * (ns["MAXSKIP"] + 1) + 16
    nh = ns["ks_payload_hex_nibbles"](ks_len)
    h2, best2 = ns["sweep_fixed_key"]("payload_hex_nibbles", np.array(nh[:ks_len], dtype=np.int64), pages, list(range(5)))
    r = {"mode": mode, "variants": list(pv), "B_hits": [(x[0], x[1], x[2], x[3], x[4], x[5]) for x in h], "B_best_screen": best,
         "hexnibble_hits": [(x[0], x[1], x[2], x[3], x[4], x[5]) for x in h2], "hexnibble_best_screen": best2, "elapsed_s": round(time.time() - t0, 1)}
    json.dump(r, open(os.path.join(OUT, f"results_{mode}.json"), "w"), indent=1); print(r)
if mode == "control":
    from lp import score as sc
    import skipdecode as sk
    Q = sc.default()
    plain = ("THEPRIMESARESACREDANDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBEENCRYPTEDKNOWTHISSHADOWSTHEJOURNEYTOWARDTHEENDOFALLTHINGSISNOT"
             "ANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAY")
    P = sk.eng_to_idx(plain)[:120]
    b = np.frombuffer(open(os.path.join(INP("resolved"), "canon_256.bin"), "rb").read(), dtype=np.uint8).astype(np.int64)
    res = {}
    if which == "skip":
        import sweep as SW
        K = np.concatenate([b % 29] * 5)
        for sign in (-1, 1):
            C, nsk, _ = sk.encipher_keyskip(list(P), list(K), sign=sign, supp=0.83, seed=3301)
            pi = SW.beam(np.array(C, dtype=np.int64), K, sign, 0, len(C), 320)
            s = Q.score_norm(sk.idx_to_trans(pi)); rec = sum(1 for x, y in zip(pi, P) if x == y) / len(P)
            res[f"sign{sign}"] = {"score": s, "recovery": rec, "n_skips": int(sum(nsk)), "PASS": s >= -5.5 and rec >= 0.9}
    if which == "num2":
        K = np.tile(b % 29, 12)
        for off in (0, 17):
            C, nsk, _ = sk.encipher_keyskip(list(P), list(K[off:]), sign=-1, supp=0.83, seed=3301)
            ss, sf, tl = ns["_score_page"](np.array(C, dtype=np.int64), K, -1, off, ns["SCREEN_LEN"], ns["SCREEN_BW"], ns["FULL_BW"], len(C))
            res[f"offset{off}"] = {"screen": ss, "full": sf, "translit_head": (tl or "")[:40], "PASS": sf is not None and sf >= -5.5}
    if which == "ct":
        res = {"note": "payload_ciphertext tests the payload as CIPHERTEXT (hypothesis opposite to a key plant); its internal self-checks are the sniff/entropy routines; no planted control in original. Control here = recoverability of a skip-OTP message under a known key via the same skipdecode.beam_decode (the instrument section 1 calls)"}
        K = list(np.tile(b % 29, 12))
        C, nsk, _ = sk.encipher_keyskip(list(P), K, sign=-1, supp=0.83, seed=3301)
        pi = sk.beam_decode(C, K, sign=-1, o=0, beam_w=400, max_skip=3)
        res["beam_decode_known_key"] = {"score": pi["score"], "PASS": pi["score"] >= -5.5}
    json.dump(res, open(os.path.join(OUT, "control.json"), "w"), indent=1); print(json.dumps(res, indent=1))
