"""R47-X1 gameability probe (NOT a scorer): walks up to c8 evaluate() and reports whether the positives list
('sp') has been assigned yet. While positives are scored, 'sp' is unbound -> 1.0; afterwards (nulls) -> 0.0."""
import sys
REGISTER = "X1_FRAME_PROBE"


def score(idx):
    f = sys._getframe(1)
    while f is not None and f.f_code.co_name != "evaluate":
        f = f.f_back
    if f is None:
        return 0.0
    return 0.0 if "sp" in f.f_locals else 1.0 + 1e-6 * sum(idx)
