#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
EXP=$(cd -- "$HERE/../.." && pwd)
[[ $# == 7 ]] || { echo 'Usage: run_pilot.sh SUT SPEC baseline|mutated FAULT SEVERITY SEED BUDGET_SECONDS' >&2; exit 2; }
sut=$1; spec=$(realpath -- "$2"); mode=$3; fault=$4; severity=$5; seed=$6; budget=$7
source "$HERE/common.sh"
load_sut "$sut"
[[ -s $spec && $spec == *.json ]] || { echo 'Spec must be an existing JSON document' >&2; exit 2; }
[[ $mode == baseline || $mode == mutated ]] || { echo 'Invalid mode' >&2; exit 2; }
[[ $severity =~ ^(0|[1-9][0-9]*)$ && $seed =~ ^(0|[1-9][0-9]*)$ && $budget =~ ^[1-9][0-9]*$ ]] || { echo 'Invalid numeric parameter' >&2; exit 2; }
((severity <= 100)) || { echo 'Severity must be 0..100' >&2; exit 2; }
if [[ $mode == baseline ]]; then
    [[ $fault == NONE && $severity == 0 ]] || { echo 'Baseline requires NONE 0' >&2; exit 2; }
else
    case $fault in REQUEST_LOOSE|REQUEST_STRICT|RESPONSE_ORACLE|METHOD_SEM) ;; *) echo 'Invalid fault class' >&2; exit 2;; esac
    ((severity > 0)) || { echo 'Mutated run requires positive severity' >&2; exit 2; }
fi
# Select/validate the fuzzer before any Docker command or run-directory creation.
export PILOT_FUZZER=${FUZZER:-schemathesis}
case $PILOT_FUZZER in
    schemathesis) ;;
    evomaster)
        /usr/bin/python3 -I -B "$HERE/evomaster_guard.py" options "$mode" "$seed" "$budget" "${DATA_GEN:-}" "${ONLY_OPS:-}"
        ;;
    *) echo 'Invalid FUZZER: use schemathesis or evomaster' >&2; exit 2;;
esac
source "$HERE/fuzzer_args.sh"
for tool in docker curl java timeout flock git sha256sum grep /usr/bin/python3; do command -v "$tool" >/dev/null || { echo "Missing tool: $tool" >&2; exit 1; }; done
docker compose version >/dev/null
export PILOT_UID=$(id -u) PILOT_GID=$(id -g)
# Original EMB port interpolation accepts an IP prefix; bind published ports to loopback.
export MITM_MAX_BODY=${MITM_MAX_BODY:-65536}
SCHEMA_IMAGE=schemathesis/schemathesis:3.39.16
if [[ $PILOT_FUZZER == evomaster ]]; then
    export PILOT_EVOMASTER_IMAGE=webfuzzing/evomaster@sha256:de1f4387e809a309a4c61517f3340c3d0b733b78bbb86d0e3ebd217d343515ab
    export PILOT_EVOMASTER_VERSION=6.2.0
    # Keep schema-image.json / schemathesis_image as compatibility aliases for analysis.
    SCHEMA_IMAGE=$PILOT_EVOMASTER_IMAGE
fi
MAX_EXAMPLES=${MAX_EXAMPLES:-100}
# Our oracle is tools/conformance.py. Schemathesis abandons an operation at its first failed check,
# so batch 2 uses a check that does not fail on 5xx to keep generating (SCHEMA_CHECKS).
export SCHEMA_CHECKS=${SCHEMA_CHECKS:-all}
[[ $SCHEMA_CHECKS =~ ^[a-z_,]+$ ]] || { echo "Invalid SCHEMA_CHECKS" >&2; exit 2; }
REQUEST_TIMEOUT_MS=${REQUEST_TIMEOUT_MS:-10000}
export PILOT_REQUEST_TIMEOUT_MS="$REQUEST_TIMEOUT_MS" PILOT_HYPOTHESIS_PHASES=explicit,generate
[[ $REQUEST_TIMEOUT_MS =~ ^[1-9][0-9]*$ ]] || { echo 'Invalid REQUEST_TIMEOUT_MS' >&2; exit 2; }
# Fixed fixture values stay in memory and are redacted from saved artifacts.
# Do not use shell xtrace, docker-debug output, or print this variable.
if [[ ${AUTH_HEADER+x} ]]; then
    export PILOT_AUTH_ROLE=${AUTH_ROLE:-custom}
    export PILOT_AUTH_SOURCE=runtime-override
