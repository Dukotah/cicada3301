"""Instrument throughput calibration (NOT a hypothesis test).

Measures: dense_scan offsets/second, beam_decode seconds/escalation at ms=3 and ms=8,
and keystream construction cost per generator. These numbers size the PREREG budget.
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))     # liber-primus/
sys.path.insert(0, os.path.join(ROOT, "analysis", "round17"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "round13", "B04"))
import numpy as np
import lib_padsweep as L
import skipdecode as sk
import ks as B04KS

C = L.nc.unsolved()
L.trigram_model()

t = time.time(); b = B04KS.make_bytes("sha256_ctr", b"THE PRIMES ARE SACRED", 1 << 20); print("sha256_ctr 1MiB bytes: %.3fs" % (time.time() - t))
t = time.time(); k = B04KS.REDUCTIONS["mod29"](b); print("mod29 reduce 1MiB: %.3fs" % (time.time() - t))
t = time.time(); k5 = B04KS.REDUCTIONS["bits5"](b[:400000]); print("bits5 reduce 400kB: %.3fs -> %d syms" % (time.time() - t, len(k5)))
t = time.time(); r = B04KS.make_bytes("rc4", b"THE PRIMES ARE SACRED", 1 << 20); print("rc4 1MiB: %.3fs" % (time.time() - t))
t = time.time(); r = B04KS.make_bytes("chacha20", b"x", 1 << 20); print("chacha20 1MiB: %.3fs" % (time.time() - t))

K = np.array(k, dtype=np.int16)
for keep in (400, 1000, 4000):
    t = time.time(); hits = L.dense_scan(K, C, sign=-1, keep=keep); dt = time.time() - t
    print("dense_scan n=%d keep=%d : %.2fs  -> %.2f Moff/s" % (len(K), keep, dt, (len(K) - 24) / dt / 1e6))

Kl = [int(x) for x in K]
for ms in (3, 8):
    for head in (400,):
        t = time.time()
        for i in range(5):
            sk.beam_decode([int(x) for x in C[:head]], Kl, sign=-1, o=1000 + i,
                           beam_w=L.BEAM_W, max_skip=ms)
        print("beam head=%d ms=%d beam_w=%d: %.3fs/decode" % (head, ms, L.BEAM_W, (time.time() - t) / 5))
