#!/bin/bash
# periodic checkpoint uploader: tars results and posts to litterbox (72h), appends "ts url sha size" to ~/up.log
D=~/liber-primus/analysis/round38/S2-php-sandbox; cd $D
FILES="sweep_rows.jsonl sweep_state.json keep_rows.json sweep_summary_final.json control.json fpr12_php.json smoke.json *.log t_*.txt driver.status"
ck() { tar czf /tmp/ck.tar.gz $(ls $FILES 2>/dev/null) 2>/dev/null; S=$(sha256sum /tmp/ck.tar.gz | cut -c1-16); Z=$(stat -c%s /tmp/ck.tar.gz)
  U=$(curl -s -m 300 -F reqtype=fileupload -F time=72h -F fileToUpload=@/tmp/ck.tar.gz https://litterbox.catbox.moe/resources/internals/api.php); echo "$(date +%s) $U $S $Z $1" >> ~/up.log; }
while [ ! -f driver.status ]; do sleep 400; [ -f driver.status ] || ck mid; done
sleep 5; ck final
