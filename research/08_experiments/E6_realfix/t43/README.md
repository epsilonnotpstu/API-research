# T43 offline contract-alignment mining

T43 manually screened **251 commits** from 12 additional bare repositories: every frozen per-repo rank 1–20 (240), plus 11 named adaptive supplements. It accepted **12 items: IMPL 11 / SPEC 1**. The deduplicated T42 ∪ T43 contains **25 items: IMPL 14 / SPEC 11**. The combined IMPL target of 16 was **not reached**. Stopping condition: every repository's ranked pool was screened to the declared depth of 20, with supplementary ranks recorded in `summary.json:per_repo`. This does not mean all history or all changed lines were exhausted.

Evidence: `summary.json`, `candidates.csv:review_status`, `accepted.csv:T43R001–T43R012`; frozen T42 input: `../accepted.csv`; union: `../combined_accepted.csv`.

## Inputs and reuse

- Bare clones: `/run/media/afridi/Shared Data/api_research_upstream/{repo}.git`. Inventory pins each HEAD; every candidate pins its exact fix and single parent SHA. Discovery used all reachable refs, non-merge history, without a date cutoff.
- `t43_mine.py` reuses T42 `../scripts/mine.py` read-only `git`/`blob` functions and its redaction filters. The T43 wrapper adds attribution/credential and multiline private-key filtering, preserving numeric source lines. No upstream code is imported or executed.
- `t43_review.py`, `t43_accepted.py` and `t43_build.py` extend the T42 bounded-diff/source inspection, manual locator definitions and table/leakage-audit model. T42 files are not edited. The pre-task SHA-256 freeze of 140 existing E6 files is in `../../../09_collab/logs/T43_scratch/freeze.json`.
- `../t43_repo_meta.csv` records stars/created month/push month supplied by the supervisor from GitHub API on 2026-11-15. These are supplied measurements, not independently fetched or verified by this offline run. `service-api` denotes `reportportal/service-api`.
- `input_freeze.json` pins the candidate pool, inventory, T42 accepted input and T43 metadata. The builder checks it before writing outputs. Discovery refuses to replace the saved pool; new history mining requires a new task directory.

## IMPL-oriented retrieval

A commit needs a correction/conformance/validation/status/serialization/null/default-related subject cue **and** a changed production-like Java/Kotlin or contract-named JSON/YAML path. Obvious merge/root/release/dependency/revert titles are excluded; test/generated/target/client path patterns are filtered. Exact regexes are in `t43_mine.py:CUE,SURFACE,CONTRACT_PATH,SPECIFIC`.

Rank score is:

`30*specific_behavior_cue + 12*correction_cue + 10*(behavior_path && no_coarse_contract_path_changed) + 4*contract_word_cue + min(production_paths,3) - 12*(feature_or_refactor_cue && !correction_cue)`.

Sort is repo, descending score, ascending full SHA. `candidates.csv:rank` and `candidate_pool.json` freeze the result. Scores are retrieval hints. The coarse contract filename detector misses differently named YAML and annotation edits; the production path detector also retrieves internal services, clients and integration code. It is **not** a same-operation detector or proof of direction. Accepted operations are linked manually at the exact parent.

Adaptive supplements: Strimzi ranks 22,23,31,33; RHSM 26,71; HiveMQ 424,436; service-api 663; CWMS 34,37. Selection followed focused status, nullable, content-type and explicit API-spec-conformance titles. It is purposive, not random. The initial 240 screens accepted 6 items; the 11 supplements accepted 6 (`summary.json:top20_accepted,supplementary_accepted`).

## Manual acceptance gate

Each accepted item has the neutral parent-state form:

`METHOD /path: contract says ...; implementation does ...`.

