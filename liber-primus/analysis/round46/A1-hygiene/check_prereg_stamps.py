"""R46-A1 (c): hash-stamp rule for PREREG addenda (R45 SYNTHESIS §2: "T1's were stamped — make that the rule").

Rule checked. Every block in a lane's PREREG.md whose header matches `#... Addendum <id>` must have a sha256 stamp,
i.e. a 64-hex digest recorded either inside the addendum block itself or in a file of the lane dir (run.log, *.log,
*.out, *.sha256, *.txt). The digest must equal sha256 of the PREREG.md bytes from the start of the file through
the end of that addendum: the file as it stood when the addendum was written. This is the R45 T1 convention.
Trailing blank lines, a '---' rule and CRLF/LF variants before the next header are allowed. Statuses:
  VERIFIED    a recorded digest equals a prefix digest for this addendum
  MISMATCH    a stamp line names this addendum but no digest matches (the prefix was edited after stamping)
  UNSTAMPED   no stamp at all
The base PREREG (prefix before the first addendum) is reported for information only.
Report only: this rewrites nothing. Usage: python check_prereg_stamps.py [--json out.json] [--selftest] [dirs...]
Default dirs: analysis/round45/*/ and analysis/round46/*/. Exit code 1 if any non-VERIFIED addendum exists."""
import os, re, sys, glob, json, hashlib, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__)); ANALYSIS = os.path.abspath(os.path.join(HERE, '..', '..'))
HDR = re.compile(rb'^#{1,6}[ \t]+Addendum\b[ \t]*([A-Za-z]?\d+[A-Za-z]?)?', re.I)
HEX = re.compile(r'\b[0-9a-f]{64}\b')
STAMP_FILES = ('*.log', '*.out', '*.sha256', '*.txt')
sha = lambda b: hashlib.sha256(b).hexdigest()


def blocks(raw):
    """[(addendum_id, start_offset, end_offset)] over raw bytes; end = start of next addendum header or EOF."""
    offs, pos = [], 0
    for line in raw.splitlines(keepends=True):
        m = HDR.match(line)
        if m: offs.append(((m.group(1) or b'?').decode(), pos))
        pos += len(line)
    return [(aid, s, offs[k + 1][1] if k + 1 < len(offs) else len(raw)) for k, (aid, s) in enumerate(offs)]


def prefix_digests(raw, end):
    """digests of raw[:e] for every line boundary e from the last non-blank, non-'---' content line up to end."""
    cut = raw[:end]; tail = end
    while True:  # walk back over trailing blank lines / horizontal rules
        body = cut[:tail].rstrip(b'\r\n')
        last = body[body.rfind(b'\n') + 1:]
        if last.strip() in (b'', b'---') and body:
            tail = len(body) - len(last); continue
        break
    ds = set(); e = len(cut[:tail].rstrip(b'\r\n'))
    for cand in range(e, end + 1):
        if cand == end or raw[cand - 1:cand] == b'\n' or cand == e:
            ds.add(sha(raw[:cand]))
    ds.add(sha(raw[:e] + b'\n')); ds.add(sha(raw[:e] + b'\r\n'))
    return ds


def lane_stamps(lane, prereg_path, raw):
    """{digest: [(file, line)]} from lane files; also digests written inside the PREREG itself."""
    found = {}
    files = set()
    for pat in STAMP_FILES: files.update(glob.glob(os.path.join(lane, pat)))
    for f in sorted(files):
        try: txt = open(f, encoding='utf8', errors='replace').read()
        except OSError: continue
        for ln in txt.splitlines():
            for h in HEX.findall(ln): found.setdefault(h, []).append((os.path.basename(f), ln.strip()[:160]))
    for ln in raw.decode('utf8', 'replace').splitlines():
        for h in HEX.findall(ln): found.setdefault(h, []).append(('PREREG.md', ln.strip()[:160]))
    return found


def check_lane(lane):
    p = os.path.join(lane, 'PREREG.md')
    if not os.path.exists(p): return None
    raw = open(p, 'rb').read(); st = lane_stamps(lane, p, raw); bl = blocks(raw)
    base_end = bl[0][1] if bl else len(raw)
    base = 'VERIFIED' if prefix_digests(raw, base_end) & set(st) else 'UNSTAMPED'
    out = []
    for aid, s, e in bl:
        ds = prefix_digests(raw, e); hit = ds & set(st)
        if hit:
            status, ev = 'VERIFIED', st[sorted(hit)[0]][0]
        else:
            named = [(f, l) for h, v in st.items() for f, l in v
                     if re.search(r'addendum\s*' + re.escape(aid) + r'\b', l, re.I) and f != 'PREREG.md']
            status, ev = ('MISMATCH', named[0]) if named else ('UNSTAMPED', None)
        header = raw[s:raw.find(b'\n', s)].decode('utf8', 'replace').strip()
        out.append(dict(addendum=aid, header=header[:140], status=status, evidence=ev))
    return dict(lane=os.path.relpath(lane, ANALYSIS).replace('\\', '/'), base_prereg=base, addenda=out)


def selftest():
    """Plants (PREREG Q1): stamped / stale / unstamped addenda must be VERIFIED / MISMATCH / UNSTAMPED."""
    d = tempfile.mkdtemp()
    try:
        a = b'# P\n\nbody\n\n## Addendum 1 - x\n\none\n'
        b = a + b'\n## Addendum 2 - y\n\ntwo\n'
        c = b + b'\n---\n\n## Addendum 3 - z\n\nthree\n'
        log = f'PREREG.md sha256 {sha(b"# P" + chr(10).encode() + chr(10).encode() + b"body" + chr(10).encode())}\n'
        log += f'PREREG Addendum 1 sha256 {sha(a)}\n'
        log += f'PREREG Addendum 2 sha256 {sha(b + b"edited")}\n'  # stale: prefix changed after stamping
        open(os.path.join(d, 'PREREG.md'), 'wb').write(c); open(os.path.join(d, 'run.log'), 'w').write(log)
        r = check_lane(d); got = [x['status'] for x in r['addenda']]
        ok = got == ['VERIFIED', 'MISMATCH', 'UNSTAMPED']
        return ok, got
    finally:
        shutil.rmtree(d)


def main(argv):
    jout = None
    if '--json' in argv: i = argv.index('--json'); jout = argv[i + 1]; del argv[i:i + 2]
    st_ok, st_got = selftest()
    print(f'selftest (plants VERIFIED/MISMATCH/UNSTAMPED): {"PASS" if st_ok else "FAIL"} {st_got}')
    if '--selftest' in argv: return 0 if st_ok else 1
    dirs = argv or sorted(glob.glob(os.path.join(ANALYSIS, 'round45', '*', '')) + glob.glob(os.path.join(ANALYSIS, 'round46', '*', '')))
    res = [r for r in (check_lane(x.rstrip('/\\')) for x in dirs) if r]
    bad = 0
    for r in res:
        print(f"{r['lane']:32s} base={r['base_prereg']:9s} addenda={len(r['addenda'])}")
        for a in r['addenda']:
            bad += a['status'] != 'VERIFIED'
            print(f"    {a['status']:9s} Addendum {a['addendum']:4s} {a['header'][:90]}")
    summary = dict(selftest_pass=st_ok, lanes=len(res), addenda=sum(len(r['addenda']) for r in res), violations=bad)
    print('summary', summary)
    if jout: json.dump(dict(summary=summary, lanes=res), open(jout, 'w', encoding='utf8'), indent=1, ensure_ascii=False)
    return 1 if (bad or not st_ok) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
