# P7 — LP2-as-Pad Inversion (Campaign XV)

- **probe_id:** P7-pad-inversion
- **verdict:** null-closed
- **headline_number:** canon_256 (the real pp49–51 payload) best LP2-key decrypt
  score_norm = **-6.970**, which is *below* its own shuffled-key null band
  (null max -6.934); across all 7 counterparts, **0** exceed the calibrated null.
  Global best score_norm -4.968 (a 16-char onion) is itself *below* the shuffled-key
  null max -4.411 — LP2 gives **zero lift over a random key**.
- **falsifiable_signal:** For any counterpart, at any offset / sign / atbash under
  the LP2 running key: quadgram `score_norm > max(-5.2, shuffled_null_max)`, OR
  `IoC*N > max(1.3, shuffled_null_max)`, OR byte-level printable-ASCII fraction
  `> 0.90`, OR a valid `>=4`-byte container magic at a decrypt's offset-0.
- **signal_fired:** false
- **synthetic_validation:** PASS. A real English plaintext
  ("THEPRIMESARESACRED…SHOULDBEENCRYPTED", 66 runes) enciphered under the LP2
  stream at offset 5000 (add) is recovered by the *fast top-K search path* at the
  exact offset 5000 with score_norm **-4.25** and IoC*N **1.69** — proving the
  detector (and its IoC-prefilter speedup) sees a genuine planted signal well above
  the -5.2 gate. If any counterpart were truly enciphered under LP2, it would show
  the same lift. None does.
- **method:** Build the 12,956-rune LP2 keystream (body pages, mirroring
  campaign14/probes.py). Assemble every machine-readable Cicada counterpart in the
  repo: `canon_256.bin` + `canon_256_decpref.bin` (256B pp49–51 payloads),
  `key_anend_hash.txt` (64B AN END SHA-512), two 16-char v2 onions
  (`ky2khlqdf7qdznac`, `xsxnaksict6egxkq`), and the armored PGP/RSA byte bodies
  (`pgp_english_prose`, `pgp_welcome` — 190B each; other pgp_* files carry no
  decodable armored payload). Map each into the 29-symbol space (runes direct;
  bytes and hex via mod-29; onion base32 via its alphabet index mod-29). Run it as a
  **running-key decrypt** against LP2 in every combination: key ∈ {forward,
  reversed} × {identity, atbash(28−k)}, op ∈ {subtract, add}, over **all** stream
  offsets. **Family 1** scores quadgram `score_norm` (via translit) on the top-60
  IoC offsets per (key,op) and exact IoC*N on all offsets. **Family 2** (byte
  targets) decrypts at byte granularity (`plain = cipher ∓ rune mod 256`) and checks
  printable-ASCII fraction and `>=4`-byte container magics at every offset.
  Crucially, each LP2 result is judged against a **null calibration**: the identical
  best-of-search statistic run under 5 *shuffled* LP2 keys, which fixes the
  multiple-testing floor (~101k trials per target). A break requires LP2 to *exceed*
  the shuffled-key band, not merely a fixed threshold.
- **script_path:** `analysis/campaign15/P7-pad-inversion.py`
  (synthetic check: `analysis/campaign15/P7_synthetic_validation.py`)
- **reproduce_cmd:** `PYTHONUTF8=1 python analysis/campaign15/P7-pad-inversion.py`
  (and `PYTHONUTF8=1 python analysis/campaign15/P7_synthetic_validation.py`)

## one_paragraph

The inversion hypothesis — that the unsolved LP2 pages are not a message but the
random one-time pad, with the real plaintext hidden in some *other* Cicada object
enciphered under LP2 — was tested exhaustively against every machine-readable
counterpart in the repository (both pp49–51 payload variants, the 64-byte AN END
SHA-512 digest, both recovered v2 onion addresses, and the armored PGP/RSA byte
bodies), using the full 12,956-rune LP2 stream as a running key in all 8
key-variant × sign combinations at every offset, scored both in the native 29-symbol
rune space (quadgram + IoC*N) and at byte granularity (printable-ASCII + container
magics). **Nothing decrypts.** Every counterpart's best LP2-key result sits *within
or below* its own shuffled-key null band: canon_256 scores -6.970 vs a null max of
-6.934; the AN END hash 1.841·IoC vs null 1.856; even the seductive-looking -4.968
on a 16-char onion is beaten by shuffled random keys (-4.411), exposing it as pure
length-16 multiple-testing noise. Because a planted control message *is* cleanly
recovered by the same detector (score -4.25 at the exact offset), the null is a
property of the data, not a blind spot in the method: **LP2 provides no cryptographic
lift over a random key for any counterpart tested**, and the pad-inversion avenue is
documented closed. (The naive first pass — before null calibration and before
dropping 1-byte magics — "fired" on single-byte 0xc1 hits and short-target IoC
spikes; calibration against shuffled keys is what turns those false positives into
the correct null.)

## ledger_row

| Attack | Verdict | Why | Where |
|---|---|---|---|
| **LP2-as-pad inversion** — treat LP2 as the OTP keystream and run it as a running key against every other machine-readable Cicada object (pp49–51 canon_256 ×2, AN END 512-bit hash, 2× onion addrs, PGP/RSA bodies), all offsets/signs/atbash, rune-space + byte-space | ❌ dead | 0/7 counterparts exceed the shuffled-key null; canon_256 best -6.970 (< null -6.934), AN END IoC 1.841 (< null 1.856), onion -4.968 beaten by random keys (-4.411); planted control recovered at -4.25 confirms detector works | Campaign XV `analysis/campaign15/P7-pad-inversion.py` |
