#!/usr/bin/env python3
"""Build confidence-weighted consensus + disagreement map.

Finding: all sources are ONE origin (rtkd/iddqd master). dude OCR is byte-identical
to canon after J-norm. So consensus == canon. Only scream314 (same lineage, re-presented)
shows 3 tail edits, of which only page-24 idx172 is in-scope (0-55). We record it as a
FLAGGED ambiguity, not a majority override (single-origin tie -> keep canon)."""
import json, os

FOUND = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/foundation"
CANON = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt"
RUNES = set("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
def runes_only(s): return "".join(ch for ch in s.replace("ᛂ","ᛄ") if ch in RUNES)

canon_raw = open(CANON, encoding="utf-8").read()
# preserve page split exactly as canon (split on %)
canon_segs = canon_raw.split("%")
canon_pages = [runes_only(p) for p in canon_segs]
# pages list with trailing empties trimmed for analysis
pages = [p for p in canon_pages]
while pages and pages[-1]=="": pages.pop()

# Independent origins among our sources: ONE (rtkd/iddqd lineage).
# Therefore consensus = canon verbatim. Write it in canon's % format.
consensus_pages = list(pages)  # identical to canon body
with open(os.path.join(FOUND,"consensus_runes.txt"),"w",encoding="utf-8") as f:
    f.write("%".join(consensus_pages))
print("wrote consensus_runes.txt with", len(consensus_pages), "pages,", sum(len(p) for p in consensus_pages), "runes")

# Disagreement map
lines = []
lines.append("LIBER PRIMUS LP2 (pages 0-55) — TRANSCRIPTION DISAGREEMENT MAP")
lines.append("="*70)
lines.append("")
lines.append("SOURCES COMPARED (7 total): canon(krisyotam), krisyotam, relikd,")
lines.append("  scream314, r4nd0mD3v3l0p3r, uncovering_wiki, cicadasolvers,")
lines.append("  + dude123124144 raw OCR (local).")
lines.append("")
lines.append("INDEPENDENCE CLASSIFICATION")
lines.append("-"*70)
lines.append("All sources trace to ONE origin: the rtkd/iddqd community master")
lines.append("transcription (cicada-solvers/iddqd fork == same). Verbatim/derived copies:")
lines.append("  krisyotam        : byte-identical to canon (canon IS krisyotam)")
lines.append("  cicadasolvers    : byte-identical over full len (rtkd/iddqd root)")
lines.append("  r4nd0mD3v3l0p3r  : byte-identical over full len (consumes rtkd)")
lines.append("  relikd           : byte-identical over its len (rtkd author)")
lines.append("  uncovering_wiki  : byte-identical over its len ('ripped from rtkd')")
lines.append("  dude123124144 OCR: byte-identical after J-norm (ᛂ->ᛄ), 0 edits")
lines.append("  scream314        : 3 edits total (korn19/2014 re-presentation)")
lines.append("")
lines.append("=> NUMBER OF GENUINELY INDEPENDENT ORIGINS: 1")
lines.append("   (the dude 'independent OCR' is byte-identical, so it is NOT a")
lines.append("    separate reading; it is the same text re-OCR'd or copied.)")
lines.append("")
lines.append("DISAGREEMENTS (the ONLY rune positions any source diverges)")
lines.append("-"*70)
lines.append("Source = scream314 vs all-others/canon. Note: scream314 is SAME lineage,")
lines.append("so these are intra-lineage variants, NOT independent-source votes.")
lines.append("")
lines.append("  PAGE 24, idx 172 : canon=ᚫ (AE)  scream314=ᚪ (A)   [IN SCOPE 0-55]")
lines.append("  PAGE 56, idx 80  : canon=ᚣ (Y)   scream314=ᛖ (E)   [out of scope]")
lines.append("  tail near pg54/56: scream314 has EXTRA ᚠ (F) (skip-clear-F convention)")
lines.append("")
lines.append("Vote tally at page24:172  -> ᚫ: 7 sources (canon,kris,relikd,r4nd0m,")
lines.append("  wiki,cicadasolvers,dude)  vs  ᚪ: 1 (scream314). But ALL 7 are one")
lines.append("  origin, so the 7-1 is illusory; it is a single fork that says ᚪ.")
lines.append("")
lines.append("CONSENSUS DECISION")
lines.append("-"*70)
lines.append("With only 1 independent origin, majority voting is undefined. Consensus")
lines.append("= canon verbatim. page24:172 is FLAGGED (canon ᚫ kept; scream's ᚪ is a")
lines.append("plausible re-read of the same glyph). consensus_runes.txt == canon body.")
lines.append("")
lines.append("VERDICT")
lines.append("-"*70)
lines.append("The canonical ciphertext is INTERNALLY consistent across every public")
lines.append("transcription, but it is NOT independently verified: all sources are one")
lines.append("origin (rtkd/iddqd). The ciphertext is therefore fundamentally unverified")
lines.append("from text comparison alone. The only way to truly check it is reading the")
lines.append("original page IMAGES. Highest-value spot to re-image-read: PAGE 24 idx 172")
lines.append("(ᚫ vs ᚪ) and the page-24/55/56 glyphs scream314 disputes.")
with open(os.path.join(FOUND,"disagreement_map.txt"),"w",encoding="utf-8") as f:
    f.write("\n".join(lines)+"\n")
print("wrote disagreement_map.txt")

# verify consensus == canon body byte for byte
con = open(os.path.join(FOUND,"consensus_runes.txt"),encoding="utf-8").read()
con_pages = [runes_only(p) for p in con.split("%")]
while con_pages and con_pages[-1]=="": con_pages.pop()
print("consensus == canon body:", con_pages == pages)
