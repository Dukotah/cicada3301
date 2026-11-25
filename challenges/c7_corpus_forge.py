"""C7 checker: forge a Gematria-Primus reference corpus in a register nobody has covered (CHALLENGES.md, C7).

    python challenges/c7_corpus_forge.py --self-test                       # worked example (Latin, Aeneid) + a corrupted copy
    python challenges/c7_corpus_forge.py my_corpus/manifest.json --build   # write corpus.txt from your table
    python challenges/c7_corpus_forge.py my_corpus/manifest.json           # validate + place LP2 against it

A submission is a directory:
  manifest.json   language (ISO 639-3), register, provenance (title, author, edition, url, license,
                  source_sha256), source, table, and optional separators / sentence_marks / drop / normalize
  source.txt      the public-domain text, exactly as fetched (or "repo:<path>" for an in-repo text)
  corpus.txt      one sentence per line; words in runes, joined by '-'   (--build writes it from the table)

The TABLE maps source graphemes (after normalisation and casefold) to a space-separated list of GP tokens,
e.g. {"th": "TH", "θ": "TH", "ξ": "C S", "ing": "NG", "h": ""}. Matching is greedy, longest grapheme first.
Letters (Unicode L*) and marks (M*) must be consumed by the table or listed in `drop`; whitespace,
punctuation, digits and symbols separate words; `sentence_marks` (default ".!?") end a sentence.

The checker validates the manifest and provenance, re-derives a seeded sample of 500 sentences from the
table and requires them to equal corpus.txt, then measures the 2-rune-word share and the 9-class
word-length profile, and places LP2 (2,896 printed words, round46/L1-word-loader/words.py) against
1,000 windows of 2,896 words from your corpus: LP2's percentile, and the R46-P1 T3 G test (LP2's profile
vs the corpus's own window null, 99 % bar). It prints a JSON row ready to add to the reference table.

Exit 0 = valid corpus (the row says whether its register is new, i.e. whether it crosses the finish line).
"""
import argparse
import collections
import json
import math
import os
import random
import sys
import tempfile
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _heavy as H  # noqa: E402
import _common as C  # noqa: E402

VERSION = "c7/1"
LP2_WORDS = 2896
MIN_WORDS, MIN_SENTENCES = 20000, 1000
SAMPLE = 500
MAX_UNMAPPED = 0.001
N_WINDOWS = 1000
EXAMPLE = os.path.join(C.ROOT, "challenges", "examples", "c7_latin_aeneid", "manifest.json")

# (ISO 639-3, register) already placed by R45-W1 / R46-P1. Latin is covered for the classical register only.
COVERED = {"eng": "English (30 fresh + 8 R45 corpora: modern, archaic, translated, verse)",
           "deu": "German (Faust, de_2)", "cym": "Welsh (Mabinogion)", "ang": "Old English (Beowulf)",
           "lat": "Latin, classical (Aeneid, latin_218)", "x-cicada": "solved Cicada pages"}
LATIN_NEW_REGISTERS = ("ecclesiastical", "vulgate", "medieval", "neo-latin")
# R47-H2 label gate (fixes R47-X1 §3.4: Dracula labelled Old Norse "crossed"). A corpus is REJECTED if its GP
# bigram profile is within LABEL_TAU (Jensen-Shannon divergence, nats, first PROFILE_RUNES runes) of the English
# reference or of any covered language other than the one it claims. Calibrated (R47-H2 RESULTS §2): 15 English
# texts (modern to Tyndale) sit 0.014-0.049 from the English dev pool; Latin-Latin 0.019, German-German 0.017;
# every cross-language pair is >= 0.079 (Old English vs English). It is a sanity gate, not a language ID: a
# hand-tuned table can move a profile, and close relatives of English (Middle English, Scots) may be flagged
# legitimately. Maintainers review the source and table by hand before any credit.
LABEL_TAU = 0.06
PROFILE_RUNES = 150000
LABEL_REFS = {"eng": ["@english"],
              "lat": ["data/keys/armada19/virgil_aeneid_latin.txt", "analysis/latin/latin_218.txt"],
              "deu": ["analysis/round10b/B6-non-english-plaintext/corpora/de_faust.txt",
                      "analysis/round10b/B6-non-english-plaintext/corpora/de_2.txt"],
              "cym": ["data/keys/welsh/welsh_mabinogion.txt"],
              "ang": ["analysis/round10b/B6-non-english-plaintext/corpora/oe_beowulf.txt"]}
