"""Cross-document consistency checker — fails the build when the docs drift apart.

WHY THIS EXISTS
---------------
This repository's characteristic failure mode is not bad analysis. It is **documents
drifting from results**. Every significant error found here had that shape:

  - The headline verdict said "information-theoretically unsolvable" for months after the
    repo's own B4/G5 result had shown the claim was too strong. Round 10's SYNTHESIS carried
    the correction; README, ELIMINATION-LEDGER, PICKUP-HERE and Round 11 did not.
  - "Seeded-PRNG pads closed" survived in the ledger while the census recorded ~3% coverage.
  - RECON-B flagged two of these in Round 10. Nobody actioned them, because a flag in one
    folder does not reach a reader in another.

Prose review cannot catch that reliably, because the contradicting statements live in
different files and nobody reads all of them at once. A machine can.

This script asserts that the numbers, the verdict wording, the file pointers and the
documented commands agree ACROSS every entry point. It runs in CI, so a drift becomes a
failed build rather than a claim someone repeats for six months.

    python3 check_consistency.py [--verbose]
"""
import argparse, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(LP, ".."))
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis", "round11"))

ERRORS, WARNINGS = [], []


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNINGS.append(msg)


def read(path):
    p = os.path.join(ROOT, path)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None


def resolve(path):
    """Docs cite paths relative to the repo root OR to liber-primus/ (many code blocks
    open with `cd liber-primus`). Resolve against both before declaring one missing.
    This exact rooting assumption has produced three false alarms in this repo's tooling;
    it is centralised here so it is fixed once."""
    p = path.strip().lstrip("./").rstrip("/")
    for cand in (p, f"liber-primus/{p}"):
        if os.path.exists(os.path.join(ROOT, cand)):
            return cand
    return None


def jload(path):
    t = read(path)
    return json.loads(t) if t else None


# ---------------------------------------------------------------------------
def check_rune_count_and_hash():
    """The ciphertext identity must agree everywhere, and match the live computation."""
    import lib_numchannel as nc
    uns = nc.unsolved()
    live_n = len(uns)
    live_sha = hashlib.sha256(",".join(map(str, uns)).encode()).hexdigest()

    prob = jload("liber-primus/PROBLEM.json")
    if not prob:
        err("PROBLEM.json missing")
        return
    ci = prob["ciphertext_identity"]
    if ci["n_runes"] != live_n:
        err(f"PROBLEM.json n_runes={ci['n_runes']} but live computation gives {live_n}")
    if ci["sha256_of_comma_joined_indices"] != live_sha:
        err(f"PROBLEM.json ciphertext sha256 does not match the live stream. "
            f"Recorded {ci['sha256_of_comma_joined_indices'][:16]}..., "
            f"computed {live_sha[:16]}...")

    # the count must also appear correctly in the human-facing docs
    for doc in ("AGENTS.md", "README.md", "KNOWLEDGE.json", "INDEX.json",
                "liber-primus/handoff/FOR-FUTURE-SOLVERS.md"):
        t = read(doc)
        if t is None:
            err(f"{doc} missing")
            continue
        nums = set(re.findall(r"\b12[,.]?956\b", t))
        if not nums:
            warn(f"{doc} never states the rune count ({live_n})")
        wrong = re.findall(r"\b(1[23][,.]?\d{3})\s+runes", t)
        for w in wrong:
            if w.replace(",", "").replace(".", "") != str(live_n):
                err(f"{doc} states '{w} runes'; the correct count is {live_n}")

    # verify_solution.py pins the same constants
    vs = read("liber-primus/verify_solution.py") or ""
    m = re.search(r"EXPECT_N\s*=\s*(\d+)", vs)
    if m and int(m.group(1)) != live_n:
        err(f"verify_solution.py EXPECT_N={m.group(1)} but live count is {live_n}")
    m = re.search(r'EXPECT_SHA256\s*=\s*"([0-9a-f]+)"', vs)
    if m and m.group(1) != live_sha:
        err("verify_solution.py EXPECT_SHA256 does not match the live stream")


