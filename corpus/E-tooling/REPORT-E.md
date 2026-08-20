# REPORT-E — Third-party Cicada 3301 / Liber Primus tooling: what exists, what it could have found, and what its silence is worth

Lane E of the corpus sweep. Working directory `corpus/E-tooling/`.
Machine-readable companion: **`TOOLS.json`** (91 rows, one per repository).
Transcription conflicts: **`CONFLICTS-E.md`**. Holes: **`GAPS-E.md`**.

The `vendor/` tree (99 clones, ~1.3 GB of third-party code) is gitignored. Every row
in `TOOLS.json` carries `url` + `clone_sha`, so any row can be reconstituted exactly.

---

## 1. The question this lane was opened to answer

This project established a fact about its own instrument that turns out to generalise:

> Under the anti-repeat filter, **rigid decoding scores the CORRECT key as noise**
> (-6.835) while a **skip-aware beam decoder recovers it** (-4.170).
> Round 8 pushed 2.52 x 10^9 decodes through a decoder that could not have succeeded
> even if its hypothesis had been right.

A null from an unvalidated instrument is not a negative. If the public solvers are
mostly rigid, then the accumulated public "we tried that, it doesn't work" is worth
much less than the field believes — and saying so precisely, with the code cited, is a
contribution to the field rather than to this repository.

So: read the decode loop of every tool that has one, and ask a single mechanical
question — **does the key pointer advance unconditionally, or can this program hold
it?**

---

## 2. Three tiers, not two

Reading the code made a binary rigid/skip-aware split untenable. There are three
distinguishable behaviours, and the middle one is the largest and the most misleading:

| tier | behaviour | what a null from it is worth |
|---|---|---|
| **rigid** | key/keystream pointer advances once per ciphertext rune, unconditionally; there is no branch that can hold it | **Nothing**, with respect to any key-skip hypothesis. The instrument is blind to the thing being tested. |
| **skip-capable** | the decode primitive *will* hold the key if you hand it interrupter positions or an interrupter character — but the tool performs **no search** over unknown skip patterns, and its **default call is rigid** (empty interrupter list) | Trustworthy for the two hypotheses it can express: "no interrupters" and "every occurrence of X interrupts". Silent on an irregular pattern, which is what the solved pages actually show. |
| **skip-aware-search** | the tool **searches** which positions interrupt — subset enumeration, beam, hill-climb, annealing — and can therefore recover a key when the pattern is unknown | A real negative, bounded by the space it actually searched (key length, crib window, cipher family). |

The `skip-capable` tier is where the damage is. A reader who greps a repository for
`interrupt` finds hits, concludes the tool handles interrupters, and treats its null as
meaningful. It does handle them — *if a human types them in*. Nothing in the repository
finds them.

---

## 3. The catalogue

91 repositories, sorted by tier. `null_trustworthy` is the answer to "is a published
negative from this tool a real negative?". `decoder_evidence` in `TOOLS.json` names
the file and line every judgement rests on.

### 3.1 Tier 3 — skip-aware search (7 rows, 5 distinct codebases)

| tool | lang | first commit | licence | null trustworthy | what the search actually covers |
|---|---|---|---|---|---|
| `relikd/LiberPrayground` (= `cicada-solvers/LiberPrayground`) | Python | 2021-01-14 | NOT-STATED | **yes** | `LP/InterruptSearch.py` `all()` enumerates **every subset** of candidate interrupter positions; `sequential()` hill-climbs the first `maxdepth=9` interrupts per step. `probability.py` searches key length, interrupts and key **jointly** against an IoC objective, over a precomputed `InterruptDB`. Bounded to **periodic/Vigenere** key lengths — says nothing about running keys. |
| `micheloosterhof/aldegonde` (= `cicada-solvers/aldegonde`) | Python | 2021-10-12 | ISC | partial | `examples/lp_lag5_attack.py` runs four **deterministic** phase rules — `skip:R`, `reset:R`, `word`, `sent` — over additive and reflective shift families, solving each coset by chi-square. It cannot express an *irregular* interrupter subset, only "every R interrupts". |
| `cicada-solvers/lp-decrypter` | Python | 2020-09-12 | NOT-STATED | partial | `get_all_interrupter_position_lists()` returns **every `combinations()` subset** of interrupter positions, and the decode loop holds `key_index` at those positions — but only over a ciphertext **cropped to key length**. Adds a self-consistency filter: a candidate is rejected if a decrypted rune *is* the interrupter rune. |
| `cicada-solvers/JBO-cicada_tools` | Python | 2023-08-13 | NOT-STATED | partial | `research_utils.py:179` yields **all 2^k subsets** of interrupter positions. But it is applied to the **first sentence only**, and `consider_interrupters` defaults to **False** — so the default run is rigid. |
| `jens-wedin/liber-primus` | Python | **2026-08-18** | NOT-STATED | **yes** | `attack_keyskip.py` beam search with a `--selftest` recovering 96-98% of a planted key-skip key. **See section 6: this is not an independent witness.** |

