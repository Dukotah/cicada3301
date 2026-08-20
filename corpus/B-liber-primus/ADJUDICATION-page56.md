# ADJUDICATION — LP2 page 56 (AN END), rune index 19

**Verdict: CANON IS CORRECT. `henkman/liberprimus` is WRONG at this position.**

Status: **DECIDED** against ground truth (page 56 is a solved page).
Date: 2026-08-19. Lane B, branch `corpus-sweep`.

---

## 1. The conflict

From `corpus/B-liber-primus/CONFLICT-henkman-2016.json`, `pages[].page_index == 56`
(the only edit block on that page; both transcriptions carry exactly 85 runes, so this
is a pure substitution, not an insertion/deletion):

| | rune | codepoint | translit | gematria index |
|---|---|---|---|---|
| canon (`relikd` / `krisyotam` / `rtkd`) | ᛉ | U+16C9 | `X` (EOLH) | 14 |
| henkman (repo created 2016-08-14) | ᛚ | U+16DA | `L` (LAGU) | 20 |

Ciphertext neighbourhood (transliterated, runes 10–29):

```
canon    ...OHOAECTHGWWLAE X OAPMD...
henkman  ...OHOAECTHGWWLAE L OAPMD...
                           ^ index 19
```

## 2. Why this one is decidable

Page 56 is **solved**. Its plaintext is published and attested by sources entirely
outside this repository, so it is genuine ground truth and not circular:

- `corpus/C-community/wikis/uncovering-cicada/export_cur_01420.xml:2164`
- GitHub org description of `cicada-solvers/3301-hash-alarm`
  (`corpus/E-tooling/repo_meta.json:605`) — quotes the line verbatim
- Boxentriq's Liber Primus guide and scream314's `liber_primus.md`, both cited at
  `research/06-liber-primus-status.md:59`

All of them read: **"WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO …"**

## 3. Method (established, not guessed)

The AN END cipher, as documented in `liber-primus/ELIMINATION-LEDGER.md:479,525` and
re-implemented independently in `analysis/reproduce/reproduce_page_56_an_end.py`:

- keystream `key[i] = (p_i − 1) mod 29` over the consecutive primes 2, 3, 5, 7, …
  (the totient of a prime; *"the totient function is sacred"*)
- decrypt `P = (C − K) mod 29`, Gematria Primus alphabet, N = 29
- **interrupters**: the F rune (ᚠ, U+16A0) may be a null. A null is dropped from the
  plaintext and does **not** advance the keystream. Which F runes are null is not
  given, so the script beam-searches the skip/keep choices (beam 500) scored by
  English quadgram log-probability.
  Page 56 carries **5 literal F runes** and the search recovers exactly **1 null**,
  at F-occurrence index 3. Start offset is the very first prime (no offset).

This method reproduces the published plaintext from the raw artifact with zero manual
steps — that is what makes it a usable adjudicator.

Raw artifact: `liber-primus/data/sources/relikd_p56_an_end.txt`
SHA-256 `ad3b79a3b1d21e696fff8d95c7652784a930a07a7b41b436f2ddbb7f0c8b886f`
Rune-string SHA-256 `c7fbf793ff74c949c7e250d1ed4e9d420a48f4ceef604dc00b10f02971c6bb6e` (85 runes)

## 4. Commands

```bash
cd /c/Users/dukot/projects/cicada3301
export PYTHONIOENCODING=utf-8

# baseline: the canonical page decodes to the published plaintext
python analysis/reproduce/reproduce_page_56_an_end.py

# the adjudication: same method, both readings, one variable changed
python corpus/B-liber-primus/adjudicate/adjudicate_page56.py
```

## 5. Output

```
page          : LP2 page 56
title         : AN END
method        : keystream (p_i - 1) mod 29 over consecutive primes, decrypt C-K | 1 interrupters recovered at F-occurrences [3]
n_runes       : 85
interrupters  : 5 literal F runes
rune sha256   : c7fbf793ff74c949c7e250d1ed4e9d420a48f4ceef604dc00b10f02971c6bb6e

  ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTOITISTHEDUTYOEUERYPILGRIMTOSEE
  COUTTHISPAGE

  ANEND          FOUND
  WITHIN         FOUND
  THEDEEPWEB     FOUND
  HASHES         FOUND
  DUTY           FOUND
  PILGRIM        FOUND

PASS  LP2 page 56 -- AN END
```

