# Scout API pilot harness (T5)

Write-only handoff: T5 has not run these scripts, Docker, Schemathesis, Java,
or the SUT. T7 executes them under its own authorization. Only scout-api is
supported; unsupported SUT names fail. Scripts require Bash 4+, GNU coreutils
(`timeout`, `realpath`, `sha1sum`, `sha256sum`), `flock`, curl, Git, Java 8+
(for the JaCoCo CLI), Docker Engine + Compose v2, and `/usr/bin/python3` with
existing PyYAML/jsonschema dependencies. There are no dependency installs.

## Exact sequence (Bash, from research/)

Before running: finish T10 and its checks, verify Docker access, available
ports 18080/16300, disk space and the built scout jar. `prepare_dist.sh` writes
to EMB/dist only when executed; it downloads the 0.8.12 runtime agent **and**
nodeps JaCoCo CLI, checks each against its Maven Central `.sha1` over HTTPS,
and atomically installs changed artifacts. SHA-1 here is the requested
repository integrity check, not an independent authenticity signature.

```bash
set -euo pipefail
H="$PWD/08_experiments/E1_pilot/harness"
SPEC="$PWD/08_experiments/_external/emb/openapi-swagger/scout-api.json"
RUNS="$PWD/08_experiments/E1_pilot/runs/scout-api"
"$H/prepare_dist.sh" scout-api

# Same per-operation maximum and wall budget for every condition.
export MAX_EXAMPLES=100
export HEALTH_PATH=/admin/healthcheck
export BASE_PATH=/api
for seed in 1 2 3; do
  "$H/run_pilot.sh" scout-api "$SPEC" baseline NONE 0 "$seed" 600
done

# Select this batch's seed-1 baseline; timestamp-prefixed names sort by start time.
# Check the printed path and run.json before using a baseline from another session.
baselines=("$RUNS"/*_baseline_NONE_p0_s1_*)
BASELINE="${baselines[-1]}"
test -f "$BASELINE/run.json"
printf 'Seed-1 baseline: %s\n' "$BASELINE"
for fault in REQUEST_LOOSE REQUEST_STRICT RESPONSE_ORACLE METHOD_SEM; do
  "$H/run_pilot.sh" scout-api "$SPEC" mutated "$fault" 30 1 600
  mutants=("$RUNS"/*_mutated_"${fault}"_p30_s1_*)
  MUTATED="${mutants[-1]}"
  "$H/analyse_run.sh" "$MUTATED" "$BASELINE" --mode both
done
```

Standalone analysis alternatives (choose a completed mutated run from the
printed output):

```bash
"$H/analyse_run.sh" "$MUTATED" "$BASELINE" --mode fresh
"$H/analyse_run.sh" "$MUTATED" "$BASELINE" --mode replay
```

