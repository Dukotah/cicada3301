"""P1: Round 32 power gate on panel-R36 (build1/panel12.npz). Executes I1's run_gate.py source UNCHANGED except its OUT path
(redirected into this lane). Pre-registered reduced null (4000/2000/2000), 24 reps, nproc=1."""
import os, sys
sys.dont_write_bytecode = True
LANE = os.path.dirname(os.path.abspath(__file__))
I1 = os.path.abspath(os.path.join(LANE, "..", "I1-new-registers"))
src = open(os.path.join(I1, "run_gate.py"), encoding="utf-8").read()
old = 'OUT = os.path.join(HERE, f"out_gate_{TAG}.json")'
assert old in src
src = src.replace(old, f'OUT = {os.path.join(LANE, "out_gate_r36.json")!r}')
sys.argv = [os.path.join(I1, "run_gate.py"), "--panel", os.path.join(LANE, "build1", "panel12.npz"),
            "--test", os.path.join(LANE, "build1", "testhalves12.npz"), "--tag", "r36"]
g = {"__file__": os.path.join(I1, "run_gate.py"), "__name__": "__main__"}
exec(compile(src, os.path.join(I1, "run_gate.py"), "exec"), g)