```
==========================================================================
reading        : canon   X (U+16C9)   at rune index 19
translit ctx   : ...OHOAECTHGWWLAEXOAPMD...
nulls found    : [3]
quadgram/char  : -4.5727
plaintext      : ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTOITISTHEDUTYOEUERYPILGRIMTOSEECOUTTHISPAGE
crib words     : 10/10  -> all present
==========================================================================
reading        : henkman L (U+16DA)   at rune index 19
translit ctx   : ...OHOAECTHGWWLAELOAPMD...
nulls found    : [3]
quadgram/char  : -4.6001
plaintext      : ANENDWITHINTHEDEEPWEBHEREEXISTSAPAGETHATHASHESTOITISTHEDUTYOEUERYPILGRIMTOSEECOUTTHISPAGE
crib words     : 9/10  -> MISSING: THEREEXISTS
==========================================================================
canon    plaintext[16:26] = EPWEBTHERE
henkman  plaintext[16:26] = EPWEBHEREE
```

## 6. Reading the result

The two readings differ by 6 in gematria index (X = 14, L = 20), so under a
subtractive keystream the plaintext glyph shifts by exactly 6 as well:

| ciphertext rune 19 | plaintext glyph | sentence |
|---|---|---|
| canon ᛉ X (14) | ᚦ **TH** (2) | `…THE DEEP WEB **THERE** EXISTS A PAGE…` |
| henkman ᛚ L (20) | ᚻ **H** (8) | `…THE DEEP WEB **HERE** EXISTS A PAGE…` |

Everything else on the page — all 84 other runes, the null position, the keystream —
is untouched. The single glyph is the whole difference.

Canon's reading yields the attested sentence and the higher English quadgram score
(−4.5727 vs −4.6001 per character). henkman's reading yields *"within the deep web
here exists a page"*, which is not the published plaintext and is not idiomatic
English. Note the failure mode is subtle: henkman's variant is still *readable*,
because `THERE` → `HERE` deletes rather than corrupts. Quadgram scoring alone
separates them by only 0.027 nats/char — it is the **external ground truth**, not the
score, that decides this.

**Canon is right. henkman is wrong at page 56 index 19.**

## 7. What this calibrates

This is the *only* one of henkman's 13 edit blocks that lands on a solved page, and it
comes out **against** henkman. That is a real, if single, data point:

- henkman's transcription **contains at least one demonstrable rune error** in a place
  where the truth is checkable.
- Its total is 13,072 runes against canon's 13,136 — 64 short. Most of the divergence
  is canon-has-runes-henkman-lacks, the signature of **dropped lines**, i.e. an
  incomplete transcription rather than a competing careful reading.
- Therefore the remaining substantive conflicts — page 33 (`W` vs `B`, ×2) and page 35
  (a ᛒ `B` positioned 5 runes earlier than canon puts it) — should be treated as
  **low-prior candidates, not as evidence canon is wrong**. They still deserve the
  image test, because a single error does not prove every reading wrong, but the burden
  of proof sits on henkman.
  **UPDATE, same day:** the image test was run — see
  `corpus/B-liber-primus/ADJUDICATION-pages33-35-images.md`. All three positions read
  unambiguously in **canon's** favour on the SHA-1-pinned 400-DPI onion7 renders.
  henkman is now **0-for-4** on every conflict that can be checked.
- **No downstream statistic needs re-examining.** Canon survived the one check that
  existed, so the 12,956-rune unsolved index and everything computed from it stand
  unchanged.

## 8. Caveats

- One checkable conflict is a *weak* calibration. It rules out "henkman is a superior
  independent reading" but does not rule out "henkman is right in one or two places
  canon is wrong".
- henkman's repo carries **no provenance statement**, so its independence from the
  2017 rtkd/iddqd root is *unestablished* — only its creation date (2016-08-14,
  per the GitHub API) puts it earlier. An early date does not by itself mean an
  independent reading of the images.
- This adjudication says nothing about pages 0, 3, 6, 19, 26, 39, all of which are
  unsolved and whose divergences are bulk insert/delete blocks (dropped lines), not
  glyph disputes.
