"""Render the Bengali T12 report from final verified CSV evidence."""
import collections
import csv
import json
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / '08_experiments/E1_pilot/pilot_results'
SCRATCH = ROOT / '09_collab/logs/T12_scratch'


def read(name):
    with (OUT / name).open() as handle:
        return list(csv.DictReader(handle))


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '|' + '|'.join('---' for _ in headers) + '|'] + ['| ' + ' | '.join(str(c) for c in row) + ' |' for row in rows])


runs = read('runs.csv')
assert len(runs) == 7
verification = json.loads((SCRATCH / 'verification.json').read_text())
assert verification['result'] == 'PASS'
alias = {r['run_id']: ('B' + r['seed'] if r['mode'] == 'baseline' else {'REQUEST_LOOSE': 'M1', 'REQUEST_STRICT': 'M2', 'RESPONSE_ORACLE': 'M3', 'METHOD_SEM': 'M4'}[r['fault']]) for r in runs}
lookup = {r['run_id']: r for r in runs}
status = read('status_codes.csv'); kinds = read('violations_by_kind.csv'); comparisons = read('fault_comparison.csv')
exposure = read('mutation_exposure.csv'); variability = read('baseline_variability_summary.csv')
complete = sum(r['complete'] == 'True' for r in runs)
exchanges = sum(int(r['exchanges']) for r in runs)
probes = sum(int(r['schemathesis_probe_records']) for r in runs)
strict_extra = sum(int(r['occurrences']) for r in read('strict_only.csv'))
run_rows = []
for r in runs:
    junit = 'unavailable' if r['junit_errors'] == 'unparseable' else '/'.join(r[k] for k in ('junit_tests', 'junit_failures', 'junit_errors'))
    run_rows.append([alias[r['run_id']], r['fault'] if r['mode'] == 'mutated' else 'baseline s' + r['seed'], f"{float(r['wall_seconds']):.1f}/{float(r['utc_span_seconds']):.1f}", r['harness_exit'] + '/' + r['schemathesis_exit'], r['exchanges'], r['unique_operations_hit_original'] + '/' + r['original_operations_total'], junit, r['jacoco_bytes']])
run_table = table(['ID', 'Condition', 'Elapsed/UTC seconds', 'Harness/ST exit', 'Exchanges', 'Ops hit', 'JUnit tests/fail/errors', 'JaCoCo bytes'], run_rows)
id_table = table(['ID', 'Run ID'], [[alias[r['run_id']], '`' + r['run_id'] + '`'] for r in runs])
status_keys = sorted({r['status'] for r in status}, key=int)
status_table = table(['ID'] + status_keys, [[alias[r['run_id']]] + [next((x['exchanges'] for x in status if x['run_id'] == r['run_id'] and x['status'] == key), '0') for key in status_keys] for r in runs])
violation_rows = []
for r in runs:
    row = [alias[r['run_id']]]
    for policy in ('default', 'strict'):
        relevant = [x for x in kinds if x['run_id'] == r['run_id'] and x['policy'] == policy]
        total = next(x for x in relevant if x['kind'] == 'ALL')
        row.extend([total['occurrences'] + ' (' + total['unique_fingerprints'] + ')', '; '.join(x['kind'] + '=' + x['occurrences'] for x in relevant if x['kind'] != 'ALL') or '0'])
    violation_rows.append(row)
violation_table = table(['ID', 'Default occ (unique)', 'Default kinds', 'Strict occ (unique)', 'Strict kinds'], violation_rows)
comparison_rows = []
for r in runs:
    if r['mode'] != 'mutated':
        continue
    for policy in ('default', 'strict'):
        group = [x for x in comparisons if x['run_id'] == r['run_id'] and x['policy'] == policy]
        find = lambda mode, status: next(x for x in group if x['mode'] == mode and x['status'] == status)
        rn, rv, fn, fv = (find(m, s) for m, s in (('replay', 'NEW'), ('replay', 'VANISHED'), ('fresh', 'NEW'), ('fresh', 'VANISHED')))
        expected = rn['expected_label_matches_new_replay'] + '/' + rn['expected_label_tested_new_replay'] if int(rn['expected_label_tested_new_replay']) else 'NA (0 tested)'
        comparison_rows.append([alias[r['run_id']], policy, rn['operations_mutated'], rn['unique_fingerprints'] + '/' + rv['unique_fingerprints'], expected, fn['on_mutated_op_explained_locality'] + '/' + fn['outside_mutated_op_unexplained'], fv['on_mutated_op_explained_locality'] + '/' + fv['outside_mutated_op_unexplained']])
