# Campaign XIII — The Armada (wide keytext sweep + fresh external OSINT)

_2026-07-07. 13-agent Workflow (`analysis/campaign13/`, ~0.57M tokens, 82 keytexts
tested). Two fronts: burn down the one falsifiable open avenue (untried public
keytexts) at scale, and refresh the external picture (state of the puzzle, the AN END
hash, attribution/key). Every finding below was adversarially checked; any lane
scoring near threshold would have been independently re-verified (none did)._

## Front 1 — 82 never-tested keytexts as running keys: **clean null**

Ten thematic lanes each fetched and tested a distinct net of primary sources that had
**never** been run against LP2, through the validated `attack.py runningkey` (all
offsets, both signs, ±Atbash, per page; threshold −5.2, English ≈ −4.0…−4.4). Sources
verified by title/author before use; nothing on the prior-campaign list re-run.

| lane | # texts | best score | best-scoring keytext |
|---|---|---|---|
| mysticism_poetry | 8 | **−5.809** | Dark Night of the Soul (St John of the Cross) |
| hermetica | 8 | −5.967 | Splendor Solis (Trismosin) |
| occult | 9 | −6.019 | The Enochian Calls/Keys (Dee & Kelley) |
| kabbalah_gnostic | 7 | −6.020 | Pistis Sophia |
| norse_runic | 9 | −6.040 | Heimskringla (Laing) |
| scripture | 8 | −6.050 | The Koran (Rodwell) |
| cypherpunk | 7 | −6.077 | The Trial (Kafka) |
| english_canon | 9 | −6.089 | Shakespeare's Sonnets |
| math_science | 10 | −6.155 | The Foundations of Science (Poincaré) |
| philosophy | 7 | −6.186 | Beyond Good and Evil (Nietzsche) |

**82 texts, 0 over threshold, best −5.809 — ~0.6 below the −5.2 gate and ~1.4 below an
English break.** No lane reported a hit, so the adversarial-verify phase found nothing
to check. Representative eliminated works (full list in the workflow journal):
Corpus Hermeticum / Divine Pymander, The Kybalion, the Chymical Wedding, the complete
Crowley *Liber* set (Book of Lies, 777, Book of Thoth, Goetia), Eliphas Levi, the
Golden Dawn, the Book of Enoch, Sepher Yetzirah, the Zohar, Pistis Sophia, the Koran,
the Upanishads, the Poetic & Prose Eddas, Havámál, Milton's *Paradise Lost*, the
complete Carroll, Plato's *Republic*, Spinoza's *Ethics*, Euclid's *Elements*, Newton's
*Principia*, the Cypherpunk/Crypto-Anarchist manifestos, Kafka, Rumi, Tagore, and more.

This is the mechanistically expected outcome — Campaign IV proved any natural-English
running key injects ~3.3% doublets that LP2 lacks — but it **enumerates 82 more named,
sourced eliminations**, shrinking the "we can't say we tried all keytexts" gap by a
large, documented margin.

## Front 2 — fresh external OSINT (2022–2026), three angles

**A. Current state — STILL UNSOLVED, independently confirmed.** As of 2026, no Liber
Primus page has been credibly solved since 2017; the ~17 solved pages were all cracked
2014–2017. No credible key reveal, no method disclosure, and **no authenticated 3301
activity since the April 2017 PGP "Beware false paths" message.** Documented 2024 GPT-4
attempts produced no breakthrough (useful only as a plaintext scorer) — corroborating
this project's stance that "AI solved Liber Primus" claims should be distrusted.
- **New (transcription, not decryption):** by late 2024 the community consolidated the
  full runic book to **~75 pages** (Tumbleson), ~4 more than the 0–55 set attacked here.
  This is ciphertext completeness, *not* new solves — but it is a genuine **coverage gap**
  (see open item below).

**B. The "AN END" deep-web hash — cold, and two popular theories debunked.** No preimage
or page ever found. This armada's angle actually **closes a long-shot this repo had left
open**: CT-log brute-forcing is **not viable** (CT logs hold CA-issued cert domains, not
page contents or v2 onions — no relevant candidates exist). It also debunks the 2024
"hash-is-a-v2-onion payload" theory (the *standard* first-80-bit base32 of the hash is
`gy3hoy5lon4dy6xs`, which does **not** match the theory's cherry-picked
`gy3hoy2zizvuzvdb`), and the "ed25519/v3 onion" theory (anachronistic — v3 didn't exist
until 2017; AN END is 2014). Tor v2 was removed in Oct 2021, so any original target is
permanently unreachable. Only tractable path left = a finite lookup of archived v2-onion
corpora (low prior), not a brute force.

**C. Attribution / external key — negative.** No credible external key or keytext, no
published method reproducing any unsolved page, no authenticated leaked artifact
2023–2026. The only new items: Schoenberger's March-2023 self-attribution (**fails the
PGP gate** — no signature, no reference to key 7A35090F) and a 2025 paper noting that
SHA-1-based signatures make *future* purported 3301 messages forgeable (does **not**
break the verified 2012–2017 chain). Neither is probative.

## Net for Campaign XIII
- **+82 named/sourced keytexts eliminated** — the largest single expansion of the
  falsifiable frontier to date; still 0 breaks (best −5.809).
- **CT-log avenue closed** (was a documented long-shot) — non-viable by construction.
- **Two AN END onion theories debunked**; trail confirmed cold.
- **Independent confirmation** LP2 remains unsolved in 2026 with no key ever published.
- **One genuinely new open item surfaced** (below).

## New open item (worth a future pass)
The runic corpus has grown to **~75 pages** in the community transcription since this
project ingested pages 0–55. Verifying and, if needed, ingesting the ~4 additional
transcribed pages is the one concrete new coverage gap — not a solve path, but the
statistics and any future attack should run over the *complete* current page set.
(The falsifiable-keytext avenue remains formally open but is now much narrower; extend
it trivially by adding IDs to `analysis/campaign12/fetch_keytexts.py`.)
