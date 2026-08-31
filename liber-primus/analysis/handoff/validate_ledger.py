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

        # 4. dangling links
        for field in ("supersedes", "superseded_by"):
            for ref in e.get(field) or []:
                if ref not in ids:
                    errors.append(f"[{eid}] {field} points at unknown id {ref!r}")

        # informational: open lanes with no reopen condition are hard to act on later
        if e.get("status") in ("never-run", "open", "partially-run") and not e.get("reopens_if"):
            notes.append(f"[{eid}] open lane with no `reopens_if` - a future reader cannot "
                         f"tell what would settle it")

    print(f"LEDGER.json  schema {doc['schema_version']}  {len(entries)} entries")
    for k, v in sorted(doc["counts"]["by_status"].items(), key=lambda x: -x[1]):
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

    bad = len(errors) if strict else len(unsound)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
