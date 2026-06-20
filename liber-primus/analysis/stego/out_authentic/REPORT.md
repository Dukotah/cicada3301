# Image-stego sweep report

Source: `data/relikd`  (56 images)

- distinct DQT fingerprints: 2  {'32386501afff': 33, 'a3a96add050f': 23}
- images with trailing-after-EOI: 0
- images with carved embedded sigs: 1
- images with EXIF: 0
- images with flagged strings: 1
- lossless (LSB-meaningful): 0

## Per-image anomalies (only rows with something)
- **p1.jpg** (667228B, sha f804fae06a): CARVE ['bzip2']
- **p24.jpg** (654761B, sha 62148ef272): STR ['base64-ish', 'base64-ish', 'base64-ish', 'base64-ish', 'base64-ish', 'base64-ish', 'base64-ish', 'base64-ish']

## NOTE
DCT-domain stego (OutGuess/F5/jsteg/steghide) is NOT testable here (needs a binary). Spatial LSB above is only meaningful for lossless images; for JPEG it is compression noise. Authentic originals + a Linux env with outguess/stegdetect needed to close that gap.