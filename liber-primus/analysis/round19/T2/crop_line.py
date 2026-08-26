import os, sys, json
from PIL import Image
import t2lib as T
gl = int(sys.argv[1])
lm = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_linemap.json')))['map']}
rec = lm[gl]
p = os.path.join(T.ROOT, rec['path'])
im = Image.open(p).convert('L')
im.crop((max(0, rec['x0'] - 40), rec['y0'] - 25, min(2400, rec['x1'] + 40), rec['y1'] + 25)).save(
    os.path.join(T.HERE, 'crop_g%d.png' % gl))
print('gline', gl, 'page', rec['num'], 'seg', rec['seg'], 'y', rec['y0'], rec['y1'],
      'x', rec['x0'], rec['x1'], 'ncomp', rec['ncomp'], 'nrune', rec['nrune'])
canon = T.canon_lines()[gl]
print('tokens:', ''.join('#' if t[0] == 'r' else t[1] for t in canon['tokens']))
