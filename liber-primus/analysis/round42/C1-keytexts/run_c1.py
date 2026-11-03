"""R42 / C1 - the R35 keytexts (round12/C2/texts/) as running keys over the 55 unsolved LP2
pages, adjudicated under panel-R36 and judged against the standing free-null bar of record.
Honest-instrument re-run of the T-LEG H7xF4/H8xF4 cells.

Data-integrity gate FIRST: ~10 of the 33 fetched files are globalgrey 'Page Not Found' HTML
error pages, not the intended esoteric texts. Those are classified out and listed; only real
texts are swept, so the negative is not manufactured by feeding garbage.

Running key: transliterate each real text to rune indices (gp.keyword_to_indices on the letters),
then slide a window of length = page over the key stream from stride-sampled start offsets
(~OFFSETS per text), both signs, both atbash. Statistic per page = max panel-R36 pmax over the
whole (text x offset x sign x atb) grid; bar = bars_v3 'free' at the grid size.
"""
import json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis", "src", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))
from lp import gematria as gp                      # noqa
from run_stats import load_pages                   # noqa
import adjudicate as A                             # noqa
import bars_v3 as B                                # noqa

N = gp.N
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
TXT = os.path.join(LP, "analysis", "round12", "C2", "texts")
SIGNS, ATB = (1, -1), (0, 1)
OFFSETS = 150          # stride-sampled start positions per text (logged; no silent cap)
FREE_LS = (120, 240, 400, 729)


def is_corrupt(raw):
    return bool(re.search(r"(?i)<!doctype|<html|Page Not Found|globalgrey", raw[:400]))


def to_idxs(raw):
    letters = re.sub(r"[^A-Za-z]", "", raw).upper()
    out = []
    for ch in letters:
        try:
            out.extend(gp.keyword_to_indices(ch))
        except Exception:
            pass
    return out


def free_bar(Ngrid, L):
    cand = [x for x in FREE_LS if x <= L] or [120]
    return B.bar_v3(Ngrid, max(cand), "free")


def vig_running(c, key, start, sign, atb):
    Lk = len(key)
    if atb:
        return [(((N - 1) - c[i]) + sign * key[(start + i) % Lk]) % N for i in range(len(c))]
    return [(c[i] + sign * key[(start + i) % Lk]) % N for i in range(len(c))]


def offsets_for(keylen, pagelen):
    span = max(1, keylen - pagelen)
    if span <= OFFSETS:
        return list(range(span))
    stride = span // OFFSETS
    return list(range(0, span, stride))[:OFFSETS]


def main():
    t0 = time.time()
    pages = load_pages()[:-2]
    real, corrupt = [], []
    for f in sorted(os.listdir(TXT)):
        if not f.endswith(".txt"):
            continue
        raw = open(os.path.join(TXT, f), encoding="utf-8", errors="ignore").read()
        if is_corrupt(raw):
            corrupt.append(f)
            continue
        ki = to_idxs(raw)
        if len(ki) >= 60:
            real.append((f, ki))
    print(json.dumps({"real_texts": len(real), "corrupt_404": len(corrupt),
                      "corrupt_list": corrupt}))

    gbest = {"pmax": -99.0}
    per_page, crossers = [], []
    # approximate grid size for the bar: real texts x avg offsets x signs x atb
    grid = sum(min(OFFSETS, max(1, len(ki) - 240)) for _, ki in real) * len(SIGNS) * len(ATB)
    for pi, c in enumerate(pages):
        best = {"pmax": -99.0}
        for fname, ki in real:
            for st in offsets_for(len(ki), len(c)):
                for sign in SIGNS:
                    for atb in ATB:
                        r = A.adjudicate(vig_running(c, ki, st, sign, atb), pan=PAN)
                        if r["pmax"] > best["pmax"] and not r["degenerate"]:
                            best = {"pmax": r["pmax"], "preg": r["preg"], "text": fname,
                                    "start": st, "cfg": f"sign{sign:+d} atb{atb}",
                                    "degenerate": r["degenerate"]}
        bar = free_bar(grid, len(c))
        best.update(page=pi, L=len(c), bar=round(bar, 4),
                    clears=bool(best["pmax"] >= bar))
        per_page.append(best)
        if best["clears"]:
            crossers.append(best)
        if best["pmax"] > gbest["pmax"]:
            gbest = dict(best)
        if pi % 10 == 0:
            print(f"  page {pi}/{len(pages)} gbest {gbest['pmax']:.3f} "
                  f"({gbest.get('text')}) {time.time()-t0:.0f}s", flush=True)

    out = {"real_texts": len(real), "corrupt_404": len(corrupt), "corrupt_list": corrupt,
           "offsets_per_text": OFFSETS, "grid_size_for_bar": grid,
           "observed_global_best": gbest, "n_crossers": len(crossers),
           "crossers": crossers[:10],
           "verdict": "NEGATIVE" if not crossers else "CROSS - inspect",
           "per_page_best": [round(b["pmax"], 3) for b in per_page],
           "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "c1_results.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("real_texts", "corrupt_404", "observed_global_best",
          "n_crossers", "verdict", "grid_size_for_bar", "elapsed_s")}, indent=1))


if __name__ == "__main__":
    main()
