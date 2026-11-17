#!/bin/bash
# Re-run every frozen R1 scorer on a scratch copy of 08_experiments and compare its outputs with the committed ones.
# Nothing in the working tree is modified. Needs only codes/labels/keys/scorers (no upstream code, no item excerpts).
# Usage: bash reproduce_scores.sh [WORKDIR]   (default: a new mktemp dir)
set -uo pipefail
SRC="$(cd "$(dirname "$0")/../../08_experiments" && pwd)"
W="${1:-$(mktemp -d)}"; mkdir -p "$W"; D="$W/08_experiments"
[ -e "$D" ] && { echo "refuse: $D exists"; exit 2; }
PY="/usr/bin/python3 -I -B"
# copy everything except bulky or upstream-content directories (scorers never read them)
tar -C "$SRC/.." -cf - \
  --exclude='08_experiments/E1_pilot' --exclude='08_experiments/E5_codemut' --exclude='08_experiments/_external' \
  --exclude='*/__pycache__' --exclude='08_experiments/E7_mining/key/t4[5-9]_evidence' --exclude='08_experiments/E7_mining/key/t50_evidence' \
  --exclude='08_experiments/E7_mining/key/*previews*' --exclude='08_experiments/E7_mining/pool2.json' --exclude='08_experiments/E7_mining/pool3.json' \
  --exclude='08_experiments/E7_mining/key/pool[23]_sources.json' --exclude='08_experiments/E7_mining/key/review*_evidence' \
  --exclude='08_experiments/E2_labelling/*/[KXWVUQ][0-9][0-9]' --exclude='08_experiments/E2_labelling/*/[KXWVUQ][0-9][0-9][0-9]' \
  08_experiments | tar -C "$W" -xf -
echo "workdir: $W ($(du -sh "$D" | cut -f1))"
fail=0
cmp_file(){  # committed file vs reproduced file (relative path); CSV compared after normalising line endings
  local rel=$1
  if [ ! -f "$D/$rel" ]; then echo "  MISSING  $rel"; fail=1; return; fi
  if diff -q <(tr -d '\r' < "$SRC/$rel") <(tr -d '\r' < "$D/$rel") > /dev/null; then echo "  SAME     $rel"; else echo "  DIFFERS  $rel"; fail=1; fi
}
cmp_out(){  # committed stdout file vs captured stdout
  local rel=$1 got=$2
  if diff -q <(tr -d '\r' < "$SRC/$rel") <(tr -d '\r' < "$got") > /dev/null; then echo "  SAME     $rel (stdout)"; else echo "  DIFFERS  $rel (stdout)"; fail=1; fi
}
run(){ local dir=$1; shift; (cd "$D/$dir" && $PY "$@") > "$W/out.txt" 2>&1; local rc=$?; [ $rc -eq 0 ] || { echo "  EXIT $rc  $dir $*"; tail -3 "$W/out.txt"; fail=1; }; }

# Committed CSVs are first removed from the copy, so a SAME result proves the scorer re-created them.
echo "== E6";  rm -f "$D/E6_realfix/e6_scores.csv";  run E6_realfix score_e6.py;  cmp_file E6_realfix/e6_scores.csv
echo "== E7";  rm -f "$D/E7_repairdir/e7_scores.csv"; run E7_repairdir score_e7.py; cmp_file E7_repairdir/e7_scores.csv
echo "== E8";  rm -f "$D/E8_blindprop/e8_scores.csv"; run E8_blindprop score_e8.py; cmp_file E8_blindprop/e8_scores.csv
echo "== E8b"; rm -f "$D/E8_blindprop/e8b_scores.csv"; run E8_blindprop score_e8b.py; cmp_file E8_blindprop/e8b_scores.csv
echo "== E9";  rm -f "$D/E9_hybrid/e9_scores_A.csv" "$D/E9_hybrid/e9_scores_B.csv"
run E9_hybrid score_e9.py --part A; cmp_file E9_hybrid/e9_scores_A.csv
run E9_hybrid score_e9.py --part B; cmp_file E9_hybrid/e9_scores_B.csv
echo "== E10"; rm -f "$D/E10_fallback/e10_scores.csv"; run E10_fallback score_e10.py; cmp_out E10_fallback/e10_score_output.txt "$W/out.txt"; cmp_file E10_fallback/e10_scores.csv
run E10_fallback score_e10_cluster.py; cmp_out E10_fallback/e10_cluster_output.txt "$W/out.txt"
echo "== E11"; run E11_crossfamily score_e11.py --out e11_scores.csv.new; cmp_out E11_crossfamily/e11_score_output.txt "$W/out.txt"
mv "$D/E11_crossfamily/e11_scores.csv.new" "$D/E11_crossfamily/e11_scores.csv" 2>/dev/null; cmp_file E11_crossfamily/e11_scores.csv
echo "== E12"; run E12_extend score_e12.py --out e12_scores.csv.new; cmp_out E12_extend/e12_score_output.txt "$W/out.txt"
mv "$D/E12_extend/e12_scores.csv.new" "$D/E12_extend/e12_scores.csv" 2>/dev/null; cmp_file E12_extend/e12_scores.csv
echo "== E13"; run E13_newrepos score_e13.py --out e13_scores.csv.new; cmp_out E13_newrepos/e13_score_output.txt "$W/out.txt"
mv "$D/E13_newrepos/e13_scores.csv.new" "$D/E13_newrepos/e13_scores.csv" 2>/dev/null; cmp_file E13_newrepos/e13_scores.csv
echo "== freezes (working tree, read-only)"
$PY "$(dirname "$0")/check_freezes.py" > "$W/freezes.txt" || fail=1; sed "s/^/  /" "$W/freezes.txt" | grep -v "^  OK  " || true
echo; [ $fail = 0 ] && echo "REPRODUCED: all scorer outputs identical" || echo "NOT FULLY REPRODUCED (see above)"
exit $fail
