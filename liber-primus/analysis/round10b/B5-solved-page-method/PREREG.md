# Round 10B / Lane B5 — METHOD CONTINUITY — pre-registration

Written **before** any sweep was run. Trust anchor confirmed first:
`python tests/validate.py` → *ALL VALIDATIONS PASSED* (2026-08-12), i.e. the rig
still reproduces 01.jpg −4.48, 05.jpg −4.98, 06.jpg −4.13, 03.jpg DIVINITY −4.34,
14.jpg FIRFUMFERENFE −4.24.

---

## 1. The continuity argument (what predicts the hypothesis)

Reconstructed escalation of the author's **key specification** across every solved
stage (sources: `research/05-crypto-techniques.md`, `analysis/recon/LP1-METHODOLOGY.txt`,
`tests/validate.py` SOLVED table, `src/lp/ciphers.py`):

| stage | cipher | key | key MATERIAL length | new idea demanded of the solver |
|---|---|---|---|---|
| 2012 s2 | Caesar | 4 | 1 number | key is a *semantic riddle* ("Claudius = 4th emperor") |
| 2012 s3/s5 | book code / Vigenère | Mabinogion; Mayan numerals | external | key delivered **out of band**, in another notation |
| LP p01 | Atbash over GP | — | 0 | a classical cipher over a **custom 29-symbol alphabet** |
| LP p06–09 | Atbash **then** Caesar+3 | 3 | 1 | **composition** of two named transforms + a numeric parameter |
| LP p03–04 | Vigenère | DIVINITY | 8 runes | key is a **theme word of the book itself**; ᚠ-nulls that do not advance the key |
| LP p14–15 | Vigenère | FIRFUMFERENFE | 13 runes | the key is spelled in the author's **own orthography** (C→F) |
| LP p56 | keystream | φ(pᵢ) = pᵢ−1 mod 29 | **∞** | key is a **generated sequence from a function the book declared sacred** (p05) |

**The dimension that escalates is not key length** — key material already reached ∞ at
p56, so there is nowhere further to go on that axis. What escalates is the
**abstraction and indirectness of the key SPECIFICATION** (named transform → transform +
parameter → semantic word → semantic word + orthography rule → named mathematical
function), while **the key material is always derivable from inside the book**. No solved
Liber Primus page has ever used an external artifact as its key.

**Therefore the predicted next step is not a new primitive.** It is the author's two
demonstrated *keyed* constructions, **composed** — exactly the move p06–09 already makes
with Atbash∘Caesar — with the composition's free parameter (a start offset into the
sacred sequence) as the new thing the solver must find.

This is also, independently, the repo's own un-executed proposal:
`analysis/recon/i7_constants/AUDIT.md` l.104–106 and l.140 name
**"G5 = G4 ⊕ G2 (composition: keyword then totient stream, both signs)"** and
`i7_constants/priority_seeds.json` lists `G5_keyword_xor_totient` in `family_priority`.
`analysis/recon/i7_oracle/sweep.py` then swept **G1/G2/G3 only** (prime, totient,
φ(prime), Fibonacci, golden × add/sub/Beaufort × strides 1–3 × offsets 0–39). **G5 was
proposed and never run.** Grep of `analysis/campaign18_skip/**` confirms the skip-aware
armada also kept the two families strictly separate: `RUN-keywords-full.log` (~620
keywords, periodic only) and `RUN-numeric.log` / `RUN-numeric2-full.log` (874 + extended
numeric streams, stream only). No composed key appears in any log or catalog builder.

---

## 2. Hypothesis (H-B5)

LP2 pages 0–54 are enciphered with a **composed keystream**

```
K[j] = ( cw · W[(j + wphase) mod L]  +  cg · G[j + goff] )  mod 29
p[i] = ( c[i] + K[key_ptr(i)] ) mod 29
```

where
- `W` = a **Gematria-Primus themed word** (the author's demonstrated key TYPE), taken from
  `data/keys/thematic.txt` + the `i7_constants/priority_seeds.json` keyword list;
- `G` ∈ {`prime_totient_stream` (the sanctified p56 generator), `prime_stream`,
  `totient_stream`} from `src/lp/ciphers.py` — no new generator is invented;
- `cw, cg ∈ {+1, −1, 0}` (0 recovers the two already-eliminated single-family lanes and
  serves as an in-sweep sanity anchor);
- `goff ∈ 0..63` — the **start offset**, the free parameter the continuity argument says
  is the new work;
- optional Atbash pre-reflection (demonstrated at p01/p06);
- `key_ptr` advances under the **validated skip-tolerant beam** (`campaign18_skip/sweep.py`
  `beam`/`prefilter`, gate: rigid −7.24/8.5% vs beam −4.15/100%), because the ~83%
  doublet filter desynchronises any key.

## 3. Controls (mandatory, run before the sweep is trusted)

- **PC-A (task-mandated re-find):** the pipeline's word→index→decode path must recover
  **DIVINITY** on 03.jpg and **FIRFUMFERENFE** on 14.jpg as the top-scoring word out of the
  full candidate list, at score ≥ −5.0. Failure ⇒ abort, do not report a null.
- **PC-B (planted composed key):** encipher real English under
  `K = DIVINITY ⊕ prime_totient_stream(goff=17)` **with the 0.83 doublet key-skip filter**,
  then run the identical sweep. Requirement: the true `(word, gen, goff, coefs)` is
  recovered at score ≥ −5.0, and the rigid (non-skip) decode of the same correct key
  scores < −6.0. Failure ⇒ the instrument cannot see its own signal ⇒ abort.
- **Null control:** the identical full sweep over **length-matched shuffles** of the same
  real pages (structure destroyed, composition preserved) — gives the empirical
  false-positive ceiling for this exact search size.

## 4. Pre-registered decision rule (numeric, fixed now)

Scale = the project's canonical `score_norm` (English solves −4.13…−4.98;
confirm −5.5; historical skip-beam null-max −6.82; floor ≈ −7.5).

| verdict | condition |
|---|---|
| **BREAK** | any real-page config ≥ **−5.2** on the full-page beam **and** readable English **and** reproducible under `tests/validate.py` conventions |
| **POSITIVE (lead)** | real best ≥ **−5.5** **and** exceeds the shuffled-null maximum by ≥ **0.5** |
| **NEGATIVE** | real best < −5.5, **or** real best ≤ shuffled-null max + 0.3 |
| **ABORT** | either positive control fails |

## 5. Scope declared in advance

Pages 0, 1, 2, 5, 20, 54 (book-initial + mid + the last unsolved page). One 20-minute
budget. A negative here is a negative **for the composed-key family on these pages at
these offsets**, not for all compositions; the script is resumable over `--pages`.
