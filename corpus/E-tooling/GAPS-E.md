# GAPS-E — what Lane E did not retrieve, did not read, or could not decide

Everything here is a known hole, stated so the next reader does not mistake silence
for absence of evidence. Nothing in this file is a claim.

---

## 1. Repositories that could not be cloned

The lane was interrupted by a network outage mid-run; a repair pass (`repair2.sh`,
`clone3.sh`) recovered most targets when connectivity returned. These were still
missing at the end of the session. Each has a live GitHub URL and a name in
`all_targets.txt` / `retry2.txt`; re-running `repair2.sh` is the whole recovery
procedure.

| target | URL | status |
|---|---|---|
| `artistofreap-byte/liber-primus-matrix-attack` | https://github.com/artistofreap-byte/liber-primus-matrix-attack | R2-FAIL — empty or removed; name suggests a matrix/Hill attack, worth a second try |
| `cicada-solvers/The-Complete-Cicada3301-Archive` | https://github.com/cicada-solvers/The-Complete-Cicada3301-Archive | R2-FAIL — large archive, likely a clone timeout rather than a 404 |
| `cicada-solvers/gutenberg-txt` | https://github.com/cicada-solvers/gutenberg-txt | R2-FAIL — running-key candidate corpus, large |
| `cicada-solvers/csrkd` | https://github.com/cicada-solvers/csrkd | R2-FAIL |
| `cicada-solvers/project-runeberg` | https://github.com/cicada-solvers/project-runeberg | not retried after the outage |
| ~~`cicada-solvers/solving-3301-code-2013`~~ | | **RETRIEVED** `addb2e64...` — first commit **2014-01-23**, the oldest repository in the corpus; 2013/2014-puzzle tooling, no LP transcription |
| ~~`thomasandfriends/Cicada3301Runes`~~ | | **RETRIEVED** `52e5c7e4...` — single commit **2015-01-09**, the earliest dated rune stream found; see CONFLICTS-E.md C-E-03b |
| ~~`cmbsolver/cmbcidada3301`, `iBotPeaches/cicada_3301`, `sgroveman/cicada3301_lp`, `rtkd/idclip`, `localavaster/cadrypt`, `cijhho123/cicada3301`~~ | | **RETRIEVED** (clone_sha for each is in TOOLS.json) |
| `cmbsolver/cmbcidada3301` | https://github.com/cmbsolver/cmbcidada3301 | queued in `clone3.sh` |
| `iBotPeaches/cicada_3301` | https://github.com/iBotPeaches/cicada_3301 | queued |
| `sgroveman/cicada3301_lp` | https://github.com/sgroveman/cicada3301_lp | queued |
| `rtkd/idclip` | https://github.com/rtkd/idclip | queued — same author as idkfa/iddqd, so likely relevant |
| `localavaster/cadrypt` | https://github.com/localavaster/cadrypt | queued (org mirror `cicada-solvers/cadrypt` was obtained) |
| `thomasandfriends/Cicada3301Runes` | https://github.com/thomasandfriends/Cicada3301Runes | queued |
| `cijhho123/cicada3301` | https://github.com/cijhho123/cicada3301 | queued |
| `neuroretransmit/cicada` | https://github.com/neuroretransmit/cicada | queued (the sibling `neuroretransmit/liberprimus-tool` was obtained) |
| `mortlach/Liber-Primus-Crib-Assist` | https://github.com/mortlach/Liber-Primus-Crib-Assist | **still missing** — clone failed with `early EOF` / `invalid index-pack output`, twice. It generates the crib lists that drive `mortlach/Liber-Primus-Rune-Decrypting`, which WAS retrieved and is one of only two skip-aware tools in the corpus with a positive control. Retry with `--depth 1` or a tarball download. |
| ~~`mortlach/Liber-Primus-Rune-Decrypting`~~ | | **RETRIEVED** `765a0260e88617194a2e2c255a34e519f653a90c` |
| ~~`mortlach/runeglish-lm`~~ | | **RETRIEVED** |
| ~~`henkman/liberprimus`~~ | | **RETRIEVED** `2212f631714711a2d51c858c47dfb6f89ae9ee44` — see CONFLICTS-E.md C-E-03 |
| ~~`yo-yo-yo-jbo/cicada_tools`~~ | | **RETRIEVED** `717625c5...` |
| ~~`krisyotam/cicada3301`~~ | | **RETRIEVED** on the second attempt, `76d3ee8c762f60025822c8c05edbf31351636469` — see CONFLICTS-E.md C-E-03b |

| `cicada-solvers/neuroretransmit-cicada` | https://github.com/cicada-solvers/neuroretransmit-cicada | cloned into a broken checkout, directory removed |

## 2. Sources not searched at all

The brief asked for these; the session did not reach them. None was attempted, so
their absence from `TOOLS.json` says nothing about what they contain.

- **Software Heritage** (`archive.softwareheritage.org`) — the single biggest gap.
  It archives deleted GitHub repositories, which is exactly where pre-2017 LP tooling
  would survive after account deletion. Query by origin URL and by content hash of
  a known rune file.
- **GitHub code search** (as opposed to repo search) for rune codepoints
  (`ᚠ`–`ᛪ`), `Gematria Primus`, `FIRFUMFERENFE`, and literal rune-index
  arrays. Only repo-name/topic search was used here (`search/*.tsv`).
- **Gists.** None searched. Early LP work was often posted as a gist rather than a repo.
- **GitLab, Bitbucket, SourceForge, Codeberg.** None searched.
- **PyPI / npm / crates.io.** None searched; `cicada`, `gematria`, `futhorc` are
  plausible package names.
