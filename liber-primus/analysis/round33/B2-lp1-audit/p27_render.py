import os, sys
sys.dont_write_bytecode = True
exec(open('p27_probe.py').read().split("r, votes = R.build('LP2')")[0])
from PIL import Image, ImageDraw
r, votes = R.build('LP2'); S = r['S']
z, mask = E_.load('LP2')
def first(b):
    k = next(int(k) for k in range(S.n) if int(S.ids[k]) == b); return k
def crop_of(k, pad=14):
    pg = int(z['page'][k]); im = Image.open(T.relikd_path(pg)).convert('L')
    return im.crop((int(z['x0'][k]) - pad, int(z['y0'][k]) - pad, int(z['x1'][k]) + pad, int(z['y1'][k]) + pad)), pg
S_ = 3
tiles = []
for label, b in (('p27:93 (canon U, T1 B)', 586), ('p13:97 bmp421 (canon U)', 421), ('U exemplar bmp282 x57', 282), ('real B exemplar bmp40 x68', 40)):
    k = first(b); c, pg = crop_of(k); tiles.append((label + ' [p%d]' % pg, c.resize((c.width * S_, c.height * S_), Image.LANCZOS)))
W = sum(t.width for _, t in tiles) + 20 * (len(tiles) + 1); H = max(t.height for _, t in tiles) + 50
canvas_ = Image.new('L', (W, H), 255); d = ImageDraw.Draw(canvas_)
x = 20
for lab_, t in tiles:
    canvas_.paste(t, (x, 40)); d.text((x, 10), lab_, fill=0); x += t.width + 20
canvas_.save('p27_93_side_by_side.png')
# context strip, native pixels x3 (source 2400x3600 is the highest resolution on disk)
im = Image.open(T.relikd_path(27)).convert('L')
box = (1330, 1640, 1720, 1810)
st = im.crop(box); st = st.resize((st.width * 3, st.height * 3), Image.LANCZOS)
st.save('p27_93_context_row4.png')
print(im.size, canvas_.size, st.size)
