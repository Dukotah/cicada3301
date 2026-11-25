"""Run a challenge submission in a separate, isolated Python process (R47-H2; fixes R47-X1 §3.4).

The heavy-lift checkers (C8, C9, C10) used to import your file into their own process, so a submission could
walk up the stack and read the plaintext, the plant key or the checker's own lists (R47-X1 did exactly that and
"passed" all three). Now:

  * the checker builds and scores every plant in ITS process;
  * your file is loaded by this module's runner in a CHILD process started as `python -I` (isolated mode: no
    PYTHON* environment variables, no user site-packages, no script directory on sys.path) with a minimal
    environment and the repo root as working directory;
  * the child receives, one call at a time over a pipe, only the arguments the challenge says you get
    (C8: a rune window; C9: C and K; C10: C and the printed lengths), never the plaintext, a key you are not
    owed, the seed or the checker's objects, and it returns only a number or a list of rune indices;
  * calls arrive in a random order drawn from os.urandom (independent of --seed), so "the first n calls are
    the positives" is not information a submission has.

What this does NOT stop: a deliberately hostile program running as your own user can still inspect other
processes (the parent's command line, its memory). That is not a gap in the checker's logic but in the
operating system's, and it is why every crossing is also code-reviewed before credit (CHALLENGES.md, How
sealing works). Your file may import the repo's public code (_heavy, skipdecode, lp, ...): sys.path in the
child holds challenges/ and the liber-primus source folders, as `import _common` sets them.
"""
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_ENV_KEEP = ("SYSTEMROOT", "SystemRoot", "PATH", "TEMP", "TMP", "WINDIR", "COMSPEC", "PATHEXT",
             "LANG", "LC_ALL", "HOME", "USERPROFILE", "NUMBER_OF_PROCESSORS")


class SubmissionError(RuntimeError):
    """The submission crashed, returned the wrong type, or the child died. Not a TypeError on purpose:
    benchmark/gates.run_all() swallows TypeError and silently falls back to the reference decoder."""


class SubmissionTimeout(SubmissionError):
    pass


class Sandbox:
    """sb = Sandbox(path, func, kind, attrs=("REGISTER",), timeout=None); sb.call(*args); sb.map(arg_tuples)

    kind: "float" (C8 score), "plain" (C9 decode: dict with plain_idx, or a list) or "list" (C10 attack).
    timeout: wall-clock seconds per call; on expiry the child is killed and restarted (fresh state) and the
    call raises SubmissionTimeout.
    """

    def __init__(self, path, func, kind, attrs=(), timeout=None):
        self.path, self.func, self.kind, self.attrs_req, self.timeout = os.path.abspath(path), func, kind, attrs, timeout
        self.calls = 0
        self._start()

    def _start(self):
        import queue
        import threading
        env = {k: os.environ[k] for k in _ENV_KEEP if k in os.environ}
        env["PYTHONIOENCODING"] = "utf-8"
        self.p = subprocess.Popen([sys.executable, "-I", os.path.join(HERE, "_sandbox.py"), "--child",
                                   self.path, self.func, self.kind, ",".join(self.attrs_req)],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=ROOT, env=env,
                                  text=True, encoding="utf-8", bufsize=1)
        self.q = queue.Queue()
        p, q = self.p, self.q

        def pump():
            for line in p.stdout:
                q.put(line)
            q.put(None)
        threading.Thread(target=pump, daemon=True).start()
        hello = self._read(timeout=120)
        if "e" in hello:
            self.close()
            raise SubmissionError(f"could not load {self.path}: {hello['e']}")
        self.attrs = hello.get("attrs", {})

    def _read(self, timeout=None):
        import queue
        try:
            line = self.q.get(timeout=timeout)
        except queue.Empty:
            self.p.kill()
            self._start()
            raise SubmissionTimeout(f"call exceeded {timeout} s; submission process restarted")
        if not line:
            raise SubmissionError(f"submission process exited (code {self.p.poll()})")
        return json.loads(line)

    def call(self, *args):
        self.p.stdin.write(json.dumps({"a": args}) + "\n")
        self.p.stdin.flush()
        self.calls += 1
        r = self._read(timeout=self.timeout)
        if "e" in r:
            raise SubmissionError(r["e"])
        return r["r"]

    def map(self, arg_tuples, on_error=None):
        """Call once per argument tuple, in a random order (os.urandom), results returned in input order.
        With on_error=callable(i, exc) a failed call yields its return value instead of raising."""
        order = list(range(len(arg_tuples)))
        random.SystemRandom().shuffle(order)
        out = [None] * len(arg_tuples)
        for i in order:
            try:
                out[i] = self.call(*arg_tuples[i])
            except SubmissionError as e:
                if on_error is None:
                    raise
                out[i] = on_error(i, e)
                if self.p.poll() is not None:
                    self._start()
        return out

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=10)
        except Exception:
            self.p.kill()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# ------------------------------------------------------------------ child side
def _coerce(kind, v):
    if kind == "float":
        x = float(v)
        if x != x:
            raise ValueError("score returned NaN")
        return x
    if kind == "plain" and isinstance(v, dict):
        v = v["plain_idx"]
    out = [int(x) for x in v]
    if any(not 0 <= x < 29 for x in out):
        raise ValueError("rune indices must be 0-28")
    return out


def _child(path, func, kind, attrs):
    real_out = os.fdopen(os.dup(1), "w", encoding="utf-8", newline="\n")
    os.dup2(2, 1)                              # anything the submission prints goes to stderr, not the pipe
    sys.stdout = sys.stderr
    sys.path.insert(0, HERE)
    import _common  # noqa: F401  (repo source folders on sys.path for the submission)
    import importlib.util

    def send(obj):
        real_out.write(json.dumps(obj) + "\n")
        real_out.flush()

    try:
        sys.path.insert(0, os.path.dirname(path))
        spec = importlib.util.spec_from_file_location("submission", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = getattr(mod, func)
        got = {a: str(getattr(mod, a)) for a in attrs if a and hasattr(mod, a)}
    except BaseException as e:                 # noqa: BLE001
        send({"e": f"{type(e).__name__}: {e}"})
        return
    send({"attrs": got})
    for line in sys.stdin:
        try:
            args = json.loads(line)["a"]
            send({"r": _coerce(kind, fn(*args))})
        except BaseException as e:             # noqa: BLE001
            send({"e": f"{type(e).__name__}: {e}"})


if __name__ == "__main__":
    if len(sys.argv) >= 5 and sys.argv[1] == "--child":
        _child(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5].split(",") if len(sys.argv) > 5 else [])
    else:
        print(__doc__)
