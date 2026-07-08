# Campaign XII — Burning Down the Self-Contained Leads

_2026-07-07. Two fronts, both aimed at converting "not yet tried" into "tried,
measured, reproducible, null" so future solvers don't re-run them. Reproduce:_
`PYTHONUTF8=1 python3 analysis/campaign12/payload_forensics.py` _and_
`… fetch_keytexts.py && … run_sweep.py`.

## Part 1 — pp49–51 payload: the remaining self-contained leads (all null)

Campaign VII characterized `canon_256.bin` (2048-bit high-entropy blob; not prime,
not RSA, not a runic key, not text); Campaign IX ran the hash-structure / AN-END /
64-byte-block-preimage leads. This closes what was left **without any external data**:

| Lead | Test | Result |
|---|---|---|
| Is it a container/format? | Magic-byte sniff (PGP/gzip/zip/bzip2/PNG/JPEG/GIF/PDF/ELF/DER/OpenSSH/LUKS), fwd/rev/decpref; base64 & base32 of the hex | **null** — the lone "PGP packet" flag is a false positive (first byte ≥0xC0, true of ~25% of random data; no packet body). base64→33% printable (noise). |
| Preimage under **32-byte** hashes | 37-string Cicada dictionary × {SHA-256, SHA3-256, blake2s} vs all sixteen 32-byte blocks (IX only did 64-byte digests) | **null** — 0 hits; `sha256(AN-END)` not a block either. |
| Short-key **repeating XOR**? | Hamming-distance keysize search 2–40, then column-crack the best candidate | **null** — a marginal ks=12 "dip" (d=3.789 vs 4.0) appeared, but transposing into 12 columns gives entropy **at the small-sample ceiling** and ~53% best printable = indistinguishable from random. Artifact of 15 block-pairs, not a key. |
| Hidden **image/QR**? | 2D bit-matrix vertical autocorrelation at widths 8/16/32/45/46/64/128 | **null** — all ≈0.50 (pure noise). No periodic raster structure, consistent with entropy 7.17/8. |

**Verdict:** the payload has no container, no short-key XOR, no image, and no
32-byte-hash preimage. Combined with VII/IX, `canon_256.bin` is now attacked from
every self-contained angle and remains a featureless 2048-bit high-entropy object —
consistent with a digest/keystream fragment whose meaning is only recoverable with
external context (or genuinely random).

## Part 2 — expanded running-key sweep (15 new keytexts, clean null)

The repo's tested key corpus was small (the 5 explicitly-referenced works + rune poem
+ solved plaintext). This adds a **documented, content-verified** set of further texts
Cicada thematically gestured at, each run through the validated `attack.py runningkey`
(all offsets, both signs, ±Atbash, per unsolved page; threshold −5.2, English
≈ −4.0…−4.4). Every text was verified by an expected title/author substring before use,
so nothing is mislabeled.

| keytext | best score | | keytext | best score |
|---|---|---|---|---|
| The Prophet (Gibran) | −6.048 | | Meditations (M. Aurelius) | −6.126 |
| Rubáiyát (Khayyám) | −6.104 | | The Gold-Bug &c. (Poe) | −6.14 |
| Walden (Thoreau) | −6.109 | | Leaves of Grass (Whitman) | −6.152 |
| The Dhammapada | −6.117 | | Thus Spake Zarathustra | −6.231 |
| Tao Te Ching (Legge) | −6.117 | | Confessions (Augustine) | −6.246 |
| | | | I Ching (Legge) | −6.258 |
| | | | Epic of Gilgamesh | −6.275 |
| | | | Beowulf | −6.286 |
| | | | Bhagavad Gita | −6.301 |
| | | | The Art of War (Sun Tzu) | −6.341 |

**0 texts cleared threshold. Best score −6.048 — solidly in the noise band, ~1.6
below an English break.** This is the *mechanistically expected* result: Campaign IV
showed any natural-English running key injects ~3.3% doublets that LP2 does not have,
so keytext-hunting was doomed regardless of *which* text. The sweep confirms it across
a much wider thematic net and, more importantly, **enumerates the eliminated set** so
the "we can't claim we tried all keytexts" gap shrinks by 15 named, sourced entries.

### Honest limits of the corpus
- **Not exhaustive.** 5 further candidates (Alice in Wonderland, the Kybalion, Divine
  Comedy, and two others) failed to download on transient Gutenberg TLS timeouts and
  are **not** in this run; 2 IDs (Egyptian Book of the Dead, a Fabre insect volume)
  were auto-**dropped** by the content-verify guard rather than risk mislabeling. The
  falsifiable-keytext avenue remains formally open — this narrows it, doesn't shut it.
- Any solver can extend the closed set: add a slug/ID to `fetch_keytexts.py` and re-run
  `run_sweep.py`; a break would print an over-threshold hit (none did).

## Net for Campaign XII
- **Payload:** every self-contained forensic angle now closed (format, 32-byte
  preimage, repeating-XOR, image) — all measured nulls, not assumed.
- **Keytexts:** +15 named/sourced running-key candidates eliminated and documented.
- **Integrity:** the one marginal signal (ks=12 XOR dip) was chased down and shown to
  be a small-sample artifact rather than spun as a lead; the corpus's incompleteness is
  stated plainly.

No break — none was expected for an externally-keyed OTP — but the map of "already
tried, don't re-run" is materially larger and the one falsifiable open avenue is
smaller and now trivially extendable.
