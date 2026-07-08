"""Campaign XII, Part 2b -- run the expanded running-key sweep, document every null.

Drives each verified candidate keytext (data/keys/campaign12/*.txt) through the
project's validated running-key attack (attack.py runningkey: all offsets, both
signs, +-Atbash, per unsolved page; THRESHOLD -5.2, English ~ -4.0..-4.4). Captures
the best score seen per keytext into a reproducible table.

A break would print a hit over threshold; the expected (and observed) outcome is a
full null table -- its value is that no future solver re-runs these texts.

Reproduce:  PYTHONUTF8=1 python3 run_sweep.py
"""
import os, sys, re, json, subprocess, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
KEYDIR = os.path.join(ROOT, "data", "keys", "campaign12")
ATTACK = os.path.join(ROOT, "attack.py")

texts = sorted(glob.glob(os.path.join(KEYDIR, "*.txt")))
print(f"running-key sweep over {len(texts)} verified candidate keytexts\n")
rows = []
for t in texts:
    slug = os.path.splitext(os.path.basename(t))[0]
    env = dict(os.environ, PYTHONUTF8="1")
    try:
        out = subprocess.run([sys.executable, ATTACK, "runningkey", "--key", t,
                              "--label", slug], cwd=ROOT, env=env,
                             capture_output=True, text=True, timeout=300).stdout
    except subprocess.TimeoutExpired:
        rows.append((slug, None, "TIMEOUT")); print(f"  {slug:20s} TIMEOUT"); continue
    nh = re.search(r"(\d+) hits over threshold", out)
    bs = re.search(r"best score seen:\s*(-?\d+\.\d+)", out)
    best = float(bs.group(1)) if bs else None
    nhit = int(nh.group(1)) if nh else None
    verdict = "BREAK?" if (nhit and nhit > 0) else "null"
    rows.append((slug, best, verdict))
    flag = "  <-- OVER THRESHOLD, INSPECT" if verdict == "BREAK?" else ""
    print(f"  {slug:20s} best {best}  {verdict}{flag}")

rows.sort(key=lambda r: (r[1] is None, -(r[1] or -99)))
json.dump(rows, open(os.path.join(HERE, "sweep_results.json"), "w"), indent=2)
print("\n=== SWEEP SUMMARY (best score per keytext; higher = closer to English) ===")
print("English break ~ -5.0 or above; noise floor ~ -7.4; nothing here should clear -5.2.")
for slug, best, verdict in rows:
    print(f"  {best if best is not None else 'n/a':>8}  {slug:22s} {verdict}")
breaks = [r for r in rows if r[2] == "BREAK?"]
print(f"\n{len(breaks)} texts produced an over-threshold hit "
      f"{'-> INSPECT: '+str([r[0] for r in breaks]) if breaks else '(clean null across the corpus)'}")
