# Ciphers & Stego — Technique Reference + Tooling

A working reference for the cryptographic/steganographic methods 3301 used, with notes on tooling you'd actually run.

Source writeup: `research/05-crypto-techniques.md`.

## Techniques index (filled by research run)
- Image steganography: `outguess`, `steghide`
- Book / running-key ciphers (literary keys: Mabinogion, Agrippa, The King in Yellow, Self-Reliance)
- Classical substitution: Caesar / Vigenère / Atbash
- Gematria Primus runic alphabet (rune ↔ letter ↔ prime)
- Gematria / numerology, Magic Squares
- Prime numbers & Euler's totient as keystream material
- PGP signatures (authentication of genuine 3301 messages)
- Tor hidden services, QR codes, audio spectrograms

## Handy tooling (to verify locally)
```
# stego extract
outguess -r image.jpg out.txt
steghide extract -sf image.jpg

# PGP verify a 3301 message
gpg --verify message.asc
```
