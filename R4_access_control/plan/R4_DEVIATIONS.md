# R4 deviations (append-only)

## D1 (2026-11-23 18:05, before any mining output existed): two independent pipeline implementations
**Change.** Codex was unavailable until 18:23. Instead of waiting, Claude implements the mining pipeline of §3, §4 and §6 itself, in `mining/claude/`, as the **primary** implementation. Codex implements the same specification independently, as task **T56b**: T56 plus one extra rule, "do not read `mining/claude/`", with its output in `mining/*.py`.

**Safeguard.** Before any package is shown to a coder, the two implementations must agree on the following, compared mechanically:
- the eligible pool: item set, repositories, fix and parent SHAs, and mechanical fields;
- the exclusion counts by reason;
- the sample.

Each mismatch is resolved by the plan text and logged here. No mismatch may be resolved by looking at advisory content or coder output.

**Why it cannot bias results.** The pipeline is mechanical (§3 to §6). Neither implementation reads advisory text for any decision. Only the commit URLs and the repository trees are used.

## F1 (2026-11-23 18:20): shallow-boundary bug in resolve; first pool superseded before any package existed
- **Problem.** The first `pool` run of `mining/claude/r4p.py` gave `NO_PARENT` for 51 advisories. The cause: fix commits that a parallel prefetch had already fetched only as the shallow boundary of another commit, so their parent object was absent.
- **Fix.** If the parent does not resolve, the fix commit is re-fetched with `--depth=2` and the parent is checked again.
- **Effect.** The first run's `resolved.json`, `pool*.json` and `pool_freeze.json` were moved, unopened, to `mining/cache/superseded_run1/`; only their counts were printed. No sample, package or advisory text was produced from them.
- **Nature of the change.** Purely mechanical, with no judgement involved.

## F2 (2026-11-23 18:40): credit redaction in item.md strengthened before any coder saw a package
- **Problem.** The supervisor inspected a partial build (134 of 148 items). Reporter names survived on the lines after a "Credits" heading, and in phrasings such as "would like to thank these contributors" (12 items).
- **Fix.** A credit line, and every following line up to the next Markdown heading, is now redacted. The trigger phrases are credit, thank, acknowledge, contributors, reporter(s), "reported/discovered/found/identified/disclosed by/this", and "researcher(s) who".
- **Effect.** The partial build was deleted, and `build` was re-run with the same shuffle salt, so the item ids are unchanged. No coder had been launched.
- **Nature of the change.** Mechanical; affects only advisory acknowledgement text.

## F3 (2026-11-23 18:50): one more credit phrasing; rebuild before any coder
- **Problem.** The package audit (`collab/scripts/r4_package_audit.py`) found one item whose advisory names the person who wrote the original fix, with their GitHub handle ("The original fix by … (@…)").
- **Fix.** The credit trigger now also covers "authorship", "fix/patch/commit by|from" and "sign-off".
- **Effect.** Rebuilt with the same salt, so the item ids are unchanged.
- **Other audit hits, kept with this rationale.**
  - In one item, the fix author's name equals the repository owner that appears in Go import paths. The repository name is shown anyway.
  - In one item, a 6-character committer name coincides with an ordinary word in the contract.

## D1 note A (2026-11-23 ~19:00): defect found in Codex's independent implementation
Run in the scratch copy `../R4_codex_run/`, Codex's `r4_collect.py` sent CWE ids as `CWE-284,…`. The GitHub API returns 0 advisories for that form; it needs plain numbers, as plan §3 lists them. The scratch copy was patched with this one-line change only (`collab/reports/D1_codex_collect_patch.diff`); Codex's file in `mining/` is unchanged. After the patch, its collection matched Claude's: 1,972 kept plus 53 withdrawn equals 2,025.

## F4 (2026-11-23 ~19:10): primary pipeline aligned with the plan text after Codex review T57; run 2 superseded before any coder
Codex's review (`collab/reports/T57_report.md`) listed 24 potentially material differences. Most concern inputs absent from our data (empty pools, malformed URLs, git configuration). Those that apply were resolved **by the plan text**:
- **M05.** Contract path is the file name only, as in §3.1 ("a path whose file name contains"). The T50 directory alternative is dropped; §3.1's mention of "the T50 detection rule" is read as referring to the file-name rule.
- **M06.** Source files exclude test files by file name too (§3.2 says "non-test").
- **M07.** `numstat` uses git's default rename detection (`-M`, NUL-separated), per T56's `git diff --numstat`. Before files are read at the old path.
- **M12.** `fix_touches_annotation` scans the **whole fix diff** (§6, "the fix diff"), with hunk-state parsing.
- **M13.** `test_in_fix` counts only added, modified, renamed or type-changed test files (§6, "adds or modifies").
- **M15/M16.** Raw PEM private-key blocks and known token prefixes (GitHub, AWS, Slack, Stripe, Google, GitLab) are redacted in every delivered text. Before this fix, one contract had an AWS-style example key.
- **M18.** Failure to read any blob is now fatal instead of being skipped.

Run 2's pool, sample, key and packages were moved to `mining/cache/superseded_run2/` or deleted. Rebuilt with the same salt. No coder had been launched.

## D1 note B (2026-11-23 ~19:20): safeguard met; the two implementations agree
The comparison used Codex's patched scratch run and Claude's F4 run (`collab/reports/D1_comparison.txt`).
- **Pool.** Identical: 176 items. All of these fields are identical on every item:
  - repository, fix SHA, parent SHA, GHSA set;
  - `fix_lines`;
  - `fix_touches_contract`, `fix_touches_annotation`, `fix_silent`, `test_in_fix`.
- **Sample.** Identical: 138 items.
- **Remaining differences.**
  - `language`: Codex computes it only at build time, so it is absent from Codex's pool.
  - Exclusion accounting: Claude's 945 `NO_COMMIT` + 1 `FETCH_ERROR` + 831 `NO_CONTRACT_AT_PARENT` against Codex's 947 `NO_COMMIT` + 830 `NO_CONTRACT_AT_PARENT`. One advisory is labelled differently; pool membership is unaffected.
- **Packages.** Built by Claude's implementation, as primary.
