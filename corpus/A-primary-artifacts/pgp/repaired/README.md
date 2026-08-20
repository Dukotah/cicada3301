# pgp/repaired/ — derived files, NOT retrieved originals

Nothing in this directory is a retrieved artifact. Each file is a byte-level repair of a
mirror-damaged file kept elsewhere in this corpus, produced only to isolate the cause of a
verification failure. The damaged original is preserved unmodified at its original path and
its sha256 is the one recorded in `MANIFEST.json` / `SIGNATURES.json`.

## ky_2013-01-opening-book-code.repaired.asc

- Damaged original: `pgp/messages/ky_2013-01-opening-book-code.asc`
  sha256 `cbc0abbea8f36fdf30433806a3418b30ad06f21f60eeee212b1692e2d5c9811b`
  from `https://raw.githubusercontent.com/krisyotam/cicada3301/main/pgp/messages/2013-01-opening-book-code.asc`
- Repair applied: re-inserted the single empty line that RFC 4880 §7 requires between the
  cleartext armor headers (`Hash: SHA1`) and the start of the signed text. The krisyotam
  mirror's copy has no blank line there, so GnuPG parses the first body line
  `Welcome again.` as an armor header (`gpg: invalid armor header: Welcome again.`),
  removes it from the hashed text, and the digest no longer matches -> BADSIG.
  No other byte was touched.
- Repaired sha256 `bd6be7123f455d950177d465d5d6fdf02fcc46ae920971fe55daa4ba6adf5f5d`
- Result after repair: **Good signature**, RSA key `181F01E57A35090F`,
  SIG_ID `B4/S2U0VepM5G4Idm4YLjSo2aNs`, signature made 2013-01-03T04:33:29Z.
  Identical SIG_ID to the independently-sourced clean copy
  `pgp/messages/2013-01-opening-book-code.asc` (jaxonkuipers mirror), which verifies VALID
  as retrieved.

This is a defect in one mirror's transcription. It is not evidence about the authenticity of
the 3301 message. See `CONFLICTS-A.md` C-01.
