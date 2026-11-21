"""Shared helpers for the volunteer-compute kit (stdlib only, Python 3.8+).

Nothing in here scores anything. Scoring is done only by the committed C engine
(analysis/round36/P1-panel-r36/engine_inputs_copy/grind27.c), compiled unmodified.
The one exception is the positive-control binary, which is the stock source plus the
2-line Round 38 control patch (analysis/round38/S1-s2-windows/patch_ctl.py), applied
verbatim. That binary is only ever used for the planted control, never for a sweep.
"""
import hashlib
import json
import os
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

KIT_VERSION = 1
VOL = Path(__file__).resolve().parent
LP = VOL.parent                      # liber-primus/
SHARDS_PATH = VOL / "shards.json"
RESULTS_DIR = VOL / "results"
BUILD_DIR = VOL / "build"
RUNS_DIR = VOL / "runs"

CFLAGS = ["-O2", "-std=gnu17", "-fopenmp", "-ffp-contract=off"]   # Round 34/36 flags, no -march=native
HIST_BINS = 2600                      # engine: 0.01-wide pmax bins over [0, 26)
TOP_K = 50
TEXT_SUFFIXES = {".c", ".dat", ".txt", ".py", ".json"}

# Fields that enter result_sha256. Everything else (wall time, machine, logs) is metadata.
CANON_FIELDS = [
    "kit_version", "shard_id", "lane", "range", "relation", "reducer", "offset", "sign",
    "engine_source_sha256", "threshold", "n_scored", "n_candidates", "n_above_bar",
    "best", "above_bar", "top_k", "histogram_0p01", "candidates",
]
ROW_FIELDS = ("above_bar", "top_k", "candidates")


class KitError(Exception):
    pass


def log(msg):
    print(msg, flush=True)


# ------------------------------------------------------------------ files / hashes
def file_bytes(p):
    """File contents, with CRLF normalised to LF for text files (a Windows checkout
    with autocrlf must hash the same as the committed blob)."""
    b = Path(p).read_bytes()
    if Path(p).suffix in TEXT_SUFFIXES:
        b = b.replace(b"\r\n", b"\n")
    return b


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    return sha256_bytes(file_bytes(p))


def load_shards(path=None):
    with open(path or SHARDS_PATH, encoding="utf-8") as f:
        return json.load(f)


def write_shards(db, path=None):
    """shards.json with one shard per line, so a claim or a status flip is a one-line diff."""
    head = {k: v for k, v in db.items() if k != "shards"}
    body = json.dumps(head, indent=1)[:-2]          # strip closing "\n}"
    rows = ",\n".join("  " + json.dumps(s) for s in db["shards"])
    txt = body + ',\n "shards": [\n' + rows + "\n ]\n}\n"
    json.loads(txt)
    Path(path or SHARDS_PATH).write_text(txt, encoding="utf-8")


def shard_by_id(db, sid):
    for s in db["shards"]:
        if s["id"] == sid:
            return s
    raise KitError("unknown shard id %r (see shards.json)" % sid)