Default is `both`. Each analysis creates a new `analysis-MODE/` directory and
refuses to overwrite it. Analysis requires complete run metadata, matching
seed, budget, generator maximum, original spec hash, SUT jar, EMB commit,
image IDs, auth/base path, logger size and captured tools; it checks exchange,
spec and manifest hashes. Keep tool files stable throughout the batch. Analysis
records the current checker hashes separately. T10's `attribute.py --mode
fresh|replay` is required; there is no fallback to the pre-T10 attribution.

If a command fails, `set -e` stops the batch. Inspect that run's `run.json`,
`schemathesis.log`, `compose.log`, and `jacoco-dump.log`; correct the cause and
start a new run. Do not reuse or overwrite partial run directories.

## Execution and artifacts

`run_pilot.sh` uses a unique Compose project, serializes runs with `flock`,
sets the EMB context explicitly, binds host ports to loopback, and runs
Schemathesis on the private Compose network through mitmproxy. Only the spec
changes between conditions. A fresh JVM and H2 in-memory database are created
for each run (configuration: `../../_external/emb/scripts/dockerize/data/additional_files/scout-api/scout_api_evomaster.yml:24-36`).
Proxy readiness probes are moved to `readiness-exchanges.jsonl` after stopping
and flushing the proxy, then excluded from the generator exchange file.
The logger runs as the host UID/GID to keep artifacts writable.

The pinned official image is `schemathesis/schemathesis:3.39.16`. This harness
uses its v3 CLI: `--checks all`, `--hypothesis-seed`,
`--hypothesis-max-examples`, `--base-url`, `--junit-xml`, `--cassette-path`.
Version-specific docs could not be retrieved during T5; T7 must verify image
availability and CLI behavior. The harness saves `run --help` and rejects
missing flags before starting the SUT. Current CLI documentation uses changed
flag names; do not silently swap to a v4 image
([official CLI](https://schemathesis.readthedocs.io/en/stable/reference/cli/)).

`MAX_EXAMPLES` is per operation, not a whole-run request count. GNU `timeout`
caps generation wall time at the requested seconds, with up to 20 seconds
for interrupt handling, followed by cleanup. Startup (roughly 240 seconds
maximum health probing), builds, pulls and collection are outside that budget.
Schemathesis status 1 is retained as a testing outcome if a JUnit report exists;
JUnit and text logs must still be reviewed for test errors versus assertions.
Budget expiry is an incomplete run and exits nonzero; JUnit/cassette may be
unfinished, while stdout remains available. Raise the common budget or lower
the common example limit and rerun all conditions if complete runs are needed.

Each `E1_pilot/runs/scout-api/<run_id>/` holds:

- `run.json`: all seven arguments, effective example/body limits, paths, auth
  assumption, timestamps, return codes, EMB commit/dirty status, SHA-256 hashes,
  image IDs and registry digests when present. Local SUT builds usually have
  an image ID without `RepoDigests`; that is recorded explicitly.
- Original and tested spec snapshots; mutated runs also have `mutation/`,
  `manifest.json`, `specmut.log` and the exact generator input.
- `exchanges.jsonl`, `schemathesis.log`, JUnit XML and cassette when flushed;
  exact generator arguments, saved CLI help, resolved compose and inspection JSON.
- `jacoco.exec`, dump log, Compose logs, cleanup logs and health evidence.

The EXIT/INT/TERM handler removes only this run's named generator, dumps
coverage while the SUT is alive, then tears down only this Compose project.
There is no system prune or volume deletion. JaCoCo's CLI dump is the documented
way to retrieve TCP-server execution data
([official dump command](https://www.jacoco.org/jacoco/trunk/doc/cli.html)).
Coverage failure, empty exchanges or teardown failure marks the run incomplete.
SIGKILL, host loss or Docker daemon loss cannot guarantee cleanup; use the
saved project name and resolved compose to inspect and clean up that project.
Do not infer successful completion from directory existence alone.

## Assumptions and review gates for T7

- **Health:** `/admin/healthcheck` through port 8080 is an inference from
  `scout_api_evomaster.yml:5-10` and `ScoutAPIApplication.java:146-147` (under
  `jdk_8_maven/cs/rest/original/scout-api/api/src/main/java/se/devscout/scoutapi/`).
  ⚠️ Its actual HTTP route and proxy behavior remain unverified. A non-2xx
  response fails readiness. Override `HEALTH_PATH` only after confirming it.
- **Base path:** `/api` is declared in `openapi-swagger/scout-api.json:11` and
  `scout_api_evomaster.yml:5`; the v3 `--base-url` handling must be checked
  against actual captured request paths, especially doubled or missing `/api`.
- **Authentication:** spec has no security declaration, but
  `ScoutAPIApplication.java:186-203` registers auth filters, and
  `auth/src/main/java/se/devscout/scoutapi/auth/apikey/ApiKeyAuthenticator.java:17`
  declares `ApiKey`. Config seeds `user`, `moderator`, `administrator`
  identities (`scout_api_evomaster.yml:50-65`). ⚠️ Unauthenticated coverage may
  be limited. This batch deliberately records auth=`none`; a confirmed auth
  experiment needs a separate documented configuration and reruns of controls.
- **Logger errors (T4 S03):** T10 owns `tools/mitm_fulllog.py`. T10/T7 should
  provide and verify an `error(flow)` hook for upstream timeout/reset, recording
  request + correlation ID + transport error even without a response. Add that
  hook in the logger, not this harness. Keep failed flows distinct from HTTP
  violations; reconcile attempted/generated requests, response exchanges,
  transport failures and truncated bodies before interpreting coverage.
  T5 has not changed the logger and does not assert that this hook exists.
- **Inference limits:** fresh analysis uses baseline traffic/original oracle
  versus mutated traffic/mutated oracle (`--mode fresh`); NEW/VANISHED are
  observational and need manual causal review. Replay evaluates **the same
  baseline exchange records**, first with the original, then mutated spec
  (`--mode replay`); it sends no HTTP requests and isolates checker/oracle
  differences. It cannot measure generation-side harm of REQUEST_LOOSE or
  REQUEST_STRICT. See `09_collab/reports/T4_review.md:R03,S03` from research/.
- **Runtime checks:** UID/GID permissions, image entrypoint/flags, health route,
  base-path behavior, JVM/agent compatibility, TCP dump and proxy flushing are
  integration questions. T5 only supplies static validation. Fixed seeds do
  not make stateful fuzzing or fresh runs identical; baseline seeds 1–3 help
  observe variation but do not prove causal attribution.
