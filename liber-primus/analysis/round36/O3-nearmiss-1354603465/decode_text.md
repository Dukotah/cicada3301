# decode_text.md - best decodes (rune indices -> R32 transliteration letters, lower-case, no word breaks) + calibration plant

Candidate = bash 4.2 LP64 seed 1354603465, `%29`, keyskip2, sign -1, o=0, c0=0, beam_w 400, v3 panel_max. Plant = SAME seed/key, English test-half plaintext, enc_pair(supp .83), same pipeline.


## Candidate L=120  pmax9 7.07 (LP1_REAL)  pmax12 7.07 (LP1_REAL)  n_skips 8  IoC*N 1.015  mds 17  h2 0.199  zlib 0.833  wordhits 3

Panel z (9): EN_MODERN 5.5, EN_KJV 6.3, LP1_REAL 7.1, LATIN 1.7, OE 5.7, DE 4.3, CY 3.8, EN_HALFVOWEL 4.3, EN_NOVOWEL 1.0

```
eaoeeahewasedorowosbymoengngeoellraeaimfwgodyoathonerahmonleahriaoaeeobjtherahmaengntingsuhlburffhdg
dlingeopfeofthjeulneahsusoexthutccoageddaneaw
```

## Candidate L=240  pmax9 6.54 (LP1_REAL)  pmax12 6.54 (LP1_REAL)  n_skips 18  IoC*N 1.008  mds 16  h2 0.344  zlib 0.729  wordhits 3

Panel z (9): EN_MODERN 3.9, EN_KJV 6.1, LP1_REAL 6.5, LATIN 0.2, OE 4.6, DE 3.3, CY 3.1, EN_HALFVOWEL 3.1, EN_NOVOWEL 2.0

```
eaoeeahewasedorowosbymoengngeoellraeaimfwgodyoathonerahmonleahriaoaeeobjtherahmaengntingsuhlburffhdg
dlingeopfeofthjeulneahsusoexthutccoageddaneaweainglcllwhccmseoiapeameautuiaoeeothusltiphfofiaoaethoi
atlooenmaegneobgaheothumeeothgiceohaegiaaethirjdlngootsoenoeexwsotaeoepeathjeeahathngwnyfthnxpriagfu
nj
```

## Candidate L=262  pmax9 6.64 (LP1_REAL)  pmax12 6.64 (LP1_REAL)  n_skips 16  IoC*N 0.987  mds 16  h2 0.364  zlib 0.718  wordhits 3

Panel z (9): EN_MODERN 3.5, EN_KJV 5.8, LP1_REAL 6.6, LATIN 0.2, OE 4.5, DE 3.1, CY 2.9, EN_HALFVOWEL 3.0, EN_NOVOWEL 1.7

```
eaoeeahewasedorowosbymoengngeoellraeaimfwgodyoathonerahmonleahriaoaeeobjtherahmaengntingsuhlburffhdg
dlingeopfeofthjeulneahsusoexthutccoageddaneaweainglcllwhccmseoiapeameautuiaoeeothusltiphfofiaoaethoi
atlooenmaegneobgaheothumeeothgiceohaegiaaethirjdlngootsoenoeexwsotaeoepeathjeeahathngwnyfthnxpriagym
bthntjdljrtbjngtggthycpudag
```

## Candidate L=729  pmax9 5.75 (LP1_REAL)  pmax12 5.75 (LP1_REAL)  n_skips 26  IoC*N 0.991  mds 16  h2 0.764  zlib 0.652  wordhits 5

Panel z (9): EN_MODERN 2.7, EN_KJV 4.3, LP1_REAL 5.8, LATIN -0.2, OE 2.6, DE 0.9, CY 1.7, EN_HALFVOWEL 2.0, EN_NOVOWEL 1.1

```
eaoeeahewasedorowosbymoengngeoellraeaimfwgodyoathonerahmonleahriaoaeeobjtherahmaengntingsuhlburffhdg
dlingeopfeofthjeulneahsusoexthutccoageddaneaweainglcllwhccmseoiapeameautuiaoeeothusltiphfofiaoaethoi
atlooenmaegneobgaheothumeeothgiceohaegiaaethirjdlngootsoenoeexwsotaeoepeathjeeahathngwnyfthnxpriagym
bthntjdljrtbjngtggthycpudaghiyiaiugoejymyriarfpgtogdyodnggthriaaebthithrxsnaejclfpyngnuntwtgxiaeoeng
reomhdsuaedejeongooeaeibreaiwerfoeleoxiththmaeodseaaeamnbceobgcpaiojngfwialliaaeigjngaeiaedngpingrle
aiaxrhnjeoiaeaingedeasceaiuyrjwmhetixotrheodjeotewmyshmwoethpuxihngcyeahantwscngbhaeofwiathuiaxfnpae
 ...[truncated at 600 letters]
```

