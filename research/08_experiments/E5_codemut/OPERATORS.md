# E5 implementation mutation operators — T19

The tool implements five operator families as **reviewed, digest-pinned exact
edits**, not arbitrary Java AST rewriting. Every site is reviewed catalogue
data in `sites.json` (row key `site_id`). All runtime effects below are **[H]**:
no Java compilation, SUT execution or mutation kill was observed in T19.
Synthetic safety tests do not establish real Java compilation
(`test_codemut.py`; `../../09_collab/logs/T19_scratch/tests.txt`, final summary).

## Operator-level expectations

All five inject on the IMPL side. The L1 expectation describes the newly inserted
defect's intended origin; it does not relabel pre-existing SPEC/BOTH/TEST faults.
Codebook: `08_experiments/R1_triage_codebook.md:90–114,228–259`;
current evidence: `08_experiments/E1_pilot/pilot_results/PILOT_SUMMARY.md:39–52,79–112`
and `08_experiments/E2_labelling/FINAL_LABELS.md:18–24`.

| Operator | Expected L1 / L2 | [H] conformance signal when exposed | Required distinction |
|---|---|---|---|
| DROP_VALIDATION | IMPL / I-ACCEPT-INVALID; I-CRASH if it instead crashes | INVALID_ACCEPTED for spec-invalid → 2xx; SERVER_ERROR for a causal 5xx | Revalidate the actual request with the unchanged spec; binding, service or persistence validation can still reject it. |
| WRONG_STATUS | IMPL / I-RESP-CONTRACT | UNDOCUMENTED_STATUS, only without applicable exact/range/default response | A schema-free default can make the mutation invisible; do not pick 503 and then misinterpret ENV policy. These sites use 418. |
| DROP_NULL_CHECK | IMPL / I-CRASH | SERVER_ERROR | Require an absence/null witness that reaches the removed guard. Existing crashes on the same path are not new ground truth. |
| RESP_FIELD | IMPL / I-RESP-CONTRACT | RESPONSE_SCHEMA for a missing required field | Dropping an optional field is usually invisible. WRITE_ONLY targets serialization while retaining setters/input binding; verify framework behavior at runtime. |
| REJECT_VALID | IMPL / I-REJECT-VALID | VALID_REJECTED, optionally UNDOCUMENTED_STATUS | Need a control 2xx for the identical request and equivalent state; spec-valid syntax alone does not prove resource existence or business validity. |

Signal implementation: `08_experiments/tools/conformance.py:399–442`.
Market's 406 rejection convention needs the separately reported SUT oracle
(`08_experiments/R1_triage_codebook.md`, §10.8;
`08_experiments/E1_pilot/harness_v2/suts/market.env`, REJECT_STATUSES_DEFAULT).
No strict-only missing-property policy is invented here.

## Exposure evidence and limits

`exposure.json` records a frozen selection of one **complete seed-1 baseline per
SUT**, its run/exchange hashes, and operation-level status counts. It is read-only
evidence of captured requests, not bytecode/site coverage. These latest baselines
can be from negative-data variants and are **not** matched E5 controls. A new
same-harness control build/run is required. `evidence_id` identifies rows below.
The URI templates are matched to the original spec by method/path; no source or
saved exchange was changed (`../../09_collab/logs/T19_scratch/make_catalogue.py`,
exposure loop; `exposure.json`, `selection` and `runs`).

