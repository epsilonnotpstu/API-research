# T12 — Run the scout-api pilot batch end-to-end and report (autonomous; Claude may be offline)
Read first: `../PROTOCOL.md` (rule 6a), `../../08_experiments/E1_pilot/harness/README.md`, `../reports/T5_report.md`, `../reports/T10_report.md`, `../../08_experiments/R1_triage_codebook.md` §5/§9.

## Authorization (supervisor launches this task personally, 2026-11-13)
You MAY execute exactly these, nothing else external:
- `08_experiments/E1_pilot/harness/run_pilot.sh`, `analyse_run.sh`, `prepare_dist.sh`.
- Read-only diagnostics on runs you started: `docker ps`, `docker inspect`, `docker logs`, `docker compose ... ps/logs/down`.

Never `docker system prune`, never delete images/volumes you did not create, never sudo, never install packages, never touch unrelated containers (e.g. `sql-practice`, `dc20-db`).

## Steps
0. **Wait** until both are true:
   - (a) No pilot is running: `flock -n 08_experiments/E1_pilot/harness/.run.lock true` succeeds.
   - (b) The T11 row on `COLLAB_BOARD.md` is DONE.

   Poll every 60 s. Give up after 3 h and report.
1. **Smoke test:** inspect the latest run under `08_experiments/E1_pilot/runs/scout-api/`. Claude started it before T11 finished, so its `tool_sha256` will differ from the batch; use it only to detect harness problems.
   - Check: run.json phase, Schemathesis exit code, exchanges.jsonl line count, jacoco.exec size, errors in compose.log.
   - Note: Claude already fixed one harness bug — the mitmproxy entrypoint `usermod` failure (`compose.override.scout-api.yaml`, entrypoint → mitmdump).
   - If the harness has another bug, make a **minimal fix to harness scripts only** (`08_experiments/E1_pilot/harness/`), document it, and re-run the smoke test.
   - **Never edit `08_experiments/tools/` during the batch** — tool hashes are checked by `analyse_run.sh`.
1b. **Known issues from Claude's smoke run #2** (`runs/scout-api/20261113T154523Z_baseline_NONE_p0_s1_1450656`; proxy, logging and JaCoCo work; exit 124):
   - **Auth:** all write operations return 401 ("Credentials are required"); the spec has no securityDefinitions. EMB provides benchmark test credentials in `08_experiments/_external/emb/auth/scout-api-auth.yaml` (roles user / moderator / administrator; fixed `Authorization` headers seeded by `init_db.sql`).
     - Add an `AUTH_HEADER` option to `run_pilot.sh`, passed to Schemathesis as `-H`. Default it to the **administrator** role read from that YAML at run time.
     - Never print the header value in reports or logs. Record only the role name in run.json.
   - **Stall:** after GET `/v2/activities/{id}` (100 examples), Schemathesis sent 5 PUTs and then no requests for the rest of the 600 s budget. Only 2/49 operations were reached.
     - Using the pinned image's captured `schemathesis-help.txt`, add a request timeout and disable shrinking (e.g. `--request-timeout`, `--hypothesis-phases=explicit,generate`). Verify that each flag exists in 3.39.16.
     - If it still stalls, reduce `MAX_EXAMPLES` (e.g. 25) for all conditions equally.
     - **Goal:** all 49 operations reached within budget. Report operations reached per run.
   - Treat these as harness fixes (allowed path). Re-run the smoke test until it completes with exit 0/1 and reaches most operations, before starting the batch.

2. **Batch**, exactly as in the harness README:
   - Settings: `MAX_EXAMPLES=100 HEALTH_PATH=/admin/healthcheck BASE_PATH=/api`.
   - Baselines: seeds 1, 2, 3 (600 s each).
   - Mutated runs: `REQUEST_LOOSE REQUEST_STRICT RESPONSE_ORACLE METHOD_SEM` at severity 30, seed 1 (600 s each). Follow each with `analyse_run.sh MUTATED BASELINE_s1 --mode both`.
   - If a run fails, record it and continue with the rest. Retry a failed run at most once.
3. **Analysis** (our own Python, `/usr/bin/python3 -I -B`).
   - Per run:
     - Exchanges and unique operations hit.
     - Status-code distribution.
     - Violations by kind, under both default and strict policies (`conformance.py`).
     - JaCoCo line coverage, if computable with `jacococli.jar report` (needs class files extracted from the SUT jar; otherwise skip with a note).
   - Baseline seed variability: violations present in all 3 seeds vs. seed-specific → nondeterminism estimate.
   - Per fault class:
     - Replay mode: NEW/VANISHED, and whether labels match the manifest's expected label.
     - Fresh mode: NEW/VANISHED, split into explained (on a mutated op) vs unexplained.
   - Write tables as CSV under `08_experiments/E1_pilot/pilot_results/`.
4. **Report** `09_collab/reports/T12_report.md` (Bengali):
   - What ran: run ids, durations, exit codes.
   - Harness fixes.
   - Results tables.
   - Threats: single SUT, short budget, seed effects.
   - Concrete recommendations for the next batch: budget, SUTs, seeds.

   Update your board row and the Log after each major step, so the supervisor can follow progress.

## Allowed write paths
- `08_experiments/E1_pilot/runs/`
- `08_experiments/E1_pilot/pilot_results/`
- `08_experiments/E1_pilot/harness/` (minimal fixes only)
- `08_experiments/_external/emb/dist/` (via prepare_dist.sh)
- `09_collab/reports/T12_report.md`
- `09_collab/logs/T12_scratch/`
- Your board row + Log