`proposition_check` contains only **parent** contract/implementation/route locators. `evidence` adds SHA-256-checked parent/fix snapshots, numbered excerpts, a concrete changed hunk, and a contract gate. For every IMPL item, the parent already has an independent checked-in OpenAPI spec or Swagger/OpenAPI response annotation. Independent spec blobs are identical in parent/fix; changed Java files retain identical scoped contract annotation blocks. The SPEC item retains its parent implementation block. No decision is based solely on tests, client behavior or a commit title.

Confidence: 3 = direct local contract/source/patch linkage; 2 = stated framework, exception-mapping, header-default or external-success-path inference remains; 1 = substantial unresolved ambiguity (none accepted). New endpoints/features, pure refactors, generated-only churn and client/test-only contracts are rejected; unresolved parent contracts are deferred. One proposition per fix commit; no multiplication by fields or endpoints. See `t43_curation.py`, `t43_accepted.py`, `source_evidence/` and `review_evidence/`.

Rejected/deferred review depth is a bounded production diff screen. Large patches are not exhaustively adjudicated. There are 127 rejected and 112 deferred screens; 6,119 heuristic candidates remain unreviewed. In particular, Strimzi's binary-key repair is deferred: its parent prose states the binary restriction, but the shared OpenAPI key schema also permits objects without expressing that conditional restriction (`candidates.csv:T43C06239`). This strict run does not turn prose alone into spec-file evidence.

## Deduplication, popularity and leakage

`../combined_accepted.csv` adds `source_task`, `fix_family`, stars and leakage flags. Deduplication key: repo + exact operation + manually scoped fix family. T42 family defaults to its existing `mismatch_type`; all original T42 columns/values are preserved. The two cohorts have disjoint repo names, so this cross-cohort family-vocabulary difference causes no collision here. No accepted duplicate was dropped. T42 evidence paths and T43 `t43/...` evidence paths are relative to E6. Its T42 stars remain explicitly unavailable.

The parent-only leakage audit covers all tracked Markdown/text/RST/AsciiDoc/HTML, plus extensionless/JSON/YAML changelog, release, history, news, changes, README or issue paths. It scans full future fix SHA, seven-character SHA, and the recorded sanitized subject; numeric issue/PR and JIRA identifiers are separately flagged as potential pointers. **612 item-file scans across all 25 combined items: 0 exact fix-reference hits, 0 issue-identifier hits** (`leakage_audit.json`). Counts can include the same physical file at multiple parent/item states. Only tracked parent issue material is available; no issue text was fetched. This does not cover paraphrases, every source file, external issue histories or package-level blindness.

## Verification and reproduction

From the `research/` directory, use only our standard-library Python scripts:

```sh
/usr/bin/python3 -I -B 08_experiments/E6_realfix/t43/t43_build.py
/usr/bin/python3 -I -B 08_experiments/E6_realfix/t43/t43_verify.py
```

The original one-time discovery command was `t43_mine.py`; the saved pool is now frozen. Review examples, without executing upstream code:

```sh
/usr/bin/python3 -I -B 08_experiments/E6_realfix/t43/t43_review.py strimzi-kafka-bridge 13 --lines 70
/usr/bin/python3 -I -B 08_experiments/E6_realfix/t43/t43_review.py rhsm-subscriptions 71 --probe '^api/rhsm-subscriptions-api-spec.yaml$' 'name: beginning|name: ending' --context 8
```

The builder checks real single parents/dates, locator existence and line stability, parent-only proposition roles, unchanged parent contracts, actual diff hunks, depth coverage, union preservation, frozen T42 hashes and privacy patterns. `verification.json` records **401 passing assertions**. `final_qa.json` records independent CSV/union/locator and explicit parent-contract checks. Mechanical checks do not replace semantic review.

No checkout, build, generator, SUT, Docker, Java/Maven/Gradle, upstream script/hook, network, blind package or key was used. No runtime traffic was observed. These are static mining items; runnable benchmark readiness, HTTP witnesses and independent adjudication remain outstanding. Report: `../../../09_collab/reports/T43_report.md`.
