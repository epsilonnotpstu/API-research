#!/bin/bash
# R4 package freeze: package trees, items.csv, TASK copies, key, pool/sample freezes, scorer, deviations. Run BEFORE any coder.
# TREE hash = (cd pkg && find A* -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum)  -- byte-order sort (locale fixed).
set -euo pipefail
export LC_ALL=C
B="$(cd "$(dirname "$0")/../.." && pwd)"; O="$B/plan/r4_packages_freeze.sha256"
[ -e "$O" ] && { echo "refuse: $O exists"; exit 1; }
cd "$B" && sha256sum -c --quiet plan/r4_plan_freeze.sha256 && echo "plan freeze OK"
{
  for d in packages/r4_blind packages/r4_kb*; do
    h=$(cd "$d" && find A* -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1)
    echo "$h  TREE:$d/A*"
  done
  sha256sum packages/r4_*/items.csv packages/r4_*/TASK_R4.md mining/key/r4_key.csv mining/pool_freeze.json mining/sample_freeze.json \
            mining/pool.json mining/sample.json mining/claude/r4p.py plan/score_r4.py plan/test_score_r4.py plan/R4_DEVIATIONS.md
} > "$O"
awk '{print substr($1,1,12), $2}' "$O"
for d in packages/r4_*; do cmp "$d/TASK_R4.md" plan/TASK_R4.md; done && echo "TASK_R4.md byte-identical in all packages"
echo "r4 package freeze done"
