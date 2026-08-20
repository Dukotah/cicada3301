#!/usr/bin/env python3
"""Locate the core decode loop in each vendored tool and extract the lines that
decide whether the KEY POINTER advances on an interrupter/skip.

RIGID      = key index advances once per ciphertext rune, unconditionally.
SKIP-AWARE = the tool can hold the key pointer (or search over which positions
             hold it) -- i.e. it can recover a key when interrupters are unknown.
"""
import os, re, json, datetime

E = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(E, "vendor")
CODE_EXT = {".py",".js",".ts",".go",".java",".c",".cc",".cpp",".h",".hpp",".rs",
            ".cs",".rb",".zig",".jl",".php",".kt",".scala",".hs",".lua",".pl",".m"}
SKIP_PAT = re.compile(
    r"interrupt|interupt|skip[_ ]?rune|isSkip|skipChar|keyIndex\s*(\+\+|\+=)?|"
    r"key_?(index|idx|pos|offset|pointer)|advance.*key|key.*advance|"
    r"beam|hill[_ ]?climb|simulated[_ ]?anneal|anneal|genetic|hold.*key|"
    r"F_?rune|rune\s*==\s*0|idx\s*==\s*0", re.I)
CIPHER_PAT = {
 "vigenere": re.compile(r"vigen", re.I),
 "beaufort": re.compile(r"beaufort", re.I),
 "atbash": re.compile(r"atbash", re.I),
 "caesar_shift": re.compile(r"\bcaesar\b|\bshift\b|\brot\d", re.I),
 "affine": re.compile(r"affine", re.I),
 "autokey": re.compile(r"auto[_ ]?key", re.I),
 "running_key": re.compile(r"running[_ ]?key|book[_ ]?cipher", re.I),
 "transposition": re.compile(r"transpos|columnar|rail[_ ]?fence|route[_ ]?cipher", re.I),
 "totient_prime": re.compile(r"totient|\bphi\b|prime", re.I),
 "playfair": re.compile(r"playfair", re.I),
 "hill_cipher": re.compile(r"hill[_ ]?cipher|matrix[_ ]?cipher", re.I),
 "substitution_search": re.compile(r"substitution", re.I),
 "gematria": re.compile(r"gematria", re.I),
 "hash_bruteforce": re.compile(r"sha512|sha-512|hashcat|deep[_ ]?web[_ ]?hash", re.I),
 "ngram_scoring": re.compile(r"quadgram|trigram|tetragram|ngram|bigram|chi[_ ]?squared|"
                             r"index[_ ]?of[_ ]?coincidence|\bIoC\b", re.I),
 "gpu": re.compile(r"\bcuda\b|opencl|__global__|kernel<<<|wgpu|compute[_ ]?shader", re.I),
 "llm_ml": re.compile(r"torch|tensorflow|transformers|openai|anthropic|\bLLM\b", re.I),
}
ADV_PAT = re.compile(r"(key\w*|k)\s*(?:\[[^\]]*\])?\s*(?:\+\+|\+=\s*1)|"
                     r"(?:key\w*|k)\s*=\s*\(?\s*(?:key\w*|k)\s*\+\s*1", re.I)

def walk(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in (".git","node_modules","__pycache__",
                  "vendor","dist","build",".venv","venv","target",".idea")]
        for fn in fns:
            if os.path.splitext(fn)[1].lower() in CODE_EXT:
                yield os.path.join(dp, fn)

def main():
    out = {}
    for d in sorted(os.listdir(V)):
        p = os.path.join(V, d)
        if not os.path.isdir(p): continue
        rec = {"n_code_files": 0, "ciphers": {}, "skip_evidence": [], "advance_lines": [],
               "loc": 0}
        for f in walk(p):
            try: t = open(f, encoding="utf-8", errors="ignore").read()
            except Exception: continue
            if len(t) > 3_000_000: continue
            rel = os.path.relpath(f, p).replace("\\","/")
            rec["n_code_files"] += 1
            rec["loc"] += t.count("\n")
            for name, pat in CIPHER_PAT.items():
                n = len(pat.findall(t))
                if n: rec["ciphers"][name] = rec["ciphers"].get(name, 0) + n
            for i, line in enumerate(t.splitlines(), 1):
                if len(line) > 300: continue
                if SKIP_PAT.search(line) and len(rec["skip_evidence"]) < 40:
                    rec["skip_evidence"].append(f"{rel}:{i}: {line.strip()[:200]}")
                if ADV_PAT.search(line) and len(rec["advance_lines"]) < 25:
                    rec["advance_lines"].append(f"{rel}:{i}: {line.strip()[:200]}")
        out[d] = rec
    json.dump({"generated_utc": datetime.datetime.now(datetime.timezone.utc)
               .strftime("%Y-%m-%dT%H:%M:%SZ"), "repos": out},
              open(os.path.join(E, "decoder_type_scan.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    for d, r in out.items():
        print(f"{d[:52]:52s} files={r['n_code_files']:4d} loc={r['loc']:7d} "
              f"skiphits={len(r['skip_evidence']):3d} ciphers={','.join(sorted(r['ciphers'])[:6])}")

if __name__ == "__main__":
    main()
