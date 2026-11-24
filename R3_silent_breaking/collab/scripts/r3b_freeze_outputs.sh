#!/bin/bash
# R3b output freeze before scoring. Refuses to overwrite.
set -euo pipefail; export LC_ALL=C
B="$(cd "$(dirname "$0")/../.." && pwd)"; O="$B/plan/r3b_outputs_freeze.sha256"
[ -e "$O" ] && { echo "refuse: $O exists"; exit 1; }
cd "$B" && sha256sum -c --quiet plan/r3b_plan_freeze.sha256 && echo "r3b plan freeze OK"
grep -v ' TREE:' plan/r3b_packages_freeze.sha256 | sha256sum -c --quiet && echo "r3b package files OK"
while read h p; do d=${p#TREE:}; d=${d%/D\*}; g=$(cd "$d" && find D* -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1); [ "$g" = "$h" ] || { echo "TREE MISMATCH $d"; exit 1; }; done < <(grep ' TREE:' plan/r3b_packages_freeze.sha256)
echo "r3b package trees OK"
sha256sum packages/r3b_blind/codes_G5.csv packages/r3b_blind/codes_G6.csv packages/r3b_blind/codes_report_G?.md packages/r3b_kb*/codes_H?.csv packages/r3b_kb*/codes_report_H?.md plan/r3b_packages_freeze.sha256 > "$O"
wc -l < "$O"; echo "r3b output freeze done"
