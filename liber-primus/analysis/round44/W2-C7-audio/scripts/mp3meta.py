"""R44 W2-C7 — pure-python MPEG frame walker (no external tool; PREREG section 8).

walk(path) -> dict with per-frame byte sizes, bitrate indices, padding bits, sample rate,
resync/garbage accounting, and whether frame 0 is a Xing/Info header frame (excluded from
the streams if so).
"""
# MPEG-1 Layer III bitrate table (kbps) by index 0..15
BR_V1L3 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, -1]
# MPEG-2/2.5 Layer III
BR_V2L3 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, -1]
SR = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


def _id3v2_size(b):
    if b[:3] != b"ID3":
        return 0
    s = (b[6] << 21) | (b[7] << 14) | (b[8] << 7) | b[9]
    return 10 + s + (10 if b[5] & 0x10 else 0)


def walk(path):
    b = open(path, "rb").read()
    n = len(b)
    pos = _id3v2_size(b)
    frames, br_idx, padbits, resyncs, garbage = [], [], [], 0, 0
    sr_set, ver_set = set(), set()
    xing = False
    first = True
    while pos + 4 <= n:
        if b[pos] == 0xFF and (b[pos + 1] & 0xE0) == 0xE0:
            ver = (b[pos + 1] >> 3) & 3            # 3=MPEG1, 2=MPEG2, 0=MPEG2.5
            layer = (b[pos + 1] >> 1) & 3          # 1=Layer III
            bri = b[pos + 2] >> 4
            sri = (b[pos + 2] >> 2) & 3
            pad = (b[pos + 2] >> 1) & 1
            if ver != 1 and layer == 1 and 0 < bri < 15 and sri < 3:
                sr = SR[ver][sri]
                kbps = (BR_V1L3 if ver == 3 else BR_V2L3)[bri]
                spf = 1152 if ver == 3 else 576
                fsz = (spf // 8) * kbps * 1000 // sr + pad
                if fsz > 4 and pos + fsz <= n + 1:
                    if first:
                        head = b[pos:pos + min(fsz, 200)]
                        xing = (b"Xing" in head) or (b"Info" in head)
                        first = False
                    frames.append(fsz)
                    br_idx.append(bri)
                    padbits.append(pad)
                    sr_set.add(sr)
                    ver_set.add(ver)
                    pos += fsz
                    continue
        # tail tags
        if b[pos:pos + 3] == b"TAG" and n - pos == 128:
            break
        if b[pos:pos + 8] == b"APETAGEX":
            break
        pos += 1
        garbage += 1
        if frames:
            resyncs += 1
    start = 1 if xing else 0
    spf = 1152 if (ver_set == {3} or not ver_set) else 576
    sr = sr_set.pop() if len(sr_set) == 1 else sorted(sr_set)
    nfr = len(frames) - start
    return dict(n_frames_total=len(frames), xing_frame=bool(xing),
                frame_sizes=frames[start:], bitrate_indices=br_idx[start:],
                padding_bits=padbits[start:], sample_rate=sr, mpeg_versions=sorted(ver_set),
                samples_per_frame=spf, duration_ms=int(round(nfr * spf / (sr if isinstance(sr, int) else sr[0]) * 1000)),
                resyncs=resyncs, garbage_bytes=garbage)
