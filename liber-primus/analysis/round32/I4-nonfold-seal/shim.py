"""shim.py -- environment shim for lane I4 (no writes outside this lane directory).

Known gaps in this checkout (stated in RESULTS.md not_covered):
  * data/keys/welsh/welsh_mabinogion.txt  MISSING  -> CY register cannot be trained; panel is 8-register.
  * data/kjv.txt, data/keys/mabinogion.txt MISSING -> redirected to analysis/bookcipher/books/{kjv,mabinogion}.txt
    (same-named texts; byte-identity with the originals is NOT verifiable here).
The round19/I2 panel.npz is gitignored/unbuilt, so we rebuild it INTO THIS LANE (models/), never into I2.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A = os.path.join(LP, "analysis")
for p in (HERE, os.path.join(A, "round19", "I1"), os.path.join(A, "round19", "I2"),
          os.path.join(A, "round19", "I3"), os.path.join(A, "round20", "P3"),
          os.path.join(A, "round20", "HITFN"), os.path.join(A, "round21", "L1-seal-realmode-proxy"),
          os.path.join(A, "round18", "L7-redteam"), os.path.join(A, "round13", "B04"),
          os.path.join(LP, "src"), os.path.join(A, "campaign18_skip"),
          os.path.join(LP, "benchmark"), os.path.join(A, "round11"),
          os.path.join(A, "round10b", "B6-non-english-plaintext")):
    if p not in sys.path:
        sys.path.insert(0, p)

REDIRECT = {
    os.path.normpath(os.path.join(LP, "data", "kjv.txt")): os.path.join(A, "bookcipher", "books", "kjv.txt"),
    os.path.normpath(os.path.join(LP, "data", "keys", "mabinogion.txt")): os.path.join(A, "bookcipher", "books", "mabinogion.txt"),
}
WELSH = os.path.normpath(os.path.join(LP, "data", "keys", "welsh", "welsh_mabinogion.txt"))
MODELDIR = os.path.join(HERE, "models")

def _read(p):
    q = os.path.normpath(p)
    if q == WELSH:
        return ""
    q = REDIRECT.get(q, q)
    with open(q, encoding="utf-8", errors="ignore") as f:
        return f.read()

def install(build=False):
    import build_models as BM
    import a1_scorer_language as A1
    BM._read = _read
    A1._read = _read
    BM.REGISTERS = [r for r in BM.REGISTERS if r != "CY"]
    BM.NON_ENGLISH = [r for r in BM.NON_ENGLISH if r != "CY"]
    BM.MODELDIR = MODELDIR
    BM.HERE = HERE
    return BM

def load_panel():
    import adjudicate as AD
    AD._PANEL = AD.Panel(os.path.join(MODELDIR, "panel.npz"))
    return AD

if __name__ == "__main__":
    BM = install()
    BM.NULL_DRAWS = 4000
    BM.main()