**`micheloosterhof/aldegonde` produces the only properly instrumented negative in the
entire corpus.** It has both halves that everything else lacks:

- a **positive control** — page-57 plaintext re-encrypted with a random 5-shift key
  *plus an interrupter* — which it cracks exactly, key and full plaintext, at only 95
  runes, z ~ +7; and
- a **doublet-preserving null** — shuffle the lag-1 delta stream and rebuild the random
  walk — adopted for a stated reason worth quoting in full: *"against a naive shuffle
  null every real page scores high simply because the corpus lacks adjacent doublets,
  which is exactly how this attack produced plausible-looking false positives before
  the null was fixed."*

That is an outside party discovering, independently, that the corpus's own doublet
anomaly poisons naive significance testing. Its conclusion — real pages top out at
z ~ +3 over 6,710 attack runs, no phase rule clearing the multiple-testing threshold —
excludes period-5 key-schedule-with-interruptor for the shift family, and by
coset-IoC detection for general period-5 polyalphabetic substitution including
Quagmire-style keyed alphabets. **That negative should be treated as real.**

### 3.2 Tier 2 — skip-capable, no search (12 rows)

| tool | lang | first commit | licence | the line that decides it |
|---|---|---|---|---|
| `Taiiwo/cicada` | Python | 2019-08-29 | GPL-3.0 | `cicada/gematria.py:142` `running_shift(key, interrupts, skip_indices)` — on a match it emits the char and does **not** call `next(key)`. Correct hold. Nothing searches either argument. |
| `Taiiwo/TaiiwoBot` | Python | 2022-04-16 | GPL-3.0 | vendors the above; `plugins/Gematria.py:125` parses `interrupts` and `skip_indices` **from a chat command a human types**. |
| `lipeeeee/gematria` | Python | 2023-05-23 | MIT | `lib/gematria.py:180` — Taiiwo's `running_shift` verbatim. |
| `LiberPrimus/primus.py` | Python | 2021-08-13 | NOT-STATED | `primus.py:62` calls `Runes(text).vigenere(key, [], True)` — an **empty interrupter list hard-coded at the call site**. |
| `cicada-solvers/lphelper` | Python | 2021-03-01 | NOT-STATED | `core.py:147` `decription(key, missing_f=[], ...)` — the parameter is literally the missing-F positions; the key cursor holds; the caller supplies the list. |
| `cicada-solvers/LPDecrypter` | Python | 2020-11-27 | MIT | `vigenere_cipher.py:50` `VigenereWithInterruptersCipher` — correct hold semantics; `examples/solve_vigenere.py:38` passes the literal `[48, 74, 84]`. |
| `Protheme-777/Liber-Primus-decoder` | Python | 2026-03-20 | NOT-STATED | `_apply_key(idx, key, fn, skip_f)` — `skip_f` is an **all-or-nothing boolean**. Its hill-climbing and simulated annealing search the *substitution map*, not the interrupter pattern. `beaufort()` does not take `skip_f` at all. |
| `neuroretransmit/liberprimus-tool` | Python | 2024-04-26 | NOT-STATED | holds the key on a skip, then **raises `NotImplementedError("Permutations mode not implemented yet")`** on the non-fast branch — the clearest statement in the corpus that the skip search is the missing piece. |
| `thecornerspore-dev/rune_swiss` | Python | 2024-03-10 | MIT | `rune_swiss.py:194` `decrypt_vigenere(ct, key, skip_indices)`; nothing searches `skip_indices`. |
| `naliferopoulos/3301` | Python | 2021-03-17 | NOT-STATED | `lputils/crypto.py:56` holds the key **but `continue`s without emitting the rune**, so skip-mode output is shorter than the page and misaligned. Treat its skip results as unsound. |
| `Locyyx64/lp-cribbs` | Python | 2024-01-03 | GPL-3.0 | works in differential space; `vkeygetf_diff_err()` emits keys at plus/minus 1 absolute error — a crude tolerance for a **one-step** desynchronisation, not an accumulating skip. |
| `Skyro7777777/LiberPrimusDecoded` | Python | 2026-08-11 | NOT-STATED | its hill-climbing searches 2x2 Hill matrices mod 29, not interrupter positions. |

