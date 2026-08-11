# AN-END deep-web page — fresh, correctly-targeted hunt (2026-08)

_A fresh-POV pass on the one avenue the standing verdict left open: the lost "AN END"
deep-web page. Method: reachability analysis from the 2014 chain grammar + an
address-free local hash-scan + a 4-lens adversarially-verified OSINT armada (12 agents,
all claims live-checked 2026-08). **Result: the avenue is CLOSEABLE** — sharpened from
"cold trail" to **unreachable-by-construction**, with no retrievable in-scope corpus and a
well-sourced 2026 community negative._

## The target (grounded, not from memory)
The solved AN END page (LP2 page 56) reads verbatim:
> AN END: WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO:
> `36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4`
> IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE.

That is the **entire** message: a 512-bit **content** hash (algorithm unconfirmed —
SHA-512 / BLAKE-512 / BLAKE2b) and **no address**. So this was never a cipher problem; it
is a scavenger hunt for a page you find some other way, then hash to verify.

## (1) Reachability — UNREACHABLE BY CONSTRUCTION
Reconstructed the full 2014 trail from the artifacts we hold
(`analysis/armada_osint/artifacts/raw/2014.md`, `onions_ibotpeaches/`): it is **seven
onions, where each onion's SOLVED content yields the NEXT onion's address** — book-code →
`auqgnxjtvdbll3pv` → RSA → `cu343l33nqaekrnw` → column-transposition → `fv7lyucmeozzd5j4`
→ `avowyfgl5lkzfj3n` → `q4utgdi2n4m4uim5` → `ut3qtzbrvs7dtvzp` → `ky2khlqdf7qdznac`
(onion7, which published the Liber Primus).

By that grammar the AN-END target's address is produced by **solving the pages between** —
i.e. LP2 pages 0–54, which are OTP-class and unsolved. There is **no independent address**
in onion7, the AN-END page, the PARABLE page, or the April-2017 "Beware false paths"
message. The page's location is therefore **gated behind the cipher solve** — you cannot
find it without first solving the thing the whole project has shown to be
information-theoretically unsolvable from ciphertext alone.

Independently corroborated by the OSINT armada (all live-checked 2026-08):
- Canonical solver ref (scream314) publishes no AN-END address; it must be derived from
  solved content. <https://github.com/scream314/cicada3301/blob/master/liber_primus.md>
- Boxentriq frames the hash as an endpoint whose route is the unsolved pages.
- Connor Tumbleson's 2024 deep-solve: chain terminates at onion7; no successor Cicada onion
  hosts a fixed target page. <https://connortumbleson.com/2024/12/23/the-cicada-3301-mystery-puzzle-3-solve-part-4/>
- **`gy3hoy2zizvuzvdb.onion` REFUTED** as the destination — it is a search-summary
  hallucination with zero primary corroboration. Discard it (matches the repo's prior
  "gy3hoy5 debunked").

## (2) Address-free local hash-scan — CLEAN NULL (extends prior in the representation axis)
Prior work hashed every held blob's **raw bytes** vs the target across all major 512-bit
digests (null). Since the target is a *page*, this pass attacked the never-covered axis —
**content representations** of the correctly-targeted local Cicada corpus.
- `repr_hashscan.py`: 77 held files (the iBotPeaches onion1–7 chain + held onion/wiki HTML +
  decrypted AN-END/PARABLE text) × ~11 representations (raw / utf8 / HTML-stripped /
  whitespace-collapsed / alnum-upper / letters-only …) × {sha512, sha3_512, blake2b512} =
  **2,574 tests → CLEAN NULL.**
- Closed the armada's one flagged loose end: fetched the *original* (not re-upload)
  anomalous captures from `micheloosterhof/cicada-2014` — stage04 `server-status` (real
  Apache mod_status dump w/ trailing hex-JPEG), stage03 `index.html.2` (hex-JPEG payload),
  stage11 onion7 `index.html` — and hashed them the same way: **132 tests → CLEAN NULL.**

