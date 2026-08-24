# CROSSCHECK-CICADA-SOLVERS — the org's repos vs ours, line by line

_2026-08-24. Companion to `REPORT-E.md` (105 vendored repos, decoder tiering) and `GAPS-E.md`._

The question: **has `github.com/cicada-solvers` — the community's own org — already run a test
we are about to re-run, or already run one whose negative we are wrongly trusting?**

Method: pulled the live org listing (`gh api orgs/cicada-solvers/repos --paginate`, 54 repos),
diffed it against `TOOLS.json` by repo basename, then read the code or fetched the results of
every unvendored repo that could plausibly hold a *test* rather than a tool.

---

## 1. Scoreboard

| | count |
|---|---:|
| Live repos in the org | **54** |
| Already vendored under `cicada-solvers/` in `TOOLS.json` | **33** |
| Vendored under the upstream owner instead (`rtkd/idkfa`, `rtkd/idclip`, `cmbsolver/cmbcidada3301`, `micheloosterhof/aldegonde`, `relikd/LiberPrayground`, …) | **5** |
| **Not held in any form** | **16** |

So the org is ~70% covered and every *decoder* in it has been tiered. Nothing found in this
pass contradicts a single negative result in `ELIMINATION-LEDGER.md`.

The 16 that are missing, triaged:

| repo | size | holds a test? | verdict |
|---|---:|---|---|
| **`csrkd`** | 251 MB | **yes — results committed** | **read today, see §2. Rigid. No threat.** |
| **`gutenberg-txt`** | 5.2 GB | no — a *corpus* | **§3 — the actionable one** |
| **`project-runeberg`** | 6.8 GB | no — a *corpus in rune-space* | **§3 — the actionable one** |
| `The-Complete-Cicada3301-Archive` | 487 MB | no — artifacts | closes `GAPS.md` **G-01** |
| `neuroretransmit-cicada` | 2.1 GB | no — artifacts/solves archive | closes G-01 |
| `document-cicada-2014-micheloosterhof` | 101 MB | no — 2014 artifacts | closes G-01 |
| `a2e7j6ic78h0j-archive`, `845145127.com` | small | no — forum/site archive | closes G-01 (2012 era) |
| `joutguess`, `joutguess-rebirth` | 15 MB | tool | **already superseded** — we built OutGuess 0.4 from source (`STEGO-VERDICT.md`) |
| `LiberPrTools-Web`, `3301terminal`, `CicadaArchiveTool`, `ale-cicada3301-search`, `wiki-timelines`, `documenting-cicada-2016-micheloosterhof` | small | no | ignorable |

---

## 2. `csrkd` read in full — the claim it could have broken, and does not

`csrkd` = "Cicada **Shifting Running Key** Decoder". On the name alone it is the one repo in the
org that could falsify `REPORT-E.md` §4.2's headline — *"the intersection of skip-aware and
running-key is empty across 105 repositories"* — and could mean the community had already run
our open lane #1. It failed to clone twice (`GAPS-E.md` §1) so it was never read.

Read today from `raw.githubusercontent.com` (`decoder.py`, `test.py`). **It is tier-1 rigid.**

- Decode loop: `decrypted_index = (runes.index(ct[idx]) - runes.index(cipher_key[idx]) + 29) % 29`
  followed by an unconditional `idx += 1`. **There is no branch that can hold the key pointer.**
- "Shifting" means sliding the **start offset** of the keytext — `generateKey(ct, filtered_key[cycle:])`,
  one output file per `cycle` — not interrupters. Exactly the axis Campaign XVIII showed a rigid
  decoder scores the *correct* key at −7.24 / 8.5% recovery.
- Its keytext is a single text: **the Red Book LP runes** ("thanks mortlach"), swept forward and
  reversed into `data_normal_key/` and `data_reverse_key/`.
- Scoring is `enchant` dictionary hits after a Zipf-cost space-inference pass — a weaker
  instrument than our quadgram beam, with no null model and no positive control.

**Consequences:**

1. `REPORT-E.md` §4.2 stands. csrkd is a running-key tool and it is rigid, so the empty
   intersection holds at 106 repos.
2. Its negative over LP-as-its-own-running-key is **not** a real negative — but we do not need
   it to be. Campaign XVIII already re-ran the self-key / self-referential family **skip-aware**
   (0 hits), so we are ahead of it, not behind it.
3. One `GAPS-E.md` §1 row closes. `TOOLS.json` should gain a `cicada-solvers/csrkd` row at
   `decoder_type: rigid`, `null_trustworthy: false`, `decoder_evidence: decoder.py idx += 1`.

---

## 3. The one thing we are genuinely missing: their keytext corpora

`ELIMINATION-LEDGER.md` § "Still genuinely open" item **#1** is *"an untried already-public
keytext"*, and says the fix is *"trivially extendable: add a slug to `fetch_keytexts.py`"*.
We have swept ~200 named texts. The community pre-assembled, for precisely this purpose:

| corpus | size | what it is |
|---|---:|---|
| `cicada-solvers/gutenberg-txt` | 5.2 GB | a flat Project Gutenberg `.txt` dump — **≥1,000 files** at the root alone |
| `cicada-solvers/project-runeberg` | 6.8 GB | mortlach's Nordic-literature corpus **already transliterated into runes** |
| `mortlach/projectRuneberg_2022` | **31 GB** | "even more data for books, in runes" |

