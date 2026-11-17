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
