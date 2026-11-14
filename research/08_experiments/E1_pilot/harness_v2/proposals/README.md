# T27 proposal

## Second fuzzer

The harness proposal is ready for review; the full T27 goal is **BLOCKED on the existing E5 wrapper/validator contract**. The patch has not been applied to the live harness. The seven patched files pass offline validation in a temporary copy; the 22 original harness files retain their initial hashes. Evidence: `09_collab/logs/T27_scratch/validation.json:2–73`, `patch-apply.txt:1–7` and `static-tests.txt:41–75`.

### Apply and inspect

`harness.evomaster.proposed.diff` uses paths relative to `08_experiments/` and is a unified patch for `patch -p1`. `harness.evomaster.base-sha256.json` maps the three modified existing paths to their required SHA-256 values. Four additional files are new. Evidence: `09_collab/logs/T27_scratch/build_and_validate.py:24–53` and `validation.json:3–11`.

Coordinator commands, from `08_experiments/`, after the active-run gate described in `09_collab/tasks/T27.md`:

```bash
/usr/bin/python3 -I -B - <<'PY'
import hashlib, json, pathlib
base = pathlib.Path('E1_pilot/harness_v2/proposals')
for name, expected in json.loads((base / 'harness.evomaster.base-sha256.json').read_text()).items():
    assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest() == expected, name
print('Base hashes match')
PY
patch --dry-run --batch --fuzz=0 -p1 -i E1_pilot/harness_v2/proposals/harness.evomaster.proposed.diff
patch --batch --fuzz=0 -p1 -i E1_pilot/harness_v2/proposals/harness.evomaster.proposed.diff
/usr/bin/python3 -I -B E1_pilot/harness_v2/static_validate.py
```

Future run examples, after applying the patch:

```bash
env -u DATA_GEN FUZZER=evomaster E1_pilot/harness_v2/run_pilot.sh scout-api \
    _external/emb/openapi-swagger/scout-api.json baseline NONE 0 1 300
env -u DATA_GEN FUZZER=evomaster BUDGET_SECONDS=300 \
    E1_pilot/harness_v2/run_batch.sh scout-api 1 2 3
```

These commands are documentation; this task executed neither the live harness nor a fuzzer. Evidence: `09_collab/logs/T27_scratch/build_and_validate.py:55–77` and `static-tests.txt:75`.

### Selection, routing and outputs

`FUZZER` unset, empty, or `schemathesis` selects the existing path. Its golden fixture captures six cases from the original shell statements, including auth and `DATA_GEN`; seven source fragments pin Docker argv, image/help preflight, readiness, cleanup/coverage, mutation pools, de-recursion, and exit classification. Evidence: `09_collab/logs/T27_scratch/make_golden.py:16–63`, staged `test_fuzzer_args.py:58–128`, and `static-tests.txt:45–53`. The new `fuzzer` provenance field and changed harness hashes are intentional additions; runtime equality has not been experimentally measured.

`FUZZER=evomaster` selects the local immutable image `webfuzzing/evomaster@sha256:de1f4387e809a309a4c61517f3340c3d0b733b78bbb86d0e3ebd217d343515ab`, recording the task-supplied version `6.2.0`. The EvoMaster branch only inspects this local image; it does not pull it or invoke help. Evidence: `09_collab/tasks/T27.md:12–15`, staged `run_pilot.sh:34–40,186–190`.

The container joins `${project}_default` and receives `--base http://mitmproxy:8080`. The API path comes from the schema because EvoMaster explicitly requires an origin-only `--base`; the schema guard checks agreement with `BASE_PATH`. It rejects divergent paths, server variables, and path/operation server overrides. All four checked-in specs pass this guard. The run's unchanged `spec.test.json` is mounted over the writable run-directory mount as `/work/spec.test.json:ro`, and that exact path is passed as `--schema`. Evidence: saved help `09_collab/logs/T27_scratch/evomaster_help.txt:177–190,1531–1540`, staged `evomaster_guard.py:19–53`, `fuzzer_args.sh:16–22`, `run_pilot.sh:282–285`, and `static-tests.txt:54–61`. ⚠️ These are source/static checks; Docker mount behavior, absolute-server authority replacement, and captured traffic still require an authorized smoke run.

The argv explicitly requests black-box REST, `SEED`, TIME stopping, `--maxTime ${budget}s`, Java JUnit 5 source under `evomaster/tests/`, and CSV statistics at `evomaster/statistics.csv`. Generated tests are artifacts, not executed tests. `REQUEST_TIMEOUT_MS` maps to `--tcpTimeoutMs`; rate limiting is disabled and schema oracles are enabled. The watchdog allows `budget + 120` seconds, with the existing 20-second kill grace. Evidence: staged `fuzzer_args.sh:16–22` and `run_pilot.sh:279–286`.

