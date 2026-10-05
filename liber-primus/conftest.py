"""pytest collection rules for this tree.

WHY THIS FILE EXISTS. Three round artifacts are *scripts* that happen to be named like
tests (`test_*.py` / `*_test.py`) and that do all of their work at MODULE scope. pytest
therefore executed them during COLLECTION, and one of them shells out to an absolute
Linux CPython-2.7 path that does not exist on every machine. The resulting
FileNotFoundError aborted collection and took the entire suite down with it, so

    cd liber-primus && python -m pytest -q -m "not network"

-- the command CLAUDE.md tells every future contributor to run before committing --
failed on a clean checkout with 0 tests run. It had been failing that way since
Round 28 landed.

They are ignored here rather than renamed, because `LEDGER.json` and the round RESULTS
documents cite them by path and renaming would break those citations. They are still
runnable, exactly as they were written, with `python <path>`.

`collect_ignore` is resolved relative to THIS file's directory, which is why the fix
lives in a conftest rather than in `pyproject.toml`'s `addopts`: it then holds whether
pytest is invoked from `liber-primus/`, from the repository root, or with an explicit
path argument.
"""

collect_ignore = [
    "analysis/round28/R/t3_subsumption_test.py",
    "analysis/armada20/test_id18.py",
    "analysis/armada20/test_id18b.py",
]
