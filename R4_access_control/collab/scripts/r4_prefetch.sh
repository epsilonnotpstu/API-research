#!/bin/bash
# Pre-warm mining/cache/git/<owner>__<repo>.git (layout of T56 r4_resolve.py): depth-2 blob:none fetch of every full-SHA commit reference,
# then a numstat diff against the first parent (lazily fetches the changed blobs). Only commit URLs are used; no advisory text is read.
B="$(cd "$(dirname "$0")/../.." && pwd)"; C="$B/mining/cache/git"; mkdir -p "$C"
one_repo(){ o=$1; r=$2; shift 2; g="$C/${o}__${r}.git"
  [ -d "$g" ] || { git init -q --bare "$g" && git -C "$g" remote add origin "https://github.com/$o/$r.git"; }
  for s in "$@"; do
    timeout 300 git -C "$g" -c protocol.version=2 fetch -q --depth=2 --filter=blob:none origin "$s" 2>/dev/null || { echo "FAIL $o/$r $s"; continue; }
    timeout 300 git -C "$g" diff --numstat "$s^1" "$s" >/dev/null 2>&1 || echo "NODIFF $o/$r $s"
  done; echo "DONE $o/$r $#"; }
export -f one_repo; export C
awk -F/ '{print $4" "$5" "$7}' "$B/mining/cache/prefetch_refs.txt" | sort | awk '{k=$1" "$2; a[k]=a[k]" "$3} END{for(k in a) print k a[k]}' \
 | xargs -P 12 -L 1 bash -c 'one_repo "$@"' _
echo PREFETCH-ALL-DONE
