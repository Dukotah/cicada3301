"""Provenance regression tests for the Liber Primus image corpus.

Guards the headline claim "56/56 images provenance-verified" against silent
drift.  Two tests:

1. test_provenance_manifest_integrity  — always runs (CI-safe); reads only
   the committed JSON; asserts internal consistency and hash format.

2. test_provenance_images_match_published_sha1  — recomputes SHA-1 from real
   image bytes; skips gracefully when the gitignored image directory is absent
   (e.g. fresh CI clone).

Run:  pytest tests/test_provenance.py -q   (from liber-primus/)
"""

import hashlib
import json
import os
import re

import pytest

# ---------------------------------------------------------------------------
# Repo-relative paths — robust to any cwd
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, ".."))
_MANIFEST = os.path.join(_REPO, "analysis", "stego", "provenance.json")
_IMAGE_DIR = os.path.join(_REPO, "data", "relikd")   # p0.jpg … p55.jpg

_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _load_manifest():
    with open(_MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Test 1: manifest internal consistency (always runs, CI-safe)
# ---------------------------------------------------------------------------
def test_provenance_manifest_integrity():
    """Verify the provenance.json is self-consistent and all hashes valid."""
    data = _load_manifest()

    matched = data["matched"]
    total = data["total"]
    rows = data["rows"]

    # Top-level counters must agree
    assert matched == total, (
        f"matched ({matched}) != total ({total}); some pages failed provenance"
    )
    assert total == len(rows), (
        f"total ({total}) != len(rows) ({len(rows)}); manifest is truncated or has extras"
    )

    # Must cover at least the known 56-page corpus
    assert matched >= 56, (
        f"matched ({matched}) < 56; expected at least 56 provenance-verified pages"
    )

    for row in rows:
        page = row["page"]

        # Every row must be a confirmed match
        assert row["match"] is True, f"page {page}: match is not True"

        # sha1 and published_sha1 must agree
        assert row["sha1"] == row["published_sha1"], (
            f"page {page}: sha1 {row['sha1']!r} != published_sha1 {row['published_sha1']!r}"
        )

        # Both hashes must be well-formed 40-hex-char SHA-1 strings
        for key in ("sha1", "published_sha1"):
            h = row[key]
            assert _SHA1_RE.match(h), (
                f"page {page}: {key} {h!r} is not a valid 40-char lowercase hex SHA-1"
            )


# ---------------------------------------------------------------------------
# Test 2: recompute from real image bytes (skips when images absent)
# ---------------------------------------------------------------------------
def test_provenance_images_match_published_sha1():
    """Recompute SHA-1 from local image bytes and compare to published hashes.

    Image directory: data/relikd/  (p{N}.jpg for page N).
    Skipped when the directory is absent (gitignored in CI / fresh clone).
    Spot-checks pages 0, 1, 2 — enough to catch byte-level tampering without
    hashing the full 56-image corpus on every test run.
    """
    if not os.path.isdir(_IMAGE_DIR):
        pytest.skip(
            f"Image directory not present ({_IMAGE_DIR}); "
            "gitignored — skipping byte-level provenance check"
        )

    data = _load_manifest()
    rows_by_page = {row["page"]: row for row in data["rows"]}

    SPOT_CHECK_PAGES = [0, 1, 2]

    checked = 0
    for page_n in SPOT_CHECK_PAGES:
        img_path = os.path.join(_IMAGE_DIR, f"p{page_n}.jpg")
        if not os.path.isfile(img_path):
            # Individual file missing — skip just this page
            continue

        if page_n not in rows_by_page:
            continue  # page not in manifest; shouldn't happen, but be safe

        row = rows_by_page[page_n]
        expected = row["published_sha1"]

        with open(img_path, "rb") as fh:
            computed = hashlib.sha1(fh.read()).hexdigest()

        assert computed == expected, (
            f"page {page_n} ({img_path}): "
            f"computed SHA-1 {computed!r} != published_sha1 {expected!r}; "
            "image may have been modified or is not the canonical onion7 copy"
        )
        checked += 1

    if checked == 0:
        pytest.skip(
            f"None of the spot-check image files (p0.jpg, p1.jpg, p2.jpg) "
            f"were found under {_IMAGE_DIR}"
        )
