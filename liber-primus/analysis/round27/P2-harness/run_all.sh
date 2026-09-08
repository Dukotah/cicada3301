#!/usr/bin/env bash
# Round 27 / P2 -- run the full validation harness against the P1 C engine.
# Order is load-bearing: trust anchor first, then parity, drill, false-reject, repro, bench.
# Per-check exit codes: 0 PASS, 1 FAIL, 2 BLOCKED-ON-BINARY.
# Overall: exits 1 if ANY check FAILs; exits 2 if none fail but some are blocked; else 0.
# ACCEPTANCE RULE: the 2^32 sweep may not launch until every check reports PASS.

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
LP="$(cd "$HERE/../../.." && pwd)"

case "${GRIND27:-}" in
  *mock_engine.py) echo "REFUSING: GRIND27 points at mock_engine.py -- the mock is a" \
                        "harness self-test, not an acceptance target."; exit 1 ;;
esac

declare -A RESULT
overall=0
blocked=0

run_check () {
  local name="$1"; shift
  echo
  echo "================================================================"
  echo "== $name"
  echo "================================================================"
  "$@"
  local rc=$?
  case $rc in
    0) RESULT[$name]="PASS" ;;
    2) RESULT[$name]="BLOCKED-ON-BINARY"; blocked=1 ;;
    *) RESULT[$name]="FAIL (rc=$rc)"; overall=1 ;;
  esac
}

# 0. Trust anchor -- if this fails, STOP: nothing else means anything.
echo "== trust anchor: tests/validate.py"
( cd "$LP" && python3 tests/validate.py > /tmp/p2_validate.out 2>&1 )
if grep -q "ALL VALIDATIONS PASSED" /tmp/p2_validate.out; then
  RESULT[validate.py]="PASS"
  echo "PASS: ALL VALIDATIONS PASSED"
else
  echo "FATAL: tests/validate.py did not pass -- STOPPING. Output:"
  tail -20 /tmp/p2_validate.out
  exit 1
fi

cd "$HERE"
run_check check_vectors      python3 check_vectors.py --pyref
run_check check_drill        python3 check_drill.py
run_check check_false_reject python3 check_false_reject.py
run_check check_r25_repro    python3 check_r25_repro.py
run_check bench              python3 bench.py

echo
echo "================================================================"
echo "== HARNESS SUMMARY"
echo "================================================================"
for k in validate.py check_vectors check_drill check_false_reject check_r25_repro bench; do
  printf "  %-20s %s\n" "$k" "${RESULT[$k]:-NOT-RUN}"
done
if [ "$overall" -ne 0 ]; then
  echo "OVERALL: FAIL -- the C engine may NOT launch the 2^32 sweep."
  exit 1
elif [ "$blocked" -ne 0 ]; then
  echo "OVERALL: BLOCKED-ON-BINARY -- python-side checks green; rerun when P1 lands."
  exit 2
fi
echo "OVERALL: PASS -- acceptance gates V1/V2/false-reject/R25-repro/bench all green."
exit 0
