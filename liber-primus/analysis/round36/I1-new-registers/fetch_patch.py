"""PROPOSED (not applied) addition to liber-primus/data/fetch_sources.py: `--r36` fetches the Round 36 I1 corpora
(Greek Nestle 1904, Hebrew WLC, Norse Heimskringla) into data/keys/r36/<corpus>/ and verifies every sha256/size.
Paste after ensure_r19_corpora and add to __main__:   if "--r36" in sys.argv: ensure_r36_corpora(force=force)
Data only; never executed. Source of truth for the table: analysis/round36/I1-new-registers/fetch_log.json.
NOTE: heimskringla.no is a live wiki; if a page is re-edited the sha256 check will (correctly) refuse it.
"""
R36_CORPORA = {
    "greek_nestle1904": [
        ('Matthew-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Matthew-ap.xhtml',
         "351a15993ab3edd95722ac7ab23348bdd0c45e9d3884c5c022b3b166615d7213", 271520),
        ('Mark-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Mark-ap.xhtml',
         "66e09a519f26d1f578495c108ec029e6d2e16483be5e2a67019d6e4ef4a8619b", 169525),
        ('Luke-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Luke-ap.xhtml',
         "ab9e24268d06ae19303b373a4f4a227bd90d2a826f1219a00423da5fcb6b3450", 287062),
        ('John-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/John-ap.xhtml',
         "9db036d9b75f0e1e83fdc2b1d4dba7bae810106472151677444e082d71b913a3", 214018),
        ('Acts-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Acts-ap.xhtml',
         "062c37d8aec9ea5858414e22a99c607973a5519c4e9f7c62d94badc7f73cb504", 286589),
        ('Romans-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Romans-ap.xhtml',
         "b5c55bff8381c2f787ca02898b15a170f242d13c9781a840a445e8b945a944ad", 109342),
        ('1-Corinthians-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/1-Corinthians-ap.xhtml',
         "29adfbfec208ada63649b02ee702e1a4e942a6c64d8a90d4d6d4b58aaaea5228", 102029),
        ('2-Corinthians-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/2-Corinthians-ap.xhtml',
         "01dc9683a3d303b09bd5872747c989700a862dbddfc71ee29f9a0fa1e7721e35", 69921),
        ('Galatians-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Galatians-ap.xhtml',
         "bc284b6a46a10a046ada7a885de57087b6dd596cf8aaec2d5462e1b816a87da0", 37167),
        ('Ephesians-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Ephesians-ap.xhtml',
         "072165256c4b1bf3111136595577eeb08e6176cd2f726a3ad78a25771efec15f", 39666),
        ('Philippians-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Philippians-ap.xhtml',
         "1595674014882e3085f2bc3503f636d808b66a9a5a2a359041b1928fff5ca1d5", 27268),
        ('Colossians-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Colossians-ap.xhtml',
         "cc2628c28a8dd233fb875d408e4116fcc0c5b2e5ce1bcad7ec44c89ea6f1fc2f", 26607),
        ('1-Thessalonians-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/1-Thessalonians-ap.xhtml',
         "1641a15dd85f55f60c3eaa26e5d9cb7dd81a06b0f1852e80982ced9a2e075aeb", 25782),
        ('2-Thessalonians-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/2-Thessalonians-ap.xhtml',
         "5671c0a4f687a47658322b32e085b489e4929fa3ae3ff2d0678982e1cdcd2256", 15782),
        ('1-Timothy-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/1-Timothy-ap.xhtml',
         "907da93785045940589e9c92ff7ed8e47304c24bcb023c00cc7c8fe1a1ddd4bd", 29491),
        ('2-Timothy-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/2-Timothy-ap.xhtml',
         "8d87adfeff58ade40124411872ad4679589da0a8c9d1cced8d23afa42e9f5268", 22607),
        ('Titus-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Titus-ap.xhtml',
         "28b1b91c1171e3277158000cb74b2052d94a404008f17539cd8249f812321fc0", 14487),
        ('Philemon-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Philemon-ap.xhtml',
         "a515e595877fc8898a46c271a3e34f5ce234060c449c354baba6acdb4a836bce", 8271),
        ('Hebrews-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Hebrews-ap.xhtml',
         "9cfe820d7db365aff3b1824495daf8c7a4434092e307165f17544fad61773186", 88069),
        ('James-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/James-ap.xhtml',
         "a1dca6ad572758211388f23db1478b03c064594d55ad0749f726de3fded0224b", 29712),
        ('1-Peter-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/1-Peter-ap.xhtml',
         "aac999c16019091186b3d248c45bde26167392fd11d07c65b05fce3278f5b202", 35271),
        ('2-Peter-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/2-Peter-ap.xhtml',
         "01aa905a9e3aeae77e0896ed03d8a0eff7f3e6943d1c59f052a36ca07c4e50c8", 20538),
        ('1-John-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/1-John-ap.xhtml',
         "ec395f1c4e24d5bc7c8f2485a46e51489d7e7ecb54f88b7fda30e953b342d79a", 31451),
        ('2-John-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/2-John-ap.xhtml',
         "eff8a91b94255f61d34d6d24bb548d13063d7b2223ec7dbe29e7db86d439441b", 6810),
        ('3-John-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/3-John-ap.xhtml',
         "2220c039b058df3c3ff742e76b2d61e9567b3faf16fe72aa95892d54506abe24", 6791),
        ('Jude-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Jude-ap.xhtml',
         "32dbdef104cc22b2810e9925d7e68d3be0d6c0e37c2e206d09619a67d80de613", 10664),
        ('Revelation-ap.xhtml', 'https://raw.githubusercontent.com/biblicalhumanities/Nestle1904/master/xhtml/Revelation-ap.xhtml',
         "1c365b8e4e18cb9053cff694df5fc40e79732b74109186adcab232a9479cd528", 166142),
    ],
    "hebrew_wlc": [
        ('Gen.xml', 'https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Gen.xml',
         "0526e5c9a5fb4d907847645f954ed3d1268fa69decbd872056cedd2668d86449", 1859928),
        ('Exod.xml', 'https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Exod.xml',
         "04868367cdacb6ccdc61488e923e20f918172042e6437842a0621f63ac5b847f", 1524391),
        ('Lev.xml', 'https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Lev.xml',
         "e21e70265c9ef500182f8ccb4f4e1186e5a79e1169d24cef23cc479baf07b191", 1085066),
        ('Num.xml', 'https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Num.xml',
         "02e4febfcc027d10b3e35e4f091eae67a40d26f37b6254faac6b4af053fe4896", 1496830),
        ('Deut.xml', 'https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Deut.xml',
         "04f8087442a1e67a631cd70f2ac4e42fe0a780ae132edb165a3a29f3f290358f", 1315399),
        ('Josh.xml', 'https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Josh.xml',
         "a066200ab2269c0a86a2e9ba119a3d0fce8c5f7ecc44bb53ec134b83dffc6006", 919916),
        ('Judg.xml', 'https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Judg.xml',
         "3b3a909f04041dbd52dc6b7293a96ce75d94db8a90fdeda878943db7b8fac57f", 904347),
    ],
    "norse_heimskringla": [
        ('Egils_saga_Skalla-Grímssonar.html', 'https://heimskringla.no/wiki/Egils_saga_Skalla-Gr%C3%ADmssonar',
         "e8ab4d8a4bfd2f7f0a142b4cda540490418f4e7ae8affdc1d0636ddcf5daffd2", 450084),
        ('Eyrbyggja_saga.html', 'https://heimskringla.no/wiki/Eyrbyggja_saga',
         "47b1c0cdc9f2f93533205bf576cafef8f324a1c12f237f81f513c4707248a745", 302611),
        ('Völsunga_saga.html', 'https://heimskringla.no/wiki/V%C3%B6lsunga_saga',
         "9151ff63ca799acd7855b79be267c56a551069bc63782fd5090ba7aab12eff78", 181050),
        ('Ynglinga_saga.html', 'https://heimskringla.no/wiki/Ynglinga_saga',
         "00c7e0a91b6a528c533bdbd921a72c0c27aa8da19eb68d4937c355453f1c1175", 100301),
        ('Gunnlaugs_saga_ormstungu.html', 'https://heimskringla.no/wiki/Gunnlaugs_saga_ormstungu',
         "c939ba3f75bea19757dbde1962eb02819ebf5fc258950b082867c74bcf577af5", 95263),
        ('Hrafnkels_saga_Freysgoða.html', 'https://heimskringla.no/wiki/Hrafnkels_saga_Freysgo%C3%B0a',
         "afca90b24883bbae0711abb25e9eee8aff43ed559a4bbde79761cda02daa7ad9", 83991),
        ('Gísla_saga_Súrssonar.html', 'https://heimskringla.no/wiki/G%C3%ADsla_saga_S%C3%BArssonar',
         "f2bcf903ae916a66386a4636aebbaca8035bf3a7899a866513b7faa4790c549c", 177400),
        ('Fóstbræðra_saga.html', 'https://heimskringla.no/wiki/F%C3%B3stbr%C3%A6%C3%B0ra_saga',
         "ab8d46869c682b9d07b65c4d6eddecc752a83c00f07f18b1c32d5519e530e0c6", 271062),
    ],
}


def ensure_r36_corpora(force=False, verbose=True):
    import hashlib
    root = os.path.join(HERE, "keys", "r36")
    for sub, items in R36_CORPORA.items():
        os.makedirs(os.path.join(root, sub), exist_ok=True)
        for fn, url, sha, n in items:
            dst = os.path.join(root, sub, fn)
            if os.path.exists(dst) and not force and hashlib.sha256(open(dst, "rb").read()).hexdigest() == sha:
                continue
            req = urllib.request.Request(url, headers={"User-Agent": "cicada3301-rig"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if hashlib.sha256(data).hexdigest() != sha or len(data) != n:
                raise RuntimeError(f"{url}: sha/size differs from the Round 36 I1 record")
            with open(dst, "wb") as f:
                f.write(data)
            if verbose:
                print(f"  fetched r36/{sub}/{fn} ({n} B, sha verified)")
