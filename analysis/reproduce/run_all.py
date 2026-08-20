#!/usr/bin/env python3
"""Run every reproduce_page_*.py in this directory and report PASS/FAIL.

Exit 0 only if all of them pass.
Run: PYTHONUTF8=1 python analysis/reproduce/run_all.py [-v]
"""
import os
import sys
import glob
import time
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    verbose = "-v" in sys.argv
    scripts = sorted(glob.glob(os.path.join(HERE, "reproduce_page_*.py")))
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    rows, failed = [], 0
    for s in scripts:
        t0 = time.time()
        p = subprocess.run([sys.executable, s], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env)
        dt = time.time() - t0
        ok = p.returncode == 0
        if not ok:
            failed += 1
        rows.append((os.path.basename(s), ok, dt, p.stdout, p.stderr))
        if verbose:
            print(p.stdout)
            if not ok:
                print(p.stderr)

    print("=" * 72)
    print("%-34s %-6s %8s  %s" % ("script", "result", "seconds", "title"))
    print("-" * 72)
    for name, ok, dt, out, err in rows:
        title = ""
        for ln in out.splitlines():
            if ln.startswith("title"):
                title = ln.split(":", 1)[1].strip()
                break
        print("%-34s %-6s %8.2f  %s" % (name, "PASS" if ok else "FAIL", dt, title))
        if not ok and not verbose:
            tail = (err or out).strip().splitlines()[-1:] or [""]
            print("%38s%s" % ("", tail[0]))
    print("-" * 72)
    print("%d/%d passed" % (len(rows) - failed, len(rows)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
