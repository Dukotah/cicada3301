"""Round 36 / P1 - build panel-R36 by calling I1's builder with fixed parameters, outputs redirected into this lane.

usage: python build_r36.py <outdir>        (e.g. build1, build2)
Fixed: --nine=rebuild (all twelve registers from on-disk corpora), full null (20000 draws x 14 lengths, seed 3301),
mapping variants GREEK/HEBREW/NORSE = 1. I1's builder is imported UNCHANGED; only its output locations are redirected
(MODELDIR, and its out_build12.json open() -> <outdir>/out_build12.json) so nothing is written outside this lane.
"""
import importlib.util, os, sys, builtins

LANE = os.path.dirname(os.path.abspath(__file__))
I1 = os.path.abspath(os.path.join(LANE, "..", "I1-new-registers"))
out = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(LANE, "build1")
os.makedirs(out, exist_ok=True)

sys.argv = [os.path.join(I1, "build_models_r36.py"), "--nine=rebuild"]      # fixed parameters; no --quick, no --v2
spec = importlib.util.spec_from_file_location("build_models_r36", sys.argv[0])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

mod.MODELDIR = out
_i1_out = os.path.join(I1, "out_build12.json")

def _open(path, *a, **k):
    if os.path.abspath(str(path)) == _i1_out:
        path = os.path.join(out, "out_build12.json")
    return builtins.open(path, *a, **k)
mod.open = _open                      # module-global shadow of open(); only affects the builder's own calls

# ---- DETERMINISM FIX (P1 finding). I1's mappings_r36.hebrew_to_ascii builds each consonant cluster's marks as a python `set`
# of single-character strings and iterates it (`for x in m if x in _HV`, `for x in pm if x in _HV`). Iteration order of a str set
# depends on PYTHONHASHSEED, so the (rare: 15 of 384,147 clusters) clusters carrying two vowel marks get their vowel letters in a
# process-dependent order, and the HEBREW rune stream / LM / test half differ run to run. Fix: iterate sorted(marks) (code-point
# order). I1's file is NOT edited (outside this lane); the transform is applied to its function source at import time and asserted.
import inspect
_src = inspect.getsource(mod.MP.hebrew_to_ascii)
_fix = _src.replace("for x in m if x in _HV", "for x in sorted(m) if x in _HV").replace("for x in pm if x in _HV", "for x in sorted(pm) if x in _HV")
assert _fix.count("sorted(") == 2, "determinism patch did not apply"
exec(compile(_fix, "<hebrew_to_ascii sorted-marks patch>", "exec"), mod.MP.__dict__)

mod.main()
