# Witness / primary-source document archive (local pointer)

The full 133-file primary-source archive from upstream `krisyotam/cicada3301/papers/`
is mirrored locally at `liber-primus/analysis/attribution/papers-archive/` (~106 MB,
**gitignored** — copyrighted third-party PDFs, re-pullable anytime).

Re-pull:
```
cd /tmp && git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/krisyotam/cicada3301.git m && cd m && \
  git sparse-checkout set papers
cp -r /tmp/m/papers/. <repo>/liber-primus/analysis/attribution/papers-archive/
```

## Why it matters for the key-hunt

This is the community's consolidated primary-source dump: news features, the raw 4chan
`/x/` and `sci` board threads, the a2e7j6ic78h0j7eiejd0120 onion pages #1–8, the leaked
2013 PGP-email threads, PiratePad captures, and the witness profiles. It is the corpus
Campaign XIX's roster sweep (workflow wf_cf045169-3a3) reads against, and the on-disk home
for the primary docs behind Wanner/Eriksson quotes so link rot (The Face already 404s)
can't erase them.

## Roster candidates surfaced by the file list (to run down)

Confirmed-insider vs merely-named still to be adjudicated by the roster workflow:

- **Marcus Wanner** — confirmed 2012 winner (VT Magazine, WNYC, Rolling Stone, Collegiate
  Times profiles all present). Located; outreach in progress (see CAMPAIGN-XIX).
- **Max Bernstein** — `3301 - Max Bernstein.pdf`. NEW name not previously in our records;
  verify whether solver/insider or commentator.
- **CageThrottleUs** — `overview for CageThrottleUs.pdf` (a Reddit user history). Verify
  role (solver / community figure).
- **Calypne** — authored LP how-to material (`3 ways to progress the Liber Primus _
  Calypne.pdf`, `Bit Message addresses _ Calypne.pdf`). A solver-era analyst, likely not
  an insider but a substantive LP contributor.
- **"Sage", "Tekk"** — brood b.0h handles from Wanner's account (already in CAMPAIGN-XIX).
- Cypherpunk lineage docs (Gilmore, Hughes, Zimmermann, Appelbaum, Assange, Cult of the
  Dead Cow) — the Campaign VIII thematic-attribution pool, NOT insiders; do not conflate.
- Hoax/impostor material present and labeled as such: `reddit imposters.pdf`,
  `Message from 3301_Cicada - Pastebin.com.pdf`, the 2015/2017 "Cicada breaks silence"
  PGP messages. Keep these on the CLAIMED/hoax side of the ledger.

## Key primary artifacts already known-relevant

- `a2e7j6ic78h0j7eiejd0120 - #1..8.pdf` — the 2012 onion pages (Campaign VIII noted this
  v2 onion is dead; these captures are the surviving record).
- `Search results for '0x181f01e57a35090f'.pdf` + `header 7A35090F ...pdf` — the PGP key
  7A35090F forensics (Campaign VIII: 503×509×3301).
- `PGP Signed Message April 2017.pdf` — the "Beware false paths" message (Campaign VI:
  zero key payload).
- The leaked-2013-PGP-email threads — provenance of the individualized RSA distribution.