elif [[ $PILOT_AUTH_ROLE == none ]]; then
    AUTH_HEADER=
    export PILOT_AUTH_SOURCE=none
else
    [[ -n $AUTH_SOURCE ]] || { echo 'No auth fixture configured' >&2; exit 2; }
    AUTH_HEADER=$(/usr/bin/python3 -I -B "$HERE/auth_header.py" "$EMB_DIR/$AUTH_SOURCE" "$PILOT_AUTH_ROLE")
    export PILOT_AUTH_SOURCE="$AUTH_SOURCE"
fi
if [[ -n $AUTH_HEADER ]]; then
    [[ $AUTH_HEADER == *:* && $AUTH_HEADER != *$'\n'* && $AUTH_HEADER != *$'\r'* ]] || { echo 'Invalid AUTH_HEADER' >&2; exit 2; }
else
    [[ $PILOT_AUTH_ROLE == none ]] || { echo 'Empty header for authenticated role' >&2; exit 2; }
fi
# Only the redactor receives this host-side environment value; Docker receives -H.
export PILOT_AUTH_REDACT="$AUTH_HEADER"
[[ $MAX_EXAMPLES =~ ^[1-9][0-9]*$ && $HEALTH_PATH == /* && $BASE_PATH == /* ]] || { echo 'Invalid MAX_EXAMPLES, HEALTH_PATH or BASE_PATH' >&2; exit 2; }
# Proposed E5: prebuilt images only; never replace EMB/dist or a fixed pilot tag.
export PILOT_CODE_ROLE=${CODE_ROLE:-}
export PILOT_CODE_SOURCE_SHA256=${CODE_SOURCE_TREE_SHA256:-}
export PILOT_SUT_JAR_PATH=${SUT_JAR_OVERRIDE:-$EMB_DIR/dist/$sut-sut.jar}
if [[ -n $PILOT_CODE_ROLE || -n ${SUT_IMAGE_OVERRIDE:-} || -n ${SUT_JAR_OVERRIDE:-} || -n ${CODE_MANIFEST:-} ]]; then
    [[ $PILOT_CODE_ROLE == control || $PILOT_CODE_ROLE == mutant ]] || { echo 'E5 requires CODE_ROLE=control|mutant' >&2; exit 2; }
    [[ $mode == baseline && $fault == NONE && $severity == 0 ]] || { echo 'E5 keeps the spec unchanged' >&2; exit 2; }
    [[ -n ${SUT_IMAGE_OVERRIDE:-} && -n ${SUT_JAR_OVERRIDE:-} && -s ${CODE_MANIFEST:-} && -s $PILOT_SUT_JAR_PATH ]] || { echo 'E5 image/jar/manifest missing' >&2; exit 2; }
    [[ $PILOT_CODE_SOURCE_SHA256 =~ ^[a-f0-9]{64}$ ]] || { echo 'Missing E5 source-tree digest' >&2; exit 2; }
    export SUT_IMAGE="$SUT_IMAGE_OVERRIDE"
fi
[[ -s $PILOT_SUT_JAR_PATH ]] || { echo 'Missing selected SUT jar' >&2; exit 1; }
for jar in jacocoagent.jar jacococli.jar; do
    [[ -s $EMB_DIR/dist/$jar ]] || { echo "Missing $jar; run prepare_dist.sh first" >&2; exit 1; }
done
# Serialize runs to avoid port, build, and resource contention. Never replace an existing run.
acquire_run_lock
run_id=${PILOT_RUN_ID:-"$(date -u +%Y%m%dT%H%M%SZ)_${mode}_${fault}_p${severity}_s${seed}_$$"}
[[ $run_id =~ ^[A-Za-z0-9][A-Za-z0-9_-]{0,180}$ ]] || { echo 'Invalid run ID' >&2; exit 2; }
run_dir="$EXP/E1_pilot/runs/$sut/$run_id"
mkdir -p "$EXP/E1_pilot/runs/$sut"
mkdir "$run_dir"
export PILOT_LOG_DIR="$run_dir"
project="r1-$sut-$(date -u +%s)-$$"
generator="$project-generator"
compose=(docker compose --project-name "$project" --project-directory "$EMB_DIR" \
    -f "$EMB_DIR/$COMPOSE_FILE" -f "$HERE/compose.override.$sut.yaml")
started=$(date -u +%FT%TZ)
phase=preparation
schema_rc=not_started
coverage_rc=not_attempted
cleanup_rc=0
metadata() {
    /usr/bin/python3 -I -B "$HERE/run_metadata.py" "$run_dir" "$EMB_DIR" "$sut" "$spec" \
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
    container_id=$("${compose[@]}" ps -q "$SUT_SERVICE" 2>>"$run_dir/cleanup.log")
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
    if [[ $PILOT_FUZZER == evomaster ]]; then
        echo "Run: $run_dir; harness exit=$rc; EvoMaster exit=$schema_rc; coverage exit=$coverage_rc"
    else
    echo "Run: $run_dir; harness exit=$rc; Schemathesis exit=$schema_rc; coverage exit=$coverage_rc"
    fi
    exit "$rc"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
metadata pending
cp "$HERE/suts/$sut.env" "$run_dir/sut-config.env"
if [[ -n $PILOT_CODE_ROLE ]]; then
    # Pin to immutable local image ID and require the build labels from the E5 plan.
    e5_image_id=$(docker image inspect --format '{{.Id}}' "$SUT_IMAGE_OVERRIDE")
    e5_jar_sha=$(sha256sum "$PILOT_SUT_JAR_PATH"); e5_jar_sha=${e5_jar_sha%% *}
    [[ $(docker image inspect --format '{{index .Config.Labels "org.r1.jar_sha256"}}' "$e5_image_id") == "$e5_jar_sha" ]] || { echo 'E5 image/jar label mismatch' >&2; exit 1; }
    [[ $(docker image inspect --format '{{index .Config.Labels "org.r1.source_tree_sha256"}}' "$e5_image_id") == "$PILOT_CODE_SOURCE_SHA256" ]] || { echo 'E5 image/source label mismatch' >&2; exit 1; }
    cp "$CODE_MANIFEST" "$run_dir/code.manifest.json"
    /usr/bin/python3 -I -B - "$run_dir/code.manifest.json" "$sut" "$PILOT_CODE_ROLE" "$PILOT_CODE_SOURCE_SHA256" "$run_dir/compose.code-image.json" "$SUT_SERVICE" "$e5_image_id" <<'E5_PY'
import json, pathlib, sys
manifest, sut, role, expected, dest, service, image = sys.argv[1:]
m = json.loads(pathlib.Path(manifest).read_text())
assert m['injection_side'] == 'IMPL' and m['sut'] == sut
key = 'source_tree_sha256' if role == 'control' else 'mutated_tree_sha256'
assert m[key] == expected, 'E5 source digest differs from manifest'
with open(dest, 'x') as stream:
    json.dump({'services': {service: {'image': image}}}, stream)
E5_PY
    compose+=(-f "$run_dir/compose.code-image.json")
fi
# Snapshot the JSON source before either mutation pass.
cp "$spec" "$run_dir/spec.original.${spec##*.}"
original_spec="$run_dir/spec.original.${spec##*.}"
test_spec="$original_spec"
if [[ $mode == mutated ]]; then
    # Optional candidate pool (ONLY_OPS = eligible_ops.py output); the same pool feeds both passes.
    only_args=()
    if [[ -n ${ONLY_OPS:-} ]]; then
        [[ -s $ONLY_OPS ]] || { echo "ONLY_OPS file missing: $ONLY_OPS" >&2; exit 2; }
        cp "$ONLY_OPS" "$run_dir/only-ops.json"
        only_args=(--only-ops "$run_dir/only-ops.json")
    fi
    /usr/bin/python3 -I -B "$TOOLS_DIR/specmut.py" "$original_spec" --fault "$fault" --severity "$severity" \
        --seed "$seed" "${only_args[@]}" --out "$run_dir/mutation" >"$run_dir/specmut.log" 2>&1
    shopt -s nullglob
    manifests=("$run_dir"/mutation/*.manifest.json)
    [[ ${#manifests[@]} == 1 ]] || { echo 'Expected exactly one mutation manifest' >&2; exit 1; }
    cp "${manifests[0]}" "$run_dir/manifest.json"
    /usr/bin/python3 -I -B -c 'import json,sys; m=json.load(open(sys.argv[1])); sys.exit(0 if m["operations_mutated"] > 0 else "Mutation changed no operations")' "$run_dir/manifest.json"
    test_spec="${manifests[0]%.manifest.json}.json"
fi
cp "$test_spec" "$run_dir/spec.test.${test_spec##*.}"
# Keep both the effective compose configuration and immutable image IDs/digests.
"${compose[@]}" config >"$run_dir/compose.resolved.yaml"
if [[ $PILOT_FUZZER == evomaster ]]; then
    /usr/bin/python3 -I -B "$HERE/evomaster_guard.py" schema "$run_dir/spec.test.json" "$BASE_PATH"
    # The supervisor already pulled this immutable image. Never pull or run help here.
    docker image inspect "$SCHEMA_IMAGE" >"$run_dir/schema-image.json"
    cp "$run_dir/schema-image.json" "$run_dir/evomaster-image.json"
else
# A registry/DNS outage must not abort a run when the pinned image is already local;
# its exact ID/digest is recorded below either way.
if ! docker pull "$SCHEMA_IMAGE" >"$run_dir/schema-pull.log" 2>&1; then
    docker image inspect "$SCHEMA_IMAGE" >/dev/null 2>&1 || { echo "Cannot pull $SCHEMA_IMAGE and no local copy" >&2; exit 1; }
    echo "pull failed; using local copy of $SCHEMA_IMAGE" >>"$run_dir/schema-pull.log"
fi
docker image inspect "$SCHEMA_IMAGE" >"$run_dir/schema-image.json"
# Capture CLI help from the pinned image before starting the SUT; abort on incompatible flags.
docker run --rm "$SCHEMA_IMAGE" run --help >"$run_dir/schemathesis-help.txt" 2>&1
for flag in --checks --hypothesis-seed --hypothesis-max-examples --junit-xml --cassette-path --base-url --request-timeout --hypothesis-phases --header --sanitize-output; do
    if ! grep -q -- "$flag" "$run_dir/schemathesis-help.txt"; then
        echo "Pinned Schemathesis CLI missing $flag" >&2; exit 1
    fi
done
fi
phase=startup
if [[ -n $PILOT_CODE_ROLE ]]; then
    "${compose[@]}" up -d --no-build >"$run_dir/compose-up.log" 2>&1
elif docker image inspect "$SUT_IMAGE" >/dev/null 2>&1; then
    "${compose[@]}" up -d --no-build >"$run_dir/compose-up.log" 2>&1
else
    "${compose[@]}" up -d --build >"$run_dir/compose-up.log" 2>&1
fi
for service in "$SUT_SERVICE" mitmproxy; do
    cid=$("${compose[@]}" ps -q "$service")
    [[ -n $cid ]] || { echo "Missing container: $service" >&2; exit 1; }
    docker inspect "$cid" >"$run_dir/$service-container.json"
    image_id=$(docker inspect --format '{{.Image}}' "$cid")
    docker image inspect "$image_id" >"$run_dir/$service-image.json"
done
# Probe through the proxy; readiness traffic is quarantined before generation.
ready=0
for ((attempt=1; attempt<=60; attempt++)); do
    if [[ ${HEALTH_METHOD_DEFAULT:-GET} == POST ]]; then
        # CWA disables actuator HTTP and exposes POST-only business routes.
        # Empty body tests MVC binding without invoking the operation or dependencies.
        if health_status=$(curl --silent --show-error --max-time 2 --request POST \
            --header 'Content-Type: application/json' --data '' -o /dev/null --write-out '%{http_code}' \
            "http://127.0.0.1:18080$HEALTH_PATH" 2>"$run_dir/health-error.txt") \
            && [[ $health_status == "${HEALTH_STATUS_DEFAULT:?Set expected POST readiness status}" ]]; then ready=1; break; fi
    elif curl --fail --silent --show-error --max-time 2 "http://127.0.0.1:18080$HEALTH_PATH" \
        -o /dev/null 2>"$run_dir/health-error.txt"; then ready=1; break; fi
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
if [[ $PILOT_FUZZER == schemathesis ]]; then
build_schemathesis_argv
# mount the run directory, so the input and every output remain in this run.
# Generator input only: cut recursive $ref back-edges (hypothesis-jsonschema stalls on them).
# Conformance analysis keeps using spec.test.* (the untouched original or mutated spec).
if [[ $mode == mutated ]]; then
    # specmut inlines $refs into mutated operations, which would unroll recursive schemas again.
    # So: de-recurse the ORIGINAL first, then apply the same mutation (same fault/severity/seed
    # => same operations selected) to obtain the generator input.
    /usr/bin/python3 -I -B "$HERE/derecurse.py" "$original_spec" "$run_dir/spec.derecursed.json" >"$run_dir/derecurse-cuts.json"
    /usr/bin/python3 -I -B "$TOOLS_DIR/specmut.py" "$run_dir/spec.derecursed.json" --fault "$fault" --severity "$severity" \
        --seed "$seed" "${only_args[@]}" --out "$run_dir/mutation_gen" >"$run_dir/specmut_gen.log" 2>&1
    gen=("$run_dir"/mutation_gen/*.manifest.json)
    [[ ${#gen[@]} == 1 ]] || { echo 'Expected one generator mutation manifest' >&2; exit 1; }
    /usr/bin/python3 -I -B -c 'import json,sys; a,b=(json.load(open(p)) for p in sys.argv[1:3]); k=lambda m: sorted((x["path"],x["method"]) for x in m["mutations"]); sys.exit(0 if k(a)==k(b) else "Generator mutation selected different operations")' "$run_dir/manifest.json" "${gen[0]}"
    cp "${gen[0]%.manifest.json}.json" "$run_dir/generator-input.json"
else
    /usr/bin/python3 -I -B "$HERE/derecurse.py" "$test_spec" "$run_dir/generator-input.json" >"$run_dir/derecurse-cuts.json"
fi
schema_cmd[1]="/work/generator-input.json"
record_fuzzer_argv "$run_dir/schemathesis-argv.txt" -H
else
    # Compatibility snapshot required by analyse_run.sh; no de-recursion for EvoMaster.
    cp "$run_dir/spec.test.json" "$run_dir/generator-input.json"
    mkdir "$run_dir/evomaster"
    build_evomaster_argv
    record_fuzzer_argv "$run_dir/evomaster-argv.txt" --header0
fi
metadata pending
set +e
if [[ $PILOT_FUZZER == evomaster ]]; then
    # maxTime bounds search; allow startup and generated-test/statistics serialization.
    # A watchdog timeout is still incomplete, exactly as on the default path.
    timeout --signal=INT --kill-after=20 "$((budget + 120))s" docker run --rm --name "$generator" \
        --user "$PILOT_UID:$PILOT_GID" --workdir /work/evomaster --network "${project}_default" \
        -v "$run_dir:/work" -v "$run_dir/spec.test.json:/work/spec.test.json:ro" \
        "$SCHEMA_IMAGE" "${schema_cmd[@]}" 2>&1 | /usr/bin/python3 -I -B "$HERE/redact_auth.py" >"$run_dir/evomaster.log"
    pilot_pipeline_rc=("${PIPESTATUS[@]}")
else
timeout --signal=INT --kill-after=20 "${budget}s" docker run --rm --name "$generator" \
    --user "$PILOT_UID:$PILOT_GID" -e XDG_CACHE_HOME=/tmp/cache \
    -e HYPOTHESIS_STORAGE_DIRECTORY=/tmp/hypothesis --network "${project}_default" \
    -v "$run_dir:/work" "$SCHEMA_IMAGE" "${schema_cmd[@]}" 2>&1 | /usr/bin/python3 -I -B "$HERE/redact_auth.py" >"$run_dir/schemathesis.log"
    pilot_pipeline_rc=("${PIPESTATUS[@]}")
fi
schema_rc=${pilot_pipeline_rc[0]}
((pilot_pipeline_rc[1] == 0)) || { echo 'Output redaction failed' >&2; exit 1; }
set -e
phase=collection
if [[ $PILOT_FUZZER == evomaster ]]; then
    case $schema_rc in
        0|1) /usr/bin/python3 -I -B "$HERE/evomaster_guard.py" outputs "$run_dir/evomaster" ;;
        124|137) echo 'Generation budget expired; partial run retained, do not treat as complete' >&2; exit "$schema_rc";;
        *) echo "EvoMaster execution failed ($schema_rc)" >&2; exit "$schema_rc";;
    esac
else
# Exit 1 includes test failures; the report/log retains the outcome. Timeouts are incomplete.
case $schema_rc in
    0|1) [[ -s $run_dir/schemathesis.junit.xml ]] || { echo 'Missing JUnit report' >&2; exit 1; };;
    124|137) echo 'Generation budget expired; partial run retained, do not treat as complete' >&2; exit "$schema_rc";;
    *) echo "Schemathesis execution failed ($schema_rc)" >&2; exit "$schema_rc";;
esac
fi
phase=complete
