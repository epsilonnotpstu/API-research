# R3 deviations and process notes
Every entry here is recorded before any R3 blind run and before any score.

## D1: Claude completes T53 mining after a Codex usage limit (2026-11-17, ~19:00)
**What happened.** Codex hit its usage limit at 18:02, with reset announced for 19:56. By then it had written:
- the T53 scripts: pool, sample, contracts, privacy, build, report and tests;
- pool checkpoints for 30 of the 54 repositories.

It had not frozen the pool. The user asked Claude not to wait for Codex.

**Decision.** Claude (supervisor-delegated) runs Codex's own T53 scripts, unchanged, to finish the pool, freeze it, draw the sample and build the packages.

**Why this does not bias the data.** T53 contains no judgement step. Every rule was fixed in the frozen `collab/tasks/T53.md` before mining:
- the candidate criteria;
- the seeded sample (`random.Random("20261117:" + repo)`);
- the mechanical contract projection;
- the redaction and the mechanical key fields.

Claude knows the hypotheses but makes no choice that could favour them. Two further safeguards:
1. Claude does not open any sampled commit's content before the pool and sample are frozen.
2. Package building, like everything else here, is done only by Codex's scripts.

**Blind roles are not taken over.** The GPT coders G1/G2 still run on Codex after the reset. The Claude coders H1/H2 run as fresh-context subagents, as planned.

**Code provenance.**
- Codex's 29 synthetic tests passed before use (`test_t53.py --synthetic-only`).
- Any fix Claude has to make to Codex's scripts will be listed below with its reason, before packages are frozen.

**Fix F1 to Codex's `t53_pool.py`.**
- **Cause.** Discovery stopped in the `harness` repository. `git cat-file --batch` answers `<oid> submodule` for a `rev:path` inside a git submodule, and `Git.batch` accepted only `missing` as a two-field answer.
- **Change.** One line: a `submodule` answer is treated like `missing`. A path inside a submodule is not a blob of the repository, so it can be neither a contract document nor a behaviour file of this repository.
- **No rule change.** The candidate rules are unchanged.
- **Consequence.** The code hash changes, so every per-repository checkpoint is invalidated and all 54 repositories are rediscovered with the fixed code.
- **Tests.** The 29 synthetic tests pass after the fix.

**Speed-up S1 (no code or rule change).**
- **Why.** Sequential rediscovery of all 54 repositories was slow, about 6 minutes per large repository.
- **What.** `collab/logs/T53_scratch/parallel_checkpoints.py` calls Codex's own `discover()` in 5 worker processes. It writes per-repository checkpoints in exactly the format and signature (HEAD + code hashes) that `t53_pool.main()` validates.
- **Effect.** `main()` reuses a checkpoint only if its signature matches. The pool and its freeze are still produced only by `main()`. Discovery is deterministic, so the order of computation cannot change the pool.

**Fix F2 to Codex's `t53_privacy.py` (before any package was published).**
- **Cause.** The build preflight's package scan flagged the fixed `README.md` and `TASK_R3.md` texts.
  - Every non-empty line of the sampled commit messages was used as a redaction needle.
  - Of the 777 needles, 125 were shorter than 20 characters. Single-word lines of 1–10 characters matched ordinary words.
  - Those needles would also have replaced ordinary source tokens in the item files with `[REDACTED]`.
- **Change.** A message line is a needle only if it has at least 20 characters and at least 3 words.
  - Distinctive message text copied into code or contract files is still redacted.
  - Issue and PR numbers, ticket IDs and commit SHAs are still redacted by their own rules.
- **Inspection.** Only needle lengths and word counts were inspected; no message text was displayed.
- **Tests.** The 29 synthetic tests pass after the fix.
- **Timing.** The fix comes after sampling and before packaging, so the sample is unchanged.

