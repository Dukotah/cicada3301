import sys, os, json, re, time, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
LP = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(LP, 'src')); sys.path.insert(0, os.path.join(LP, 'analysis', 'round10', 'L2-map'))
from lp import gematria as g
import mapcommon as M
HERE = os.path.dirname(os.path.abspath(__file__))
PR = [t[3] for t in g.GEMATRIA]
rng = np.random.default_rng(3301)
VARIANTS = ['V1_prime_mod8_rel', 'V2_idx_rel_29', 'V3_idx_abs_card', 'V4_wordsum_rel12']
MINSTEPS = {'V1_prime_mod8_rel': 12, 'V2_idx_rel_29': 12, 'V3_idx_abs_card': 12, 'V4_wordsum_rel12': 10}

# ---------------- turtle: page = list of words (lists of rune idx)
def walk(words, var):
    x = y = 0.0; h = 0.0; segs = []   # (x0,y0,x1,y1,down)
    if var == 'V4_wordsum_rel12':
        for w in words:
            s = sum(PR[i] for i in w)
            h += (s % 12) * 30.0
            L = float(len(w)); down = 0 not in w
            nx = x + L * math.cos(math.radians(h)); ny = y + L * math.sin(math.radians(h))
            segs.append((x, y, nx, ny, down)); x, y = nx, ny
        return segs
    for w in words:
        for i in w:
            if var == 'V1_prime_mod8_rel': h += (PR[i] % 8) * 45.0
            elif var == 'V2_idx_rel_29': h += i * 360.0 / 29
            else: h = (i % 4) * 90.0
            nx = x + math.cos(math.radians(h)); ny = y + math.sin(math.radians(h))
            segs.append((x, y, nx, ny, i != 0)); x, y = nx, ny
    return segs

def strokes(segs):
    out = []; cur = []
    for s in segs:
        if s[4]: cur.append(s)
        else:
            if cur: out.append(cur); cur = []
    if cur: out.append(cur)
    return out

def raster(seglist, size=64, width=3):
    if not seglist: return None
    xs = [v for s in seglist for v in (s[0], s[2])]; ys = [v for s in seglist for v in (s[1], s[3])]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span = max(x1 - x0, y1 - y0, 1e-9); sc = (size - 10) / span
    ox = (size - (x1 - x0) * sc) / 2; oy = (size - (y1 - y0) * sc) / 2
    im = Image.new('L', (size, size), 0); d = ImageDraw.Draw(im)
    for (a, b, c, e, dn) in seglist:
        d.line([(ox + (a - x0) * sc, size - (oy + (b - y0) * sc)), (ox + (c - x0) * sc, size - (oy + (e - y0) * sc))], fill=255, width=width)
    return np.asarray(im, dtype=np.float32) / 255.0

def feat(a):
    b = gaussian_filter(a, 3.0)[::2, ::2]
    v = b.reshape(-1) - b.mean(); n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v

