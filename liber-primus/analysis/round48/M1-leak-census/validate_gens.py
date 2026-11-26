"""Cross-check repro.c's generators against live libraries / the repo's byte-exact references."""
import subprocess, sys, os, random, json, ctypes
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "round19", "G1"))
import gen_bash
def dump(gen, seed, n=30):
    return [int(x) for x in subprocess.check_output([os.path.join(HERE, "repro"), os.path.join(HERE, "stream.txt"), gen, "dump", str(seed), str(n)]).split()]
SEEDS = [0, 1, 42, 3301, 1357000000, 1388534400, 2**31 - 1, 2**31, 2**32 - 1]
libc = ctypes.CDLL("libc.so.6")
def ref_glibc(s, n):
    libc.srand(ctypes.c_uint(s)); return [libc.rand() for _ in range(n)]
def ref_perl(s, n):
    out = subprocess.check_output(["perl", "-e", f"srand({s}); print join(' ', map {{ int(rand(281474976710656)) }} 1..{n})"])
    return [int(x) for x in out.split()]
def ref_py(s, n):
    r = random.Random(s); return [int(r.random() * 2**53) for _ in range(n)]
def ref_bash(fn):
    def f(s, n):
        out, last = [], 0
        while len(out) < n:
            rv, s = fn(s)
            if rv == last: continue
            last = rv; out.append(rv)
        return out
    return f
def ref_msvc(s, n):
    o = []
    for _ in range(n): s = (s * 214013 + 2531011) & 0xffffffff; o.append((s >> 16) & 0x7fff)
    return o
def ref_ansi(s, n):
    o = []
    for _ in range(n): s = (s * 1103515245 + 12345) & 0xffffffff; o.append((s >> 16) & 0x7fff)
    return o
def ref_minstd(s, n):
    s %= 2147483647; s = s or 1; o = []
    for _ in range(n): s = s * 16807 % 2147483647; o.append(s)
    return o
REFS = {"glibc": (ref_glibc, "live libc srand/rand via ctypes"), "drand48": (ref_perl, "live perl srand/rand"),
        "py27": (ref_py, "CPython random.Random(int).random() (identical to 2.7 for int seeds)"),
        "bash42": (ref_bash(gen_bash.brand_42_lp64), "round19/G1/gen_bash.brand_42_lp64 + get_random_number loop"),
        "bash42_32": (ref_bash(gen_bash.brand_42_ilp32), "round19/G1/gen_bash.brand_42_ilp32 + loop"),
        "msvc": (ref_msvc, "independent formula"), "ansi": (ref_ansi, "independent formula"), "minstd": (ref_minstd, "independent formula")}
res = {}
for g, (fn, what) in REFS.items():
    ok = all(dump(g, s) == fn(s, 30) for s in SEEDS)
    res[g] = {"reference": what, "seeds": len(SEEDS), "raws_each": 30, "match": ok}
    print(g, "MATCH" if ok else "MISMATCH", "-", what)
json.dump(res, open(os.path.join(HERE, "validate_gens.json"), "w"), indent=1)
sys.exit(0 if all(v["match"] for v in res.values()) else 1)