- **Kaggle / HuggingFace datasets.** None searched.
- **University course projects / theses.** None searched.
- **Forks.** `search/iddqd_forks.tsv` was collected but forks were not individually
  diffed for divergent transcriptions. A fork that edited the transcription would be
  a first-class finding and would be cheap to detect (compare each fork's
  `liber-primus__transcription--master.txt` index hash against the three known ones).

## 3. Decoder assessments not made

`TOOLS.json` carries `decoder_type: "unknown"` for **34 of 108** rows. That value means
exactly one thing: *the decisive key-advance loop was not read in this lane*. It does
**not** mean the tool is rigid, and no count in `REPORT-E.md` treats it as such.

The unknowns worth reading first, by size and by likely relevance:

1. `AegisTrustCore/Liber-Primus-HMS-Run-Time` (8.7k LOC, 2026-08-12) — makes explicit
   claims about routes over page 33 and self-corrects an earlier prime/totient claim;
   the claims deserve checking against its own code.
2. `VzGarnet/Liber-Primus` (5.7k LOC PHP, 88 commits) — no keyed decode loop was found
   by grep, but PHP naming conventions may have defeated the pattern.
3. `Pitchfork-and-Torch/instar` and `/liber-research` (2026-08) — recent, active.
4. `cicada-solvers/cadrypt` and `cicada-solvers/cmbsolverwp` — both carry 12 rune
   files each; the rune files were hashed but the code was not read.
5. `krcdavis/cicada-tools` — 12 rune files, code not read.
6. `cmbsolver/cmbcidada3301` (C#, 2024-12 to 2026-07) — same author as
   `cicada-solvers/lp-decrypter` and `libergo`, i.e. the person who wrote the corpus's
   most thorough interrupter-subset enumeration. Establishing its tier is worth more
   than any other single unknown.
7. `localavaster/cadrypt` (Flutter/Dart, 2021-2023) and `sgroveman/cicada3301_lp`.

## 4. Transcription questions left open

- **C-E-01 is not resolved from pixels.** Neither our `ᚫ` nor scream314's `ᚪ` at
  canon segment 24, rune 172 was checked against the original page scan in this lane.
  It is the only one of the four contested runes that sits on unsolved ciphertext and
  therefore the only one that could change a future decode.
  The concrete way to settle it: `dude123124144/Liber-Primus-Runes-OCR` (vendored,
  2017-03-12) carries per-rune template bitmaps and an OCR script, and its author also
  produced the January-2015 transcription in `resvolver/c1cada`. Running that OCR
  against the page-24 scan would give a third, pixel-derived reading.
- **The 15,857-rune `rtkd/idkfa/data/liber` file** was confirmed to contain all 57
  canon segments but its relationship to the 15,933/15,935 iddqd lineage (78 runes
  fewer) was not characterised.
- **RESOLVED during the session; recorded here so the old question is not re-asked.**
  The provenance of the canon stream is now walked commit by commit across three
  repositories (`thomasandfriends/Cicada3301Runes` 2015-01-09, `resvolver/c1cada`
  2015-01-16 to 2015-01-23, `dude123124144/Liber-Primus-Runes-OCR` 2017-05-10). See
  `CONFLICTS-E.md` C-E-03b. What remains open is only whether the 2015-01-21 correction
  was made against the page images or against another person's post — not answerable
  from git alone.
- **Files under 1,000 runes were not segment-tested** — alphabet tables, single pages,
  key lists, README samples. A single-page transcription that contradicted canon would
  be missed by the current filter.

## 5. Method limits that a reader should know about

- **The rune extractor is codepoint-based.** It maps the 29 standard Gematria Primus
  codepoints plus the one alias `U+16C2 → 11` discovered here. Any *other* alias in a
  file not yet examined would present as missing runes, exactly as the `ᛂ` alias did
  before it was found. The census in `CONFLICTS-E.md` covers only the files scanned.
- **The divergence classifier anchors on the longest common run.** For a file that
  stores the same page twice (a JSON with both `runes` and `raw_section` fields, for
  instance) a flat extraction interleaves the copies and the anchor lands wrong. This
  produced two false CONTRADICTIONs before it was caught. Structured files should be
  parsed field-wise, and only `Skyro7777777/LiberPrimusDecoded` was handled that way.
- **`decoder_type_scan.json` is a keyword scan, not a parse.** It is a search aid for
  locating the decisive loop; every `decoder_type` value in `TOOLS.json` other than
  `unknown` rests on a human read of named lines, cited in `decoder_evidence`.
- **Licence detection is pattern-based** over `LICENSE`/`COPYING` files. `NOT-STATED`
  means no licence file was found in the clone — it does **not** mean the work is
  public domain, and nothing in `vendor/` has been relicensed. Repos whose only
  licence signal is GitHub's API `license` field are recorded as `NOT-STATED` here
  because `repo_meta.json` was not refreshed after the outage.
- **`vendor/` is gitignored.** Only manifests and findings are committed. Every row in
  `TOOLS.json` carries `url` + `clone_sha`, which is what makes it reproducible.

## 6. Housekeeping debts

- Two clone loops from the pre-outage session ran concurrently with the repair pass;
  one of them had a path bug that cloned into
  `vendor/c/Users/.../vendor/<name>`. Those clones were harvested into `vendor/`, but
  the stray tree should be checked for leftovers before the directory is archived:
  `ls vendor/c/Users/dukot/projects/cicada3301/corpus/E-tooling/vendor`.
- `repo_meta.json` (GitHub API metadata: stars, forks, archived flag, upstream parent)
  predates the outage and is missing the ~25 repos cloned afterwards. `TOOLS.json`
  derives its licence and language from the files on disk instead, so nothing depends
  on it, but a `fetch_meta.py` re-run would add the fork/parent relationships that
  would let duplicate lineages be collapsed automatically.
