# Lane C — CONFLICTS

Contradictions inside the community record retrieved by this lane. **Nothing here is
resolved.** Both sides are recorded with the file and line that carries them.

Branch `corpus-sweep`. Lane close 2026-08-19/20 UTC.

A standing caution that applies to every entry: **community sources are self-reported.**
An IRC nick claiming insider status is evidence *that the claim was made on that date*, and
nothing more. That is still worth having — the claims themselves are dated primary record.

---

## C-C-01 — Self-claimed 2013 "brood" insiders: what they say vs. what the repo's
falsifier requires

**Source:** `irc/2013_winners-leak_irc-log.txt` (820 lines).
Provenance: `https://raw.githubusercontent.com/cicada-solvers/The-Complete-Cicada3301-Archive/master/2013/additional%20files/Winners%20leak/logs%20from%20IRC%20winners%20leak.txt`,
retrieved 2026-08-19T22:24:14Z, HTTP 200. The file contains **two separate sessions**:
a Freenode webchat log of 2013-05-06 and an earlier log of 2013-02-13.

Claims made in it:

| line | speaker | claim |
|---|---|---|
| 5 | `guy1` | "Actually I WAS a 3301 brood member" |
| 15 | `guy1` | on the pastebin warning: "y, they gave multiple" |
| 31 | `guy1` | "They gave us access to a board in the tor network" |
| 33 | `guy1` | asked to share the link: "it's down now" |
| 77 | `Elephant` | "we were brood 0H and they suggested, that there were more" |
| 127 | `Elephant` | "I think she was in the brood of 2011" |
| 245–249 | `guy3` (2013-02-13) | "3301 recruits in broods" / "we were brood 0H" / "who guided the brood" |

**The conflict.** This repository's own falsifier for the Campaign XIX attribution bound
(recorded in `liber-primus/analysis/round10/L6-archives/reddit_fetch.log`) is explicit:

> the Campaign XIX bound survives UNLESS this log contains a first-person claim that 3301
> distributed CIPHER MATERIAL OR KEYS to insiders. 'they gave us access / a wiki / a git'
> does NOT meet that bar.

Read against that standard, **the log does not clear the bar.** The strongest first-person
statement is access to a Tor board (line 31), which the falsifier names as insufficient.
No line in the file describes receiving cipher material, a keytext, or a decryption key.

**Recorded, unresolved:** the log is nonetheless a genuine 2013-dated first-person insider
claim, and it *is* the material the falsifier was written to be tested against. Anyone
re-opening the Campaign XIX bound should read the file rather than this summary. Note also
that the log's own participants dispute each other in-channel — line 61 (`Zebra`) and
line 156 (`Elephant`, "Whoever wrote that was atleast in a brood and why should he lie
about the rest?") are the two sides of a live credibility argument, in 2013, among people
who were there.

**Independent corroboration status: none.** The claims are not signed, not corroborated by
any 7A35090F-signed message, and the one verifiable artifact offered (the Tor board link)
was already down when asked for.

---

## C-C-02 — "brood 0H" vs. "brood 1H" vs. "brood of 2011": the numbering does not agree

Within the same file:

- line 77 (`Elephant`, 2013-05-06): "we were **brood 0H**"
- line 246 (`guy3`, 2013-02-13): "we were **brood 0H**"
- line 127 (`Elephant`): "I think she was in the **brood of 2011**" — a brood predating the
  2012 puzzle entirely
- line 643 (`guy3301 :-)`): "i bet 1000% this game will end in **Brood 1H**"
- lines 632–636: the same speaker is quoting *entomological* Magicicada Brood II material
  (the 2013 US Eastern Seaboard emergence) as if it were puzzle-relevant

So "brood" is used in at least three incompatible senses in one log: an insider cohort
label (`0H`), a speculative future cohort (`1H`), and the literal cicada-biology brood
cycle. The repository's own records use `b.0h` as a cohort label
(`PAPERS-ARCHIVE.md` notes Wanner's account naming handles "Sage", "Tekk" in brood b.0h).

**Not resolved.** The conflict matters because "brood 0H" is used elsewhere in this repo as
if it were a stable identifier. On this evidence it is a term the 2013 community itself
used loosely.

---

## C-C-03 — A "brood of 2011" claim conflicts with the standard 2012 origin

Line 127 asserts a brood existed in **2011**. The documented public timeline in this
repository (`research/01-origins-2012.md`) starts with the 2012-01-04 4chan post. If a 2011
cohort existed, the public record begins after the recruitment did.

**Both sides on the record, unresolved.** No corroborating 2011-dated artifact was
retrieved by this lane. The claim is single-sourced, hearsay ("I *think* she was…"), and
made in 2013 about two years earlier.

---

## C-C-04 — Two mailing-list corpora disagree about what is publicly available

`mailinglists/metzdowd-cryptography/` holds **19 monthly archives** that returned HTTP 200
while `_logs/failed.jsonl` holds **56 URLs of the identical form that returned HTTP 404**,
covering the same 2011–2015 window. The two sets interleave by month.

This is not a Cicada conflict; it is a conflict about **what the public pipermail index
actually contains**, and it must be resolved before anyone treats an absent month as
evidence that no Cicada-related traffic occurred in it. A 404 here means "this constructed
filename does not exist", not "this month was empty" — see `GAPS-C.md` C-G-04.

---

## C-C-05 — `cicada3301.boards.net` is simultaneously "dead archive" and "live site"

Corpus `GAPS.md` lists `cicada3301.boards.net` among the missing sources to recover *from
archives*. This lane found the board **still live and serving**, with a `robots.txt`
(`User-agent: *`) that permits `/thread/` and `/board/`.

Both records are now held and they do not agree:

- `forums/boards_net/` — 202 files of Wayback captures (206 archive rows).
- `forums/boards_net_live/` — 79 files: 63 of 64 live threads plus 15 board indexes,
  fetched directly 2026-08-19.

**Unresolved and worth resolving:** whether the live board's current thread text matches
its archived captures. A live forum can be edited after the fact; the archive captures are
the only check on that. This is the same question Lane D answered for files
(`CONFLICTS-D.md` D-C-01) and it has **not** been answered for these threads. Both corpora
are on disk, so the diff is cheap and nobody has run it.

---

## C-C-06 — The pre-existing Reddit corpus was once scored as EMPTY, and that scoring was wrong

Recorded because it is a conflict between two states of this repository's own record, and
the earlier state may still be cited somewhere.

`liber-primus/analysis/round10/L6-archives/pull_reddit.py` documents in its own docstring
that an earlier script, `analysis/round10/RECON-C/fetch_recon_c.sh`, paginated the
arctic-shift API with `after=0`, which the API rejects. It therefore recorded **0 rows**,
and *the corpus was scored as empty on that basis*.

The corpus is not empty. Measured in this lane
(`reddit/HELD_DUMPS_STATS.json`): **29,871** `Cicada` comments, **7,160** `Cicada` posts,
**660** `a2e7j6ic78h0j` comments, **192** `a2e7j6ic78h0j` posts.

**Consequence:** any conclusion anywhere in this repository that rests on "the Reddit
corpus is empty" is void. Two files genuinely are near-empty —
`cicada3301_comments.jsonl` (0 bytes) and `cicada3301_posts.jsonl` (1 record) — and
whether *those* are truly empty or a second instance of the same class of bug is **not
established** (see `GAPS-C.md` C-G-11, unknown #3).
