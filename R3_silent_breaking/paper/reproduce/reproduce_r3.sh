#!/bin/bash
# Re-run the frozen R3 scorer on a scratch copy of its inputs and compare with the committed outputs byte for byte.
# Also runs the scorer self-test and verifies the three freezes (plan, packages, outputs).
# Run from anywhere: bash paper/reproduce/reproduce_r3.sh     (needs only /usr/bin/python3, sha256sum; nothing upstream is executed)
set -uo pipefail
B="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$B" || exit 2
fail=0
/usr/bin/python3 -I -B paper/reproduce/check_freezes_r3.py || fail=1
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
mkdir -p "$S/plan" "$S/mining/key"
cp plan/score_r3.py "$S/plan/"; cp mining/key/r3_key.csv "$S/mining/key/"
for d in packages/r3_*; do mkdir -p "$S/$d"; cp "$d"/codes_*.csv "$S/$d/" 2>/dev/null; done
( cd "$S" && /usr/bin/python3 -I -B plan/score_r3.py --root "$S" --out "$S/r3_scores.csv" > "$S/r3_score_output.txt" ) || { echo "scorer FAILED"; fail=1; }
for f in r3_score_output.txt r3_scores.csv; do
  if cmp -s "$S/$f" "plan/$f"; then echo "OK   $f byte-identical"; else echo "DIFF $f"; diff "$S/$f" "plan/$f" | head -5; fail=1; fi
done
( cd "$B" && /usr/bin/python3 -I -B plan/test_score_r3.py > "$S/selftest.txt" 2>&1 ) && echo "OK   scorer self-test" || { echo "FAIL scorer self-test"; tail -5 "$S/selftest.txt"; fail=1; }
[ $fail = 0 ] && echo "R3 REPRODUCTION OK" || echo "R3 REPRODUCTION FAILED"
exit $fail
