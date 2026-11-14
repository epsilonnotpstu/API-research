# T20 paired execution and analysis

These scripts implement the T19 manual plan. T20 did not execute a harness,
Docker, Maven, Java or SUT. Only synthetic saved-run tests and our own Python
analysis tools ran. Claude executes the external run stage within the
supervisor's authorization (`09_collab/tasks/T20.md`, Constraints;
`09_collab/PROTOCOL.md:12–14`).

The harness patch is now applied according to `09_collab/tasks/T20.md`, Current
state. Build-image provenance and the unknown historical scout build image are
recorded in `COORDINATOR_NOTES.md`, Maven build images. The rebuilt pair is the
comparison unit. `build_pair.sh` and live `work/` builds were not edited in T20.

## Commands for Claude

Use the completed directory printed by `build_pair.sh`. Paths may contain spaces;
no script sources data from a manifest or executes values as shell commands.
The scripts locate the repository from their own location.

```bash
E5="$PWD/08_experiments/E5_codemut"
MUT="$E5/work/market-drop-null_20261114T113144Z"
# External execution: control then mutant for each seed; default seeds 1 2 3.
"$E5/run_pair.sh" "$MUT"
# Alternatively select canonical nonnegative seeds explicitly, e.g. 1 3.
# "$E5/run_pair.sh" "$MUT" 1 3
# Own saved-evidence analysis, both oracles, after pair validation:
"$E5/analyse_pair.sh" "$MUT"
# All directories with work/*/runs.tsv; creates/replaces only this top-level CSV.
/usr/bin/python3 -I -B "$E5/summarise_e5.py"
# Or summarise named pairs to a chosen output:
# /usr/bin/python3 -I -B "$E5/summarise_e5.py" "$MUT" --out "$E5/e5_summary.csv"
```

`run_pair.sh` delegates to `e5_pipeline.py`, `run_pair`. It verifies the build
bundle before running, records a frozen `run-plan.json`, and creates `runs.tsv`
with columns `seed,role,run_dir,harness_exit,status` (TSV). Each row starts RUNNING
before process launch and ends COMPLETE, FAILED or INTERRUPTED. Each harness
invocation uses baseline/NONE/0, 300 s, DATA_GEN=all, 100 examples,
SCHEMA_CHECKS=response_headers_conformance, timeout 10000 ms and logger limit
65536. Custom auth/role/base/readiness/pool overrides are cleared; SUT configs
supply the normal auth fixture. Source-tree digest, JAR and code manifest are
passed separately for each role. The launcher selects immutable image IDs from
the build snapshots, avoiding later tag movement (`e5_pipeline.py`, `run_pair`;
`e5_common.py`, `LEDGER_FIELDS`).

The launcher stops after a failed run or failed pair validation. PASS_WITH_EXCLUSION is eligible for analysis. It never silently
resumes or overwrites a launch ledger. Preserve failed attempts and arrange a
fresh pair/launch with the coordinator. SIGINT/SIGTERM are forwarded to the
harness so its cleanup trap can finish; the ledger records the interrupt. No
image build or shared dist staging occurs in these scripts (`e5_pipeline.py`,
`harness_process`, `run_pair`, `main`).

## Pair validation contract

`run_pair.sh` validates after each seed; `analyse_pair.sh` revalidates before
analysis. A standalone validation command is also available:

```bash
/usr/bin/python3 -I -B "$E5/validate_pair.py" "$CONTROL_RUN" "$MUTANT_RUN" "$MUT"
```

It writes `pair-validation-s<seed>.json` with one PASS/FAIL per named check and
exits nonzero for any FAIL. Missing evidence fails; no check silently skips.
Malformed/missing control seed produces `pair-validation-sunknown.json`. Report
replacement is atomic; a new FAIL replaces a prior PASS for the same seed.
Use `--report-staging-dir DIR` on the same filesystem when only the final report
path may be written inside MUT_DIR; the atomic temporary file stays in DIR.
JSON errors and differences are described without dumping container environment
values (`validate_pair.py`, `Checks`, `validate`, `main`; `e5_common.py`, `atomic_json`).

