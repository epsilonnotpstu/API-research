#!/usr/bin/env bash
# One baseline and four mutation conditions for each requested seed.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
EXP=$(cd -- "$HERE/../.." && pwd)
[[ $# -ge 1 ]] || { echo 'Usage: run_batch.sh SUT [SEEDS ...]' >&2; exit 2; }
source "$HERE/common.sh"
sut=$1
shift
load_sut "$sut"
seeds=("$@")
if ((${#seeds[@]} == 0)); then seeds=(1 2 3); fi
declare -A seen=()
for seed in "${seeds[@]}"; do
    [[ $seed =~ ^(0|[1-9][0-9]*)$ ]] || { echo 'Invalid seed' >&2; exit 2; }
    [[ ! ${seen[$seed]+present} ]] || { echo 'Duplicate seed' >&2; exit 2; }
    seen[$seed]=1
done
export MAX_EXAMPLES=${MAX_EXAMPLES:-100}
export SCHEMA_CHECKS=${SCHEMA_CHECKS:-all}
budget=${BUDGET_SECONDS:-300}
severity=${SEVERITY:-30}
[[ $budget =~ ^[1-9][0-9]*$ && $severity =~ ^[1-9][0-9]?$|^100$ ]] || { echo 'Invalid budget/severity' >&2; exit 2; }
# Non-empty STRICT_KEYWORDS requires exactly FAULTS=REQUEST_STRICT. Validate
# before creating any batch output; the comparison baseline runs without the knob.
source "$HERE/fuzzer_args.sh"
build_strict_args REQUEST_STRICT
if [[ -n ${STRICT_KEYWORDS:-} ]]; then
    strict_fault_count=0
    for strict_fault in ${FAULTS:-REQUEST_LOOSE REQUEST_STRICT RESPONSE_ORACLE METHOD_SEM}; do
        [[ $strict_fault == REQUEST_STRICT ]] || { echo 'STRICT_KEYWORDS requires FAULTS=REQUEST_STRICT' >&2; exit 2; }
        strict_fault_count=$((strict_fault_count + 1))
    done
    [[ $strict_fault_count == 1 ]] || { echo 'STRICT_KEYWORDS requires FAULTS=REQUEST_STRICT' >&2; exit 2; }
fi
spec="$EMB_DIR/$SPEC_SOURCE"
runs="$EXP/E1_pilot/runs/$sut"
batch_id="$(date -u +%Y%m%dT%H%M%SZ)_batch_$$"
mkdir -p "$runs/batches"
batch_dir="$runs/batches/$batch_id"
mkdir "$batch_dir"
printf 'seed\tmode\tfault\trun_dir\n' >"$batch_dir/runs.tsv"
run_one() {
    local mode=$1 fault=$2 percent=$3 seed=$4 id
    id="${batch_id}_${mode}_${fault}_p${percent}_s${seed}"
    # Exact path reserved by run_pilot's exclusive mkdir; never guess from old runs.
    LAST_RUN="$runs/$id"
    if [[ $mode == baseline && -n ${STRICT_KEYWORDS:-} ]]; then
        STRICT_KEYWORDS= PILOT_RUN_ID="$id" "$HERE/run_pilot.sh" "$sut" "$spec" "$mode" "$fault" "$percent" "$seed" "$budget"
    else
        PILOT_RUN_ID="$id" "$HERE/run_pilot.sh" "$sut" "$spec" "$mode" "$fault" "$percent" "$seed" "$budget"
    fi
    printf '%s\t%s\t%s\t%s\n' "$seed" "$mode" "$fault" "$LAST_RUN" >>"$batch_dir/runs.tsv"
}
for seed in "${seeds[@]}"; do
    run_one baseline NONE 0 "$seed"
    baseline=$LAST_RUN
    # FAULTS (space-separated) selects a subset; default = all four classes.
    for fault in ${FAULTS:-REQUEST_LOOSE REQUEST_STRICT RESPONSE_ORACLE METHOD_SEM}; do
        case $fault in REQUEST_LOOSE|REQUEST_STRICT|RESPONSE_ORACLE|METHOD_SEM) ;; *) echo "Invalid fault: $fault" >&2; exit 2;; esac
        # ORACLE_POOL=baseline: RESPONSE_ORACLE mutates only operations with a 2xx body in this seed's baseline.
        # LOOSE_POOL=spec: REQUEST_LOOSE mutates only operations with a checker-evaluated request constraint.
        if [[ $fault == REQUEST_LOOSE && ${LOOSE_POOL:-all} == spec ]]; then
            /usr/bin/python3 -I -B "$TOOLS_DIR/eligible_ops.py" "$baseline" --fault REQUEST_LOOSE \
                --out "$batch_dir/eligible_loose_s$seed.json"
            ONLY_OPS="$batch_dir/eligible_loose_s$seed.json" run_one mutated "$fault" "$severity" "$seed"
        elif [[ $fault == RESPONSE_ORACLE && ${ORACLE_POOL:-all} == baseline ]]; then
            /usr/bin/python3 -I -B "$TOOLS_DIR/eligible_ops.py" "$baseline" --base-path "$BASE_PATH" \
                --out "$batch_dir/eligible_s$seed.json"
            ONLY_OPS="$batch_dir/eligible_s$seed.json" run_one mutated "$fault" "$severity" "$seed"
        else
            ONLY_OPS= run_one mutated "$fault" "$severity" "$seed"
        fi
        "$HERE/analyse_run.sh" "$LAST_RUN" "$baseline" --mode both
    done
done
echo "Batch complete: $batch_dir/runs.tsv"
