"""Arm B2 positive control: splice a known word-start-skipping run over a page start; recover its seed."""
import subprocess, os, random, json, tempfile
from common import stream, HERE
B = os.path.join(HERE, "repro2"); S = os.path.join(HERE, "stream.txt"); LAY = os.path.join(HERE, "layout.txt")
starts = [int(x) for x in open(LAY).readline().split()]
rng = random.Random(4803); out = []
for g in ["drand48", "bash42", "bash42_32", "glibc", "py27"]:
    for trial in range(3):
        seed = rng.randrange(600000, 2**32 - 600000); m = rng.choice(range(29, 41)); red = rng.randrange(2); atb = rng.randrange(2)
        e = rng.choice([1, 2]); pos = rng.choice(starts)
        E = [int(x) for x in subprocess.check_output([B, S, LAY, g, "emit", str(seed), str(m), str(red), str(e), str(pos), "14"]).split()]
        if len(E) < 14: print(g, "short plant, skipped"); continue
        t = stream(); t[pos:pos + len(E)] = [28 - x for x in E] if atb else E
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("\n".join(map(str, t)) + "\n"); p = f.name
        lo = seed - rng.randrange(1, 500000)
        r = subprocess.check_output([B, p, LAY, g, str(lo), str(lo + 1000000)]).decode(); os.unlink(p)
        want = f"seed={seed} m={m} red={red} e={e} atbash={atb} pos={pos} "
        hit = any(l.startswith("HIT") and want in l for l in r.splitlines())
        extra = sum(l.startswith("HIT") for l in r.splitlines()) - hit
        out.append({"gen": g, "seed": seed, "m": m, "red": red, "e": e, "atbash": atb, "pos": pos, "recovered": hit, "other_hits": extra})
        print(g, m, red, e, atb, pos, "RECOVERED" if hit else "MISSED", "other_hits", extra)
json.dump(out, open(os.path.join(HERE, "plants2.json"), "w"), indent=1)
print("recovered", sum(o["recovered"] for o in out), "/", len(out))
