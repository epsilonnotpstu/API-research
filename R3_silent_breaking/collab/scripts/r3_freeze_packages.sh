#!/bin/bash
# R3 package freeze (round 2): package trees, items.csv, TASK copies, key, scorer, deviations. Run BEFORE any coder.
set -euo pipefail
B="$(cd "$(dirname "$0")/../.." && pwd)"; O="$B/plan/r3_packages_freeze.sha256"
[ -e "$O" ] && { echo "refuse: $O exists"; exit 1; }
cd "$B" && sha256sum -c --quiet plan/r3_plan_freeze.sha256 && echo "plan freeze OK"
{
  for d in packages/r3_blind packages/r3_kb*; do
    h=$(cd "$d" && find B* -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1)
    echo "$h  TREE:$d/B*"
  done
  sha256sum packages/r3_*/items.csv packages/r3_*/TASK_R3.md mining/key/r3_key.csv mining/freeze4.json mining/freeze4_sample.json \
            plan/score_r3.py plan/test_score_r3.py plan/R3_DEVIATIONS.md
} > "$O"
cat "$O" | awk '{print substr($1,1,12), $2}'
for d in packages/r3_*; do cmp "$d/TASK_R3.md" plan/TASK_R3.md; done && echo "TASK_R3.md byte-identical in all packages"
echo "r3 package freeze done"
