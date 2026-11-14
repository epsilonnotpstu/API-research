#!/usr/bin/env bash
# Trusted, non-secret configuration shared by the v2 scripts.
load_sut() {
    case ${1:-} in scout-api|swagger-petstore|market|cwa-verification) ;; *) echo 'Unsupported SUT' >&2; return 2;; esac
    # Only checked-in configurations from the allowlist are sourced.
    source "$HERE/suts/$1.env"
    export EMB_DIR="$EXP/_external/emb" TOOLS_DIR="$EXP/tools"
    export SUT_ID SUT_SERVICE INTERNAL_PORT SUT_IMAGE COMPOSE_FILE DOCKERFILE
    export JAR_SOURCE SPEC_SOURCE AUTH_SOURCE
    export HEALTH_PATH=${HEALTH_PATH:-$HEALTH_PATH_DEFAULT}
    export BASE_PATH=${BASE_PATH:-$BASE_PATH_DEFAULT}
    export PILOT_AUTH_ROLE=${AUTH_ROLE:-$AUTH_ROLE_DEFAULT}
    # These interpolate into the original EMB Compose port declarations.
    export HOST_PORT=127.0.0.1:18080 JACOCO_PORT=127.0.0.1:16300
}

acquire_run_lock() {
    exec 9>"$HERE/.run.lock"
    flock -n 9 || { echo 'Another v2 pilot/preparation is running' >&2; return 1; }
    # Share the existing v1 lock without writing or truncating any v1 file.
    if [[ -f $HERE/../harness/.run.lock ]]; then
        exec 8<"$HERE/../harness/.run.lock"
        flock -n 8 || { echo 'The v1 pilot is running; retry after it finishes' >&2; return 1; }
    fi
}