REQUIRED = ("language", "register", "provenance", "source", "table")
PROV_REQUIRED = ("title", "author", "url", "license", "source_sha256")


def fail(errs, msg):
    errs.append(msg)


# ------------------------------------------------------------------ derivation
def compile_table(table, errs):
    out = {}
    for g, v in table.items():
        if not g:
            fail(errs, "table has an empty grapheme key")
            continue
        toks = v.split()
        bad = [t for t in toks if t not in H.GP_TOKENS]
        if bad:
            fail(errs, f"table[{g!r}] = {v!r}: {bad} not GP tokens (allowed: {' '.join(H.GP_TOKENS)})")
            continue
        out[g] = [H.GP_TOKENS.index(t) for t in toks]
    return out


def derive(text, M, errs):
    """source text -> (sentences [[ [rune idx] per word ]], unmapped Counter, letters seen)."""
    norm = M.get("normalize", "NFC")
    text = unicodedata.normalize(norm, text)
    if M.get("casefold", True):
        text = text.casefold()
    table = compile_table(M["table"], errs)
    maxlen = max((len(k) for k in table), default=1)
    marks = set(M.get("sentence_marks", ".!?"))
    extra_sep = set(M.get("separators", ""))
    drop = set(M.get("drop", ""))
    drop_cats = set(M.get("drop_categories", []))
    sents, sent, word = [], [], []
    unmapped = collections.Counter()
    letters = 0
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        cat = unicodedata.category(ch)
        if ch in drop or cat in drop_cats:
            i += 1
            continue
        if ch in marks:
            if word:
                sent.append(word)
                word = []
            if sent:
                sents.append(sent)
                sent = []
            i += 1
            continue
        hit = None
        for L in range(min(maxlen, n - i), 0, -1):
            v = table.get(text[i:i + L])
            if v is not None:
                hit = (L, v)
                break
        if hit:
            word.extend(hit[1])
            letters += hit[0]
            i += hit[0]
            continue
        if ch in extra_sep or cat[0] in "ZPSNC":
            if word:
                sent.append(word)
                word = []
            i += 1
            continue
        unmapped[ch] += 1                      # a letter the table cannot read: dropped, counted
        letters += 1
        i += 1
    if word:
        sent.append(word)
    if sent:
        sents.append(sent)
    return sents, unmapped, letters


def line_of(sent):
    return "-".join(H.to_runes(w) for w in sent)


def parse_corpus_line(line):
    return [[H.RUNE_IDX[c] for c in w] for w in line.strip().split("-") if w]


# ------------------------------------------------------------------ loading
def load_manifest(path, errs):
    M = json.load(open(path, encoding="utf-8"))
    for k in REQUIRED:
        if k not in M:
            fail(errs, f"manifest missing '{k}'")
    prov = M.get("provenance", {})
    for k in PROV_REQUIRED:
        if not prov.get(k):
            fail(errs, f"provenance missing '{k}'")
    lic = str(prov.get("license", "")).lower()
    if "public domain" not in lic and "cc0" not in lic:
        fail(errs, f"provenance.license must be public domain or CC0, got {prov.get('license')!r}")
    return M


def source_path(M, mdir):
    s = M["source"]
    return os.path.join(C.ROOT, s[5:]) if s.startswith("repo:") else os.path.join(mdir, s)


