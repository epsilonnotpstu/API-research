#!/bin/bash
# Re-run the frozen R4 scorer on a scratch copy (key + codes) and compare with the committed outputs byte for byte;
# run the scorer self-test; verify the three freezes. Run from anywhere: bash paper/reproduce/reproduce_r4.sh
set -uo pipefail
B="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$B" || exit 2
fail=0
/usr/bin/python3 -I -B paper/reproduce/check_freezes_r4.py || fail=1
S="$(mktemp -d)"; trap 'rm -rf "$S"' EXIT
mkdir -p "$S/plan" "$S/mining/key"; cp plan/score_r4.py "$S/plan/"; cp mining/key/r4_key.csv "$S/mining/key/"
for d in packages/r4_*; do mkdir -p "$S/$d"; cp "$d"/codes_*.csv "$S/$d/" 2>/dev/null; done
( cd "$S" && /usr/bin/python3 -I -B plan/score_r4.py --root "$S" --out "$S/r4_scores.csv" > "$S/r4_score_output.txt" 2>&1 ) || { echo "scorer FAILED"; fail=1; }
for f in r4_score_output.txt r4_scores.csv; do
  if cmp -s "$S/$f" "plan/$f"; then echo "OK   $f byte-identical"; else echo "DIFF $f"; diff "$S/$f" "plan/$f" | head -5; fail=1; fi
done
/usr/bin/python3 -I -B plan/test_score_r4.py > "$S/selftest.txt" 2>&1 && echo "OK   scorer self-test ($(tail -1 "$S/selftest.txt"))" || { echo "FAIL scorer self-test"; fail=1; }
[ $fail = 0 ] && echo "R4 REPRODUCTION OK" || echo "R4 REPRODUCTION FAILED"
exit $fail