### 3.3 Tier 1 — rigid (10 rows)

| tool | lang | first commit | licence | the line that decides it | LOC |
|---|---|---|---|---|---|
| **`NoxxGames/LiberPrimus-GPU`** | Python + CUDA | 2026-05-15 | GPL-3.0 | `bounded_execution/reset_advance.py` — `state_position += 1` for **every** transformable token, unconditionally. Its two `ADVANCE_MODES` (`runes_only`, `token_break_preserving`) are word-separator handling; its `RESET_MODES` restart the key at punctuation. The word "interrupt" appears **only in two research-backlog markdown files** — there is no interrupter code path in the engine. | 307k |
| `rtkd/idkfa` | JavaScript | 2018-05-09 | ISC | `lib/shift.js:79` `arrKeyData[i][keyOffset ++]` — post-increment for every futhark char, no branch. Interrupters exist only as `Config.patch`, a hard-coded table of literal positions for pages **already solved**. | 2.2k |
| `cicada-solvers/idkfa-web` | JavaScript | 2018-05-09 | ISC | `lib/shift.js` byte-identical to the above. | 27k |
| `cicada-solvers/libergo` | Go | 2025-09-19 | Apache-2.0 | `pkg/utility/cipher/vigenere.go` — `keyIndex = (keyIndex + 1) % len(cleanKey)` every rune. The only hold is for out-of-alphabet characters (punctuation). | 18k |
| `ale64bit/cicada3301` | Go | 2020-07-10 | MIT | `cipher/vigenere/vigenere.go` — `defer func(){ index++ }()` inside the per-rune closure. Same in `cipher/prime`, `cipher/totient`, `cipher/affine`. | 13k |
| `cicada-solvers/LiberPrimusSolver` | JavaScript | 2019-09-30 | GPL-3.0 | `src/ciphers/vigenere.js` — `this.key.next()` on a `CircularArray` for every rune. Zero skip hits repo-wide. | 1k |
| `r4nd0mD3v3l0p3r/LiberPrimusSolver` | JavaScript | 2019-09-30 | GPL-3.0 | upstream of the above, same file. | 1k |
| `bobby-bobby-bobby-bobby/Libre-Primus-...-Solver-Demo` | Python | 2026-04-23 | NOT-STATED | beam width 256 + genetic pool — over **keys**, with a rigid decode underneath. | 1k |
| `ztlw30813/cicada3301` | Python | 2024-05-20 | NOT-STATED | `decryptor.py:161` and `:358` — `key_idx += 1` unconditionally, **and over the 26-letter Latin alphabet mod 26**, not the 29-rune Gematria Primus. It cannot decode LP runes at all. | 2.6k |
| `Wra1th/Nebuchadnezzar` | Python | 2023-06-22 | NOT-STATED | key and ciphertext zipped position-for-position; no hold. | 0.2k |

### 3.4 no-decoder (34 rows) and unknown (28 rows)

`no-decoder` covers transcriptions, gematria tables, hash/steganography work, page
archives, and UI shells — `resvolver/c1cada`, `scream314/cicada3301`, `rtkd/iddqd`,
`cicada-solvers/GematriaPrimusTool`, `cicada-solvers/3301chef`,
`cicada-solvers/deep-web-hash-as-ed25519`, `crackalamoo/futhorc`, and so on. Full list
in `TOOLS.json`.

**`unknown` means the decisive loop was not read in this lane. It does not mean rigid,
and none of the counts below treat it as such.** The 28 unknowns are listed with
reading priorities in `GAPS-E.md` section 3.

---

## 4. The assessment

### 4.1 The headline count

Of the **29 repositories in this corpus that contain a polyalphabetic rune decoder and
were actually read**:

| tier | count | share of read decoders |
|---|---:|---:|
| rigid | 10 | **34%** |
| skip-capable, no search | 12 | **41%** |
| skip-aware search | 7 rows / 5 distinct codebases | **24%** |

