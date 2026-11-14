# T12 scout-api pilot results

This directory is produced by the local analysis script
`09_collab/logs/T12_scratch/summarize.py` (re-run with `/usr/bin/python3 -I -B`).
The final Bengali interpretation is `09_collab/reports/T12_report.md`.
During batch execution the tables contain only runs that have already finished;
`summary.json:run_ids` identifies their scope.

## Tables and units

- `runs.csv`: one row per T12 batch run. `wall_seconds` is subprocess elapsed time
  measured with `time.monotonic`; `utc_span_seconds` is the difference between
  saved UTC start/finish timestamps. Neither is the per-operation test duration.
  The fixed 600-second budget applies to generation (harness README).
  `unique_operations_hit_original` counts distinct documented method/template
  pairs under the original spec; it excludes undocumented probe paths and methods.
  The historical smoke run is excluded (T12 task step 1).
- `status_codes.csv`: counts captured response exchanges, not attempted requests.
- `operations.csv`: distinct method/template pairs normalized with the original
  checker, with undocumented pairs explicitly flagged.
- `violations_by_kind.csv`: default and strict local conformance results, with
  occurrence, unique fingerprint, affected-exchange, and generator-probe counts.
  `ALL` is a summary row and must not be added to the kind-specific rows.
  `exchanges_affected` is deduplicated within its row.
- `strict_only.csv`: extra occurrences under strict policy. Additional-property
  policy findings use TEST/T-ORACLE-STRICT, not SPEC (codebook §9.2).
- `schemathesis_findings.csv`: parsed JUnit failure/error/skipped entries. These
  are generator checker results and can differ from the local conformance tool.
- `baseline_variability*.csv`: presence of each violation fingerprint across
  baseline seeds, including the generator probe if emitted by conformance.
  `variable_fraction = (union - all_three) / union`. This is an observed
  seed/run-variability proxy on captured traffic; it does not estimate pure
  nondeterminism independently of seeds, coverage and budget truncation.
- `fault_comparison.csv`: default/strict × replay/fresh × NEW/VANISHED/PERSISTENT
  unique identity counts for each fault. `on_mutated_op_explained_locality` means
  operation locality only; fresh causal labels remain NEEDS_MANUAL. PERSISTENT
  outside-mutated-op counts are unchanged findings, not unexplained changes.
- `attribution_details.csv`: the underlying rows. Replay uses exactly the same
  baseline records for both oracles. NEW replay labels are copied from the
  manifest; matching them is a consistency check, not independent classifier
  accuracy. VANISHED replay labels are MASKED, so expected-label match is NA.
- `mutation_exposure.csv`: captured responses on each mutated original/new method
  for baseline seed 1 and fresh mutated traffic; zero responses means unexposed.
  Requested severity is operation selection, whereas the manifest records actual
  operations changed after no-op mutations are discarded (`tools/specmut.py:230`).
- `coverage.csv`: JaCoCo dump sizes and exits; line coverage is omitted because
  standalone jar extraction/java report is outside T12's exact external execution
  authorization (`09_collab/tasks/T12.md:4-12`).
- `artifact_integrity.csv`: checks of saved exchange/spec/manifest hashes.
- `*.violations.jsonl`: local conformance occurrences with source exchange indexes.
  Source exchange index is zero-based. No HTTP requests are sent by this analysis.

## Partial-run handling and provenance

`complete=False` remains unchanged in each source `run.json`. The reviewed
`analyse_run.sh` refuses incomplete run pairs (`harness/analyse_run.sh:14-15`).
Its invocation and exit are recorded in
`09_collab/logs/T12_scratch/batch_events.jsonl`; any separate local comparison
here with `pair_complete=False` is a partial audit, never an accepted complete
harness analysis. Interpret differences under that limitation.

The pre-batch tool hashes are in
`09_collab/logs/T12_scratch/batch_tool_sha256.json`. The wrapper checks them before
and after each run. Final raw-artifact/table reconciliation is recorded in
`09_collab/logs/T12_scratch/verification.json` after all seven runs.

The logger has a response hook but no transport-error hook
(`08_experiments/tools/mitm_fulllog.py:39`); zero transport records does not prove
zero failed attempts. Generator probes are identified by the captured
`x-schemathesis-probe` header. No tool or harness changes are made by the analysis.
