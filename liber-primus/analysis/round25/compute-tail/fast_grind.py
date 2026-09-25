#!/usr/bin/env python3
"""FAST GRIND -- Single supervisor over the OpenMP C runner.
Delegates the heavy screening to `./runner`, which uses all 16 cores natively.
Any candidate seed with sc >= -5.8 is evaluated by the exact Python adjudicator
and stage_b from runner.py.
"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import runner as pyrunner

SPACE = pyrunner.SPACE
PROGRESS = os.path.join(HERE, "progress_fast.json")
HIT_FILE = os.path.join(HERE, "HIT.json")
CKPT_EVERY = 30.0

def default_resume_start():
    p1 = os.path.join(HERE, "progress.json")
    if os.path.exists(p1):
        try: return int(json.load(open(p1))["next_seed"])
        except Exception: pass
    return pyrunner.TAIL_START_DEFAULT

def load_progress():
    if os.path.exists(PROGRESS):
        try: return json.load(open(PROGRESS))
        except Exception: pass
    return {
        "cursor": default_resume_start(),
        "seeds_done": 0,
        "seeds_skipped_excluded": 0,
        "best_pmax": -1e9,
        "best_word": None,
        "flagged_survivors": []
    }

def save_progress(pr):
    tmp = PROGRESS + ".tmp"
    with open(tmp, "w") as f:
        json.dump(pr, f, indent=1)
    os.replace(tmp, PROGRESS)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=None)
    args = ap.parse_args()
    
    if not os.path.exists(os.path.join(HERE, "runner")):
        print("Error: ./runner not compiled. Run: gcc -O3 -march=native -fopenmp runner.c -o runner -lm")
        sys.exit(1)
        
    excl = pyrunner.build_exclusion()
    pr = load_progress()
    cursor = pr["cursor"]
    
    t0 = time.time()
    
    print(f"Fast Grind started at cursor {cursor}...")
    
    while cursor < SPACE:
        if args.seconds and time.time() - t0 >= args.seconds:
            print("Time budget exhausted.")
            break
            
        chunk_end = min(cursor + 10000000, SPACE)
        
        # Invoke C runner for this chunk
        cmd = ["./runner", str(cursor), str(chunk_end)]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        for line in p.stdout:
            line = line.strip()
            if not line: continue
            
            parts = line.split()
            if len(parts) == 2:
                seed = int(parts[0])
                sc = float(parts[1])
                
                # Excluded?
                if seed in excl:
                    continue
                
                # High score candidate! Re-run in Python for exact adjudicate pmax.
                pmax = pyrunner.stage_a(seed)
                if pmax > pr["best_pmax"]:
                    pr["best_pmax"] = pmax
                    pr["best_word"] = seed
                
                if pmax >= pyrunner.SCREEN_BAR:
                    print(f"[{seed}] CLEARED SCREEN_BAR: {pmax} (C score: {sc})")
                    # Stage B
                    res = pyrunner.stage_b(seed, n_adj=3)
                    if res["hit"]:
                        print("HIT FLAGGED FOR ORACLE!")
                        pr["flagged_survivors"].append(res)
                        with open(HIT_FILE, "w") as f:
                            json.dump(res, f, indent=1)
                        save_progress(pr)
                        sys.exit(3)
        
        p.wait()
        stderr_out = p.stderr.read()
        if p.returncode != 0:
            print(f"C runner failed: {stderr_out}")
            sys.exit(1)
            
        # Update progress
        chunk_done = chunk_end - cursor
        pr["seeds_done"] += chunk_done # Approximation for excluding logic
        pr["cursor"] = chunk_end
        save_progress(pr)
        
        print(f"Chunk done. Cursor: {chunk_end} ({(chunk_end/SPACE)*100:.2f}%)")
        
    print("Sweep complete or stopped.")

if __name__ == "__main__":
    main()
