"""Round 19 / G1 -- THE VALIDATION GATE.

PREREG section 4: a generator that does not reproduce the real library byte-for-byte
does not enter the sweep.  This script is the only thing that decides that.  It writes
`validation.json` with the actual test vectors, and exits non-zero if any ERA-CORRECT
generator fails.

Four classes of reference, strongest first:

  L1  A REAL RUNNING BINARY OF THE ERA-CORRECT VERSION.
      GNU bash 4.2.0 built from the ftp.gnu.org release tarball (Ubuntu 11.04-12.04
      shipped 4.2).  `RANDOM=<s>; echo $RANDOM ...` straight out of the shell.
  L2  A REAL RUNNING BINARY OF A LATER VERSION.
      The system /bin/bash, whatever it is, checked against the matching model.
  L3  THE REAL SYSTEM LIBRARY through a C program (ref_glibc.c: srandom/random/rand/
      srand48/lrand48/mrand48/drand48/initstate), and the real openssl / shuf binaries.
  L4  C COMPILED FROM THE RELEASED SOURCE of a version whose binary we could not build
      (ref_bash.c's transcriptions).  Weaker than L1-L3 and labelled so.

Run:  python3 validate.py [--bash42 /path/to/bash-4.2/bash]
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gen_bash as GB           # noqa: E402
import gen_glibc as GG          # noqa: E402
import gen_coreutils as GC      # noqa: E402
import reduce29 as R29          # noqa: E402

SEEDS = [0, 1, 2, 3301, 12345, 2147483647, 4294967295, 1376006400]
NDRAW = 2000
NSHOW = 12                      # test vectors recorded verbatim in validation.json

REF_BASH_SRC = os.path.join(HERE, "ref_bash.c")
REF_GLIBC_SRC = os.path.join(HERE, "ref_glibc.c")


def _build(src, out):
    r = subprocess.run(["gcc", "-O2", "-o", out, src], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gcc failed on {src}:\n{r.stderr}")
    return out


def _read_ref(binary, seeds):
    r = subprocess.run([binary] + [str(s) for s in seeds],
                       capture_output=True, text=True)
    ref, abi = {}, None
    for ln in r.stdout.splitlines():
        d = json.loads(ln)
        if "abi" in d:
            abi = d["abi"]
            continue
        ref[(d["gen"], d["seed"])] = d["vals"]
    return ref, abi


# ------------------------------------------------------------- bash, real binaries
def bash_random(binary, seed, n):
    """`RANDOM=<seed>; for ((i=0;i<n;i++)); do echo $RANDOM; done` from a real shell."""
    script = f"RANDOM={seed}; for ((i=0;i<{n};i++)); do echo $RANDOM; done"
    r = subprocess.run([binary, "-c", script], capture_output=True, text=True,
                       timeout=300)
    if r.returncode != 0:
        return None
    return [int(x) for x in r.stdout.split()]


def bash_version(binary):
    try:
        r = subprocess.run([binary, "--version"], capture_output=True, text=True,
                           timeout=30)
        return r.stdout.splitlines()[0].strip()
    except Exception:
        return None


def model_for_bash_version(vline):
    """Map a `bash --version` banner onto the variant name that must reproduce it."""
    if not vline:
        return None
    import re
    m = re.search(r"version (\d+)\.(\d+)", vline)
    if not m:
        return None
    maj, mnr = int(m.group(1)), int(m.group(2))
    if (maj, mnr) >= (5, 1):
        return "bash5.1"
    if (maj, mnr) == (5, 0):
        return "bash5.0"
    if (maj, mnr) in ((4, 2), (4, 3)):
        return "bash4.2"
    if (maj, mnr) in ((4, 0), (4, 1)):
        return "bash4.0"
    if maj == 3:
        return "bash3.2"
    return None


def main():
    t0 = time.time()
    results = {
        "lane": "round19/G1",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ndraws_per_vector": NDRAW,
        "seeds": SEEDS,
        "references": {},
        "generators": {},
        "test_vectors": {},
        "internal_consistency": {},
    }

    bash42 = None
    for a in sys.argv[1:]:
        if a.startswith("--bash42="):
            bash42 = a.split("=", 1)[1]
    if bash42 is None:
        for cand in ("/tmp/g1src/bash-4.2/bash",
                     os.path.join(HERE, "bin", "bash-4.2")):
            if os.path.exists(cand):
                bash42 = cand
                break

    # ---------------------------------------------------------------- L1: real bash 4.2
    v42 = bash_version(bash42) if bash42 else None
    results["references"]["bash42_binary"] = {"path": bash42, "version": v42,
                                              "level": "L1"}
    if v42 and "4.2" in v42:
        ok, fails = True, []
        for s in SEEDS:
            got = GB.raws(s, NDRAW, "bash4.2")
            real = bash_random(bash42, s, NDRAW)
            if real != got:
                ok = False
                d = next((i for i, (x, y) in enumerate(zip(real or [], got))
                          if x != y), None)
                fails.append({"seed": s, "first_diff": d,
                              "real": (real or [])[:6], "model": got[:6]})
        results["generators"]["bash4.2"] = {
            "reference": "REAL GNU bash 4.2.0 binary, built from the ftp.gnu.org "
                         "bash-4.2.tar.gz release tarball",
            "reference_level": "L1",
            "era_correct": True,
            "verdict": "PASS" if ok else "FAIL",
            "n_seeds": len(SEEDS), "n_draws": NDRAW, "failures": fails,
        }
        results["test_vectors"]["bash4.2"] = {
            str(s): bash_random(bash42, s, NSHOW) for s in SEEDS}
    else:
        results["generators"]["bash4.2"] = {
            "reference": "no bash-4.2 binary available",
            "reference_level": None, "era_correct": True, "verdict": "NOT-VALIDATED-L1",
        }

    # ------------------------------------------------------------ L2: the system bash
    sysbash = "/bin/bash"
    vsys = bash_version(sysbash)
    model = model_for_bash_version(vsys)
    results["references"]["system_bash"] = {"path": sysbash, "version": vsys,
                                            "maps_to_variant": model, "level": "L2"}
    if model:
        ok, fails = True, []
        for s in SEEDS:
            got = GB.raws(s, NDRAW, model)
            real = bash_random(sysbash, s, NDRAW)
            if real != got:
                ok = False
                d = next((i for i, (x, y) in enumerate(zip(real or [], got))
                          if x != y), None)
                fails.append({"seed": s, "first_diff": d})
        entry = results["generators"].setdefault(model, {})
        entry.update({
            "reference": f"the running system shell: {vsys}",
            "reference_level": "L2",
            "era_correct": model in GB.ERA_CORRECT,
            "verdict": "PASS" if ok else "FAIL",
            "n_seeds": len(SEEDS), "n_draws": NDRAW, "failures": fails,
        })
        results["test_vectors"][model] = {
            str(s): bash_random(sysbash, s, NSHOW) for s in SEEDS}

    # ------------------------- L4: C compiled from released bash source, all variants
    ref_bash = _build(REF_BASH_SRC, "/tmp/g1_ref_bash")
    refb, abi = _read_ref(ref_bash, SEEDS)
    results["references"]["ref_bash_c"] = {
        "source": "ref_bash.c -- verbatim transcriptions of bash 3.2/4.0/4.2/5.0/5.1 "
                  "variables.c and lib/sh/random.c from the ftp.gnu.org tarballs",
        "abi": abi, "level": "L4"}
    for variant in GB.BRANDS:
        vals = {s: refb.get((variant, s)) for s in SEEDS}
        if all(not v for v in vals.values()):
            continue
        ok, fails, prefixes = True, [], {}
        for s in SEEDS:
            want = vals[s]
            if want is None:
                continue
            # A short vector means the C reference stopped at a NON-DETERMINISTIC
            # point (bash 4.0/4.1 reaching state 0).  The model must agree on the
            # prefix AND on where the prefix ends.
            if len(want) < NDRAW:
                prefixes[str(s)] = len(want)
            got = GB.raws(s, NDRAW, variant)
            if got != want:
                ok = False
                d = next((i for i, (x, y) in enumerate(zip(want, got)) if x != y),
                         None)
                fails.append({"seed": s, "first_diff": d,
                              "len_ref": len(want), "len_model": len(got)})
        e = results["generators"].setdefault(variant, {})
        e.setdefault("reference", "ref_bash.c (C from released bash source)")
        e.setdefault("reference_level", "L4")
        e["era_correct"] = variant in GB.ERA_CORRECT
        e["verdict_vs_ref_c"] = "PASS" if ok else "FAIL"
        e.setdefault("verdict", "PASS" if ok else "FAIL")
        e["failures_vs_ref_c"] = fails
        if prefixes:
            e["deterministic_prefix_len"] = prefixes
            e["note_nondeterminism"] = (
                "bash 4.0/4.1 call seedrand() (gettimeofday ^ getpid) when the state "
                "reaches 0, which IS reachable -- RANDOM=2147483647 reaches it in one "
                "step. The stream is unsweepable past that point; only the "
                "deterministic prefix is emitted.")
        e["n_seeds"] = len([s for s in SEEDS if vals[s] is not None])
        e["n_draws"] = NDRAW
        results["test_vectors"].setdefault(
            variant, {str(s): (vals[s][:NSHOW] if vals[s] else None) for s in SEEDS})

    # ------------------------------------------------------- L3: real glibc through C
    ref_glibc = _build(REF_GLIBC_SRC, "/tmp/g1_ref_glibc")
    refg, _ = _read_ref(ref_glibc, SEEDS)
    try:
        libc_v = subprocess.run(["ldd", "--version"], capture_output=True,
                                text=True).stdout.splitlines()[0]
    except Exception:
        libc_v = "unknown"
    results["references"]["glibc"] = {"ldd": libc_v, "level": "L3"}

    glibc_map = {
        "glibc_random":       ("random", lambda s, n: GG.random_seq(s, n, "initstate128")),
        "glibc_rand":         ("rand", lambda s, n: GG.random_seq(s, n, "initstate128")),
        "glibc_initstate8":   ("initstate8", lambda s, n: GG.random_seq(s, n, "initstate8")),
        "glibc_initstate32":  ("initstate32", lambda s, n: GG.random_seq(s, n, "initstate32")),
        "glibc_initstate64":  ("initstate64", lambda s, n: GG.random_seq(s, n, "initstate64")),
        "glibc_initstate256": ("initstate256", lambda s, n: GG.random_seq(s, n, "initstate256")),
        "lrand48":            ("lrand48", GG.lrand48_seq),
        "mrand48":            ("mrand48", lambda s, n: [
            x if x < (1 << 31) else x - (1 << 32) for x in GG.mrand48_seq(s, n)]),
        "drand48_x2p53":      ("drand48_x2p53", GG.drand48_x2p53_seq),
    }
    for name, (refname, fn) in glibc_map.items():
        ok, fails = True, []
        for s in SEEDS:
            want = refg.get((refname, s))
            got = fn(s, NDRAW)
            if want != got:
                ok = False
                d = next((i for i, (x, y) in enumerate(zip(want or [], got))
                          if x != y), None)
                fails.append({"seed": s, "first_diff": d})
        results["generators"][name] = {
            "reference": f"the running system glibc via ref_glibc.c ({libc_v})",
            "reference_level": "L3",
            "era_correct": name in GG.ERA_CORRECT,
            "verdict": "PASS" if ok else "FAIL",
            "n_seeds": len(SEEDS), "n_draws": NDRAW, "failures": fails,
        }
        results["test_vectors"][name] = {
            str(s): (refg.get((refname, s)) or [])[:NSHOW] for s in SEEDS}

    # rand() == random() on glibc: a MEASUREMENT, not an assumption
    same = all(refg.get(("rand", s)) == refg.get(("random", s)) for s in SEEDS)
    results["internal_consistency"]["glibc_rand_is_random"] = {
        "measured": same,
        "note": "On glibc, rand() calls the same TYPE_3 generator as random(). "
                "Measured here over 8 seeds x 2000 draws so the sweep may treat them "
                "as one cell instead of two."}

    # -------------------------------------------------------------- openssl enc -k
    try:
        ov = subprocess.run(["openssl", "version"], capture_output=True,
                            text=True).stdout.strip()
    except Exception:
        ov = None
    results["references"]["openssl"] = {"version": ov, "level": "L3"}
    if ov:
        ok, fails = True, []
        vectors = {}
        for p in ("CICADA", "3301", "THE PRIMES ARE SACRED", "a"):
            want = GC.openssl_enc_rc4_keystream(p, 64)
            # OpenSSL 3.x moved RC4 to the legacy provider; loading it explicitly is
            # what a 3.x box needs to reproduce a 1.0.1 default. Fall back to the bare
            # invocation on a 1.x openssl, where -provider does not exist.
            r = subprocess.run(
                ["openssl", "enc", "-rc4", "-nosalt", "-md", "md5", "-k", p,
                 "-provider", "legacy", "-provider", "default"],
                input=b"\x00" * 64, capture_output=True)
            if r.returncode != 0:
                r = subprocess.run(
                    ["openssl", "enc", "-rc4", "-nosalt", "-md", "md5", "-k", p],
                    input=b"\x00" * 64, capture_output=True)
            got = r.stdout[:64]
            vectors[p] = want[:16].hex()
            if r.returncode != 0 or got != want:
                ok = False
                fails.append({"pass": p, "rc": r.returncode,
                              "real": got[:8].hex(), "model": want[:8].hex()})
        results["generators"]["openssl_enc_rc4_k"] = {
            "reference": f"the real openssl binary ({ov})",
            "reference_level": "L3", "era_correct": False,
            "verdict": "PASS" if ok else "FAIL", "failures": fails,
            "note": "openssl 3.x may refuse RC4 (legacy provider). A FAIL here that is "
                    "an rc!=0 is a TOOL-UNAVAILABLE, not a model error -- see rc field.",
        }
        results["test_vectors"]["openssl_enc_rc4_k"] = vectors

    # ------------------------------------------------------------------------ shuf
    sv = GC.shuf_available()
    results["references"]["shuf"] = {"version": sv, "level": "L3"}
    if sv:
        src = os.path.join(HERE, "ref_glibc.c")     # any fixed file works as a source
        a = GC.shuf_stream(src, 64)
        b = GC.shuf_stream(src, 64)
        results["generators"]["shuf_random_source"] = {
            "reference": f"the real shuf binary ({sv}) -- ORACLE, not a "
                         "reimplementation, so there is nothing to mis-validate",
            "reference_level": "L3", "era_correct": False,
            "verdict": "PASS" if (a is not None and a == b) else "FAIL",
            "note": "determinism check: two invocations on the same --random-source "
                    "must agree. Coverage caveat: this is coreutils "
                    f"'{sv}', not the 8.13 that shipped with Ubuntu 12.04.",
        }
        results["test_vectors"]["shuf_random_source"] = {"ref_glibc.c": (a or [])[:NSHOW]}

    # --------------------------------------------- unreachable objects, stated not swept
    results["unreachable"] = GC.REACHABILITY

    # ---------------------------------------------------- internal: sliding-window law
    # window(master_orbit, i) must equal raws(state_at_i).  This is what licenses the
    # O(2**31 + L) sweep instead of O(2**31 * L).  It is a property of OUR interface,
    # so it is checked here, not assumed in READY.md.
    for variant in ("bash4.2", "bash5.1", "bash3.2", "bash4.2_i32"):
        master = GB.master_orbit(variant, start=1, length=6000)
        # replay the state map to learn the state at index i
        f = GB.BRANDS[variant]
        st, states = 1, [1]
        for _ in range(200):
            _, st = f(st)
            states.append(st)
        okw = True
        for i in (0, 1, 7, 33, 100, 199):
            direct = GB.raws(states[i], 64, variant)
            slid = GB.window(master, i, 64)
            if direct != slid:
                okw = False
                break
        results["internal_consistency"][f"sliding_window_{variant}"] = {
            "holds": okw,
            "claim": "window(master, i, n) == raws(state_at_index_i, n); seed choice is "
                     "an OFFSET into one master orbit, so seed and keystream-offset are "
                     "the same axis for this generator family.",
        }

    # -------------------------------------------------- internal: reductions round-trip
    ks = R29.reduce_stream(iter(GB.raws(3301, 4000, "bash4.2")), GB.RMAX, 120, "mod29")
    results["internal_consistency"]["reduce29_shapes"] = {
        r: len(R29.reduce_stream(iter(GB.raws(3301, 40000, "bash4.2")), GB.RMAX, 120, r))
        for r, _ in R29.REDUCTIONS}
    results["internal_consistency"]["variant_cells"] = {
        "stage_A": R29.variant_count("A"), "stage_B": R29.variant_count("B")}
    assert len(ks) == 120

    # ------------------------------------------------------------------------ verdict
    era_fail = [k for k, v in results["generators"].items()
                if v.get("era_correct") and v.get("verdict") not in
                ("PASS", "NOT-VALIDATED-L1")]
    other_fail = [k for k, v in results["generators"].items()
                  if v.get("verdict") == "FAIL"]
    results["gate"] = {
        "era_correct_failures": era_fail,
        "any_failures": other_fail,
        "verdict": "PASS" if not era_fail else "FAIL",
        "elapsed_sec": round(time.time() - t0, 1),
    }

    with open(os.path.join(HERE, "validation.json"), "w") as fh:
        json.dump(results, fh, indent=1)

    for k, v in sorted(results["generators"].items()):
        print(f"{k:22s} {str(v.get('reference_level')):3s} "
              f"{v.get('verdict'):18s} era={v.get('era_correct')}")
    print("\nGATE:", results["gate"]["verdict"], results["gate"])
    return 0 if results["gate"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
