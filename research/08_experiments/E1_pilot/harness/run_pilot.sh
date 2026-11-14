#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
EXP=$(cd -- "$HERE/../.." && pwd)
[[ $# == 7 ]] || { echo 'Usage: run_pilot.sh scout-api SPEC baseline|mutated FAULT SEVERITY SEED BUDGET_SECONDS' >&2; exit 2; }
sut=$1; spec=$(realpath -- "$2"); mode=$3; fault=$4; severity=$5; seed=$6; budget=$7
[[ $sut == scout-api && -s $spec ]] || { echo 'Only scout-api is supported; spec must exist' >&2; exit 2; }
[[ $mode == baseline || $mode == mutated ]] || { echo 'Invalid mode' >&2; exit 2; }
[[ $severity =~ ^(0|[1-9][0-9]*)$ && $seed =~ ^(0|[1-9][0-9]*)$ && $budget =~ ^[1-9][0-9]*$ ]] || { echo 'Invalid numeric parameter' >&2; exit 2; }
((severity <= 100)) || { echo 'Severity must be 0..100' >&2; exit 2; }
if [[ $mode == baseline ]]; then
    [[ $fault == NONE && $severity == 0 ]] || { echo 'Baseline requires NONE 0' >&2; exit 2; }
else
    case $fault in REQUEST_LOOSE|REQUEST_STRICT|RESPONSE_ORACLE|METHOD_SEM) ;; *) echo 'Invalid fault class' >&2; exit 2;; esac
    ((severity > 0)) || { echo 'Mutated run requires positive severity' >&2; exit 2; }
fi
for tool in docker curl java timeout flock git sha256sum grep /usr/bin/python3; do command -v "$tool" >/dev/null || { echo "Missing tool: $tool" >&2; exit 1; }; done
docker compose version >/dev/null
export EMB_DIR="$EXP/_external/emb" TOOLS_DIR="$EXP/tools"
export PILOT_UID=$(id -u) PILOT_GID=$(id -g)
# Original EMB port interpolation accepts an IP prefix; bind published ports to loopback.
export HOST_PORT=127.0.0.1:18080 JACOCO_PORT=127.0.0.1:16300
export MITM_MAX_BODY=${MITM_MAX_BODY:-65536}
SCHEMA_IMAGE=schemathesis/schemathesis:3.39.16
MAX_EXAMPLES=${MAX_EXAMPLES:-100}
# Our oracle is tools/conformance.py. Schemathesis abandons an operation at its first failed check,
# so batch 2 uses a check that does not fail on 5xx to keep generating (SCHEMA_CHECKS).
SCHEMA_CHECKS=${SCHEMA_CHECKS:-all}
[[ $SCHEMA_CHECKS =~ ^[a-z_,]+$ ]] || { echo "Invalid SCHEMA_CHECKS" >&2; exit 2; }
HEALTH_PATH=${HEALTH_PATH:-/admin/healthcheck}
BASE_PATH=${BASE_PATH:-/api}
REQUEST_TIMEOUT_MS=${REQUEST_TIMEOUT_MS:-10000}
export PILOT_REQUEST_TIMEOUT_MS="$REQUEST_TIMEOUT_MS" PILOT_HYPOTHESIS_PHASES=explicit,generate
[[ $REQUEST_TIMEOUT_MS =~ ^[1-9][0-9]*$ ]] || { echo 'Invalid REQUEST_TIMEOUT_MS' >&2; exit 2; }
# Load the benchmark fixture at runtime; never persist its credential in provenance.
if [[ ${AUTH_HEADER+x} ]]; then
    export PILOT_AUTH_ROLE=${AUTH_ROLE:-custom}
else
    AUTH_HEADER=$(/usr/bin/python3 -I -B - "$EMB_DIR/auth/scout-api-auth.yaml" <<'AUTH_PY'
import sys, yaml
from pathlib import Path
config = yaml.safe_load(Path(sys.argv[1]).read_text())
role = next(item for item in config['auth'] if item['name'] == 'administrator')
header = next(item for item in role['fixedHeaders'] if item['name'].lower() == 'authorization')
print(header['name'] + ': ' + header['value'])
AUTH_PY
    )
    export PILOT_AUTH_ROLE=administrator
