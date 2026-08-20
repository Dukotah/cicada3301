==========================================================================================
REPO: AegisTrustCore__Liber-Primus-HMS-Run-Time
# HMS Endeavour — Liber Primus Public Research Record

> **HMS Endeavour v0.1.0 is the released public research foundation.** This repository is the evidence, verification, puzzle, and public tooling layer for our independent *Liber Primus* research. It is not a claim that the full corpus has been solved.

> **Independent research:** HMS Endeavour is not Cicada 3301, has no affiliation with or endorsement from Cicada 3301, and does not possess Cicada 3301's private signing key. See [Cicada 3301 and the historical OpenPGP key](CICADA_3301.md).

## Current public releases

| Release | What it contains | Access |
|---|---|---|
| [HMS Endeavour v0.1.0](https://github.com/AegisTrustCore/Liber-Primus-HMS-Run-Time/releases/tag/v0.1.0) | Public research foundation, schemas, evidence records, validation source, and provenance tooling | Free / public |
| [Research Release RR-0002](https://github.com/AegisTrustCore/Liber-Primus-HMS-Run-Time/releases/tag/RR-0002) | Five bounded closure and correction packages with a portable evidence archive | Free / public |
| [Research Release RR-0003](https://github.com/AegisTrustCore/Liber-Primus-HMS-Run-Time/releases/tag/RR-0003) | E1477 board-family closure, E156 solved-LP1 segment frames, and E159 terminal known controls | Free / public |
| [HMS GP29 Calculator v0.1.1](https://github.com/AegisTrustCore/Liber-Primus-HMS-Run-Time/releases/tag/GP29-v0.1.1) | Offline Windows desktop and CLI Gematria Primus calculator | Free / public |

Only the releases listed above are downloadable customer-facing GitHub releases. Development source may be visible on `main` before a packaged tool is approved for release.

## Next two public instruments

| Candidate | What is complete | Final gate |
|---|---|---|
| **Corpus Manifest Verifier 0.1.0-rc.3** | Canonical 75-page identity binding, file/folder selection, searchable findings, portable reports, five-case controls, deterministic Windows package | Exact-package visual UAT and owner approval |
| **HMS Endeavour Runtime Environment 1.0.0-rc.1** | GP29, corpus verification, embedded 75-page Atlas with zoom/pan, research objects, bounded experiments, comparison, audit, safe backup, GUI/CLI packaging | Merge the green RC branch, exact-package visual UAT, and owner approval |

Release-candidate source and CI artifacts are not public downloads. When approved, each instrument receives one immutable GitHub release, SHA-256, quick start, limitations, and matching Patreon notice.

## Start here

| I want to… | Start with |
|---|---|
| Understand the 75-page working corpus | [Liber Primus: Start Here](
==========================================================================================
REPO: Eternalth__Liber-Primus
these are drafts for codes that I used to experiment with Liber Primus, code is not documented well (and is old), read at your own risk

==========================================================================================
REPO: Fafison4k__cicada-3301-page32
# Cicada 3301 — Расшифровка страницы 32.jpg (Liber Primus)

Этот репозиторий содержит инструменты для автоматического подбора ключа к одной из неразгаданных страниц.

## 📄 Данные

- `data/runes.txt` — 16 строк рун (Gematria Primus)
- Ожидаемые суммы строк: `3258 3222 3152 3038 3278 3299 3298 2838 3288 3294 3296 2472 4516 1206 708 1820`

## ❌ Что уже проверено и не подошло

- Простые сдвиги Gematria (-10..+10, прямой/обратный)
- Виженер, ключи из книги (FIRFUMFERENFE, DIVINITY, ...)
- Виженер, полный перебор длин 3, 4, 5, 6
- Сдвиг Gematria + Виженер (все комбинации для длин 3-5)
- Обратный порядок строк + Виженер

## 🚀 Как запустить (Rust)

1. `git clone git clone https://github.com/Fafison4k/cicada-3301-pafe32.git`
2. `cp data/runes.txt cicada_brute_src/runes.txt`
3. `cd cicada_brute_src`
4. `rustc -O main.rs -o cicada_brute`
5. `./cicada_brute`

## 💡 Идеи для дальнейших попыток

- [ ] Длина ключа 7+
- [ ] Автоключ (первые N рун как ключ)
- [ ] Перестановка рун внутри строк
- [ ] Running key cipher (ключ — фрагмент текста из книги)
- [ ] Двойная Gematria (сдвиг + сдвиг)
- [ ] Ключ из самих чисел (3258, 3222...)

Любые пул-реквесты и идеи приветствуются!

==========================================================================================
REPO: LiberPrimus__Failed-Attempts
# Failed-Attempts
Documenting &amp; archiving failed attempts at decrypting the Liber Primus

==========================================================================================
REPO: LiberPrimus__primus.py
### Primus.py

A python script to help attempt to decrypt the Liber Primus.

This tool allows you to chain different ciphers in a given order on any page/segment/paragraph of the Liber Primus.
You can also do Gematria sums of the words, lines, sentences or full page/segment/paragraph.

Results are checked against an English dictionary so you can scan through the results much more quickly and reliably.
Optionally you can check for words that are close matches (eg: DIUINITY -> DIVINITY) using the `--closewords` argument

It uses Taiiwo's great [Cicada Python Library](https://github.com/Taiiwo/cicada)

**Installation:**
```bash
git clone https://github.com/LiberPrimus/primus.py.git primus
cd primus
git submodule update --init
# For matching close words (--closewords)
pip3 install python-Levenshtein

# Optionally, add primus.py to your path so you can use it anywhere
echo PATH=$PATH:$(pwd) >> ~/.bashrc && . ~/.bashrc
```

**Usage examples:**
```bash
# View help page
./primus.py --help

# Process all pages with Totient -> Atbash -> Shift by 13 -> Vigenere w/ key "PRIMUS" -> Reverse text
./primus.py --page all --ciphers [totient,atbash,shift:13,vigenere:primus,reverse]
# only unsolved pages (uall)
./primus.py -p uall -c [totient,atbash,shift:13,vigenere:primus,reverse]
# try it on segments instead of pages
./primus.py --segment all -c [totient,atbash,shift:13,vigenere:primus,reverse]
# shorthand version
./primus.py -p all -c [t,@,S:13,v:primus,R]

# Print the 1st of the solved pages ("A Warning") in Latin
./primus.py --page 0
# shorthand version
./primus.py -p 0

# Print the 1st of the solved pages ("A Warning") in Runic
./primus.py --page 0 --runic
# shorthand version
./primus.py -p 0 -r

# Print the 1st of the unsolved pages (0.jpg)
./primus.py --page 15
# prefix with 'u' to match only the unsolved pages
./primus.py --page u0

# Atbash the first solved page ("A Warning")
./primus.py --page 0 --atbash
# alternative
./primus.py -p 0 -c [atbash]
# shorthand version
./primus.py -p 0 -@

# Atbash followed by Shift of 3 on page 4
./primus.py --page 4 --ciphers [atbash, shift:3]
./primus.py -p 4 -c [@,S:3]

# Vigenere with key "FIRFUMFERENCE" on page 12
./primus.py --page 12 --vigenere FIRFUMFERENCE
# key can be in latin or runic, uppercase or lowercase
./primus.py --page 12 --vigenere ᚠᛁᚱᚠᚢᛗᚠᛖᚱᛖᚾᚠᛖ
# alternative
./primus.py --page 12 --ciphers [vigenere:firfumference]
# other alternative
./primus.py -p 12 -c [v:firfumference]
# shorthand version                   
./primus.py -p 12 -v firfumference               

# Totient running stream on page 56
./primus.py --
==========================================================================================
REPO: Locyyx64__liber-primus-analysis
# liber-primus-analysis
Analysing certain properties of the unsolved pages of Liber Primus (latest puzzle within Cicada 3301)

==========================================================================================
REPO: Locyyx64__lp-cribbs
# lp-cribbs
## Purpose

lp-cribbs is a Python-based cryptanalysis & cryptography tool designed to make attempts at deciphering the remaining parts of the Liber Primus, the latest mystery of the famous Cicada 3301 puzzle. On the cryptanalytical side, it is (not quite yet, but we'll get there) capable of running dozens of tests on both the solved and the unsolved sectionsof the book, in order to try narrowing down on the cryptographic functions that might have been used on the text. On the other hand, it can run many types of brute-force attacks on the given encrypted text, by means of cribbing and key derivation. It's still in its very early stages, and there are tons of things I still have to add.

## Installation

First and foremost, make sure that you have the Python3 interpreter installed and a virtual environment set up. Next, install the packages contained within the *requirements.txt* file using pip.

## Usage

If you want to get into decryption right away, you can do that through **main.py**. As for the cryptanalysis, everything can be found within the scripts of the analysis folder.

==========================================================================================
REPO: MuthuRanjanA__cicada3301
# cicada3301
==========================================================================================
REPO: N1-rt__lp-runes-translator
***OBS: This is a tool to decrypt runes from Cicada 3301 using the Gematria Primus table, 
the project is not complete and needs improvements, this is not a professional project, 
so don't expect much, the purpose of the project is just for my fun and training, 
I'm just a beginner.***

![Screenshot_20250425_201957](https://github.com/user-attachments/assets/0cbe83ff-ee13-4805-86cb-f4c13629a15e)

# Commands:

!clear - clear the screem.

!exit - close the shell.

!et - enter the runes text

!tr - translate the entered runes text

!invert - invert the translated text using atbash

!sr - shift the translated runes

# installing 
just clone the repository with **git clone**
and run **python3 shell.py**

==========================================================================================
REPO: NoxxGames__LiberPrimus-GPU
# liberprimus-gpu

[![CI](https://github.com/NoxxGames/LiberPrimus-GPU/actions/workflows/ci.yml/badge.svg)](https://github.com/NoxxGames/LiberPrimus-GPU/actions/workflows/ci.yml)

## Mission

`liberprimus-gpu` is a reproducible research workbench for conservative Liber Primus cryptanalysis experiments. The project keeps corpus provenance, solved baselines, transform metadata, run records, and CI gates ahead of any exploratory search or GPU acceleration work.

## Current boundaries and deferred work

Current completed stage: Stage 6H - Current-state integrity repair and dot-angle / right-triangle number-triangle source-lock addendum, without execution.

Current next prompt: Stage 6I - Final finite Stage 7 probe manifest and archive-run contract, without execution.

Stage 6H repairs Stage 6G current-state and doc-staleness misses, source-locks dot-angle/right-triangle/PDD153 review metadata, creates required Source Browser overlays, and hands explicit inputs to Stage 6I. Stage 6H created no final Stage 7 manifest, archive, probe execution, route stream, byte stream, target selection, image interpretation, or solve claim.

These are not permanent project exclusions. CUDA and broad campaigns are deferred, not permanently excluded.

### Permanent safety rules

No generated output is a solve by itself. No Liber Primus page is claimed solved unless a future reproducible manifest and matching output prove it. Any page still unsolved must not receive a solve claim.

### Current boundaries

- Canonical corpus: inactive.
- Page boundaries: reviewable.
- Broad unsolved-page search campaigns: not started.
- Scoring campaigns: not started; Stage 3A/3B minimal triage scoring exists only for sorting and inspecting bounded 841-candidate CPU runs, Stage 3C calibration uses small local controls only, Stage 3D applies that scorer to a four-key explicit Vigenere preview only, Stage 3F applies it to the bounded 48-candidate LP evidence-key Vigenere pack only, Stage 3G applies it to a bounded 256-candidate p56-local prime-minus-one offset sweep only, Stage 3H applies it to a bounded 64-candidate reset/advance ablation with 100 negative controls only, Stage 3I applies it to a bounded 56-candidate historical motif Vigenere pack only, Stage 3J applies it to a bounded 192-candidate Mersenne/perfect-number stream probe only, and Stage 3S applies it to the bounded 72-candidate Onion 7 explicit seed pack only.
- Cookie/hash preimage work: Stage 3L tests two explicit SHA-256 packs only.
- Visual/image-derived observations: registry and deterministic feature summaries only.
- CUDA expe
==========================================================================================
REPO: O4N4c__gematria-primus
(no top-level README)
files: .git Untitled.py
==========================================================================================
REPO: Pitchfork-and-Torch__instar
# INSTAR

A school for the cryptography [Cicada 3301](https://en.wikipedia.org/wiki/Cicada_3301) actually used.

Original seven-molt puzzle. Not affiliated. Not a recruiter. No identity collection.

Live: https://instar.jonbailey.xyz/

## What you practice

- View-source and hidden static files
- Atbash, then Vigenere (the 2012 emperor-key move, new plaintext)
- Book cipher against a local journal
- LSB steganography and a strings tail
- Audio spectrograms
- Classroom RSA (factor, invert, decrypt)
- Futhorc sound values (not Liber Primus gematria)
- A signed-statement / onion primer in the field manual
- Page 56 as a payload reading (ruled-out paths, no preimage search)

## Play

Open the live site. Begin at Hello. The first molt is not on the page you see.

Workbench (always open): `/workbench/`

v1.1 keeps the same hashed gates. The workbench is a living lab (live dual pane, frequency, bit-planes, STFT sliders, RSA steps). Depth marks molt without scores. Optional Guide names the next neighborhood, never the lock. Optional Skins shows shed depth as dots only, off by default, names stay unspoken. Optional Soil is a low tone, off by default. The school installs as a quiet PWA.

## Local

```
npx --yes serve public
```

Rebuild puzzle payloads (spoilers live in the encoder):

```
py -3 scripts/build_payloads.py
```

Page 56 lab (public hex, no preimage search):

```
python3 scripts/page56_lab.py
```

Field lesson: `/husk/`

Page cook guard (no spoilers, no decipherment):

```
python3 scripts/cook_guard.py
```

The guard fails if a cook is about to commit the secret manifest, a new onion host, a credential shape, or a Liber Primus solve claim. The published dead page-56 v2 host stays allowlisted as a teaching artifact. Do not add a live hidden service. Do not claim a Cicada break.

Shed check (public-safe school gate, no secret journal). Run before a chamber or lab PR. CI runs the same command:

```
python3 scripts/shed_check.py
```

The shed check runs the cook guard, the page 56 lab, the unit lab, Ensure-TweetCard, the PWA precache check, the Pages headers check, the search-listing check, the page-lab contract, the 404/redirects door check, the cook map, the PWA manifest check, the EN-only check, the canonical-host check, the llms.txt check, the seal/icon check, the cache-freshness check, and the hits-slug check, then confirms the browser and CLI labs still agree, required public files are present, no new magnet / IPFS / Freenet / I2P locator landed, public copy stayed ASCII, the hello tweet card and hits slug `instar` still hold, and README / AGENTS.md 
==========================================================================================
REPO: Pitchfork-and-Torch__liber-research
# Liber Primus research

This is a hypothesis lab, not a solve.

LP2 pages 0-55 are unsolved.

Not affiliated with Cicada 3301. Not a recruiter. This repo does not claim a new
plaintext for the unsolved book.

If you want a live school for the cryptography Cicada actually used, that is
INSTAR:

- https://github.com/Pitchfork-and-Torch/instar
- https://instar.jonbailey.xyz/

## Last status (2026-08-15 ET)

- LP1 00-16 solved (community).
- LP2 56 AN END and 57 PARABLE solved (community). Those English texts may be
  quoted here as already-public calibration. No extra plaintext is invented.
- LP2 0-55 unsolved (~12956 runes, IOC ~0.03448).
- Eight named families burned 2026-08-14 (all FAIL): outguess, book-index,
  running-key, periodic, columnar, word-unit, acrostic, homophonic.
- A same-day Playfair / two-square / four-square pass also FAIL.
- Public-web gauntlet scan 2026-08-15: NO_NEW_METHOD.
- No new public method since.

Known public solved pages (LP1 00-16, LP2 56 AN END, LP2 57 PARABLE) are named
only as community-known calibration. The published 512-bit AN END hash hex may
appear because it is already on the solved page. Derived hidden-service
encodings are not added.

## What this repo does not contain

- Liber Primus page images (no JPEG/PNG uploads).
- The full rune dump (cite scream314/rtkd and cicadasolvers.com instead).
- Onion / magnet / IPFS / Freenet / I2P / GNUnet locator lists.
- Attack scripts or large JSON dumps.
- A claimed break of LP2 0-55.

`notes/anend-tor2web-cdx-pass1.md` is a FAIL archive lookup of the published
hash. Live hidden-service locator encodings were stripped before publish.

Skipped on purpose (not copied here):

- instar-stego-pass1.md (belongs to INSTAR; already public).
- cicada-page56-locators.txt (locator encodings).
- liber-primus-rtkd.txt (full rune dump).
- attack .py scripts and large .json dumps.
- page JPEGs (lp2-0.jpg, lp2-1.jpg, lp2-15.jpg, and the rest).

## Notes

| File | What |
|---|---|
| [notes/burned-2026-08-14.md](notes/burned-2026-08-14.md) | Eight-family rollup. All FAIL. |
| [notes/uncracked-inventory.md](notes/uncracked-inventory.md) | Unsolved-page inventory. No new plaintext. |
| [notes/gauntlet-cycle1-scan.md](notes/gauntlet-cycle1-scan.md) | Public-web scan, 2026-08-15. NO_NEW_METHOD. |
| [notes/outguess-pass1.md](notes/outguess-pass1.md) | Passworded outguess pass 1. No real extract. |
| [notes/outguess-pass2.md](notes/outguess-pass2.md) | Passworded outguess pass 2. No real extract. |
| [notes/outguess-lp2-1.md](notes/outguess-lp2-1.md) | LP2 page 1 outguess receipt. Honest fail. |
| [
==========================================================================================
REPO: ProfessorJ17__Cicada3301
Direcitons:

A warning
Huh2
Ciphertext:

ᚱ-ᛝᚱᚪᛗᚹ.ᛄᛁᚻᛖᛁᛡᛁ-ᛗᚫᚣᚹ-ᛠᚪᚫᚾ-/
ᚣᛖᛈ-ᛄᚫᚫᛞ.ᛁᛉᛞᛁᛋᛇ-ᛝᛚᚱᛇ-ᚦᚫᛡ/
-ᛞᛗᚫᛝ-ᛇᚫ-ᛄᛁ-ᛇᚪᛡᛁ.ᛇᛁᛈᛇ-ᚣᛁ-ᛞ/
ᛗᚫᛝᚻᛁᚳᛟᛁ.ᛠᛖᛗᚳ-ᚦᚫᛡᚪ-ᛇᚪᛡᚣ.ᛁᛉ/
ᛋᛁᚪᛖᛁᛗᛞᛁ-ᚦᚫᛡᚪ-ᚳᚠᚣ.ᚳᚫ-ᛗᚫᛇ-ᛁᚳᛖᛇ-ᚫ/
ᚪ-ᛞᛚᚱᚹᛁ-ᚣᛖᛈ-ᛄᚫᚫᛞ.ᚫᚪ-ᚣᛁ-ᚾᛁᛈᛈᚱᛟᛁ-/
ᛞᚫᛗᛇᚱᛖᛗᛁᚳ-ᛝᛖᚣᛖᛗ.ᛁᛖᚣᛁᚪ-ᚣᛁ-ᛝᚫ/
ᚪᚳᛈ-ᚫᚪ-ᚣᛁᛖᚪ-ᛗᛡᚾᛄᛁᚪᛈ.ᛠᚫᚪ-ᚱᚻᚻ-ᛖ/
ᛈ-ᛈᚱᛞᚪᛁᚳ./
Method:

Atbash:
decimal[i] = 28 - decimal[i]
Plaintext:

A WARNNG
BELIEVE NOTHNG FROM THIS BOOC
EXCEPT WHAT YOV CNOW TO BE TRVE
TEST THE CNOWLEDGE
FIND YOVR TRVTH
EXPERIENCE YOVR DEATH
DO NOT EDIT OR CHANGE THIS BOOC
OR THE MESSAGE CONTAINED WITHIN
EITHER THE WORDS OR THEIR NVMBERS
FOR ALL IS SACRED
Welcome
LiberPrimuspage5
Ciphertext:

ᚢᛠᛝᛋᛇᚠᚳ.ᚱᛇᚢᚷᛈᛠᛠ-ᚠᚹᛉ/
ᛏᚳᛚᛠ-ᚣᛗ-ᛠᛇ-ᛏᚳᚾᚫ-ᛝᛗᛡ/
ᛡᛗᛗᚹ-ᚫᛈᛞᛝᛡᚱ-ᚩᛠ-ᛡᛗᛁ-ᚠᚠ-/
ᛖᚢᛝ-ᛇᚢᚫ.ᚣᛈ-ᚱᚫ-ᛁᛈᚫ-ᚳᚫ-ᚫᚾᚹ-ᛒᛉᛗᛞ/
-ᚱᛡᛁ-ᚠᛈᚳ-ᛇᛇᚫᚳ-ᚱᚦᛈ-ᚠᛄᛗᚩ-ᛇᚳᚹᛡ-ᛒᚫᚹ-/
ᛒᛠᛚᛋ-ᚱᚣ-ᛄᚫ-ᚱ-ᛗᚳᚦᛇᚫᛏᚳᛈᚹ-ᛗᚷᛇ.ᚳ/
ᛝᛈᚢ-ᛇᚳ-ᚱᛖᚹ-ᛡᛈᛁ-ᛒᚣᛒᛉ-ᚠᛚᛁᚱ-ᚱᛗ-ᚳᚷ/
ᛒ-ᚣᚱ-ᚳᚠᚢ-ᚦᛈᛡᛄᚹᛏᚠᛠ-ᛄᚷᛒ-ᚫᚦᚠᚠᛠ/
ᛈᚦ-ᛈᚠᚪᛉ-ᛄᛗᛖᛈᛝᛋᚩᛋᛗ-ᚹᛇᛄᛚ-ᚹᛉᚢᚦ/
ᚫᚹᛗᚦ-ᛞᚣᛄᚳ-ᛋᛡᛉᚩᛝᚱᛗᛒᚹ-ᚱᛗᛁ-ᛞᚣᛄ/
ᚳ-ᛉᚻᚢᚣᛈᛚ.ᛄᛝᚣᛗᚠᛄᛈᛇᚢᛡ-ᚹᛇᛄ-ᛞ/
ᚹᛉᚢ-ᚪᛚᚪᛋᛗᛡᛇᛉ-ᚫᛗ-ᛡᛗᛁ-ᛈᚣ-ᚫᛗᚢᚠ/
%
.ᛗᚣ-ᚣᛇ-ᚫᛉᚱᛄᛋᛖ-ᛖᚹᚾ-ᛞᛄᚢᛋᛉᚣᛏ/
ᛖᛏᛗ-ᛇᚱᚣ-ᛞᛋ-ᚾᛖᚫᛞᛡ-ᛈᛒᚢᚾᛠᛝᛄᛡ/
ᚫ-ᛄᚷᛒ-ᛈᚦᛉ-ᛈᚾᚹᚹᛁᛚᛗᚫ.ᛚᛈᛒᚢᚩᛠᛡ-ᚱ/
ᛡᛠᚠ-ᚱᚱᛇᛄᛗ-ᚱᛗᛁ-ᛞᚣᛄ-ᚻᛚᚠᚢ-ᛄᚢᛡᛚᚦ/
ᛠ-ᛇᛄᚩᛇᚱᚱᛗ.ᚢᛗᛋᚳ-ᛠᛇ-ᛚᛁᚫᚫᚳᛚ-ᚹᛁ-ᛚ/
ᛏ-ᛈᛖᚢᛈ-ᛠᛡᛈᚦᛏᛒ-ᛏᛗᛖ-ᚢᛚᚩᛚᛖ-ᛇᛄ/
ᛈ-ᚢᛠ-ᛚᚳᚷ-ᛠᚷᛋᛡᛏᛗ./
&
ᛒᛗᚱᚦᚠᛈ.ᚹᚱᛄ-ᚱᛉᚳ-ᛝ-ᛄᛠᛟ-ᛄᛖ/
ᚣᛗ-ᛞᚣᛄᚳᚫᛡᚢᚠ.ᛈᚠᚪ-ᚳᚳᛠ-ᚱ-/
ᚢᛄᚱ-ᚪᛗᛒᛈ-ᚷᛈᛒᚢᚾᛠᛝᚠ.ᚾᛉᛖ-/
ᚣᚷᛁᛠᛝᚢᛗᛏᚳᚷᛠᛠ-ᛄᚫ-ᛒᛈᚹᛞ.ᚠᚣ/
ᛉ-ᚫᚢᚠ-ᛇᛄᛈ-ᛉᛚᚦᛠᚪ-ᛚᚦ-ᚳᚣᚢᛡ./
ᚳᛖ-ᛚᚫᛇᛁᛉᚦᛋᚫᚻᚫ-ᚦᚣᚠᛚᚳᛖᚱ-ᛈᚠᚪᛉ-ᚱᛒᛖ-ᚫᚳᛒᚠ./
LiberPrimusPage6
Method:

Vigenere with key "DIVINITY" ("ᛞᛁᚢᛁᚾᛁᛏᚣ")

Skip indices 62, 102, 115, 181, 217, 218, 333, 566, 596, 625, 689
Plaintext:

WELCOME
WELCOME PILGRIM TO THE GREAT JOVRNEY TOWARD THE END OF ALL THNGS
IT IS NOT AN EASY TRIP BVT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE
ALONG THE WAY YOV WILL FIND AN END TO ALL STRVGGLE AND SVFFERNG YOVR INNOCENCE YOVR ILLVSIANS YOVR CERTAINTY AND YOVR REALITY
VLTIMATELY YOV WILL DISCOVER AN END TO SELF
IT IS THROVGH THIS PILGRIMAGE THAT WE SHAPE OVRSELVES AND OVR REALITIES
JOVRNEY DEEP WITHIN AND YOV WILL ARRIVE OVTSIDE
LICE THE INSTAR IT IS ONLY THROVGH GONG WITHIN THAT WE MAY EMERGE

WIDSOM
YOV ARE A BENG VNTO YOVRSELF
YOV ARE A LAW VNTO YOVRSELF
EACH INTELLIGENCE IS HOLY
FOR ALL THAT LIVES IS HOLY
AN INSTRVCTIAN COMMAND YOVR OWN SELF
Some wisdom
Onion 3 v3
Ciphertext:

ᛋᚩᛗᛖ-ᚹᛁᛋᛞᚩᛗ.ᚦᛖ-ᛈᚱᛁᛗᛖᛋ-ᚪᚱᛖ-ᛋᚪᚳ/
ᚱᛖᛞ.ᚦᛖ-ᛏᚩᛏᛁᛖᚾᛏ-ᚠᚢᚾᚳᛏᛡᚾ-ᛁᛋ-ᛋᚪ/
ᚳᚱᛖᛞ.ᚪᛚᛚ-ᚦᛝᛋ-ᛋᚻᚩᚢᛚᛞ-ᛒᛖ-ᛖᚾᚳᚱᚣ/
ᛈᛏᛖᛞ./
&
ᚳᚾᚩᚹ-ᚦᛁᛋ./
272		138		ᛋᚻᚪᛞᚩᚹᛋ		131		151./
ᚫᚦᛖᚱᛠᛚ		ᛒᚢᚠᚠᛖᚱᛋ		ᚢᚩᛁᛞ		ᚳᚪᚱᚾᚪᛚ		18./
226		ᚩᛒᛋᚳᚢᚱᚪ		ᚠᚩᚱᛗ		245		ᛗᚩᛒᛁᚢᛋ./
18		ᚪᚾᚪᛚᚩᚷ		ᚢᚩᛁᛞ		ᛗᚩᚢᚱᚾᚠᚢᛚ		ᚫᚦᛖᚱᛠᛚ./
151		131		ᚳᚪᛒᚪᛚ		138		272./
Method:

Direct translation
Plaintext:

SOME WISDOM
THE PRIMES ARE SACRED
THE TOTIENT FVNCTIAN IS SACRED
ALL THNGS SHOVLD BE ENCRYPTED

CNOW THIS
272		13
==========================================================================================
REPO: Protheme-777__Liber-Primus-decoder
Cicada 3301 — Liber Primus cryptanalysis tool built around the 
correct Gematria Primus system (mod 29, not 26).

DOWNLOAD EVERY FILE THATS CONNECTED

or

git clone https://github.com/Protheme-777/liber-primus-decoder.git
for the entire working build.

## What it does
- Auto-detects cipher type per page
- Vigenère, Beaufort, Autokey, Atbash, Caesar, Affine (all mod 29)
- F-interrupt (skip-index) logic as used by Cicada
- Totient stream decryption (method that solved page 56)
- Prime key streams: φ(p), Fibonacci, prime gaps, Euler
- GP sum validator — filters results by known target GP sum
- Crib dragging with LP-specific vocabulary
- Genetic algorithm + Hill-climbing + Simulated Annealing
  for substitution cipher solving
- Key length analysis (Friedman, IoC matrix, Kasiski)
- Prime word % check as correctness signal
- Built-in database of all 35 known LP pages with GP sums,
  solution methods, and verified keys
- Global pattern analysis (19949 is prime, 11252 = 29×388, etc.)

## Requirements
Python 3.6+, no external libraries needed.

## Usage
python liber_primus_decoder_v5.py --interactive
python liber_primus_decoder_v5.py --page "LP2, Page 56"

## Files
- liber_primus_decoder_v5.py  — main script
- quadgrams.json              — English quadgram scoring database  
- lp_bigrams.json             — LP-specific bigram database
- lp_trigrams.json            — LP-specific trigram database

goodluck and the best of all.

I'm reachable via discord pr0theme_

==========================================================================================
REPO: Skyro7777777__LiberPrimusDecoded
(no top-level README)
files: .env .git .github .gitignore .zscripts Caddyfile bun.lock cicada3301-research classcentral_defcon31.json components.json db download eslint.config.mjs examples mini-services next.config.ts package.json postcss.config.mjs primary_2014_p1.json primary_facts4.json prisma public search_github_recent.json search_reddit_2025.json src tailwind.config.ts tests tool-results tsconfig.json worklog.md
==========================================================================================
REPO: Taiiwo__TaiiwoBot
TaiiwoBot - v5
==========
Introduction - What is TaiiwoBot v5?
------------------------------------------------
This program is a chat bot framework that allows you to add custom plugins and customization options that runs quickly on a high memory system.
There are some plugins preinstalled that I developed.
You can use these as is, or as examples to build your own plugins.
It it built to run on any platform, but the currently supported plaforms are IRC and Discord.

![menu gif](https://thumbs.gfycat.com/FearlessTightGarpike-size_restricted.gif)

Refactor - Why is this different from IRCLinkBot?
-----------------------------------------------------------------
In this restructure, I decided to make the bot totally platform independant.
Theoretically, all of the plugins should work on any chat platform, as long as an appropriate
server wrapper is created.

On top of having drop in plugins like in the previous version, the plugins now have
a class structure for a more robust plugin coding experience, automatic help text,
and implementation of argument and subcommand parsing, allowing you to code normal pythonic
functions as opposed to parsing input data from the message string.

The server wrappers are implemented in a way that makes creating cross platform plugins
extremely high level and simple. Many interface features are implemented at the server wrapper
level, so you can create very advanced looking, experience-rich plugins with very little code.

How to run the bot:
-------------------
1. Install the dependecies in requirements.txt: `pip install -r requirements.txt`
2. Run the bot with `python discord_main.py` or replace `discord` with your platform of choice
3. If it's your first time running the bot, a `config.json` file will be created for you to edit. Add the required values for your chosen platform (including API Tokens), and repeat step 2

Once the bot successfully logs in, you can get started by typing `$help` anywhere the bot can read.

Developing Plugins
------------------
### The Plugin Code
Creating plugins is very simple. Open a new python file in the plugins directory.
Create a new class that inherits the Plugin base class. Make sure the class name
is the same as the file name, and type `$reload example` to load your plugin into
the running bot (The plugin will also automatically load when the bot is restarted).

Most basic plugin example:

```python
from taiiwobot import Plugin

class Example(Plugin):
    def __init__(self, bot):
        # this code runs when the plugin is loaded
```

### Interfacing with the platform
The code above wil
==========================================================================================
REPO: Taiiwo__cicada
# Taiiwo's Cicada Library
This library contains a selection of tools for performing high level operations on the LiberPrimus

# Example usage:

```python
from cicada import LiberPrimus
from cicada.gematria import Latin, Runes

# load the lp from file
lp = LiberPrimus()

shift = 0
# for pages 0 - 3 of the lp
for page in lp.pages[0:3]:
    # page is a Runes() object so we can do some cool things:
    # atbash substitution
    page.runes.atbash()
    # caesar shift
    page.runes.shift(shift)
    # use .text to get the contents of a Gematria() object such as Runes()
    # Note: it will also convert to str with str(Runes()) or equiv
    print("Runes: %s" % page.text)
    print("Plaintext: %s" % page.runes.to_latin())
    # example of automated shifting
    shift += 1

print(Runes("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ").to_latin())
# FUTHORKGWHNIJEOPXZTBEMLINGOEDAAEYIAEA
print(Latin("Hello World!").to_runes())
# ᚻᛖᛚᛚᚩ ᚹᚩᚱᛚᛞ!
print(Latin("How would cicada type question everything?").to_runes().to_latin())
# HOW WOULD CICADA TYPE CWESTION EUERYTHING?
```

# API

## LiberPrimus()
A class for accessing the contents of the Liber Primus

### Property: pages
Returns an array of LiberPrimus() objects containing each page

### Property: lines
Returns an array of LiberPrimus() objects containing each line

### Property: chapters
Returns an array of LiberPrimus() objects containing each chapter

### Property: segments
Returns an array of LiberPrimus() objects containing each segment

### Property: paragraphs
Returns an array of LiberPrimus() objects containing each paragraph

### Property: clauses
Returns an array of LiberPrimus() objects containing each clause

### Property: words
Returns an array of LiberPrimus() objects containing each word

### Property: runes
Returns a Runes() object of the contents

## Gematria()
A base class for translating and manipulating the runes

## Cipher()
A base class for manipulating text given an alphabet

### Method: sub(abc, cba)
Runs a substitution cipher where abc is the plain alphabet, and cba is the desired alphabet.

### Method: shift(n)
Runs a caesar shift on the contents. `alpha` determines if the shift should be on the runic alphabet or the
latin one

### Method: gematria_sum()
Returns the gematria sum of the contents

### Method: atbash()
Returns atbashed contents

### Method gematria_sum()
Returns integer sum of prime values

### Method gematria_sum_words()
returns list of integer sums of prime values for each word

### Method gematria_sum_lines()
returns list of integer sums of prime values for each line

### Method: to_runes()
Co
==========================================================================================
REPO: Taters79__LiberPrimus_CLI_Tool-Zig
# LiberPrimus_CLI_Tool-Zig
CLI program to assist in attempting to decipher the Liber Primus

==========================================================================================
REPO: Taters79__liber_primus
# liber_primus
 Learning Rust, writing a terminal application to assist in attempting to solve the Liber Primus

 ## 

==========================================================================================
REPO: Viusthas__Liber_Primus
(no top-level README)
files: .git .gitignore .idea src untitled.iml
==========================================================================================
REPO: VzGarnet__Liber-Primus
<p align="center"><a href="https://laravel.com" target="_blank"><img src="https://raw.githubusercontent.com/laravel/art/master/logo-lockup/5%20SVG/2%20CMYK/1%20Full%20Color/laravel-logolockup-cmyk-red.svg" width="400" alt="Laravel Logo"></a></p>

<p align="center">
<a href="https://github.com/laravel/framework/actions"><img src="https://github.com/laravel/framework/workflows/tests/badge.svg" alt="Build Status"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/dt/laravel/framework" alt="Total Downloads"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/v/laravel/framework" alt="Latest Stable Version"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/l/laravel/framework" alt="License"></a>
</p>

## About Laravel

Laravel is a web application framework with expressive, elegant syntax. We believe development must be an enjoyable and creative experience to be truly fulfilling. Laravel takes the pain out of development by easing common tasks used in many web projects, such as:

- [Simple, fast routing engine](https://laravel.com/docs/routing).
- [Powerful dependency injection container](https://laravel.com/docs/container).
- Multiple back-ends for [session](https://laravel.com/docs/session) and [cache](https://laravel.com/docs/cache) storage.
- Expressive, intuitive [database ORM](https://laravel.com/docs/eloquent).
- Database agnostic [schema migrations](https://laravel.com/docs/migrations).
- [Robust background job processing](https://laravel.com/docs/queues).
- [Real-time event broadcasting](https://laravel.com/docs/broadcasting).

Laravel is accessible, powerful, and provides tools required for large, robust applications.

## Learning Laravel

Laravel has the most extensive and thorough [documentation](https://laravel.com/docs) and video tutorial library of all modern web application frameworks, making it a breeze to get started with the framework.

You may also try the [Laravel Bootcamp](https://bootcamp.laravel.com), where you will be guided through building a modern Laravel application from scratch.

If you don't feel like reading, [Laracasts](https://laracasts.com) can help. Laracasts contains over 2000 video tutorials on a range of topics including Laravel, modern PHP, unit testing, and JavaScript. Boost your skills by digging into our comprehensive video library.

## Laravel Sponsors

We would like to extend our thanks to the following sponsors for funding Laravel development. If yo
==========================================================================================
REPO: Wra1th__Nebuchadnezzar
# Project "Nebuchadnezzar"

![William_Blake_-_Nebuchadnezzar_(Tate_Britain)](https://github.com/Wra1th/Nebuchadnezzar/assets/12640013/9c40de66-82d7-4b74-a2a2-5bda52d2db24)

## 3301 Cicada | Liber Primus | Solving Tool | GP_tool
# ![Screenshot 2023-09-16 162429](https://github.com/Wra1th/Nebuchadnezzar/assets/12640013/67c733b7-162e-486a-a331-1c3d169ffbde)

> [!NOTE]
> This program does **NOT** work with runes. Only letters and numbers. All string inputs are CSV format.

example:
```
input:
(2, 3, 5, 7, 11, ...)
(2,3,5,7,11,...)
(A, B, C, D, E, ...)
(A,B,C,D,E,...)
```
## Tutorial
Main Menu
1. Key Shift
2. Prime Values (needs revision)
3. Count Elements
4. String Cleaner
5. Rolling Key
6. Quit

### 1. Key Shift
+ First accepts a user input for a character string to be shifted. **MUST BE LETTERS** Then asks for user for shift sequence. **CAN BE LETTERS OR NUMBERS**. 

> [!Note]
> Length of string and shift sequence **MUST** be the same length.

<br>

example:<br>
```
Main Menu:
[1] Key Shift
[2] Prime Values
[3] Count Elements
[4] String Cleaner
[5] Rolling Key
[6] Quit

Enter the option number: 1
Enter a string to be shifted. (separated by commas): F, U, TH, O, R, C
Enter a shift sequence (characters or numbers, separated by commas): 2, 3, 5, 7, 1, 13
chars: ['f', 'u', 'th', 'o', 'r', 'c']
shift_seq: [2, 3, 5, 7, 1, 13]
results: TH, R, W, I, C, E
Return to menu? (y/n)

```
### 2. Prime Value
{to be revised}

### 3. Count Elements
+ Counts the elements  within the string provided by the user.

example:<br>
```
Main Menu:
[1] Key Shift
[2] Prime Values
[3] Count Elements
[4] String Cleaner
[5] Rolling Key
[6] Quit

Enter the option number: 3
Enter one or more characters to check (separated by commas): F, U, TH, O, R, C, A, B, C, D, E
There are 11 elements in the input.
Return to menu? (y/n)
```

### 4. String Cleaner
+ Takes commas and whitespace out of input string.

example:
```
Main Menu:
[1] Key Shift
[2] Prime Values
[3] Count Elements
[4] String Cleaner
[5] Rolling Key
[6] Quit

Enter the option number: 4
Enter a string: A, N, E, N, D, W, I, TH, I, N, TH, E, D, E, E, P, W, E, B, TH, E, R, E, E, X, I, S, T, S, A, P, A, G, E, TH, A, T, H, A, S, H, E, S, T, O, I, T, I, S, TH, E, D, U, T, Y, O, F, E, U, E, R, Y, P, I, L, G, R, I, M, T, O, S, E, E, C, O, U, T, TH, I, S, P, A, G, E
Cleaned String: ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTOITISTHEDUTYOFEUERYPILGRIMTOSEECOUTTHISPAGE
Return to menu? (y/n)
```

to be continued...

==========================================================================================
REPO: _iddqd_tmp
(no top-level README)
files: .git .gitattributes 2012 2013 2014 2016 byte-strings liber-primus__images--full liber-primus__images--unsolved liber-primus__index liber-primus__keys liber-primus__transcription--master liber-primus__transcription--sentences liber-primus__translation lp_outguessed ttf
==========================================================================================
REPO: aadishgoel__Cicada-3301
# Cicada-3301
In Attempt to solve Cicada 3301 Puzzle by myself 

## Start From Start.jpg
![](Start.jpg)

### Content Hidden in the image can be seen by opening image in any editor or in notepad.
> CLAVDIVS CAESAR says "lxxt>33m2mqkyv2gsq3q=w]O2ntk"

This is encrypted by CAESAR CIPHER   (Key 4 as Claudius was the 4th emperor).

So decrypt it by running ` clavdivs_caesar.py ` 
```python
for i in "lxxt>33m2mqkyv2gsq3q=w]O2ntk": print(chr(ord(i)-4),end="")
```
### You will get
> http://i.imgur.com/m9sYK.jpg

![](http://i.imgur.com/m9sYK.jpg)

This image is decoy. You have to use outguess on `Start.jpg`

``` outguess -r Start.jpg Start.txt ```

### Now you get ` Start.txt `
>In which you have
http://www.reddit.com/r/a2e7j6ic78h0j/
and Book codes

#### There You find only 2 posts having images
* Problems: http://i.imgur.com/8D7hN.jpg
![](Problems.jpg)
##### Outguess it You will get ` Problems.txt `
``` outguess -r Problems.jpg Problems.txt ```

* Welcome: http://i.imgur.com/KXLOP.jpg
![](Welcome.jpg)
##### Outguess it You will get ` Welcome.txt `
``` outguess -r Welcome.jpg Welcome.txt ```

==========================================================================================
REPO: ale64bit__cicada3301
# Intro

This is a harness I built for myself for experimenting with the cicada puzzles. 
It's written in Golang. See [here](https://golang.org/doc/install) how to install it.
It has no external dependencies and should run in all supported runtimes (Windows, Mac, Linux, etc.).

# How to use it

There are two main binaries:

## done

The `done` binary shows the already decoded sections along with the information related to the decoder. This is useful to verify the already-solved pages and to try tweaks to existing decoders.

Example output for running the command `go run bin/done/main.go` under Linux:

![Alt text](/doc/done.png?raw=true "Done")

Additionally, you can restrict which sections to decode by passing a space-separated list of section IDs (see [data/data.go](/data/data.go)) as arguments to the binary.

## search
The `search` binary builds a set of decoders of various types and tries to decode the unsolved sections. The result is evaluated according to a dictionary search and scored accordingly.

Example output for running the command `go run bin/search/main.go` under Linux:

![Alt text](/doc/search.png?raw=true "Search")

Additionally, you can pass the following flags:
* `-prefix_len`: specify the length of the prefix to try to decode from each unsolved section. Longer prefixes result in slower searches.
* `-selected_sections`: a comma-separated list of the unsolved sections to try to decode. If unspecified, all unsolved sections are tried.
* `-match_score`: the minimum score that is considered a match (i.e. successfully decoded). Scores range from 0 to 1.

==========================================================================================
REPO: bobby-bobby-bobby-bobby__Libre-Primus-Cicada-3301-Solver-Demo
# Liber Primus Cicada 3301 Solver Demo

Production-oriented, auto-bootstrapping cryptanalysis framework for large-scale search over unsolved Liber Primus pages.

> This repository builds the search engine and distributed infrastructure. It does **not** claim to solve the cipher.

## Features

- Auto-bootstrap data source clone (`run_all.py`)
- Rune + page models and Gematria Primus conversion
- Tensorized numeric representation for accelerated kernels
- Composable transform pipelines:
  - `ModularShift`
  - `VigenereShift`
  - `AtbashVariant`
  - `BlockTransposition`
  - `IndexPermutation`
  - `UnknownTransformSlot` (learnable substitution/evolution slot)
- Hardware auto-detection:
  - CUDA via PyTorch
  - Apple MPS via PyTorch
  - CPU fallback (NumPy)
- Distributed multiprocessing coordinator/worker architecture
- Search strategies:
  - random
  - grid
  - beam (with adaptive evolution step)
  - genetic mutation/crossover
- Search-space narrowing constraints from `config.json`
- Multi-layer scoring:
  - statistical (entropy, IOC, n-gram)
  - structural (symmetry, repetition)
  - cross-page consistency
  - lexical coherence proxy
- Checkpoints + experiment logs

## Quick Start

```bash
python run_all.py
```

This command will:
1. Create `config.json` if missing
2. Clone the configured LP data repository
3. Parse rune pages
4. Build tensors
5. Start distributed workers
6. Run search loop and save candidates to `experiments/best_candidates.json`

## Config

Edit `config.json` to control:
- worker count
- strategy
- batch sizes
- max iterations
- search constraints

## Optional Dependencies

- `torch` (recommended for CUDA/MPS acceleration)
- `numpy`

Install:

```bash
pip install torch numpy
```

## Run with Custom Config

```bash
python run_all.py --config /absolute/path/to/config.json
```

## Output

- `experiments/logs/run.log`
- `experiments/checkpoints/iter_*.json`
- `experiments/best_candidates.json`

==========================================================================================
REPO: chipper1999__Liber-Primus-Solver
# Liber Primus Page 17 Solver
Successfully decrypted Page 17 using a Prime-Shift Vigenere cipher and the F-Skip rule.
==========================================================================================
REPO: chipper1999__liber-primus-solutions
(no top-level README)
files: .git solution.py solution_signed.py
==========================================================================================
REPO: cicada-solvers__3301_assist
(no top-level README)
files: .git LP LP_text.py english_text english_text.py helper_functions.py main.py new_quadgrams.txt plot_functions.py readeasiertranscript2.csv statistics.py
==========================================================================================
REPO: cicada-solvers__Cicada-DWH-HashcatAttempts
# Cicada-DWH-HashcatAttempts 

To run tests yourself, clone this repository into your hashcat directory (so that 
Cicada-DWH-HashcatAttempts is its own subdirectory).

Then copy the allbytes.hcchr into your hashcat directory

Delete the contents of the `results` folder, but not the folder itself.

Run `python3 run_checks.py` to generate all of the results.
If you know the name of a specific check and hash you want to generate, the full command options are:
`python3 run_checks.py [checkname [hashname]]`  (eg: `python3 run_checks.py allbytes streebog`)

Tests and supported hashes can be changed from the `presets.py` file.

These tests were performed on Windows, however it *should* work with linux as well.

==========================================================================================
REPO: cicada-solvers__GPPrimeView
# GPPrimeView 

==========================================================================================
REPO: cicada-solvers__GematriaPrimusTool
# GematriaPrimusTool
A translator tool based off of JXlate for use with the Cicada 3301 Gematria Primus table.

==========================================================================================
REPO: cicada-solvers__LPDecrypter
# LPDecrypter

A Python framework to work with the Liber Primus decryption.

## Usage
There are examples in `examples`, but indeed more documentation is needed.

## Contributing
Obviously all contributions are welcome, here are some guidelines:
- if you implement some cipher to test it on LiberPrimus you may as well add it to this repository via a pull request. Name the class like `YourNickname_SomeNameThatDescribesTheCipherCipher` like if i implemented some modified Vigenere cipher that uses the mobius function i would name it `Ekardnam_MobiusVigenereCipher`, put its code in `lpdecrypter/ciphers/yournickname_ciphers.py` and export it in `lpdecrypter/ciphers/__init__.py`.
- as above if you implemented some alphabets follow the same convention. An example would be `Ekardnam_GematriaPrimus`, and put in `lpdecrypter/alphabets/yournickname_alphabets.py` and export it in `lpdecrypter/alphabets/__init__.py`.
- to avoid having to many files try to put all your alphabets and cipher implementation in one file for each category named as described above, but if you really implement a lot of stuff split it in multiple files with your nick name prepended.
- the above rules aren't valid if you implement some kind of famous cipher, alphabet or analyzer. If i implemented the railfence cipher I would name it `RailfenceCipher` and put it in a file named `railfence_cipher.py` in the corresponding folder. In fact the prepositions of nicknames has the purpose to avoid complex identifiers for very specific ciphers and to give some kind of namespacing to the ciphers, which isn't needed for ciphers (or anything else) that have a globally understood name (and would actually make the class names look bad)

Check the [issues](https://github.com/ekardnam/LPDecrypter/issues) or the [not yet implemented features](https://github.com/ekardnam/LPDecrypter/search?q=%23+NOT+YET+IMPLEMENTED).

==========================================================================================
REPO: cicada-solvers__LiberPrTools
(no top-level README)
files: .git GPVigenere_Decipher_v1Release.cpp GPVigenere_Decipher_v1Release.exe GPVigenere_DeciphererV1.1.cpp
==========================================================================================
REPO: cicada-solvers__LiberPrayground
(no top-level README)
files: .git
==========================================================================================
REPO: cicada-solvers__Red_Rune_Cribs
# Red_Rune_Cribs
cribs for red runes

==========================================================================================
REPO: cicada-solvers__WPCH-3301
# WPCH-3301
Hash Web page content using SHA512 

This is a tool used for the Cicada-3301 Hash.
You're welcome to reuse the code but don't use it for ilegal things.

==========================================================================================
REPO: cicada-solvers__aldegonde
`aldegonde` is a Python library for classical cryptography. It is
written to accomodate non-standard alphabets (i.e. not just A-Z).

==========================================================================================
REPO: cicada-solvers__cicada-library
# Taiiwo's Cicada Library
This library contains a selection of tools for performing high level operations on the LiberPrimus

# Example usage:

```python
from cicada import LiberPrimus
from cicada.gematria import Latin, Runes

# load the lp from file
lp = LiberPrimus()

shift = 0
# for pages 0 - 3 of the lp
for page in lp.pages[0:3]:
    # page is a Runes() object so we can do some cool things:
    # atbash substitution
    page.atbash()
    # caesar shift
    page.shift(shift)
    # use .text to get the contents of a Gematria() object such as Runes()
    # Note: it will also convert to str with str(Runes()) or equiv
    print("Runes: %s" % page.text)
    print("Plaintext: %s" % page.to_latin())
    # example of automated shifting
    shift += 1

print(Runes("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ").to_latin())
# FUTHORKGWHNIJEOPXZTBEMLINGOEDAAEYIAEA
print(Latin("Hello World!").to_runes())
# ᚻᛖᛚᛚᚩ ᚹᚩᚱᛚᛞ!
print(Latin("How would cicada type question everything?").to_runes().to_latin())
# HOW WOULD CICADA TYPE CWESTION EUERYTHING?
```

# API

## LiberPrimus()
A class for accessing the contents of the Liber Primus

### Property: pages
Returns an array of LiberPrimus() objects containing each page

### Property: lines
Returns an array of LiberPrimus() objects containing each line

### Property: chapters
Returns an array of LiberPrimus() objects containing each chapter

### Property: segments
Returns an array of LiberPrimus() objects containing each segment

### Property: paragraphs
Returns an array of LiberPrimus() objects containing each paragraph

### Property: clauses
Returns an array of LiberPrimus() objects containing each clause

### Property: words
Returns an array of LiberPrimus() objects containing each word

### Property: runes
Returns a Runes() object of the contents

## Gematria()
A base class for translating and manipulating the runes

## Cipher()
A base class for manipulating text given an alphabet

### Method: sub(abc, cba)
Runs a substitution cipher where abc is the plain alphabet, and cba is the desired alphabet.

### Method: shift(n)
Runs a caesar shift on the contents. `alpha` determines if the shift should be on the runic alphabet or the
latin one

### Method: gematria_sum()
Returns the gematria sum of the contents

### Method: atbash()
Returns atbashed contents

### Method gematria_sum()
Returns integer sum of prime values

### Method gematria_sum_words()
returns list of integer sums of prime values for each word

### Method gematria_sum_lines()
returns list of integer sums of prime values for each line

### Method: to_runes()
Converts text conten
==========================================================================================
REPO: cicada-solvers__cicada-runes-2014-transcriber
(no top-level README)
files: .git
==========================================================================================
REPO: cicada-solvers__csrkd
(no top-level README)
files: .git
==========================================================================================
REPO: cicada-solvers__deep-web-hash-as-ed25519
# Failed attempt : Interpret the deep web hash as a ed25519 secret to find its associated v3 onion address

Based on https://github.com/cathugger/mkp224o/

## Modified files
* `main.c` : force arguments
* `worker_slow.inc.h` : changes made to print the resulting onion address, and to prevent additional onions from being generated
* `ed25519/ed25519.h` : function 'ed25519_seckey_expand'. Originally, this function took a random seed and created an ed25519 secret using a 512 bits hashing algorithm. Then, it altered the secret slightly.

All changes are commented.

## Tests available
To select a test, use the associated compile-time define.
Tests :
* Custom hash : use `-DCUSTOM_HASH="DEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF"`
* Don't alter hash : use `-DDONT_ALTER_HASH`
* Use reverse hash endianness : use `-DREVERSE_ENDIANNESS`

> All onion addresses generated by this method are not reachable

## Compile and generate onion address
```
./autogen.sh
./configure CFLAGS='-DTESTS_DEFINES_HERE -DANOTHER_TEST_DEFINE=42'
make
./mkp224o
```

==========================================================================================
REPO: cicada-solvers__idkfa-web
#### Liber Primus Translator ####
___

A toolset for working with 3301's Liber Primus.

#### Quick start ####
___

Clone and run the repository to translate the first segment of Liber Primus.

```bash
$ git clone https://github.com/rtkd/idkfa .
$ npm install
$ chmod u+x idkfa
$ ./idkfa -s 0.0 -v l -i l
```

#### Available Commands ####
___

##### -c, --charAt #####

Returns latin character(s) at position(s) n.

```bash
-c 0 1 2 3
```

##### -f, --find #####

Finds crib candidates and returns source, source path and key

```bash
-f the circumference
```

##### -i, --invert #####

Inverts/Reverses source, gematria and key properties

```bash
-i f
```

  * **f** — Invert gematria column: futhark
  * **k** — Invert key
  * **l** — Invert gematria column: latin
  * **o** — Invert gematria column: offset
  * **p** — Invert gematria column: prime
  * **s** — Reverse shift
  * **t** — Reverse source text

##### -k, --key #####

Generates and applies key(s) for decryption.
Keys can be denoted as `integer`, `integer csv`, `latin`, `futhark` or `mathematical expression`. Multiple keys are seperated by a space.

For details on using mathematical expressions see: [MathJS Functions](http://mathjs.org/docs/reference/functions.html)

**Expressions must be enclosed in single quotation marks.**

Generator functions `int()`, `odd()`, `even()`, `prime()`, `fib()` will accept 0, 1 or 2 parameters of type `integer`
.
  
  * 0 parameters will generate as many consecutive numbers as the selected source has graphs.
  * 1 parameter will generate first n consecutive numbers, and repeat as source has graphs.
  * 2 parameters will generate consecutive numbers from n to n, and repeat as source has graphs.

If first parameter is larger than second, order of numbers will be reversed.

Available transformations: Euler Phi `ephi()`, Möbius: `mob()`

##### Examples #####

Generate key: 1,1,1,1..
```bash
-k 1
```

Generate key: 1,2,3,1,2,3..
```bash
-k 1,2,3
```

Generate key: 23,10,1,10,9,10,16,26,23,10,1,10,9,10,16,26..
```bash
-k divinity
```

Generate key: 0,3,3,17,24,4,0,3,3,17,24,4..
```bash
-k ᚠᚩᚩᛒᚪᚱ
```

Generate key: 1,2,4,6,10,12,16,18,22,28,30,36..
```bash
-k '$(ephi(x), x, prime())'
```

Generate key: 29,23,19,17,13,11,7,5,29,23,19,17,13,11,7,5..
```bash
-k '$(x, x, prime(10, 2))'
```
Generate keys: 1,2,3,1,2,3.. **and** 23,10,1,10,9,10,16,26,23,10,1,10,9,10,16,26..
```bash
-k 1,2,3 divinity
```

##### -p, --patch #####

  *	**d** — Patch the dictionary to match expected output ((I)NG, I(A/O)..)
  *	**s** — Patch chars at specific positions within source. (See config.js)

```ba
==========================================================================================
REPO: cicada-solvers__liber_primus_finds
(no top-level README)
files: .git .github .gitignore global_cribs
==========================================================================================
REPO: cicada-solvers__libergo
# LiberGo
This is a Liber Primus Analysis Toolkit. I have been using it for investigating the Liber Primus. It is **very early** in its development and I am working on it as I have the time to do it. I have also used it on some other puzzles so its application is not limited to the Liber Primus.

## Program Information

LiberGo includes many command-line utilities for cryptographic analysis, text processing, and mathematical operations:

### Text Processing Tools
- **rdtext**: Processes Excel files to generate sentence permutations and checks if their gemmatria sums are prime numbers. Can process in normal or reverse word order.
- **rdcheck**: Validates and checks text data against various criteria.
- **detangle**: Untangles encoded or interleaved text.
- **rencode**: Encodes text using various methods.
- **winchafftext**: Processes text using chaff techniques.
- **railit**: Applies rail fence cipher to text.
- **corpuslist**: Analyzes text corpora.
- **wordlecheat**: Helper for Wordle puzzles.
- **calrunestats**: Calculates statistics for runes/characters.
- **runedonkey**: Performs operations on rune-encoded text.

### Mathematical Tools
- **gemsum**: Calculates gemmatria sums for text.
- **gemproduct**: Calculates gemmatria products.
- **isprime**: Checks if a number is prime.
- **primedb**: Database operations for prime numbers.
- **factorize**: Factorizes numbers into prime factors.
- **intgen**: Generates integers based on specified patterns.
- **genseq**: Generates numerical sequences.
- **invgoldbach**: Inventory Goldbach operations.
- **mob**: Mobius operations tool.
- **fanalysis**: Factorization verification tool.

### Conversion Tools
- **base60**: Converts to/from base 60.
- **binfile**: Binary file operations.
- **binstring**: Binary string operations.
- **binvert**: Binary inversion operations.
- **byte2bin**: Converts bytes to binary.
- **byte2binstring**: Converts bytes to binary strings.
- **byte2int**: Converts bytes to integers.
- **hex2bytearray**: Converts hex to byte arrays.
- **hex2int**: Converts hex to integers.
- **decode64**: Base64 decoder.

### Network & Specialized Tools
- **ipaddressgen**: Generates IP addresses.
- **primeaddressgen**: Generates addresses based on prime numbers.
- **checkhashes**: Validates hashes.
- **checkmultihash**: Validates multiple hashes.
- **cipherval**: Calculates cipher values.
- **permute**: Generates permutations.
- **libergo**: Main application that provides a framework for other tools.

## Building release binaries
You will need to have go installed on your system. You can get it from https:
==========================================================================================
REPO: cicada-solvers__lp-decrypter
## UPDATE
* being re-written in c++ too big and compicated for my python skills :)
* looking to better integrate with c++ cribbing, so crib app first 
* for latest data see https://github.com/mortlach/google_ngrams_Version-20200217

## Table of contents
* [General info](#general-info)
* [Hints](#hints)
* [Future](#future)
* [Issues](#issues)
* [Packages](#packages)
* [Setup](#setup)
* [help-me](#help-me)

## General info
- An LP brute-forcing tool for decrypting cipher-text with user defined keys and functions 
of two runes:   
`Function(plaintext_rune,key_rune) = cipher_rune`     
including automated Gematria rotations, interrupters, key-dragging and plaintext ranking.    
- Very much in early access.
- Much more information, benchmarking, features and manual to follow.   
- Good Luck    

## Hints
- In principle, **anything this app can encrypt it should be able to decrypt** 
(with the right settings and bugfixes).   
- Try setting up test decryptions using your own encryption functions, plaintext, key and encoding and see if they are 
successfully decrypted. 
- If test decryption fails, perhaps settings in the "options" tab are wrong?   
- The app can be used for LP decrypting as is, however, it is still under development.  

## Future
Planned features not yet implemented:
* Load save general set-up 
* Batch-mode support for use without GUI. Once the app is well benchmarked by the community long scans with large key 
lists (etc.) would probably be better run without the gui. This can be accomplished now, but there are no examples and
the expectation is that data-structures etc. will change during this initial-release phase.   
* Moar encryption methods. Hopefully, this will provide a framework in which a wider variety of encryption methods can be
implemented and shared between solvers. 

## Issues
- Be aware: i'm an entirely self-taught coder, this is done out of love not competence :)
- There are bugs, errors and hopefully suggestions. Please share them through the github issues, and irc / discord.  
- Particularly welcome are bugs, code improvements, speed-up suggestions and expanding (or re-writing) the mutl-theading framework 

## packages
1. created with:  
[Python 3.6](https://www.python.org)    
[tabulate](https://pypi.org/project/tabulate/)     
[pyqt5](https://pypi.org/project/PyQt5/)     

	
## setup
1. install python3     
2. you may need to install  
`pip3 install pyqt5`  
`pip3 install tabulate`  
2. To run:  
`python3 main.py  `    
run the text decryption with defaults on start-up 
`python3 main.py -test  `    

## help-me
cicadsolvers 
==========================================================================================
REPO: cicada-solvers__lphelper
## Installation
```pip install -i https://test.pypi.org/simple/ lphelper==0.7```
## Examples
***see examples folder in this repository***

==========================================================================================
REPO: cicada-solvers__miteo-3301tools
(no top-level README)
files: .git .github emirp_prime_generator.py pagedots_nullcipher.py quadratic_prime_generator.py spiral_message_base60plus15.py spiral_message_split.py
==========================================================================================
REPO: cicada-solvers__monokuma-ConvolutionKernels
# convolutionKernel.py

Applies a convolution kernel to an image

## Arguments/usage

### Box blur

`python3 convolutionKernel.py <filename> box-blur <kernel size>`

### Normalized box-blur

`python3 convolutionKernel.py <filename> normalized-box-blur <kernel size>`

### Gaussian blur

`python3 convolutionKernel.py <filename> gaussian-blur <kernel size> <sigma>`

### Custom

`python3 convolutionKernel.py <filename> <kernel entries in right-to-left, top-to-bottom order>`

## Keybinds

**X**: Close window

**S**: Save convoluted image

## Progress

### 32.jpg

* Doesn't seem to be a box-blur; seems to be a Gaussian blur unless there's some weird custom kernel. Closest match I can get by guessing prime numbers is a 17x17 Gaussian-blur kernel with σ = 5 on a 183x191 nearest-neighbor downsize of the original image (apparent dimensions counted on the 32.jpg image by hand), but it's not an exact match.
* Downsizing before applying the kernel is for sure the way to go, because otherwise it gets really messed up.

### 55.jpg

* For sure a convolution kernel meant to get outlines. Can't find an exact match.
* Colors seem to be inverted for some reason, which I don't believe convolution kernels can do on their own. Maybe this is a part of the step if we were to apply this to other forms of data.
* The border is grey; I've seen convolution kernels do this when I was testing with custom ones, but I'm not sure which one is the right one because the colors are inverted as per the previous point. Should make a program to invert the colors (subtract the greyscale and/or individual RGB values from 255) and then use that to help compare.

## To-do

1. Create a program to score image similarities by just summing the diferences between each pixel in the two images.
2. Create program to turn the scaled-up image of the scaled-down image of the trees on 32.jpg and 55.jpg (i.e. the images are made of pixels that were sized up to be ~5x5 blocks of pixels) into an image that's just the original scaled-down image by identifying the pixels based on the greyscale values being similar to a certain threshold in a square region and then averaging their values to find the most probable pixel color. Basically just clean up the tree image so we can pretty much get what image Cicada created as a result of the convolution kernel they applied. This does not account for JPEG compression.
3. Create a program to deconvolute a given image with a given kernel using linear algebra.
4. Create a program to generate the 8 different possible results of JPEG compressing an image with the given settings 
==========================================================================================
REPO: cicada-solvers__neuroretransmit-cicada
(no top-level README)
files: .git
==========================================================================================
REPO: cicada-solvers__optimisticninja_cicada3301
(no top-level README)
files: .git
==========================================================================================
REPO: cicada-solvers__project-runeberg
(no top-level README)
files: .git
==========================================================================================
REPO: crackalamoo__futhorc
# ᚠᚢᚦᚩᚱᚳ: ᚫᛝᛚᚩ-ᛋᚫᛉᚢᚾ᛫ᚱᚣᚾᛁᚳ᛫ᚳᛁᛁᛒᚩᚱᛞ
## Futhorc: Anglo-Saxon runic keyboard

A keyboard adapting Anglo-Saxon runes to write modern English, particularly American English. Hosted at [harysdalvi.com/futhorc](http://harysdalvi.com/futhorc).


==========================================================================================
REPO: ctvrty-rozmer__bruh
(no top-level README)
files: .git cicada-master lp-full-english perl-rsa-decrypt.pl song.mid
==========================================================================================
REPO: dude123124144__Liber-Primus-Runes-OCR
(no top-level README)
files: .git letters misc_scripts rune_translate.py
==========================================================================================
REPO: geomatria__CicaData
# CicaData

Files:
CicaData.json - A catalogue of Cicada 3301 files, their attributes and relationships, using JSON.

Folders:
assets/ - repository of files, each asset has a folder corresponding to its "id".
templates/ - contains JSON templates for predefining attributes for common and specific file types.

==========================================================================================
REPO: greenie-neuko__arg-skills
# ARG Skills for Claude

Skills for designing Alternate Reality Games (ARGs) with Claude.

## Installation

```bash
npx skills add https://github.com/greenie-neuko/arg-skills --skill arg-designer
```

## Available Skills

### arg-designer

Comprehensive ARG design toolkit for creating immersive puzzle experiences.

**Ciphers & Encoding (30+):**
- Beginner: Caesar, ROT13, Atbash, Reverse, A1Z26
- Intermediate: Vigenère, Rail Fence, Morse, Base64, Polybius, Pigpen
- Advanced: Playfair, Nihilist, Book Cipher, Baconian, Columnar Transposition
- Expert: XOR, Homophonic, Gematria Primus, Multi-layer custom systems

**Hiding Methods (60+):**
- Text: Unicode steganography, EXIF metadata, HTML comments, null bytes
- Image: LSB steganography, layer hiding, QR codes, brightness tricks
- Audio: Spectrograms, reversed audio, DTMF tones, phase cancellation
- Video: Frame insertion, subtitle tracks, timecode data
- File: Nested archives, polyglot files, alternate data streams

**Trailheads (40+):**
- Digital: Hidden pages, source code, 404 customization, robots.txt
- Physical: QR codes, geocaches, USB dead drops, event handouts
- Social: Character accounts, forum posts, "wrong number" contacts

**Design Theory:**
- TINAG (This Is Not A Game) philosophy
- Crimes Against Mimesis avoidance
- Puppetmaster role and real-time adaptation
- Player types (Organizers, Hunters, Detectives, Hackers, Collaborators)
- Difficulty curves (linear, wave, plateau)
- Hint systems and fatigue prevention
- Meta-puzzle structures and gating mechanics

**Case Studies:**
- I Love Bees (Halo 2 ARG)
- Cicada 3301
- Year Zero (Nine Inch Nails)
- The Beast
- Marble Hornets

**Included Scripts:**
- `cipher_tools.py` - Encode/decode 9 cipher types
- `steganography.py` - LSB image hiding, metadata, Unicode zero-width
- `spectrogram.py` - Convert images/text to audio spectrograms

**Recommended Tools:**
- dCode.fr, CyberChef, Boxentriq
- Binwalk, zsteg, Steghide, ExifTool
- Sonic Visualizer, Audacity

## Reference Files

| File | Content |
|------|---------|
| `ciphers.md` | 30+ ciphers with implementations |
| `hiding-methods.md` | 60+ techniques by content type |
| `trailheads.md` | 40+ entry point patterns |
| `connectors.md` | Puzzle linking methods |
| `platforms.md` | Discord, Twilio, YouTube setup |
| `design-principles.md` | TINAG, pacing, player types |
| `meta-puzzles.md` | Meta structures, gating, puzzle hunts |
| `recipes.md` | Complete chains from famous ARGs |

## Usage

Once installed, the skill triggers when you ask Claude about:
- Designing ARGs or puzzle trails
- Hiding messages with
==========================================================================================
REPO: harry-sar__3301-gematria-primus-solver
**Cicada 3301 Liber Primus inscription decoder tool**

==========================================================================================
REPO: henkman__liberprimus
(no top-level README)
files: .git
==========================================================================================
REPO: hugvig__liber-primus-research
(no top-level README)
files: .git ciphers pages tools
==========================================================================================
REPO: jens-wedin__liber-primus
# Liber Primus toolkit

Cryptanalysis tooling for the unsolved sections of Cicada 3301's *Liber
Primus*, working from the rune transcription in
[scream314/cicada3301](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)
(vendored at `data/liber_primus.md`).

Findings so far are in [REPORT.md](REPORT.md).

## Layout

| File | Purpose |
| --- | --- |
| `gematria.py` | The Gematria Primus table (29 runes ↔ letters ↔ primes) and transliteration both ways, including digraph handling (TH, ING, EA, …). |
| `parse_lp.py` | Parses the markdown into segments (section, key annotation, rune text). Run directly for an inventory. |
| `ciphers.py` | Cipher ops in rune-index space mod 29: shifts, atbash (reversed gematria), Vigenère, prime/totient keystreams — encrypt and decrypt, with Cicada's literal-ᚠ rule. |
| `validate_solved.py` | Reproduces every known solved page. Keyed pages are verified by *forward-encrypting* the known plaintext and comparing rune-for-rune. |
| `analyze_unsolved.py` | Statistics (IoC, periodic IoC, doublet rate) plus a battery of simple attacks over all unsolved segments. |
| `attack_autokey.py` | Brute force of plaintext- and ciphertext-autokey with short primers. |
| `crib_drag.py` | Word-aligned crib-dragging with the literal-ᚠ filter; tests implied keystreams for structure. `--selftest` recovers known keys. |
| `doublet_sim.py` | Simulates cipher families and measures which reproduce the observed (IoC 1.000, doublet 0.66%) signature. |
| `no_repeat_model.py` | Models the no-adjacent-repeat mechanism (re-roll vs key-skip) and quantifies the keystream desync. |
| `attack_keyskip.py` | Beam-search attack on the key-skip hypothesis over prime/totient streams. `--selftest` proves 98% recovery when the hypothesis holds. |
| `attack_runningkey.py` | Key-text-free running-key attack (joint English-ness of plaintext and key). Self-calibrates and reports when it is underpowered. |
| `language_model.py` | Frequency-weighted n-gram model (order 2–4) over rune indices, built from the `wordfreq` English list with Stupid Backoff. Run directly for the English-vs-random discrimination test. |
| `attack_keycrib.py` | Candidate-key attacks: self-referential running keys via key-skip (Part A) and a common-word key crib with a random-ciphertext false-positive control (Part B). |
| `results/` | Archived run outputs, dated. |

## Usage

```bash
cd liber-primus
python3 parse_lp.py          # segment inventory
python3 validate_solved.py   # should print 9/9 checks passed
python3 analyze_unsolved.py  # statistics + simple-attack battery
python3 att
==========================================================================================
REPO: krcdavis__cicada-tools
# cicada-tools
Cicada 3301 Liber Primus python scripts

The Liber Primus is an unsolved cipher manuscript produced by the mysterious Cicada 3301. It uses a unique rune-based substitution alphabet combined with (at least in the solved pages) a variety of combinations of atbash, Caesar and vignere ciphers. The vast majority of the manuscript remains unsolved, mysterious and impenetrable. This repository contains a variety of python files for poking and prodding at the text, attempting to wring something, anything out of it, that might help unlock the solution.

Folders
rune-sentences: Unsolved pages, runic form, separated by sentence.
pseudo-sentences: Unsolved pages converted to the "pseudo-readable" alphabet.
pseudo-labeled: Unsolved pages converted to "pseudo-readable" with sentences labeled.
rune-solved: Solved pages in runic.

The transcriptions are sourced from https://github.com/scream314/cicada3301/blob/master/liber_primus.md

Files
crunes.py
Alphabets, basic functions.

convertor.py
Converts the runic transcriptions to as ASCII alphabet that's kind of readable if the underlying text isn't encrypted beyond having been converted to runes. Makes the text easier to manipulate without worrying about encoding. Also generates the labeled-sentence files. So any changes to the underlying transcriptions can easily be propagated... or changes to the alphabet. I've been told that using parentheses for those two letters is not very good. I'll fix it later

solved.py
Solves the already-solved pages using their known solutions. This includes pages 56 and 57 from the otherwise unsolved sections, which is why they're labeled as "unsolved" despite being, you know, solved.

buffer.py
One of the most interesting things about the unsolved pages is the statistical lack of doublets. The easiest way to explain this is some kind of autokey cipher where the amount of "f" runes (first in the runic alphabet, so a value of zero) in the text before autokeying is low. In fact Cicada has played with "f" rune before, so them engineering text to have low "f"s isn't unthinkable. This file undoes the presumed autokey encryption. It doesn't really reveal anything, but there it is anyway.

wordconverter.py
Converts words to runic form. The dictionary used for brute force attempts was made using this and a selection of Cicada's writings, to get likely vocabuary. Some assumptions are made about certain problem points- for example, is the word "aeon" processed as ae-o-n or a-eo-n? A converter that works in alphabetical order as Mortlach's does will convert the 'eo' first, while one that 
==========================================================================================
REPO: lipeeeee__gematria
<div align="center">
	
# gematria
	
</div>

gematria is an efficient criptography tool to aid in the decyphering of cicada 3301's [Liber Primus](https://uncovering-cicada.fandom.com/wiki/Liber_Primus)(LP), It's purpose is to process a given string and analyse it into various hash functions and gematria sums. It can process hashes and gematria sums almost instantly.

![image](https://github.com/lipeeeee/gematria/assets/62669782/d42250b9-4c13-4442-b82d-6b1bdd6a0182)

***After processing, gematria will create a file with the results in ./outputs/{string}.txt***

# Gematria Primus
Gematria Primus, found during the 2013 puzzle, is an alphabet with 29 runes, each with an English equivalent and a numerical value, The numerical values are consecutive prime numbers in ascending order. The runes themselves are the focal point of the current step, Liber Primus.

3301's inclusion of a value for each rune allows for a function to assign a number to any word. This is simply adding the value of each rune - what we call gematria sum. 3301 has used this gematria sum previously, notably in the count command from the onion terminal and with certain phrases throughout the puzzles. Certain phrases include:

- The Instar Emergence: 761 (reflected in the song's file name of 761.mp3, and in the song's length of 167 seconds)
- Patience is a virtue: 761
- Interconnectedness: 772 (not prime, but 277 is, which is the song's length in seconds)
- one of the solved pages contains words in runes within a square of numbers; gematria summing the words completes a magic square
- more sentences than you would expect in the solved pages gematria sum to prime numbers

![image](https://github.com/lipeeeee/gematria/assets/62669782/6ad1d502-0076-4fd9-9ca1-ea7b240cdd72)

## Gematria Primus Script
By running gematria, it will automatically process the sums and calculte primes and [emirps](https://en.wikipedia.org/wiki/Emirp) of the Gematria Primus values... Processing order:
1. Whole string
2. Each word in string
3. Each line in string
4. Atbash string
5. Each word in atbash string
6. Each line in atbash string

Example of output:
```shell
$ python lib/main.py 'Any Message'
```
```
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   GEMATRIA PROCESSING...
	RUNIC: ᚪᚾᚣ ᛗᛖᛋᛋᚪᚷᛖ
	LATIN: AENY MESSAGE >>> 2023-06-14 11:09:36.018235
-----------------------------------------------------------------------
==========================================================================================
REPO: localavaster__cadrypt
(no top-level README)
files: .git
==========================================================================================
REPO: micheloosterhof__aldegonde
`aldegonde` is a Python library for classical cryptography. It is
written to accomodate non-standard alphabets (i.e. not just A-Z).

==========================================================================================
REPO: micheloosterhof__cicada-2016
(no top-level README)
files: .git stage01
==========================================================================================
REPO: mortlach__runeglish-lm
(no top-level README)
files: .git
==========================================================================================
REPO: naliferopoulos__3301
(no top-level README)
files: .git examples.py lputils
==========================================================================================
REPO: neuroretransmit__liberprimus-tool
(no top-level README)
files: .git
==========================================================================================
REPO: nexon33__cicada3301
# Cicada 3301 Liber Primus - Complete Solution Package
## Reddit Post Materials

This package contains the complete research findings on the Cicada 3301 Liber Primus cipher system.

## 📁 Files Included

### Main Documentation

1. **FINAL_COMPLETE_SOLUTION.md** - Complete comprehensive summary
   - All solved components (95% complete)
   - Dual Fibonacci-Lucas pattern explanation
   - Skip position independence discovery
   - Application guide for Page 32
   - ~13KB, the definitive reference

2. **BREAKTHROUGH_SUMMARY.md** - Mid-research breakthrough findings
   - Discovery of dual sequence pattern
   - The "689 anomaly" that revealed everything
   - Philosophical insights
   - ~12KB

### Verification Scripts

3. **verify_lucas_pattern.py** - Proves the dual Fibonacci-Lucas pattern
   - Verifies 689 = 566 + L₁₀
   - Shows F₁, F₇, F₁₃ arithmetic progression
   - Demonstrates L₁, L₇ overlay
   - Run this first to see the pattern!

4. **solve_skip_position_transformation.py** - Discovers independence
   - Tests 8 different hypotheses
   - Proves master indices ≠ skip positions
   - Shows seed + gaps reconstruction
   - Critical insight discovery

5. **test_independent_skip_generation.py** - Validates across all 5 solved pages
   - Tests seed formulas
   - Analyzes gap patterns
   - 100% reconstruction verification
   - Strongest evidence

6. **analyze_skip_patterns.py** - Cross-page pattern analysis
   - Compares all 5 solved pages
   - Fibonacci gap identification
   - Modular pattern analysis
   - Statistical overview

## 🚀 Quick Start

### For Reddit Readers:

1. **Start here:** Read `FINAL_COMPLETE_SOLUTION.md` for the complete picture
2. **See the proof:** Run `verify_lucas_pattern.py` to see the mathematics
3. **Understand independence:** Run `test_independent_skip_generation.py`

### Running the Scripts:

```bash
# Install dependencies (if needed)
pip install numpy

# Run the verification scripts
python verify_lucas_pattern.py
python test_independent_skip_generation.py
python solve_skip_position_transformation.py
python analyze_skip_patterns.py
```

## 🎯 Key Discoveries

### 1. Dual Fibonacci-Lucas Pattern (100% Solved)
- Welcome page uses BOTH Fibonacci AND Lucas sequences simultaneously
- F₁, F₇, F₁₃ create arithmetic progression (positions 1, 7, 13, diff=6)
- L₁, L₇ start with same progression
- 689 = 566 + L₁₀ (123) - completely deterministic!

### 2. Master Indices Generate Keys (100% Solved)
```python
KEY = [master_index % 29 for master_index in selected_indices]
```
- No separate key storage in Page 57
- Mathematics generates the key itself
- E
==========================================================================================
REPO: r4nd0mD3v3l0p3r__LiberPrimusSolver
# LiberPrimusSolver
an attempt at solving Cicada 3301 Liber Primus

This program is Free Software, released under GNU GPL v3

## How to run it

You need both [Node](https://nodejs.org/en/) and 
[Yarn](https://yarnpkg.com/lang/en/)

- Clone the repository
- launch `yarn install`
- use `yarn start` to launch the program
- use `yarn test` to run tests

## How it works

Liber Primus Solver (LPS from now on) can execute various tasks.

## How to configure it

the **data** folder contains various txt files.

aWarning.txt, firstKoan.txt, welcome.txt and unsolved.txt are excerpts from the
Liber Primus. First three files contain the sections that were decrypted, while
unsolved.txt contains all the pages that have yet to be decrypted.
You can add more if you want to test different parts of the Liber Primus.

LPS uses [rtkd transcription of Liber Primus](https://github.com/rtkd/iddqd/tree/master/liber-primus__transcription--master).

output files will be placed into a folder named output, that will be created in
data folder as soon as the program is launched.

## The tasks.txt file

**Tasks.txt** is the file used to program LPS. Each row should be a valid JSON,
and represents a task that LPS will execute.
There is another file, **tasks.examples.txt**. This one contains the tasks that were executed by me against the
unsolved pages, along with some comments and observations.

### Type of tasks available

Each row of the tasks.txt file should contain **taskType**, used to specify which type of task the line is
for. Here's all the available task types:

#### decrypt

This one is used to try and decrypt the Liber Primus text using (and chaining) various cipher methods

The general form of a line is as follows:
```json
{"inputFileName":"firstKoan.txt", "outputFileName": "atbashThenShift","taskType":"decrypt", "pipeline":[{"cipher":"atbash"}, {"cipher":"shift", "by":"3"}]}
```

- **inputFileName** is the file the task will use as input (it must be an excerpt
from Liber Primus that follows the transcription rules mentioned above)
- **outputFileName** is the name of the file that will contain the task outcome.
Two files will be generated, one outputFileName.rune.txt containing the result
in runes, another outputFileName.txt containing plain english. At the moment,
runes with multiple possible translations (eg ᛋ that translates
 both into S and Z) will be written with both values enclosed in square brakets.
 An example from the First Koan: ᚹ-ᚣᛠᚹᛟ will appear as A-[C,K]OAN
 Future version will handle these situations in a better way.
- **pipeline** this contains the list of c
==========================================================================================
REPO: ralphatobe__cicada-3301
# cicada-3301
Repository for decoding the remaining Liber Primus pages.

[Unsolved Liber Primus pages](https://www.dropbox.com/sh/lkta4q921vliyuw/AADmZ1YUHXWSjSizlMGZHXVMa?dl=0)

[Liber Primus cipher](https://vignette.wikia.nocookie.net/the-cicada-puzzles/images/9/95/Gematria_primus.jpg/revision/latest?cb=20140109214308) (Gematria Primus)

Packages:
* OpenCV
* numpy
* scipy
* matplotlib

Running the repo:
1. Download the [unsolved Liber Primus pages](https://www.dropbox.com/sh/lkta4q921vliyuw/AADmZ1YUHXWSjSizlMGZHXVMa?dl=0)
2. Unzip vocabulary.zip
3. Run `python process_characters.py` to uniformly crop vocabulary images
4. Run `python process_images.py` to extract transcripts from Liber Primus pages


==========================================================================================
REPO: relikd__LiberPrayground
# Liber Prayground

![animated program](img/main.gif)

## Quick Overview

### Main components:

- `playground.py` this is where you want to start. Simply run it and it will greet you with all the posibilities. Use this if you want to experiment, translate runes, check for primes, etc. See [Playground](#playground) for more info.

- `solver.py` you can run `solver.py -s` to output all already solved pages. Other than that, this is the playground to test new ideas against the unsolved pages. Here you can automate stuff and test it on all the remaining pages; e.g., there is a section to try out totient functions. See [Solving](#solving) for more info.

- `probability.py` some tools for rune frequency analysis, interrupt detector, and Vigenere / Affine breaker. These tools will try to guess the key length of the cipher and determine the most probable key shift per key group. See [Heuristics](#heuristics) for more info.

You can call `playground.py` and `solver.py` with command line arguments `-v` or `-q` (or both), to control the verbosity of the output (see [Log levels](#l-log-levels)).

### LP pages and notation

The `pages` folder contains all LP pages in text and graphic. Note, I have double checked each and every rune while copying and added missing whitespace characters like `'` and `"`.

Rune values are taken from Gematria, with these unicode characters representing: space (`•`), period (`⁘`), comma (`⁚`), semicolon (`⁖`), and chapter mark (`⁜`).

### The LP library

These files you probably wont need to touch unless you want to modify some output behavior or rune handling. E.g. if you want to add a rune multiply method. These are the building blocks for the main components.

- `utils.py`, a small collection of reusable functions like `rev`, `is_prime`, and `is_emirp` (reverse prime) checking.

- `RuneText.py` is the representation layer. The class `RuneText` holds an array of `Rune` objects, which represent the individual runes. Each `Rune` has the attributes `rune`, `text`, `prime`, `index`, and `kind` (see [Solving](#solving)).

- `RuneSolver.py` contains a specific implementation for each cipher type. Two implementations in particular, `VigenereSolver` which has methods for setting and modifying key material as well as automatic key rotation and interrupt skipping. `SequenceSolver` interprets the cipher on a continuous or discrete function (i.e., Euler's totient).

- `IOWriter.py` handles data ouput to stdout. It does all the word sum calculations, prime word detection, line sums, and output formatting (including colors). Everything you don't want
==========================================================================================
REPO: resvolver__c1cada


==========================================================================================
REPO: rtkd__iddt
#### IDDT ####

Find a hidden service URL that matches the hash from 3301's Liber Primus, page 73.

#### Quick start ####

Clone and run the repository to start the server and IRC client.

```bash
$ git clone https://github.com/rtkd/iddt .
$ npm install
$ npm start
```

#### Available HTTPD routes ####

```bash
/serve/client/
```
Serves the client for auto install.

```bash
/store/packet/
```
Stores and checks descriptors and URLs send by clients.

#### Available IRC commands ####

##### client all #####

Lists all clients.

```bash
lb client all
```

##### client active <interval|date> #####

Lists all active clients within/at specified interval or date.

```bash
lb client active 1w
lb client active 01.01.2019
```

##### client inactive <interval|date> #####

Lists all inactive clients within/at specified interval or date.

```bash
lb client inactive 1w
lb client inactive 01.01.2019
```

##### client status #####

Lists all clients with specified status.<br>

0 = client is not sending<br>
1 = client is sending descriptors<br>
2 = client is sending urls<br>
3 = client is sending descriptors and urls

```bash
lb client status 3
```

##### client top <integer> #####

Lists top x most sending clients.

```bash
lb client top 10
```

##### service count #####

Lists loot.length

```bash
lb service count
```

##### service list <interval|date> #####

Lists collected services within/at specified interval or date.

```bash
lb service list 1w
lb service list 01.01.2019
```

##### service top #####

Lists top x most picked up services.

```bash
lb service top 10
```

##### hash all #####

Hashes all collected hidden service URLs and compares them to target hashes.

```bash
lb hash all
```

##### hash url <16 char domain name> #####

Hashes 16 char domain name and compares it to target hashes.

```bash
lb hash url facebookcorewwwi
```

#### Bugs ####

https://github.com/martynsmith/node-irc/issues/491

==========================================================================================
REPO: rtkd__idkfa
#### Liber Primus Translator ####
___

A toolset for working with 3301's Liber Primus.

#### Quick start ####
___

Clone and run the repository to translate the first segment of Liber Primus.

```bash
$ git clone https://github.com/rtkd/idkfa .
$ npm install
$ chmod u+x idkfa
$ ./idkfa -s 0.0 -v l -i l
```

#### Available Commands ####
___

##### -c, --charAt #####

Returns latin character(s) at position(s) n.

```bash
-c 0 1 2 3
```

##### -f, --find #####

Finds crib candidates and returns source, source path and key

```bash
-f the circumference
```

##### -i, --invert #####

Inverts/Reverses source, gematria and key properties

```bash
-i f
```

  * **f** — Invert gematria column: futhark
  * **k** — Invert key
  * **l** — Invert gematria column: latin
  * **o** — Invert gematria column: offset
  * **p** — Invert gematria column: prime
  * **s** — Reverse shift
  * **t** — Reverse source text

##### -k, --key #####

Generates and applies key(s) for decryption.
Keys can be denoted as `integer`, `integer csv`, `latin`, `futhark` or `mathematical expression`. Multiple keys are seperated by a space.

For details on using mathematical expressions see: [MathJS Functions](http://mathjs.org/docs/reference/functions.html)

**Expressions must be enclosed in single quotation marks.**

Generator functions `int()`, `odd()`, `even()`, `prime()`, `fib()` will accept 0, 1 or 2 parameters of type `integer`
.
  
  * 0 parameters will generate as many consecutive numbers as the selected source has graphs.
  * 1 parameter will generate first n consecutive numbers, and repeat as source has graphs.
  * 2 parameters will generate consecutive numbers from n to n, and repeat as source has graphs.

If first parameter is larger than second, order of numbers will be reversed.

Available transformations: Euler Phi `ephi()`, Möbius: `mob()`

##### Examples #####

Generate key: 1,1,1,1..
```bash
-k 1
```

Generate key: 1,2,3,1,2,3..
```bash
-k 1,2,3
```

Generate key: 23,10,1,10,9,10,16,26,23,10,1,10,9,10,16,26..
```bash
-k divinity
```

Generate key: 0,3,3,17,24,4,0,3,3,17,24,4..
```bash
-k ᚠᚩᚩᛒᚪᚱ
```

Generate key: 1,2,4,6,10,12,16,18,22,28,30,36..
```bash
-k '$(ephi(x), x, prime())'
```

Generate key: 29,23,19,17,13,11,7,5,29,23,19,17,13,11,7,5..
```bash
-k '$(x, x, prime(10, 2))'
```
Generate keys: 1,2,3,1,2,3.. **and** 23,10,1,10,9,10,16,26,23,10,1,10,9,10,16,26..
```bash
-k 1,2,3 divinity
```

##### -p, --patch #####

  *	**d** — Patch the dictionary to match expected output ((I)NG, I(A/O)..)
  *	**s** — Patch chars at specific positions within source. (See config.js)

```ba
==========================================================================================
REPO: rtkd__kerry
### Kerry (de)crypter ###

Because we all want to know..

### Run ###

```bash
$ node kerry.js <kerry/unkerry> <string>
```

### Example ###

```bash
$ node kerry.js unkerry 'kerry zoxrn'
```
==========================================================================================
REPO: scream314__cicada3301
(no top-level README)
files: .git
==========================================================================================
REPO: seeker-it__3301-gematria
# 3301-gematria
A simple Python script that calculates the Gematria values based on Cicada 3301's Gematria Primus.

# Requirements
This script requires Python 3.6 or higher. No additional libraries need to be installed.

# How To Run
1. **Open a terminal**
- On *Windows*, press *Win + R*, then type *"cmd"* and hit *Enter*.
- On Mac/Linux, open the Terminal application.

2. **Navigate to the script's directory, e.g. where you saved it.**
- If the file *gematria_calc.py* is located on your desktop, type the following command:
```
cd %UserProfile%\Desktop
```

3. **Run the script.**
```
python gematria_calc.py
```

# Usage
1. Run the script (for a detailed guide on how to do this, check **How To Run** above).
2. You will be prompted to enter a string of text. The script will add up values of each letter corresponding to 3301's Gematria Primus table and tell you whether the end result is a prime number or not.
3. If you enter a character that isn't a part of the Gematria Primus (most commonly V), a warning will be shown, and the character will be substituted with the default value for U (3).
4. To exit the program, type 1234. The style of Cicada OS has been implemented as a cute little reference.

# Examples
### Example 1: Prime Checker returns a prime number.
```
LP Input: Cicada

Total: 157
Prime Checker: Congrats! The result is a prime number!
```

### Example 2: Prime Checker doesn't return a prime number.
```
LP Input: Example

Total: 465
Prime Checker: The result is not a prime number!
```

### Example 3: Invalid character detected in user input.
```
LP Input: Ex@mple

Warning: You have inputted a character that isn't present in 3301's Gematria Primus ('@')!
This character was substituted for U (Value = 3) instead.

Total: 371
Prime Checker: The result is not a prime number!
```

# Explanation
- The *is_prime(n):* function which checks if a given number *n* is prime.
- *mappings* includes a list of latin characters as seen from the [Gematria Primus](https://uncovering-cicada.fandom.com/wiki/Gematria_Primus?file=Testout.jpg).
- *process_input(user_input)* processes the user's input by summing the corresponding Gematria values for each character. This is called a **gematria sum**, I'm just not referring to it that way.

If a character isn't in the *mappings* section, namely V, it's replaced with the value for **U (3)** - That is because these two letters are interchanged in the solved pages, similarly to letters like **C and K (which both have the value 13)** or **NG/ING (value 79)**.

This doesn't only work for V, but for any special character you input
==========================================================================================
REPO: taraweling__Cicada3301
Hello.

Epiphany is upon you. Your pilgrimage has
begun. Enlightenment awaits.

Good luck.

3301

–––––––––––––––––––––––––––––––––––––––––

In 2012, a mysterious message appeared on
4chan that referred to an entity called
"3301." The message contained another 
secret messege within it, a clue, a cypher. 
Those who found this clue were then led to
another, and another, until the trail went cold...

–––––––––––––––––––––––––––––––––––––––––

Modeled after this international 
informatics events of the 10's, our game
immerses you in a world of cyphers, 
monsters, and mysteries as well. 

themes: cryptography, logic, linguistics, 
data security, warped reality, breaking the fourth wall 

our implementation of the Cicada mystery 
is a text-based adventure game where the 
player works through puzzles increasing 
in complexity and difficulty. the player 
interacts with the game world (and 
sometimes the real world) to progress 
through the series of events that may 
eventually lead you to the identity of 
cicada 3301.

–––––––––––––––––––––––––––––––––––––––––

Our game is not yet everything we 
envisioned; We have written the following 
parts:

-me command
-inspect command
-limited inventory
-drop command
-other commands (eat, use, pickup)
-healing item
-regeneration
-victory condition
-events
-complex rooms
-leveling up
-world modification (maybe?)
-game saving
-ASCII art
-help command
-live typing

==========================================================================================
REPO: thecornerspore-dev__rune_swiss
# Rune Cipher Swiss Army Knife

The Rune Cipher Swiss Army Knife is a versatile cryptographic tool designed to work with Elder Futhark runes. It provides functionalities for transliteration, encryption, decryption, and brute-force decryption attempts with various ciphers.

## Features

- Transliteration between Elder Futhark runes and English.
- Encryption and decryption using Atbash, Caesar, and Vigenère ciphers.
- Playfair cipher encryption and decryption.
- Brute-force decryption with prime shifts and user-provided keys.
- Coherence checks for transliterated and decrypted texts.

## Installation

To use the Rune Cipher Swiss Army Knife, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/sasha-thecornerspore-dev/rune_swiss.git
Navigate to the repository directory:
cd rune-cipher-tool

Install dependencies: This script requires Python 3 and NLTK library. Ensure you have Python 3 installed on your system. You can download it from python.org. Install NLTK using pip:
pip install nltk

Run the script:
python rune_cipher_tool.py
Follow the on-screen prompts to select the operation you wish to perform.
Usage
After running the script, you will be prompted to choose an operation from the list of options. Enter the number corresponding to your choice and provide the necessary input when prompted.

For example, to transliterate runes to English, select option 1 and enter the runes when prompted.

Contributing
Contributions to the Rune Cipher Swiss Army Knife are welcome. Please fork the repository, make your changes, and submit a pull request.

License
This project is licensed under the MIT License - see the LICENSE.md file for details.

Acknowledgments
This tool was developed using Microsoft Copilot by Jeffrey M. Schatz
Special thanks to the Cicada 3301 community for their valuable feedback.

==========================================================================================
REPO: thomasandfriends__Cicada3301Runes
(no top-level README)
files: .git
==========================================================================================
REPO: tweqx__dwh-check
# dwh-check

Command line utility to check whether some data hashes to the deep web hash

Usage : `command | dwh-check`

Return 0 and prints a message when the deep web hash is found, returns 1 otherwise.

## Examples

`cat file | dwh-check`

`find -type f -exec sh -c "cat {} | dwh-check" \;`

`wget -o /dev/null -O - example.com | dwh-check`

`echo -n sheogmiof | dwh-check > /dev/null && echo O_o`

## Hashes supported
 * SHA-512
 * BLAKE2b
 * Streebog
 * SHA-3
 * FNV-0/FNV-1/FNV-1a
 * Grøstl
 * MD6
 * JH
 * BLAKE-512
 * LSH
 * Skein
 * Keccak3
 * CubeHash
 * Whirlpool-0/Whirlpool-T/Whirlpool

## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)

==========================================================================================
REPO: wtf-jik__cicada3301
# cicada3301

`page_1` contains the first page of the Liber Primus encoded as UTF-8.

`atbash.py` Solves the Atbash cipher of page_1.

# To run

`$ python atbash.py` 


==========================================================================================
REPO: yo-yo-yo-jbo__cicada_tools
(no top-level README)
files: .git
==========================================================================================
REPO: ztlw30813__cicada3301
# Cicada 3301 Liber Primus Decryptor

A Python-based decryptor for the Cicada 3301 Liber Primus puzzle.

## Features

- **Rune to Text Conversion**: Converts Elder Futhark runes to alphabetic text using the Gematria Primus
- **Caesar Cipher Decryption**: Tries all 26 possible shifts and finds the best fit using chi-squared analysis
- **Vigenère Cipher Decryption**: Tests known Cicada 3301 keywords and common keys
- **Frequency Analysis**: Compares letter frequencies to standard English distribution
- **Interactive Mode**: User-friendly interface for exploring different decryption methods

## Usage

### Command Line Mode

```bash
# Analyze a file with all methods
python3 decryptor.py LiberPrimus3301 --all

# Caesar cipher with specific shift
python3 decryptor.py LiberPrimus3301 --caesar 13

# Vigenère cipher with specific key
python3 decryptor.py LiberPrimus3301 --vigenere PSYOP

# Show frequency analysis
python3 decryptor.py LiberPrimus3301 --frequency
```

### Interactive Mode

```bash
python3 interactive_decryptor.py
```

### Helper Tool

```bash
# Interactive mode (full menu system)
python3 cicada_helper.py

# Command line mode
python3 cicada_helper.py gematria      # Show Gematria reference table
python3 cicada_helper.py structure     # Analyze Liber Primus structure
python3 cicada_helper.py analyze       # Perform Gematria analysis
python3 cicada_helper.py decrypt       # Quick decryption menu
python3 cicada_helper.py frequency     # Frequency analysis
python3 cicada_helper.py solutions     # Known solutions
python3 cicada_helper.py export        # Export results to file
```

## Gematria Primus Reference

| Rune | Letter | Value | Rune | Letter | Value |
|------|--------|-------|------|--------|-------|
| ᚠ | F | 0 | ᛋ | S(Z) | 15 |
| ᚢ | V(U) | 1 | ᛏ | T | 16 |
| ᚦ | TH | 2 | ᛒ | B | 17 |
| ᚩ | O | 3 | ᛖ | E | 18 |
| ᚱ | R | 4 | ᛗ | M | 19 |
| ᚳ | C(K) | 5 | ᛚ | L | 20 |
| ᚷ | G | 6 | ᛝ | NG(ING) | 21 |
| ᚹ | W | 7 | ᛟ | OE | 22 |
| ᚻ | H | 8 | ᛞ | D | 23 |
| ᚾ | N | 9 | ᚪ | A | 24 |
| ᛁ | I | 10 | ᚫ | AE | 25 |
| ᛄ | J | 11 | ᚣ | Y | 26 |
| ᛇ | EO | 12 | ᛡ | IO | 27 |
| ᛈ | P | 13 | ᛠ | EA | 28 |
| ᛉ | X | 14 | | | |

## Delimiters

- `-` : Word separator
- `.` : Clause separator  
- `&` : Paragraph separator
- `$` : Segment separator
- `/` : Line separator
- `%` : Page separator

## Known Cicada 3301 Keywords

Some keys that have been discovered or are suspected:

- PSYOP
- ENLIGHTENMENT  
- CICADA
- WELCOME
- LUPUS
- TOTEN
- QUID
- OBSIDIAN
- PUER
- NOVUS
- ORDO
- TEMPUS
- FUGIT
- SOLVED
- PRIMUS
- GEMATRIA

## Files

- `decryptor.py` - Main dec
