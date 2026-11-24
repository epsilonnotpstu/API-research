# Coder G5: blind contract review report (R3b)

There are 60 items, coded in items.csv order. The output is `codes_G5.csv`, and the work files are in `codes_work_G5/`. No item code was executed. All searches named explicit item paths inside this package.

## Totals
- contract_operation: PRESENT 30, ABSENT 4 (D006, D021, D032, D048), NO_CONTRACT 25, UNCLEAR 1 (D035).
- contract_specified: SPECIFIED 2 (D040, D050), UNSPECIFIED 58.

## Hard cases
- **D012, D020 (ditto):** the "contract" files are only Kubernetes/Helm Swagger UI deployment manifests, which fetch the real spec at runtime. I treated them as NO_CONTRACT, not ABSENT.
- **D052 (halo):** the only files are OpenAPI generator config files, so I coded NO_CONTRACT.
- **D048 (nessie):** the document has `paths: {}` (filled from annotations at build time), so no operation is described. I coded ABSENT.
- **D035 (casdoor CORS):** the change affects every route, so no single operation applies. I set affected = UNKNOWN and contract_operation = UNCLEAR. The contract never mentions CORS.
- **D040:** the contract explicitly gives 400 for "product not found", and the code now returns 404. Coded SPECIFIED with confidence 3.
- **D050:** the PUT description says "Replace an existing process.", but the update now merges omitted fields from the current config. Coded SPECIFIED with confidence 2. This depends on reading "replace" as a statement about the semantics.
- **D060:** the description "Stop scanAll job execution" is generic. The fix stops further scans from being enqueued after a stop. I coded it UNSPECIFIED, but it is close to D050.
- **D016 (keto):** the `error` field is documented as "any error generated while checking". Strict-mode limitation reporting is not mentioned, so I coded UNSPECIFIED (confidence 2). An argument for SPECIFIED via "the field in question" is possible.
- **D055 (pay):** the response-schema `return_url` is described as "An HTTPS URL…", but the request schema has no HTTPS constraint, and the 422/P0920 mapping and the live-account condition are absent. I coded UNSPECIFIED (confidence 2).
- **D038 (vikunja):** the preview_size description promises a preview for images. The change only affects cache-failure fallback (mostly a refactor), so I coded UNSPECIFIED (confidence 1).
- **D004, D010, D025, D044, D051, D049, D018, D024:** these are internal or concurrency changes (controller tracking, token refresh, races, owner and authorization plumbing). The HTTP-observable effect is indirect, so confidence is 1–2.
- **D031, D057:** the HTTP-observable effect is unclear (an upstream DTO field, and registry endpoint descriptors), so I set affected = UNKNOWN.
- **D022 (harness gitspaces):** the change is in gitness controllers. I mapped it to the CDE swagger's account/org/project gitspace create and action operations, with confidence 2.
- **D023 (FAAAST):** the 405 fix applies to any path, so I set affected = UNKNOWN.
