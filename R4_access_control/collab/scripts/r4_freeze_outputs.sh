#!/bin/bash
# R4 output freeze: all coder outputs (codes_*.csv, codes_report_*.md) + package freeze, BEFORE scoring. Refuses to overwrite.
set -euo pipefail; export LC_ALL=C
B="$(cd "$(dirname "$0")/../.." && pwd)"; O="$B/plan/r4_outputs_freeze.sha256"
[ -e "$O" ] && { echo "refuse: $O exists"; exit 1; }
cd "$B" && sha256sum -c --quiet plan/r4_plan_freeze.sha256 && echo "plan freeze OK"
grep -v ' TREE:' plan/r4_packages_freeze.sha256 | sha256sum -c --quiet && echo "package file freeze OK"
while read h p; do d=${p#TREE:}; d=${d%/A\*}; g=$(cd "$d" && find A* -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1); [ "$g" = "$h" ] || { echo "TREE MISMATCH $d"; exit 1; }; done < <(grep ' TREE:' plan/r4_packages_freeze.sha256)
echo "package trees OK"
sha256sum packages/r4_blind/codes_G1.csv packages/r4_blind/codes_G2.csv packages/r4_blind/codes_report_G?.md packages/r4_kb*/codes_H?.csv packages/r4_kb*/codes_report_H?.md plan/r4_packages_freeze.sha256 > "$O"
wc -l < "$O"; echo "r4 output freeze done"
