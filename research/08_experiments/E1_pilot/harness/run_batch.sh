#!/usr/bin/env bash
# Batch 1: 3 seeds x (baseline + 4 fault classes at 30%), then analysis in both modes.
set -uo pipefail
H=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
SPEC="$H/../../_external/emb/openapi-swagger/scout-api.json"
RUNS="$H/../runs/scout-api"
export MAX_EXAMPLES=100
export SCHEMA_CHECKS=${SCHEMA_CHECKS:-all}
for seed in 1 2 3; do
  "$H/run_pilot.sh" scout-api "$SPEC" baseline NONE 0 "$seed" 300 || echo "BATCH-FAIL baseline s$seed"
  b=("$RUNS"/*_baseline_NONE_p0_s"${seed}"_*); BASE="${b[-1]}"
  for fault in REQUEST_LOOSE REQUEST_STRICT RESPONSE_ORACLE METHOD_SEM; do
    "$H/run_pilot.sh" scout-api "$SPEC" mutated "$fault" 30 "$seed" 300 || echo "BATCH-FAIL $fault s$seed"
    m=("$RUNS"/*_mutated_"${fault}"_p30_s"${seed}"_*); MUT="${m[-1]}"
    "$H/analyse_run.sh" "$MUT" "$BASE" --mode both || echo "BATCH-ANALYSIS-FAIL $fault s$seed"
  done
done
echo BATCH-DONE
