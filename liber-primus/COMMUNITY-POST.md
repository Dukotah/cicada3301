# Draft community post (r/codes, CicadaSolvers, r/cicada)

*Copy-paste and post under your own name. Tone is deliberately humble + skeptical —
this audience is expert and (rightly) allergic to overclaiming. Don't claim a solve.*

---

**Title:** Liber Primus: verified image provenance + a reproducible map of what's
ruled out (open-source repo + dataset + tooling)

I've put together an open, reproducible toolkit and writeup for the unsolved
Liber Primus (LP2) pages. I'm **not** claiming a solve — the opposite. The point
is to (a) hand the community some things I think are genuinely useful, and (b)
save people from re-running the dead ends I re-ran. Everything is code you can
check; please poke holes in it.

**Repo:** https://github.com/Dukotah/cicada3301 →
[`liber-primus/SOLVERS-DOSSIER.md`](https://github.com/Dukotah/cicada3301/blob/master/liber-primus/SOLVERS-DOSSIER.md)

**What I think is actually useful:**

1. **Verified image provenance.** The circulating relikd/LiberPrayground image set
   is **byte-identical to the archived onion7 dump** — 56/56 SHA1 match the hashes
   published on the Internet Archive item `ky2khlqdf7qdznac.onion`. So if your
   copies match those hashes, you can trust them for stego/coefficient work.
   Authentic-original fingerprint: 2400×3600, 400 DPI, uniform "Artifex Software
   2011" ICC (Ghostscript output). Re-saved/Imgur copies will differ — don't use
   them for OutGuess/LSB. (Hash table in `analysis/stego/provenance.json`.)

2. **A canonical, machine-readable dataset** (`dataset/liber_primus.json`):
   gematria, per-page runes + transliteration + indices, the verified image
   hashes, solved-page keys, a ruled-out registry, and the statistical profile —
   one file to build on.

3. **A self-validating rig + a "test your idea" tool.** `tests/validate.py`
   reproduces every solved page (atbash / shift / Vigenère DIVINITY /
   FIRFUMFERENFE / totient). `lp-try --key YOURKEY` (or `--keystream totient`)
   scores any hypothesis against all pages with a built-in sanity gate, so you
   don't fool yourself on a near-miss.

**What I re-ran and got nothing from (so you don't have to):** every periodic key
(len 1–40, both directions, +atbash), running keys from the referenced texts,
number-theoretic keystreams (primes/totient/φ-iter/gaps/cumsums/fibonacci),
autokey, first-difference/integral, page-on-page in-depth, fractionation (bifid),
substitution, transposition-only, block/permutation (Lehmer) decode, and
no-repeat/collision inversion decodes. Each is in the repo with a reproduce command.

**A couple of things I checked that I haven't seen written up:**
- The no-repeat "no equal neighbours" property (doublet rate 0.66% vs 3.45%) is
  **structural, not a reading-order artifact**: file order is the unique
  doublet-suppression minimum; every columnar transposition restores doublets
  toward random.
- That suppression is **continuous across the entire book** — it holds across
  word/clause/line *and page* boundaries (page-join doublet rate = 0.0000). So the
  keystream does **not** reset per page; there's no boundary to mount an in-depth
  attack on.
- The ᚠ-interrupter counts per page
  (`14,13,7,7,7,8,3,1,8,11,7,14,12,12,2,7,...` — full list in the repo) match no
  standard integer sequence I tested, and the F/not-F mask isn't hidden ASCII.
- AI-vision re-transcription of the runes is **not** reliable (I tried; ~0.145
  alignment) — don't trust LLM "re-reads" of whole pages.

**My honest read:** from the ciphertext alone the unsolved pages look
one-time-pad-class (perfect IoC flatness ⇒ full-length keystream, plus the
deliberate no-repeat rule), i.e. underdetermined without the key. If that's right,
the realistic path is **external** — most likely the AN END deep-web page
(`36367763…c2a8b4`), which no one has found.

If I've made an error anywhere, I'd genuinely like to know — it's all reproducible.
And as always: PGP-verify any "key" claim against 7A35090F.
