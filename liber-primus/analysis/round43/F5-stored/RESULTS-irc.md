# Round 43 — Lane F5b RESULTS (archived IRC/community logs, key-material hunt)

**Verdict: FOUND (one key-candidate, with caveat) — plus CLEAN on the two headline questions.**

Provenance classes used: **A** = Cicada-signed (0x7A35090F), **B** = Cicada-served (bytes delivered by a 3301-controlled
server/steg channel, unsigned), **C** = solver-recorded observation of a Cicada-controlled process, **D** = solver
speculation (context only). Only A/B count as key-candidate outright; C is flagged with caveat.

---

## 1. KEY-CANDIDATE (new to this project's working record)

### 1a. The onion-2 growing-string TIMING CHANNEL (class B values / class C timestamps) — FOUND
cu343l33nqaekrnw.onion (Jan 6-7 2014) appended 1 byte every n×5 minutes for ~23 h until the 256-byte string
`634292ba...442846` was complete. The byte VALUES are Cicada-served (they equal the final string, which is in our
record); the INTER-ARRIVAL INTERVALS were chosen by Cicada's server and are structured numeric data published by the
entity that our record reduces to one sentence ("multiples of five"). No prior lane ever held the interval sequence.

Recovered and stored this session (both pastebins still live 2026-11-03):
- `onion2-timing_BotSottile_qn8jmPJr.txt` — 275 lines, #cicada3301 IRC bot log ("Starting to poll the onion every
  10 seconds..."), per-byte arrival timestamps (GMT+1) from len 159 through the FINAL byte (`46`, len 256, 05:10).
- `onion2-timing_Cripion101_5bTLHqCN.txt` — solver table, 31 consecutive samples:
  minute / elapsed / byte, e.g. `00 20 25 35 50 05 15 20 45 00 15 20 40 45 05 10 25 30 40 15 25 30` ↔
  `26 e1 97 83 99 56 92 1d ab 29 72 4c d4 8e 1a 81 fc 9b ab 35 65 f7`, plus a second 9-sample block
  (`51 3e 3e 36 8c d0 32 7b 47`).
- Two more samples are in the locally-held wiki export (`corpus/C-community/wikis/uncovering-cicada/
  export_cur_00120.xml` "MAIN CICADA 3301 2014 PAGE PART 2" — a 20-column clock/interval/interval÷5/byte table —
  and `export_cur_00140.xml` — a 25-sample sequence `10 30 10 15 05 05 10 15 05 05 20 05 10 15 15 10 05 25 15 15
  05 20 05 20 05`).

