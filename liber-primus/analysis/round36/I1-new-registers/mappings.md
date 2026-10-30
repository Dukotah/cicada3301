# Round 36 / I1 — alphabet mappings (the mapping IS the register)

> **SUPERSEDED (R36 X1):** the mapping code iterates Python sets (hash-seed-dependent order in the Hebrew mapper); see RESULTS.md "Correction". The documented letter rules below are the intended, deterministic mapping; P1's build_r36.py implements them deterministically.

All three are two-step and fully deterministic: (1) a corpus-specific romanisation to uppercase ASCII
(`mappings_r36.py`, function names below), then (2) the **unchanged** Round 32 step `detectors.text_to_runes(s, "EN")`:
fold K,Q->C, V->U, Z->S; every non-A-Z char is a word break (digraphs never straddle a break); then greedy
longest-match over the Gematria Primus transliterations (TH EO NG OE AE IA EA first, then single letters; J, X, W,
Y, H are runes in their own right). Consequence worth knowing: digraph runes appear by *spelling collision*, not
linguistic intent (e.g. Greek ἐάν -> EAN -> rune EA; Norse "ng" -> rune NG). That is the same behaviour every existing
register has. Mapping version used for the panel: **v1 for all three** (all passed the gate, so the v2 revision slot
was never used; v2 code exists in `mappings_r36.py` only as the pre-registered fallback and was NOT run).

## GREEK — `greek_html_text` + `greek_to_ascii(V=1)`
Corpus: Nestle 1904 GNT base text (27 xhtml books). Tags stripped, entities unescaped, NFD decomposed, lowercased, split
into words on non-Greek chars. Per letter: α A, β B, γ G (γ before γ/κ/ξ/χ -> N), δ D, ε E, ζ Z(->S), **η E** (no
long/short distinction), θ TH, ι I, κ K(->C), λ L, μ M, ν N, ξ X, ο O, π P, ρ R, σ/ς S, τ T, υ Y (**U** after α ε η ο:
αυ ευ ηυ ου -> AU EU EU OU), φ F, **χ CH** (-> runes C,H), ψ PS, **ω O**. Rough breathing on an initial vowel -> H
before it; initial ρ -> RH. Smooth breathing, accents, diaeresis and iota subscript are dropped. Letters with no rune:
none (every output letter maps). Vowel handling: all vowels kept, η/ε and ο/ω merged.
V=2 (unused fallback): η EA, ω OE, χ K, φ PH, υ U.

## HEBREW — `hebrew_osis_words` + `hebrew_to_ascii(V=1)`
Corpus: WLC (openscriptures/morphhb OSIS), Gen, Exod, Lev, Num, Deut, Josh, Judg. Words = text of `<w>` elements, "/" morpheme
separators removed, cantillation ignored (only U+05B0–05BB vowels, dagesh, shin/sin dots used). **Pointed (voweled)
romanisation**, so it is a pronounced-text register, not a bare-consonant one. Consonants: א (silent) and ע dropped; ב B, ג G,
ד D, ה H, ו W, ז Z(->S), ח H, ט T, י Y, כ ך K(->C), ל L, מ ם M, נ ן N, ס S, פ ף P, צ ץ TS, ק K(->C), ר R, **ש SH
(sin dot -> S)**, ת T. Vowels emitted after their consonant: patah/qamets/hataf-patah A, segol/tsere/hataf-segol E,
hiriq I, holam/hataf-qamets O, qubuts U, **sheva dropped**; **vav+holam -> O, vav+dagesh (no vowel) -> U**, otherwise W; yod
after an I/E vowel and word-final unpointed he are treated as vowel letters and dropped. Dagesh does not double letters.
Letters with no rune: none after the above (SH, TS are two-rune sequences; there is no CH/KH rune, ח is plain H).
V=2 (unused fallback): ע A, ח KH, vocal sheva -> E, פ without dagesh F.

## NORSE — `norse_html_text` + `norse_to_ascii(V=1)`
Corpus: eight normalised Old Norse saga pages from heimskringla.no (Egils, Eyrbyggja, Völsunga, Ynglinga, Gunnlaugs,
Hrafnkels, Gísla, Fóstbræðra). Text = content between `mw-parser-output` and `printfooter`, after the ► language-selector
line, tags stripped. Lowercased, NFC. **þ ð -> TH**, æ ǽ -> AE, œ ø ǿ **ö -> OE**, ǫ ȯ ó -> O, á A, é ę E, í I, ú U, ý Y;
any other accented letter loses its accent; j stays J (rune J); v->U, z->S, k->C by the common fold; ng -> rune NG
by the greedy parse. Letters with no rune: none. Digits/punctuation are word breaks.
V=2 (unused fallback): ð D, ö O, ø O, ǫ OE.

## Honest limits
These romanisations are *a* convention, not the only one a puzzle author could use. The panel detects Greek/Hebrew/Norse
plaintext written by *these* conventions (plus any convention whose rune trigram statistics are close to them); a
different convention (e.g. unpointed consonant-only Hebrew, η->Ē, þ->D) is a distinct register and remains uncovered.
Norse is Guðni-Jónsson-normalised saga prose (13th c.-style orthography), not runic-inscription Old Norse.
