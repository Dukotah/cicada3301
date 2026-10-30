#!/usr/bin/env python3
"""C1 U1: build candidates.json (clue-derived strings, deduped vs round13/B04 seeds + round26/C seeds). Writes candidates.json only."""
import os, sys, re, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round13", "B04")); import seeds as B04
norm = lambda s: re.sub(r"[^A-Z]", "", s.upper())
b04 = set()
for lab, b in B04.build():
    try: t = b.decode("utf-8")
    except Exception: continue
    n = norm(t)
    if n and len(n) >= 3: b04.add(n)
r26 = {norm(s["value"]) for s in json.load(open(os.path.join(LP, "analysis", "round26", "C", "seeds.json")))["seeds"] if s["is_str"]}
clues = {c["id"]: c for c in json.load(open(os.path.join(LP, "analysis", "round36", "O4-clue-coverage", "clues.json")))}
def ct(i): return clues[i]["text"]
C16 = {k: ct("C-2016-%d" % k) for k in range(1, 6)}
# (as-written string, source-id, group)
raw = []
def add(s, src, grp): raw.append((s, src, grp))
add("Liber Primus is the way.", "C-2016-2", "2016-clause")
add("Its words are the map,", "C-2016-3", "2016-clause")
add("their meaning is the road,", "C-2016-4", "2016-clause")
add("and their numbers are the direction.", "C-2016-5", "2016-clause")
add("their numbers are the direction", "C-2016-5", "2016-clause")
add("The path lies empty; epiphany seeks the devoted.", "C-2016-1", "2016-clause")
add("The path lies empty", "C-2016-1", "2016-clause")
add("epiphany seeks the devoted", "C-2016-1", "2016-clause")
add("Its words are the map, their meaning is the road, and their numbers are the direction.", "C-2016-3..5", "2016-composition")
add("Liber Primus is the way. Its words are the map, their meaning is the road, and their numbers are the direction.", "C-2016-2..5", "2016-composition")
add("Its words are the map, their meaning is the road, and their numbers are the direction. Liber Primus is the way.", "C-2016-2..5", "2016-composition")
add("words map meaning road numbers direction", "C-2016-3..5 keywords", "2016-composition")
for s, g in [("the way", 0), ("the map", 0), ("the road", 0), ("the direction", 0), ("map", 0), ("road", 0), ("direction", 0), ("way", 0),
             ("epiphany", 0), ("seek", 0), ("seeks", 0), ("the devoted", 0), ("devoted", 0), ("the path", 0), ("path", 0),
             ("its words", 0), ("their meaning", 0), ("their numbers", 0), ("meaning", 0), ("words", 0), ("numbers", 0), ("the words", 0),
             ("the numbers", 0), ("the meaning", 0), ("an empty path", 0), ("epiphany seeks", 0), ("seek epiphany", 0), ("the path lies empty epiphany", 0)]:
    add(s, "C-2016 noun phrase", "2016-noun-phrase")
LP1 = {k: ct(k) for k in clues if k.startswith("LP1-0.")}
imp = ["LP1-0.0.0.1", "LP1-0.0.0.2", "LP1-0.0.0.3", "LP1-0.0.0.4", "LP1-0.0.0.5", "LP1-0.0.0.6", "LP1-0.0.0.7", "LP1-0.0.0.8", "LP1-0.0.0.9",
       "LP1-0.1.0.6", "LP1-0.1.1.5", "LP1-0.1.2.3", "LP1-0.1.3.0", "LP1-0.2.1.1", "LP1-0.3.1.1", "LP1-0.3.1.2", "LP1-0.3.1.3",
       "LP1-0.3.2.1", "LP1-0.3.2.2", "LP1-0.4.1.1", "LP1-0.4.1.2", "LP1-0.4.1.3", "LP1-0.4.1.4", "LP1-0.13.0.2", "LP1-0.13.0.1",
       "LP1-0.14.0.3", "LP1-0.14.0.2", "LP1-0.1.0.1"]
for i in imp: add(LP1[i], i, "LP1-imperative")
for s, src in [("QUESTION ALL THINGS", "LP1-0.4.1.1 standard spelling"), ("COMMAND YOUR OWN SELF", "LP1-0.1.1.5 tail"),
               ("BE PREPARED", "LP1-0.3.1.3 head"), ("PROGRAM", "LP1-0.3.2.1/2 head"), ("FOLLOW YOUR TRUTH", "LP1-0.4.1.3"),
               ("DISCOVER TRUTH", "LP1-0.4.1.2 head"), ("SEEK OUT THIS PAGE", "LP1-0.13.0.2 tail"), ("AMASS", "LP1-0.3.1.1 head"),
               ("EMERGE", "LP1-0.14.0.3 tail"), ("TEST", "LP1-0.0.0.3 head"), ("EXPERIENCE", "LP1-0.0.0.5 head"), ("BELIEVE NOTHING", "LP1-0.0.0.1 head"),
               ("KWESTION", "LP1-0.4.1.1 head"), ("QUESTION", "std spelling"), ("IMPOSE NOTHING", "LP1-0.4.1.4 head"), ("NEVER BECOME ATTACHED", "LP1-0.3.1.2 head")]:
    add(s, src, "LP1-imperative-fragment")
seen, cands, covered = {}, [], []
for s, src, grp in raw:
    n = norm(s)
    if n in seen: continue
    seen[n] = 1
    cov = [k for k, S in (("round13/B04", b04), ("round26/C", r26)) if n in S]
    rec = {"as_written": s, "upper": re.sub(r"\s+", " ", re.sub(r"[^A-Za-z ]", "", s)).strip().upper(), "norm": n, "source": src, "group": grp}
    if cov: rec["covered_by"] = cov; covered.append(rec)
    else: cands.append(rec)
for i, r in enumerate(cands): r["id"] = "U1-%03d" % i
out = {"note": "dedupe key = letters-only uppercase; covered_by = normalized string present among round13/B04 build() text seeds (all 4 byte forms -> SHA/PBKDF2 routes, 534 secrets incl.) or round26/C str seeds. Covered strings are NOT re-run; direct-text-key route for them was only done as legacy-beam Vigenere keywords in round10b (B1).",
       "n_candidates": len(cands), "n_covered": len(covered), "candidates": cands, "already_covered": covered, "b04_norm_seed_count": len(b04), "r26c_str_seeds": len(r26)}
json.dump(out, open(os.path.join(HERE, "candidates.json"), "w"), indent=1)
print(len(cands), len(covered))
for r in covered: print("COV", r["covered_by"], r["upper"])
for r in cands: print(r["id"], r["group"], "|", r["upper"])