No page or artifact we hold is the pre-image, under any tested representation. (Expected:
all of these are *upstream* of the AN-END target in the chain; a hit would contradict the
chain grammar.)

## (3) No retrievable, correctly-targeted corpus exists
The revive-bar was "a correctly-targeted, locally-held archive that could plausibly contain
the page." It cannot be met:
- **Wayback tor2web CDX** (`onion.to/.link/.city/…`) — the *only* corpus both retrievable
  in 2026 AND correctly-targeted. Verified live: it even indexed the *known* onion7 host
  (`ky2khlqdf7qdznac.onion.to`, 14 rows) — but the only root captures are a 2015 "onion.to
  temporarily not available" **downtime placeholder** + a 302 + robots.txt. **Zero real
  Cicada content was ever archived, even for a known onion.** And Wayback rejects
  wildcard/"any-onion" CDX queries (HTTP 403, auth required) → it supports **lookup of a
  known host only, not blind discovery** — and the AN-END address is exactly what is unknown.
- **DUTA/DUTA-10K** — public but ~2016+ illicit-category sampling; out of time window + topic.
- **DARPA Memex CDR** — only code/schema on GitHub; bulk crawl data never publicly released.
- **LIGHTS** (SRI/GaTech, KDD 2017) — largest era-appropriate crawl but not publicly
  downloadable; market/forum-labeled.
- **Historical Ahmia** — live indexer (most plausible place a 2014 page *could* be indexed)
  but publishes only a current search UI + an MD5 CSAM blacklist; no downloadable 2014 dump,
  no evidence any Cicada onion was ever indexed.

None is both retrievable AND in-scope. Drug-market crawls remain correctly excluded (the
mistake the prior OSINT made).

## (4) 2026 community status — still unfound, well-sourced
- Official CicadaSolvers Cryptanalysis Briefing: **"The referenced hash has never been
  found."** LP2 = 2/58 solved (56, 57). <https://www.cicadasolvers.com/quickstart/>
- Most recent *organized* attack — **`cicada-solvers/Cicada-DWH-HashcatAttempts`** —
  documents **ZERO matches**; latest activity **2025-10-29**. A live, dated negative.
- Passive detector **`tweqx/3301-hash-alarm`** (~15 hash families incl. SHA-512 / BLAKE2b /
  BLAKE-512 / SHA-3 / Streebog / Skein / Whirlpool) — **never logged a hit**; dormant since
  2021 but not retired.
- **No authentic 7A35090F-signed Cicada message since April 2017** → no new address/hint.
- The only 2024-26 "development" is fringe: the non-verified 2026 Zenodo "complete
  translation" (BECKER/OFELLIA, AI-generated) — community-rejected, does not claim the page.

## Verdict
**This avenue is closeable.** The AN-END page is **unreachable-by-construction** (address
gated behind unsolved OTP-class LP2 0–54), no genuinely-retrievable in-scope corpus can
surface it, no page we hold is the pre-image (raw + representation axes both null), and the
live 2026 community status — including an organized hashcat effort as recent as
2025-10-29 — is a clean negative. This is not a "we gave up" cold trail; it is a structural
result: **the only door left is solving LP2 0–54, which is cryptanalysis, not OSINT.**

**One correction to the prior record:** *original* 2014 raw onion captures DO survive
(`micheloosterhof/cicada-2014`, committed 2014-05 by Michel Oosterhof; the `krisyotam`
`cijhho` archive) — not only the 2020 IA re-uploads — but they are upstream of the target and
hash null. "IA copies = re-uploads" was true of IA specifically, not of the GitHub mirrors.

**Residual (passive only, not a retrieval step):** watch the commit feeds of
`Cicada-DWH-HashcatAttempts` and `3301-hash-alarm` for any future non-zero match, and watch
for a new 7A35090F-signed message. Absent one of those, the external front is exhausted.

_Artifacts: `repr_hashscan.py`, `fetched/`, the OSINT armada transcript. All hashes vs
target `36367763…c2a8b4`._