## scout-api
Source root: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/scout-api/`.
Exposure source: `08_experiments/E1_pilot/runs/scout-api/20261114T094102Z_batch_237105_baseline_NONE_p0_s1/exchanges.jsonl`; `run.json` was complete, baseline, seed 1 (`exposure.json`, `runs.scout-api`).

### scout-drop-validation — DROP_VALIDATION
- Site: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/scout-api/api/src/main/java/se/devscout/scoutapi/resource/ActivityResource.java:54`; exact before/after/file digest: `sites.json`, `scout-drop-validation`.
- [H] Expected: IMPL / I-ACCEPT-INVALID; signal: none guaranteed under the current oracle.
- Operations: `GET /v2/activities`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/scout-api.json:167`.
- Captured exposure: 100 requests, statuses `{"200": 35, "400": 23, "404": 27, "500": 15}`; first 2xx line `402`, first nonempty JSON 2xx line `None` (`exposure.json`, `scout-api:GET /v2/activities`; `08_experiments/E1_pilot/runs/scout-api/20261114T094102Z_batch_237105_baseline_NONE_p0_s1/exchanges.jsonl:402`).
- Conditions/limitations: Latent under current spec: comma-separated numeric filters are declared strings. Removing the explicit parser guard changes code intent, but INVALID_ACCEPTED needs an encoded spec constraint. Exclude from detection denominator until a non-spec-changing oracle/witness is justified.
- Witness plan: Send ages=not-an-integer to demonstrate the removed guard; report semantic-only survival if original spec accepts it.

### scout-wrong-status — WRONG_STATUS
- Site: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/scout-api/api/src/main/java/se/devscout/scoutapi/resource/SystemResource.java:31`; exact before/after/file digest: `sites.json`, `scout-wrong-status`.
- [H] Expected: IMPL / I-RESP-CONTRACT; signal: UNDOCUMENTED_STATUS.
- Operations: `GET /v1/system/roles`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/scout-api.json:770`.
- Captured exposure: 1 requests, statuses `{"200": 1}`; first 2xx line `2002`, first nonempty JSON 2xx line `2002` (`exposure.json`, `scout-api:GET /v1/system/roles`; `08_experiments/E1_pilot/runs/scout-api/20261114T094102Z_batch_237105_baseline_NONE_p0_s1/exchanges.jsonl:2002`).
- Conditions/limitations: This operation declares only 200; 418 has no default fallback. Confirm body unchanged and original 200 witness.
- Witness plan: GET /api/v1/system/roles with the same headers against clean baseline and mutant.

### scout-drop-null — DROP_NULL_CHECK
- Site: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/scout-api/data-access/src/main/java/se/devscout/scoutapi/dao/TagDao.java:36`; exact before/after/file digest: `sites.json`, `scout-drop-null`.
- [H] Expected: IMPL / I-CRASH; signal: SERVER_ERROR.
- Operations: `GET /v2/tags`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/scout-api.json:898`.
- Captured exposure: 100 requests, statuses `{"200": 95, "404": 5}`; first 2xx line `2304`, first nonempty JSON 2xx line `2304` (`exposure.json`, `scout-api:GET /v2/tags`; `08_experiments/E1_pilot/runs/scout-api/20261114T094102Z_batch_237105_baseline_NONE_p0_s1/exchanges.jsonl:2304`).
- Conditions/limitations: Absent optional name reaches name.toUpperCase(); original skips the filter. Verify original request succeeds; group/name mutations can share an existing SERVER_ERROR fingerprint.
- Witness plan: GET /api/v2/tags without name; preserve optional attrs behavior and inspect the new stack.

### scout-response-field — RESP_FIELD
- Site: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/scout-api/api/src/main/java/se/devscout/scoutapi/resource/SystemResource.java:51`; exact before/after/file digest: `sites.json`, `scout-response-field`.
- [H] Expected: IMPL / I-RESP-CONTRACT; signal: none guaranteed under the current oracle.
- Operations: `GET /v1/system/roles`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/scout-api.json:770`, `08_experiments/_external/emb/openapi-swagger/scout-api.json:2074`.
- Captured exposure: 1 requests, statuses `{"200": 1}`; first 2xx line `2002`, first nonempty JSON 2xx line `2002` (`exposure.json`, `scout-api:GET /v1/system/roles`; `08_experiments/E1_pilot/runs/scout-api/20261114T094102Z_batch_237105_baseline_NONE_p0_s1/exchanges.jsonl:2002`).
- Conditions/limitations: Dropping permission_levels is invisible to the current default schema because neither RolesView field is required. Strict additional-property policy does not detect an absent optional field. Keep as an oracle-blind negative control, not a claimed killed mutant.
- Witness plan: Compare raw JSON key presence, separately from conformance. Do not strengthen the test spec.

### scout-reject-valid — REJECT_VALID
- Site: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/scout-api/api/src/main/java/se/devscout/scoutapi/resource/TagResource.java:44`; exact before/after/file digest: `sites.json`, `scout-reject-valid`.
- [H] Expected: IMPL / I-REJECT-VALID; signal: VALID_REJECTED.
- Operations: `GET /v2/tags`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/scout-api.json:898`.
- Captured exposure: 100 requests, statuses `{"200": 95, "404": 5}`; first 2xx line `2304`, first nonempty JSON 2xx line `2304` (`exposure.json`, `scout-api:GET /v2/tags`; `08_experiments/E1_pilot/runs/scout-api/20261114T094102Z_batch_237105_baseline_NONE_p0_s1/exchanges.jsonl:2304`).
- Conditions/limitations: group is optional. Use an original 2xx witness without group; default/SUT rejection oracle includes 400.
- Witness plan: GET /api/v2/tags without group against fresh identical seed state.

## swagger-petstore
Source root: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/swagger-petstore/`.
Exposure source: `08_experiments/E1_pilot/runs/swagger-petstore/20261114T092517Z_batch_184034_baseline_NONE_p0_s1/exchanges.jsonl`; `run.json` was complete, baseline, seed 1 (`exposure.json`, `runs.swagger-petstore`).

