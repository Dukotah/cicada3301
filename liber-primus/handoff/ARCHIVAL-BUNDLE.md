# ARCHIVAL BUNDLE — the gitignored primary material a clone does NOT ship

_Written 2026-11-09. This file exists because the repository's `.gitignore` deliberately
excludes fetched corpora and raw dumps (per `CLAUDE.md`: "could someone re-derive this file
by running committed code? If yes, ignore it") — which is the right rule for *derived*
artifacts and the wrong outcome for *primary* ones once their sources die. That is not a
hypothetical: the R35 keytext refetch found **10 of 33 texts already corrupted at source**
(globalgrey served 404 pages where books used to be — `analysis/round42/C1-keytexts/RESULTS.md`),
and the R42-S1 full candidate lists were destroyed with their hosting project
(`analysis/round43/D1-export/RESULTS.md`). A future solver cloning this repo gets every
script and every verdict, but **none of the ~2.7 GB of gitignored material** — and about
**1.13 GB of it cannot be re-derived from committed code if the external sources are gone.**_

## 1. Headline numbers

Measured 2026-11-09 by [`build_archival_manifest.py`](build_archival_manifest.py) (hashes
measured, never typed — the capsule rule):

| class | files | size |
|---|---:|---:|
| **IRREPLACEABLE-external** (this bundle) | **3,625** | **1,128.6 MB** |
| REGENERABLE / refetchable-from-durable-sources (NOT bundled — §4) | ~2,900 | ~1,566 MB |
| total gitignored on the canonical machine | ~6,500 | ~2,694 MB |

The exact per-file list — repo-relative path, byte size, sha256 — is the committed sidecar
[`archival-bundle.manifest.tsv`](archival-bundle.manifest.tsv) (3,625 rows). Regenerate /
re-verify on the canonical machine with:

```bash
python3 liber-primus/handoff/build_archival_manifest.py   # from repo root
```

## 2. The IRREPLACEABLE-external trees (what the bundle contains, and why each is primary)

Only files **not tracked by git** inside these trees are bundled (tracked files ship with
every clone). "Irreplaceable" means: the bytes came from an external source that can die
(or already has), and no committed script can rebuild them without that source.

| tree | files | size | what it is / why it cannot be rebuilt |
|---|---:|---:|---|
| `corpus/A-primary-artifacts/` | 1,466 | 657.8 MB | The primary-artifact collection (Lane A, 2026-08-19): fetched original bytes of the 2012–2017 chains (IA items, signed payloads, onion drops) + four mirrored primary GitHub repos (`krisyotam/`, `wiki-uncovering-cicada/`, `cijhho123/`, `Hadyn_cicada/`). The committed `MANIFEST.json` records source URL + sha256 + response headers for 531 fetched items — the provenance survives a loss, the bytes do not. |
| `liber-primus/data/relikd/` | 562 | 92.4 MB | The 56+1 page-image **masters** (2400×3600, SHA-1-verified against the archived onion7 dump — the project's provenance chain) + the relikd upstream's derived PNGs. Upstream is one GitHub repo; the onion7 origin is long dead. |
| `liber-primus/analysis/round12/A1/pads/` | 9 | 126.4 MB | The authored CicadaOS blobs, incl. `DATA_560.13` (118,818,811 B, sha256 `db79072c…` — recovered 2026-08-19 from the archive.org `3301.iso` item, the ONLY known source) and the authoritative `_560.00` (the community mirrors carry a 40%-truncated copy). |
| `liber-primus/analysis/round10/L6-archives/fetched/` | 77 | 91.1 MB | Round 10 archival hunt payloads: the cijhho leak set, reddit exports, Software Heritage pulls. |
| `liber-primus/analysis/armada_osint/artifacts/` | 380 | 81.7 MB | OSINT-sweep raw dumps: onion mirror captures, T1–T7 extraction inputs, the 2012–2017 raw chronology inputs (`raw/{2012..2017}.md` feed the 43-B1 auto keys). The `.gitignore` calls these "re-downloadable" — true in 2026-07, decreasingly true since. |
| `corpus/D-archives/captures/` | 237 | 22.7 MB | tor2web-era (`onion.city` / `onion.link`) capture mirrors of the 2014 hidden services. Tor v2 is dead; these capture sites are dead; only mirrors of mirrors remain. |
| `corpus/G-forensics/raw/` | 808 | 19.2 MB | Raw inputs to the forensics lane (originals the G-forensics scripts analyze — the RESULTS regenerate, the inputs do not). |
| `liber-primus/analysis/round12/C2/texts/` | 33 | 12.0 MB | The 33 R35 keytexts. **The poster child: 10 of 33 are already corrupt 404 captures** (source died between fetch and refetch) — this local copy is what the intact-23 negatives were measured on. |
| `liber-primus/analysis/round43/F5-stored/fetched/` | 16 | 8.4 MB | The R43-F5a/F5b recoveries: the pages-56/57 Wayback masters + Jan-2014 stego carriers (closed R36-O2), and the pastebin/wiki exports holding the **onion-2 timing channel** (the inter-byte interval sequence no prior archive held). |
| `liber-primus/analysis/round19/C3/l8/archives/` | 11 | 7.4 MB | Pre-disclosure mailing-list archive exports (cypherpunks/bitcointalk legs). |
| `liber-primus/analysis/anend_hunt/fetched/` | 3 | 5.0 MB | The AN-END hunt's held corpus (the 2,706-test hash battery's inputs). |
| `liber-primus/analysis/armada_osint/onions_ibotpeaches/` | 23 | 4.5 MB | The ibotpeaches onion-dump mirror: pre/post-page HTML (source of the 256-byte blobs + payload context) and image captures. |

## 3. Producing the bundle — one command, from repo root

```bash
tar -czf lp-archival-bundle-$(date +%Y%m%d).tar.gz \
    liber-primus/handoff/archival-bundle.manifest.tsv \
    -T <(tail -n +2 liber-primus/handoff/archival-bundle.manifest.tsv | cut -f1)
```

Verify any unpacked copy against the manifest:

```bash
tail -n +2 liber-primus/handoff/archival-bundle.manifest.tsv | \
  awk -F'\t' '{print $3 "  " $1}' | sha256sum -c --quiet && echo BUNDLE-INTACT
```

**Intended destination: a Zenodo release asset, uploaded next to the repository snapshot on
the same DOI'd release** (see [`OWNER-DOI-STEPS.md`](OWNER-DOI-STEPS.md)). Zenodo's per-record
limit is 50 GB; this bundle is ~1.1 GB compressed-or-not (mostly already-compressed media).
That puts the primary bytes under the same permanent identifier as the code that interprets
them, so "clone + one download" reconstructs the full evidentiary state.

## 4. REGENERABLE — deliberately NOT bundled (and why that is safe)

| tree | size | regeneration route |
|---|---:|---|
| `liber-primus/analysis/round17/{P1_blockchain,P2_beacons,P3_tables}/data/` | 656 MB | The R36/R42 "dated pads": random.org daily files (published archive since 2006, MD5-verified), NIST beacon, blockchain headers, Marsaglia CDROM — all durable public archives with committed fetch scripts + recorded digests. |
| `liber-primus/analysis/attribution/papers-archive/`, `corpus/F-press-academic/{papers,theses}/` | 162 MB | Published papers/theses with DOIs/URLs in the committed manifests — refetchable from multiple archives. Second-tier candidates for a future bundle v2 if link-rot is observed. |
| `liber-primus/data/{keys,kjv.txt,moby.txt,pride.txt,war.txt}`, `analysis/bookcipher/books/`, `analysis/foundation/`, `analysis/round12/C2`'s Gutenberg tier, `analysis/skeleton/corpus/` | ~160 MB | Project Gutenberg / sacred-texts fetches with committed fetch scripts; sources are massively mirrored. |
| everything else (crops, `.npz`/`.npy`/`.u64`, logs, checkpoints, compiled `sweep32`/`grind27`, `__pycache__`, `candidates.jsonl` bulk) | ~590 MB | Pure derivations of committed scripts over committed-or-bundled inputs — the `.gitignore` block comments name the regenerating script per tree. |

Judgement call, recorded: the dated pads and the papers are *external* too, but their sources
are institutional archives with redundancy, while §2's sources are single GitHub accounts,
single IA items, dead tor2web mirrors and pastebins — the class that has already failed twice.
If the owner wants belt-and-braces, adding the §4 first two rows costs ~0.8 GB more.

## 5. Maintenance rule

When a future lane fetches new primary bytes (anything whose source is a single repo, a
pastebin, a Wayback capture or an onion mirror): add the tree to
`build_archival_manifest.py`'s `IRREPLACEABLE_TREES`, re-run it, and re-cut the bundle at the
next release. The D1 lesson (`analysis/round43/D1-export/RESULTS.md`) generalizes: **pull
load-bearing artifacts into durable storage before the lane that produced them closes.**