| T19 requirement | Implemented saved-evidence check |
|---|---|
| Complete baseline/NONE/0 pair; same seed and scenario | Completion/exit/coverage/cleanup, expected budget/checks, metadata field equality with a narrow allowlist of run/code differences. JUnit must parse and contain test cases. Identical sets of (testcase name, execution-error text) pass with a recorded note/list. Asymmetry exclusively on known non-mutated operations yields PASS_WITH_EXCLUSION; any mutated or unmappable differing operation fails. Test failures remain for manual review. |
| Unchanged original/test specs, derecursion, auth and generator settings | Rehash all recorded artifacts; compare paired spec/generator/cuts/config/help/argv; enforce DATA_GEN=all from argv; auth fixture hash checked against its current file; runtime auth override rejected. |
| Same frozen tools, harness, EMB config and JaCoCo | Compare dictionaries across the pair and rehash every listed file against the current files; validate staged agent bytes and metadata. |
| Same source except the reviewed edit | Recompute both retained source inventories; verify original manifest inventory, tree digests, exact edited bytes, changed-file set and patch bytes/hash. `target/` remains excluded from source hashing. |
| Same Maven/dependencies and non-JAR runtime inputs | Saved Maven image ID and arguments/logs; compare actual cloned `.m2` JAR/POM inventories to `resolved-artifacts.json`; rehash context checksum inventories, reject extra/missing files, compare all non-SUT-JAR files. |
| Correct built/selected/running code image | Built target JAR equals staged JAR; image labels match role-specific source/JAR digests; copied manifests and code metadata match; built image ID equals collected image ID and actual container `.Image`; actual container config and Compose code override use the immutable ID. |
| Same runtime base and container settings | Both image layer chains have the recorded runtime-base prefix; FROM uses its digest; platform/image runtime config match. Compare SUT/proxy container Config, HostConfig, mounts, entrypoint/args after normalizing Docker hostnames, each own project prefix in network mode and known Compose bookkeeping. SandboxID is excluded; environment entries compare as a multiset (including multiplicity), and Binds compare as a set after normalizing each run directory. Every environment value and bind setting remains strict. No SUT mounts/persistent volumes; separate container IDs/projects and proxy volumes. |
| Reject unexplained differences | Unknown metadata differences, unrecognized image records, image/schema/proxy drift, changed snapshots and changed runtime settings fail. The `compose.code-image` metadata entry is treated specially because the existing metadata glob mistakes the Compose JSON for an image inspection; the Compose JSON itself is checked directly. |

Implementation: `validate_pair.py`, `build_checks`, `generator_argv`,
`normalized_runtime`, `validate`; provenance source:
`08_experiments/E1_pilot/harness_v2/run_metadata.py:20–78` and the capture/launch
blocks in `run_pilot.sh`. The existing spec-mutation `analyse_run.sh` is untouched.

This validates available provenance, not business-state equivalence. The harness
removes the generator container, so its launch settings are evidenced by the
frozen harness and saved argv rather than a generator-container inspection.
A shared saved Maven image snapshot/argv does not independently attest each
past build process. Runtime-base checks concern the rebuilt pair, including the
coordinator's replacement JDK11 base, not the historical baseline image.
Require directed state/witness review before a causal kill. Inspect JUnit test
failures manually even when the structural validation passes (`validate_pair.py`,
report `limitations`; `09_collab/tasks/T20.md`, Current state).

## Analysis outputs and failure handling

For each complete paired seed, `analyse_pair.sh` writes fresh outputs to
`analysis-s<seed>-default/` and `analysis-s<seed>-sut/`. Earlier complete seeds
can be analysed when a later seed failed; failed/unpaired seeds are announced
and skipped. A seed that fails validation stops analysis. Existing analysis
directories, including partial ones, are never overwritten automatically
(`e5_pipeline.py`, `analyse_pair`; `e5_common.py`, `paired_rows`).

Each directory retains unfiltered `control.raw.violations.jsonl` and
`mutant.raw.violations.jsonl`, plus scoped `control.violations.jsonl`, `mutant.violations.jsonl`,
`attribution.csv`, `tools.log`, and `analysis.json`. Conformance uses the original
spec and `--deploy-origin http://$SUT_SERVICE:$INTERNAL_PORT`. Default rejects
400/422; market's SUT variant additionally includes 406. Other SUTs' two oracles
have identical rejection sets. Excluded operations are removed from both roles before attribution.
Attribution always uses `--mode fresh` with the code manifest. `analysis.json` records the oracle, inputs, validation report,
tool/pipeline and output hashes, and COMPLETE/FAIL. Errors retain partial files;
a partial directory is never treated as a successful empty analysis
(`e5_pipeline.py`, `tool`, `analyse_pair`; `08_experiments/tools/attribute.py:1–7,33–57`;
`08_experiments/tools/conformance.py:455–467`).

## Summary meanings

`summarise_e5.py` revalidates each pair, checks the saved validation report and
analysis hash chain, then recomputes fresh attribution from the saved violations
to verify the CSV. One row is written per selected pair × seed × oracle. Seeds
recorded in the launch plan but never attempted are included as error rows.
Missing/failed/stale validation or analysis gives blank metric cells and an
error, with nonzero summary exit. It never turns missing evidence into zero
failures. An empty discovery produces only a header and prints NO_RUNS; that is
not an empirical E5 result. Build-invalid selections without a launch ledger remain
in the coordinator build record (`COORDINATOR_NOTES.md`, Build results); they
are not fabricated run-summary rows (`summarise_e5.py`, `verify_analysis`, `summarise`, `main`).

