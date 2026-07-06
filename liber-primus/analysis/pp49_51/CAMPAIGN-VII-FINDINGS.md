# Campaign VII — The pp49–51 Base-60 Payload

_2026-07-06. Executed after an independent review (Fable 5) noticed that every prior
"LP2 is a closed one-time-pad" verdict was proven only about the **runic** pages — while
three of the unsolved pages (49, 50, 51) are not runic prose at all, but a table of
two-character tokens that no campaign had ever loaded or attacked._

**All artifacts in this directory reproduce every number below:**
`canonicalize.py` → `canon_256.bin` / `canon_256.hex` / `canon_256_decpref.bin`;
`characterize.py`; `keytest.py`; `completeness_keys.py`.

---

## TL;DR

pp49–51 went from *"the one unexamined object in the corpus"* to a fully characterized
**2048-bit high-entropy binary payload** that is:

- **provably not a prime** and not a clean RSA modulus (the big-endian integer is even);
- **provably not a simple polyalphabetic key** over any runic page or the whole corpus
  (337,944 decryption configs, clean null);
- **not plaintext text** (40% ASCII-printable, longest printable run = 5 bytes).

It is consistent with a **pad / keystream / ciphertext that requires an external key** —
exactly the class the doublet analysis (Campaign IV) said the runic pages belong to.
The two remaining catalogued numeric keys (2012 Mayan rotation key, 2012 P.S. digit
string) were also run for completeness and are **null**.

---

## 0. The loophole this campaign exploits

Campaigns IV–V established that the runic ciphertext has a **soft, diagonal-only doublet
deficit** (measured doublet rate 0.66% vs ~3.45% expected), which **mechanistically
excludes any plaintext-independent keystream applied additively** — English running keys,
non-English keys, prime/totient streams, and raw numeric pads alike (they all inject
~3.3–3.45% doublets). That is why every keytext failed: *wrong mechanism, not wrong text.*

**But that exclusion only covers the runic stream.** Pages 49–51 carry a different data
type — a numeric table — that was never included in any statistical or cryptanalytic
result. This campaign characterizes that object directly.

---

## 1. Canonicalization — the first documented 256-byte stream

**Source pages.** Inspecting the master images (`data/relikd/p49.jpg`, `p50.jpg`,
`p51.jpg`): p49 = 3 rune lines + a 10×8 token table (80 tokens); **p50 = a 13×8 table,
no runes at all** (104 tokens); p51 = a 9×8 table (72 tokens) + 4 rune lines.
**80 + 104 + 72 = exactly 256 tokens = 256 bytes = 2048 bits.**

**Encoding.** Each two-character token is a base-60 pair. Digit values:
`0–9 → 0–9`, `A–Z → 10–35`, `a–x → 36–59` (60 symbols). Byte = `d0*60 + d1`.
Lowercase `f` (value 41) is a legal symbol that simply **never occurs** in the data —
the "F-skip" fingerprint that mirrors Cicada's own Gematria F-skip convention and
confirms base-60 intent.

**Decode verified against ground truth.** relikd token `3N` → 3·60+23 = **203**, `3p` →
231, `2l` → 167 — each exactly matching scream314's own independent decimal column.

**Three witnesses, majority-vote adjudication** (`canonicalize.py`):
(A) relikd tab-separated tables (structure-authoritative), (B) scream314 tokens,
(C) scream314's decimal column (an independent decode). Of 256 cells, **11 disagree**:

| class | count | resolution |
|---|---|---|
| token-split (relikd ≠ scream314), decimal breaks the tie by majority | 5 | resolved (idx 45, 50, 165, 172, 246) |
| **contested** (both tokens agree, only the derived decimal differs) | 6 | flagged; needs the master image (idx 25, 175, 182, 199, 215, 237) |

The two output variants (`canon_256.bin` majority vs `canon_256_decpref.bin`
decimal-preferred) **differ in exactly those 6 of 256 bytes.** Note: the project's
99.2%-accurate glyph classifier was **rune-trained** and does *not* read these Latin/digit
table characters, so the 6 contested cells are an honest open item, not a solved one.

**Canonical (majority-vote) stream, hex:**
```
cbe7a7ba61ed7eb75cf99cdef704b7d479ca0f2166893b576dc6ad1996428d85
7372c5273650850550541c49e651c74cfd10153b56ab9c50fe7692456ac47c33
7aff19c0c749a96ca44fcdb172902e528e3ac9c1ad1c6f41d3dcc631ec543823
de96482253e520ce7a3f1fda0eb82073498fc5f736ab23b82aed56360d14a3c1
c9b35678a98d48ab0a81e90df52ea0987dd25cadf6ae99bde7210e7034fbf9f8
e9d9c0526912faf8f0e4fe369475d112eb83a6af9028a751809c135126c0aa21
009b9f59b073692f6e4ad144c24c7f1539af063d4696fb548edb943b3a343397
443449f9900075af6aeac479ee2081ad908d2ad61638e0c0719eace6b424bd50
```
_This canonical byte stream did not previously exist in the community and is itself a
publishable primary source._

---

## 2. Characterization — what kind of object is it? (`characterize.py`)

