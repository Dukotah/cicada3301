import sys, os, glob, hashlib
sys.dont_write_bytecode=True
sys.path.insert(0, os.path.abspath('../I1-new-registers'))
import mappings_r36 as M
fs = sorted(glob.glob('../I1-new-registers/corpora/hebrew_wlc/*'))
h = hashlib.sha256()
for f in fs:
    raw = open(f, encoding='utf-8').read()
    ws = M.osis_words(raw) if hasattr(M,'osis_words') else None
    if ws is None:
        import re; ws=[w.replace('/','') for w in re.findall(r"<w [^>]*>([^<]*)</w>", raw)]
    h.update(M.hebrew_to_ascii(ws).encode())
print(os.environ.get('PYTHONHASHSEED'), h.hexdigest()[:16], [os.path.basename(f) for f in fs])
