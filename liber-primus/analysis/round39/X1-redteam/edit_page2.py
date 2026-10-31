"""Round 39 X1: second page edit pass (I1 V2 page-null rows; row count)."""
import sys
sys.dont_write_bytecode = True
p = r"C:\Users\Jeff\cicada3301\liber-primus\MEASURED-CEILING.md"
raw = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in raw else "\n"
t = raw.replace("\r\n", "\n")


def rep(old, new):
    global t
    assert t.count(old) == 1, (old[:70], t.count(old))
    t = t.replace(old, new)


rep("(261 rows after the X1 audit)", "(262 rows after the X1 audit)")
rep("232 renders (58 pages x 4 variants); 174-render variant-limited diagnostic; the three above-null renders were viewed and are random walks",
    "232 renders (58 pages x 4 variants); 174-render variant-limited diagnostic; the three above-null renders were viewed and are random walks; Round 39: V2 page-matched nulls (within-line, within-word; 200 draws; 50 windows of page 0, 24-31 distinct), the 58 V2 renders not re-scored")
rep("Planted-glyph detection 1.0 (D2) but realised FPR 0.16 (V2 29/50, V3 3/50), so the control failed",
    "Planted-glyph detection 1.0 (D2) but realised FPR 0.16 (V2 29/50, V3 3/50), so the control failed; Round 39 null A: detection 0.875-1.0 but FPR 15/50 (0.30), null B: leak 0.21 and 29-gon detection 3/40 (FPR 0.22); the control failed again")
rep("[[R37-C2-U8-GEOMETRY]] [[R38-I1-GLYPH-RECOGNIZER]] | **inconclusive** (V1/V3/V4 at chance level as a diagnostic, not evidence; V2 unmeasured)",
    "[[R37-C2-U8-GEOMETRY]] [[R38-I1-GLYPH-RECOGNIZER]] [[R39-I1-V2-PAGE-NULL]] | **inconclusive** (V1/V3/V4 at chance level as a diagnostic, not evidence; V2 unmeasurable by this recognizer family after two page-matched nulls)")
rep("a page-matched null (shuffle within line and word, keeping interrupters) brings V2 FPR to 0.05 or below; the pre-registered D2 revision is run",
    "a different recognizer family, or a null preserving local rune-pair statistics, brings V2 FPR to 0.05 or below on windows from many pages; the R38 pre-registered D2 revision (reweight plus turning-function term) is run (it has still not been run)")
rep("V2 render FPR 0.16; `SEAL_PASS=false` | unmeasured | [[R38-I1-GLYPH-RECOGNIZER]] [[R37-C2-U8-GEOMETRY]]",
    "V2 render FPR 0.16 (Round 38) and 0.30 / 0.22 under the Round 39 page-matched nulls; `SEAL_PASS=false` | unmeasured | [[R38-I1-GLYPH-RECOGNIZER]] [[R39-I1-V2-PAGE-NULL]] [[R37-C2-U8-GEOMETRY]]")
rep("a page-matched null for V2; a seal that reaches", "a recognizer family or null that calibrates V2 (the Round 39 page-matched nulls failed); a seal that reaches")
t = t.rstrip("\n") + "\n<!-- pin: R39-I1-V2-PAGE-NULL | 15/50 -->\n"
open(p, "w", encoding="utf-8", newline="").write(t.replace("\n", nl))
print("ok")
