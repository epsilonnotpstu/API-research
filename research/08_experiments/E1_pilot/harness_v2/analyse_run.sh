#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
EXP=$(cd -- "$HERE/../.." && pwd)
[[ $# == 2 || $# == 4 ]] || { echo 'Usage: analyse_run.sh MUTATED_RUN BASELINE_RUN [--mode both|fresh|replay]' >&2; exit 2; }
run_dir=$(realpath -- "$1"); baseline=$(realpath -- "$2"); mode=both
if [[ $# == 4 ]]; then [[ $3 == --mode ]] || { echo 'Expected --mode' >&2; exit 2; }; mode=$4; fi
case $mode in both|fresh|replay) ;; *) echo 'Invalid analysis mode' >&2; exit 2;; esac
sut=$(/usr/bin/python3 -I -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["sut"])' "$run_dir/run.json")
source "$HERE/common.sh"
load_sut "$sut"
# Validate before producing analysis; incomplete runs need a separate, manual audit.
/usr/bin/python3 -I -B - "$run_dir" "$baseline" "$EXP/tools" "$HERE" <<'PY'
import hashlib, json, pathlib, sys
run, base, tools, harness = map(pathlib.Path, sys.argv[1:])
r, b = (json.loads((p / 'run.json').read_text()) for p in (run, base))
if not (r['complete'] and b['complete'] and r['mode'] == 'mutated' and b['mode'] == 'baseline'):
    raise SystemExit('Need complete mutated and baseline runs; inspect run.json and logs')
for key in ('sut', 'sut_jar_sha256', 'emb_commit', 'source_sha256', 'base_path', 'auth',
            'max_examples', 'budget_seconds', 'seed', 'schemathesis_image', 'logger_max_body',
            'request_timeout_ms', 'hypothesis_phases', 'schema_checks', 'harness_version',
            'sut_service', 'sut_image', 'internal_port', 'auth_source', 'auth_source_sha256',
            'health_path', 'harness_sha256', 'emb_config_sha256',
            'jacoco_agent_sha256', 'jacoco_cli_sha256'):
    if r[key] != b[key]:
        raise SystemExit(f'Incompatible runs: {key}')
for key in ('schema-image', f'sut-{r["sut"]}-image', 'mitmproxy-image'):
    if r['images'][key]['id'] != b['images'][key]['id']:
        raise SystemExit(f'Image changed between runs: {key}')
if r['tool_sha256'] != b['tool_sha256']:
    raise SystemExit('Tool snapshots differ between runs')
for name, digest in r['tool_sha256'].items():
    path = tools / name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit(f'Current tool differs from collection: {name}')
for name, digest in r['harness_sha256'].items():
    path = harness / name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise SystemExit(f'Current harness differs from collection: {name}')
for directory, meta in ((run, r), (base, b)):
    specs = list(directory.glob('spec.test.*'))
    if len(specs) != 1:
        raise SystemExit('Expected exactly one spec.test snapshot')
    for name in ('exchanges.jsonl', specs[0].name, 'generator-input.json', 'sut-config.env'):
        digest = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if digest != meta['file_sha256'].get(name):
            raise SystemExit(f'Artifact changed: {directory / name}')
manifest = run / 'manifest.json'
if hashlib.sha256(manifest.read_bytes()).hexdigest() != r['file_sha256'].get('manifest.json'):
    raise SystemExit('Manifest changed since collection')
PY
# -I excludes ambient paths; explicitly add only the trusted local tools directory.
pytool() {
    /usr/bin/python3 -I -B -c 'import runpy,sys; sys.path.insert(0,sys.argv.pop(1)); script=sys.argv.pop(1); sys.argv[0]=script; runpy.run_path(script,run_name="__main__")' \
        "$EXP/tools" "$EXP/tools/$1" "${@:2}"
}
# T10 must deliver --mode. Never silently fall back to the unsafe pre-T10 CLI.
pytool attribute.py --help > /dev/null
base_specs=("$baseline"/spec.test.*); mut_specs=("$run_dir"/spec.test.*)
[[ ${#base_specs[@]} == 1 && -f ${base_specs[0]} && ${#mut_specs[@]} == 1 && -f ${mut_specs[0]} ]] || exit 1
analysis="$run_dir/analysis-$mode"
mkdir "$analysis" # Refuse to overwrite earlier analysis.
pytool conformance.py "${base_specs[0]}" "$baseline/exchanges.jsonl" >"$analysis/baseline.violations.jsonl"
if [[ $mode == both || $mode == fresh ]]; then
    pytool conformance.py "${mut_specs[0]}" "$run_dir/exchanges.jsonl" >"$analysis/fresh.violations.jsonl"
    pytool attribute.py "$analysis/baseline.violations.jsonl" "$analysis/fresh.violations.jsonl" \
        "$run_dir/manifest.json" --mode fresh >"$analysis/fresh.attributed.csv"
fi
if [[ $mode == both || $mode == replay ]]; then
    pytool conformance.py "${mut_specs[0]}" "$baseline/exchanges.jsonl" >"$analysis/replay.violations.jsonl"
    pytool attribute.py "$analysis/baseline.violations.jsonl" "$analysis/replay.violations.jsonl" \
        "$run_dir/manifest.json" --mode replay >"$analysis/replay.attributed.csv"
fi
sha256sum "$EXP/tools/conformance.py" "$EXP/tools/attribute.py" "$EXP/tools/specmut.py" >"$analysis/tool-sha256.txt"
printf '%s\n' "baseline=$baseline" "mutated=$run_dir" "mode=$mode" >"$analysis/inputs.txt"
echo "Analysis: $analysis"