Exact candidate key stream (interval÷5, Cripion101 31-sample run):
`4 1 2 3 3 2 1 5 3 3 1 4 1 4 1 1 3 2 7 2 1` ... (full table in stored file; alignment byte↔interval must be
re-derived from BotSottile's absolute timestamps before use).

**Caveat (why not auto-certified):** timestamps are class C — solver-recorded, partially overlapping, one dataset
GMT+1. Coverage is incomplete (~60-100 of 256 bytes across the four sources). A follow-on lane should merge
BotSottile+Cripion101+wiki tables, check mutual consistency, and test interval÷5 as a key stream against the LP
instrument. Flag-for-oracle per HUMAN-ORACLE.md before any certification.

### 1b. The disputed trailing "57" on the Jan-11 onion-3 hex (class B, UNVERIFIABLE) — context only
IRC #33012014, 2014-01-11 14:36-14:51 (held locally: `corpus/A-primary-artifacts/cijhho123/2014/Websites/ONION 3/
We dont have legit html of onion 3 v2 string logs.txt`): two captures of the 4,302,741-byte hex delivered at
`Date: Sat, 11 Jan 2014 22:19:20 GMT` circulated — gjvc's curl capture WITHOUT a trailing ASCII "57" and
BurkeAndHare's dragonstudios.tk capture WITH it; one witness (Ror) claims he watched "57" get appended live
("first it was without 57, then after few minutes with 57" — note 0x3301 = 13057 decimal, and LP's last page is 57).
Both original capture URLs are now unrecoverable (wayback: parked page / 404 only). The surviving cijhho/krisyotam
copy (md5 f2f0841a8fb4306fc5d1f648e2e33e0b) ends `...e0ffd8ff` — the WITHOUT-57 variant. Under the strict provenance
rule this stays CONTEXT ONLY (single witness, captures lost, same-Date-header anomaly suggests one paste was derived
from the other), but it is recorded here because if "57" was real it is a Cicada-appended clue byte absent from
every modern record.

---

## 2. CLEAN findings (the two headline questions)

### 2a. Pages 0-57 ordering/delivery — CLEAN, record CONFIRMED byte-exact
Two independent Cicada-served copies agree exactly with `raw/2014.md`:
- micheloosterhof/cicada-2014 `stage11/ky2khlqdf7qdznac.onion/index.html` (fetched raw this session,
  md5 `aaf1aa4d3fc0440c3a62eed5452c2876`, 1,640 bytes): `<title>133</title>`, `<div id="331">`, sequential
  `<img src="0.jpg">` ... `<img src="57.jpg">`, nothing else. No runes.txt was served by the onion (runes.txt is a
  solver transcription artifact, rtkd/iddqd). No alternate numbering, no directory listing, no reordering.
- Locally-held wiki export of "What Happened Liber Primus (Post 2014)" quotes the identical source plus the same
  thttpd/2.25b headers (Last-Modified Wed, 02 Apr 2014 08:33:19 GMT) and the 404/telnet `Apache Server at
  127.0.0.1 Port 5243` oddity — all already in our record.
- `message.txt.asc` fetched raw (md5 `6808ed6409c243aacfe8a0f077dba606`): trailing-space counts measured per line =
  **2, 3, (5 leading + 7 trailing on the onion line), 11, 13, 17, 23, 29, 31, 37 — 19 absent** — confirms the
  record's annotation at byte level.

### 2b. Unknown Cicada-authored messages — NONE FOUND beyond the release record
Swept: 500 local wiki Talk: pages (ns1), wiki content exports (89 XML files), cijhho Titanpads (22 files),
2013 winners-leak IRC log (already adjudicated C-C-01..03), #33012014/#cicada3301 IRC fragments, boards.net forum
mirror, 2017 pastebin. Every PGP-signed block encountered is already in raw/{2012..2017}.md. The 2026 Zenodo
"Final and Complete Translation" (record 18199474, Bruno Becker) is class D — unverified solver claim, no entity
material.

---

## 3. Record-gap fills (not new to the PROJECT, new to the raw release record)

Our `raw/2014.md` has two "TODO: missing" placeholders; both strings exist byte-complete in the already-held corpus:
- Jan-11 server-status replacement hex (delivered 03.jpg/04.jpg): `corpus/A-primary-artifacts/cijhho123/2014/
  additional docs/Titanpads from time of solving/the Apache server status page changed once again to display a new
  hexadecimal string.txt` (4,373,525 B incl. HTTP headers `Last-Modified: Sat, 11 Jan 2014 22:07:12 GMT`,
  `ETag "d3e7-41a795-4efb910854400"`, `Content-Length: 4302741`).
- Onion-4 Jan-29 signed gzip hex (`1f8b...`, "data.out"): same dir, `the fourth onion hex string.txt` (5,233,438 B).
- Also absent from raw/2014.md verbatim: the onion-4 image02 outguess raw ciphertext (class B, unsigned):
  `For those who have fallen behind:` / `TL BE IE OV UT HT RE ID TS EO ST PO SO YR` /
  `SL BT II IY T4 DG UQ IM NU 44 2I 15 33 9M` / `Good luck.` / `3301` — record holds only the decoded form; note the
  decode leaves an unconsumed numeric residue `9133` after the onion address.
- The three 58152-byte "non-ASCII outguess" blobs the 2014 IRC chased are already adjudicated as OutGuess
  capacity-length false positives (`liber-primus/analysis/stego/STEGO-VERDICT.md`); nothing here reopens that.

## 4. Files written
- `analysis/round43/F5-stored/irc-log.md` (query log)
- `analysis/round43/F5-stored/RESULTS-irc.md` (this file)
- `analysis/round43/F5-stored/onion2-timing_BotSottile_qn8jmPJr.txt`
- `analysis/round43/F5-stored/onion2-timing_Cripion101_5bTLHqCN.txt`
