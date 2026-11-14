# Multi-SUT pilot harness v2 — T14 handoff

T14 supplies scripts and static validation only. Docker, Java, Schemathesis,
SUTs, downloads and these orchestration scripts were not executed during T14;
validation evidence is in `static_checks.txt:2–39`. The source harness is unchanged
(reference digests: `source-harness-sha256.json:1–12`; verification in `static_checks.txt:17`).

The scripts load only the three allowlisted, non-secret `suts/*.env` files
(`common.sh:3–15`). Paths below are relative to `08_experiments/_external/emb/`.

| SUT | Fixed image | Base path | Readiness path | Runtime auth |
|---|---|---|---|---|
| scout-api | `r1-scout-api-sut:pilot` | `/api` | ⚠️ `/admin/healthcheck` | `administrator`, `auth/scout-api-auth.yaml` |
| swagger-petstore | `r1-swagger-petstore-sut:pilot` | ⚠️ `/api/v3` | ⚠️ `/api/v3/openapi.json` | `none`; no auth fixture exists |
| market | `r1-market-sut:pilot` | `/` | ⚠️ `/v2/api-docs` | `user`, `auth/market-auth.yaml` |

These are the exact defaults in `suts/scout-api.env:2–14`,
`suts/swagger-petstore.env:2–14`, and `suts/market.env:2–14`.
All three internal HTTP ports are 8080; sources are their
`dockerfiles/<sut>.yaml` service/proxy definitions and
`dockerfiles/<sut>.dockerfile` entrypoints. First-run assumptions appear below;
T14 has not verified any HTTP route.

## Exact batch commands from research/ (Bash)

Run after the existing v1 batch has finished. Required local tools are Bash 4+,
GNU coreutils (`realpath`, `timeout`, `sha1sum`, `sha256sum`), `flock`, curl, Git,
Java for JaCoCo, Docker Engine/Compose v2, and `/usr/bin/python3` with the existing
PyYAML/jsonschema dependencies. There are no installation steps in this harness
(`prepare_dist.sh:9`; `run_pilot.sh:19`; `auth_header.py:5`).

Each invocation below runs 3 seeds × (baseline + 4 fault classes), then analyses
each mutation in fresh and replay modes. `SCHEMA_CHECKS` defaults to `all`; these
commands explicitly choose `response_headers_conformance` to continue generation
past checks such as 5xx. Keep the same check choice across every paired condition;
it is recorded in `run.json` (`run_batch.sh:19–20,39–44`; `run_metadata.py:46`). This setting
does not change the separate conformance oracle in `analyse_run.sh:63–72`.

```bash
set -euo pipefail
H="$PWD/08_experiments/E1_pilot/harness_v2"
export MAX_EXAMPLES=100 REQUEST_TIMEOUT_MS=10000 BUDGET_SECONDS=300 SEVERITY=30
export SCHEMA_CHECKS=response_headers_conformance
# Use each SUT's default route/role; do not inherit another SUT's override.
unset HEALTH_PATH BASE_PATH AUTH_ROLE AUTH_HEADER PILOT_RUN_ID

# scout-api: built Java 8 jar; administrator fixture loaded at runtime.
"$H/prepare_dist.sh" scout-api
"$H/run_batch.sh" scout-api 1 2 3

# swagger-petstore: built Java 8 jar; no credential injected.
"$H/prepare_dist.sh" swagger-petstore
"$H/run_batch.sh" swagger-petstore 1 2 3

# market: built Java 11 jar; user fixture loaded at runtime.
"$H/prepare_dist.sh" market
"$H/run_batch.sh" market 1 2 3
```

The three SUT blocks can be run individually after the shared setup. Omitting
seeds uses `1 2 3`; any distinct non-negative seeds can be passed. A failed run
or analysis stops the batch with nonzero exit; the next attempt uses a new batch
ID. `runs/<sut>/batches/<batch_id>/runs.tsv` lists successful runs from that exact
batch. Pairing never selects directories from earlier batches (`run_batch.sh:26–44`).

`prepare_dist.sh <sut>` copies only the corresponding built jar to
`EMB/dist/<sut>-sut.jar`, if changed. It fetches/verifies the JaCoCo 0.8.12 runtime
agent and nodeps CLI against Maven Central `.sha1` files over HTTPS; changes are
staged and atomically moved (`prepare_dist.sh:10–51`). SHA-1 provides a repository
integrity check, not an independent signature. Built jar paths are listed in
each SUT config's `JAR_SOURCE`.

## Exact single-pair commands

The same interface supports each SUT. Set `sut` to `scout-api`,
`swagger-petstore`, or `market`; the following example is a market pair.

