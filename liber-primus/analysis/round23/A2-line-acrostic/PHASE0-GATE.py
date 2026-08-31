"""PHASE 0 GATE (doctrine mechanics R2 / Aiming-Test Q1) — for the LINE/WORD geometry.

Two gates, both must PASS with recovery = 1.000 before any real acrostic is scored:

  P0.1 (recognizer power on a planted LINE-FIRST acrostic):
    Build a control page with the SAME line count and SAME per-line word/rune
    widths as a real solved page, fill it with runes drawn i.i.d. from the solved
    letter histogram, then OVERWRITE the first rune of each line so the line-first
    acrostic spells a known English message. Confirm the line-first read is
    recovered as a survivor above its size-matched null bar.

  P0.2 (word-first family): same, but plant on the first rune of each WORD.

  P0.3 (extractor structural check): confirm the geometry extractor reproduces the
    known printed-line count of page 01 (10 lines) AND that its line-first read of
    the REAL page 01 equals 'ABETFEDOEF' (the first letters of the ten visible
    English lines A WARNING / BELIEVE / EXCEPT / TEST / FIND / EXPERIENCE / DO /
    OR / EITHER / FOR). This is the P0.2-style hand-anchored validation that the
    line/word extractor is faithful before any acrostic means anything.

PASS iff P0.1 recovery == 1.0 AND P0.2 recovery == 1.0 AND P0.3 holds.
"""
import os, sys, math, random
import lib_geom as G

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 3301
FPR = 0.001

# a clearly-English message (letters only). Long enough to fill every line/word.
_MSG = ("THEKEYTOTHEBOOKISFINDTHETRUTHWITHINYOURSELFANDTESTTHEKNOWLEDGE"
        "BELIEVENOTHINGEXCEPTWHATYOUKNOWTOBETRUEALLISSACRED") * 6

_ALPHA_SRC = None


def solved_letter_pool():
    global _ALPHA_SRC
    if _ALPHA_SRC is None:
        pool = ""
        for _, _, lines in G.load_all_pages():
            pool += G.page_flat_letters(lines)
        _ALPHA_SRC = pool
    return _ALPHA_SRC


def build_control_shape(real_lines, seed):
    """Return a control 'lines' structure with the SAME shape (line count, words
    per line, runes per word) as real_lines, filled with i.i.d. single-letter
    tokens from the solved histogram. i.i.d. sampling carries NO message and NO
    periodic structure, so the only structure a read can find is a planted one."""
    src = solved_letter_pool()
    rnd = random.Random(seed)
    out = []
    for line in real_lines:
        wl = []
        for word in line:
            wl.append([rnd.choice(src) for _ in word])
        out.append(wl)
    return out


def plant_line_first(lines, msg):
    """Overwrite the first token of each line with successive chars of msg."""
    out = [[list(w) for w in line] for line in lines]
    for i, line in enumerate(out):
        if line and line[0] and i < len(msg):
            line[0][0] = msg[i]
    return out


def plant_word_first(lines, msg):
    """Overwrite the first token of each word with successive chars of msg."""
    out = [[list(w) for w in line] for line in lines]
    j = 0
    for line in out:
        for word in line:
            if word and j < len(msg):
                word[0] = msg[j]
                j += 1
    return out


def score_reads(lines):
    """Return dict {read_name: (letters, score_norm)} for all four acrostic reads."""
    reads = {
        "line_first": G.line_first_tokens(lines),
        "line_last": G.line_last_tokens(lines),
        "word_first": G.word_first_tokens(lines),
        "word_last": G.word_last_tokens(lines),
    }
    out = {}
    for name, toks in reads.items():
        s = G.tokens_to_letters(toks)
        out[name] = (s, G.scorer().score_norm(s) if s else 0.0)
    return out


def null_bar_for_read(control_shape, read_name, length, n_shuffles=1000,
                      seed=SEED, fpr=FPR):
    """Null: shuffle the solved letter pool and take a size-matched contiguous
    slice; 99.9th percentile of its English score. Length-keyed."""
    rnd = random.Random(seed)
    pool = list(solved_letter_pool())
    scores = []
    for _ in range(n_shuffles):
        rnd.shuffle(pool)
        scores.append(G.scorer().score_norm("".join(pool[:length])))
    scores.sort()
    idx = min(len(scores) - 1, int(math.ceil((1 - fpr) * len(scores))) - 1)
    return scores[idx]


def run():
    pages = G.load_all_pages()
    # use the longest page (06) as the control shape so plants fully occupy reads
    shape_page = max(pages, key=lambda p: sum(len(w) for line in p[2] for w in line))
    real_lines = shape_page[2]
    n_lines = len(real_lines)
    n_words = sum(len(line) for line in real_lines)
    print(f"[phase0] control shape from page {shape_page[0]}: "
          f"{n_lines} lines, {n_words} words")

    ok_all = True

    # ---- P0.1 line-first plant ----
    ctrl = build_control_shape(real_lines, SEED)
    planted = plant_line_first(ctrl, _MSG)
    reads = score_reads(planted)
    lf_letters, lf_score = reads["line_first"]
    bar = null_bar_for_read(ctrl, "line_first", len(lf_letters))
    # winner = read with the max score
    winner = max(reads.items(), key=lambda kv: kv[1][1])[0]
    rec1 = (winner == "line_first") and (lf_score > bar)
    print(f"[phase0] P0.1 LINE-FIRST plant: read='{lf_letters[:40]}' "
          f"score={lf_score:.3f} bar={bar:.3f} winner={winner} "
          f"-> {'RECOVERED' if rec1 else 'MISS'}")
    ok_all = ok_all and rec1

    # ---- P0.2 word-first plant ----
    ctrl2 = build_control_shape(real_lines, SEED + 1)
    planted2 = plant_word_first(ctrl2, _MSG)
    reads2 = score_reads(planted2)
    wf_letters, wf_score = reads2["word_first"]
    bar2 = null_bar_for_read(ctrl2, "word_first", len(wf_letters))
    winner2 = max(reads2.items(), key=lambda kv: kv[1][1])[0]
    rec2 = (winner2 == "word_first") and (wf_score > bar2)
    print(f"[phase0] P0.2 WORD-FIRST plant: read='{wf_letters[:40]}' "
          f"score={wf_score:.3f} bar={bar2:.3f} winner={winner2} "
          f"-> {'RECOVERED' if rec2 else 'MISS'}")
    ok_all = ok_all and rec2

    # ---- P0.3 extractor structural check (hand-anchored) ----
    p01 = next(p for p in pages if p[0] == "Runes - 01.jpg")
    p01_lf = G.tokens_to_letters(G.line_first_tokens(p01[2]))
    p01_nlines = len(p01[2])
    rec3 = (p01_nlines == 10) and (p01_lf == "ABETFEDOEF")
    print(f"[phase0] P0.3 extractor check: page01 n_lines={p01_nlines} "
          f"line_first='{p01_lf}' (expect 10 / 'ABETFEDOEF') "
          f"-> {'OK' if rec3 else 'FAIL'}")
    ok_all = ok_all and rec3

    n_ok = sum([rec1, rec2, rec3])
    power = (rec1 + rec2) / 2.0  # recognizer power over the two planted families
    print(f"\n[phase0] recognizer recovery/power (line+word) = {int(rec1)+int(rec2)}/2 "
          f"= {power:.3f}")
    print(f"[phase0] all gates ({n_ok}/3):",
          "PASS" if ok_all else "FAIL (instrument/extractor not trustworthy)")
    return ok_all, power


if __name__ == "__main__":
    ok, _ = run()
    sys.exit(0 if ok else 1)
