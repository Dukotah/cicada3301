#!/usr/bin/env python3
"""
ROUND 19 / LANE G3 — the validation gate.

Runs the B-04 seed dictionary through a **real CPython 2.7** interpreter and
through `gen_py27.py`, and requires element-for-element agreement before any
keystream is allowed into Phase 2.

Gates (declared in PREREG.md §4):
  V1  a real CPython 2.7 executes
  V2  gen_py27 == real 2.7.3 over the seed dictionary x 4 reductions   (100 % or FAIL)
  V3  real 2.7.3 == real 2.7.18 on the same vectors
  V4  seed(int) / seed(float) / seed(str)+jumpahead(k) reproduce exactly
  V5  randrange(29) == randint(0,28) == choice(pool) == int(random()*29)  [measured]
  V6  Py2 stream != Py3 stream for the same literal  (the Q5 kill check)
  V7  i386 (32-bit long) branch: validated, or PROVISIONAL with a reason
  V8  scorer-free plant-and-recover through the enumerator

Usage (inside WSL):
    python3 validate_py27.py            # full gate, writes validation.json
    python3 validate_py27.py --quick    # 120-seed sample, for iteration
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]                      # .../cicada3301
B04 = REPO / "liber-primus" / "analysis" / "round13" / "B04"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(B04))

import gen_py27 as G                        # noqa: E402
import seeds as B04SEEDS                    # noqa: E402

HOME = Path(os.path.expanduser("~"))
BUILDS = {
    "2.7.3": {
        "bin": HOME / "py27/root273/usr/bin/python2.7",
        "home": HOME / "py27/root273/usr",
        "ld": [HOME / "py27/root273/lib/x86_64-linux-gnu",
               HOME / "py27/root273/usr/lib/x86_64-linux-gnu"],
        "note": "Ubuntu 12.04 LTS system Python (python2.7_2.7.3-0ubuntu3.19, GCC 4.6.3)",
    },
    "2.7.18": {
        "bin": HOME / "py27/root2718/usr/bin/python2.7",
        "home": HOME / "py27/root2718/usr",
        "ld": [HOME / "py27/root2718/usr/lib/x86_64-linux-gnu"],
        "note": "Ubuntu 20.04 python2.7_2.7.18-13ubuntu1.5 (independent second build)",
    },
    "2.7.3-i386": {
        "bin": HOME / "py27/root273_i386/usr/bin/python2.7",
        "home": HOME / "py27/root273_i386/usr",
        "ld": [HOME / "py27/root273_i386/lib/i386-linux-gnu",
               HOME / "py27/root273_i386/usr/lib/i386-linux-gnu",
               HOME / "py27/root273_i386/lib",
               HOME / "py27/root273_i386/usr/lib"],
        "loader": HOME / "py27/root273_i386/lib/ld-linux.so.2",
        "note": ("Ubuntu 12.04 LTS system Python, 32-bit build "
                 "(python2.7_2.7.3-0ubuntu3.19_i386, GCC 4.6.3): sizeof(long) == 4, "
                 "so hash() and therefore the whole seed image are 32-bit"),
    },
}

NVALS = 64            # rune indices per vector
MODES = ("random29", "grb5_mod", "grb5_rej", "shuffle29")

# ------------------------------------------------------------------ py2 driver
DRIVER = r'''
import sys, json, random, math

def modes(seedval, n, jump=None):
    out = {}
    for name in ("random29", "grb5_mod", "grb5_rej", "shuffle29"):
        r = random.Random()
        r.seed(seedval)
        if jump is not None:
            r.jumpahead(jump)
        if name == "random29":
            v = [int(r.random() * 29) for _ in range(n)]
        elif name == "grb5_mod":
            v = [r.getrandbits(5) % 29 for _ in range(n)]
        elif name == "grb5_rej":
            v = []
            while len(v) < n:
                x = r.getrandbits(5)
                if x < 29:
                    v.append(x)
        else:
            v = []
            while len(v) < n:
                pool = list(range(29))
                r.shuffle(pool)
                v.extend(pool)
            v = v[:n]
        out[name] = v
    return out

def equiv(seedval, n):
    """V5: are randrange/randint/choice/int(random()*29) the same call?"""
    res = {}
    for name in ("randrange", "randint", "choice", "random29"):
        r = random.Random(); r.seed(seedval)
        if name == "randrange":
            v = [r.randrange(29) for _ in range(n)]
        elif name == "randint":
            v = [r.randint(0, 28) for _ in range(n)]
        elif name == "choice":
            pool = list(range(29))
            v = [r.choice(pool) for _ in range(n)]
        else:
            v = [int(r.random() * 29) for _ in range(n)]
        res[name] = v
    return res

def main():
    job = json.load(sys.stdin)
    n = job["n"]
    out = {"version": sys.version, "maxint": sys.maxint,
           "sizeof_long_bits": 64 if sys.maxint > 2**32 else 32,
           "hashes": {}, "streams": {}, "equiv": {}, "extras": {}}
    for h in job["seeds_hex"]:
        s = h.decode("hex")
        out["hashes"][h] = hash(s)
        out["streams"][h] = modes(s, n)
    for h in job.get("equiv_hex", []):
        out["equiv"][h] = equiv(h.decode("hex"), n)
    for label, spec in job.get("extras", {}).items():
        kind = spec["kind"]
        if kind == "int":
            val = spec["value"]
        elif kind == "float":
            val = spec["value"]
        elif kind == "str":
            val = spec["value"].decode("hex")
        else:
            continue
        e = {"hash": None}
        try:
            e["hash"] = hash(val)
        except TypeError:
            pass
        e["streams"] = modes(val, n, jump=spec.get("jump"))
        out["extras"][label] = e
    sys.stdout.write(json.dumps(out))

main()
'''


def run_py2(build: str, job: dict, timeout=1800):
    cfg = BUILDS[build]
    if not Path(cfg["bin"]).exists():
        return None, "interpreter not present at %s" % cfg["bin"]
    env = dict(os.environ)
    env["PYTHONHOME"] = str(cfg["home"])
    env["LD_LIBRARY_PATH"] = ":".join(str(p) for p in cfg["ld"])
    env.pop("PYTHONHASHSEED", None)          # default (randomisation OFF in 2.7)
    env.pop("PYTHONPATH", None)
    argv = [str(cfg["bin"]), "-c", DRIVER]
    if cfg.get("loader"):
        argv = [str(cfg["loader"]), "--library-path", env["LD_LIBRARY_PATH"]] + argv
    try:
        p = subprocess.run(argv, input=json.dumps(job).encode(),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=env, timeout=timeout)
    except Exception as exc:                                  # noqa: BLE001
        return None, "%s: %s" % (type(exc).__name__, exc)
    if p.returncode != 0:
        return None, p.stderr.decode("utf-8", "replace")[-500:]
    return json.loads(p.stdout.decode()), None


def digest(streams: dict) -> str:
    h = hashlib.sha256()
    for k in sorted(streams):
        h.update(k.encode())
        for m in MODES:
            h.update(m.encode())
            h.update(bytes(streams[k][m]))
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default=str(HERE / "validation.json"))
    a = ap.parse_args()

    t0 = time.time()
    entries = B04SEEDS.build()
    core = set(B04SEEDS.core(entries)) if hasattr(B04SEEDS, "core") else set()
    if a.quick:
        # stratified: up to 12 per family
        by_fam, sample = {}, []
        for fam, b in entries:
            by_fam.setdefault(fam, [])
            if len(by_fam[fam]) < 12:
                by_fam[fam].append(b)
                sample.append((fam, b))
        entries = sample
    seed_bytes = [b for _, b in entries]
    fams = sorted({f for f, _ in entries})
    seeds_hex = [b.hex() for b in seed_bytes]

    equiv_hex = seeds_hex[:24]
    extras = {
        "int_3301":        {"kind": "int",   "value": 3301},
        "int_0":           {"kind": "int",   "value": 0},
        "int_neg3301":     {"kind": "int",   "value": -3301},
        "int_1387498126":  {"kind": "int",   "value": 1387498126},
        "int_2p40p7":      {"kind": "int",   "value": 2 ** 40 + 7},
        "float_3301":      {"kind": "float", "value": 3301.0},
        "float_3p301":     {"kind": "float", "value": 3.301},
        "float_0p5":       {"kind": "float", "value": 0.5},
        "float_neg3p301":  {"kind": "float", "value": -3.301},
        "float_3301p5":    {"kind": "float", "value": 3301.5},
        "jump_3301":       {"kind": "str", "value": b"CICADA3301".hex(), "jump": 3301},
        "jump_29":         {"kind": "str", "value": b"CICADA3301".hex(), "jump": 29},
        "jump_1":          {"kind": "str", "value": b"DIVINITY".hex(), "jump": 1},
        "jump_845145127":  {"kind": "str", "value": b"THE PRIMES ARE SACRED".hex(),
                            "jump": 845145127},
    }
    job = {"n": NVALS, "seeds_hex": seeds_hex,
           "equiv_hex": equiv_hex, "extras": extras}

    report = {
        "lane": "round19/G3",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "seed_dictionary": {
            "source": "liber-primus/analysis/round13/B04/seeds.py (REUSED, not rebuilt)",
            "n_entries_tested": len(seed_bytes),
            "n_entries_total": 2165,
            "families": fams,
            "values_per_vector": NVALS,
            "reductions": list(MODES),
        },
        "interpreters": {},
        "gates": {},
        "vectors": {},
        "notes": [],
    }

    # ---------------------------------------------------------------- V1 / run
    ref = {}
    for build in ("2.7.3", "2.7.18"):
        print("[*] running real CPython %s over %d seeds ..." % (build, len(seed_bytes)))
        out, err = run_py2(build, job)
        report["interpreters"][build] = {
            "note": BUILDS[build]["note"],
            "path": str(BUILDS[build]["bin"]),
            "ran": out is not None,
            "error": err,
            "version": out["version"] if out else None,
            "sizeof_long_bits": out["sizeof_long_bits"] if out else None,
        }
        if out:
            ref[build] = out
        print("    ->", "OK" if out else "FAIL: %s" % err)

    report["gates"]["V1_real_python27_executes"] = {
        "pass": bool(ref),
        "detail": "builds that ran: %s" % ", ".join(sorted(ref)) or "none",
    }
    if "2.7.3" not in ref:
        report["gates"]["V2_gen_matches_real_273"] = {
            "pass": False, "detail": "no real 2.7.3 available"}
        Path(a.out).write_text(json.dumps(report, indent=1))
        print("FATAL: no real 2.7.3"); return 1

    R3 = ref["2.7.3"]

    # ------------------------------------------------- V2 gen_py27 vs real 2.7.3
    print("[*] V2: gen_py27 vs real 2.7.3 ...")
    hash_ok = hash_bad = 0
    hash_fail_examples = []
    for h, want in R3["hashes"].items():
        got = G.py2_str_hash(bytes.fromhex(h), 64)
        if got == want:
            hash_ok += 1
        else:
            hash_bad += 1
            if len(hash_fail_examples) < 5:
                hash_fail_examples.append({"seed_hex": h, "want": want, "got": got})

    stream_ok = stream_bad = 0
    stream_fail_examples = []
    for h, want in R3["streams"].items():
        sb = bytes.fromhex(h)
        for m in MODES:
            got = G.keystream(sb, m, NVALS, wordsize=64)
            if got == want[m]:
                stream_ok += 1
            else:
                stream_bad += 1
                if len(stream_fail_examples) < 5:
                    stream_fail_examples.append(
                        {"seed_hex": h, "mode": m,
                         "want": want[m][:12], "got": got[:12]})

    report["gates"]["V2_gen_matches_real_273"] = {
        "pass": hash_bad == 0 and stream_bad == 0,
        "hash_vectors_ok": hash_ok, "hash_vectors_failed": hash_bad,
        "stream_vectors_ok": stream_ok, "stream_vectors_failed": stream_bad,
        "failures": hash_fail_examples + stream_fail_examples,
        "detail": ("%d seeds x %d reductions x %d values, plus %d hash() values"
                   % (len(seed_bytes), len(MODES), NVALS, len(seed_bytes))),
    }
    print("    hashes %d/%d, streams %d/%d"
          % (hash_ok, hash_ok + hash_bad, stream_ok, stream_ok + stream_bad))

    # ------------------------------------------------------- V3 2.7.3 vs 2.7.18
    if "2.7.18" in ref:
        d3, d18 = digest(R3["streams"]), digest(ref["2.7.18"]["streams"])
        same_hash = R3["hashes"] == ref["2.7.18"]["hashes"]
        report["gates"]["V3_cross_build_agreement"] = {
            "pass": d3 == d18 and same_hash,
            "sha256_2.7.3": d3, "sha256_2.7.18": d18,
            "hashes_identical": same_hash,
            "detail": "two independent real builds, 12 years and 2 compilers apart",
        }
        print("    V3 cross-build:", "PASS" if d3 == d18 else "FAIL")
    else:
        report["gates"]["V3_cross_build_agreement"] = {
            "pass": False, "detail": "2.7.18 unavailable"}

    # ------------------------------------------ V4 int / float / jumpahead
    print("[*] V4: int / float / jumpahead ...")
    v4 = {"pass": True, "items": {}}
    for label, spec in extras.items():
        want = R3["extras"][label]
        if spec["kind"] == "int":
            sv = spec["value"]
        elif spec["kind"] == "float":
            sv = spec["value"]
        else:
            sv = bytes.fromhex(spec["value"])
        item = {"kind": spec["kind"], "jump": spec.get("jump")}
        if spec["kind"] == "float":
            gh = G.py2_float_hash(sv, 64)
            item["hash_ok"] = (gh == want["hash"])
            item["hash_real"] = want["hash"]
            item["hash_gen"] = gh
        ok = True
        for m in MODES:
            got = G.keystream(sv, m, NVALS, wordsize=64, jump=spec.get("jump"))
            ok &= (got == want["streams"][m])
            if got != want["streams"][m]:
                item.setdefault("mismatch", {})[m] = {
                    "want": want["streams"][m][:12], "got": got[:12]}
        item["streams_ok"] = ok
        if spec["kind"] == "float":
            ok &= item["hash_ok"]
        v4["items"][label] = item
        v4["pass"] &= ok
    # jumpahead variant: which branch does 2.7.3 implement?
    jl = "jump_3301"
    w = R3["extras"][jl]["streams"]["random29"]
    a_ = G.keystream(b"CICADA3301", "random29", NVALS, wordsize=64,
                     jump=3301, issue14591=True)
    b_ = G.keystream(b"CICADA3301", "random29", NVALS, wordsize=64,
                     jump=3301, issue14591=False)
    v4["jumpahead_variant_2.7.3"] = (
        "issue14591_applied" if w == a_ else
        "pre_issue14591" if w == b_ else "NEITHER")
    v4["jumpahead_variants_differ"] = (a_ != b_)
    report["gates"]["V4_int_float_jumpahead"] = v4
    print("    V4:", "PASS" if v4["pass"] else "FAIL",
          "| jumpahead branch:", v4["jumpahead_variant_2.7.3"])

    # --------------------------------------------------- V5 reduction identity
    print("[*] V5: randrange/randint/choice/int(random()*29) identity ...")
    ident = {"all_identical": True, "n_seeds": len(R3["equiv"]), "per_pair": {}}
    for h, d in R3["equiv"].items():
        base = d["random29"]
        for name in ("randrange", "randint", "choice"):
            same = (d[name] == base)
            ident["per_pair"].setdefault(name + " == int(random()*29)", True)
            ident["per_pair"][name + " == int(random()*29)"] &= same
            ident["all_identical"] &= same
    report["gates"]["V5_reduction_identity_py27"] = {
        "pass": True,           # this gate MEASURES, it cannot fail
        "measured": ident,
        "detail": ("Python 2.7 Lib/random.py: randrange uses _int(self.random()*istart) "
                   "for width < 2**53; randint delegates to randrange; choice is "
                   "seq[int(random()*len(seq))]. Measured on real 2.7.3, not assumed."),
    }
    print("    all identical:", ident["all_identical"])

    # -------------------------------------------------------------- V6 Py2!=Py3
    print("[*] V6: Py2 vs Py3 streams for the same literal ...")
    diff = same = 0
    same_examples = []
    for h in list(R3["streams"])[:600]:
        sb = bytes.fromhex(h)
        p2 = R3["streams"][h]["random29"]
        try:
            p3b = G.py3_keystream(sb, "random29", NVALS)
            p3s = G.py3_keystream(sb.decode("latin-1"), "random29", NVALS)
        except Exception:                                     # noqa: BLE001
            continue
        if p2 == p3b or p2 == p3s:
            same += 1
            if len(same_examples) < 5:
                same_examples.append(h)
        else:
            diff += 1
    report["gates"]["V6_py2_differs_from_py3"] = {
        "pass": same == 0,
        "n_compared": same + diff, "n_different": diff, "n_identical": same,
        "identical_examples": same_examples,
        "detail": ("Python 3 str/bytes seeding is "
                   "int.from_bytes(b + sha512(b).digest(),'big') -> >=18 init_by_array "
                   "words; Python 2.7 is (unsigned long)hash(s) -> <=2 words. "
                   "This is the Q5 kill check: identical streams would make the lane "
                   "a duplicate of analysis/seed_sweep/string_seeds.py."),
    }
    print("    different %d / identical %d" % (diff, same))

    # ------------------------------------------------------------ V7 i386 (32)
    print("[*] V7: 32-bit (i386) branch ...")
    out32, err32 = run_py2("2.7.3-i386", {"n": NVALS,
                                           "seeds_hex": seeds_hex[:400],
                                           "equiv_hex": [], "extras": {}})
    if out32:
        h_ok = h_bad = 0
        s_ok = s_bad = 0
        for h, want in out32["hashes"].items():
            got = G.py2_str_hash(bytes.fromhex(h), 32)
            h_ok, h_bad = (h_ok + 1, h_bad) if got == want else (h_ok, h_bad + 1)
        for h, want in out32["streams"].items():
            for m in MODES:
                got = G.keystream(bytes.fromhex(h), m, NVALS, wordsize=32)
                s_ok, s_bad = (s_ok + 1, s_bad) if got == want[m] else (s_ok, s_bad + 1)
        report["gates"]["V7_i386_32bit_branch"] = {
            "pass": h_bad == 0 and s_bad == 0,
            "status": "VALIDATED",
            "interpreter": out32["version"],
            "sizeof_long_bits": out32["sizeof_long_bits"],
            "hash_ok": h_ok, "hash_failed": h_bad,
            "stream_ok": s_ok, "stream_failed": s_bad,
        }
        report["interpreters"]["2.7.3-i386"] = {
            "note": BUILDS["2.7.3-i386"]["note"],
            "ran": True, "version": out32["version"],
            "sizeof_long_bits": out32["sizeof_long_bits"],
        }
        print("    V7 VALIDATED: hashes %d/%d streams %d/%d"
              % (h_ok, h_ok + h_bad, s_ok, s_ok + s_bad))
    else:
        report["gates"]["V7_i386_32bit_branch"] = {
            "pass": False,
            "status": "PROVISIONAL",
            "reason": err32,
            "detail": ("The 32-bit branch is a one-line parameter change "
                       "(wordsize=32) to the same validated string_hash and the same "
                       "validated MT19937; it is NOT independently confirmed against a "
                       "running i386 interpreter. Rows produced with wordsize=32 must "
                       "be labelled PROVISIONAL in the SWEEPROW."),
        }
        print("    V7 PROVISIONAL:", (err32 or "")[:160])

    # ---------------------------------------------- V8 plant-and-recover (no scorer)
    print("[*] V8: scorer-free plant-and-recover ...")
    planted_seed = b"THE PRIMES ARE SACRED"        # family `slogan`, in the dictionary
    planted = {"seed": planted_seed.decode(), "mode": "grb5_rej",
               "wordsize": 64, "n": 96}
    target = G.keystream(planted_seed, "grb5_rej", 96, wordsize=64)
    matches = []
    all_entries = B04SEEDS.build()
    t1 = time.time()
    for fam, sb in all_entries:
        for m in MODES:
            for ws in (64, 32):
                if G.keystream(sb, m, 96, wordsize=ws) == target:
                    matches.append({"family": fam, "seed": sb.decode("latin-1"),
                                    "mode": m, "wordsize": ws})
    report["gates"]["V8_plant_and_recover_scorer_free"] = {
        "pass": len(matches) == 1 and matches[0]["seed"] == planted_seed.decode(),
        "planted": planted,
        "cross_product": len(all_entries) * len(MODES) * 2,
        "n_exact_matches": len(matches),
        "matches": matches[:5],
        "seconds": round(time.time() - t1, 1),
        "detail": ("Identity recovery over the full 2,165 x 4 x 2 cross product. "
                   "Uses NO decoder and NO adjudicator, so it is independent of "
                   "Round 19 Phase 0."),
    }
    print("    V8: %d exact match(es) over %d configs in %.1fs"
          % (len(matches), len(all_entries) * len(MODES) * 2, time.time() - t1))

    # -------------------------------------------------------- pinned vectors
    pinned = {}
    for lbl in (b"CICADA3301", b"3301", b"DIVINITY", b"THE PRIMES ARE SACRED",
                b"cicada3301", b"an end", b"ky2khlqdf7qdznac"):
        h = lbl.hex()
        if h in R3["streams"]:
            pinned[lbl.decode()] = {
                "py2_hash_64": R3["hashes"][h],
                "py2_hash_32_gen": G.py2_str_hash(lbl, 32),
                "seed_key_words_64": G._chunks32(
                    G.py2_str_hash(lbl, 64) & ((1 << 64) - 1)),
                "py27_random29_first16": R3["streams"][h]["random29"][:16],
                "py27_grb5_rej_first16": R3["streams"][h]["grb5_rej"][:16],
                "py3_random29_first16": G.py3_keystream(lbl.decode(), "random29", 16),
            }
    report["vectors"]["pinned"] = pinned
    report["vectors"]["explanation"] = (
        "py2_hash_64 is the value real CPython 2.7.3 returned for hash(<str>). "
        "seed_key_words_64 is the init_by_array key array Python 2.7 builds from it. "
        "py3_random29_first16 is the Python-3 stream for the same literal, i.e. what "
        "analysis/seed_sweep/string_seeds.py actually swept."
    )

    gates = report["gates"]
    report["verdict"] = {
        "all_blocking_gates_pass": all(
            gates[g]["pass"] for g in
            ("V1_real_python27_executes", "V2_gen_matches_real_273",
             "V3_cross_build_agreement", "V4_int_float_jumpahead",
             "V6_py2_differs_from_py3", "V8_plant_and_recover_scorer_free")),
        "confidence_64bit": ("VALIDATED against two real CPython 2.7 builds"
                             if gates["V2_gen_matches_real_273"]["pass"]
                             and gates["V3_cross_build_agreement"]["pass"]
                             else "NOT VALIDATED"),
        "confidence_32bit": gates["V7_i386_32bit_branch"].get("status"),
        "elapsed_seconds": round(time.time() - t0, 1),
    }
    Path(a.out).write_text(json.dumps(report, indent=1))
    print("\n[*] wrote", a.out)
    print("[*] verdict:", json.dumps(report["verdict"], indent=1))
    return 0 if report["verdict"]["all_blocking_gates_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
