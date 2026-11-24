#!/bin/bash
# GPT blind coders on packages/r3b_blind (Codex, high effort).
# usage: r3b_launch_gpt.sh                 -> fresh runs G1 G2 (parallel)
#        r3b_launch_gpt.sh resume K ID...  -> resume listed sessions after a usage limit (round K)
B="$(cd "$(dirname "$0")/../.." && pwd)"; D="$B/packages/r3b_blind"; L="$B/collab/logs"; mkdir -p "$L"
run(){ id=$1
  (cd "$D" && codex exec -m gpt-6.1-sol -c model_reasoning_effort=high -s workspace-write -C "$D" -o "$L/R3b_${id}_last.md" \
    "You are blind coder $id. YOUR_ID=$id. Your first command must be: cat TASK_R3b.md. Then follow TASK_R3b.md in this directory exactly. Do not read anything outside this directory." \
    > "$L/R3b_$id.log" 2>&1 < /dev/null
   echo "$id exit=$? out=$( [ -f "$D/codes_$id.csv" ] && echo yes || echo no ) limit=$(grep -c 'hit your usage limit' "$L/R3b_$id.log")") & }
rs(){ k=$1; id=$2; sid=$(grep -m1 'session id' "$L/R3b_$id.log" | awk '{print $3}')
  (cd "$D" && codex exec resume "$sid" -m gpt-6.1-sol -c model_reasoning_effort=high -c sandbox_mode='"workspace-write"' -o "$L/R3b_${id}_last.md" \
    "Usage limit has reset. Continue as blind coder $id (YOUR_ID=$id) exactly per TASK_R3b.md in this directory, from where you stopped, and finish all deliverables." \
    > "$L/R3b_${id}_resume$k.log" 2>&1 < /dev/null
   echo "$id resume$k exit=$? out=$( [ -f "$D/codes_$id.csv" ] && echo yes || echo no ) limit=$(grep -c 'hit your usage limit' "$L/R3b_${id}_resume$k.log")") & }
if [ "${1:-}" = resume ]; then k=$2; shift 2; for id in "$@"; do rs "$k" "$id"; done; else for id in G5 G6; do run "$id"; done; fi
wait; echo r3b-gpt-runs-done