def build_bank():
    fA = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 52); fR = ImageFont.truetype('C:/Windows/Fonts/seguihis.ttf', 52)
    items = [(c, fA) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'] + [(t[1], fR) for t in g.GEMATRIA]
    names = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') + ['rune_' + t[2] for t in g.GEMATRIA]
    F = []; N = []
    for (ch, fo), nm in zip(items, names):
        im = Image.new('L', (128, 128), 0); ImageDraw.Draw(im).text((20, 10), ch, font=fo, fill=255)
        a = np.asarray(im); ys, xs = np.nonzero(a > 100)
        if len(xs) == 0: continue
        if (xs.max()-xs.min()+1)*2.5 < (ys.max()-ys.min()+1) or (ys.max()-ys.min()+1)*2.5 < (xs.max()-xs.min()+1): continue  # drop line-like glyphs (I, 1, rune I)
        crop = Image.fromarray(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
        w, h = crop.size; sc = 54.0 / max(w, h)
        crop = crop.resize((max(1, int(w * sc)), max(1, int(h * sc))))
        can = Image.new('L', (64, 64), 0); can.paste(crop, ((64 - crop.size[0]) // 2, (64 - crop.size[1]) // 2))
        arr = np.asarray(can, dtype=np.float32) / 255.0
        for r in range(4):
            F.append(feat(np.rot90(arr, r))); N.append(f'{nm}@{90 * r}')
    return np.array(F), N
BANK, BNAMES = build_bank()

def score_segs(segs, var):
    st = [s for s in strokes(segs)]
    ms = MINSTEPS[var]; cands = [s for s in st if len(s) >= ms]
    cands += [st[i] + st[i + 1] for i in range(len(st) - 1) if len(st[i]) + len(st[i + 1]) >= ms and len(st[i]) >= 2 and len(st[i + 1]) >= 2]
    def asp(c):
        xs = [v for q in c for v in (q[0], q[2])]; ys = [v for q in c for v in (q[1], q[3])]
        a, b = max(xs) - min(xs), max(ys) - min(ys); return max(a, b) / max(min(a, b), 1e-9)
    cands = [c for c in cands if asp(c) <= 2.5 and len(c) <= 40]
    if not cands: return 0.0, None, None
    R_ = [(c, raster(c)) for c in cands]
    R_ = [(c, a) for c, a in R_ if (a > 0.3).mean() <= 0.18]
    if not R_: return 0.0, None, None
    cands = [c for c, a in R_]
    Fc = np.array([feat(a) for c, a in R_]); S = Fc @ BANK.T
    Z = (S - S.mean(axis=1, keepdims=True)) / (S.std(axis=1, keepdims=True) + 1e-9)   # distinctiveness z of the best template within the bank
    i, j = np.unravel_index(Z.argmax(), Z.shape)
    return float(Z[i, j]), BNAMES[j], cands[i]

def shuffled_words(words, var, r):
    if var == 'V4_wordsum_rel12':
        return [words[k] for k in r.permutation(len(words))]
    flat = [i for w in words for i in w]; nz = [i for i in flat if i != 0]; nz = list(np.array(nz)[r.permutation(len(nz))])
    it = iter(nz); out = []
    for w in words: out.append([0 if i == 0 else int(next(it)) for i in w])
    return out

def null_scores(words, var, n, r):
    return np.array([score_segs(walk(shuffled_words(words, var, r), var), var)[0] for _ in range(n)])

def save_png(segs, fn, size=256, hi=None):
    if not segs: return
    xs = [v for s in segs for v in (s[0], s[2])]; ys = [v for s in segs for v in (s[1], s[3])]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys); sc = (size - 16) / max(x1 - x0, y1 - y0, 1e-9)
    im = Image.new('RGB', (size, size), 'white'); d = ImageDraw.Draw(im)
    for (a, b, c, e, dn) in segs:
        d.line([(8 + (a - x0) * sc, size - 8 - (b - y0) * sc), (8 + (c - x0) * sc, size - 8 - (e - y0) * sc)], fill=(20, 20, 20) if dn else (200, 200, 255), width=1)
    if hi:
        for (a, b, c, e, dn) in hi:
            d.line([(8 + (a - x0) * sc, size - 8 - (b - y0) * sc), (8 + (c - x0) * sc, size - 8 - (e - y0) * sc)], fill=(220, 0, 0), width=2)
    im.save(fn)

def pages():
    P = M.parse(max_page=60); out = []
    for pg in range(57):
        out.append([w for w, wp in zip(P['words'], P['w_page']) if wp == pg])
    txt = open(os.path.join(LP, 'data', 'keys', 'armada18', 'cicada_koans_and_lp_sections.txt'), encoding='utf-8').read()
    ws = [g.keyword_to_indices(w) for w in re.sub(r'[^A-Z ]', ' ', txt.upper()).split()]
    out.append(ws); return out

def planted(var, which=None):
    P = M.parse(max_page=0); w0 = P['words']
    # noise words: first ~100 runes either side
    acc = 0; pre = []
    for w in w0:
        if acc >= 100: break
        pre.append(w); acc += len(w)
    post = [w for w in M.parse(max_page=1)['words'][len(w0):]][:20]
    Fw = [[0, 5, 9]]  # an interrupter-bearing word
    if var == 'V1_prime_mod8_rel':
        o = [i for i in range(29) if PR[i] % 8 == 1][0]; blk = [[o] * 24]
        return pre + [[0]] + blk + [[0]] + post
    if var == 'V2_idx_rel_29':
        return pre + [[0]] + [[1] * 29] + [[0]] + post
    if var == 'V3_idx_abs_card':
        e, n_, w_, s_ = 0, 1, 2, 3  # idx mod 4 -> heading; use idx 4k to get 0 -> avoid idx 0 (F): E=4, N=1, W=2, S=3
        E, N_, W_, S_ = 4, 1, 2, 3
        T = [E] * 12 + [W_] * 6 + [S_] * 12; L = [S_] * 12 + [E] * 9
        return {'T': pre + [[0]] + [T] + [[0]] + post, 'L': pre + [[0]] + [L] + [[0]] + post}[which]
    # V4: 12 words length 3 sum%12==1
    import itertools
    best = None
    for a, b, c in itertools.product(range(1, 29), repeat=3):
        if (PR[a] + PR[b] + PR[c]) % 12 == 1: best = [a, b, c]; break
    return pre + Fw + [best] * 12 + Fw + post

if __name__ == '__main__':
    t0 = time.time(); out = {'controls': {}, 'pages': {}}; os.makedirs('png', exist_ok=True)
    r = np.random.default_rng(11)
    cl = [('V1_prime_mod8_rel', None), ('V2_idx_rel_29', None), ('V3_idx_abs_card', 'T'), ('V3_idx_abs_card', 'L'), ('V4_wordsum_rel12', None)]
    ok = True
    for var, wh in cl:
        words = planted(var, wh); segs = walk(words, var)
        s, nm, cand = score_segs(segs, var); ns = null_scores(words, var, 200, r)
        passed = bool(s > ns.max()); ok &= passed
        key = var + ('_' + wh if wh else '')
        out['controls'][key] = dict(score=s, best_template=nm, null_max=float(ns.max()), null_mean=float(ns.mean()), passed=passed)
        save_png(segs, f'png/plant_{key}.png', hi=cand)
        print(key, round(s, 3), nm, round(float(ns.max()), 3), passed, flush=True)
    out['controls_pass'] = ok
    json.dump(out, open('results.json', 'w'), indent=1)
    if os.environ.get('CONTROLS_ONLY'): sys.exit(0)
    PG = pages(); rows = []
    allsegs = {}
    for v in VARIANTS:
        for pi, words in enumerate(PG):
            segs = walk(words, v); s, nm, cand = score_segs(segs, v)
            ns = null_scores(words, v, 200, r)
            row = dict(var=v, page=pi, n_steps=len(segs), n_strokes=len(strokes(segs)), score=s, template=nm, null_max=float(ns.max()), null_mean=float(ns.mean()),
                       null_q99=float(np.quantile(ns, .99)), above_null=bool(s > ns.max()))
            if row['above_null']:
                big = null_scores(words, v, 25000, np.random.default_rng(100 + pi))
                row['p_refined'] = float((1 + (big >= s).sum()) / 25001); row['flag'] = bool(row['p_refined'] <= 0.01 / 232)
                save_png(segs, f'png/oracle_{v}_p{pi}.png', hi=cand)
            rows.append(row); allsegs[(v, pi)] = segs
        print(v, 'done', round(time.time() - t0), flush=True)
    out['pages'] = rows; out['n_renders'] = len(rows)
    json.dump(out, open('results.json', 'w'), indent=1)
    # contact sheets
    for v in VARIANTS:
        th = 96; cols = 10; rowsn = math.ceil(len(PG) / cols)
        sheet = Image.new('RGB', (cols * th, rowsn * th), 'white')
        for pi in range(len(PG)):
            save_png(allsegs[(v, pi)], 'png/_t.png', size=th)
            sheet.paste(Image.open('png/_t.png'), ((pi % cols) * th, (pi // cols) * th))
        sheet.save(f'png/contact_{v}.png')
    if os.path.exists('png/_t.png'): os.remove('png/_t.png')
    print('done', round(time.time() - t0))