# ------------------------------------------------------------------ canonical result hash
def canonical_sha(result):
    canon = {k: result[k] for k in CANON_FIELDS}
    blob = json.dumps(canon, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256_bytes(blob.encode("utf-8"))


def write_result(path, result):
    """Readable JSON: one row per line for the row lists, so diffs stay small."""
    out = ["{"]
    keys = list(result.keys())
    for i, k in enumerate(keys):
        v = result[k]
        comma = "," if i + 1 < len(keys) else ""
        if k in ROW_FIELDS:
            if not v:
                out.append(' "%s": []%s' % (k, comma))
            else:
                rows = ",\n".join("  " + json.dumps(r) for r in v)
                out.append(' "%s": [\n%s\n ]%s' % (k, rows, comma))
        else:
            out.append(' "%s": %s%s' % (k, json.dumps(v, sort_keys=True), comma))
    out.append("}")
    tmp = Path(str(path) + ".tmp")
    tmp.write_text("\n".join(out) + "\n", encoding="utf-8")
    os.replace(tmp, path)


# ------------------------------------------------------------------ machine info (no personal data)
def machine_info(threads):
    cpu = platform.processor() or ""
    try:
        for ln in open("/proc/cpuinfo", encoding="utf-8", errors="ignore"):
            if ln.lower().startswith("model name"):
                cpu = ln.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    return {
        "os": platform.system(), "os_release": platform.release(), "arch": platform.machine(),
        "cpu_model": cpu, "logical_cpus": os.cpu_count(), "threads_used": threads,
        "python": platform.python_version(), "compiler": compiler_version(),
    }


def compiler():
    return os.environ.get("CC", "gcc")


def compiler_version():
    try:
        r = subprocess.run([compiler(), "--version"], capture_output=True, text=True)
        return (r.stdout or r.stderr).splitlines()[0].strip()
    except (OSError, IndexError):
        return "unknown"


# ------------------------------------------------------------------ build
CTL_OLD = '''        if (self_test(NULL)) { printf("ABORT: self-test failed; broken scan, not a null\\n"); return 1; }
        return run_plan(plan, seconds);'''
CTL_NEW = '''        if (self_test(NULL)) { printf("ABORT: self-test failed; broken scan, not a null\\n"); return 1; }
        { const char *cc = getenv("GRIND27_CTL_CIPHER");   /* R38 control-only: swap C_SCREEN AFTER the real self-test */
          if (cc) { load_cipher_override(cc, C_SCREEN); printf("CTL: C_SCREEN replaced from %s\\n", cc); } }
        return run_plan(plan, seconds);'''


def check_pins(lane):
    """Every engine input must hash to the value pinned in shards.json."""
    src = LP / lane["engine_dir"]
    bad = []
    for name, want in lane["engine_source_sha256"].items():
        p = src / name
        if not p.exists():
            bad.append("%s missing" % name)
            continue
        got = sha256_file(p)
        if got != want:
            bad.append("%s sha256 %s != pinned %s" % (name, got[:12], want[:12]))
    if bad:
        raise KitError("engine inputs do not match the pinned instrument: " + "; ".join(bad))


def build_engine(lane_id, lane, quiet=False):
    """Copy the pinned inputs into build/<lane>/ and compile grind27 (stock) and
    grind27_ctl (stock + R38 2-line control patch). Rebuilds only when inputs change."""
    check_pins(lane)
    src = LP / lane["engine_dir"]
    bdir = BUILD_DIR / lane_id
    bdir.mkdir(parents=True, exist_ok=True)
    for name in lane["engine_source_sha256"]:
        data = file_bytes(src / name)
        dst = bdir / name
        if not dst.exists() or dst.read_bytes() != data:
            dst.write_bytes(data)
    stock = (bdir / "grind27.c").read_text(encoding="utf-8")
    if stock.count(CTL_OLD) != 1:
        raise KitError("R38 control patch anchor not found exactly once in grind27.c")
    ctl_src = stock.replace(CTL_OLD, CTL_NEW)
    if not (bdir / "grind27_ctl.c").exists() or (bdir / "grind27_ctl.c").read_text(encoding="utf-8") != ctl_src:
        (bdir / "grind27_ctl.c").write_text(ctl_src, encoding="utf-8")
    stamp = sha256_bytes(json.dumps([lane["engine_source_sha256"], CFLAGS, compiler_version(),
                                     sha256_bytes(ctl_src.encode())]).encode())
    stamp_p = bdir / "BUILD-STAMP"
    if (bdir / "grind27").exists() and (bdir / "grind27_ctl").exists() and \
            stamp_p.exists() and stamp_p.read_text().strip() == stamp:
        return bdir
    for out, c in (("grind27", "grind27.c"), ("grind27_ctl", "grind27_ctl.c")):
        cmd = [compiler()] + CFLAGS + ["-o", out, c, "-lm"]
        if not quiet:
            log("  build: " + " ".join(cmd))
        r = subprocess.run(cmd, cwd=bdir, capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            raise KitError("compile failed (need gcc with OpenMP; on macOS use Homebrew gcc via CC=gcc-14)")
    stamp_p.write_text(stamp + "\n")
    return bdir


def binary_sha(bdir):
    return sha256_bytes((bdir / "grind27").read_bytes())


# ------------------------------------------------------------------ engine runs
def plan_lane(name, lane, lo, hi):
    return {"lane": name, "reducer": lane["reducer"], "relation": lane["relation"],
            "offset": lane["offset"], "from": lo, "to": hi,
            "cand_bar": lane["cand_bar"], "claim_bar": lane["claim_bar"]}


def run_plan(bdir, run_dir, lanes, threads, binary="grind27", extra_env=None):
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    plan = run_dir / "plan.json"
    plan.write_text(json.dumps(lanes))
    env = dict(os.environ)
    env["GRIND27_S2_CONTROL_OK"] = "1"     # set only after the exact-relation control passed (gate order in run_gates)
    env.update(extra_env or {})
    r = subprocess.run(["./" + binary, "--plan", str(plan.resolve()), "--run-dir", str(run_dir.resolve()),
                        "--threads", str(threads)], cwd=bdir, env=env, capture_output=True, text=True)
    return r


def read_top(run_dir, name):
    with open(Path(run_dir) / ("top_%s.json" % name), encoding="utf-8") as f:
        return [(int(r["seed"]), float(r["pmax"])) for r in json.load(f)]


def read_hist(run_dir, name):
    b = (Path(run_dir) / ("hist_%s.u64" % name)).read_bytes()
    n = len(b) // 8
    if n % HIST_BINS:
        raise KitError("histogram size not a multiple of %d bins" % HIST_BINS)
    vals = struct.unpack("<%dQ" % n, b)
    tot = [0] * HIST_BINS
    for i, v in enumerate(vals):
        tot[i % HIST_BINS] += v
    return tot


def score_seeds(bdir, lane, seeds):
    """Score individual seeds with the STOCK engine: one 1-seed plan lane per seed,
    1 thread, so the band is exactly [s, s+1). Returns {seed: pmax}."""
    seeds = sorted(set(int(s) for s in seeds))
    out = {}
    with tempfile.TemporaryDirectory(prefix="vol_score_") as td:
        for bi in range(0, len(seeds), 60):            # engine MAX_LANES = 64
            batch = seeds[bi:bi + 60]
            rd = Path(td) / ("b%d" % bi)
            lanes = [plan_lane("v%d" % s, lane, s, s + 1) for s in batch]
            r = run_plan(bdir, rd, lanes, 1)
            if r.returncode != 0:
                raise KitError("engine scoring run failed rc=%d:\n%s%s" % (r.returncode, r.stdout[-2000:], r.stderr[-2000:]))
            for s in batch:
                top = read_top(rd, "v%d" % s)
                if len(top) != 1 or top[0][0] != s:
                    raise KitError("scoring lane for seed %d returned %r" % (s, top))
                out[s] = top[0][1]
    return out


def sweep_window(bdir, lane, lo, hi, threads):
    """Re-sweep [lo, hi) with the stock engine; returns ({seed: pmax} for pmax >= cand_bar, hist)."""
    with tempfile.TemporaryDirectory(prefix="vol_win_") as td:
        r = run_plan(bdir, td, [plan_lane("W", lane, lo, hi)], threads)
        if r.returncode != 0:
            raise KitError("window re-sweep failed rc=%d" % r.returncode)
        cands = {}
        for ln in (Path(td) / "candidates.jsonl").read_text().splitlines():
            if ln.strip():
                c = json.loads(ln)
                cands[int(c["seed"])] = float(c["pmax"])
        return cands, read_hist(td, "W")


# ------------------------------------------------------------------ gates (run BEFORE any sweep or verify)
def run_gates(bdir, lane, threads=2):
    """Panel gate, stock self-test (V1 64/64 + V2 planted screen), the R38 exact-relation
    planted control reproduced to the last digit, and the real-ciphertext anchor seed.
    Returns (ok, record)."""
    rec = {}
    # 1. panel gate (the engine itself never compares PANEL_SHA256; this script does)
    r = subprocess.run([sys.executable, "check_panel_gate.py"], cwd=bdir, capture_output=True, text=True)
    rec["panel_gate"] = {"pass": r.returncode == 0, "line": (r.stdout.strip().splitlines() or [""])[-1]}
    if r.returncode != 0:
        return False, rec
    # 2. stock self-test
    r = subprocess.run(["./grind27", "--self-test"], cwd=bdir, capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.startswith(("V1 ", "V2 ", "SELF-TEST"))]
    ok = r.returncode == 0 and any("64/64" in l and "PASS" in l for l in lines) and \
        any(l.startswith("SELF-TEST: PASS") for l in lines)
    rec["self_test"] = {"pass": ok, "lines": [l[:160] for l in lines]}
    if not ok:
        return False, rec
    # 3. exact-relation planted control (Round 38 S1 (a), seed 1234567891), reproduced exactly
    c = lane["control"]
    with tempfile.TemporaryDirectory(prefix="vol_ctl_") as td:
        lo, hi = c["band"]
        r = run_plan(bdir, td, [plan_lane("CTL", lane, lo, hi)], threads, binary="grind27_ctl",
                     extra_env={"GRIND27_CTL_CIPHER": str((LP / c["cipher"]).resolve())})
        top = read_top(td, "CTL") if r.returncode == 0 else []
    got1 = top[0] if top else None
    got2 = top[1] if len(top) > 1 else None
    ok = bool(top) and got1 == (c["seed"], c["expect_pmax"]) and \
        got2 == (c["expect_second"][0], c["expect_second"][1]) and got1[1] >= lane["claim_bar"]
    rec["exact_control"] = {"pass": ok, "planted_seed": c["seed"], "band": c["band"],
                            "rank1": list(got1) if got1 else None, "rank2": list(got2) if got2 else None,
                            "expected_pmax": c["expect_pmax"], "source": c["source"]}
    if not ok:
        return False, rec
    # 4. real-ciphertext anchor: a known seed must re-score to its recorded value
    a = lane["anchor"]
    got = score_seeds(bdir, lane, [a["seed"]])[a["seed"]]
    ok = got == a["pmax"]
    rec["anchor"] = {"pass": ok, "seed": a["seed"], "pmax": got, "expected": a["pmax"], "source": a["source"]}
    return ok, rec


def default_threads():
    return max(1, os.cpu_count() or 1)


def rmtree(p):
    shutil.rmtree(p, ignore_errors=True)
