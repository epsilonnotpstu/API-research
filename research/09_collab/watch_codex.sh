#!/usr/bin/env bash
# Codex-এর কাজ দেখার সহজ উপায় (supervisor-এর জন্য)।
#
#   ./watch_codex.sh            এখন কী চলছে + প্রতিটি task-এর শেষ অবস্থা (একবার দেখায়)
#   ./watch_codex.sh -f         চলমান (বা সর্বশেষ) Codex task live দেখা — Ctrl+C দিয়ে বন্ধ
#   ./watch_codex.sh -f T16     নির্দিষ্ট task live দেখা
#   ./watch_codex.sh T15        কোনো task-এর শেষ ২০টি পদক্ষেপ দেখা (শেষ হয়ে যাওয়া task-ও)
#
# Live mode-এ শুধু অর্থবহ লাইন দেখায়:
#   [CMD]   Codex যে command চালাচ্ছে
#   [SAYS]  Codex-এর নিজের বার্তা বা পরিকল্পনা
#   [FILE]  ফাইল লেখা বা বদলানো
#   [ERR]   ত্রুটি (Codex-এর error, usage/rate limit)
#   [FAIL]  কোনো command ব্যর্থ হয়েছে
set -uo pipefail
C=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
LOGS="$C/logs"
BOLD=$'\e[1m'; DIM=$'\e[2m'; GRN=$'\e[32m'; YEL=$'\e[33m'; CYN=$'\e[36m'; RED=$'\e[31m'; OFF=$'\e[0m'

running_tasks() { pgrep -af "codex exec" | grep -o 'tasks/T[0-9]*\.md' | sed 's|tasks/||; s|\.md||' | sort -u; }

# Codex log: a marker line ("exec", "codex", "apply patch") followed by its content; diff lines are skipped.
filter() {
    awk -v g="$GRN" -v y="$YEL" -v c="$CYN" -v r="$RED" -v o="$OFF" '
        /^[0-9]{4}-[0-9][0-9]-[0-9][0-9]T[^ ]*Z +ERROR/ { if ($0 !~ /failed to load skill/) { print r "[ERR]  " o substr($0, 1, 200); fflush() } next }
        /^ exited [1-9][0-9]* in/ { print r "[FAIL] " o "command" $0; fflush(); next }
        /^[-+@ ]|^diff --git|^index |^new file mode|^deleted file mode/ { next }
        /usage limit|rate limit/  { print r "[ERR]  " o substr($0, 1, 200); fflush(); next }
        /^exec$/                  { m = g "[CMD]  " o; skip = 0; next }
        /^codex$/                 { m = c "[SAYS] " o; skip = 0; next }
        /^apply patch$/           { m = y "[FILE] " o; skip = 1; next }
        skip && /^patch: /        { skip = 0; next }
        m != "" && NF             { print m substr($0, 1, 200); fflush(); m = "" }
    '
}

status() {
    echo "${BOLD}== এখন চলছে ==${OFF}"
    local r; r=$(running_tasks)
    if [[ -z $r ]]; then echo "  (কোনো Codex task চলছে না)"; else
        for t in $r; do echo "  ${GRN}●${OFF} $t  — log: logs/$t.log ($(wc -l < "$LOGS/$t.log") লাইন, শেষ লেখা $(date -r "$LOGS/$t.log" +%H:%M:%S))"; done
    fi
    echo; echo "${BOLD}== Board-এর শেষ ৮টি Log লাইন ==${OFF}"
    grep '^- 20' "$C/COLLAB_BOARD.md" | tail -8 | cut -c1-220
    echo; echo "${BOLD}== Task-এর অবস্থা (board) ==${OFF}"
    grep -E '^\| T[0-9]+ ' "$C/COLLAB_BOARD.md" | awk -F'|' '{printf "  %-5s %-12s %s\n", $2, $6, substr($3,1,70)}'
    echo; echo "${DIM}Live দেখতে: ./watch_codex.sh -f   |   একটি task: ./watch_codex.sh T16${OFF}"
}

case "${1:-}" in
    -f)
        t=${2:-$(running_tasks | tail -1)}
        [[ -z $t ]] && t=$(ls -t "$LOGS"/T*.log | head -1 | xargs -n1 basename | sed 's/\.log$//')
        echo "${BOLD}== $t live (Ctrl+C দিয়ে বন্ধ) ==${OFF}"
        tail -n 400 -F "$LOGS/$t.log" | filter ;;
    T[0-9]*)
        echo "${BOLD}== $1: শেষ ২০টি পদক্ষেপ ==${OFF}"
        filter < "$LOGS/$1.log" | tail -20
        [[ -f $LOGS/${1}_last.md ]] && { echo; echo "${BOLD}== $1: Codex-এর শেষ বার্তা ==${OFF}"; cut -c1-200 "$LOGS/${1}_last.md"; } ;;
    "") status ;;
    *) sed -n '2,13p' "$0" ;;
esac