And on the question that matters — **can this tool's published negative be trusted as a
negative?**

| verdict | count |
|---|---:|
| `false` — the decoder could not have succeeded even if its hypothesis were right | **10** |
| `partial` — trustworthy only for "no interrupters" / "every X interrupts" | **16** |
| `true` — searched a space it could actually have succeeded in | **3** (2 distinct codebases, one of them same-week AI work) |

**Roughly three quarters of the read decoders in the public corpus cannot recover a key
under an unknown interrupter pattern.** That is the finding.

### 4.2 Stated as an assessment, with its limits

This is a reasoned assessment from reading 29 decode loops, not a verdict on the field.
Four things bound it:

1. **28 repositories were not read.** Some of them may search skips. The 34/41/24 split
   describes the *read* subset and would move if the rest were read.
2. **"Rigid" is a statement about the code, not about the author.** Most of these
   repositories make no negative claim at all. `rtkd/idkfa` ships as a tool;
   `cicada-solvers/libergo` is infrastructure; `ale64bit/cicada3301` is explicitly
   exploratory. A rigid decoder that never claims a negative has done nothing wrong.
   The problem is downstream: the *field* treats the accumulated absence of results
   from these tools as evidence, and for the key-skip hypothesis it is not.
3. **A rigid negative is still a real negative for the no-interrupter hypothesis.**
   `NoxxGames/LiberPrimus-GPU` sweeps Vigenere key packs and prime-family keystreams
   with hash-pinned fixtures and CI locks. Within the rigid family that is rigorous
   work and the best available baseline. It simply does not reach the key-skip family,
   and its own documentation never claims it does.
4. **Skip-awareness is necessary, not sufficient.** Every tier-3 tool is bounded
   somewhere else instead: `relikd` to periodic key lengths, `lp-decrypter` to a
   key-length crib window, `JBO` to a first sentence with the flag off by default,
   `aldegonde` to period 5 and deterministic phase rules. **No tool in this corpus
   searches skips over a running key.** The intersection of "skip-aware" and
   "running-key" is empty across 99 repositories.

### 4.3 The three patterns worth naming

**The default-off search.** `cicada-solvers/JBO-cicada_tools` contains a genuine
exhaustive interrupter-subset enumerator, and `consider_interrupters=False` in the
signature of every experiment that uses it. A reader who sees the enumerator assumes
the published runs used it. They did not.

**The acknowledged, unwritten search.** `neuroretransmit/liberprimus-tool` holds the
key correctly on a skip and then raises `NotImplementedError("Permutations mode not
implemented yet")` on the branch that would enumerate which skips. The author
identified the exact missing capability and shipped without it. That line is the
cleanest single piece of evidence that this gap is known and unclosed in public tooling.

**The patch table masquerading as interrupter handling.** `rtkd/idkfa` — the reference
decoder, the one most others descend from — handles interrupters through
`Config.patch`, a hard-coded list of literal positions for pages that were *already
solved*. It reproduces the known solutions perfectly and can discover nothing. Because
so much downstream tooling inherits from it, the shape of the reference implementation
is a substantial part of why the corpus looks the way it does.

---

## 5. The transcription result (full detail in `CONFLICTS-E.md`)

### 5.1 Our transcription is attested in January 2015

`resvolver/c1cada` (first commit 2015-01-05) carries an eleven-file LP2 rune
transcription in `perl/page.*.txt`. Concatenated in page order it is **13,136 runes**
with index SHA-256 **`74cebdb074898f4c2742733a421e6d1717068a4f4cf2802d2b50923285aad329`
— bit-for-bit identical to `liber-primus/data/krisyotam_runes.txt`**, all 57 canon
segments verbatim, zero divergences.

Walked commit by commit, the file set reaches that hash at **`fe9b2255`,
2015-01-21T16:34:18+01:00** (the preceding 2015-01-20 draft had a garbled
`page.27-32.txt` of 1,674 runes where the corrected file has 1,433) and has not been
modified since. That is **25.5 months before** the `rtkd/iddqd` root commit `218ed88`
of 2017-03-01. **Our canon does not sit downstream of iddqd.**

Caveat stated plainly: an exact match does not prove two *independent* readings. Both
could descend from one community transcription posted in January 2015. What it does
establish is that the 13,136-rune stream is the long-standing reading and not an
artefact of 2017-era tooling.

### 5.2 Omission versus contradiction, across every vendored transcription