### petstore-drop-validation — DROP_VALIDATION
- Site: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/swagger-petstore/src/main/java/io/swagger/petstore/controller/OrderController.java:59`; exact before/after/file digest: `sites.json`, `petstore-drop-validation`.
- [H] Expected: IMPL / I-CRASH; signal: SERVER_ERROR.
- Operations: `POST /store/order`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/swagger-petstore.json:584`.
- Captured exposure: 103 requests, statuses `{"200": 30, "400": 44, "500": 29}`; first 2xx line `772`, first nonempty JSON 2xx line `772` (`exposure.json`, `swagger-petstore:POST /store/order`; `08_experiments/E1_pilot/runs/swagger-petstore/20261114T092517Z_batch_184034_baseline_NONE_p0_s1/exchanges.jsonl:771`).
- Conditions/limitations: Removing the explicit empty-order guard lets null reach OrderData.addOrder. Framework request validation may reject first: verify handler reachability before treating survival as an attribution miss.
- Witness plan: Empty order request; compare the original 400 with a mutant stack, and report framework-preempted if the handler is never invoked.

### petstore-wrong-status — WRONG_STATUS
- Site: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/swagger-petstore/src/main/java/io/swagger/petstore/controller/OrderController.java:34`; exact before/after/file digest: `sites.json`, `petstore-wrong-status`.
- [H] Expected: IMPL / I-RESP-CONTRACT; signal: none guaranteed under the current oracle.
- Operations: `GET /store/inventory`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/swagger-petstore.json:550`.
- Captured exposure: 23 requests, statuses `{"200": 15, "400": 8}`; first 2xx line `748`, first nonempty JSON 2xx line `748` (`exposure.json`, `swagger-petstore:GET /store/inventory`; `08_experiments/E1_pilot/runs/swagger-petstore/20261114T092517Z_batch_184034_baseline_NONE_p0_s1/exchanges.jsonl:748`).
- Conditions/limitations: default is declared without a schema. Thus 418 does not trigger UNDOCUMENTED_STATUS or RESPONSE_SCHEMA under this spec. A status-semantic negative control, not a conformance kill.
- Witness plan: GET /api/v3/store/inventory; record raw 200-to-418 delta without inventing an oracle failure.