**Fix F3 to Codex's `t53_build.py` (before any package was published).**
- **Cause.** The first preflight after F2 built only 43 of 136 sampled items.
  - 93 items failed in contract projection: 36 JSONDecodeError after redaction, and 57 ContractError (27 missing reference target, 22 unsupported syntax, 5 missing local reference, 3 line bound).
  - Dropping them would make the delivered set a non-random subset of the frozen sample.
- **Change.** In `build_item`, a ContractError or JSONDecodeError in projection no longer drops the item. Instead it falls back:
  - the parent's root contract document(s), redacted, are delivered as plain text;
  - the first 2,000 lines are kept, in path byte order;
  - the mapping mode is `raw_fallback`.
  - The redacted-missing-local-reference check now raises ContractError, so it falls back too.
  - Unsafe-path and privacy findings still fail the item.
- **Plan basis.** The plan already allows "the whole document projected to at most 2,000 lines" when no operation can be mapped.
- **Review.** Codex reviews F1–F3 independently in T54 before packages are frozen.

**Codex T54 review of F1–F3 and the resulting decisions (`collab/reports/T54_report.md`).** 53 synthetic tests pass (24 new in `mining/test_t54.py`, plus 29 in T53).

- **F1: protocol fix OK, eligibility gap noted.** A pure gitlink at a behaviour-looking path could enter the pool without any source blob.
  - Checked mechanically, using object types only: none of the 136 sampled commits touches a gitlink path, and every sampled commit has at least one source blob.
  - The frozen pool and sample are therefore kept unchanged. A pool-level patch would change the frozen pool for no effect on the sample.
- **F2: accepted with a documented residual risk.** Short or two-word distinctive message text that also appears verbatim in delivered source or contract text is not redacted. Such text is a code comment or string the developers wrote into the code, which coders legitimately see as code. The residual risk is that a coder could identify the commit. Coders work offline with no history access, so they cannot look it up.
  - Codex's alternative was to use all message lines. That reproduces the generic-token damage, where ordinary words in source are replaced, so it was rejected.
  - The full-text scan remains for distinctive lines (at least 20 characters and at least 3 words), ticket and PR IDs, and SHAs.
- **F3: OK, with the scope of D1 narrowed.**
  - "Unsafe path still fails" refers to unsafe **output** paths.
  - An escaping `$ref` inside a contract leads to the raw fallback, which delivers only the parent's root contract document(s), so no file outside the repository tree is read.
- **F4 (new, from the T54 review).** `scan_package` now also scans every delivered relative path, against both the generic privacy findings and the sample metadata.
  - A finding fails the build.
  - T54's characterisation test `test_risk_metadata_in_fallback_filename_is_not_scanned` now fails, as expected: the risk it demonstrated is closed.

**Fix F5 to `t53_build.py` `scan_package` (before publication).**
- **Cause.** After F3, the preflight failed at package level on three `raw_fallback` contract files, all with finding kind `vcs_header` and no other kind. The case-insensitive VCS-header pattern (`^index <hex>`, `^Date:`, …) matches ordinary upstream YAML lines, such as a top-level `date:` key.
- **Change.** The VCS-header check now applies to the generated files: `diff.patch`, `item.md`, `items.csv`, `README.md` and `TASK_R3.md`. It no longer applies to upstream `contract/`, `before/` or `after/` file contents. Those still pass the full privacy and metadata findings: emails, attribution, credentials, encoded literals, sample SHAs, IDs and message text.
- **Inspection.** Only the finding kinds and file roles were inspected; no contents.

**F4 revised (before publication, 2026-11-18).**
- **Cause.** The first version of F4 ran the generic content rules on delivered paths. The build then flagged almost every path: 143 before, 153 after and 176 contract paths. `ENCODED` matches any token of 40 or more characters joined by `/`, such as Java source paths.
- **Change.** Paths now get a targeted check (`path_flag`). A path is flagged only if:
  - it contains a sample SHA of at least 7 characters, or a distinctive message line; or
  - one of its segments contains an email address, a ticket-style ID, or a `#N` ID written with `#`.
