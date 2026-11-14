#!/usr/bin/env bash
# Own Python analysis only; pair validation is mandatory before either oracle.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
[[ $# == 1 ]] || { echo 'Usage: analyse_pair.sh MUT_DIR' >&2; exit 2; }
exec /usr/bin/python3 -I -B "$HERE/e5_pipeline.py" analyse "$@"