### petstore-drop-null — DROP_NULL_CHECK
- Site: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/swagger-petstore/src/main/java/io/swagger/petstore/data/PetData.java:87`; exact before/after/file digest: `sites.json`, `petstore-drop-null`.
- [H] Expected: IMPL / I-CRASH; signal: SERVER_ERROR.
- Operations: `GET /pet/findByTags`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/swagger-petstore.json:244`.
- Captured exposure: 100 requests, statuses `{"200": 77, "400": 23}`; first 2xx line `309`, first nonempty JSON 2xx line `None` (`exposure.json`, `swagger-petstore:GET /pet/findByTags`; `08_experiments/E1_pilot/runs/swagger-petstore/20261114T092517Z_batch_184034_baseline_NONE_p0_s1/exchanges.jsonl:308`).
- Conditions/limitations: Needs a stored pet with null tags; default seeded lists may be non-null. State setup and Jackson null handling must be verified. Any propagated faults outside this operation need manual review.
- Witness plan: Create a valid named pet with photoUrls and tags:null (if accepted by intended contract), then findByTags; otherwise reject the witness as spec-invalid.

### petstore-response-field — RESP_FIELD
- Site: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/swagger-petstore/src/main/java/io/swagger/petstore/model/Pet.java:55`; exact before/after/file digest: `sites.json`, `petstore-response-field`.
- [H] Expected: IMPL / I-RESP-CONTRACT; signal: RESPONSE_SCHEMA.
- Operations: `GET /pet/{petId}`, `GET /pet/findByStatus`, `GET /pet/findByTags`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/swagger-petstore.json:306`, `08_experiments/_external/emb/openapi-swagger/swagger-petstore.json:179`, `08_experiments/_external/emb/openapi-swagger/swagger-petstore.json:244`, `08_experiments/_external/emb/openapi-swagger/swagger-petstore.json:1147`.
- Captured exposure: 57 requests, statuses `{"400": 17, "404": 40}`; first 2xx line `None`, first nonempty JSON 2xx line `None` (`exposure.json`, `swagger-petstore:GET /pet/{petId}`; `08_experiments/E1_pilot/runs/swagger-petstore/20261114T092517Z_batch_184034_baseline_NONE_p0_s1/exchanges.jsonl:408`).
- Captured exposure: 100 requests, statuses `{"200": 12, "400": 88}`; first 2xx line `210`, first nonempty JSON 2xx line `210` (`exposure.json`, `swagger-petstore:GET /pet/findByStatus`; `08_experiments/E1_pilot/runs/swagger-petstore/20261114T092517Z_batch_184034_baseline_NONE_p0_s1/exchanges.jsonl:208`).
- Captured exposure: 100 requests, statuses `{"200": 77, "400": 23}`; first 2xx line `309`, first nonempty JSON 2xx line `None` (`exposure.json`, `swagger-petstore:GET /pet/findByTags`; `08_experiments/E1_pilot/runs/swagger-petstore/20261114T092517Z_batch_184034_baseline_NONE_p0_s1/exchanges.jsonl:308`).
- Conditions/limitations: Pet.name is required. Force Accept:application/json and a nonempty successful Pet result. Verify Inflector/Jackson honors WRITE_ONLY; XML is outside this witness. Input setters remain present.
- Witness plan: GET a seeded pet that returned JSON 200/name in the control; repeat identical request against the mutant.

