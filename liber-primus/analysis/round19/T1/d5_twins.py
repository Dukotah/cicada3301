"""Test Round 8's premise directly at NATIVE resolution: how many DISTINCT bitmaps are
there among the 13k LP2 rune crops?  If the pixel-identical-twin finding holds, the
answer is small and the classification problem is nearly a lookup."""
import numpy as np, collections
import t1_extract as E

for face in ['LP2', 'LP1']:
    z, mask = E.load(face)
    n = len(z['h'])
    keys = collections.Counter()
    for i in range(n):
        keys[(int(z['h'][i]), int(z['w'][i]),
              bytes(np.frombuffer(z['blob'].tobytes()[z['off'][i]:z['off'][i+1]], np.uint8)))] += 1
    c = np.array(sorted(keys.values(), reverse=True))
    print('%s: %d crops -> %d distinct exact bitmaps' % (face, n, len(c)))
    print('   top counts:', c[:12].tolist())
    print('   distinct bitmaps covering 50%%/90%%/99%% of crops: %d / %d / %d'
          % ((np.cumsum(c) < .5*n).sum()+1, (np.cumsum(c) < .9*n).sum()+1,
             (np.cumsum(c) < .99*n).sum()+1))
    print('   singletons: %d (%.2f%% of crops)' % ((c==1).sum(), 100.0*(c==1).sum()/n))
    hw = collections.Counter((int(z['h'][i]), int(z['w'][i])) for i in range(n))
    print('   distinct (h,w) geometries: %d ; top: %s' % (len(hw), hw.most_common(8)))
