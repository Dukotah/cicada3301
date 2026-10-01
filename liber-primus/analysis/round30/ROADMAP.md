# ROUND 30 — "The Rendered Book" Special Armada — ROADMAP (2026-09-28)

## Why this round exists (grounded in 29 prior armadas)

The internal ciphertext war is over: LP2 0-54 is OTP-class, unsolvable-by-design, every hinted channel
read, every instrument audited, the number/color/skip/matched-runic/non-English/date-pad lanes all closed.
Re-running any of that is forbidden. Passive monitoring is off the table by owner directive.

But Round 29 cracked open a genuinely **new frontier** that could not have been conceived before it:
**the 2014 Liber Primus master is not a scan or a hand-drawing — it is a PDF/PostScript document
machine-rendered through Ghostscript (Artifex) at 400 DPI** (HIGH confidence, reproducible control).
That single fact re-frames the whole artifact:

- The runes were drawn as **font glyphs or vector paths**, positioned by a typesetter, embedded in a PDF.
- A rendered PDF has channels a scan does not: font identity, glyph-variant selection, sub-pixel
  positioning, producer metadata, an authoring toolchain and OS window.
- None of these were ever examined, because until Round 29 nobody knew it was a rendered PDF.

Round 30 attacks the **container, the toolchain, the maker's hand, and the last live crypto residue** —
all active, all new, none in the ledger.

## Frontiers & lanes

### FRONTIER A — The PDF / font / rendering channel (freshest lead, highest novelty)
- **A1 — Rune font identification & glyph-outline forensics.** Extract the exact rendered glyph shapes
  from the 400dpi renders. Was a KNOWN Anglo-Saxon futhorc font used (2012-14 there were few — pin them),
  or a CUSTOM font? A custom font is an authorial artifact with a name/producer string. Check whether the
  SAME rune renders pixel-identically everywhere or has variant glyphs (a hidden selection channel).
- **A2 — Sub-pixel / positioning channel.** GS rendering is deterministic; kerning, baseline micro-shifts,
  and glyph-variant choice can encode data invisibly. Diff every identical rune instance pixel-exact across
  the book. This channel exists ONLY because it's a rendered PDF and has never been examined.
- **A3 — Producer / version / source-PDF forensics.** Pin the exact Ghostscript version range (optimized
  Huffman ⇒ < GS 10.06) → dates the authoring window & OS. Active OSINT hunt for the original source PDF
  (producer strings, font tables, any leaked/archived copy). Ties to the earlier N1 font-subset lead.

### FRONTIER B — External-key ciphertext battery (the last live internal crypto residue)
Round 29 proved only 3 artifacts are genuinely random: the 2.jpg stage04 payload, folly, and canon_256.
Two-time-pad can't touch a non-reused OTP — but a KEYED cipher under a Cicada-derivable key CAN be tested.
- **B1 — Structural crypto-ID + symmetric battery.** Identify block structure of each blob; test as
  AES/RC4/Blowfish/DES/GPG-symmetric (header-stripped) under every Cicada-derivable key (LP plaintext,
  gematria streams, page-56 hash, 3301 constants, PRNG seeds). Control-gated.
- **B2 — RSA / GPG-message structural test.** canon_256 = exactly 2048 bits — test as an RSA block / PKCS
  / OAEP structure and as a GPG message body against the known 7A35090F packets (on disk:
  armada20/pubkey_packets.json). Note the 4096-bit key can't wrap a 2048-bit ciphertext by size — so test
  under 2048-bit-key hypotheses and as a raw modular residue.

### FRONTIER C — The maker's hand (attribution vector never run)
- **C1 — Illustration / artist attribution.** The book's ART (drop-caps, the shrouded-corpse, mayfly,
  trees, cicada borders, section ornaments) is an ARTIST fingerprint. Reverse-image search + style
  comparison to known illustrators / woodcut / esoterica artists / ARG-art communities 2010-2014. Nobody
  has ever attacked the *illustration* as a signature. Active, web-driven, new.

### FRONTIER D — Integrity re-audit (R29-L1 proved the record lies)
- **D1 — Ledger integrity audit.** Round 29 found the repo carried a FALSE "tested" belief (the onion
  chain was never actually key-attacked). Systematically re-verify every "CLOSED/TESTED" claim in
  LEDGER.json against what code actually ran. Surface any lane the record THINKS is done but isn't —
  cheap, high-EV, can reopen real ground.

### FRONTIER E — Does the render finding reopen a prior null?
- **E1 — Render-aware re-examination.** The pp49-51 base-60 table, the red rubrication, and the "5×5"
  page were all analyzed as SCANS. Re-examine them as RENDERED GLYPHS at 400dpi: do the base-60 characters
  have variant renderings that resolve the 6 contested canon_256 bytes? Does knowing the glyph set is a
  font change any prior character-identity call?

### FRONTIER V — Adversarial verification + synthesis
Every A-E finding is verified refute-by-default before it's allowed to stand. Then synthesized; ledger
entries drafted.

## Doctrine (non-negotiable)
Control-validate before ANY positive claim (positive control recovers a planted target; negative control
fires null). No false positives — a dip/hit must survive as real structure, not a number. Report clean
NEGATIVE honestly. Distinguish "consistent-with" from "evidence-of". Do NOT re-run any ledgered lane.
Harness blocks subagent .md writes → agents RETURN findings as text; parent persists them.

## Honest prior
This will very likely NOT solve LP2 (the cipher is math-locked). Its realistic wins: (1) name the exact
authoring toolchain/font → narrows the maker; (2) find or exclude a font/sub-pixel data channel that only
exists in a rendered PDF; (3) resolve the 3 random blobs' cipher class; (4) an illustration-based
attribution lead; (5) reopen any falsely-closed lane. That is meaningful active progress on understanding
and attribution even if the runes stay locked.