Auth uses the existing fixture/runtime override resolution, then `--header0` for EvoMaster. Only `<redacted>` is written to `evomaster-argv.txt`; the existing streaming/final recursive redactor also covers logs, generated source and statistics. `run.json` records `fuzzer`, `evomaster_image`, `evomaster_version`, `evomaster_exit`, redacted `evomaster_argv`, its file name, the watchdog budget, and nested output hashes. Evidence: staged `run_pilot.sh:49–70,275,285`, `fuzzer_args.sh:25–31`, `run_metadata.py:78–96`, `test_fuzzer_args.py:205–283`, and `static-tests.txt:65–68`.

Exit `0` or `1` requires nonempty CSV statistics and generated Java source before collection can complete. This retains the current treatment of exit `1` as a possible test-failure result, while missing outputs fail the harness. Exit `124`/`137` remains incomplete; other exits propagate. Coverage, cleanup, redaction and nonempty exchange checks still gate final completion. Evidence: staged `run_pilot.sh:111–140,294–312` and `evomaster_guard.py:56–63`; original exit policy: `08_experiments/E1_pilot/harness_v2/run_pilot.sh:278–284`.

### Options and analysis compatibility

- A nonempty `DATA_GEN` is rejected before any Docker command or run-directory creation for EvoMaster. `positive`, `negative`, and `all` are Schemathesis modes with no asserted EvoMaster equivalent in this proposal. Evidence: staged `run_pilot.sh:19–29`, `evomaster_guard.py:8–16`, and `static-tests.txt:63`.
- `ONLY_OPS` keeps its existing role as the spec-mutation candidate pool; it never limits fuzzer traffic. EvoMaster rejects it in baseline mode. Evidence: staged `evomaster_guard.py:11–12`, `run_pilot.sh:167–175`, and `static-tests.txt:56,62`.
- `MAX_EXAMPLES`, `SCHEMA_CHECKS`, and Hypothesis phases remain legacy provenance settings for comparisons; they do not control EvoMaster. The explicit EvoMaster flags above control that fuzzer. Evidence: staged `fuzzer_args.sh:4–22` and `run_metadata.py:38,46–48`.
- `analyse_run.sh` is unchanged. Its existing `schema-image.json` and `schemathesis_image` keys identify the selected generator image, retaining these names as compatibility aliases. `generator-input.json` is a byte copy of `spec.test.json` for EvoMaster; it is not de-recursed. `schemathesis_exit` is truthfully `not_started`, with the actual exit in `evomaster_exit`. Existing artifact/tool/harness hash checks remain intact. Evidence: original `analyse_run.sh:22–56`; staged `run_pilot.sh:189–190,270–275`, `run_metadata.py:39,78–96`, and `validation.json:48`.

⚠️ The unchanged analysis input contract is supported by source inspection and metadata tests, not an end-to-end EvoMaster collection/replay. An authorized future smoke run must inspect `exchanges.jsonl`, the proxy origin/base path, output files, coverage, redaction and final `run.json` before interpreting results. Evidence: `09_collab/tasks/T27.md` execution constraints and `static-tests.txt:75`.

### E5 blocker

`run_pair.sh` delegates to `e5_pipeline.py`; that wrapper unconditionally injects `DATA_GEN=all` into the harness environment. Therefore `FUZZER=evomaster` through the current E5 wrapper fails the required unsupported-option check before collection. Even removing that environment setting would not suffice: the E5 validator requires Schemathesis argv, help, de-recursion/JUnit artifacts, Schemathesis exit status and exact Schemathesis flags. Evidence: `08_experiments/E5_codemut/run_pair.sh:6–7`, `e5_pipeline.py:94–106`, and `validate_pair.py:146–161,241–255,351`.

T27 forbids changes to `E5_codemut/`. No E5 implementation or fake Schemathesis artifacts are included in this proposal. The coordinator needs a separately scoped E5 adapter task covering environment selection, genuine EvoMaster completion evidence, paired metadata comparison and generator-specific validation. The full T27 goal remains blocked until that contract is resolved. Evidence: `09_collab/tasks/T27.md` Goal/Constraints and `09_collab/PROTOCOL.md:7,15`.

### Offline validation

`09_collab/logs/T27_scratch/build_and_validate.py` copies the harness under `/tmp`, applies the patch with `patch -p1 --fuzz=0`, compares every patched file with the staged source, runs `static_validate.py`, checks all six shell files with `bash -n`, and verifies the 22 original live files against the initial snapshot. External EMB files and the original v1 harness are read through symlinks solely for existing static checks. Results: 13 existing de-recursion tests plus 24 new tests pass; all six shell checks pass. Evidence: `build_and_validate.py:55–88`, `validation.json`, `patch-apply.txt`, and `static-tests.txt:41–75`.
