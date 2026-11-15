T41 future-version oracle (offline, baseline items only)

`future_oracle.csv` contains all 62 requested items. `confidence (1–3)` is the
literal requested CSV header. It measures confidence in the recorded historical
assessment, not confidence in the original label. No final labels are edited.

Run from the research directory, in this order:

```sh
/usr/bin/python3 -I -B 08_experiments/E4_triage/future_oracle/mine_history.py
/usr/bin/python3 -I -B 08_experiments/E4_triage/future_oracle/collect_evidence.py
/usr/bin/python3 -I -B 08_experiments/E4_triage/future_oracle/assess_items.py
/usr/bin/python3 -I -B 08_experiments/E4_triage/future_oracle/verify.py
```

The first script reads only the three named clones, EMB snapshots/specs, and
seven explicit baseline label/adjudication CSVs. The collector additionally reads
the three representative baseline run specs and exchanges. The assessment script
contains manual, reviewed decisions, not a general automatic classifier. The
verification script checks data/locators and the material historical conclusions.
All Git calls use a verb whitelist, disable hooks/pagers and lazy fetching, and
never check out or execute project files. No network, packages, Docker, Java,
Maven, build, server or upstream scripts are needed. Source copies are inert text.

Evidence navigation:

- `anchors.json`: per-file Git blob matches, aliases, ties, dates and search bounds.
- `anchor_scores.csv`: scores for every commit reachable from any local ref.
- `*_file_inventory.json`: hash-only inventory of all non-build EMB files,
  including modified SQL/README paths whose contents are deliberately not copied.
- `*_emb_local.diff`: relevant EMB patches, excluding seed SQL values.
- `*_all_descendant_history.json`: all post-anchor descendants from every local
  ref, with default-HEAD membership. Other development lines are not mixed into
  the primary repair judgement. `*_history.json` is the default-HEAD history.
- `history_diffs/`: reviewed Java/spec/configuration patches. No README/HTML or
  SQL seed contents. Dependencies/refactors are evidence candidates, not repairs.
- `source_index.json`, `source_evidence/`: selected anchor/HEAD text and Git blob
  provenance; line numbers correspond to the original source files.
- `spec_origins.json`, `spec_provenance.json`: generation markers and baseline
  spec provenance. The three baseline run specs equal the supplied deployed JSON
  semantically; CWA's deployed document equals its anchor document byte-for-byte.
- `item_history.json`: item-specific propositions, HEAD state, exact source
  locators, paths searched, every candidate commit touch and manual decision.
- `candidate_witnesses.json`: header/body-free witness features for the three
  positive items; includes partial-cluster coverage.
- `cwa_spec_semantic_delta.json`: JSON Pointer changes, avoiding reorder noise.
- `agreement.csv`, `review_proposals.csv`, `summary.json`: comparison and yield.
- `verification.json`: checks and input-hash verification. Scratch input hashes
  and the final artifact manifest live in `09_collab/logs/T41_scratch/`.
- Bengali report: `09_collab/reports/T41_report.md`.

Decision meanings:

- `spec_changed_to_match_code`: a target spec predicate converged to existing
  behaviour. An annotation edit would also be spec-facing, even inside Java.
- `code_changed_to_match_spec`: target handler/validation/mapping logic converged
  to the original spec. None found in this sample.
- `both_changed`: target spec and handler logic both changed. None found.
- `unchanged_at_head`: the relevant checked-in predicates/source remain, with no
  matching repair found. This is a static assessment, not a fresh runtime result.
- `changed_unrelated`: a candidate changed other semantic elements, while the
  target mismatch survived. C005 is the one such case.
- `unclear`: no reliable SUT repair proposition/direction, including 25 original
  TEST items and two deployment-specific transport items. Do not use as a
  negative defect label.

Only the first three directions map to final_L1 for agreement. The remaining
directions, especially `changed_unrelated`, have no fault-side mapping. The
manual analysis was non-blind to the baseline final labels. Historical developer
repair choice is evidence of direction, not proof of original fault origin.

Confidence: 3 = direct targeted predicate edit with unchanged corresponding
handler; 2 = partial/generated refresh or supported static history assessment;
1 = deployment/runtime correspondence is unresolved. P015 is confidence 3 about
the omitted-tags repair, while coverage remains only 2/5 cluster witnesses.

All "future" relations are relative to the EMB source anchor. These fixes
predate the November 2026 baseline experiments. C002 updates a generated,
checked-in JSON document without changing Java annotations or handler logic;
it is a spec-artifact refresh, not a code fix and not independent BOTH evidence.
