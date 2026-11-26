"""Arm B positive control: splice a known generator run into LP2 and recover its seed with the sweep binary."""
import subprocess, os, random, json, sys, tempfile
from common import stream, HERE
B = os.path.join(HERE, "repro"); S = os.path.join(HERE, "stream.txt")
rng = random.Random(4801)
GENS = ["glibc", "drand48", "py27", "bash42", "bash42_32", "msvc", "ansi", "minstd"]
out = []
for g in GENS:
    for trial in range(3):
        seed = rng.randrange(600000, 2**32 - 600000); m = rng.choice(range(29, 41)); red = rng.randrange(2); atb = rng.randrange(2)
        E = [int(x) for x in subprocess.check_output([B, S, g, "emit", str(seed), str(m), str(red), "40"]).split()]
        if len(E) < 14: continue
        t = stream(); pos = rng.randrange(0, len(t) - len(E))
        t[pos:pos + len(E)] = [28 - x for x in E] if atb else E
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("\n".join(map(str, t)) + "\n"); p = f.name
        lo = seed - rng.randrange(1, 500000)
        r = subprocess.check_output([B, p, g, str(lo), str(lo + 1000000)]).decode()
        os.unlink(p)
        want = f"seed={seed} m={m} red={red} atbash={atb} pos={pos} "
        hit = any(l.startswith("HIT") and want in l for l in r.splitlines())
        extra = sum(l.startswith("HIT") for l in r.splitlines()) - hit
        out.append({"gen": g, "seed": seed, "m": m, "red": red, "atbash": atb, "pos": pos, "plant_len": len(E), "recovered": hit, "other_hits": extra})
        print(g, m, red, atb, len(E), "RECOVERED" if hit else "MISSED", "other_hits", extra)
json.dump(out, open(os.path.join(HERE, "plants.json"), "w"), indent=1)
print("recovered", sum(o["recovered"] for o in out), "/", len(out))