def read_source(M, mdir, errs):
    p = source_path(M, mdir)
    if not os.path.exists(p):
        fail(errs, f"source not found: {p}")
        return None
    raw = open(p, "rb").read()
    got = __import__("hashlib").sha256(raw).hexdigest()
    want = M.get("provenance", {}).get("source_sha256", "")
    if want and got != want:
        fail(errs, f"source sha256 {got} != provenance.source_sha256 {want}")
    try:
        t = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        fail(errs, f"source is not UTF-8 ({e}); re-encode it and update source_sha256")
        return None
    if M.get("strip_gutenberg", False):
        t = H.strip_gutenberg(t)
    if M.get("start_after"):
        i = t.find(M["start_after"])
        if i < 0:
            fail(errs, f"start_after marker {M['start_after']!r} not in source")
            return None
        t = t[i + len(M["start_after"]):]
    if M.get("end_before"):
        i = t.find(M["end_before"])
        if i < 0:
            fail(errs, f"end_before marker {M['end_before']!r} not in source")
            return None
        t = t[:i]
    return t


def covered(M):
    lang = str(M.get("language", "")).lower()
    reg = str(M.get("register", "")).lower()
    if lang == "lat" and any(r in reg for r in LATIN_NEW_REGISTERS):
        return None
    return COVERED.get(lang)


# ------------------------------------------------------------------ label gate (R47-H2)
def bigram_profile(stream):
    import numpy as np
    x = np.asarray(stream[:PROFILE_RUNES], dtype=np.int64)
    c = np.full((H.N, H.N), 0.5)
    np.add.at(c, (x[:-1], x[1:]), 1)
    return c / c.sum()


def jsd(p, q):
    import numpy as np
    m = (p + q) / 2
    return float(0.5 * (p * np.log(p / m)).sum() + 0.5 * (q * np.log(q / m)).sum())


_REF = {}


def label_gate(M, words):
    """{ref language: JSD} and the list of references the corpus is indistinguishable from (excluding its own
    claimed language). English reference = the four English dev texts (_heavy.DEV_ENGLISH)."""
    lang = str(M.get("language", "")).lower()
    prof = bigram_profile([x for w in words for x in w])
    dists, hits = {}, []
    for ref, paths in LABEL_REFS.items():
        if ref not in _REF:
            st = []
            for p in paths:
                st += (H.english_stream() if p == "@english" else H.latin_text_to_idx(p))[:PROFILE_RUNES]
            _REF[ref] = bigram_profile(st)
        d = round(jsd(prof, _REF[ref]), 4)
        dists[ref] = d
        if ref != lang and d <= LABEL_TAU:
            hits.append(ref)
    return dists, hits


# ------------------------------------------------------------------ statistics (R46-P1 conventions)
def cls9(n):
    return min(n, 9) - 1


def counts9(L):
    c = [0] * 9
    for x in L:
        c[cls9(x)] += 1
    return c


def dist9(L):
    c = counts9(L)
    t = sum(c) + 4.5
    return [(x + 0.5) / t for x in c]


def G(L, q):
    c = counts9(L)
    n = len(L)
    return 2 * sum(x * math.log(x / (n * p)) for x, p in zip(c, q) if x)


def s2(L):
    return sum(1 for x in L if x == 2) / len(L)


def lp2_lengths():
    sys.path.insert(0, os.path.join(C.LP, "analysis", "round46", "L1-word-loader"))
    import words as W
    L = W.lp2().lengths
    assert len(L) == LP2_WORDS, len(L)
    return L


def place(lengths, seed):
    rng = random.Random(seed)
    lp2 = lp2_lengths()
    q = dist9(lengths)
    wins = []
    for _ in range(N_WINDOWS):
        a = rng.randrange(0, len(lengths) - LP2_WORDS + 1)
        wins.append(lengths[a:a + LP2_WORDS])
    ws2 = sorted(s2(w) for w in wins)
    lp2s2 = s2(lp2)
    pct = sum(1 for v in ws2 if v <= lp2s2) / len(ws2)
    gnull = sorted(G(w, q) for w in wins)
    bar = gnull[int(0.99 * (len(gnull) - 1))]
    g = G(lp2, q)
    return {"lp2_two_rune_share": round(lp2s2, 4), "corpus_two_rune_share": round(s2(lengths), 4),
            "window_two_rune_share_p01_p50_p99": [round(ws2[int(f * (len(ws2) - 1))], 4) for f in (.01, .5, .99)],
            "lp2_percentile_in_windows": round(pct, 4),
            "profile9_corpus": [round(x, 4) for x in dist9(lengths)],
            "profile9_lp2": [round(x, 4) for x in dist9(lp2)],
            "G_lp2_vs_corpus": round(g, 1), "G_window_bar99": round(bar, 1),
            "T3_verdict": "admitted" if g <= bar else "rejected",
            "T3_bar_scope": "within-text windows only: no between-text variance, so a single corpus's bar is "
                            "narrow and a 'rejected' is weaker than it looks (R46-P1 X1 caveat). Two corpora "
                            "of one register make a pooled bar."}


