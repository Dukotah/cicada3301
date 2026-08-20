#!/usr/bin/env python3
"""Lane F — re-derive per-file provenance for the PRESS half.

The 134-file press archive at liber-primus/analysis/attribution/papers-archive/ is a mirror
of github.com/krisyotam/cicada3301 papers/. 126 of its files are PDFs, and they are browser
print-to-PDF captures whose running header/footer preserves the ORIGINAL article URL and the
CAPTURE DATE. This extracts both and writes meta/press_provenance.json.
"""
import json, os, re, subprocess, sys, hashlib, time

REPO = "/mnt/c/Users/dukot/projects/cicada3301"
SRC = os.path.join(REPO, "liber-primus/analysis/attribution/papers-archive")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meta", "press_provenance.json")
DEADLINE = time.time() + float(sys.argv[1]) if len(sys.argv) > 1 else time.time() + 600

URL_RE = re.compile(r'https?://[^\s<>"\']{6,200}')
# print-to-PDF footers carry dd.mm.yyyy (German locale), dd/mm/yyyy or yyyy-mm-dd
DATE_RES = [
    (re.compile(r'\b([0-3]?\d)\.([01]?\d)\.(20[12]\d)\b'), 'dmy_dot'),
    (re.compile(r'\b([0-3]?\d)/([01]?\d)/(20[12]\d)\b'), 'dmy_slash'),
    (re.compile(r'\b(20[12]\d)-([01]\d)-([0-3]\d)\b'), 'ymd'),
]

recs = {}
if os.path.exists(OUT):
    recs = json.load(open(OUT, encoding='utf-8'))

files = sorted(os.listdir(SRC))
for fn in files:
    if time.time() > DEADLINE:
        print("deadline"); break
    if fn in recs:
        continue
    p = os.path.join(SRC, fn)
    if not os.path.isfile(p):
        continue
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    rec = {"file": fn, "bytes": os.path.getsize(p), "sha256": h,
           "mirror_of": "github.com/krisyotam/cicada3301 papers/" + fn}
    if not fn.lower().endswith('.pdf'):
        rec["kind"] = "non-pdf"
        recs[fn] = rec
        continue
    rec["kind"] = "pdf"
    try:
        r = subprocess.run(["pdftotext", "-layout", "-f", "1", "-l", "1", p, "-"],
                           capture_output=True, timeout=60)
        txt = (r.stdout or b"").decode("utf-8", "replace")
        r2 = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, timeout=90)
        full = (r2.stdout or b"").decode("utf-8", "replace")
    except Exception as e:
        rec["error"] = str(e)[:120]
        recs[fn] = rec
        continue
    tail = full[-3000:]
    head = txt[:3000]
    zone = head + "\n" + tail
    urls = [u.rstrip('.,)') for u in URL_RE.findall(zone)]
    # prefer a URL that is not an archive/print-service artefact
    art = [u for u in urls if not re.search(r'(fonts\.|w3\.org|schema\.org|googleapis|gstatic)', u)]
    rec["source_url_candidates"] = list(dict.fromkeys(art))[:5]
    rec["source_url"] = art[0] if art else None
    dt = None
    for rx, kind in DATE_RES:
        m = rx.search(zone)
        if m:
            g = m.groups()
            dt = ("%s-%02d-%02d" % (g[2], int(g[1]), int(g[0]))) if kind != 'ymd' else ("%s-%s-%s" % g)
            rec["capture_date_format"] = kind
            break
    rec["capture_date"] = dt
    recs[fn] = rec

json.dump(recs, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
pdfs = [r for r in recs.values() if r.get("kind") == "pdf"]
both = [r for r in pdfs if r.get("source_url") and r.get("capture_date")]
print("files %d | pdfs %d | with URL+date %d" % (len(recs), len(pdfs), len(both)))
dates = sorted(r["capture_date"] for r in both)
if dates:
    print("capture-date range:", dates[0], "..", dates[-1])
