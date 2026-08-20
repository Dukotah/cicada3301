# Lane F — GAPS

What Lane F could not retrieve, and what remains unsearched. Two rules held throughout:

1. **No paywall was bypassed.** Paywalled items are recorded here as citation + DOI +
   whatever metadata is publicly available, and left unretrieved.
2. **No citation or DOI was invented.** Every citation below was resolved through the
   **DBLP** search API and then verified against the **Crossref** API
   (`meta/dblp_paywalled_queries.json`, `meta/paywalled_citations.json`). Where an abstract
   is not publicly deposited, this file says so rather than paraphrasing one.

---

## F-G-01 — PAYWALLED: the canonical running-key cryptanalysis papers (Cryptologia)

**Cryptologia** (Taylor & Francis) is the other principal venue for historical
cryptanalysis alongside HistoCrypt, and unlike HistoCrypt it is closed access. DBLP marks
every entry below `access=closed`. These are the papers the held ACL/HistoCrypt material
points back to.

| citation | DOI | abstract |
|---|---|---|
| Craig Bauer; Christian N. S. Tate. **A Statistical Attack on the Running Key Cipher.** *Cryptologia* 26(4):274–282 (2002). | [10.1080/0161-110291890939](https://doi.org/10.1080/0161-110291890939) | **not publicly deposited** — Crossref returns no abstract for this DOI; the abstract sits on the publisher landing page behind the paywall. Not reproduced or paraphrased here. |
| Craig Bauer; Elliott J. Gottloeb. **Results of an Automated Attack on the Running Key Cipher.** *Cryptologia* 29(3):248–254 (2005). | [10.1080/01611190508951301](https://doi.org/10.1080/01611190508951301) | not publicly deposited (as above) |
| Alexander Griffing. **Solving the Running Key Cipher with the Viterbi Algorithm.** *Cryptologia* 30(4):361–367 (2006). | [10.1080/01611190600789117](https://doi.org/10.1080/01611190600789117) | not publicly deposited (as above) |

**Why these three matter here.** The held Reddy & Knight (ACL 2012) paper is the modern NLP
treatment of running-key decoding, but these are the papers that established the
*statistical* attack and the *Viterbi/HMM* attack on running keys specifically. The
unsolved Liber Primus pages behave as a running key over a near-random keytext; if there is
a published bound on when a running-key attack succeeds as a function of keytext
predictability, it is in this line of work.

**Route in:** institutional library access to Taylor & Francis, or interlibrary loan by DOI.
Do not attempt any other route.

## F-G-02 — PAYWALLED: runic cryptography in Cryptologia

| citation | DOI | abstract |
|---|---|---|
| O. G. Landsverk. **Cryptography in Runic Inscriptions.** *Cryptologia* 8(4):302–319 (1984). | [10.1080/0161-118491859141](https://doi.org/10.1080/0161-118491859141) | not publicly deposited |
| Ben Johnsen. **Cryptography in Runic Inscriptions: A Remark on the Article "Cryptography in Runic Inscriptions" by O. G. Landsverk.** *Cryptologia* 25(2):95–100 (2001). | [10.1080/0161-110191889833](https://doi.org/10.1080/0161-110191889833) | not publicly deposited |

These two are a **published dispute** (Johnsen is explicitly a rebuttal of Landsverk), which
is worth more than either alone: it is the historical-runic analogue of the Liber Primus
signal-vs-noise question. The held open-access substitute is Wase, *The Upplandic Non-Lexical
Rune Stones: Ciphers or Nonsense?* (HistoCrypt, DOI 10.3384/ecp183168).

## F-G-03 — PAYWALLED: autokey cryptanalysis in Cryptologia

| citation | DOI | abstract |
|---|---|---|
| Otokar Grošek; Eugen Antal; Tomáš Fabšič. **Remarks on breaking the Vigenère autokey cipher.** *Cryptologia* 43(6):486–496 (2019). | [10.1080/01611194.2019.1596997](https://doi.org/10.1080/01611194.2019.1596997) | not publicly deposited |
| Jack Levine; Michael Willet. **The Two-Message Problem in Cipher Text Autokey. Part I.** *Cryptologia* 3(3):177–186 (1979). | [10.1080/0161-117991854016](https://doi.org/10.1080/0161-117991854016) | not publicly deposited |
| Jack Levine; Michael Willet. **The Two-Message Problem in Cipher Text Autokey. Part II.** *Cryptologia* 3(4):220–231 (1979). | [10.1080/0161-117991854115](https://doi.org/10.1080/0161-117991854115) | not publicly deposited |

**Nothing on autokey cryptanalysis was retrieved in open access.** The autokey family is one
of the cipher families corpus `GAPS.md` G-08 names, and it is currently represented in the
held corpus by **zero** papers. This is the largest single subject-matter hole remaining.

---

## F-G-04 — SJSU ScholarWorks: 8 theses failed to download (0 bytes)

`meta/downloads.json` `_failures` records eight San José State University master's theses
that returned **0 bytes** from `scholarworks.sjsu.edu/cgi/viewcontent.cgi` — the Digital
Commons `viewcontent.cgi` endpoint requires a browser session / referer that the fetcher did
not supply. These are **open access**; the failure is mechanical, not a paywall.

- *Cryptanalysis of Classic Ciphers Using Hidden Markov Models* (2015) — `article=1408&context=etd_projects`
- *Cryptanalysis of Homophonic Substitution Cipher Using Hidden Markov Models* (2016) — `article=1505&context=etd_projects`
- *Classifying Classic Ciphers using Machine Learning* (2019) — `article=1699&context=etd_projects`
- *Generative Adversarial Networks for Classic Cryptanalysis* (2021) — `article=2034&context=etd_projects`
- *Analysis of the Zodiac 340 cipher* (2008) — `article=4566&context=etd_theses`
- *Efficient Attacks on Homophonic Substitution Ciphers* (2011) — `article=1195&context=etd_projects`
- *Cryptanalysis of the Purple Cipher using Random Restarts* (2015) — `article=1428&context=etd_projects`
- *Malware Detection using the Index of Coincidence* (2017) — `article=1507&context=etd_projects`

Also failed: *Genetic algorithms in cryptography* (RIT, 2004),
`https://scholarworks.rit.edu/theses/5456` — returned a 35,447-byte landing page, not a PDF.

**Note on the titles above:** these are the titles as recorded in the lane's own download
plan. They have **not** been re-verified against the repository listing in this pass, so
treat them as retrieval targets rather than as citations until the PDFs are in hand.

**Route in:** fetch the *landing* page first
(`https://scholarworks.sjsu.edu/etd_projects/<n>/`), read the canonical PDF link from it,
and send a `Referer` header. This is the standard Digital Commons pattern and closes all
eight.

## F-G-05 — IACR ePrint was searched but nothing was downloaded

`PROGRESS.md` records that the IACR ePrint search page was fetched; `meta/downloads.json`
contains **no ePrint item**. ePrint is fully open access, so this is pure unfinished work,
not a block. Worth targeting: modern treatments of keystream distinguishers and
indistinguishability, which bear directly on the derived-vs-true-pad question.

## F-G-06 — Semantic Scholar was abandoned mid-sweep

`PROGRESS.md`: Semantic Scholar "429'd on nearly every call and was killed", and OpenAlex
(30 queries) was used instead. OpenAlex has good coverage but a different ranking, so the
discovery sweep is **single-source for anything OpenAlex ranks poorly**. Semantic Scholar's
citation graph in particular was never used to walk *forward* from Reddy & Knight (2012) —
which is the obvious way to find work that cites the canonical running-key attack.

**Route in:** Semantic Scholar's API with a free key (`api.semanticscholar.org`), or
OpenAlex's `cited_by_api_url` on the Reddy & Knight record.

## F-G-07 — Subject areas from G-08 with thin or no coverage

Measured against the list corpus `GAPS.md` G-08 sets out:

| G-08 subject | held | status |
|---|---|---|
| runic Vigenère variants | 2 open-access runic papers | **thin** — neither is about Vigenère over runes; the Cryptologia pair (F-G-02) is unretrieved |
| totient-indexed shifts | **0** | **NOTHING HELD.** No search in this lane returned anything on totient- or φ-indexed shift schedules. It may simply not exist as a literature. |
| autokey cryptanalysis | **0** open access | **NOTHING HELD** — see F-G-03 |
| running-key cryptanalysis | 2 (Reddy & Knight 2012; HistoCrypt 2020) | adequate open-access coverage; the 3 Cryptologia foundations unretrieved |
| book ciphers | **0** | **NOTHING HELD.** Book-cipher cryptanalysis as such was not retrieved; the closest held item is the Gutenberg/hexagram keytext-search paper. |
| interrupter / null-insertion schemes | 1 (Szarka, 17th-c. Germany) | **thin** — one historical paper, no cryptanalytic treatment |
| OTP indistinguishability / derived vs true pad | 5 | **the best-covered area**; see `REPORT-F.md` |
| extreme-value statistics for keyspace search | 3 | adequate |
| anti-repeat constrained sequences (Smirnov / Carlitz) | 5 | adequate |

**Two subjects are at literally zero: totient-indexed shifts and book ciphers.** For
totient-indexed shifts that may be the true state of the literature — it is a Cicada-specific
construction — but that should be established by a deliberate search, not assumed from one
lane's failure to find anything.

## F-G-08 — The press half was not extended

`PROGRESS.md` step [t6] planned a press-half extension covering documentaries, podcasts,
interviews, attribution claims and the PGP 7A35090F signature status. **None of it was
done.** `corpus/F-press-academic/press/` is empty; the press half of the bibliography is
entirely the pre-existing mirrored archive. Specifically missing: the *Dark Web* / Cicada
documentaries, podcast episodes, and any interview published after March 2021 (the mirrored
archive's capture horizon — see `BIBLIOGRAPHY.md` half 2).

## F-G-09 — 24 press PDFs yield no source URL and 23 no capture date

Of 126 PDFs in the mirrored press archive, `press_reprov.py` recovered a source URL for 102
and a capture date for 103, with **88 yielding both**. The files that yielded neither are
listed individually in `BIBLIOGRAPHY-GENERATED.md`. For those, provenance stops at the
collection level (the verified `krisyotam/cicada3301` @ `1ccf9583b706` mirror) and their
original source URLs are **unknown**.

**Note on a discrepancy with the lane's own earlier log:** `PROGRESS.md` [t1] reports
**102/126** PDFs yielding *both* a URL and a date. This pass, with a re-implemented
extractor, gets **88/126**. The earlier run's output was never written to disk, so the two
cannot be reconciled; the lower figure is the one this lane can currently evidence, and
`meta/press_provenance.json` is the file that backs it. See `CONFLICTS-F.md` F-C-01.

## F-G-10 — Nothing in this lane was read, only retrieved

Stated plainly so it is not assumed otherwise: **no held paper has been read and applied to
this project's data.** `REPORT-F.md` says what each paper *would* change if applied, based
on its abstract and stated method. That is a reading plan, not a result. No claim anywhere
in this repository should cite a Lane F paper as having been *used*.
