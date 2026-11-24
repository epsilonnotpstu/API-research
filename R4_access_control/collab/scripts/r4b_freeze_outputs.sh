#!/bin/bash
# R4b output freeze before scoring. Refuses to overwrite.
set -euo pipefail; export LC_ALL=C
B="$(cd "$(dirname "$0")/../.." && pwd)"; O="$B/plan/r4b_outputs_freeze.sha256"
[ -e "$O" ] && { echo "refuse: $O exists"; exit 1; }
cd "$B" && sha256sum -c --quiet plan/r4b_plan_freeze.sha256 && echo "r4b plan freeze OK"
grep -v ' TREE:' plan/r4b_packages_freeze.sha256 | grep -v 'R4b_DEVIATIONS' | sha256sum -c --quiet && echo "r4b package files OK"
while read h p; do d=${p#TREE:}; d=${d%/C\*}; g=$(cd "$d" && find C* -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1); [ "$g" = "$h" ] || { echo "TREE MISMATCH $d"; exit 1; }; done < <(grep ' TREE:' plan/r4b_packages_freeze.sha256)
echo "r4b package trees OK"
sha256sum packages/r4b_blind/codes_G3.csv packages/r4b_blind/codes_G4.csv packages/r4b_blind/codes_report_G?.md packages/r4b_kb*/codes_H?.csv packages/r4b_kb*/codes_report_H?.md plan/r4b_packages_freeze.sha256 > "$O"
wc -l < "$O"; echo "r4b output freeze done"