### petstore-reject-valid — REJECT_VALID
- Site: `08_experiments/_external/emb/jdk_8_maven/cs/rest/original/swagger-petstore/src/main/java/io/swagger/petstore/controller/PetController.java:71`; exact before/after/file digest: `sites.json`, `petstore-reject-valid`.
- [H] Expected: IMPL / I-REJECT-VALID; signal: VALID_REJECTED.
- Operations: `GET /pet/{petId}`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/swagger-petstore.json:306`.
- Captured exposure: 57 requests, statuses `{"400": 17, "404": 40}`; first 2xx line `None`, first nonempty JSON 2xx line `None` (`exposure.json`, `swagger-petstore:GET /pet/{petId}`; `08_experiments/E1_pilot/runs/swagger-petstore/20261114T092517Z_batch_184034_baseline_NONE_p0_s1/exchanges.jsonl:408`).
- Conditions/limitations: Use a positive seeded ID with a control 200 and JSON Accept; request-side int64 format coverage must not be confused with a valid resource witness.
- Witness plan: Replay the control's successful GET /api/v3/pet/<positive ID> as an actual HTTP request to both SUTs.

## market
Source root: `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/`.
Exposure source: `08_experiments/E1_pilot/runs/market/20261114T104059Z_batch_339514_baseline_NONE_p0_s1/exchanges.jsonl`; `run.json` was complete, baseline, seed 1 (`exposure.json`, `runs.market`).

### market-drop-validation — DROP_VALIDATION
- Site: `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/market-rest/src/main/java/market/rest/CustomerRestController.java:52`; exact before/after/file digest: `sites.json`, `market-drop-validation`.
- [H] Expected: IMPL / I-ACCEPT-INVALID; signal: INVALID_ACCEPTED, SERVER_ERROR.
- Operations: `POST /register`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/market.json:540`.
- Captured exposure: 37 requests, statuses `{"406": 6, "500": 31}`; first 2xx line `None`, first nonempty JSON 2xx line `None` (`exposure.json`, `market:POST /register`; `08_experiments/E1_pilot/runs/market/20261114T104059Z_batch_339514_baseline_NONE_p0_s1/exchanges.jsonl:1103`).
- Conditions/limitations: DTO validation is removed, but domain/service validation and persistence may reject independently. Need an original 4xx and mutant 2xx for a spec-invalid witness, or a new causal 5xx classified I-CRASH instead.
- Witness plan: Use a fresh unique email and an invalid required request field; check remaining validators and the unchanged original schema first.

### market-wrong-status — WRONG_STATUS
- Site: `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/market-rest/src/main/java/market/rest/ProductsRestController.java:37`; exact before/after/file digest: `sites.json`, `market-wrong-status`.
- [H] Expected: IMPL / I-RESP-CONTRACT; signal: UNDOCUMENTED_STATUS.
- Operations: `GET /products`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/market.json:469`.
- Captured exposure: 1 requests, statuses `{"200": 1}`; first 2xx line `1002`, first nonempty JSON 2xx line `1002` (`exposure.json`, `market:GET /products`; `08_experiments/E1_pilot/runs/market/20261114T104059Z_batch_339514_baseline_NONE_p0_s1/exchanges.jsonl:1002`).
- Conditions/limitations: GET products documents 200/401/403/404 without default. Existing response-schema gaps remain baseline defects; only injected 418 is the expected new signal. Verify HATEOAS method-link generation compiles with ResponseEntity return type.
- Witness plan: GET /products with the same runtime user fixture and JSON Accept.

### market-drop-null — DROP_NULL_CHECK
- Site: `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/market-rest/src/main/java/market/rest/ProductsRestController.java:60`; exact before/after/file digest: `sites.json`, `market-drop-null`.
- [H] Expected: IMPL / I-CRASH; signal: SERVER_ERROR.
- Operations: `GET /products/{productId}`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/market.json:501`.
- Captured exposure: 100 requests, statuses `{"404": 44, "500": 56}`; first 2xx line `None`, first nonempty JSON 2xx line `None` (`exposure.json`, `market:GET /products/{productId}`; `08_experiments/E1_pilot/runs/market/20261114T104059Z_batch_339514_baseline_NONE_p0_s1/exchanges.jsonl:1003`).
- Conditions/limitations: Absent Optional now throws NoSuchElementException rather than mapped UnknownEntityException/404. Verify the missing-ID control and the stack; successful resources retain the map chain.
- Witness plan: Use a control request with 404 for a spec-valid missing product ID; repeat in the mutant.

