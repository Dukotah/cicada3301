#!/usr/bin/env python3
"""R44 W2-C4 — keyed-stego sweep driver (outguess 0.4 + steghide 0.5.1).

Modes:
  controls          PC1 (1033.jpg keyless), PC2 (keyed outguess plant), PC3 (steghide plant)
  derived           ARM-D: per-page derived keys x 56 pages x both tools
  global [START END]ARM-G: keys_big.txt x 56 pages x both tools (page range for chunking)

Every extraction row goes through adjudicate.adjudicate(); R3 stats appended to
results/sweep_stats.tsv (gzipped at closeout). FLAG = F1 or F2 or (F3 if armed).
"""
import json, os, re, subprocess, sys, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.abspath(os.path.join(HERE, ".."))
LP = os.path.abspath(os.path.join(CELL, "..", "..", ".."))
sys.path.insert(0, HERE)
import adjudicate as adj

CAL = json.load(open(os.path.join(CELL, "results", "calibration.json")))
F3_ARMED = CAL["f3_armed"]
SHM = "/dev/shm/c4_pages"
OUTGUESS = "/usr/local/bin/outguess"
STEGHIDE = "/usr/bin/steghide"
RE_SEED = re.compile(rb"seed:\s*(\d+),\s*len:\s*(\d+)")

def stage_pages():
    os.makedirs(SHM, exist_ok=True)
    for n in range(56):
        dst = f"{SHM}/p{n}.jpg"
        if not os.path.exists(dst):
            src = os.path.join(LP, "data", "relikd", f"p{n}.jpg")
            open(dst, "wb").write(open(src, "rb").read())

def og_extract(img, key, tmp):
    cmd = [OUTGUESS] + (["-k", key] if key is not None else []) + ["-r", img, tmp]
    r = subprocess.run(cmd, capture_output=True)
    m = RE_SEED.search(r.stderr + r.stdout)
    seed, dlen = (int(m.group(1)), int(m.group(2))) if m else (-1, -1)
    try:
        payload = open(tmp, "rb").read()
        os.unlink(tmp)
    except FileNotFoundError:
        payload = b""
    return seed, dlen, payload

def sh_extract(img, key, tmp):
    if os.path.exists(tmp):
        os.unlink(tmp)
    r = subprocess.run([STEGHIDE, "extract", "-sf", img, "-p", key, "-xf", tmp, "-f"],
                       capture_output=True)
    ok = r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 0
    payload = open(tmp, "rb").read() if ok else b""
    if os.path.exists(tmp):
        os.unlink(tmp)
    return ok, payload

def row_for(tool, page, kclass, key, img, tmp):
    if tool == "og":
        seed, dlen, payload = og_extract(img, key, tmp)
        a = adj.adjudicate(payload, dlen)
        flag = a["f1"] or a["f2"] or (a["f3"] and F3_ARMED)
        return [tool, page, kclass, key if key is not None else "<keyless>",
                seed, dlen, a["out_len"], a["entropy"], a["printable"],
                int(a["f1"]), int(a["f2"]), int(a["f3"]), int(a["naive"]), int(flag)]
    ok, payload = sh_extract(img, key, tmp)
    a = adj.adjudicate(payload, len(payload))
    flag = ok                                   # steghide self-authenticates
    return [tool, page, kclass, key, -1, len(payload), a["out_len"], a["entropy"],
            a["printable"], int(a["f1"]), int(a["f2"]), int(a["f3"]),
            int(a["naive"]), int(flag)]

def work(task):
    # tmp is keyed by os.getpid(): each pool worker process runs tasks serially, so a
    # per-PID name cannot race. (Instrument fix 2026-11-09, runlog: the original per-task
    # wid%8 naming allowed two concurrent tasks to share a tmp file — a clobber window
    # that could in principle eat a true payload. All rows produced under the racy naming
    # were deleted and both arms re-run from zero.)
    page, keys, _wid = task
    img = f"{SHM}/p{page}.jpg"
    tmp = f"/dev/shm/c4_w{os.getpid()}.bin"
    rows = []
    for kclass, key in keys:
        rows.append(row_for("og", page, kclass, key, img, tmp))
        if key is not None:
            rows.append(row_for("sh", page, kclass, key, img, tmp))
    return rows

HDR = "tool\tpage\tkey_class\tkey\tog_seed\tog_declared_len\tout_len\tentropy\tprintable\tf1\tf2\tf3\tnaive\tflag\n"

def run_tasks(tasks, out_tsv, procs=8):
    t0 = time.time()
    new = not os.path.exists(out_tsv)
    flags = []
    with open(out_tsv, "a", encoding="utf-8") as fh:
        if new:
            fh.write(HDR)
        with Pool(procs) as pool:
            done = 0
            for rows in pool.imap_unordered(work, tasks, chunksize=1):
                for r in rows:
                    fh.write("\t".join(str(x) for x in r) + "\n")
                    if r[-1]:
                        flags.append(r)
                done += 1
                if done % 50 == 0:
                    print(f"  {done}/{len(tasks)} tasks {time.time()-t0:.0f}s "
                          f"flags={len(flags)}", flush=True)
    print(f"done {len(tasks)} tasks in {time.time()-t0:.0f}s, flags={len(flags)}")
    return flags

def main():
    mode = sys.argv[1]
    stage_pages()
    os.makedirs(os.path.join(CELL, "results"), exist_ok=True)

    if mode == "derived":
        kp = json.load(open(os.path.join(CELL, "results", "keys_per_page.json")))["keys"]
        tasks = []
        for n in range(56):
            keys = [("derived", k) for k in kp[str(n)]] + [("keyless_repl", None)]
            tasks.append((n, keys, n % 8))
        flags = run_tasks(tasks, os.path.join(CELL, "results", "sweep_stats_derived.tsv"))
    elif mode == "global":
        # 2026-11-09 chunking extension (post-ARM-G-teardown, runlog): optional args 4/5
        # are a KEY slice [k0,k1) into keys_big.txt file order (= priority order per
        # R29-L1 provenance). Task construction only; work()/row_for()/adjudicate
        # untouched, controls remain valid. All chunks append to ONE tsv
        # (sweep_stats_global_0_56.tsv) so closeout.py sees a single ARM-G file.
        start, end = int(sys.argv[2]), int(sys.argv[3])
        k0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        k1 = int(sys.argv[5]) if len(sys.argv) > 5 else None
        biglist = [l.rstrip("\n") for l in
                   open(os.path.join(LP, "analysis", "round29", "L1-onion3-crack",
                                     "keys_big.txt"), encoding="utf-8", errors="replace")]
        biglist = [k for k in biglist if k]
        if k1 is None:
            k1 = len(biglist)
        sl = biglist[k0:k1]
        CH = 250
        tasks = []
        for n in range(start, end):
            for ci in range(0, len(sl), CH):
                tasks.append((n, [("global", k) for k in sl[ci:ci + CH]],
                              (n * 17 + ci) % 8))
        flags = run_tasks(tasks, os.path.join(CELL, "results",
                                              "sweep_stats_global_0_56.tsv"))
    else:
        raise SystemExit("mode?")
    tag = "_".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    json.dump([dict(zip(HDR.split(), f)) for f in flags],
              open(os.path.join(CELL, "results", f"flags_{mode}_{tag}.json".replace("__", "_")), "w"),
              indent=1, default=str)

if __name__ == "__main__":
    main()