# ------------------------------------------------------------------ check
def check(manifest_path, build=False, seed=None, corpus_override=None, quiet=False, errs_out=None):
    errs = [] if errs_out is None else errs_out
    mdir = os.path.dirname(os.path.abspath(manifest_path))
    M = load_manifest(manifest_path, errs)
    src = read_source(M, mdir, errs) if "source" in M else None
    if src is None or any(e.startswith("manifest missing") for e in errs):
        return report(errs, None, quiet)
    sents, unmapped, letters = derive(src, M, errs)
    rate = sum(unmapped.values()) / max(1, letters)
    if rate > MAX_UNMAPPED:
        fail(errs, f"unmapped letters {rate:.3%} > {MAX_UNMAPPED:.1%}; add them to the table or 'drop': "
                   + ", ".join(f"{ch!r}({unicodedata.name(ch, '?')}) x{n}" for ch, n in unmapped.most_common(8)))
    cpath = corpus_override or os.path.join(mdir, M.get("corpus", "corpus.txt"))
    if build:
        with open(cpath, "w", encoding="utf-8", newline="\n") as f:
            for s in sents:
                f.write(line_of(s) + "\n")
        print(f"wrote {cpath}: {len(sents)} sentences")
    if not os.path.exists(cpath):
        fail(errs, f"corpus not found: {cpath} (run with --build to write it from the table)")
        return report(errs, None, quiet)
    lines = [ln.rstrip("\n") for ln in open(cpath, encoding="utf-8")]
    stray = sorted({c for ln in lines for c in ln if c not in H.RUNE_IDX and c != "-"})
    if stray:
        fail(errs, f"corpus.txt has non-rune characters {stray[:10]}")
    if len(lines) != len(sents):
        fail(errs, f"corpus.txt has {len(lines)} lines; the table derives {len(sents)} sentences")
    seed = H.resolve_seed(seed)
    rng = random.Random(seed)
    idx = rng.sample(range(min(len(lines), len(sents))), min(SAMPLE, len(lines), len(sents)))
    bad = [i for i in idx if lines[i] != line_of(sents[i])]
    if bad:
        i = bad[0]
        fail(errs, f"re-derivation mismatch on {len(bad)}/{len(idx)} sampled sentences; first at line {i + 1}:\n"
                   f"      corpus : {lines[i][:80]}\n      derived: {line_of(sents[i])[:80]}")
    words = [w for ln in lines for w in parse_corpus_line(ln)]
    if len(words) < MIN_WORDS or len(lines) < MIN_SENTENCES:
        fail(errs, f"too small: {len(words)} words / {len(lines)} sentences (need >= {MIN_WORDS} / {MIN_SENTENCES})")
    if errs:
        return report(errs, None, quiet)
    dists, hits = label_gate(M, words)
    if hits:
        fail(errs, f"label check: the corpus's GP bigram profile is within {LABEL_TAU} (JSD) of the "
                   f"{'/'.join(hits)} reference ({', '.join(f'{k} {dists[k]}' for k in hits)}), so it cannot be "
                   f"told apart from a covered register; its language label {M.get('language')!r} is not credible "
                   "as a new register. (Close relatives of English such as Middle English can trip this "
                   "legitimately: say so in the submission and the maintainers decide by hand.)")
        return report(errs, None, quiet)
    lengths = [len(w) for w in words]
    cov = covered(M)
    row = {"id": f"C7-{M['language']}-{M['register']}".replace(" ", "_"), "checker": VERSION, "seed": seed,
           "language": M["language"], "register": M["register"], "provenance": M["provenance"],
           "n_words": len(words), "n_sentences": len(lines), "unmapped_rate": round(rate, 5),
           "sample_rederived": f"{len(idx)}/{len(idx)}",
           **place(lengths, seed),
           "label_gate_jsd": dists, "label_gate_tau": LABEL_TAU,
           "register_already_covered": cov,
           "crosses_finish_line": cov is None}
    return report(errs, row, quiet)


