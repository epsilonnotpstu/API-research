#!/usr/bin/env bash
set -euo pipefail
# Pure argv builders. The caller supplies validated run settings; no subprocesses.
build_schemathesis_argv() {
    schema_cmd=(run "/work/$(basename "$test_spec")" --base-url "http://mitmproxy:8080$BASE_PATH" \
        --checks "$SCHEMA_CHECKS" --hypothesis-seed "$seed" --hypothesis-max-examples "$MAX_EXAMPLES" \
        --junit-xml /work/schemathesis.junit.xml --cassette-path /work/schemathesis-cassette.yaml \
        --request-timeout "$REQUEST_TIMEOUT_MS" --hypothesis-phases "$PILOT_HYPOTHESIS_PHASES" --sanitize-output true)
    # An unset or empty DATA_GEN preserves the original argv exactly.
    if [[ -n ${DATA_GEN:-} ]]; then
        [[ $DATA_GEN =~ ^(positive|negative|all)$ ]] || { echo 'Invalid DATA_GEN' >&2; return 2; }
        schema_cmd+=(--data-generation-method "$DATA_GEN")
    fi
}

build_evomaster_argv() {
    schema_cmd=(--blackBox true --problemType REST --base http://mitmproxy:8080 \
        --schema /work/spec.test.json --seed "$seed" --stoppingCriterion TIME --maxTime "${budget}s" \
        --outputFolder /work/evomaster/tests --outputFormat JAVA_JUNIT_5 \
        --writeStatistics true --statisticsFile /work/evomaster/statistics.csv \
        --appendToStatisticsFile false --ratePerMinute 0 --schemaOracles "$PILOT_EVOMASTER_SCHEMA_ORACLES" \
        --tcpTimeoutMs "$REQUEST_TIMEOUT_MS" --createConfigPathIfMissing false)
}

record_fuzzer_argv() {
    local destination=$1 header_flag=$2
    printf '%s\n' "${schema_cmd[@]}" >"$destination"
    if [[ -n $AUTH_HEADER ]]; then
        printf '%s\n' "$header_flag" '<redacted>' >>"$destination"
        schema_cmd+=("$header_flag" "$AUTH_HEADER")
    fi
}

# Keep the container schema path stable; only opt-in changes its read-only source.
build_evomaster_mounts() {
    local schema_source="$run_dir/spec.test.json"
    if [[ ${PILOT_EVOMASTER_INPUT:-spec} == derecursed ]]; then
        schema_source="$run_dir/generator-input.json"
    fi
    evomaster_mounts=(-v "$run_dir:/work" -v "$schema_source:/work/spec.test.json:ro")
}