### market-response-field — RESP_FIELD
- Site: `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/market-core/src/main/java/market/dto/ProductDTO.java:63`; exact before/after/file digest: `sites.json`, `market-response-field`.
- [H] Expected: IMPL / I-RESP-CONTRACT; signal: RESPONSE_SCHEMA.
- Operations: `GET /products`, `GET /products/{productId}`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/market.json:469`, `08_experiments/_external/emb/openapi-swagger/market.json:501`, `08_experiments/_external/emb/openapi-swagger/market.json:808`.
- Captured exposure: 1 requests, statuses `{"200": 1}`; first 2xx line `1002`, first nonempty JSON 2xx line `1002` (`exposure.json`, `market:GET /products`; `08_experiments/E1_pilot/runs/market/20261114T104059Z_batch_339514_baseline_NONE_p0_s1/exchanges.jsonl:1002`).
- Captured exposure: 100 requests, statuses `{"404": 44, "500": 56}`; first 2xx line `None`, first nonempty JSON 2xx line `None` (`exposure.json`, `market:GET /products/{productId}`; `08_experiments/E1_pilot/runs/market/20261114T104059Z_batch_339514_baseline_NONE_p0_s1/exchanges.jsonl:1003`).
- Conditions/limitations: price is required in ProductDTO. Select nonempty JSON product responses and inspect required-price messages separately from existing _links schema failures.
- Witness plan: Reuse successful product listing/detail requests with non-null prices in the control.

### market-reject-valid — REJECT_VALID
- Site: `08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market/market-rest/src/main/java/market/rest/ProductsRestController.java:56`; exact before/after/file digest: `sites.json`, `market-reject-valid`.
- [H] Expected: IMPL / I-REJECT-VALID; signal: UNDOCUMENTED_STATUS, VALID_REJECTED.
- Operations: `GET /products/{productId}`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/market.json:501`.
- Captured exposure: 100 requests, statuses `{"404": 44, "500": 56}`; first 2xx line `None`, first nonempty JSON 2xx line `None` (`exposure.json`, `market:GET /products/{productId}`; `08_experiments/E1_pilot/runs/market/20261114T104059Z_batch_339514_baseline_NONE_p0_s1/exchanges.jsonl:1003`).
- Conditions/limitations: The existing CustomNotValidException mapper returns 406. UNDOCUMENTED_STATUS should appear; VALID_REJECTED additionally needs the code-justified market SUT oracle (400,406,422). Generic 400/422 will not recognize 406 as rejection.
- Witness plan: Use an existing positive product ID; check control 200 and the 406 handler outcome; report default and market-SUT oracles separately.

## cwa-verification
Source root: `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/`.
Exposure source: `08_experiments/E1_pilot/runs/cwa-verification/20261114T103253Z_batch_321562_baseline_NONE_p0_s1/exchanges.jsonl`; `run.json` was complete, baseline, seed 1 (`exposure.json`, `runs.cwa-verification`).

### cwa-drop-validation — DROP_VALIDATION
- Site: `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/controller/ExternalTokenController.java:80`; exact before/after/file digest: `sites.json`, `cwa-drop-validation`.
- [H] Expected: IMPL / I-CRASH; signal: SERVER_ERROR, INVALID_ACCEPTED.
- Operations: `POST /version/v1/registrationToken`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/cwa-verification.json:114`.
- Captured exposure: 8 requests, statuses `{"400": 8}`; first 2xx line `None`, first nonempty JSON 2xx line `None` (`exposure.json`, `cwa-verification:POST /version/v1/registrationToken`; `08_experiments/E1_pilot/runs/cwa-verification/20261114T103253Z_batch_321562_baseline_NONE_p0_s1/exchanges.jsonl:166`).
- Conditions/limitations: An empty object bypasses bean validation and reaches switch(null), causing 500. Other invalid GUID inputs can be stored locally. The readiness probe uses a different DTO/controller and remains unchanged.
- Witness plan: POST {} JSON to registrationToken; original bean validation should return 400 and the mutant should reach a null keyType switch.

### cwa-wrong-status — WRONG_STATUS
- Site: `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/controller/ExternalTokenController.java:97`; exact before/after/file digest: `sites.json`, `cwa-wrong-status`.
- [H] Expected: IMPL / I-RESP-CONTRACT; signal: UNDOCUMENTED_STATUS.
- Operations: `POST /version/v1/registrationToken`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/cwa-verification.json:114`.
- Captured exposure: 8 requests, statuses `{"400": 8}`; first 2xx line `None`, first nonempty JSON 2xx line `None` (`exposure.json`, `cwa-verification:POST /version/v1/registrationToken`; `08_experiments/E1_pilot/runs/cwa-verification/20261114T103253Z_batch_321562_baseline_NONE_p0_s1/exchanges.jsonl:166`).
- Conditions/limitations: GUID registration branch only; 418 is undocumented and needs no missing test-result backend. A duplicate GUID would change 400 too, so prefer a fresh valid GUID/control 201 witness.
- Witness plan: POST a fresh valid GUID registration request against clean control and mutant states.

