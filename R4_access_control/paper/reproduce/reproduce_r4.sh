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
# R4b follow-up: frozen score_r4b.py via the documented D1 normalisation (plan/r4b_score_with_D1.sh), output to scratch
bash plan/r4b_score_with_D1.sh "$S" > "$S/r4b_score_output.txt" 2>&1 || { echo "R4b scorer FAILED"; fail=1; }
for f in r4b_score_output.txt r4b_scores.csv; do
  if cmp -s "$S/$f" "plan/$f"; then echo "OK   $f byte-identical"
  elif [ -f packages/r4b_blind/WITHHELD.sha256 ] && [ "$f" = r4b_score_output.txt ] && \
       diff <(grep -v 'EXPLORATORY locator validity' "$S/$f") <(grep -v 'EXPLORATORY locator validity' "plan/$f") >/dev/null; then
    echo "EXPLAINED $f: only the exploratory locator-validity lines differ (contracts of licence-withheld items are absent in this archive)"
  else echo "DIFF $f"; diff "$S/$f" "plan/$f" | head -5; fail=1; fi
done
/usr/bin/python3 -I -B plan/test_score_r4b.py > "$S/selftest_b.txt" 2>&1 && echo "OK   R4b scorer self-test ($(tail -1 "$S/selftest_b.txt"))" || { echo "FAIL R4b self-test"; fail=1; }
/usr/bin/python3 -I -B plan/test_score_r4.py > "$S/selftest.txt" 2>&1 && echo "OK   scorer self-test ($(tail -1 "$S/selftest.txt"))" || { echo "FAIL scorer self-test"; fail=1; }
[ $fail = 0 ] && echo "R4 REPRODUCTION OK" || echo "R4 REPRODUCTION FAILED"
exit $fail