comparison_table = table(['ID', 'Policy', 'Changed ops', 'Replay NEW/VANISHED', 'NEW expected match', 'Fresh NEW on/off op', 'Fresh VANISHED on/off op'], comparison_rows)
exposure_rows = []
for r in runs:
    if r['mode'] != 'mutated':
        continue
    group = [x for x in exposure if x['run_id'] == r['run_id']]
    row = [alias[r['run_id']]]
    for cohort in ('baseline_s1', 'fresh_mutated'):
        selected = [x for x in group if x['cohort'] == cohort]
        row.append(str(sum(int(x['captured_responses']) > 0 for x in selected)) + ' / ' + str(sum(int(x['captured_responses']) for x in selected)))
    exposure_rows.append(row)
exposure_table = table(['ID', 'Baseline exposed method-ops / responses', 'Fresh exposed method-ops / responses'], exposure_rows)
variability_table = table(['Policy', 'Union', 'All 3', 'Seed-specific', '2 seeds', 'Variable fraction'], [[r['policy'], r['union'], r['all_three'], r['seed_specific'], r['two_seeds'], r['variable_fraction']] for r in variability])
report = f'''# T12 — scout-api pilot batch execution ও partial audit

**কাজ সম্পন্ন: নির্ধারিত সাতটি condition চেষ্টা করা হয়েছে; complete run {complete}/7।** মোট {exchanges} captured response exchange, যার {probes}টি Schemathesis probe। Raw run metadata অপরিবর্তিত আছে; incomplete pair-এর জন্য reviewed harness analysis প্রত্যাখ্যানের ফলও সংরক্ষিত। CSV-গুলোর raw-artifact reconciliation PASS (`08_experiments/E1_pilot/pilot_results/runs.csv`, সাত run row; `09_collab/logs/T12_scratch/batch_events.jsonl`, stage=run/analysis; `09_collab/logs/T12_scratch/verification.json`, result)।

## অনুমতি, gate ও smoke

Supervisor-এর সরাসরি launch অনুযায়ী protocol 6a অনুসরণ করে external execution কেবল `prepare_dist.sh`, `run_pilot.sh`, `analyse_run.sh`-এ সীমিত ছিল। Package install, standalone Docker/SUT/tool execution, sudo বা prune করা হয়নি; tools directory-তে লেখা হয়নি। Wrapper-এর external command list ও tool freeze checks: `09_collab/logs/T12_scratch/batch.py:1`; অনুমতি: `09_collab/tasks/T12.md:4-12`।

প্রতি 60 seconds-এ poll করে **480.02 seconds** অপেক্ষার পর T11 DONE এবং free pilot lock দুটোই পাওয়া যায় (`09_collab/logs/T12_scratch/gate.jsonl`, elapsed_seconds=480.02)। Latest pre-batch smoke `20261113T154523Z_baseline_NONE_p0_s1_1450656`: phase=collection, ST/harness exit124, 106 exchanges, JaCoCo 311978 bytes, dump ও cleanup exit0। Log-এ startup connection-refused এবং SUT class-scanning exceptions আছে; পরের health success ও traffic-ও আছে। অতিরিক্ত harness fix-এর evidence পাওয়া যায়নি (`09_collab/logs/T12_scratch/smoke_inspection.json`; smoke run-এর `compose.log`, `health-response.txt`, `schemathesis.log`)।

**T12 harness fix: শূন্য।** পূর্বে Claude-এর করা `entrypoint: ["mitmdump"]` fix বিদ্যমান ছিল (`08_experiments/E1_pilot/harness/compose.override.scout-api.yaml:12`; `09_collab/tasks/T12.md:26`)। Task-এর অনুমানের বিপরীতে smoke-এর final `tool_sha256` batch-এর সঙ্গে মিলে গেছে; helper finalization-এ hashes আবার গণনা করে। ⚠️ সেই match pre-T11 start snapshot প্রতিষ্ঠা করে না। Task অনুযায়ী smoke statistical batch থেকে বাদ রাখা হয়েছে (`smoke_inspection.json`, final_metadata_tool_hash_differences_from_batch/provenance_note; `08_experiments/E1_pilot/harness/run_metadata.py:49`; `pilot_results/runs.csv`, run_id column)। এখানে সংক্ষিপ্ত scratch/result filenames-এর পূর্ণ prefix যথাক্রমে `09_collab/logs/T12_scratch/` ও `08_experiments/E1_pilot/`।

## কী চলেছে

সব condition-এ `MAX_EXAMPLES=100 HEALTH_PATH=/admin/healthcheck BASE_PATH=/api`; generation budget **600 seconds**, auth=`none (pilot assumption)`। Baseline seeds 1/2/3, চার mutation class-এ requested severity30 ও seed1। Tool/harness/SUT/image provenance সাত run-এ স্থিতিশীল থাকার check PASS (`pilot_results/runs.csv`, budget_seconds; প্রতিটি run-এর `run.json`, max_examples/health_path/base_path/auth; `logs/T12_scratch/verification.json`, settings_match_T12/tool_and_harness_hashes_stable/images_stable)। এই paragraph থেকে `pilot_results/`-এর prefix `08_experiments/E1_pilot/`; `logs/T12_scratch/`-এর prefix `09_collab/`।

{id_table}

{run_table}

উপরের সব row-এর source `pilot_results/runs.csv`, key=run_id। `Elapsed` wrapper-এর `time.monotonic()` duration; UTC span saved start/finish timestamps-এর পার্থক্য। Startup, pull/build ও collection generation budget-এর বাইরে। B3-তে দুই duration-এ প্রায় 68.6-second পার্থক্য আছে; কারণ প্রতিষ্ঠিত নয় (`runs.csv`, B3; `logs/T12_scratch/batch.py:46`; `harness/README.md:88-96`)। JUnit-এর counts কেবল flushed completed cases; unavailable হলে XML parse করা যায়নি, error count শূন্য ধরে নেওয়া হয়নি (`runs.csv`, junit_*; সংশ্লিষ্ট `schemathesis.junit.xml`)।

Timeout-গুলোকে পুনরায় একই settings-এ retry করা হয়নি; task-এর সর্বোচ্চ এক retry সীমার মধ্যে শূন্য retry হয়েছে। প্রতিটি failure record করে পরের condition চালানো হয়েছে; সব সাত planned run-এর evidence `batch_events.jsonl`, stage=run। প্রতিটি mutated run-এর পর `analyse_run.sh --mode both` চালানো হয়েছে; সব incomplete pair-এর rejection লগ রয়ে গেছে (`logs/T12_scratch/analyse_*.log`; `batch_events.jsonl`, stage=analysis)। Complete flag বা gate শিথিল করা হয়নি (`harness/analyse_run.sh:14-15`; প্রতিটি run-এর `run.json`)।

## Exchanges, status ও conformance

{status_table}

Status table source: `pilot_results/status_codes.csv`, key=(run_id,status)। Operation coverage ও frequency: `pilot_results/operations.csv`, key=(run_id,method,template)। Actual paths-এ `/api` একবার আছে; 49টি original operation-এর denominator source spec থেকে গণনা করা হয়েছে (`operations.csv`; `runs.csv`, original_operations_total; `logs/T12_scratch/summarize.py:1`)।

{violation_table}

Violation table source: `pilot_results/violations_by_kind.csv`, key=(run_id,policy,kind); full evidence `pilot_results/*.violations.jsonl`, exchange index zero-based। `ALL` summary-তে unique fingerprint ও occurrences আলাদা; kind rows-এর সঙ্গে ALL যোগ করা হয় না (`pilot_results/README.md`, Tables and units)। প্রতিটি run-এর এক `/api` undocumented-operation occurrence generator-এর null-header probe; captured `x-schemathesis-probe= NULL_BYTE_IN_HEADER` দিয়ে এটি পৃথক করা হয়েছে (`runs.csv`, schemathesis_probe_records; B1 `exchanges.jsonl`, row1; `violations_by_kind.csv`, probe_occurrences)।

Strict-only extra violation occurrence **{strict_extra}**; policy differences আলাদা `pilot_results/strict_only.csv`-তে আছে; additional-property strict-only finding হলে codebook অনুযায়ী TEST/T-ORACLE-STRICT প্রযোজ্য, SPEC নয় (`08_experiments/R1_triage_codebook.md:177-183`)। এই batch-এর schema-policy সীমা ও raw counts একই CSV-তে audit করা যায়।

**Checker পার্থক্য:** B2-তে JUnit দুই assertion failure দেয়: PUT-এ undocumented Content-Type ও 401 status; DELETE-এ undocumented Content-Type। Local checker ওই PUT status flag করে, কিন্তু description-only response-এ Content-Type check করে না (`pilot_results/schemathesis_findings.csv`, B2 PUT/DELETE rows; `violations_by_kind.csv`, B2; `08_experiments/tools/conformance.py:208-216`)। GET-এর description-only default response-এ response schema নেই; তাই তার traffic থেকে response-schema coverage প্রতিষ্ঠিত হয় না (`08_experiments/_external/emb/openapi-swagger/scout-api.json`, /paths/~1v2~1activities~1{{id}}/get/responses/default; `conformance.py:201-215`)।

## Baseline seed variability

{variability_table}

Source: `pilot_results/baseline_variability_summary.csv`, policy rows; প্রতিটি fingerprint-এর seed membership `baseline_variability.csv`। `variable_fraction=(union-all_three)/union`। দুই shared identity হলো probe GET `/api`-এর undocumented operation এবং PUT `/v2/activities/{{id}}`-এর undocumented401 (`baseline_variability.csv`, fingerprint column)। Exchange frequencies ও operation coverage তবু আলাদা (`runs.csv`, B1/B2/B3; `status_codes.csv`)। ⚠️ Zero observed identity variation অল্প, incomplete traffic-এর conditional estimate; seed-independent nondeterminism বা deterministic testing প্রমাণ করে না।

## Fault class: replay ও fresh partial audit

নিচের সব pair incomplete; এগুলো reviewed harness-এর accepted complete analysis নয়। Local Python audit-এ replay-এর উভয় oracle ঠিক একই baseline-s1 records পেয়েছে; fresh-এ respective run traffic ব্যবহার হয়েছে (`pilot_results/fault_comparison.csv`, pair_complete; `logs/T12_scratch/summarize.py:1`)।

{comparison_table}

Source: `pilot_results/fault_comparison.csv`, key=(run_id,policy,mode,status)। `on/off op` মানে mutated operation-এ/বাইরে থাকা difference। Fresh on-op অংশ task-এর locality অর্থে explained; label NEEDS_MANUAL থাকে। Off-op changed finding UNEXPLAINED; causal label নয় (`pilot_results/attribution_details.csv`; `08_experiments/tools/attribute.py:21-57`)।

Replay NEW expected-label match কেবল manifest-consistency check: label সরাসরি manifest থেকে বসানো হয়। 0 tested হলে NA; VANISHED-এর label MASKED, তাই expected SPEC label-এর সঙ্গে equality test প্রযোজ্য নয়। Independent classifier accuracy দাবি করা হয়নি (`attribute.py:37-49`; `attribution_details.csv`, expected_label_match_new_only)। Requested30% selection-এর পর no-op বাদ দেওয়ায় actual changed-op count আলাদা হতে পারে (`specmut.py:230-260`; প্রতিটি `manifest.json`, operations_mutated/operations_total)।

{exposure_table}

Exposure source: `pilot_results/mutation_exposure.csv`, key=(run_id,cohort,method,template)। METHOD_SEM-এ original/new method দুটো থাকায় exposed method-op count distinct injected-fault count নয়। M1-এর fresh VANISHED হলো PUT401; fresh mutated traffic ওই PUT-এ response পায়নি, আর একই baseline replay-তে সেটি vanish হয়নি (`fault_comparison.csv`, M1; `mutation_exposure.csv`, M1 PUT row; `attribution_details.csv`, M1 fresh VANISHED)। ⚠️ এই observation দিয়ে causal masking প্রতিষ্ঠিত হয় না।

## JaCoCo, verification ও সীমাবদ্ধতা

JaCoCo dump size উপরের run table ও `pilot_results/coverage.csv`-তে; dump exit source প্রতিটি `jacoco-dump.log`/`run.json`। Line coverage skip করা হয়েছে: reviewed scripts dump সমর্থন করে, কিন্তু standalone jar extraction/`java ... report` task-এর exact external-execution allowlist-এ নেই। Byte size-কে coverage score বলা হয়নি (`09_collab/tasks/T12.md:4-12,39-44`; `harness/run_pilot.sh:58-66`; `coverage.csv`, reason)।

Final verification PASS: সাত condition, 48 comparison groups, raw exchange/status/operation/violation totals, attribution locality/labels, saved artifact SHA-256, stable tools/harness/images/settings cross-check করা হয়েছে (`09_collab/logs/T12_scratch/verification.json`; runner `verify_results.py:1`)। Reproduction: `/usr/bin/python3 -I -B 09_collab/logs/T12_scratch/summarize.py`, তারপর একই interpreter-এ `verify_results.py`; external requests ছাড়া local artifacts পড়ে (`summarize.py:1`; `verify_results.py:1`)।

- **Single SUT ও ছোট budget:** scout-api-র partial captures; operation hit ও incomplete flags run table-এ আছে। ⚠️ অন্য SUT, full API বা detection-rate population-এ ফল generalize করা যায় না (`runs.csv`, sut-equivalent run paths/complete; `operations.csv`)।
- **Seed ও timing:** seeds বদলালে observed counts/coverage বদলেছে; request-free intervals আছে, কিন্তু সেগুলোর generation/shrinking/runtime কারণ আলাদা করা হয়নি (`runs.csv`, maximum_between_response_gap_seconds; `status_codes.csv`)। [H] Complex-body generation বা shrinking bottleneck হতে পারে; phase-level timing ছাড়া hypothesis অমীমাংসিত।
- **Authentication ও oracle scope:** protected PUT/DELETE traffic-এ 401 ও description-only responses আছে। ⚠️ Unauthenticated traffic ও weak schema oracle injected-fault exposure সীমিত করতে পারে; baseline findings-কে injection label দেওয়া হয়নি (`schemathesis_findings.csv`, PUT/DELETE rows; `mutation_exposure.csv`; codebook §5)।
- **Missing attempts:** logger-এ response hook আছে, transport-error hook নেই। তাই captured transport_records=0 থেকে zero transport failures বলা যায় না; readiness traffic আলাদা হলেও generator probe থাকে (`08_experiments/tools/mitm_fulllog.py:39`; `runs.csv`, transport_records/schemathesis_probe_records; `harness/run_pilot.sh:125-130`)।
- **Fresh causality ও labels:** NEW/VANISHED observational; exposure, incomplete traffic ও manifest-derived replay labels classifier accuracy/causal SUT correctness প্রতিষ্ঠা করে না (`attribute.py:1-7`; `fault_comparison.csv`, interpretation)।

## পরের batch-এর নির্দিষ্ট প্রস্তাব ও খোলা প্রশ্ন

নিচেরগুলো ⚠️ এই pilot-এর সীমা থেকে পরিকল্পনামূলক সুপারিশ; নতুন measurement নয় (`runs.csv`; `mutation_exposure.csv`; `schemathesis_findings.csv`)।

1. আগে scout-api-তে `MAX_EXAMPLES=10`, **600-second smoke**, auth profile ও per-operation timing যাচাই করা হোক। সব operation পৌঁছানো এবং mutation exposure মাপা না হওয়া পর্যন্ত বড় comparative batch স্থগিত রাখা যুক্তিযুক্ত; বর্তমান 100-example/600-second settings ছোট অংশেই আটকে গেছে (run table)। এরপর একটি আলাদা common-settings batch-এ **1800 seconds/run**, **25 examples/operation** দিয়ে শুরু; অসম্পূর্ণ হলে সব condition একই **3600-second** budget-এ পুনরায় চালানো অথবা reviewed operation scheduling বদলানো হোক। শুধু দীর্ঘ budget-এ full coverage-এর নিশ্চয়তা নেই।
2. প্রথমে একই SUT-তে seeds **1,2,3 প্রতিটি condition-এ** দিন; চার mutation-এ শুধু seed1 রাখবেন না। এতে 3 baseline + 12 mutant = **15 runs**, 1800-second generation budget মোট **7.5 hours**, startup/collection অতিরিক্ত। এরপর resources থাকলে seeds4/5 যোগ করুন; generation seed effects আলাদা করতে একটি identical-seed repeat রাখুন (baseline variability table; `harness/README.md:151-155`)।
3. পরের SUT candidate **petstore ও market**; এগুলো coordinator handoff-এর candidate, এই task-এ deploy/run করা হয়নি। প্রতিটির health/base/auth ও mutation-capable operations আগে যাচাই করে harness support review করতে হবে; বর্তমান harness scout-api-only (`09_collab/HANDOFF.md`, Claude ফিরে এলে §3; `harness/run_pilot.sh:7`)।
4. Next batch-এর আগে logger transport-error capture, local checker বনাম Schemathesis Content-Type behavior, এবং reviewed JaCoCo report path আলাদা task-এ সমাধান করুন; original controls ও candidate mutants একই frozen tools-এ চালান (checker পার্থক্য ও missing-attempt evidence উপরে; `verification.json`, tool_and_harness_hashes_stable)।

খোলা প্রশ্ন: authenticated user/moderator profile কোনটি হবে; description-only/default responses-এ intended contract কী; দীর্ঘ response-free interval generation/shrinking নাকি অন্য runtime behavior; এবং UTC/monotonic span পার্থক্যের কারণ কী। বর্তমান evidence এগুলো স্থির করে না (`schemathesis_findings.csv`; source spec first GET response pointer; `runs.csv`, timing columns)।
'''
# Expand citation shorthands to repository-relative evidence paths.
report = report.replace('`harness/', '`08_experiments/E1_pilot/harness/').replace('`pilot_results/', '`08_experiments/E1_pilot/pilot_results/').replace('`logs/T12_scratch/', '`09_collab/logs/T12_scratch/')
for name in ('runs.csv', 'status_codes.csv', 'operations.csv', 'violations_by_kind.csv', 'strict_only.csv', 'schemathesis_findings.csv', 'baseline_variability.csv', 'baseline_variability_summary.csv', 'fault_comparison.csv', 'mutation_exposure.csv', 'attribution_details.csv', 'coverage.csv'):
    report = report.replace('`' + name + '`', '`08_experiments/E1_pilot/pilot_results/' + name + '`')
for name in ('smoke_inspection.json', 'verification.json', 'batch_events.jsonl', 'summarize.py:1', 'verify_results.py:1'):
    report = report.replace('`' + name + '`', '`09_collab/logs/T12_scratch/' + name + '`')
report = report.replace('`conformance.py:', '`08_experiments/tools/conformance.py:').replace('`attribute.py:', '`08_experiments/tools/attribute.py:').replace('`specmut.py:', '`08_experiments/tools/specmut.py:')
(ROOT / '09_collab/reports/T12_report.md').write_text(report)
print('Wrote 09_collab/reports/T12_report.md')
