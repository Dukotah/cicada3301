# Community Research — the whole field in one place

_Consolidated 2026-07-07. Goal: **stop re-researching where others have dug.** This is
the single index of every external Cicada 3301 / Liber Primus researcher, repo, wiki,
and tool we know of — what each contributed, its reliability tier, and where a **local
vendored copy** lives so you never need to re-fetch it. Live artifacts are under
[`sources/community/`](community/); transcriptions are under
[`liber-primus/analysis/foundation/`](../liber-primus/analysis/foundation/)._

> Reliability tiers follow [`sources/README.md`](README.md): primary artifacts > solving
> wikis > journalism > forums. Community work is **high-trust for mechanics, low-trust
> for identity.**

---

## 1. Locally vendored (in this repo — no re-fetch needed)

| Source | What it is | Why it matters | Local copy |
|--------|-----------|----------------|------------|
| **scream314/cicada3301** `liber_primus.md` | The most complete solved-page catalog: every LP1+LP2 page, solved plaintext, method, and **the page-number Rosetta Stone** (scream314 jpg ↔ relikd 0-index) | Canonical solved reference **and** resolves Roadmap Track A1 numbering divergence | [`community/scream314_liber_primus.md`](community/scream314_liber_primus.md) |
| **scream314/cicada3301** `2017.md` | The verified April-2017 PGP-signed "Beware false paths" message | Last confirmed 3301 activity; Campaign VI proved it carries no key material | [`community/scream314_2017-pgp-message.md`](community/scream314_2017-pgp-message.md) |
| **krisyotam/cicada3301** `HINTS-NEVER-USED.md` | Catalog of numeric hints nobody has tried as keys: 2012 P.S. digit string, 2013 telnet missing-prime gaps, trailing-space encodings, cookie hashes | Direct feed for Roadmap **Track B3** (untested key artifacts) | [`community/krisyotam_HINTS-NEVER-USED.md`](community/krisyotam_HINTS-NEVER-USED.md) |
| **krisyotam/cicada3301** `README.md` | "Definitive research archive" index of all three rounds | Cross-check / second opinion on the solved corpus | [`community/krisyotam_README.md`](community/krisyotam_README.md) |
| **relikd/LiberPrayground** `README.md` | The interactive solving toolkit (`playground.py`) + the relikd page image set | Our canonical **image numbering** and rune tooling baseline | [`community/relikd_LiberPrayground_README.md`](community/relikd_LiberPrayground_README.md) |
| **6 transcriptions** (krisyotam, relikd, rtkd/r4nd0mD3v3l0p3r, scream314, cicadasolvers, uncovering-wiki) | Machine-readable rune streams | Campaign V proved they are **byte-identical, one origin (rtkd/iddqd)** | [`../liber-primus/analysis/foundation/trans_*.txt`](../liber-primus/analysis/foundation/) |

## 2. Known researchers & repos (catalogued; fetch on demand)

| Who | Contribution | Tier | Status in our work |
|-----|-------------|------|--------------------|
| **rtkd / iddqd** (2017) | The **root transcription** everyone else copies | Primary-ish | Verified as canon origin (Campaign V) |
| **relikd** | LiberPrayground toolkit + image host; onion7 master byte-identical | Primary tooling | Baseline image numbering; vendored |
| **scream314** | Definitive solved-page catalog + page-number map | High | Vendored §1 |
| **krisyotam** | Research archive + HINTS-NEVER-USED leads | High | Vendored §1 |
| **r4nd0mD3v3l0p3r / cadrypt** | Derived transcription + solver code | High (mechanics) | Transcription vendored; = rtkd |
| **cicada-solvers / IRC #cicadasolvers** | The main solving community (Discord/IRC), 2014– | High (mechanics) | Findings folded into campaigns; no key leaked |
| **Uncovering Cicada Wiki** (fandom) | Most complete step archive; the **pp49–51 base-59/60 token-table** claim | Community | **403s on direct fetch** (documented); claim drives Roadmap A2 |
| **Boxentriq** | Beginner-facing LP guide; solved-page summaries, rune ambiguities | Journalism/guide | Cited in `research/06` |
| **clevcode.org** | Primary write-up of the 2012 **Mayan rotation key** | High | Drives Roadmap **Track B1** |
| **connortumbleson (blog)** | 2024 solve walkthroughs | Blog | Context only |
| **Academic** — "Forgery of Cicada 3301 PGP Signatures via SHA-1" (ResearchGate 403192960) | PGP-signature forgery analysis | Journal | Confirms 2017 msg is auth-only |

## 3. What the field agrees on (so we don't re-litigate)

- **Solved:** 2012 & 2013 rounds fully; LP1 ~17 pages; LP2 only ~2 pages (SOME WISDOM,
  A WARNING, plus AN END / parable fragments). See scream314 catalog for each method.
- **Unsolved:** LP2 pages ~0–56 (relikd index). No public solve since **April 2017**.
- **No public external key exists.** No insider ever leaked key material. Every
  machine-readable transcription traces to **one origin** — unanimity ≠ independence
  (Campaign V is the first genuinely image-independent check; canon passes).
- **Page-numbering is not universal.** scream314 uses original jpg numbers with an
  explicit map to relikd 0-index; the fandom wiki uses yet another scheme. **Always
  state which numbering you mean.** The Rosetta Stone is in the scream314 catalog
  (e.g. `66.jpg - 49.jpg` = scream314 p66 = relikd index 49).

## 4. Open community leads we adopted (→ Roadmap §4)

These are the community's own "somebody should try this" items that were never run —
now tracked as Campaign VII:

- pp49–51 as **base-59/60 numeric token table** (fandom wiki) → Roadmap **A2**
- **XOR** pp49–51 data ⊕ 2014 onion-trail hex (wiki author, never did it) → **B2**
- 2012 **Mayan rotation key** vs runes (clevcode) → **B1**
- `HINTS-NEVER-USED` numerics as Gematria keys (krisyotam) → **B3**

## 5. Re-fetch recipe (if a local copy is missing)

```bash
cd sources/community
curl -sSL -o scream314_liber_primus.md         https://raw.githubusercontent.com/scream314/cicada3301/master/liber_primus.md
curl -sSL -o scream314_2017-pgp-message.md     https://raw.githubusercontent.com/scream314/cicada3301/master/2017.md
curl -sSL -o krisyotam_HINTS-NEVER-USED.md     https://raw.githubusercontent.com/krisyotam/cicada3301/master/liber-primus/analysis/HINTS-NEVER-USED.md
curl -sSL -o krisyotam_README.md               https://raw.githubusercontent.com/krisyotam/cicada3301/master/README.md
curl -sSL -o relikd_LiberPrayground_README.md  https://raw.githubusercontent.com/relikd/LiberPrayground/main/README.md
```
The **uncovering-cicada fandom wiki 403s on automated fetch** — read it in a browser;
the pp49–51 token-table claim is the load-bearing item to transcribe by hand.

---

_Maintained as part of [`MASTER-ROADMAP.md`](../MASTER-ROADMAP.md). If you pull in a new
researcher's work, add a row here and vendor the artifact under `sources/community/`._