### cwa-drop-null — DROP_NULL_CHECK
- Site: `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/controller/InternalTanController.java:120`; exact before/after/file digest: `sites.json`, `cwa-drop-null`.
- [H] Expected: IMPL / I-CRASH; signal: SERVER_ERROR.
- Operations: `POST /version/v1/tan/verify`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/cwa-verification.json:200`.
- Captured exposure: 100 requests, statuses `{"400": 44, "404": 56}`; first 2xx line `None`, first nonempty JSON 2xx line `None` (`exposure.json`, `cwa-verification:POST /version/v1/tan/verify`; `08_experiments/E1_pilot/runs/cwa-verification/20261114T103253Z_batch_321562_baseline_NONE_p0_s1/exchanges.jsonl:270`).
- Conditions/limitations: Valid-format but absent TAN reaches Optional.get and 500 instead of the control 404. Neither downstream test-result service nor successful TAN generation is needed. Empty-body readiness still fails binding before this code.
- Witness plan: POST a valid-format UUID v4 TAN absent from the fresh DB; compare control 404 and mutant stack.

### cwa-response-field — RESP_FIELD
- Site: `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/model/RegistrationToken.java:50`; exact before/after/file digest: `sites.json`, `cwa-response-field`.
- [H] Expected: IMPL / I-RESP-CONTRACT; signal: RESPONSE_SCHEMA.
- Operations: `POST /version/v1/registrationToken`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/cwa-verification.json:114`, `08_experiments/_external/emb/openapi-swagger/cwa-verification.json:251`.
- Captured exposure: 8 requests, statuses `{"400": 8}`; first 2xx line `None`, first nonempty JSON 2xx line `None` (`exposure.json`, `cwa-verification:POST /version/v1/registrationToken`; `08_experiments/E1_pilot/runs/cwa-verification/20261114T103253Z_batch_321562_baseline_NONE_p0_s1/exchanges.jsonl:166`).
- Conditions/limitations: RegistrationToken.registrationToken is required. WRITE_ONLY is intended to retain input binding for /tan and /testresult; verify Lombok/Jackson merged-property behavior and retain any additional observed effects for review.
- Witness plan: Generate a token with a fresh valid GUID; expect required-registrationToken failure in its JSON response.

### cwa-reject-valid — REJECT_VALID
- Site: `08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification/controller/ExternalTokenController.java:91`; exact before/after/file digest: `sites.json`, `cwa-reject-valid`.
- [H] Expected: IMPL / I-REJECT-VALID; signal: VALID_REJECTED.
- Operations: `POST /version/v1/registrationToken`.
- Original contract evidence (operation/response schema): `08_experiments/_external/emb/openapi-swagger/cwa-verification.json:114`.
- Captured exposure: 8 requests, statuses `{"400": 8}`; first 2xx line `None`, first nonempty JSON 2xx line `None` (`exposure.json`, `cwa-verification:POST /version/v1/registrationToken`; `08_experiments/E1_pilot/runs/cwa-verification/20261114T103253Z_batch_321562_baseline_NONE_p0_s1/exchanges.jsonl:166`).
- Conditions/limitations: Fresh valid GUID would produce control 201; the new guard returns 400 through the explicit VerificationServerException handler. Use a clean DB and no fake header.
- Witness plan: Fresh 64-hex hashed GUID with keyType GUID; establish a control 201 witness first.

## First E5 batch: ten proposed mutants (2–3 per SUT)

All choices remain [H] pending compilation, controlled HTTP witnesses and source/
image verification. Exact site IDs below can be passed to `codemut.py --site`.
The original subset is also `pilot=true` in `sites.json`; the two T25 v2
additions below are separately pilot-enabled.