| test | result |
|---|---|
| Shannon entropy | **7.17 bits/byte** (161/256 distinct values; 95 byte values never appear) |
| ASCII-printable | 102/256 (40%), **longest printable run = 5** → not text |
| Miller–Rabin primality (big-endian / little-endian / reversed / both 1024-bit halves) | **composite in every interpretation** |
| RSA modulus? | **no** — big-endian integer is **even** (ends 0x50), has small factors |
| perfect square? | no |

**Verdict:** high-entropy binary — a **pad / keystream / ciphertext**, not a message and
not a self-contained number-theoretic object. The Liber Primus refrain *"the primes are
sacred"* does **not** manifest here as a 2048-bit prime.

---

## 3. Key-material test over the runes — clean null (`keytest.py`)

Reuses the rig's verified cipher (`apply_stream_to_indices`, `atbash_indices`) and its
calibrated quadgram scorer (`score_norm`: ~ −2.2 solid English, < −4 noise).

**Design rationale:** applying the payload additively over the whole 12,956-rune corpus
is *already* doublet-excluded, so a null there is uninformative. The live hypothesis is
**local / per-page** use — especially that the token table keys the runic lines on its
**own** page (short targets where the doublet statistic doesn't bite).

**Search space (337,944 configs):** payload mod 29 as key; both canonical variants;
forward and reversed; additive (both signs), Beaufort, and Atbash; each of the 55
unsolved pages individually with a **full 256-offset sweep** on short pages; plus the
whole corpus.

**Calibration:** English baseline **−4.006**; random-rune noise floor **−7.491**;
threshold **−5.2**.

**Result:** best score **−6.385** — still essentially noise; **0 configs above threshold.**
(Top hits cluster on the short pages 49/54/50, which is score variance on short texts,
not signal.) **The payload is not a simple polyalphabetic/Beaufort/Atbash key over the
runes.**

### 3b. Onion-hex XOR — dead as proposed
The wiki-proposed "XOR pp49–51 data against the 2014 onion-trail hex" was never run.
The local onion artifact
(`analysis/armada20/pgp_2014-01-onion5-liber-primus.txt`) begins
`ffd8ffe0…4a464946…"Created with GIMP"` — i.e. it is a **JPEG file dump**, not free
key material. XOR against an embedded image is meaningless; the lead is dead as literally
proposed (the other onion pages follow the same image-dump pattern).

---

## 4. Completeness pass — remaining catalogued numeric keys (`completeness_keys.py`)

The two genuinely-untested numeric keys were run through the same harness:

- **2012 Mayan rotation key** `10 2 14 7 19 6 18 12 7 8 17 0 19` — appeared only as a
  *proposal* in the Campaign VI doc; never in a test script until now.
- **2012 end-of-puzzle P.S. digit string**
  `104127906589199853598278987395943189564044251069556756437392269523726824238529590817398343903703744757648634152034234993571­08713631`
  — the prior armada test was a hollow `−99.0` sentinel, so effectively never run.

**76,360 configs** (digit / digit-pair / reversed interpretations; both signs; Atbash;
per-page offset sweep + corpus). **Best −6.491; 0 above threshold — documented null.**
The Mayan key did not reach the top 15, consistent with its period-13 being excluded by
the flat autocorrelation at lags 2–30 (Campaign IV).

_Not run (with reason):_ telnet "missing-prime gaps" — already covered by the prior
prime-gap keystream sweep (best −6.81, `KEY-HINT-RESEARCH.md`); trailing-space primes —
no local source artifact.

**Every sourceable catalogued numeric lead is now executed and null.**

---

## 5. What remains genuinely untested

1. **Payload-as-ciphertext under an external key** — unbounded; cannot be tested without
   the key. This is the honest residual, and it is the same "needs an external key"
   conclusion the runic analysis reached.
2. **Relation to the page-56 512-bit "AN END" hash** (256 bytes = 4 × 64-byte digests) —
   speculative structural check, not yet done.
3. **The 6 contested bytes** vs a re-read of the master JPGs (requires a Latin/digit OCR,
   not the rune classifier).

---

## 6. Publishable claims (for the write-up)

**Strong / defensible:**
1. First full **quantitative characterization** of the doublet deficit (Campaign IV).
2. **Mechanistic exclusion** of *all plaintext-independent additive keystreams* — converts
   dozens of keytext negatives from "didn't find it" to "wrong mechanism" (the project's
   best intellectual product).
3. **Transcription provenance**: all public transcriptions share one lineage; relikd =
   byte-identical onion7 master (so the validated-OutGuess stego null applies to the true
   originals).
4. **New (this campaign):** pp49–51 is a characterized **2048-bit high-entropy binary
   payload** — not a prime, not a runic key — the one object six campaigns walked past,
   surfaced by reading three JPEGs; plus the first canonical 256-byte stream with a
   documented provenance/conflict table.

**Soften before publishing** (overstatements in earlier campaign docs):
"information-theoretically unbreakable" → "statistically indistinguishable from a
one-time pad under all tested cipher classes"; "internal cryptanalysis CLOSED" (this
campaign reopened and then characterized a genuinely un-analyzed object); "no external
key exists publicly" → "no key found in the searched corpus."

**Honest AI framing:** the defensible story is *"AI-agent swarms exhausted the
human-proposed hypothesis space and proved **why** the popular approaches must fail"* —
not "AI solved/closed Cicada." The sharpest irony for the article: six AI campaigns
declared the problem closed while the single un-analyzed data object sat in the repo's own
data files the entire time.
