# OWNER — minting the DOI (Zenodo), step by step

_Written 2026-11-09. Everything the repo side needs is already in place: `.zenodo.json` at the
repo root is valid JSON and current (verified 2026-11-09 — title, author, and a description
that names the 322-row elimination ledger and the Round-43 blind validation). These steps are
owner-only because they need the GitHub account and the Zenodo login._

## One-time setup (~5 minutes)

1. Make the repo **public** on GitHub (Zenodo cannot archive a private repo). If it must stay
   private, use the manual-upload fallback at the bottom instead.
2. Log in at <https://zenodo.org> → **Using GitHub** (links the accounts).
3. Zenodo → account menu → **GitHub** (<https://zenodo.org/account/settings/github/>) →
   find `Dukotah/cicada3301` → flip the toggle **ON**. Zenodo now watches the repo for
   releases. (Nothing is published yet.)

## Cutting the DOI'd release

4. On GitHub: **Releases → Draft a new release**. Tag suggestion: `v2026.11-r44` (or the
   round at cut time). Title: "Elimination record through Round 44". Point it at the
   round-closeout commit on `master`.
5. Publish the release. Zenodo automatically archives the tagged snapshot, reads
   `.zenodo.json` for the metadata, and mints **two DOIs**: a version DOI for this release
   and a **concept DOI** that always resolves to the latest version. Find them at
   <https://zenodo.org/account/settings/github/> → the repo's entry.
6. **Upload the archival bundle to the same Zenodo record.** The GitHub snapshot excludes
   everything gitignored — i.e. all the primary material. Build and attach it:
   ```bash
   # from repo root (see handoff/ARCHIVAL-BUNDLE.md for what's inside and why)
   tar -czf lp-archival-bundle-$(date +%Y%m%d).tar.gz \
       liber-primus/handoff/archival-bundle.manifest.tsv \
       -T <(tail -n +2 liber-primus/handoff/archival-bundle.manifest.tsv | cut -f1)
   ```
   On the Zenodo record: **Edit → Files → upload** the ~1.1 GB tarball → **Publish**.
   (Editing files creates a new version DOI; the concept DOI is unaffected. Alternative:
   upload the bundle as a GitHub release asset too, but GitHub caps assets at 2 GB and is
   not a preservation archive — Zenodo is the destination of record.)

## Where the DOI goes afterward (three files, one commit)

Use the **concept DOI** (the `latest` one) everywhere; cite version DOIs only for
version-specific claims.

7. **`README.md`** — add a DOI badge/line near the top:
   `[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)`
8. **`CITATION.cff`** — add under the top-level keys:
   ```yaml
   identifiers:
     - type: doi
       value: 10.5281/zenodo.XXXXXXX
       description: "Concept DOI (all versions); Zenodo also archives the gitignored primary-material bundle"
   ```
9. **`PROVENANCE.md`** — §3 already says "If a DOI is present … cite the DOI for the archive
   as a whole": replace that conditional with the actual DOI and a one-line note that the
   primary-material bundle (`handoff/ARCHIVAL-BUNDLE.md`) lives on the same record.

Then commit the three edits to `master` (they'll be picked up by the *next* release/DOI
version; that is fine and normal).

## Fallback if the repo stays private

Zenodo → **New upload** → attach (a) `git archive --format=tar.gz HEAD` and (b) the archival
bundle; paste the `.zenodo.json` fields into the form by hand; publish. Same DOI placement
steps afterward.