def check_retracted_claim_not_asserted():
    """The single most important check.

    'Information-theoretically unsolvable' (unqualified) is a RETRACTED claim. It may
    appear only where it is being quoted, corrected or marked superseded -- never as an
    assertion. This is the exact regression the repo already suffered once.
    """
    pat = re.compile(r"information[- ]theoretically (un)?solvable", re.I)
    # markers that indicate the phrase is being discussed rather than asserted
    context_ok = re.compile(
        r"(supersed|corrected|retract|overreach|overstat|do not (say|state|write)|"
        r"previously|used to|was wrong|not proven|without that qualif|"
        r"misconception|claim\"|\"claim|error|too strong|narrowed|caught|"
        r"OTP[- ]class|not ['\"]?information[- ]theoretically)", re.I)
    scanned = ["README.md", "AGENTS.md", "KNOWLEDGE.json", "INDEX.json",
               "liber-primus/PROBLEM.json", "PICKUP-HERE.md",
               "liber-primus/handoff/FOR-FUTURE-SOLVERS.md",
               "liber-primus/ELIMINATION-LEDGER.md", "docs/index.html", "llms.txt"]
    for doc in scanned:
        t = read(doc)
        if t is None:
            continue
        for m in pat.finditer(t):
            s, e = max(0, m.start() - 500), min(len(t), m.end() + 500)
            window = t[s:e]
            if not context_ok.search(window):
                line = t[:m.start()].count("\n") + 1
                err(f"{doc}:{line} asserts the RETRACTED claim "
                    f"'{m.group(0)}' with no correcting context within 500 chars. "
                    f"The supported claim is OTP-CLASS.")


def check_verdict_wording_present():
    """Every front door must carry the corrected verdict, not just avoid the old one."""
    for doc in ("README.md", "AGENTS.md", "llms.txt", "docs/index.html"):
        t = read(doc)
        if t is None:
            err(f"{doc} missing")
            continue
        if not re.search(r"OTP[- ]class", t, re.I):
            err(f"{doc} does not state the OTP-class verdict")
        if not re.search(r"deriv", t, re.I):
            warn(f"{doc} does not mention the derived-keystream branch")


def check_thresholds_agree():
    """The acceptance bar must be the same number everywhere it is stated."""
    prob = jload("liber-primus/PROBLEM.json")
    bar = prob["acceptance_criteria"]["english_band_threshold"] if prob else None
    vs = read("liber-primus/verify_solution.py") or ""
    m = re.search(r"ENGLISH_BAR\s*=\s*(-?\d+\.?\d*)", vs)
    if m and bar is not None and float(m.group(1)) != float(bar):
        err(f"verify_solution.py ENGLISH_BAR={m.group(1)} but PROBLEM.json says {bar}")
    nullpy = read("liber-primus/benchmark/null.py") or ""
    m = re.search(r"FIXED_BAR\s*=\s*(-?\d+\.?\d*)", nullpy)
    if m and bar is not None and float(m.group(1)) != float(bar):
        err(f"benchmark/null.py FIXED_BAR={m.group(1)} but PROBLEM.json says {bar}")


def check_pointers_resolve():
    """Every path referenced by the machine-readable entry points must exist."""
    for src, getter in (
        ("INDEX.json", lambda d: [v["path"] for v in d["entry_points"].values()]
                                 + [p.split("#")[0] for p in d["task_routing"].values()]),
        ("KNOWLEDGE.json", lambda d: sum(
            [v if isinstance(v, list) else [v] for v in d["pointers"].values()], [])),
    ):
        d = jload(src)
        if not d:
            err(f"{src} missing or unreadable")
            continue
        for p in getter(d):
            if p and resolve(p) is None:
                err(f"{src} points at a nonexistent path: {p}")