```bash
set -euo pipefail
H="$PWD/08_experiments/E1_pilot/harness_v2"
sut=market
SPEC="$PWD/08_experiments/_external/emb/openapi-swagger/$sut.json"
RUNS="$PWD/08_experiments/E1_pilot/runs/$sut"
stamp="$(date -u +%Y%m%dT%H%M%SZ)_manual_$$"
export MAX_EXAMPLES=100 REQUEST_TIMEOUT_MS=10000
export SCHEMA_CHECKS=response_headers_conformance
unset HEALTH_PATH BASE_PATH AUTH_ROLE AUTH_HEADER PILOT_RUN_ID
"$H/prepare_dist.sh" "$sut"
PILOT_RUN_ID="${stamp}_baseline" "$H/run_pilot.sh" "$sut" "$SPEC" baseline NONE 0 1 300
PILOT_RUN_ID="${stamp}_strict" "$H/run_pilot.sh" "$sut" "$SPEC" mutated REQUEST_STRICT 30 1 300
"$H/analyse_run.sh" "$RUNS/${stamp}_strict" "$RUNS/${stamp}_baseline" --mode both
```

`--mode fresh` and `--mode replay` are available separately. Each analysis uses
exclusive `mkdir analysis-MODE` and refuses to replace earlier output
(`analyse_run.sh:61–62`). Repeating `both` on the same pair fails by design.

## Preserved behavior and artifacts

- The logger uses `entrypoint: ["mitmdump"]`, the host UID/GID, the full-exchange
  addon, and an explicit upstream service for each SUT
  (`compose.override.scout-api.yaml:1–34`, `compose.override.swagger-petstore.yaml:1–34`,
  `compose.override.market.yaml:1–34`). Original Compose publishes only proxy/JaCoCo;
  `common.sh:14` binds both to loopback, 18080 and 16300.
- SUT images build on the first missing tag and use `--no-build` thereafter
  (`run_pilot.sh:137–141`). Scout's v2 tag intentionally follows T14's naming
  convention and differs from v1's `r1-scout-sut:pilot`. Keep jars, Dockerfiles,
  image tags, tools and v2 files stable for a whole batch. Changing the jar does
  not rebuild an existing fixed tag automatically.
- A v2 flock serializes all SUTs and preparation. If v1's lock file exists,
  v2 also acquires it through a read-only descriptor, without truncating it
  (`common.sh:17–25`). Do not launch a new v1 batch concurrently when that file
  does not yet exist. Runs use fresh Compose projects and exclusive run-directory
  creation (`run_pilot.sh:57–68`).
- Input is JSON for these three SUTs. Baselines use `derecurse(original)`;
  mutants use `specmut(derecurse(original))`. The actual oracle snapshot remains
  `original` or `specmut(original)`. Both mutation passes must report the same
  set of `(path, method)` pairs or the run fails (`run_pilot.sh:111–125,176–190`).
  ⚠️ Equal operation sets do not imply equal constraint edits or generated values.
  This generator/oracle difference is a validity threat inherited from
  `../pilot_results/BATCH1_RESULTS.md:46–51`.
- `derecurse.py` handles direct named-schema refs in both `definitions` and
  `components/schemas`, escaped pointer names, arrays/compositions, and ref
  siblings. It replaces DFS back edges with an unconstrained object, preserving
  the earlier policy (`derecurse.py:19–61`). External refs, refs to other component
  groups, anchors and schema-subschema pointers are left intact. Its regression
  tests include static transforms of all three actual spec documents
  (`test_derecurse.py:108–117`). This is a generation workaround, not a semantic repair.
- Schemathesis stays pinned to `3.39.16`, with a 10000 ms default request timeout,
  `explicit,generate` phases (no shrinking), saved help/argv, JUnit and cassette.
  Generation wall budget excludes startup/pulls/collection
  (`run_pilot.sh:24–32,127–135,169–172,198–213`).
- Credentials are read in memory from EMB YAML at execution. `run.json` stores
  role/source and source digest, never the fixture value. No auth header is added
  for petstore. The logger redacts Authorization; the console stream and saved
  files also pass through `redact_auth.py` (`auth_header.py:8–30`; `run_pilot.sh:33–52,
  92–102,192–201`; `run_metadata.py:43–53`). Do not enable `bash -x`, save the
  Docker generator command, or paste fixture values into overrides/reports.
- Each `runs/<sut>/<run_id>/` contains original/test/generator specs, mutation
  manifests and cut edges, exchanges, logs, sanitized argv, image/container
  inspections, effective Compose, the non-secret SUT config, JaCoCo `.exec`, and
  atomic `run.json`. Provenance includes the check choice, tool/harness/config
  hashes, EMB commit, jar/agent/CLI hashes and image IDs/digests
  (`run_metadata.py:20–74`; `run_pilot.sh:80–111,124–148,176–202`). Analysis rejects incompatible pairs,
  changed inputs, and current tool/harness drift (`analyse_run.sh:13–50`).
