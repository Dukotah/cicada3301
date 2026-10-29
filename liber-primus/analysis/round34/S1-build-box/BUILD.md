# S1 build box - exact commands (Ubuntu 24.04/26.04, gcc >= 13, 2 vCPU)

## Item 1: engines
```bash
sudo apt-get install -y gcc make python3-numpy
cd liber-primus/analysis/round27/P1-engine
# needs analysis/round19/I2/models/panel.npz (panel_lm.f32 sha recorded in engine.dat: 14a23d3619fa02df...) -- NOT in repo
python3 export_data.py
gcc -O2 -Wall -Wextra -std=gnu17 -fopenmp -ffp-contract=off -o grind27 grind27.c -lm
./grind27 --self-test            # must be PASS; FAILS on the round32 substitute panel
# resume tests on COPIES (never the real run/):
cp -r run /tmp/t_a
GRIND27_S2_CONTROL_OK=1 ./grind27 --plan ../sweep_plan.json --run-dir /tmp/t_a --seconds 4 --threads 6
# (b) add {"seed":123456789,"pmax":7.7} to /tmp/t_b/HIT-CANDIDATE.json hits, same command; inspect STATUS.json flagged_survivors
# (a2) set STATUS.json workers[0].cursor=35563800 and use a plan copy with S2 claim_bar 7.0
# If the self-test is unavailable, make a HARNESS COPY only:
sed 's/if (self_test(NULL)) { printf("ABORT/if (0 \&\& self_test(NULL)) { printf("ABORT/' grind27.c > grind27_nost.c
cd ../../round28/L4 && gcc -O2 -Wall -Wextra -std=gnu17 -fopenmp -ffp-contract=off -o grind28 grind28.c -lm
```

## Item 2: PHP 5.6
```bash
curl -LO https://www.php.net/distributions/php-5.6.40.tar.xz && tar xf php-5.6.40.tar.xz && cd php-5.6.40
CFLAGS='-O1 -w -std=gnu89' ./configure --disable-all --disable-cgi --without-pear
# gcc>=14 mis-detects: edit main/php_config.h -> '#define HAVE_POSIX_READDIR_R 1', drop HAVE_OLD_READDIR_R, '#define HAVE_CRYPT 1'
W='-Wno-error=implicit-int -Wno-error=implicit-function-declaration -Wno-error=incompatible-pointer-types -Wno-error=int-conversion'
make -j2 CC="gcc -std=gnu89 -w -fcommon -D_GNU_SOURCE $W"
sapi/cli/php -n t.php      # mt_srand(1); 20x mt_rand(); mt_srand(1); 20x mt_rand(0,28); implode (no json ext in --disable-all)
# compare to analysis/round32/B2-php-mtrand/php_mt.py: stream31(1,'php',20) and ks(1,'php','scale',20)
```

## Item 3: gs 9.04 vs 9.14
```bash
for v in 9.04 9.14; do curl -L -o g$v.tgz https://github.com/ArtifexSoftware/ghostpdl/archive/refs/tags/ghostpdl-$v.tar.gz
  mkdir src$v; tar xzf g$v.tgz -C src$v --strip-components=1; cp /usr/share/automake-*/config.guess /usr/share/automake-*/config.sub src$v/gs/; done
sudo apt-get install -y autoconf automake libtool imagemagick
cd src$v/gs && ./configure --without-x --disable-cups --disable-gtk --disable-fontconfig --without-ijs --without-libidn --disable-dynamic
W='-Wno-error=implicit-int -Wno-error=implicit-function-declaration -Wno-error=incompatible-pointer-types -Wno-error=int-conversion -Wno-error=return-mismatch -Wno-error=old-style-declaration'
make -j2 CC="gcc -std=gnu89 -fcommon -w -D_GNU_SOURCE -include unistd.h -include string.h $W"     # 9.14 ~2 min
# 9.04 also needs -DHAVE_SYS_TIME_H in CC and CCAUX="gcc -std=gnu89 -fcommon -w -D_GNU_SOURCE -DHAVE_SYS_TIME_H -include unistd.h -include string.h $W"; rerun make once (gconfig_.h race)
export GS_LIB=$PWD/Resource/Init:$PWD/lib:$PWD/iccprofiles:$PWD/Resource/Font:$PWD/Resource
bin/gs -q -dNOPAUSE -dBATCH -sDEVICE=jpeg -dJPEGQ=92 -r400 -sOutputFile=g.jpg ctrl.ps ; convert g.jpg -quality 92 im.jpg
md5sum g.jpg im.jpg ; compare -metric AE a.jpg b.jpg null:      # plus a JPEG marker walk (DQT/DHT/APPn/scan md5 per segment)
```