## PLANT EN_MODERN_a L=120  pmax9 13.76 (EN_MODERN)  pmax12 13.76 (EN_MODERN)  recovery 0.992  wordhits 8

decode:
```
rysthesonofbryssethachfromthehilloftheblaccfernbraceinnorthbritainandgrudlwyngotrbwlchandcyfwlchands
efwlchthesonsofcleddyfcyfw
```
truth:
```
rysthesonofbryssethachfromthehilloftheblaccfernbraceinnorthbritainandgrudlwyngorrbwlchandcyfwlchands
efwlchthesonsofcleddyfcyfw
```

## PLANT EN_MODERN_a L=262  pmax9 22.66 (LP1_REAL)  pmax12 22.66 (LP1_REAL)  recovery 1.000  wordhits 19

decode:
```
rysthesonofbryssethachfromthehilloftheblaccfernbraceinnorthbritainandgrudlwyngorrbwlchandcyfwlchands
efwlchthesonsofcleddyfcyfwlchthegrandsonsofcleddyfdifwlchtheirthreeshieldswerethreegleamingglitterer
stheirthreespearswerethreepointedpiercerstheirthreeswordswerethreegrindinggashersg
```
truth:
```
rysthesonofbryssethachfromthehilloftheblaccfernbraceinnorthbritainandgrudlwyngorrbwlchandcyfwlchands
efwlchthesonsofcleddyfcyfwlchthegrandsonsofcleddyfdifwlchtheirthreeshieldswerethreegleamingglitterer
stheirthreespearswerethreepointedpiercerstheirthreeswordswerethreegrindinggashersg
```

## PLANT EN_MODERN_b L=120  pmax9 20.39 (LP1_REAL)  pmax12 20.39 (LP1_REAL)  recovery 1.000  wordhits 14

decode:
```
tiltheycametoauastopenplainwhereintheysawagreatcastlewhichwasthefairestofthecastlesoftheworldandthey
journeyedthatdayuntiltheeueni
```
truth:
```
tiltheycametoauastopenplainwhereintheysawagreatcastlewhichwasthefairestofthecastlesoftheworldandthey
journeyedthatdayuntiltheeueni
```

## PLANT EN_MODERN_b L=262  pmax9 31.69 (LP1_REAL)  pmax12 31.69 (LP1_REAL)  recovery 1.000  wordhits 42

decode:
```
tiltheycametoauastopenplainwhereintheysawagreatcastlewhichwasthefairestofthecastlesoftheworldandthey
journeyedthatdayuntiltheeueningandwhentheythoughttheywerenightothecastletheywerenonearertoitthanthey
hadbeeninthemorningandthesecondandthethirddaytheyjourneyedandeuenthenscarcelycouldtheyrea
```
truth:
```
tiltheycametoauastopenplainwhereintheysawagreatcastlewhichwasthefairestofthecastlesoftheworldandthey
journeyedthatdayuntiltheeueningandwhentheythoughttheywerenightothecastletheywerenonearertoitthanthey
hadbeeninthemorningandthesecondandthethirddaytheyjourneyedandeuenthenscarcelycouldtheyrea
```

## PLANT LP1_pages0-2 L=120  pmax9 27.54 (LP1_REAL)  pmax12 27.54 (LP1_REAL)  recovery 1.000  wordhits 9

decode:
```
awarnngbelieuenothngfromthisboocexceptwhatyoucnowtobetruetestthecnowledgefindyourtruthexperienceyour
deathdonoteditorchangethisbooc
```
truth:
```
awarnngbelieuenothngfromthisboocexceptwhatyoucnowtobetruetestthecnowledgefindyourtruthexperienceyour
deathdonoteditorchangethisbooc
```

## PLANT LP1_pages0-2 L=262  pmax9 40.84 (LP1_REAL)  pmax12 40.84 (LP1_REAL)  recovery 1.000  wordhits 22

decode:
```
awarnngbelieuenothngfromthisboocexceptwhatyoucnowtobetruetestthecnowledgefindyourtruthexperienceyour
deathdonoteditorchangethisboocorthemessagecontainedwithineitherthewordsortheirnumbersforallissacreds
omewisdomtheprimesaresacredthetotientfunctianissacredallthngsshouldbeencryptedcnow
```
truth:
```
awarnngbelieuenothngfromthisboocexceptwhatyoucnowtobetruetestthecnowledgefindyourtruthexperienceyour
deathdonoteditorchangethisboocorthemessagecontainedwithineitherthewordsortheirnumbersforallissacreds
omewisdomtheprimesaresacredthetotientfunctianissacredallthngsshouldbeencryptedcnow
```