The classifier anchors each canon segment by its longest common run inside the other
file, then labels every `difflib` opcode. Across all rune-bearing vendored files the
result is **164 omissions and exactly four genuine reading conflicts** — spread over
**two** dissenting witnesses that **do not agree with each other**:

| contested rune | canon | resvolver 2015 | iddqd (4 revs) | henkman 2016 | scream314 |
|---|---|---|---|---|---|
| seg 24 @172 (unsolved page 24) | AE | AE | AE | AE | **A** |
| seg 33 @100 | B | B | B | **W** | B |
| seg 33 @117 | B | B | B | **W** | B |
| seg 55 @19 | X | X | X | **L** | X |
| seg 56 @80 (cleartext page) | Y | Y | Y | Y | **E** |

**Canon is the majority reading on every contested rune, and every dissent is a lone
witness.** Segment 56 is decidable from English — canon gives DIUINITY, scream314
gives DIUINITE — which is a demonstrated error on scream314's side and downgrades its
other dissent. henkman's file additionally drops 64 runes outright, which makes it a
noisy witness on substitutions too.

The `henkman/liberprimus` result independently reproduces Lane B's finding from a
separate clone and a separate classifier, with one refinement: the page-35 case Lane B
recorded as "B vs absent" is a **five-place displacement** of the same B rune, not an
absence.

**Only one of the four conflicts could ever matter:** segment 24 rune 172 sits on
unsolved ciphertext and is undecidable from plaintext. It is unresolved from pixels —
see `GAPS-E.md` section 4.

### 5.3 A codepoint alias that silently corrupts reuse

Some transcriptions encode Gematria Primus index 11 (J) as **U+16C2** instead of
**U+16C4**. `cicada-solvers/lp-decrypter`'s `lp_section_data.py` has 933 of the former
and zero of the latter. The alias is old — `resvolver/c1cada` uses it in January 2015
and `cicada-solvers/CICADA2K16-solving-tool` hard-codes it in its 2016 Gematria table.

It is an encoding variant, not a reading difference. But **a tool that reads one of
those files with a plain 29-rune map silently drops every J**, shifting every later
index and desynchronising any keystream. This lane's own classifier reported 55
spurious INDELs and 11 spurious CONTRADICTIONs from that one file before the alias was
found.

### 5.4 Two hashes, one object each

`liber-primus/PROBLEM.json` pins `023312066df4...`; this lane's manifests pin
`74cebdb0...`. **These are different objects, not a conflict.** `0233120...` covers the
**12,956-rune unsolved subset** (canon segments 0-54); `74cebdb0...` covers the **full
13,136-rune canonical file** (all 57 segments). Verified: segments 0..54 sum to exactly
12,956.

---

## 6. A provenance warning that changes how one row must be read

**`jens-wedin/liber-primus` is not an independent third party.** All 8 commits are
authored `Claude <noreply@anthropic.com>`, first commit
`f7d40c225255eea6a19e76e458c6b058babdb668` at **2026-08-18T16:51:25Z** — one day before
this operation. An earlier note in this lane's own `PROGRESS.md` described it as
independently replicating this project's doublet / lag-1 / running-key conclusions.
**That is retracted.** Its agreement is sibling agreement. It remains a good tool — its
`attack_keyskip.py` is one of the few validated skip-aware beam searches here — but it
is not a witness.

Lower-confidence caution, on repo dates alone, for other 2026-vintage entries:
`Skyro7777777/LiberPrimusDecoded` (2026-08-11, sole author `z@container`),
`AegisTrustCore/Liber-Primus-HMS-Run-Time` (2026-08-12),
`Pitchfork-and-Torch/instar` and `/liber-research` (2026-08-14 and 2026-08-18),
`chipper1999/*` (2026-08-07), `hugvig/liber-primus-research` (2026-08-09),
`NoxxGames/LiberPrimus-GPU` (2026-05-15, ships a `.codex/agents` directory),
`bobby-bobby-bobby-bobby/...Solver-Demo` (2026-04-23, a Copilot co-author). Flagged in
`TOOLS.json` `notes`; not treated as corroboration anywhere.

---

## 7. Pre-2017 material recovered

The brief prioritised anything created before 2017-01, since `henkman/liberprimus`
proves pre-root material exists. Six repositories predate the `rtkd/iddqd` root:

