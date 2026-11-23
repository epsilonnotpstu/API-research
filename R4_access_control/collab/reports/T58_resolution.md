# T58 resolution (Claude, 2026-11-23): paper v0.3

All 17 findings (10 ERROR, 7 MINOR) were addressed in `paper/R4_draft.md`. No scorer output changed.

| # | Fix |
|---|---|
| E01 | §3.6: H-R4-1 to H-R4-3 use binomial tests with a minimum of 20; H-R4-4 uses a κ threshold with a minimum of 30. |
| E02 | §6: exact agreement (pool membership, SHAs, mechanical fields, sample) after the one-line query fix. The language field and the accounting of one exclusion differ. |
| E03 | §3.3: up to 20 touched source files, and up to the 3 largest contract documents with an index. |
| E04 | §4.5: "most property-level flaws (9/13)". |
| E05 | Abstract and conclusion: the 89 decided cases split 40/49, and 13 are undecided. |
| E06 | §5: the "within reach" claim was replaced by a ⚠️-marked inference; tool detection was not measured. |
| E07 | §2: "statically" removed; the CCS 2024 paper is cited by its verified title only. |
| E08 | §2: BACFuzz is described only as a "gray-box fuzzer for BOLA and BFLA in PHP web applications", which is verified. |
| E09 | Abstract, §1 and §2: evaluations combine seeded, example and real APIs. The verified claim is that P015's missed-check oracle found no faults in real APIs. |
| E10 | §2 and §5: the companion result is stated with its numbers (R3: 136 commits, 47 services; 44% observable; 29/32 = 91% of breaking changes touch no annotation). |
| M01 | §4.5: "other 5, unclear 8" added. |
| M02 | Abstract: "mostly" added. Missing authentication is 17/17, so it stays unqualified. |
| M03 | §3.2: exact detection rule, and "no contract matching our detection rule" for the 831 excluded fixes. |
| M04 | §4.1: within-family κ is computed over all 138 items, with NA counted as a category. |
| M05 | §4 note and Data availability: coding results come from the scorer; the funnel has separate provenance; the script re-scores coding results. |
| M06 | §3.3: withheld and redacted metadata, plus the two documented residual name collisions. |
| M07 | Archive: built and verified after v0.3 (`<Shared Data>/R4_replication/`). The link is pending upload by the authors. |
