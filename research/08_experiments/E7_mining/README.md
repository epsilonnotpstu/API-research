# Offline corpus and parent-state excerpts

The final frozen `pool2.json` contains 12,637 candidates across 34 repositories. Individual ranked screens cover 1,259 candidates. Exact-parent comparison admitted 29 items from 21 candidates, bringing the new corpus to 45 items with the 16 original items. The rebuilt reading package mixes these with all 25 exploratory items: 70 items total. The target was reached at rank 32 of the last reviewed repository; one repository reached its combined six-item cap. See `summary2.json` and `yield2.csv`.

Discovery verifies OpenAPI/Swagger version roots, local reference reachability, JVM contract annotation imports and production JVM/Go behaviour paths. CI, configuration-only YAML, test paths and generated clients are excluded. Ranking retains the original correction-cue strength and operation-path bit without a direction bonus. Preliminary retrieval corrections remain audited privately; final frozen bytes were retained unchanged throughout continuation.

Each reviewed candidate has its own status, reason code, specific reason of at most 25 words, sanitized full patch and hash under `key/`. Accepted items additionally have parent-only propositions, locators and resolving-patch evidence. Other screens are bounded search triage; unproved or oversized pairs remain deferred. These decisions are not runtime observations.

All item history, source identities, truth metadata and salts remain under `key/`. `key/corpus_key.csv` preserves every old logical key row and appends the new rows with `source_task`. `key/e7_key.csv` maps the fresh X-shuffle to the current package; `key/shuffle_mapping.csv` connects the stable and package IDs. The original source rows and old package manifest are preserved under `key/t45_snapshot/`.

The reading package is `../E2_labelling/e7_blind/`. Its table contains only item ID, repository, operation and the verbatim proposition. Source files come from recorded parents; large specifications retain the operation and local reference closure. Privacy redactions preserve line positions in whole files. There are at most eight implementation files per item. Cross-item overlaps retain and flag an item's own locator files; optional overlaps are excluded.

Publication requires the explicit `--replace` flag for an existing package. The build log records the old package hash and replacement event. A new salt and shuffle were used. `verification2.json` records exact disk-byte comparison with deterministic parent reconstruction and all leakage/privacy assertions. The Bengali report is `../../09_collab/reports/T46_report.md`.

The 26 tests run with standard-library Python:

```sh
/usr/bin/python3 -I -B 08_experiments/E7_mining/test_build.py
/usr/bin/python3 -I -B 08_experiments/E7_mining/test_pool2.py
/usr/bin/python3 -I -B 08_experiments/E7_mining/test_review2.py
```

No upstream checkout, build, code execution or network access is used. Synthetic repositories are created only for tests and removed afterwards. Item counts include related operations and distinct mismatch facets from shared candidates; they should not be interpreted as independent observations. Detailed limitations, freeze-preflight history and the corrected attribution-display incident are recorded in the report.
