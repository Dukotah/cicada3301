"""Round 20 / P2 -- SWEEPROW/2: append n_skips + n_unexplained so downstream sweeps persist
the transcription-robust, language-independent skip channel (T3 5.1, I3 12).

WHY A NEW VERSION, NOT AN EDIT.  I2's SWEEPROW.md 8 freezes SWEEPROW/1: "Additional statistics
are appended as fields 13+ under SWEEPROW/2; readers must accept a longer row whose first 13
fields match. Never change the meaning or the order of an existing field."  This module honours
that contract exactly.  It does NOT touch I2's adjudicate.py -- it composes it:

    fields 0..12   : bit-identical to SWEEPROW/1 (from I2.to_row)
    field 13 n_skips        : int  -- I1 driftbeam's inferred key-skip count for this decode
    field 14 n_unexplained  : int  -- I1 driftbeam's count of non-doublet-consistent advances

Both come straight off the I1 decode result dict (driftbeam.beam_decode returns them).  A
SWEEPROW/2 store is forward-readable by a SWEEPROW/1 reader that slices [:13]; a SWEEPROW/2
reader validates all 15.

The n_skips null curve for adjudicating field 13 lives in nskips_null.json (this lane).  A
Gumbel bar is NOT used: n_skips is a small-range integer, its null is discrete (I3 10.1b).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "analysis", "round19", "I2"))

import adjudicate as A   # noqa: E402  (I2 -- unmodified)

SCHEMA_VERSION = "SWEEPROW/2"
# fields 0..12 are exactly SWEEPROW/1; 13,14 appended (append-only per SWEEPROW.md 8).
ROW_FIELDS = A.ROW_FIELDS + ["n_skips", "n_unexplained"]
assert ROW_FIELDS[:13] == A.ROW_FIELDS, "SWEEPROW/2 must keep SWEEPROW/1's first 13 fields"


def to_row(adj_res, dec_res, kid):
    """Build a SWEEPROW/2 row.

    adj_res : dict from I2 adjudicate(plain_idx)  (fields 0..12)
    dec_res : dict from I1 driftbeam.beam_decode  (provides n_skips, n_unexplained)
    kid     : key/parameter identity (with the header, regenerates the decode)
    """
    row = A.to_row(adj_res, kid)                       # SWEEPROW/1, fields 0..12
    row.append(int(dec_res["n_skips"]))
    row.append(int(dec_res["n_unexplained"]))
    return row


def header(sweep_id, pan=None, **extra):
    """SWEEPROW/2 header: I2's header with the version + field order bumped, plus a pointer to
    the n_skips null curve that field 13 is adjudicated against."""
    h = A.header(sweep_id, pan=pan, **extra)
    h["v"] = SCHEMA_VERSION
    h["fields"] = ROW_FIELDS
    h["nskips_null"] = "analysis/round20/P2/nskips_null.json"
    h["nskips_note"] = ("field 13 (n_skips) is a small-range integer; adjudicate against the "
                        "EXACT discrete tail in nskips_null.json, never a Gumbel bar (I3 10.1b).")
    return h


class RowError(A.RowError):
    pass


def validate_row(row, hdr=None, n_registers=9):
    """Validate a SWEEPROW/2 row: the first 13 fields must be a valid SWEEPROW/1 row, and
    fields 13,14 must be non-negative ints."""
    if isinstance(row, dict):
        missing = [f for f in ROW_FIELDS if f != "kid" and f not in row]
        if missing:
            raise RowError(f"dict row missing SWEEPROW/2 fields: {missing}")
        row = to_row_from_dict(row)
    if not isinstance(row, (list, tuple)):
        raise RowError(f"row must be list/tuple/dict, got {type(row).__name__}")
    if len(row) != len(ROW_FIELDS):
        raise RowError(f"row has {len(row)} fields, {SCHEMA_VERSION} needs "
                       f"{len(ROW_FIELDS)}: {ROW_FIELDS}")
    # first 13 must pass SWEEPROW/1 unchanged (proves byte-compat)
    A.validate_row(list(row[:13]), hdr=None, n_registers=n_registers)
    for i, f in ((13, "n_skips"), (14, "n_unexplained")):
        v = row[i]
        if not isinstance(v, int) or v < 0:
            raise RowError(f"{f} (field {i}) must be a non-negative int, got {v!r}")
    if hdr is not None:
        if hdr.get("v") != SCHEMA_VERSION:
            raise RowError(f"header schema {hdr.get('v')} != {SCHEMA_VERSION}")
        if hdr.get("fields") != ROW_FIELDS:
            raise RowError("header field order does not match SWEEPROW/2")
    return True


def to_row_from_dict(d):
    base = A.to_row(d, d.get("kid", 0))
    return base + [int(d["n_skips"]), int(d["n_unexplained"])]


def validate_store(path, hdr=None, limit=None):
    """Validate a JSONL SWEEPROW/2 store (header line + row arrays). Also confirms a
    SWEEPROW/1 reader can still consume the rows by slicing [:13]."""
    n = 0
    with open(path, encoding="utf-8") as f:
        h = json.loads(f.readline())
        if not isinstance(h, dict) or "fields" not in h:
            raise RowError("line 1 must be the header object")
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            validate_row(row, hdr or h)
            A.validate_row(list(row[:13]))          # forward-compat proof
            n += 1
            if limit and n >= limit:
                break
    return {"path": path, "header": h, "rows_validated": n, "schema": SCHEMA_VERSION}


def screen_nskips(n_skips_value, mode, L, null_path=None, fpr=0.01):
    """Adjudicate one decode's n_skips against the stored discrete null (two-sided, since the
    correct-key footprint can sit on either side of the wrong-key median depending on L/supp --
    see nskips_null.json plants).  Returns the two-sided empirical p and a pass flag at `fpr`."""
    null_path = null_path or os.path.join(HERE, "nskips_null.json")
    nd = json.load(open(null_path, encoding="utf-8"))
    cell = nd["marginal_null"].get(f"{mode}|L{L}")
    if cell is None:
        raise KeyError(f"no null cell {mode}|L{L} in {null_path}; "
                       f"available: {list(nd['marginal_null'])}")
    hist = cell["hist"]; ntot = cell["n"]
    left = sum(c for k, c in hist.items() if int(k) <= n_skips_value) / ntot
    right = sum(c for k, c in hist.items() if int(k) >= n_skips_value) / ntot
    p_two = 2 * min(left, right)
    return {"n_skips": n_skips_value, "mode": mode, "L": L,
            "p_left": left, "p_right": right, "p_two_sided": p_two,
            "extreme": p_two <= fpr}
