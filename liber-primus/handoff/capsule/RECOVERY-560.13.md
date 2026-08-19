# Recovery record — `DATA/560.13`, and a discrepancy found on the way

_2026-08-19, agent H-3. Trust anchor re-run before and after: `python3 tests/validate.py` →
ALL VALIDATIONS PASSED._

## Result

**`DATA/560.13` is RECOVERED.** The item Round 12 front A1 recorded as unfetchable — and which
this capsule's first pass listed as the one **LOST** input — has been retrieved and
cryptographically verified.

```
sha256  db79072ce580efa54acf5f31f3ef0eb00aef867871a051d04e27ee5e7fbc112f
bytes   118818811
```

Both values match the Git-LFS pointer's own claim recorded in
`analysis/round12/A1/lfs_req.json` — which is the authoritative fingerprint, since the pointer is
what the upstream repository committed before the object was deleted. **The recovered bytes are
the real object, not a substitute.**

Placed at `analysis/round12/A1/pads/DATA_560.13` (the 134-byte pointer that previously occupied
that path is preserved beside it as `DATA_560.13.lfs-pointer`). Hash receipt committed at
`handoff/capsule/recovered/DATA_560.13.sha256`; the 118 MB payload itself is gitignored.

**This unblocks `handoff/PARKED.md` P-3** — re-run `analysis/round12/A1/` unchanged. That run was
*not* performed here (two heavy CPU sweeps were already occupying this box, and running it is the
parked item's job, not the capsule's).

---

## What was tried, in order

| # | Attempt | Outcome |
|---|---|---|
| 1 | Git-LFS batch API against the cicada-solvers and krisyotam mirrors | **Dead** — `404 Object does not exist on the server` on both. Reconfirmed Round 12's finding; the object is deleted upstream. |
| 2 | `https://archive.org/metadata/3301.iso` | **Live.** Revealed the item is a **136,398,848-byte** ISO (sha1 `df433cba87644b35cbc47f702a02e2b58d90af6a`), *not* the multi-GB image previously assumed — and that archive.org had indexed 12 members. |
| 3 | `https://archive.org/download/3301.iso/3301.iso/` (inner-file listing) | **Live.** Enumerated 11 files including `DATA/560.13`. This is the step that broke the block: the ISO never had to be downloaded whole to see inside it. |
| 4 | `https://archive.org/download/3301.iso/3301.iso/DATA%2F560.13` (direct member stream) | **HTTP 200, streams.** Does **not** honour `Range` (archive.org extracts on the fly), so a dropped connection restarts from zero. First attempt died at ~30 MB. |
| 5 | Whole ISO with `curl -C -` | **Range works on the raw ISO** (`206 Partial Content`, `Content-Range: bytes 0-99/136398848`), so it is resumable in bounded chunks — the reliable fallback when route 4 drops. |
| 6 | Retry of route 4 | **Completed at 118,818,811 bytes; hash verified.** |

**Route to use in future:** try the direct member URL (route 4) first — it is one request and no
wasted bytes. If the connection drops, fall back to the resumable whole-ISO download (route 5)
plus `handoff/capsule/iso_extract.py`, a stdlib-only ISO9660 extractor written for this recovery
because the machine had no `7z`, `bsdtar`, `xorriso`, `isoinfo` or `pycdlib`:

```bash
python3 handoff/capsule/iso_extract.py 3301.iso --list
python3 handoff/capsule/iso_extract.py 3301.iso --extract DATA/560.13 --out DATA_560.13
sha256sum DATA_560.13   # must be db79072c…, 118818811 bytes
```

---

## ⚠ Finding: the `_560.00` that Round 12 A1 actually tested is NOT the file in the ISO

While confirming the recovery, every CicadaOS pad in the repo was cross-checked against the
authoritative ISO. One does not match.

| pad | bytes in ISO | bytes tested by A1 | sha256 match? |
|---|---|---|---|
| `DATA/560.13` | 118,818,811 | *(untested — was missing)* | now recovered, verified |
| `DATA/560.17` | 1,183,811 | 1,183,811 | ✅ **identical** (`d5676b1e…`) |
| `AUDIO/761.MP3` | 4,010,732 | 4,010,732 | ✅ size-identical |
| **`DATA/_560.00`** | **3,992,970** | **2,412,544** | ❌ **DIFFERENT FILES** |

- ISO copy: sha256 `a24051a87f0eb25ca21accbd3158fdf7b4911243e5ee1b9778b81182f0d36573`, 3,992,970 B
- Copy A1 tested: sha256 `a9ba66e3fc874ce429948b1ee52b48a00f230698ac7174ed9aefb7d82ba62b59`, 2,412,544 B

The community-archive copy is **1,580,426 bytes short** — about **40% of the file missing**.
`560.17` from the same archive is byte-perfect, so this is a defect specific to `_560.00`, not a
general problem with that mirror.

**Why this matters.** `_560.00` is not a bystander in Round 12 A1 — it is the pad A1 used to
build its **positive control** and its **null ceiling** (`sweep.py`'s `null_ceiling()` loads
`PADS["_560.00"]`). So:

1. **A1's negative over `_560.00` covers only ~60% of the real blob.** Any keystream material in
   the missing 1.58 MB was never fed to the decoder. That lane is *not* closed the way the
   write-up implies.
2. A1's positive control still stands as a *control* — it planted and recovered a signal, proving
   the instrument works — but it was built from a truncated file, so it should be re-derived from
   the authoritative bytes when A1 is re-run.

The authoritative copy has been placed alongside the old one as
`analysis/round12/A1/pads/DATA__560.00.iso-authoritative` (receipt in
`handoff/capsule/recovered/`). **The truncated file was deliberately left in place and not
overwritten**, so that A1's existing results remain reproducible against the input that actually
produced them.

**Recommendation for whoever re-runs A1 (P-3):** sweep `560.13` and the authoritative `_560.00`
in the same run, and record which `_560.00` each result used. This is one extra pad, not extra
work — and it converts a partially-covered negative into a complete one.

---

## What this changes in the capsule

- `pads.cicadaos.DATA_560.13`: status **LOST → RECOVERED**, with a verified sha256 and a live,
  documented fetch route. The capsule now has **zero LOST items**.
- A new item records the authoritative `_560.00` and flags the truncated copy.
- The archive.org `3301.iso` item is now recorded as the **primary** provenance source for all
  CicadaOS pads, ahead of the GitHub community mirrors — it is a first-party artifact (the ISO
  Cicada shipped) rather than a re-upload, and it demonstrably has at least one file the mirrors
  serve incorrectly.

## Durability warning

Everything above rests on **one** surviving host: `archive.org`. The GitHub mirrors have already
lost this object once. If these bytes matter to you, mirror the ISO somewhere durable now — its
sha1 is `df433cba87644b35cbc47f702a02e2b58d90af6a` and it is only 136 MB. That is the whole reason
this capsule exists.
