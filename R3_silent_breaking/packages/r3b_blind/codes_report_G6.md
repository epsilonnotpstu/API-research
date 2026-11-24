# Coder G6: report for the R3b blind contract review

All 60 items in `items.csv` are coded in `codes_G6.csv`. Work rows are in `codes_work_G6/rows.csv`, and the read-only helpers are `add.py` and `finalize.py` in the same folder. The finalize step checked every row. Each `op_locator` line was confirmed to be the path entry, and each `spec_quote` was confirmed to occur verbatim in the cited document.

## Overall counts
- contract_operation: PRESENT 31, ABSENT 4 (D006, D021, D032, D048), NO_CONTRACT 25.
- contract_specified: SPECIFIED 2 (D040, D050). Everything else is UNSPECIFIED, including all NO_CONTRACT items.

## Conventions used
- **NO_CONTRACT items get `UNSPECIFIED`.** When no contract exists, it cannot state the behaviour. Ditto (D012, D020) counts as NO_CONTRACT: its "swagger" files are only Kubernetes/Helm manifests for a Swagger UI deployment. Halo (D052) also counts: its files are only openapi-generator configs.
- **ABSENT for D048 (nessie).** The only OpenAPI document has `paths: {}` (inferred from annotations), so no operation is described. The affected Iceberg REST catalog operations are a guess.
- **Representative operations.** For cross-cutting changes on a service that has a contract, I named one representative documented operation and set PRESENT: D028 (validation message format), D035 (CORS), D025/D044/D051 (fess SSO permission handling). For cross-cutting changes with no contract, I used `UNKNOWN`: D012, D023, D052, D057, and D031, whose HTTP exposure is unclear.

## Hard cases
- **D040 (Iced-Latte), SPECIFIED, confidence 3.** The product-review contract explicitly documents 400 for "product not found" on the list endpoint, and on GET review it says "Product not found." under 400. The code now returns 404.
- **D050 (datarhei), SPECIFIED, confidence 2.** The contract calls PUT "Replace an existing process." The commit pre-fills omitted fields from the current config, which is merge semantics. I read "replace" as a description sentence stating the behaviour that changed. UNCLEAR is also defensible.
- **D033 (authelia), UNSPECIFIED.** The 2FA passkey branch used to write two responses. The contract gives a single 200 `redirectResponse` schema, but it does not address this branch.
- **D055 (pay), UNSPECIFIED.** "An HTTPS URL on your site" appears only in the response schema (`CreatePaymentResult`). The request schema just says "service return url". The new 422/P0920 mapping is not documented.
- **D059 (microcks), UNSPECIFIED.** Only 201 is documented for import. The new 400/415/500 responses are not mentioned, so the contract is silent rather than contradicted.
- **D024 (apicurio), UNSPECIFIED, confidence 1.** The `owner`/`createdBy` fields exist as bare strings with no statement of how they are populated. The diff may partly be a refactor of how the owner is passed.
- **D016 (keto), UNSPECIFIED.** The `error` field is described generically ("any error generated while checking the relation tuple"). The strict-mode limitation message is not stated.
- **Low-confidence items (1): D010, D018, D024, D025, D031, D038, D044, D048, D049, D051, D054.** These are mostly concurrency, refactor or side-effect changes whose HTTP-observable effect is indirect.

## Boundary incidents
None. I read only files inside the package directory and did not run git. I did not execute any item code, and I opened no other coder's files.
