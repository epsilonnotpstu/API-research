#!/usr/bin/env bash
# Future execution by Claude. Never build or replace an image here.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
[[ $# -ge 1 ]] || { echo 'Usage: run_pair.sh MUT_DIR [SEEDS...]' >&2; exit 2; }
exec /usr/bin/python3 -I -B "$HERE/e5_pipeline.py" run "$@"