| repo | first commit | what it holds |
|---|---|---|
| **`resvolver/c1cada`** | **2015-01-05** | the 13,136-rune transcription identical to canon (see 5.1), plus Perl frequency tooling, XOR/steganography experiments and key-phrase files |
| `cicada-solvers/cicada-runes-2014-transcriber` | 2015-01-10 | browser transcriber for the 2014 runes |
| `cicada-solvers/GematriaPrimusTool` | 2015-02-10 | Gematria Primus transliteration widget |
| `micheloosterhof/cicada-2016` | 2016-01-06 | one 2016-puzzle image with its outguess payload |
| `cicada-solvers/CICADA2K16-solving-tool` | 2016-01-14 | rune/gematria frequency tool; **source of the U+16C2 J alias in later code** |
| `Pv3/Cicada3301` | 2016-03-13 | derivative of the above, with OEIS/word-probability work |

Plus `henkman/liberprimus`, whose `liberprimus.txt` was committed 2016-08-14 and never
edited (5.2), and `dude123124144/Liber-Primus-Runes-OCR` (2017-03-12), an OCR pipeline
with per-rune template bitmaps by the same author as the 2015 `resvolver/c1cada`
transcription.

---

## 8. Top five leads

1. **Run `dude123124144/Liber-Primus-Runes-OCR` against the page-24 scan.** It is
   vendored, it works from per-rune template bitmaps, and its author produced the
   January-2015 transcription that agrees with canon. It is the only realistic way to
   settle C-E-01 — the one contested rune that sits on unsolved ciphertext — with a
   third, pixel-derived reading rather than another copy of someone else's text file.

2. **Nobody has searched skips over a running key.** Across 99 repositories, the
   intersection of "skip-aware search" and "running key" is **empty**.
   `relikd/LiberPrayground` searches interrupters but only over periodic key lengths;
   `jens-wedin/attack_keyskip.py` searches key-skip but only over prime/totient
   streams and declares its own running-key test underpowered. Given that this project
   measures the unsolved pages as near-random running-key, that empty intersection is
   the largest untouched region of the hypothesis space — and it is untouched not
   because it was ruled out but because no instrument was built for it.

3. **Query Software Heritage.** Not attempted in this lane, and the single biggest
   retrieval gap. It archives *deleted* repositories, which is precisely where
   2014-2016 LP tooling survives after an account is removed. Query by origin URL for
   every failed name in `GAPS-E.md` section 1, and by content hash for the known rune
   files — a hit on `74cebdb0...` or `ec3d102a...` from an origin older than
   `resvolver/c1cada` would push the transcription's attested history back further
   still.

4. **Take `micheloosterhof/aldegonde`'s calibration method, not just its result.** It
   is the only outside work that built a doublet-preserving null *and* a positive
   control, and it did so after watching a naive null manufacture false positives. Its
   period-5 exclusion should be adopted as a real negative, and its null construction
   should be adopted as the standard any future negative in this project is held to.
   `examples/lp_lag5_attack.py` is roughly 400 lines and directly reusable.

5. **Retrieve the four `mortlach/*` repositories.** mortlach is a named Liber Primus
   researcher and a co-author of `cicada-solvers/lp-decrypter`, the tool with the most
   thorough interrupter-subset enumeration in the corpus. `Liber-Primus-Crib-Assist`,
   `Liber-Primus-Rune-Decrypting` and the runeglish transition-probability matrices
   were all in flight when this session ended. Given the quality of the lp-decrypter
   search, these are the highest-expected-value outstanding clones — and the runeglish
   language-model matrices in particular bear directly on the scorer problem this
   project already documented in `analysis/round15/SCORER/FINDING.md`.

---

## 9. Reproducing this lane

    cd corpus/E-tooling
    bash repair2.sh                 # clone every target in all_targets.txt into vendor/
    python3 scan_for_tools.py       # mechanical facts   -> tools_facts.json
    python3 decoder_type.py         # keyword search aid -> decoder_type_scan.json
    python3 hash_runes.py           # canon baseline hashes
    python3 diff_transcriptions.py  # segment presence   -> transcription_diff.json
    python3 classify_divergence.py  # omission vs contradiction -> divergence_classified.json
    python3 build_tools.py          # judgements + facts -> TOOLS.json

`judgements.py` holds the hand-authored, code-backed verdicts. It is the only file in
the pipeline that contains an opinion, and every opinion in it names the file and line
it rests on.
