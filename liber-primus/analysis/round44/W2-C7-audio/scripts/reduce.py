"""R44 W2-C7 — the frozen reductions (PREREG section 8) for one mp3 file.

reduce_file(path) -> (streams dict for battery S, pads dict for battery P, manifest entry).
Onsets: win 1024 hop 512 energy, half-wave flux, local max above median+3*MAD, >=4-hop gap.
Spectral: FFT-4096 Hann at onset_sample+512, argmax bin 1..2047.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c7lib as C                                   # noqa: E402
import mp3meta                                      # noqa: E402

HOP, WIN, NFFT = 512, 1024, 4096
MIN_GAP = 4                                         # hops
SIGMA_K = 6.0                                       # one-sided z threshold (addendum A1)


def onsets_from_s16(x):
    """x: int16 mono samples -> (onset hop indices, inter-onset intervals in hops)."""
    f = x.astype(np.float64) / 32768.0
    nfr = max(0, (len(f) - WIN) // HOP + 1)
    if nfr < 3:
        return np.array([], dtype=int), []
    idx = np.arange(nfr)[:, None] * HOP + np.arange(WIN)[None, :]
    e = (f[idx] ** 2).sum(axis=1)
    # PREREG addendum A1 (2026-11-10, before any real-target run): UNRECTIFIED energy diff
    # with a one-sided robust-sigma threshold; the frozen half-wave median+3*MAD threshold
    # is degenerate (median/MAD ~ 0 when >=50% of rectified flux is exactly 0) and failed
    # plant PC2/PC3 at the reduction leg (plants.json.pregate).
    d = e[1:] - e[:-1]
    sigma = 1.4826 * np.median(np.abs(d)) + 1e-12
    thr = SIGMA_K * sigma
    on = []
    for i in range(1, len(d) - 1):
        if d[i] > thr and d[i] >= d[i - 1] and d[i] >= d[i + 1]:
            if not on or i - on[-1] >= MIN_GAP:
                on.append(i)
    on = np.array(on, dtype=int)
    iv = np.diff(on).tolist()
    return on, iv


def spectral_peaks(x, onset_hops):
    f = x.astype(np.float64) / 32768.0
    w = np.hanning(NFFT)
    bins = []
    for h in onset_hops:
        s = h * HOP + HOP
        seg = f[s:s + NFFT]
        if len(seg) < NFFT:
            seg = np.pad(seg, (0, NFFT - len(seg)))
        mag = np.abs(np.fft.rfft(seg * w))
        bins.append(int(np.argmax(mag[1:2048]) + 1))
    return bins


def reduce_file(path, name):
    # --- PCM (declared decoder; determinism kill-check PREREG Q5 ii)
    cmd8, u8a = C.ffmpeg_pcm(path, "u8")
    _, u8b = C.ffmpeg_pcm(path, "u8")
    cmd16, s16a = C.ffmpeg_pcm(path, "s16le")
    _, s16b2 = C.ffmpeg_pcm(path, "s16le")
    det = (C.sha256(u8a) == C.sha256(u8b)) and (C.sha256(s16a) == C.sha256(s16b2))
    u8 = np.frombuffer(u8a, dtype=np.uint8)
    s16bytes = np.frombuffer(s16a, dtype=np.uint8)
    s16 = np.frombuffer(s16a, dtype="<i2")
    pads = {name + ":pcm_u8": (u8.astype(np.int64) % 29).astype(np.int8),
            name + ":pcm_s16bytes": (s16bytes.astype(np.int64) % 29).astype(np.int8),
            name + ":pcm_s16samp": (s16.astype(np.int64) % 29).astype(np.int8)}
    # --- derived short streams
    on, intervals = onsets_from_s16(s16)
    specs = spectral_peaks(s16, on)
    meta = mp3meta.walk(path)
    digits = "".join(str(v) for v in [os.path.getsize(path), meta["n_frames_total"] - (1 if meta["xing_frame"] else 0),
                                      meta["sample_rate"], max(meta["bitrate_indices"], default=0),
                                      meta["duration_ms"], len(s16)])
    streams = {name + ":onset_iv": intervals,
               name + ":spec_peak": specs,
               name + ":frame_sz": meta["frame_sizes"],
               name + ":br_idx": meta["bitrate_indices"],
               name + ":meta_digits": [int(d) for d in digits]}
    man = dict(file=path, sha256=C.sha256(path), ffmpeg_cmds=[cmd8, cmd16],
               pcm_u8_sha256=C.sha256(u8a), pcm_s16le_sha256=C.sha256(s16a),
               pcm_deterministic=bool(det), n_u8=len(u8), n_s16_samples=len(s16),
               n_onsets=int(len(on)), meta={k: v for k, v in meta.items()
                                            if k not in ("frame_sizes", "bitrate_indices", "padding_bits")},
               stream_lengths={k: len(v) for k, v in streams.items()})
    return streams, pads, man
