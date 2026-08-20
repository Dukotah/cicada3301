# `analysis/reproduce/` — one runnable script per solved Liber Primus page

Every solved page in the corpus, reproduced **from the raw artifact to the plaintext
with no manual steps**. Each script loads the runes out of a raw data file, applies the
documented method, prints the plaintext, and `assert`s that the expected words are there.

```
PYTHONUTF8=1 python analysis/reproduce/run_all.py      # all of them, PASS/FAIL table
PYTHONUTF8=1 python analysis/reproduce/run_all.py -v   # plus each page's full output
PYTHONUTF8=1 python analysis/reproduce/reproduce_page_03.py   # just one
```

Last run: **7/7 PASS**, 0.8 s total.

| script | page | title | method | key |
|---|---|---|---|---|
| `reproduce_page_runes_01.py` | LP1 `Runes - 01.jpg` | A WARNING | Atbash | — |
| `reproduce_page_05.py` | LP1 `05.jpg` | SOME WISDOM | direct transliteration | — |
| `reproduce_page_06.py` | LP1 `06.jpg` | A KOAN (master & student) | Atbash + Caesar shift 3 | — |
| `reproduce_page_03.py` | LP1 `03.jpg` | WELCOME | Vigenère + interrupters | `DIVINITY` |
| `reproduce_page_14.py` | LP1 `14.jpg` | A KOAN (circumference) | Vigenère + interrupters | `FIRFUMFERENFE` |
| `reproduce_page_56_an_end.py` | LP2 page 56 | AN END | prime-totient keystream + interrupter | `(p_i − 1) mod 29` |
| `reproduce_page_57_parable.py` | LP2 page 57 | PARABLE | direct transliteration | — |

## Why these are deliberately *not* thin wrappers around the rig

`liber-primus/tests/validate.py` already reproduces the five LP1 solves — by calling
`liber-primus/src/lp`. If a reproduce script simply imported the same modules, agreement
would be a tautology: it would only prove the rig agrees with itself.

So **each script here is a standalone re-implementation.** It inlines its own copy of the
Gematria Primus table, Atbash, the Caesar shift, the mod-29 Vigenère, the quadgram scorer
and the interrupter beam search, and imports nothing from `liber-primus/src`. The only
repository files it reads are raw data:

| file | what it supplies |
|---|---|
| `liber-primus/data/scream314_lp.md` | the LP1 rune transcriptions |
| `liber-primus/data/sources/relikd_p56_an_end.txt`, `..._p57_parable.txt` | the LP2 solved pages |
| `liber-primus/data/english_quadgrams.txt` | the English scorer's counts |

Two independent implementations landing on the same plaintext is evidence. Each script also
prints the SHA-256 of the rune string it read, so the object it decoded is pinned and
comparable against `corpus/B-liber-primus/PAGES.json`.

## The interrupter rule these scripts implement

Only the **ᚠ (F, index 0)** rune is ever a null, **not every ᚠ is one**, and a null ᚠ is
dropped from the plaintext *and does not advance the keystream*. Which ᚠ are null is not
given — it is recovered by a beam search (width 500) over the skip/keep decisions, scored
by quadgram fitness. Recovered sets:

- `03.jpg` — 7 nulls, at ᚠ-occurrences `[2, 4, 5, 6, 9, 11, 13]` of 16
- `14.jpg` — 2 nulls, at ᚠ-occurrences `[1, 2]` of 5
- LP2 page 56 (AN END) — **1 null**, at ᚠ-occurrence `[3]` of 5

## One thing this directory found

`liber-primus/analysis/round11/PHASE0-GATE.py` validates AN END with
`txt.startswith("ANENDWITHINTHEDEEPWEB")` and applies the prime-totient keystream with **no
interrupter handling**. That check passes, but the *tail* of the page decodes to noise under
it: `…ITISTHEDUTYOOETAXTHTEAGETHMRNXEANIEOEAEAAHIATHCJXREO`.

With a single interrupter (ᚠ-occurrence 3) the whole page reads:

```
ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTOITISTHEDUTYOEUERYPILGRIMTOSEECOUTTHISPAGE
```

i.e. *"An end. Within the deep web there exists a page that hashes to [the hex block]. It is
the duty of every pilgrim to seek out this page."* The prefix-only assertion had been hiding
a truncated decode. See `corpus/B-liber-primus/CONFLICTS-B.md` C-05.

## Regenerating

The seven scripts are emitted by `build_reproduce_scripts.py` from one shared template plus
a per-page config, so a fix to the shared cipher code lands in all of them at once:

```
PYTHONUTF8=1 python analysis/reproduce/build_reproduce_scripts.py
```

Edit the generator, never the generated files.

## Not reproducible here, and why

LP2 pages **0–55** (12,956 runes) are unsolved; there is nothing to reproduce. The current
verdict is OTP-class — see `liber-primus/PROBLEM.json`. A candidate solution can be
adjudicated mechanically by `liber-primus/verify_solution.py`.
