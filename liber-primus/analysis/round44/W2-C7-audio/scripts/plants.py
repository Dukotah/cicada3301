"""R44 W2-C7 — the four positive controls (PREREG section 7), run BEFORE any real target.

Plant audio is synthesized (seeded numpy), MP3-encoded by the declared local ffmpeg, then
fed through the IDENTICAL reduction + sweep code as the real artifacts.  Gate = ALL FOUR.
"""
import json
import os
import subprocess
import sys
import time
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c7lib as C                                   # noqa: E402
import mp3meta                                      # noqa: E402
import reduce as R                                  # noqa: E402

WORK = os.path.join(C.CELL, "work")
RES = os.path.join(C.CELL, "results")
SR = 44100
RNG = np.random.default_rng(3301)


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    s = (x * 32000).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(s.tobytes())


def to_mp3(wav, mp3):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav, "-ar", str(SR), "-ac", "1",
                    "-codec:a", "libmp3lame", "-b:a", "192k", mp3], check=True)


def grid_hit(best, cell, bar_ok, plain):
    hit = all(best.get(k) == v for k, v in cell.items())
    rec = bool(hit and best.get("decode") == list(map(int, plain)))
    return hit, rec, bool(best["pmax"] >= best["bar"]) and bar_ok


def main():
    t0 = time.time()
    os.makedirs(WORK, exist_ok=True)
    out = {"controls": [], "gate": None}

    # ---------------------------------------------------------------- PC1: PCM pad end-to-end
    noise = RNG.normal(0, 0.25, SR * 30)
    write_wav(os.path.join(WORK, "pc1.wav"), noise)
    to_mp3(os.path.join(WORK, "pc1.wav"), os.path.join(WORK, "pc1.mp3"))
    s1, pads1, man1 = R.reduce_file(os.path.join(WORK, "pc1.mp3"), "PC1")
    p1 = np.array(C.to_idx(C.PT1)[:240], dtype=np.int64)
    K = pads1["PC1:pcm_u8"][4096:4096 + 240].astype(np.int64)
    c1 = C.encipher(p1, K, "vigm")
    cnt, best, cross = C.sweep_page_P(c1, pads1)
    cell = dict(stream="PC1:pcm_u8", dir="fwd", cfg="vigm", mode="O", rot=4096)
    hit, rec, barok = grid_hit(best, cell, man1["pcm_deterministic"], p1)
    out["controls"].append(dict(
        name="PC1", planted=cell, n_decodes=cnt, pcm_deterministic=man1["pcm_deterministic"],
        grid_best={k: v for k, v in best.items() if k != "decode"},
        found_planted_cell=hit, plaintext_recovered=rec,
        passed=bool(hit and rec and barok)))

    # ---------------------------------------------------------------- PC2: onset intervals
    iv_star = RNG.integers(4, 29, 80).tolist()
    clicks = np.cumsum([40] + iv_star)              # onset hop positions
    total = (clicks[-1] + 100) * R.HOP
    x = RNG.normal(0, 0.004, total)                 # low noise floor (sets the MAD threshold)
    for h in clicks:
        s = h * R.HOP
        t = np.arange(1200) / SR
        x[s:s + 1200] += 0.85 * np.exp(-t * 900) * np.sin(2 * np.pi * 1500 * t)
    write_wav(os.path.join(WORK, "pc2.wav"), x)
    to_mp3(os.path.join(WORK, "pc2.wav"), os.path.join(WORK, "pc2.mp3"))
    s2, _, man2 = R.reduce_file(os.path.join(WORK, "pc2.mp3"), "PC2")
    got = s2["PC2:onset_iv"]
    nmatch = sum(1 for a, b in zip(got, iv_star) if a == b)
    frac = nmatch / len(iv_star)
    key2 = np.array([C.MAPPINGS["m1"](k) for k in got], dtype=np.int64)
    p2 = np.array(C.to_idx(C.PT2)[:200], dtype=np.int64)
    kk = key2[(7 + np.arange(len(p2))) % len(key2)]
    c2 = C.encipher(p2, kk, "beau")
    cnt2, best2, _ = C.sweep_page_S(c2, s2)
    cell2 = dict(stream="PC2:onset_iv", dir="fwd", map="m1", cfg="beau", mode="R", rot=7)
    hit2, rec2, barok2 = grid_hit(best2, cell2, True, p2)
    out["controls"].append(dict(
        name="PC2", planted=cell2, n_decodes=cnt2, designed_vs_recovered=f"{nmatch}/{len(iv_star)}",
        recovered_frac=round(frac, 3), reduction_ok=bool(frac >= 0.90),
        grid_best={k: v for k, v in best2.items() if k != "decode"},
        found_planted_cell=hit2, plaintext_recovered=rec2,
        passed=bool(frac >= 0.90 and hit2 and rec2 and barok2)))

    # ---------------------------------------------------------------- PC3: spectral peaks
    b_star = RNG.integers(40, 901, 70).tolist()
    seg, gap = int(0.150 * SR), int(0.030 * SR)
    xs = [np.zeros(SR // 2)]
    for b in b_star:
        f = b * SR / R.NFFT
        t = np.arange(seg) / SR
        env = np.minimum(1, t / 0.005) * np.minimum(1, (seg / SR - t) / 0.005)
        xs.append(0.7 * env * np.sin(2 * np.pi * f * t))
        xs.append(np.zeros(gap))
    x3 = np.concatenate(xs) + RNG.normal(0, 0.003, sum(len(v) for v in xs))
    write_wav(os.path.join(WORK, "pc3.wav"), x3)
    to_mp3(os.path.join(WORK, "pc3.wav"), os.path.join(WORK, "pc3.mp3"))
    s3, _, man3 = R.reduce_file(os.path.join(WORK, "pc3.mp3"), "PC3")
    got3 = s3["PC3:spec_peak"]
    nm3 = sum(1 for a, b in zip(got3, b_star) if a == b)
    fr3 = nm3 / len(b_star)
    key3 = np.array([C.MAPPINGS["m2"](k) for k in got3], dtype=np.int64)
    p3 = np.array(C.to_idx(C.PT3)[:240], dtype=np.int64)
    kk3 = key3[np.arange(len(p3)) % len(key3)]
    c3 = C.encipher(p3, kk3, "vigp_atb")
    cnt3, best3, _ = C.sweep_page_S(c3, s3)
    cell3 = dict(stream="PC3:spec_peak", dir="fwd", map="m2", cfg="vigp_atb", mode="R", rot=0)
    hit3, rec3, barok3 = grid_hit(best3, cell3, True, p3)
    out["controls"].append(dict(
        name="PC3", planted=cell3, n_decodes=cnt3, designed_vs_recovered=f"{nm3}/{len(b_star)}",
        recovered_frac=round(fr3, 3), reduction_ok=bool(fr3 >= 0.90),
        grid_best={k: v for k, v in best3.items() if k != "decode"},
        found_planted_cell=hit3, plaintext_recovered=rec3,
        passed=bool(fr3 >= 0.90 and hit3 and rec3 and barok3)))

    # ---------------------------------------------------------------- PC4: frame walker + frame-size key
    walker_ok, checks = True, []
    for name, path in [("PC1", os.path.join(WORK, "pc1.mp3"))] + list(C.ART.items()):
        w = mp3meta.walk(path)
        pk = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                             "-count_packets", "-show_entries", "stream=nb_read_packets",
                             "-of", "csv=p=0", path], stdout=subprocess.PIPE, check=True)
        nff = int(pk.stdout.decode().strip().rstrip(","))
        ok = abs(w["n_frames_total"] - nff) <= max(2, 0.01 * nff) and w["sample_rate"] == 44100
        checks.append(dict(file=name, walker_frames=w["n_frames_total"], ffprobe_packets=nff,
                           sample_rate=w["sample_rate"], xing=w["xing_frame"],
                           resyncs=w["resyncs"], ok=bool(ok)))
        walker_ok &= ok
    key4 = np.array([C.MAPPINGS["m1"](k) for k in s1["PC1:frame_sz"]], dtype=np.int64)
    p4 = np.array(C.to_idx(C.PT1)[:240], dtype=np.int64)
    kk4 = key4[(11 + np.arange(len(p4))) % len(key4)]
    c4 = C.encipher(p4, kk4, "vigm")
    cnt4, best4, _ = C.sweep_page_S(c4, s1)
    cell4 = dict(stream="PC1:frame_sz", dir="fwd", map="m1", cfg="vigm", mode="R", rot=11)
    hit4, rec4, barok4 = grid_hit(best4, cell4, True, p4)
    out["controls"].append(dict(
        name="PC4", planted=cell4, n_decodes=cnt4, walker_checks=checks,
        walker_ok=bool(walker_ok),
        grid_best={k: v for k, v in best4.items() if k != "decode"},
        found_planted_cell=hit4, plaintext_recovered=rec4,
        passed=bool(walker_ok and hit4 and rec4 and barok4)))

    out["gate"] = "passed" if all(c["passed"] for c in out["controls"]) else "FAILED"
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(RES, "plants.json"), "w"), indent=1)
    print(json.dumps([{k: c[k] for k in ("name", "passed")} for c in out["controls"]]))
    print("GATE:", out["gate"], out["elapsed_s"], "s")


if __name__ == "__main__":
    main()