The rune-space ones matter more than their size suggests: they remove the transliteration
degrees of freedom (C→K/F, QU→KW/CW) that our own sweeps have to guess at, because the
community fixed a convention when they built them.

**Neither corpus has ever been swept by a trustworthy instrument.** csrkd is rigid; every other
running-key tool in the corpus is rigid or skip-capable-without-search. So this is not
"re-running their test" — it is running the *first* sound test over material they only collected.

This is the highest-value item in this document.

---

## 4. mortlach — the highest-value external witness, 2 of 17 repos held

`round10b/PA-1/CENSUS.md` already named mortlach as the field's most disciplined solver
(`Liber-Primus-Rune-Decrypting` is one of only two tools in 105 with a skip-aware search **and**
a positive control). We hold **2 of their 17 repos**.

| repo | size | pushed | why it matters |
|---|---:|---|---|
| **`RuneDecrypterPrime`** | 828 MB | **2026-08-24 — today** | active work by the strongest solver in the field, right now, unread |
| **`Liber-Primus-Crib-Assist`** | 1.5 GB | 2024-04-30 | generates the cribs driving their decrypter; **clone failed twice** (`GAPS-E.md`) |
| `key-drag` | 22 MB | 2024-07-27 | Cython key-application; `py_test_own_text.py` is a plant-and-recover control — *"These should never fail"* |
| `Key_search` | 47 MB | 2018 | *"Checking keys (with wildcards) against the prime sequence (**491 hits**)"* — a positive claim we have not audited |
| `n-grams`, `google_ngrams_Version-20200217` | 5 GB / 13.5 GB | | scoring corpora |
| `LP_Hangman` | 1.25 GB | 2022 | word-shape guessing — adjacent to our SKELETON lane |

**Also not ingested:** `cicada3301.boards.net`, mortlach's own technical threads (flagged in
`CENSUS.md` §2, still open).

---

## 5. Vendored but never mined — results sitting on our disk

| repo | what it holds | where it belongs in our ledger |
|---|---|---|
| `Cicada-DWH-HashcatAttempts` | committed hashcat logs: 3 preimage mask spaces (**IPv4**, **all-bytes len 1–5**, **US phone numbers**) × 5 algorithms (sha512, sha3-512, blake2b-512, whirlpool, streebog) | the **AN END / deep-web-hash** section — an outside exhaustion over preimage spaces we would otherwise have to consider ourselves |
| `liber_primus_finds` | `global_cribs/`, **5,259 lines**, 21 crib words × the red-rune sheets (`cross0-2`, `spiral3-4`), each row carrying the shift list and shift-difference sum | cross-check against `analysis/armada_osint/redrune/FINDINGS.md` |
| `3301_assist` | *"base statistics so you can check if your tool is working"* — the community's own instrument-validation baseline | an **external control** for `benchmark/`; the only third-party yardstick our gates could be scored against |
| `LiberPrayground` | a precomputed **`InterruptDB`** | reusable compute — we recompute interrupt hypotheses it already enumerated |
| `monokuma-ConvolutionKernels` | convolution-kernel analysis of the tree images in `32.jpg` / `55.jpg` | a *geometry* angle Round 8 GEOMETRY did not test (it swept glyph shape, micro-spacing, baseline jitter — not image-production kernels) |

---

## 6. One convention risk, found in their issue tracker

Four open/closed issues across `3301chef` (#5), `GPPrimeView` (#1/#2) and `GematriaPrimusTool`
(#2) all say the same thing: **Q/QU transliteration is contested** — community standard is
Q→C/K and QU→KW/CW. Our `src/lp/gematria.py:108` aliases `"Q": 5` (i.e. Q→C). That matches the
standard on Q. **QU as a digraph is not handled**, which is a small, bounded scoring difference
when comparing our decode scores against community-published ones. Not a threat to any null —
our nulls are scored internally against our own English band — but worth stating before quoting
a score at anyone.

---

## 7. Bottom line

**We are not missing a test that would change a verdict.** Every negative in
`ELIMINATION-LEDGER.md` survives this cross-check, and the one repo that could have threatened
the `REPORT-E.md` headline (`csrkd`) turned out to confirm it.

What we are missing is **inputs, not conclusions**:

1. **Sweep `gutenberg-txt` + `project-runeberg` + `projectRuneberg_2022` skip-aware.** This is
   open lane #1 with the corpus already assembled by someone else. Nobody has ever run a sound
   instrument over it.
2. **Clone the mortlach set**, starting with `RuneDecrypterPrime` (pushed today) and
   `Liber-Primus-Crib-Assist` (`--depth 1` or tarball — plain clone has failed twice). Audit the
   `Key_search` "491 hits against the prime sequence" claim.
3. **Cite `Cicada-DWH-HashcatAttempts`** in the AN-END section — it is somebody else's honest
   exhaustion and it costs us nothing.
4. **Run `3301_assist` against `benchmark/`** as an external control.
5. Add `csrkd` to `TOOLS.json` as rigid; strike it from `GAPS-E.md` §1.
6. Pull `The-Complete-Cicada3301-Archive` + `neuroretransmit-cicada` to close `GAPS.md` G-01.