- `mutated_NEW`, `mutated_VANISHED`: fingerprints appearing/disappearing on the
  manifest's mapped operations. `mutated_INCREASED` / `mutated_DECREASED`: only
  PERSISTENT fingerprints whose occurrence counts rose/fell. NEW/VANISHED are
  not counted again as INCREASED/DECREASED. The four `non_mutated_*` columns use
  the same definitions for operations outside the manifest mapping.
- `expected_signal_observed`: at least one expected kind is NEW or INCREASED on
  a mapped operation. `expected_signal_present_mutant`: the expected kind occurs
  in mutant traffic, including unchanged pre-existing occurrences. The two
  notions are deliberately separate. Multiple expected kinds are alternatives
  (any match), not an assertion that all appeared. Empty expected-signal lists
  are never a positive detection.
- `fresh_L1_NEW_mutated`: counts of labels from fresh `attribute.py`, normally
  NEEDS_MANUAL. `triage_status=NOT_APPLICABLE_P001_CLI` and the triage L1 cell is
  blank because current `tools/triage.py` accepts P001 sheet/directory data, not
  E5 violations (`08_experiments/tools/triage.py:852–864`). No adapter or invented
  IMPL prediction is substituted.
- `causal_kill_status=NEEDS_INDEPENDENT_WITNESS`: a matching signal or an IMPL
  expectation is not causal attribution. Off-operation counts are an observational
  noise estimate; state propagation can also affect those operations. Repeated
  same-seed controls and independent witness/source review remain necessary.

Metric implementation: `summarise_e5.py`, `metrics`; current evidence for the
noise/state distinction: `08_experiments/E1_pilot/pilot_results/PILOT_SUMMARY.md`,
§3b and §5; policy: `08_experiments/R1_triage_codebook.md:98–118,251–259`.

## Synthetic verification

```bash
/usr/bin/python3 -I -B -m unittest discover \
  -s 08_experiments/E5_codemut -p 'test_*.py' -v
bash -n 08_experiments/E5_codemut/run_pair.sh
bash -n 08_experiments/E5_codemut/analyse_pair.sh
```

`test_e5_pipeline.py` creates synthetic build/run directories inside
`09_collab/logs/T20_scratch/` by default, then cleans them. Set `E5_TEST_SCRATCH`
to the current task's allowed scratch directory when needed (T20b uses
`09_collab/logs/T20b_scratch/`). The process boundary is mocked
for launcher failure/interrupt tests; no executable harness fixture is run.
Analysis integration tests execute our existing conformance/attribute tools on
synthetic exchanges only. Test evidence is `09_collab/logs/T20_scratch/tests.txt`.

T20b verification: all 81 E5 tests pass; the specified saved market-drop-null
seed-1 pair passes with the shared POST /register generation error listed.
Evidence: `09_collab/logs/T20b_scratch/tests.txt`, final summary;
`work/market-drop-null_20261114T113144Z/pair-validation-s1.json`, notes/checks.

## T20c exclusion and version rules

`validate_pair.py` maps each asymmetric JUnit error's exact testcase name to a
method/path in the original spec. If any differing operation is mutated, or a
name cannot be mapped, the pair is FAIL. Otherwise the pair is
PASS_WITH_EXCLUSION and `excluded_ops` lists method/path/reason. Identical error
sets still pass with a note. This is an exclusion from the comparison, not a
repair of the spec or generator (`validate_pair.py`, `paired_junit`).

`e5_pipeline.py` accepts both pass statuses, preserves raw violations, filters
both roles identically, and records `validation_status`/`excluded_ops` in
`analysis.json`. `summarise_e5.py` validates that scope against the pair report,
checks raw-to-scoped filtering, and excludes the same operations from every
metric and signal count. The CSV includes `excluded_ops` and `validation_status`.

Previously completed analyses outside T20c's writable pairs remain unchanged.
Old PASS reports without `excluded_ops` are compatible only with an empty current
exclusion list and otherwise identical current validation. The summary keeps
the saved pipeline hashes; differences in the four reviewed E5 policy modules
are accepted only while all tool/harness and other pipeline hashes remain
strict and attribution is recomputed from the hashed saved violations. Such
rows carry `pipeline_snapshot_status=PRIOR_E5_PIPELINE_RECOMPUTED`; current
analyses carry CURRENT. This avoids rewriting prior evidence or claiming that
its recorded code version equals the new one (`summarise_e5.py`,
`verify_analysis`, `summarise`).
