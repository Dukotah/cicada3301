# Round 33 / I2 -- Construction axis beyond {1, 2, free}  -- PREREG
Dated 2026-10-29, written before any output file exists.

Aiming Test.
- Q1 recognizer: plant each construction (reset_per_page, reset_per_line, skip_by_k k=3,4,5) in EN_MODERN and
  EN_NOVOWEL (R32 I1 testhalves_lite windows, seeds 9000+s, key = beam_v2.sha_ctr_key, supp 0.83) and decode with
  driftbeam relations 1 / 2 / free via beam_v2 (R32 I1 grid). "Represented" = median rune recovery >= 0.85 over 20 plants.
  Page-length plants = two consecutive REAL LP2 pages (page map from round10/L2-map mapcommon.parse(): 55 pages,
  12,956 runes; pair (2s mod 54, +1)); line resets use the real line lengths of those pages. L=120 plants use the
  real line map for per-line; per-page is invisible at L=120 by construction and is run only at page length.
  Extra control column: "oracle-segmented" = decode each segment separately with relation 1 from key offset 0
  (tests whether a reset construction is representable by SEGMENTING rather than by a new relation).
- Q2 prior: ciphertext doublet rate over 30 random (key, plaintext-window) draws at LP2 length 12,956, EN_MODERN,
  vs LP2 observed 0.66384 %. Match quality = |rate - 0.66384|. Controls keyskip1, skip_by_two.
  Caveat pre-stated: suppression strength 0.83 was itself fit to LP2; every output-side filter construction with that
  strength is expected to land near 0.6-0.85 %, so the doublet rate may not DISCRIMINATE among them.
- Q3 bounded: ~1,300 decodes, no key space. Q4: key space none; transition model = the axis; register EN_MODERN+EN_NOVOWEL.
- Q5 kill: if no new construction has match error <= 2x skip_by_two's match error, stop (no relations). Rule is
  applied literally as "err_new <= 2 * err_skip_by_two" (a better match than skip_by_two passes). Passing earns a
  relation only if ALSO unrepresented (median recovery < 0.85 under all of relation 1, 2, free, and v3 if present)
  AND not rescued by the oracle segmentation column being the only route (then it is reported as "segmentation, not relation").
- Not run: the panel adjudicator (recovery is the decoder-side criterion; adjudicator power per register is R32 I2's).
- No git; nothing outside this directory is edited.