| SUT | First sites | Why these before the alternatives |
|---|---|---|
| scout-api | scout-wrong-status; scout-drop-null; scout-reject-valid | roles had a captured 200; tags had 95 captured 200s, including absent optional query inputs. Expect distinct status/crash/rejection effects; repeat the same-state witnesses to separate existing faults (`exposure.json`, scout rows). |
| swagger-petstore | petstore-response-field; petstore-reject-valid | A nonempty JSON findByStatus response carries required name. getPetById is reached, but this selected negative-data control has no 200 there: establish a clean seeded-pet 200 before calling a later 400 a reject-valid kill (`exposure.json`, pet rows). |
| market | market-wrong-status; market-drop-null; market-response-field | The listing has a nonempty 200 with price, while product detail has 44 captured 404s. These avoid inventing a valid registration fixture and permit status, absence and field witnesses (`exposure.json`, market rows). |
| cwa-verification | cwa-drop-validation; cwa-drop-null | Registration binding and absent-TAN verification are reached with 400/404. Neither requires the missing test-result server or a successful token response. Registration's selected baseline has zero 2xx, so defer its wrong-status/response-field proposals until a manual GUID-control 201 witness exists (`exposure.json`, cwa rows). |

For field mutants, force JSON and nonempty response objects. For crash mutants,
save the new stack site as well as status. For every mutant, retain invalid or
unexposed candidates in the selection ledger; do not exclude survivors after
looking at attribution outcomes. Compile-invalid, equivalent/oracle-blind,
unexposed, killed and flaky are separate outcomes. The injected site is code-side
ground truth; causal exposure and the observed L1/L2 still require independent
review (`sites.json`, each site's `conditions`; codebook §5 and §10).

## T25 v2 sites

These are appended pilot proposals, preserving the original 20 entries and
historical failure records (`sites.json`, `market-response-field-v2` and
`petstore-reject-valid-v2`; `COORDINATOR_NOTES.md`, Build results;
`E5_RESULTS.md`, §3b).

| Site | Source edit and affected operations | Expected signal and evidence |
|---|---|---|
| market-response-field-v2 | `market-rest/src/main/java/market/RestConfig.java:13`: add a Jackson builder customizer and a WRITE_ONLY price getter mix-in for ProductDTO. GET `/products` and GET `/products/{productId}`. | ⚠️ Expected IMPL / I-RESP-CONTRACT / RESPONSE_SCHEMA for absent required price. POM compile path: market-rest → starter-web 2.4.3 → starter-json 2.4.3 → jackson-databind 2.11.4 → jackson-annotations 2.11.4. Snapshots/line citations: `09_collab/logs/T25_scratch/pom_evidence.json`; `09_collab/reports/T25_report.md`, Market evidence. |
| petstore-reject-valid-v2 | `src/main/java/io/swagger/petstore/controller/UserController.java:103`: reject null username in loginUser. GET `/user/login`; username is optional in the unchanged OAS. | ⚠️ Expected IMPL / I-REJECT-VALID / VALID_REJECTED. All 48 captured login requests across 24 saved runs are valid, omit username and return 200; no 400/422 or saved VALID_REJECTED. Counts: `09_collab/logs/T25_scratch/petstore_operation_counts.csv`, GET `/user/login` rows; exact source lines: `petstore_login_witnesses.json` in that directory. |

Witnesses: require the same request and state to produce control price-present
JSON versus mutant price-absent JSON, or control login 200 versus mutant 400.
Keep pre-existing product `_links` and login response-format/header problems
separate. The login evidence has only two exchanges per run and one empty-query
shape; 48 is repeated exposure, not input diversity. ⚠️ A new rejection
fingerprint should exceed the saved noise floor, but only fresh v2 pair/noise
runs can establish the measured result. Build and runtime mapper behavior are
unverified (`sites.json`, both v2 `conditions` and `witness_plan`;
`09_collab/reports/T25_report.md`, limitations).
