# E10 addendum: candidate-cluster sensitivity
Claude (supervisor-delegated), 2026-11-16. Written after T48 finished and before any E10 blind run (C9, C10, L3, L4, F1, F2) started. It is frozen in `e10_packages_freeze.sha256`.

## Why
- T48 accepted 40 items from 21 mined candidates. One fix can touch several operations; for example, a shared error envelope becomes several items.
- Items from the same candidate are not independent observations.
- The item-level tests in `E10_PLAN.md` are not changed.

## What is added
`score_e10_cluster.py` (self-test `test_score_e10_cluster.py`). The unit is the candidate cluster (`candidate_id` in `key/accepted_full_t48.csv`), and BOTH items are excluded.

- **H-E10-1, by cluster:**
  - A cluster counts only if it has at least one M1 abstention pair. L3 and L4 are pooled, and R must decide.
  - The cluster is a win if R is correct on more than half of its pairs, and a loss if on fewer than half. Ties are dropped.
  - Test: exact one-sided binomial on wins vs losses.
- **H-E10-2, by cluster:**
  - For each cluster, compute net = (FB correct and M1F wrong) − (FB wrong and M1F correct), summed over the pairings L3–F1 and L4–F2.
  - Test: sign test on clusters with a nonzero net, in both directions.

## Status
- Sensitivity only. The verdicts PASS, FAIL and INSUFFICIENT come from `E10_PLAN.md` alone.
- If the cluster-level result disagrees with the item-level verdict, the results file must report that disagreement next to the verdict.
