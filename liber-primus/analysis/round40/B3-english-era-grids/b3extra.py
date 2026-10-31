#!/usr/bin/env python3
"""R40-B3 supplementary control: B-04 plants restricted to the Z16/bit-group reductions (hi_nib, lo_nib, bits5) and to rev direction."""
import sys, os, random, json
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E, grids as G


class B04Red(G.B04Grid):
    name = "B04red"
    def random_meta(s, rng):
        m = G.B04Grid.random_meta(s, rng)
        m["stage"] = "A"; m["off"] = 0; m["red"] = rng.choice(("hi_nib", "lo_nib", "bits5"))
        lab, b = rng.choice(s.entries); m.update(label=lab, seed=b.hex())
        return m


if __name__ == "__main__":
    o = E.control(B04Red(), npl=10, ndecoy=256, seed=40, regs=("EN_MODERN", "EN_NOVOWEL"))
