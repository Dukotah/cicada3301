# L6-archives — FINDINGS

_Adjudication of the pre-registered gates in `PREREG.md` against the already-collected
data. No new corpora fetched. Refute-by-default. Write-scope: this folder only._

## Verdict (one line)

**NULL — H0 retained.** Zero sources clear the HIT bar. No novel LP rune line, no
retrievable key/pad artifact, and **no first-person claim that 3301 distributed cipher
material or keys to insiders**. The two `INSIDER_DELIVERY` hits are about the *publicly
published* Gematria Primus table and fail the falsifier bar by construction.

## What was scanned

| Corpus | Volume | Range | Source of record |
|---|---|---|---|
| CicadaSolvers Discord export (13 channel dumps) | 109,917 msgs / 14.6M chars | 2019-04-30 -> 2026-07-30 | `discord_inventory.txt` |
| r/cicada + r/a2e7j6ic78h0j + r/cicada3301 (posts+comments) | 6 jsonl | 2012-2026 | `fetched/reddit/` |
| Software Heritage — 30 LP git origins | 30 origins, 7 dead-on-GitHub-but-archived | — | `swh_liveness.txt`, `swh_pull.log` |
| jaxonkuipers 3301 communications corpus | 39 signed `.asc` comms | 2012-2017 | `jk_comms_list.txt` |
| Reddit 2012 Mayan-Vigenere decrypt cross-check | 175/185 titles verified | 2012 | `reddit2012_decrypt.txt` |
| Post-sweep recency check (after repo's 2026-07-27 sweep) | 17 rows, all junk/removed | 2026-07-30 -> 08-10 | `post_sweep_recent.txt` |

## Gate results

### G1 NOVELTY — mostly FAIL (already-held or repo-cited)
- The jaxonkuipers `corpus/communications/*.asc` set is the canonical 3301 signed-message
  corpus already held in the repo (key-announcement, key-in-front-of-you, book-code,
  onion pointers, RSA-OAEP challenge, signed ciphertext, public key). **G1 FAILS** — these
  are the exact primary statements the repo already ingested; nothing here is a file never
  fetched.
- The SWH git origins are community solver tools / OCR / decoders (`mortlach/*`,
  `cicada-solvers/liber_primus_finds`, etc.), i.e. derived tooling, not primary corpus.
- Reddit rune posts are file-level novel as raw strings (see rune test below) but their
  *content* is community-authored, not held LP page material.

### G2 RETRIEVABILITY (2026) — Software Heritage DEAD
- Every SWH API call returned the anti-bot interstitial
  (`<title>Making sure you're not a bot!</title>`), zero snapshots retrieved
  (`swh_pull.log`). This is the documented Wayback/CDN failure mode: HTTP 200 serving a
  wall = **DEAD** under G2. The 7 "dead-on-GitHub-but-archived-in-SWH" repos were therefore
  **not actually retrieved**; their in-scope bytes are unavailable in 2026 by this channel.
- Reddit and the Discord export *were* retrievable (live in-scope bytes) — they pass G2 but
  fail on content (below).

### G3 IN-SCOPE — passes for the community corpora, but content is redundant
- Discord/Reddit/jk-comms all bear on LP2 / the 2012-2017 primary record -> G3 satisfied.
  The gate that kills them is not scope; it is the HIT-content bars below.

## Numeric pass/fail tests (the numbers that make the negative mean something)

### Rune-novelty test — comparator VALID, candidates DO NOT clear the HIT bar
`rune_novelty.py` controls **PASS**:
- **C1** held canonical stream -> `novel_runs=0` (must be 0). PASS
- **C2** shuffled canonical (seed 3301) -> `novel_runs=1, novel_runes=13136` (must be >0). PASS
  Comparator is neither broken nor saturating; its novelty verdicts are admissible.

Candidate scan (`HELD CORPUS: 63 files, 274,426 runes`):

| Candidate | runes | novel_runs |
|---|---|---|
| `Cicada_posts.jsonl` | 445 | 7 |
| `Cicada_comments.jsonl` | 2027 | 3 |
| `a2e7j6ic78h0j_*`, `cicada3301_*` | 0 | 0 |

The 10 "novel" runic runs are **not** new LP ciphertext. Transliterated in
`novel_runes_context.txt` they are self-evidently community-authored artifacts:
- `MULTIDIMENTIOENAL STORY GAME` and `WIKILEAKS` — 2017 ADACIC1033 / kstxi wordpress spam
  posts (`kstxi is cicada3301`), a known impersonator, not 3301.
- `UFOOOOFU` — a hobbyist magic-square doodle ("Am I just getting hooked on the first three
  letters UFO?").
- `AIMSN.SORUWSLIA...CRW` and a rune block — a redditor's "Challenge accepted" posts.
- `GOOD LUCK DECODING THE RUNES` — literally an English sentence written in runes.

Per PREREG the HIT bar is a rune line **normalised to the 29-rune Gematria Primus**,
>=8 runes, that is not a re-segmentation of held text. These are novel *strings* but are
disqualified as HITs: they are not LP page material, several carry non-GP codepoints /
transliterate to English or spam URLs, and none is candidate ciphertext. **Rune test = 0
genuine novel LP lines -> NULL.**

### Key-claim test — FAIL (nothing clears the falsifier bar)
Pattern scan of 109,917 Discord messages: `PRIMARY_FIRSTPERSON=64`,
`INSIDER_DELIVERY=2`, `OTP_MENTION=56`.

The pre-registered falsifier bar (inherited verbatim from `RECON-C/fetch_recon_c.sh`)
requires a **first-person or primary-source assertion that 3301 distributed cipher material
or keys to insiders**. "They gave us a wiki / git / forum / access" does **not** meet it.

- All 64 `PRIMARY_FIRSTPERSON` hits are solvers narrating their own *attempts* ("I input the
  key 10FEOGIFT33", "I tried a vigenere key", "working through random keys from Frank's
  Casket") — hypotheses, not delivery claims.
- Both `INSIDER_DELIVERY` hits are about the **Gematria Primus**, a table 3301 published
  openly in the 2012-2014 chain — not private cipher-material delivery:
  1. `dinger7319`: *"3301 **gave us a key called the gematria primus**. Gematria being
     defined as a Kabbalistic method of..."* — the GP is the public rune<->letter alphabet,
     not a key delivered to insiders.
  2. `solving-lp-general`: *"...why **3301 gave us 2 different key tables**. because the one
     from 2013 isn't technically part of LP..."* — again the public GP / 2013 tables.
- The 56 `OTP_MENTION` hits are solver speculation about one-time-pad *structure* of the
  cipher, none an attributed statement that a pad was delivered.

**No message clears the falsifier bar.** 0/109,917.

## Null control — PASS (pipeline is not producing false positives)
- **Rune-hash control:** C1=0 / C2>0 as required (above). The comparator does not
  hallucinate novelty on its own training corpus and does not trivially saturate.
- **Decoy set:** the pre-registered decoys (`scream314/cicada3301`, `iBotPeaches`,
  `relikd/LiberPrayground`, krisyotam onion7, Wayback tor2web `*.onion.to`,
  `gy3hoy2zizvuzvdb.onion`, Zenodo 18199474, `Cicada-DWH-HashcatAttempts`,
  `tweqx/3301-hash-alarm`) are all either already cited in-repo (G1 FAIL) or
  bot-walled/dead (G2 DEAD). **None scored NEW+RETRIEVABLE -> 9/9 rejected as expected.** The
  register is not void.

## Verdict

**NULL. H0 retained.** An untested haystack (the full Discord export, live SWH origins) is
confirmed to *exist*, but nothing in the collected data clears any of the three HIT bars:

- **(a) novel rune:** 0 genuine novel LP lines (comparator valid; the 10 novel strings are
  community spam/doodles).
- **(b) key/pad artifact:** SWH bot-walled DEAD; no retrievable pad-length external data.
- **(c) primary key-delivery statement:** 0/109,917 Discord messages; the only two
  "insider-delivery" mentions are about the **publicly published Gematria Primus**, which
  fails the falsifier bar by construction.

This does not resurrect any linguistic candidate — the Round 7 keytext kill and the OTP
characterisation still bind anything found here. The single load-bearing number: **2
insider-delivery mentions, both the public Gematria Primus, 0 clearing the bar.**
