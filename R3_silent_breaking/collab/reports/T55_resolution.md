# T55 resolution (Claude, 2026-11-18): how each finding was handled in paper v0.3

All 30 findings (9 ERROR, 21 MINOR) were addressed. No scorer output changed. The two errors repeated in `plan/R3_RESULTS.md` (01, 10) are corrected there and marked inline.

| # | Severity | Fix in `paper/R3_draft.md` v0.3 |
|---|---|---|
| 01 | ERROR | §3.2: three repositories had fewer than three, with the sum 44×3+1+1+2 = 136. Also fixed in R3_RESULTS. |
| 02 | ERROR | §3.2: the size cap applies to the retained behaviour-path files (added plus deleted lines). |
| 03 | MINOR | §3.2: first-parent default-branch history up to the recorded HEAD, with a UTC committer-date cutoff. |
| 04 | MINOR | §3.2: per-file whitespace-only and rename-only filtering. |
| 05 | MINOR | §3.2: "does not match the predefined bot patterns". |
| 06 | MINOR | §3.2: the pool was frozen before any patch was inspected for a judgement (discovery reads were mechanical only), followed by the sample freeze and the package freeze. |
| 07 | MINOR | Contributions and Conclusion: 136 commits from 47 repositories of a 54-service corpus. |
| 08 | ERROR | §3.1: the contract document exists at HEAD; 29 of 136 parents have none and are kept; "unchanged" means no contract file was modified. |
| 09 | ERROR | §3.3: Table 1 gives the five mapping-mode counts. The abstract, §4.4 and §5 say "delivered parent-contract context". §6 has a contract-context threat. |
| 10 | ERROR | Abstract, §1, §3.5, §4.3, §5 and §7: proxy wording ("by our annotation proxy … would likely miss"; no generator was run). Also fixed in R3_RESULTS. |
| 11 | ERROR | §1 RQ4, §3.6 and §4.4: the H-R3-2 definition is spelled out; 0/1 no-update (the single case was updated); operation-level lag is not determined. |
| 12 | MINOR | §4.4: 1 specified, 56 unspecified, 3 unclear. |
| 13 | MINOR | §4.2: "all eight response-shape changes, which mainly add fields". |
| 14 | MINOR | §1: "The main remaining gap …", verbatim. |
| 15 | MINOR | §2: "Detection of syntactic breaks …", verbatim. |
| 16 | ERROR | §2: the full verbatim quote "A dynamic API design … often shifts the problem, i.e., creates …". |
| 17 | MINOR | `notes/NOVELTY_VERIFIED.md`: addendum with the AutoGuard entry and its local line locators. |
| 18 | MINOR | §3.1: the six metadata criteria, from `research/08_experiments/E7_mining/t50_repo_selection/SELECTION.md` (no commit content read). |
| 19 | ERROR | §5: "Silent observable change is common" (no longer called "the norm"). |
| 20 | MINOR | §5: "44% … (40% by the Claude codes) … a little over two in five". |
| 21 | ERROR | §7: the denominator is the sampled commits in which behaviour-path code changes but no contract file does. |
| 22 | MINOR | §4.1: YES/NO/UNCLEAR = 60/50/26. The abstract and §4.1 say κ is computed on the 102 both-decided commits. §6 notes the 26 unresolved commits. |
| 23 | MINOR | §3.3 and §6: blinding wording, and the residual risk from short message fragments. |
| 24 | MINOR | §6: Claude batch timing, given as an audit inference. |
| 25 | MINOR | New §3.7 (process deviation) and a process threat in §6. |
| 26 | MINOR | §6: redaction and truncation threat. |
| 27 | MINOR | §6: the pool-level gitlink gap; none was sampled. |
| 28 | MINOR | §3.2 and §6: "up to three"; three repositories contributed fewer. |
| 29 | MINOR | §6: right-censoring. Recomputed against the recorded HEAD rather than the review date: 15 commits had less than 90 days of follow-up, 5 of them with the field false (`paper/exploratory_r3.py`). H-R3-2 is unaffected. |
| 30 | MINOR | §2: the tool description was made generic. The JSS subtitle was confirmed from arXiv 2311.08175 (NOVELTY_VERIFIED addendum). |

**Additional v0.3 changes, not from T55:**
- prose abstract (IEEE);
- third-person anonymised reference to the companion study;
- Table 1–3 captions and Figure 1;
- §4.5 illustrative cases (three commits both families coded as breaking, checked against their diffs; spot-check items avoided);
- §4.6 exploratory cross-family impact cross-tab;
- an implications bullet in §5;
- Data availability and Disclosure of AI use.