- Cleanup dumps JaCoCo before JVM teardown and removes only the named generator
  and this Compose project. Timeout, empty exchanges, coverage/redaction/cleanup
  failure means incomplete; exit 1 from Schemathesis can represent assertions
  and requires JUnit review (`run_pilot.sh:80–108,207–213`). Host loss/SIGKILL can
  bypass cleanup. No prune, global cleanup, dependency installs or SUT build is
  performed by T14's checks (`static_checks.txt:2–39`).

## Assumptions Claude must verify at first execution

1. **Readiness and routing.** ⚠️ Scout's `/admin/healthcheck` follows Dropwizard's
   simple server (`scripts/dockerize/data/additional_files/scout-api/scout_api_evomaster.yml:1–9`).
   Petstore's `/api/v3/openapi.json` follows
   `jdk_8_maven/cs/rest/original/swagger-petstore/README.md:40` and
   `openapi-swagger/swagger-petstore.json#/servers`, but
   `jdk_8_maven/cs/rest/original/swagger-petstore/src/main/java/io/swagger/petstore/Main.java:54–65`
   maps the servlet to `/api/*` and `scripts/dockerize/data/additional_files/swagger-petstore/inflector.yaml:16`
   sets `rootPath: /api`. Confirm the actual endpoint; do not accept a UI page as
   proof that API routing works. Market's `/v2/api-docs` is inferred from
   `jdk_11_maven/cs/rest-gui/market/market-rest/src/main/java/market/RestConfig.java:15–21`
   (Springfox Swagger 2). A failed public readiness route stops the run. Confirm
   runtime paths against `openapi-swagger/<sut>.json` (`basePath` or `servers`).
   If petstore needs a different `BASE_PATH`, separately review how the unchanged
   conformance spec will match those paths; never silently alter the oracle.
2. **Authentication.** ⚠️ Confirm the seeded scout administrator and market user
   fixtures work through the proxy, and inspect protected-operation coverage.
   Market uses `user` because `/customer**` requires `ROLE_USER`
   (`jdk_11_maven/cs/rest-gui/market/market-rest/src/main/java/market/RestSecurityConfig.java:9–17`).
   `admin` and `user2` exist as alternate EMB fixture roles; changing `AUTH_ROLE`
   requires new matched controls. ⚠️ Petstore declares operation security schemes
   (`openapi-swagger/swagger-petstore.json#/components/securitySchemes`) but has
   no EMB auth fixture; unauthenticated operation coverage must be checked.
3. **Image and JVM identity.** ⚠️ Confirm the fixed-tag image actually contains
   the intended jar, Java 8 for scout/petstore and Java 11 for market, and that
   JaCoCo 0.8.12 dumps on TCP 16300. Dockerfile base images/entrypoints provide
   the intended versions (`dockerfiles/<sut>.dockerfile`), not execution proof.
   If rebuilding a stale tag, do so before starting a whole new batch.
4. **Reset and data.** ⚠️ Verify clean application state per fresh JVM. Scout
   has `init_db.sql` and an in-memory configuration in its additional-files
   directory; petstore has `inflector.yaml`; no additional-files/market directory
   exists. Market's Dockerfile supplies an H2 memory URL. These are source-level
   observations, not runtime reset evidence (the named files and
   `dockerfiles/market.dockerfile`). No extra database service was inferred.
5. **Generator/logging behavior.** ⚠️ Confirm pinned CLI flags, the chosen check,
   no shrinking, request timeout, UID/GID write access, proxy restart/flushing,
   secret sanitization, and successful JaCoCo collection. Inspect operation and
   2xx-body exposure; `complete=true` does not mean every operation or mutation
   was exercised. The existing logger has only a response hook
   (`../../tools/mitm_fulllog.py:40–55`); transport failures can be absent from
   exchange logs. Review truncation and generator errors before interpreting data.
6. **Interpretation.** Fresh NEW/VANISHED compare different generated traffic;
   they are observational. Replay changes the oracle over the same saved baseline
   exchanges and sends no HTTP requests (`analyse_run.sh:63–72`). Fixed seeds do
   not guarantee identical traffic. The prior validity threat and check-selection
   effects must accompany results (`../pilot_results/BATCH1_RESULTS.md:34–51`).

## Safe validation performed in T14

```bash
/usr/bin/python3 -I -B 08_experiments/E1_pilot/harness_v2/test_derecurse.py
for script in 08_experiments/E1_pilot/harness_v2/*.sh; do bash -n "$script"; done
# Reproduce the full recorded validation before collecting a batch:
/usr/bin/python3 -I -B 08_experiments/E1_pilot/harness_v2/static_validate.py
```

Python AST/inline-AST, YAML/config/path checks, secret-absence scan, preserved-fix
checks and source-harness digest verification are recorded in `static_checks.txt:2–39`.
These checks do not establish Docker Compose merge behavior or runtime success.