fi
[[ $AUTH_HEADER == *:* && $AUTH_HEADER != *$'\n'* && $AUTH_HEADER != *$'\r'* ]] || { echo 'Invalid AUTH_HEADER' >&2; exit 2; }
# Only the redactor receives this host-side environment value; Docker receives -H.
export PILOT_AUTH_REDACT="$AUTH_HEADER"
[[ $MAX_EXAMPLES =~ ^[1-9][0-9]*$ && $HEALTH_PATH == /* && $BASE_PATH == /* ]] || { echo 'Invalid MAX_EXAMPLES, HEALTH_PATH or BASE_PATH' >&2; exit 2; }
for jar in scout-api-sut.jar jacocoagent.jar jacococli.jar; do
    [[ -s $EMB_DIR/dist/$jar ]] || { echo "Missing $jar; run prepare_dist.sh first" >&2; exit 1; }
done
# Serialize runs to avoid port, build, and resource contention. Never replace an existing run.
exec 9>"$HERE/.run.lock"
flock -n 9 || { echo 'Another pilot is running' >&2; exit 1; }
run_id="$(date -u +%Y%m%dT%H%M%SZ)_${mode}_${fault}_p${severity}_s${seed}_$$"
run_dir="$EXP/E1_pilot/runs/$sut/$run_id"
mkdir -p "$EXP/E1_pilot/runs/$sut"
mkdir "$run_dir"
export PILOT_LOG_DIR="$run_dir"
project="r1-scout-$(date -u +%s)-$$"
generator="$project-generator"
compose=(docker compose --project-name "$project" --project-directory "$EMB_DIR" \
    -f "$EMB_DIR/dockerfiles/$sut.yaml" -f "$HERE/compose.override.$sut.yaml")
started=$(date -u +%FT%TZ)
phase=preparation
schema_rc=not_started
coverage_rc=not_attempted
cleanup_rc=0
metadata() {
    /usr/bin/python3 -I "$HERE/run_metadata.py" "$run_dir" "$EMB_DIR" "$sut" "$spec" \
        "$mode" "$fault" "$severity" "$seed" "$budget" "$MAX_EXAMPLES" "$SCHEMA_IMAGE" \
        "$project" "$started" "$phase" "$schema_rc" "$coverage_rc" "$cleanup_rc" "$1" \
        "$HEALTH_PATH" "$BASE_PATH"
}
finish() {
    local rc=$? container_id
    trap - EXIT INT TERM
    set +e
    docker rm -f "$generator" >>"$run_dir/cleanup.log" 2>&1
    # Dump before stopping the JVM: dumponexit=false in the EMB Dockerfile.
    container_id=$("${compose[@]}" ps -q "sut-$sut" 2>>"$run_dir/cleanup.log")
    if [[ -n $container_id ]]; then
        timeout 40 java -jar "$EMB_DIR/dist/jacococli.jar" dump --address 127.0.0.1 \
            --port 16300 --retry 3 --destfile "$run_dir/jacoco.exec" >"$run_dir/jacoco-dump.log" 2>&1
        coverage_rc=$?
    fi
    "${compose[@]}" logs --no-color 2>&1 | /usr/bin/python3 -I -B "$HERE/redact_auth.py" >"$run_dir/compose.log"
    "${compose[@]}" down --timeout 20 >"$run_dir/compose-down.log" 2>&1
    cleanup_rc=$?
    if ((rc == 0)) && { [[ $coverage_rc != 0 ]] || [[ ! -s $run_dir/jacoco.exec ]] || ((cleanup_rc != 0)); }; then rc=1; fi
    if ((rc == 0)) && [[ ! -s $run_dir/exchanges.jsonl ]]; then
        echo 'No logged exchanges: refusing to call this a complete run' >&2; rc=1
    fi
    /usr/bin/python3 -I -B "$HERE/redact_auth.py" "$run_dir"
    if (($? != 0)); then echo 'Credential redaction failed' >&2; rc=1; fi
    metadata "$rc"
    if (($? != 0)); then echo 'Failed to finalize run.json' >&2; rc=1; fi
    echo "Run: $run_dir; harness exit=$rc; Schemathesis exit=$schema_rc; coverage exit=$coverage_rc"
    exit "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
metadata pending
# Use a stable filename while preserving format (JSON and YAML are both supported).
cp "$spec" "$run_dir/spec.original.${spec##*.}"
test_spec="$run_dir/spec.original.${spec##*.}"
if [[ $mode == mutated ]]; then
    /usr/bin/python3 -I "$TOOLS_DIR/specmut.py" "$spec" --fault "$fault" --severity "$severity" \
        --seed "$seed" --out "$run_dir/mutation" >"$run_dir/specmut.log" 2>&1
    shopt -s nullglob
    manifests=("$run_dir"/mutation/*.manifest.json)
    [[ ${#manifests[@]} == 1 ]] || { echo 'Expected exactly one mutation manifest' >&2; exit 1; }
    cp "${manifests[0]}" "$run_dir/manifest.json"
    /usr/bin/python3 -I -c 'import json,sys; m=json.load(open(sys.argv[1])); sys.exit(0 if m["operations_mutated"] > 0 else "Mutation changed no operations")' "$run_dir/manifest.json"
    test_spec="${manifests[0]%.manifest.json}.json"
fi
cp "$test_spec" "$run_dir/spec.test.${test_spec##*.}"
# Keep both the effective compose configuration and immutable image IDs/digests.
"${compose[@]}" config >"$run_dir/compose.resolved.yaml"
docker pull "$SCHEMA_IMAGE" >"$run_dir/schema-pull.log" 2>&1
docker image inspect "$SCHEMA_IMAGE" >"$run_dir/schema-image.json"
# Capture CLI help from the pinned image before starting the SUT; abort on incompatible flags.
docker run --rm "$SCHEMA_IMAGE" run --help >"$run_dir/schemathesis-help.txt" 2>&1
for flag in --checks --hypothesis-seed --hypothesis-max-examples --junit-xml --cassette-path --base-url --request-timeout --hypothesis-phases --header --sanitize-output; do
    if ! grep -q -- "$flag" "$run_dir/schemathesis-help.txt"; then
        echo "Pinned Schemathesis CLI missing $flag" >&2; exit 1
    fi
done
phase=startup
if docker image inspect r1-scout-sut:pilot >/dev/null 2>&1; then
    "${compose[@]}" up -d --no-build >"$run_dir/compose-up.log" 2>&1
else
    "${compose[@]}" up -d --build >"$run_dir/compose-up.log" 2>&1
fi
for service in "sut-$sut" mitmproxy; do
    cid=$("${compose[@]}" ps -q "$service")
    [[ -n $cid ]] || { echo "Missing container: $service" >&2; exit 1; }
    docker inspect "$cid" >"$run_dir/$service-container.json"
    image_id=$(docker inspect --format '{{.Image}}' "$cid")
    docker image inspect "$image_id" >"$run_dir/$service-image.json"
done
# Probe through the proxy; readiness traffic is quarantined before generation.
ready=0
for ((attempt=1; attempt<=60; attempt++)); do
    if curl --fail --silent --show-error --max-time 2 "http://127.0.0.1:18080$HEALTH_PATH" \
        >"$run_dir/health-response.txt" 2>"$run_dir/health-error.txt"; then ready=1; break; fi
    sleep 2
done
((ready == 1)) || { echo "Health probe failed: $HEALTH_PATH" >&2; exit 1; }
# Stop the proxy to flush the readiness log before renaming it, then restart it.
"${compose[@]}" stop --timeout 10 mitmproxy >>"$run_dir/compose-up.log" 2>&1
if [[ -f $run_dir/exchanges.jsonl ]]; then mv "$run_dir/exchanges.jsonl" "$run_dir/readiness-exchanges.jsonl"; fi
"${compose[@]}" start mitmproxy >>"$run_dir/compose-up.log" 2>&1
# A host TCP check avoids adding a second HTTP readiness request to the exchange log.
proxy_ready=0
for ((attempt=1; attempt<=30; attempt++)); do
    if (exec 8<>/dev/tcp/127.0.0.1/18080) 2>/dev/null; then proxy_ready=1; break; fi
    sleep 1
done
((proxy_ready == 1)) || { echo 'Proxy did not restart' >&2; exit 1; }
phase=generation
schema_cmd=(run "/work/$(basename "$test_spec")" --base-url "http://mitmproxy:8080$BASE_PATH" \
    --checks "$SCHEMA_CHECKS" --hypothesis-seed "$seed" --hypothesis-max-examples "$MAX_EXAMPLES" \
    --junit-xml /work/schemathesis.junit.xml --cassette-path /work/schemathesis-cassette.yaml \
    --request-timeout "$REQUEST_TIMEOUT_MS" --hypothesis-phases "$PILOT_HYPOTHESIS_PHASES" --sanitize-output true)
# mount the run directory, so the input and every output remain in this run.
# Generator input only: cut recursive $ref back-edges (hypothesis-jsonschema stalls on them).
# Conformance analysis keeps using spec.test.* (the untouched original or mutated spec).
if [[ ${spec##*.} == json && $mode == mutated ]]; then
    # specmut inlines $refs into mutated operations, which would unroll recursive schemas again.
    # So: de-recurse the ORIGINAL first, then apply the same mutation (same fault/severity/seed
    # => same operations selected) to obtain the generator input.
    /usr/bin/python3 -I -B "$HERE/derecurse.py" "$spec" "$run_dir/spec.derecursed.json" >"$run_dir/derecurse-cuts.json"
    /usr/bin/python3 -I "$TOOLS_DIR/specmut.py" "$run_dir/spec.derecursed.json" --fault "$fault" --severity "$severity" \
        --seed "$seed" --out "$run_dir/mutation_gen" >"$run_dir/specmut_gen.log" 2>&1
    gen=("$run_dir"/mutation_gen/*.manifest.json)
    /usr/bin/python3 -I -c 'import json,sys; a,b=(json.load(open(p)) for p in sys.argv[1:3]); k=lambda m: sorted((x["path"],x["method"]) for x in m["mutations"]); sys.exit(0 if k(a)==k(b) else "Generator mutation selected different operations")' "$run_dir/manifest.json" "${gen[0]}"
    cp "${gen[0]%.manifest.json}.json" "$run_dir/generator-input.json"
elif [[ ${test_spec##*.} == json ]]; then
    /usr/bin/python3 -I -B "$HERE/derecurse.py" "$test_spec" "$run_dir/generator-input.json" >"$run_dir/derecurse-cuts.json"
else
    cp "$test_spec" "$run_dir/generator-input.${test_spec##*.}"; echo '[]' >"$run_dir/derecurse-cuts.json"
fi
schema_cmd[1]="/work/generator-input.${test_spec##*.}"
printf '%s\n' "${schema_cmd[@]}" >"$run_dir/schemathesis-argv.txt"
printf '%s\n' -H '<redacted>' >>"$run_dir/schemathesis-argv.txt"
schema_cmd+=(-H "$AUTH_HEADER")
metadata pending
set +e
timeout --signal=INT --kill-after=20 "${budget}s" docker run --rm --name "$generator" \
    --user "$PILOT_UID:$PILOT_GID" -e XDG_CACHE_HOME=/tmp/cache \
    -e HYPOTHESIS_STORAGE_DIRECTORY=/tmp/hypothesis --network "${project}_default" \
    -v "$run_dir:/work" "$SCHEMA_IMAGE" "${schema_cmd[@]}" 2>&1 | /usr/bin/python3 -I -B "$HERE/redact_auth.py" >"$run_dir/schemathesis.log"
pilot_pipeline_rc=("${PIPESTATUS[@]}")
schema_rc=${pilot_pipeline_rc[0]}
((pilot_pipeline_rc[1] == 0)) || { echo 'Output redaction failed' >&2; exit 1; }
set -e
phase=collection
# Exit 1 includes test failures; the report/log retains the outcome. Timeouts are incomplete.
case $schema_rc in
    0|1) [[ -s $run_dir/schemathesis.junit.xml ]] || { echo 'Missing JUnit report' >&2; exit 1; };;
    124|137) echo 'Generation budget expired; partial run retained, do not treat as complete' >&2; exit "$schema_rc";;
    *) echo "Schemathesis execution failed ($schema_rc)" >&2; exit "$schema_rc";;
esac
phase=complete