def report(errs, row, quiet):
    if errs:
        print("C7 - FAIL")
        for e in errs:
            print("  - " + e)
        return 1, row
    if not quiet:
        print("C7 - corpus VALID\n")
        print(json.dumps(row, indent=1, ensure_ascii=False))
        print()
        if row["crosses_finish_line"]:
            print("NEW REGISTER: this crosses the C7 finish line, pending source and table review by the "
                  "maintainers (the label gate is a sanity check, not a language ID). Submit it (CHALLENGES.md).")
        else:
            print(f"Valid, but already covered: {row['register_already_covered']}. Not a crossing.")
    return 0, row


def _x1_cheat_check():
    """R47-X1's C7 cheat: English source with an Old Norse label, GP greedy table. Must FAIL (label gate)."""
    import shutil
    with tempfile.TemporaryDirectory() as td:
        M = json.load(open(EXAMPLE, encoding="utf-8"))
        M.update({"language": "non", "register": "Old Norse saga prose (R47-X1 cheat: actually Dracula)",
                  "source": "repo:liber-primus/data/keys/armada19/stoker_dracula.txt", "strip_gutenberg": True})
        for k in ("start_after", "end_before", "_comment"):
            M.pop(k, None)
        raw = open(os.path.join(C.ROOT, M["source"][5:]), "rb").read()
        M["provenance"] = dict(M["provenance"], source_sha256=__import__("hashlib").sha256(raw).hexdigest())
        mp = os.path.join(td, "manifest.json")
        json.dump(M, open(mp, "w", encoding="utf-8"))
        errs_seen = []
        code, _ = check(mp, build=True, seed=4700, corpus_override=os.path.join(td, "corpus.txt"), quiet=True,
                        errs_out=errs_seen)
        label = any(e.startswith("label check") for e in errs_seen)
        print("  " + ("FAILED on the label gate, as it must" if code == 1 and label else
                      f"NOT caught by the label gate (code {code}): {errs_seen}"))
        return (1 if code == 1 and label else 0), None


def self_test():
    print("C7 self-test: worked example (Latin, Aeneid, covered register) + a corrupted copy that must FAIL\n")
    with tempfile.TemporaryDirectory() as td:
        cp = os.path.join(td, "corpus.txt")
        code, row = check(EXAMPLE, build=True, seed=4700, corpus_override=cp)
        ok = code == 0 and row is not None and not row["crosses_finish_line"]
        lines = open(cp, encoding="utf-8").read().split("\n")
        for i in range(0, len(lines), 7):                      # flip one rune on every 7th line
            if lines[i]:
                c = lines[i][0]
                lines[i] = H.RUNES[(H.RUNE_IDX[c] + 1) % 29] + lines[i][1:]
        open(cp, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        print("\n-- corrupted copy (every 7th sentence altered) --")
        code2, _ = check(EXAMPLE, seed=4700, corpus_override=cp, quiet=True)
        ok = ok and code2 == 1
    print("\n-- label control: English (Dracula) labelled Old Norse (R47-X1's cheat) must FAIL the label gate --")
    code3, _ = _x1_cheat_check()
    ok = ok and code3 == 1
    print("\nSELF-TEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("manifest", nargs="?", help="path to your manifest.json")
    ap.add_argument("--build", action="store_true", help="write corpus.txt from source + table first")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test or not a.manifest:
        sys.exit(self_test())
    code, _ = check(a.manifest, build=a.build, seed=a.seed)
    sys.exit(code)


if __name__ == "__main__":
    main()
