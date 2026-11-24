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
# R3b follow-up: frozen score_r3b.py on a scratch copy (key, codes, contracts symlinked for the quote check)
mkdir -p "$S/b/plan" "$S/b/mining/key" "$S/b/packages/r3b_blind"; cp plan/score_r3b.py "$S/b/plan/"; cp mining/key/r3b_key.csv "$S/b/mining/key/"
for d in packages/r3b_*; do mkdir -p "$S/b/$d"; cp "$d"/codes_*.csv "$S/b/$d/" 2>/dev/null; done
for d in packages/r3b_blind/D*; do ln -s "$B/$d" "$S/b/packages/r3b_blind/$(basename "$d")"; done
( cd "$S/b" && /usr/bin/python3 -I -B plan/score_r3b.py --root "$S/b" --out "$S/b/r3b_scores.csv" > "$S/b/r3b_score_output.txt" 2>&1 ) || { echo "R3b scorer FAILED"; fail=1; }
for f in r3b_score_output.txt r3b_scores.csv; do
  if cmp -s "$S/b/$f" "plan/$f"; then echo "OK   $f byte-identical"
  elif [ -f packages/r3b_blind/WITHHELD.sha256 ] && [ "$f" = r3b_score_output.txt ] && \
       diff <(grep -v 'EXPLORATORY quote validity' "$S/b/$f") <(grep -v 'EXPLORATORY quote validity' "plan/$f") >/dev/null; then
    echo "EXPLAINED $f: only exploratory quote-validity lines differ (contracts of licence-withheld items absent in this archive)"
  else echo "DIFF $f"; diff "$S/b/$f" "plan/$f" | head -5; fail=1; fi
done
( cd "$B" && /usr/bin/python3 -I -B plan/test_score_r3b.py > "$S/selftest_b.txt" 2>&1 ) && echo "OK   R3b scorer self-test" || { echo "FAIL R3b self-test"; fail=1; }
( cd "$B" && /usr/bin/python3 -I -B plan/test_score_r3.py > "$S/selftest.txt" 2>&1 ) && echo "OK   scorer self-test" || { echo "FAIL scorer self-test"; tail -5 "$S/selftest.txt"; fail=1; }
[ $fail = 0 ] && echo "R3 REPRODUCTION OK" || echo "R3 REPRODUCTION FAILED"
exit $fail
