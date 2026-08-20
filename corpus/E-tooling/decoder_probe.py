#!/usr/bin/env python3
"""Evidence-gathering probe for the METHOD NOTE question:
    is each vendored solver's decoder RIGID or SKIP-AWARE?

Rigid  = consumes one keystream symbol per ciphertext rune, unconditionally.
Skip-aware = the interrupter rune (F / index 0) can consume no key symbol, or the
             search explores alternative skip placements (beam / branching /
             backtracking over interrupter positions).

This does not decide anything on its own -- it collects the code lines that a human
then reads. Output: decoder_probe.json (repo -> hits, with file:line and the line).
"""
import os, re, json, datetime

E = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(E, "vendor")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "target", "build",
             "dist", ".idea", "vendor"}
CODE_EXT = {".py", ".js", ".ts", ".go", ".c", ".h", ".cpp", ".cs", ".dart", ".rs",
            ".java", ".php", ".rb", ".pl", ".zig", ".jsx", ".ipynb", ".md", ".txt"}

PATTERNS = {
    # skip-aware signals
    "interrupter": r"\binterrupt(er|ors?|ed)?\b",
    "skip":        r"\bskip(ped|ping|_?rune|_?index|s)?\b",
    "beam":        r"\bbeam[_ ]?(search|width|size)\b|\bbeam\b",
    "branch":      r"\bbacktrack|\bbranch(ing)?\b|\bdfs\b|\bviterbi\b",
    "f_rune_special": r"F_?RUNE|rune\s*==\s*0|index\s*==\s*0\b|'ᚠ'|\"ᚠ\"",
    # cipher families
    "vigenere":    r"\bvigen[eè]re\b",
    "beaufort":    r"\bbeaufort\b",
    "autokey":     r"\bautokey\b",
    "runningkey":  r"\brunning[ _-]?key\b",
    "affine":      r"\baffine\b",
    "atbash":      r"\batbash\b",
    "caesar":      r"\bcaesar\b|\bshift[ _]?cipher\b",
    "totient":     r"\btotient\b|\bphi\(|\bprime[s]?\b",
    "playfair":    r"\bplayfair\b",
    "hill":        r"\bhill[ _]?cipher\b|\bmatrix[ _]?cipher\b",
    "transposition": r"\btranspos",
    "otp":         r"\bone[ -]?time[ -]?pad\b|\botp\b",
    "gpu":         r"\bcuda\b|\bopencl\b|\bcupy\b|\btorch\b|\bgpu\b",
    # scoring / null discipline
    "quadgram":    r"\bquad[ _]?gram|\btetragram\b",
    "ngram":       r"\bn[- _]?gram\b|\btrigram\b|\bbigram\b",
    "ioc":         r"\bindex of coincidence\b|\bIoC\b|\bio[c]\b",
    "chisq":       r"\bchi[ _-]?squ|\bchi2\b",
    "null_model":  r"\bnull (model|hypothesis|distribution)\b|\bshuffle\b|\bpermutation test\b",
    "positive_control": r"\bpositive control\b|\bplant(ed)? (a )?(known )?(signal|key)\b|\bself[- ]?test\b",
    # conclusions
    "conclusion":  r"\b(unsolvable|no solution|gave up|abandoned|dead end|failed to|"
                   r"did not find|found nothing|inconclusive|exhaust(ed|ive))\b",
}
COMPILED = {k: re.compile(v, re.I) for k, v in PATTERNS.items()}


def main():
    out = {"generated_utc": datetime.datetime.now(datetime.timezone.utc)
           .strftime("%Y-%m-%dT%H:%M:%SZ"), "repos": {}}
    for d in sorted(os.listdir(V)):
        p = os.path.join(V, d)
        if not os.path.isdir(p):
            continue
        hits = {k: [] for k in PATTERNS}
        counts = {k: 0 for k in PATTERNS}
        for root, dirs, files in os.walk(p):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for f in files:
                if os.path.splitext(f)[1].lower() not in CODE_EXT:
                    continue
                fp = os.path.join(root, f)
                try:
                    if os.path.getsize(fp) > 3_000_000:
                        continue
                    lines = open(fp, encoding="utf-8", errors="ignore").read().splitlines()
                except Exception:
                    continue
                rel = os.path.relpath(fp, p).replace("\\", "/")
                for i, ln in enumerate(lines, 1):
                    if len(ln) > 400:
                        ln = ln[:400]
                    for k, rx in COMPILED.items():
                        if rx.search(ln):
                            counts[k] += 1
                            if len(hits[k]) < 6:
                                hits[k].append(f"{rel}:{i}: {ln.strip()[:220]}")
        out["repos"][d] = {"counts": {k: v for k, v in counts.items() if v},
                           "hits": {k: v for k, v in hits.items() if v}}
    json.dump(out, open(os.path.join(E, "decoder_probe.json"), "w", encoding="utf-8"),
              indent=1)
    for d, r in out["repos"].items():
        c = r["counts"]
        sig = sum(c.get(k, 0) for k in ("interrupter", "skip", "beam", "branch", "f_rune_special"))
        print(f"{d:60s} skipsig={sig:5d}  {dict(sorted(c.items(), key=lambda x:-x[1])[:6])}")


if __name__ == "__main__":
    main()
