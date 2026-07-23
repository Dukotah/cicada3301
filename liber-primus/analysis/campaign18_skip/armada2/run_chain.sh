#!/bin/bash
cd /mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/campaign18_skip
export PYTHONUTF8=1
echo "[chain] start $(date)"
echo "[chain] 1/6 armada19 corpus"; python3 -u sweep.py --texts armada19 > RUN-armada19.log 2>&1 || echo "armada19 FAILED"
echo "[chain] 2/6 autokey+skip";    python3 -u armada2/run_full_new.py --mode autokey > RUN-autokey-full.log 2>&1 || echo "autokey FAILED"
echo "[chain] 3/6 numeric2";        python3 -u armada2/numeric2_skip.py --full > RUN-numeric2-full.log 2>&1 || echo "numeric2 FAILED"
echo "[chain] 4/6 keywords";        python3 -u armada2/keywords_skip.py --full > RUN-keywords-full.log 2>&1 || echo "keywords FAILED"
echo "[chain] 5/6 selfref";         python3 -u armada2/selfref_skip.py --full > RUN-selfref-full.log 2>&1 || echo "selfref FAILED"
echo "[chain] 6/6 interrupter+skip";python3 -u armada2/run_full_new.py --mode interrupter > RUN-interrupter-full.log 2>&1 || echo "interrupter FAILED"
echo "[chain] ALL DONE $(date)"
grep -l "CANDIDATES FOUND\|HIT " RUN-*.log 2>/dev/null && echo "[chain] >>> A LANE FOUND A CANDIDATE <<<" || echo "[chain] all lanes null"
