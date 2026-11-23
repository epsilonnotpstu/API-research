#!/bin/bash
# Launch a Codex task Txx for R4 (workspace-write, -C R4 root), logs to collab/logs/Txx.log
# usage: r4_codex.sh Txx [effort] [not_before_HH:MM]
B="$(cd "$(dirname "$0")/../.." && pwd)"; T=$1; E=${2:-high}; NB=${3:-}
if [ -n "$NB" ]; then now=$(date +%s); tgt=$(date -d "$NB" +%s); [ $tgt -gt $now ] && sleep $((tgt-now)); fi
mkdir -p "$B/collab/logs/${T}_scratch"
cd "$B" && codex exec -m gpt-6.1-sol -c model_reasoning_effort=$E -s workspace-write -C "$B" -o "collab/logs/${T}_last.md" \
  "Your first command must be: cat collab/tasks/$T.md. Then do task $T exactly as written there." > "collab/logs/$T.log" 2>&1 < /dev/null
echo "$T exit=$? limit=$(grep -c 'hit your usage limit' collab/logs/$T.log) report=$( [ -f collab/reports/${T}_report.md ] && echo yes || echo no)"