- **Tests:**
  - `test_t53.py --synthetic-only`: 29/29 pass.
  - `test_t54.py`: 22/24 pass. Both failures are expected by design:
    - `test_risk_metadata_in_fallback_filename_is_not_scanned` now fails because the path check catches the ID in the filename.
    - `test_package_scan_still_rejects_fallback_vcs_header` fails because F5 deliberately exempts upstream contract contents from the VCS-header check; their full privacy findings still apply.

**Fix F6 to `t53_build.py` (2026-11-18, before any coder ran).**
- **Cause.** The first successful build delivered 115 of 136 items. All 21 build failures had one item-level finding, `non_idempotent_or_metadata`, always on a projected JSON contract, and always because the generic redaction rules are not idempotent (redacted output matched another rule on a second pass). None was caused by remaining sample metadata.
- **Inspection.** Only finding kinds, file roles and the cause class were inspected; no values.
- **Change.** `redact_fix` applies redaction to a fixpoint (at most 5 passes) for every delivered file in `build_item`. This only ever redacts more, and is byte-identical for files that were already idempotent.
- **Superseded build.** The first build's package and key files were moved unopened to `collab/logs/T53_scratch/superseded_build1/` (local only) and replaced by the rebuild. The salt, and therefore the item IDs, are unchanged. No coder had seen it.
- **Tests.** `test_t53.py --synthetic-only` 29/29. `test_t54.py` 22/24, with the same two expected failures as before.

**Fix F6b (2026-11-18).**
- **Cause.** After F6 the rebuild delivered 122 of 136 items. All 14 remaining failures were again `non_idempotent_or_metadata` on a projected JSON contract, generic cause: redaction did not reach a fixpoint within 5 passes.
- **Change.** A projected contract whose redaction still changes after the fixpoint attempts raises ContractError, so the item takes the F3 raw-text fallback instead of failing.
- **Superseded build.** The second build (122 items) was moved unopened to `collab/logs/T53_scratch/superseded_build2/`. The IDs are unchanged.

**Fix F6c (2026-11-18).**
- **Cause.** F6b did not change the result: 122 delivered and the same 14 failures. The non-converging redaction was in the raw-fallback contract text, which also starts with `{`.
- **Change.** If redaction still has no fixpoint after 5 passes, `redact_fix` replaces every line that redaction would still change with a whole-line `[REDACTED]` marker. The marker itself is idempotent. This removes more text, never less.
- **Superseded build.** The third build was moved unopened to `superseded_build3/`.

**Fix F6d (2026-11-18).**
- **Cause.** F6b and F6c left the build byte-identical (122 delivered, 14 failed). Direct inspection of one failing item (boolean properties only) found the cause:
  - In the raw fallback, a large JSON contract is redacted as JSON and then truncated to 2,000 lines.
  - The truncated prefix is no longer JSON, so redaction applies different line rules to it.
  - A second pass therefore changes it. One further pass reaches a fixpoint.
- **Change.** The truncated fallback text is passed through `redact_fix` again.
- **F6b and F6c** stay in place as harmless guards.
- **Superseded build.** The fourth build was moved unopened to `superseded_build4/`.

**Build outcome (2026-11-18).**
- After F6d, all 136 sampled items were delivered, with 0 build failures.
- Mapping modes:
  - `raw_fallback`: 93
  - `no_checked_in_document`: 29 (the parent commit has no checked-in contract document)
  - `bounded_document_prefix`: 6
  - `whole_document`: 5
  - `mapped_operations`: 3
- Claude's own checks:
  - 136 items with IDs matching the key;
  - `items.csv` uses LF line endings;
  - `TASK_R3.md` is byte-identical to the plan copy;
  - none of the 1,009 delivered files contains any sample commit or parent SHA (full, 10-character or 7-character).
- The Claude batches are `r3_kb1`–`r3_kb10` (14 items each; `r3_kb10` has 10).
