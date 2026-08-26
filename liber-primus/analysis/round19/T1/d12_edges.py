import numpy as np, collections, sys, os
import t1_reader as T, t1_extract as E
z, mask = E.load('LP2')
norm = z['w'] <= 90
print('normal-width crops: x0 min %d  x1 max %d' % (z['x0'][norm].min(), z['x1'][norm].max()))
for q in [0, 0.1, 1, 99, 99.9, 100]:
    print('  x0 p%-5s %6.0f    x1 p%-5s %6.0f' % (q, np.percentile(z['x0'][norm], q),
                                                  q, np.percentile(z['x1'][norm], q)))
print('crops with x0 < 500:', collections.Counter(
    (int(z['page'][i]), int(z['x0'][i]), int(z['w'][i])) for i in np.where(norm & (z['x0'] < 500))[0]).most_common(10))
print('crops with x1 > 2000:', len(np.where(norm & (z['x1'] > 2000))[0]))

print('\n=== all components on 73.jpg / 74.jpg left of the first accepted glyph in row 0')
for name, page in [('73.jpg', 56), ('74.jpg', 57)]:
    path = T.vendor_path(name)
    ink = T.page_ink(path)
    comps = T.components(ink)
    glyphs, rows = T.segment_page(path)
    g0 = glyphs[0]
    print(' %s: first accepted glyph x0=%d y0=%d h=%d w=%d' % (name, g0['x0'], g0['y0'], g0['h'], g0['w']))
    near = [c for c in comps if c['x1'] <= g0['x0'] + 20 and
            not (c['y1'] < g0['y0'] - 60 or c['y0'] > g0['y1'] + 60)]
    near.sort(key=lambda c: c['x0'])
    for c in near:
        print('    comp x0=%4d y0=%4d h=%3d w=%3d area=%5d' % (c['x0'], c['y0'], c['h'], c['w'], c['area']))
