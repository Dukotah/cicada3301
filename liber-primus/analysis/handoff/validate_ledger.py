"""Validate liber-primus/LEDGER.json.

Checks, in order of how much they matter:

  1. UNSOUND NEGATIVES — any entry claiming `negative` or `eliminated` whose
     `positive_control` is not `passed`. This is the check the whole ledger exists for.
     A null from an instrument never shown able to detect a planted signal is not a
     negative; it is an unknown wearing a negative's clothes.
  2. UNFIXED THRESHOLDS — a negative whose pass/fail bar was not fixed in advance is a
     post-hoc story, not a test.
  3. MISSING EVIDENCE — every `evidence` path must exist on disk, or the entry is a claim
     with nothing behind it.
  4. DANGLING LINKS — supersedes / superseded_by pointing at ids that do not exist.
  5. SCHEMA — required keys present, status from the controlled vocabulary.
  6. COUNT DRIFT — the published `counts` block must equal a recount of `entries`. The
     ledger is now maintained by appending coordinator merges, not by re-running
     build_ledger.py, so `counts` can silently fall behind the rows it summarises. It did:
     R19-FINITE-ORNAMENT-REGISTER was appended on 2026-10-01 leaving `total` at 171 with 172
     rows present, and this validator printed the stale block back without noticing, because
     it echoed `counts` instead of checking it. A headline number that disagrees with the
     data under it is exactly the defect this file exists to catch, so it is now an ERROR.

  7. R3 STORE COMPLIANCE — rows (round >= 19) declaring a sweep must point `sweep_store` at a
     SWEEPROW JSONL that passes adjudicate.validate_store and carries ioc/mds/pmax_ne/zl.

Exit code is 0 if no ERROR-level problem is found. WARN-level findings are printed but do
not fail the run: several are legitimately open (an in-flight lane has no result yet).

    python3 validate_ledger.py [--strict]
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(LP, ".."))
LEDGER = os.path.join(LP, "LEDGER.json")

REQUIRED = ["id", "hypothesis", "status"]
NEGATIVE_STATUSES = {"negative", "eliminated"}


def lane_dirs(e):
    """Candidate directories an entry's bare filenames are relative to.

    Most entries write `evidence` as a bare filename (`PREREG.md`, `results.json`) that is
    relative to the lane's own folder. Lane folder names are not identical to the `lane`
    field (`lane: "L1"` lives in `round21/L1-seal-realmode-proxy/`), so glob the prefix.
    """
    rnd, lane = e.get("round"), e.get("lane")
    if not rnd:
        return []
    base = os.path.join(LP, "analysis", f"round{rnd}")
    if not lane:
        return [base]
    return [base] + [d for d in glob.glob(os.path.join(base, f"{lane}*")) if os.path.isdir(d)]


def evidence_exists(p, bases):
    """Does an `evidence` path point at something real?

    The ledger was merged from rounds that used three different roots: paths relative to the
    repository root (`liber-primus/analysis/...`), to `liber-primus/` itself (`analysis/...`),
    and bare filenames relative to the entry's own lane folder. All three conventions are in
    the file and none is wrong, so resolve against each before reporting a path as missing.
    A trailing `#anchor` is a link into a document, not part of the filename; a `*` globs.
    """
    p = (p or "").split("#", 1)[0].strip()
    if not p:
        return True
    for base in bases:
        cand = os.path.join(base, p)
        if glob.has_magic(cand):
            if glob.glob(cand):
                return True
        elif os.path.exists(cand):
            return True
    return False


# --- R3 enforcement (ARMADA-DOCTRINE R3; Round 32 I3) -------------------------------
# SCOPING (Q5 rule, recorded in analysis/round32/I3-r3-enforcement/RESULTS.md): only rows
# with round >= R3_FIRST_ROUND that DECLARE a sweep are checked, so no historical row is
# retro-broken. A row declares a sweep by (a) an explicit `sweep_store` field (str|list of
# paths; a MISSING/non-compliant store is a hard ERROR) or (b) `declares_sweep: true`
# (must also carry sweep_store), or (c) implicitly: an evidence `*.jsonl` whose basename
# contains "sweep" -- (c) is advisory (WARN) because pre-R3-schema stores cannot be fixed.
R3_FIRST_ROUND = 19
R3_STATS = ("ioc", "mds", "pmax_ne", "zl")   # decrypt IoC*N, min-distinct/32, best non-EN LM, compressibility


def _round_num(e):
    try:
        return int(str(e.get("round", "")).split("/")[0])
    except ValueError:
        return -1


def resolve_path(p, bases):
    p = (p or "").split("#", 1)[0].strip()
    for b in bases:
        c = os.path.join(b, p)
        if os.path.exists(c):
            return c
    return None


def check_r3_store(path):
    """Return a list of problems with one SWEEPROW store ([] = compliant)."""
    sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))
    try:
        import adjudicate as A
    except Exception as ex:                      # pragma: no cover
        return [f"cannot import adjudicate.validate_store: {ex}"]
    try:
        with open(path, encoding="utf-8") as f:
            h = json.loads(f.readline())
    except Exception as ex:
        return [f"unreadable header: {ex}"]
    if not isinstance(h, dict) or not str(h.get("v", "")).startswith("SWEEPROW"):
        return ["line 1 is not a SWEEPROW header (R3 columns cannot be present)"]
    missing = [k for k in R3_STATS if k not in (h.get("fields") or [])]
    if missing:
        return [f"header lacks R3 statistics {missing}"]
    try:
        A.validate_store(path)
    except Exception as ex:
        return [f"validate_store: {type(ex).__name__}: {ex}"]
    return []


def r3_problems(e, bases):
    """(errors, warns) for one ledger row under the scoped R3 rule."""
    errs, warns = [], []
    if _round_num(e) < R3_FIRST_ROUND:
        return errs, warns
    eid = e.get("id", "<no id>")
    decl = e.get("sweep_store")
    decl = [decl] if isinstance(decl, str) else list(decl or [])
    if e.get("declares_sweep") and not decl:
        errs.append(f"[{eid}] R3: declares_sweep but names no sweep_store")
    for p in decl:
        path = resolve_path(p, bases)
        if not path:
            errs.append(f"[{eid}] R3: sweep_store does not exist: {p}")
            continue
        errs += [f"[{eid}] R3 VIOLATION in {p}: {m}" for m in check_r3_store(path)]
    ev = e.get("evidence") or []
    for p in ([ev] if isinstance(ev, str) else ev):
        b = os.path.basename(p.split("#", 1)[0])
        if b.endswith(".jsonl") and "sweep" in b.lower() and p not in decl:
            path = resolve_path(p, bases)
            if path:
                for m in check_r3_store(path):
                    warns.append(f"[{eid}] R3-UNVERIFIED (implicit sweep store, advisory): {p}: {m}")
    return errs, warns


def main():
    strict = "--strict" in sys.argv
    doc = json.load(open(LEDGER, encoding="utf-8"))
    entries = doc["entries"]
    ids = {e["id"] for e in entries}
    errors, warns, notes = [], [], []

    for e in entries:
        eid = e.get("id", "<no id>")

        # 5. schema
        for k in REQUIRED:
            if not e.get(k):
                errors.append(f"[{eid}] missing required field `{k}`")
        if e.get("status") not in doc["statuses"]:
            errors.append(f"[{eid}] status {e.get('status')!r} not in the controlled vocabulary")

        # 1. THE important one
        if e.get("status") in NEGATIVE_STATUSES:
            pc = e.get("positive_control")
            if pc != "passed":
                errors.append(
                    f"[{eid}] UNSOUND NEGATIVE: status={e['status']} but "
                    f"positive_control={pc!r}. A null from an unvalidated instrument "
                    f"proves nothing - either record the passing control or downgrade "
                    f"the status to `inconclusive`.")
            # 2. threshold discipline
            if not e.get("threshold"):
                warns.append(f"[{eid}] negative with no recorded threshold")
            elif e.get("threshold_fixed_in_advance") is not True:
                warns.append(f"[{eid}] negative whose threshold was not fixed in advance "
                             f"(post-hoc bars are not tests)")

        # 2b. (R33/X1) a negative with no not_covered statement is an unbounded claim (warning only)
        if e.get("status") in NEGATIVE_STATUSES and not e.get("not_covered"):
            import re as _re
            _m = _re.match(r"\s*(\d+)", str(e.get("round", "")))
            if _m and int(_m.group(1)) >= 19:
                warns.append(f"[{eid}] NULL-NOT-COVERED: negative (round >= 19) with not_covered "
                             f"null/empty - state what the null does not cover")

        # 2c. (R36 audit, item 12) WARN only: a negative should carry the three conditionals and a coverage.
        if e.get("status") in NEGATIVE_STATUSES:
            if _round_num(e) >= R3_FIRST_ROUND and not e.get("three_conditionals"):
                warns.append(f"[{eid}] NO-THREE-CONDITIONALS: negative (round >= 19) without "
                             f"`three_conditionals` (key_space / transition_model / adjudicator_register)")
            if e.get("coverage") is None:
                warns.append(f"[{eid}] NULL-COVERAGE: negative with coverage null - the claim is unbounded")

        # a failed control must not be carrying a conclusion
        if e.get("positive_control") == "failed" and e.get("status") in NEGATIVE_STATUSES:
            errors.append(f"[{eid}] positive_control FAILED but status is {e['status']} - "
                          f"must be `inconclusive`")

        # 3. evidence. A handful of entries store `evidence` as a single string rather
        # than a list; iterating that directly walks it character by character.
        ev = e.get("evidence") or []
        if isinstance(ev, str):
            ev = [ev]
        bases = [ROOT, LP] + lane_dirs(e)
        for p in ev:
            if not evidence_exists(p, bases):
                warns.append(f"[{eid}] evidence path does not exist: {p}")

        # 7. R3 (scoped to round >= 19 sweep-declaring rows)
        r3e, r3w = r3_problems(e, bases)
        errors += r3e
        warns += r3w

        # 4. dangling links
        for field in ("supersedes", "superseded_by"):
            for ref in e.get(field) or []:
                if ref not in ids:
                    errors.append(f"[{eid}] {field} points at unknown id {ref!r}")

        # informational: open lanes with no reopen condition are hard to act on later
        if e.get("status") in ("never-run", "open", "partially-run") and not e.get("reopens_if"):
            notes.append(f"[{eid}] open lane with no `reopens_if` - a future reader cannot "
                         f"tell what would settle it")

    # 6. count drift. Recount from the rows and compare against the published block.
    # Print the RECOUNT, never the stored numbers - a validator that echoes the field it is
    # meant to check cannot catch an error in it.
    recount = {}
    for e in entries:
        st = e.get("status")
        recount[st] = recount.get(st, 0) + 1
    stored = doc.get("counts") or {}
    stored_total, stored_by = stored.get("total"), stored.get("by_status") or {}
    if stored_total != len(entries):
        errors.append(f"COUNT DRIFT: counts.total is {stored_total} but `entries` holds "
                      f"{len(entries)} rows. Recount and rewrite the block.")
    for st in sorted(set(recount) | set(stored_by)):
        if stored_by.get(st) != recount.get(st):
            errors.append(f"COUNT DRIFT: counts.by_status[{st!r}] is "
                          f"{stored_by.get(st)!r} but {recount.get(st, 0)} rows carry that "
                          f"status.")
    for k in stored:
        if k not in ("total", "by_status", "note"):
            errors.append(f"COUNT DRIFT: unexpected key counts[{k!r}] - per-status numbers "
                          f"belong in counts.by_status, not beside it.")

    print(f"LEDGER.json  schema {doc['schema_version']}  {len(entries)} entries "
          f"(recounted from the rows)")
    for k, v in sorted(recount.items(), key=lambda x: -x[1]):
        print(f"   {k:18s} {v}")
    print()

    def dump(label, items, cap=None):
        print(f"{label}: {len(items)}")
        for m in (items if cap is None else items[:cap]):
            print(f"   {m}")
        if cap is not None and len(items) > cap:
            print(f"   ... and {len(items) - cap} more")
        print()

    dump("ERRORS", errors)
    dump("WARNINGS", warns, cap=25)
    dump("NOTES", notes, cap=10)

    unsound = [m for m in errors if "UNSOUND NEGATIVE" in m]
    print(f"Unsound negatives: {len(unsound)}  "
          f"(this is the number that matters - it should be 0)")

    # Count drift fails the run in BOTH modes. Every other ERROR here can be legitimately
    # open for a while (an in-flight lane, a lane whose evidence is still being written);
    # a `counts` block that contradicts the rows beneath it never can. It is a mechanical
    # disagreement between a headline number and its own data, which is the single failure
    # mode this repository has published twice, so it is not left to --strict.
    drift = [m for m in errors if m.startswith("COUNT DRIFT")]
    r3 = [m for m in errors if "] R3" in m]
    bad = len(errors) if strict else len(unsound) + len(drift) + len(r3)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
