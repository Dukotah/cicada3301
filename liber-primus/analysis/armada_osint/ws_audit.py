#!/usr/bin/env python3
"""T6 PGP trailing-whitespace channel audit.
Extract per-signed-message trailing whitespace patterns and decode candidates.
"""
import re, os, glob, sys

RAW = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/artifacts/raw"

# Known catalogued whitespace/prime channels (community wiki)
KNOWN = {
    "2013_riddle_5_3_2_2_3_5": [5,3,2,2,3,5],
    "2014_primes_A194954_2_3_5_7...37": [2,3,5,7,11,13,17,19,23,29,31,37],
    # 2013 whitespace-only tab message -> binary -> ASCII -> emiwp4muu2ktwknf.onion (catalogued)
    "2013_ws_onion_tabmsg_136_102_44_14": [137,103,45,14],
}

# Sequences that are typographic noise, not an intentional channel:
#  - runs of only [1] or [1,1] single trailing spaces = stray/double-space-after-period.
#  - [2]/[2,1] = double space after sentence period. These are NOT payloads.
NOISE_MAX_LEN = 0  # handled heuristically in reporting

def strip_md_prefix(line):
    """Remove markdown code-block leading indent (one tab or up to 4 leading spaces)
    but PRESERVE trailing whitespace."""
    # A markdown fenced/indented code block: leading tab or 4 spaces is formatting.
    if line.startswith("\t"):
        return line[1:]
    if line.startswith("    "):
        return line[4:]
    return line

def trailing_ws(line):
    """Return (count, pattern-string) of trailing whitespace after last non-ws char.
    pattern uses 's' for space, 't' for tab."""
    # strip newline
    line = line.rstrip("\n").rstrip("\r")
    m = re.search(r'[ \t]+$', line)
    if not m:
        return 0, ""
    ws = m.group(0)
    return len(ws), "".join('t' if c=='\t' else 's' for c in ws)

def extract_blocks(path):
    """Return list of signed-message blocks. Each block = list of raw lines (md prefix removed)."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
    blocks = []
    cur = None
    for ln in lines:
        s = strip_md_prefix(ln)
        if "BEGIN PGP SIGNED MESSAGE" in s:
            cur = []
            continue
        if "END PGP SIGNATURE" in s:
            if cur is not None:
                blocks.append(cur)
            cur = None
            continue
        if cur is not None:
            # stop collecting the "message body" once we hit the signature armor;
            # but the whitespace channel is historically in the BODY only.
            cur.append(s)
    return blocks

def analyze_block(block):
    """Return dict with per-line ws and derived sequences (body only, before signature)."""
    # Body is lines before '-----BEGIN PGP SIGNATURE-----'
    body = []
    for s in block:
        if "BEGIN PGP SIGNATURE" in s:
            break
        body.append(s)
    per_line = []
    for s in body:
        c, pat = trailing_ws(s)
        per_line.append((c, pat, s.rstrip()))
    counts = [c for c,_,_ in per_line]
    pats   = [p for _,p,_ in per_line]
    # nonzero-count sequence (drop leading/trailing zeros for comparison)
    nz_counts = [c for c in counts if c > 0]
    # binary channel: line has trailing ws => 1 else 0
    binary = [1 if c>0 else 0 for c in counts]
    # space-vs-tab binary within trailing runs (first ws char)
    stbin = []
    for c,p,_ in per_line:
        if c>0:
            stbin.append(0 if p[0]=='s' else 1)
    return {
        "n_lines": len(body),
        "n_ws_lines": sum(1 for c in counts if c>0),
        "counts": counts,
        "nz_counts": nz_counts,
        "binary": binary,
        "stbin": stbin,
        "pats": pats,
    }

def bits_to_bytes(bits):
    out=[]
    for i in range(0,len(bits)-7,8):
        b=0
        for j in range(8):
            b=(b<<1)|bits[i+j]
        out.append(b)
    return bytes(out)

def seq_matches_known(seq):
    for name,k in KNOWN.items():
        if seq == k:
            return name
        # subsequence match at start
        if len(seq)>=len(k) and seq[:len(k)]==k:
            return name+"(prefix)"
    return None

def main():
    all_seqs = []
    report = []
    for path in sorted(glob.glob(os.path.join(RAW,"*.md"))):
        year = os.path.basename(path).replace(".md","")
        blocks = extract_blocks(path)
        for bi, blk in enumerate(blocks):
            a = analyze_block(blk)
            if a["n_ws_lines"] == 0:
                report.append(f"{year} block#{bi}: NO trailing-whitespace in body ({a['n_lines']} lines) -> no channel")
                continue
            nz = a["nz_counts"]
            match = seq_matches_known(nz)
            # also try binary decode
            bindec = ""
            if a["n_ws_lines"] >= 8:
                bb = bits_to_bytes(a["binary"])
                printable = sum(1 for x in bb if 32<=x<127)
                if bb and printable/len(bb) > 0.7:
                    bindec = " BINARY->" + repr(bb[:40])
            report.append(
                f"{year} block#{bi}: {a['n_lines']} body lines, {a['n_ws_lines']} with trailing ws"
                f"\n   nz-count-seq: {nz}"
                f"\n   patterns(nz): {[p for p in a['pats'] if p]}"
                f"\n   KNOWN-match: {match}{bindec}"
            )
            all_seqs.append((year,bi,nz,match))
    print("\n".join(report))
    print("\n===== SUMMARY: sequences NOT matching known catalog =====")
    unaccounted = [(y,bi,seq) for (y,bi,seq,m) in all_seqs if m is None]
    for y,bi,seq in unaccounted:
        print(f"  {y} block#{bi}: {seq}")
    # dump numeric streams
    with open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/extracts/T6.txt","w") as out:
        for (y,bi,seq,m) in all_seqs:
            out.write(f"# {y} block#{bi} known={m}\n")
            out.write(",".join(map(str,seq))+"\n")
    print("\nWrote numeric streams to extracts/T6.txt")
    print(f"Total blocks with ws channel: {len(all_seqs)}; unaccounted: {len(unaccounted)}")

if __name__=="__main__":
    main()