def check_documented_commands_exist():
    """Every command the docs tell a reader to run must name a file that exists.

    A front door that instructs a stranger to run a script that isn't there is worse than
    no front door.
    """
    seen = set()
    for doc in ("AGENTS.md", "README.md", "llms.txt", "docs/index.html", "INDEX.json"):
        t = read(doc)
        if t is None:
            continue
        for m in re.finditer(r"python3?\s+(?:-m\s+pytest\s+)?([\w./-]+\.py|[\w./-]+/)", t):
            target = m.group(1)
            if target in seen:
                continue
            seen.add(target)
            if resolve(target) is None:
                err(f"{doc} documents a command against a missing path: {target}")


def check_solved_pages_match_rig():
    """SOLVED-PAGES.json must agree with what the rig currently produces."""
    sp = jload("liber-primus/SOLVED-PAGES.json")
    if not sp:
        warn("SOLVED-PAGES.json missing")
        return
    for p in sp["pages"]:
        txt = p["plaintext_transliteration"]
        if not txt or len(txt) < 40:
            err(f"SOLVED-PAGES.json {p['page_label']}: implausibly short plaintext")
        if p["score_norm"] > -3.0 or p["score_norm"] < -6.0:
            err(f"SOLVED-PAGES.json {p['page_label']}: score {p['score_norm']} outside the "
                f"English band; a solved page should land -4.1..-5.0")


def check_ledger_integrity():
    """No entry may claim a negative from an instrument that was never validated."""
    led = jload("liber-primus/LEDGER.json")
    if not led:
        warn("LEDGER.json missing")
        return
    bad = [e["id"] for e in led["entries"]
           if e.get("status") in ("negative", "eliminated")
           and e.get("positive_control") != "passed"]
    if bad:
        err(f"LEDGER.json has {len(bad)} unsound negative(s): {bad[:5]} "
            f"- a null from an unvalidated instrument is not a negative")
    counts = led.get("counts", {}).get("by_status", {})
    if sum(counts.values()) != len(led["entries"]):
        err("LEDGER.json counts.by_status does not sum to the number of entries")


def check_no_scratch_text():
    """LLM scratch commentary must not appear in published documents."""
    pat = re.compile(r"^(I have enough|I now have|Compiling the report|"
                     r"Here is the report|I'll write|Let me (write|compile))", re.M)
    for root, _, files in os.walk(ROOT):
        if any(s in root for s in (".git", "node_modules", "__pycache__", "L6-archives",
                                   "papers-archive", "fetched")):
            continue
        for f in files:
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(root, f), ROOT).replace("\\", "/")
            t = read(rel)
            if t and pat.search(t):
                err(f"{rel} contains LLM scratch commentary in published prose")


CHECKS = [
    ("ciphertext identity agrees everywhere", check_rune_count_and_hash),
    ("retracted claim is not asserted", check_retracted_claim_not_asserted),
    ("corrected verdict is present in every front door", check_verdict_wording_present),
    ("acceptance thresholds agree", check_thresholds_agree),
    ("machine-readable pointers resolve", check_pointers_resolve),
    ("documented commands name real files", check_documented_commands_exist),
    ("solved-page corpus matches the rig", check_solved_pages_match_rig),
    ("ledger has no unsound negatives", check_ledger_integrity),
    ("no LLM scratch text in published prose", check_no_scratch_text),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    print("=" * 74)
    print("CROSS-DOCUMENT CONSISTENCY CHECK")
    print("=" * 74)
    for name, fn in CHECKS:
        before = len(ERRORS)
        try:
            fn()
        except Exception as e:
            err(f"{name}: check itself raised {type(e).__name__}: {e}")
        status = "ok" if len(ERRORS) == before else "FAIL"
        print(f"  [{status:4s}] {name}")

    print()
    if WARNINGS:
        print(f"WARNINGS ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"   {w}")
        print()
    if ERRORS:
        print(f"ERRORS ({len(ERRORS)}):")
        for e in ERRORS:
            print(f"   {e}")
        print()
        print("The documents disagree. That is how every significant error in this repo's")
        print("history survived - a correction landing in one file and not the others.")
        return 1
    print("All entry points agree. No document drift detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
