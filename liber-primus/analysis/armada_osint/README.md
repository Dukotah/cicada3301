# armada_osint — external-artifact extraction rig (2026-07-27)

Working directory for the OSINT sweep written up in
[`../OSINT-SWEEP-2026-07-27.md`](../OSINT-SWEEP-2026-07-27.md). That doc holds the
findings and the final verdict; this folder holds the **reproducibility tooling and the
small text results**. The bulky raw downloads and extracted binaries (`artifacts/`,
`extracts/*.bin`, ~79 MB of JPEGs / hex blobs / `.bin` / `.png`) are **gitignored** —
they are byte-reproducible from the mirror URLs in the sweep doc, so they are not
committed.

## What's here (committed)

| File | Purpose |
|------|---------|
| `armada.mjs` | Orchestrator: fetches the community mirrors, carves the onion hex blobs, drives the extraction lanes. |
| `keys.txt` | The 60-entry broadened OutGuess password list (gematria words, LP phrases, primes) tested against the onion images. |
| `keytest_T5.py`, `t2_keytest.py`, `t3_keytest.py` | Per-lead extraction / key-test drivers (T2, T3, T5). |
| `ws_audit.py` | Whitespace (tab/space) channel audit across the PGP corpus (lead T6). |
| `extracts/T5-4gq25-2016.outguess.txt` | T5 result — the known 2016 PGP message, reproduced. |
| `extracts/T6.txt` | T6 result — whitespace run-lengths (only re-encode already-known numbers). |

## Results (full table in the sweep doc)

No new break this session. T1 (onion3 5×5-rune image) and T5 (`4gq25.jpg`) extracted to
**already-known Cicada messages** (2013 RSA key / 2016 "path lies empty"). T2 and T3 are
**unidentified high-entropy blobs** (still open, low prior). The broadened key sweep is
**null** — the "hits" are the OutGuess default-key keystream artifact, not payloads.

## Reproduce

Binaries are gitignored; regenerate them, then re-run:

```bash
node armada.mjs          # re-fetch mirrors + carve blobs into artifacts/
python t2_keytest.py     # T2 blob format/entropy detection
python t3_keytest.py     # T3 blob
python keytest_T5.py     # T5 4gq25 extraction
python ws_audit.py       # T6 whitespace channel
```

Mirror URLs (iBotPeaches `/onions/`, Internet Archive per-onion dumps, scream314,
The-Complete-Cicada3301-Archive, krisyotam `original-onion7/`) are listed under
**"Best mirrors"** in the sweep doc.
