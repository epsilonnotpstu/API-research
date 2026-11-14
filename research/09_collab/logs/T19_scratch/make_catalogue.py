"""Read source/spec/run data and write the reviewed E5 site registry and exposure evidence."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path.cwd()
OUT = BASE / "08_experiments/E5_codemut"
EMB = BASE / "08_experiments/_external/emb"
ROOTS = {
    "scout-api": "jdk_8_maven/cs/rest/original/scout-api",
    "swagger-petstore": "jdk_8_maven/cs/rest/original/swagger-petstore",
    "market": "jdk_11_maven/cs/rest-gui/market",
    "cwa-verification": "jdk_11_maven/cs/rest/cwa-verification-server",
}
SC = "api/src/main/java/se/devscout/scoutapi/resource/"
SD = "data-access/src/main/java/se/devscout/scoutapi/"
PC = "src/main/java/io/swagger/petstore/"
MR = "market-rest/src/main/java/market/rest/"
MC = "market-core/src/main/java/market/"
CW = "src/main/java/app/coronawarn/verification/"
sites = []


def add(sut, sid, op, file, before, after, operations, l2, signals, condition, witness, pilot=False):
    data = (EMB / ROOTS[sut] / file).read_bytes()
    text = data.decode()
    assert text.count(before) == 1, (sid, text.count(before))
    line = text[:text.index(before)].count("\n") + 1
    sites.append({"site_id": sid, "sut": sut, "operator": op, "file": file, "line": line,
                  "before": before, "after": after, "operations": [{"path": p, "method": m} for p, m in operations],
                  "expected_L1": "IMPL", "expected_L2": l2, "expected_conformance_signal": signals,
                  "source_sha256": hashlib.sha256(data).hexdigest(), "conditions": condition,
                  "witness_plan": witness, "pilot": pilot,
                  "evidence": f"08_experiments/_external/emb/{ROOTS[sut]}/{file}:{line}"})


add("scout-api", "scout-drop-validation", "DROP_VALIDATION", SC + "ActivityResource.java",
    'throw new WebApplicationException("Could not understand the request. Perhaps you sent text instead of integers?", Response.Status.BAD_REQUEST);',
    'return java.util.Collections.emptyList();', [("/v2/activities", "get")], "I-ACCEPT-INVALID", [],
    "Latent under current spec: comma-separated numeric filters are declared strings. Removing the explicit parser guard changes code intent, but INVALID_ACCEPTED needs an encoded spec constraint. Exclude from detection denominator until a non-spec-changing oracle/witness is justified.",
    "Send ages=not-an-integer to demonstrate the removed guard; report semantic-only survival if original spec accepts it.")
before = '''public RolesView roles() {
        return new RolesView(
                Stream.of(Permission.values()).collect(Collectors.toMap(Enum::name, Permission::getLevel)),
                Stream.of(Role.values()).collect(Collectors.toMap(Enum::name, Role::getLevel))
        );
    }'''
after = before.replace("public RolesView", "public Response").replace("return new RolesView(", "return Response.status(418).entity(new RolesView(").replace("        );", "        )).build();")
add("scout-api", "scout-wrong-status", "WRONG_STATUS", SC + "SystemResource.java", before, after,
    [("/v1/system/roles", "get")], "I-RESP-CONTRACT", ["UNDOCUMENTED_STATUS"],
    "This operation declares only 200; 418 has no default fallback. Confirm body unchanged and original 200 witness.",
    "GET /api/v1/system/roles with the same headers against clean baseline and mutant.", True)
add("scout-api", "scout-drop-null", "DROP_NULL_CHECK", SD + "dao/TagDao.java",
    "if (name != null) {", "if (true) {", [("/v2/tags", "get")], "I-CRASH", ["SERVER_ERROR"],
    "Absent optional name reaches name.toUpperCase(); original skips the filter. Verify original request succeeds; group/name mutations can share an existing SERVER_ERROR fingerprint.",
    "GET /api/v2/tags without name; preserve optional attrs behavior and inspect the new stack.", True)
add("scout-api", "scout-response-field", "RESP_FIELD", SC + "SystemResource.java",
    "public Map<String, Integer> getPermissionLevels() {",
    "@com.fasterxml.jackson.annotation.JsonProperty(access = com.fasterxml.jackson.annotation.JsonProperty.Access.WRITE_ONLY)\n        public Map<String, Integer> getPermissionLevels() {",
    [("/v1/system/roles", "get")], "I-RESP-CONTRACT", [],
    "Dropping permission_levels is invisible to the current default schema because neither RolesView field is required. Strict additional-property policy does not detect an absent optional field. Keep as an oracle-blind negative control, not a claimed killed mutant.",
    "Compare raw JSON key presence, separately from conformance. Do not strengthen the test spec.")
add("scout-api", "scout-reject-valid", "REJECT_VALID", SC + "TagResource.java",
    "return okResponse(dao.find(group, name, minActivitiesCount), attrs);",
    'if (group == null) { throw new javax.ws.rs.BadRequestException("E5 requires optional group"); }\n        return okResponse(dao.find(group, name, minActivitiesCount), attrs);',
    [("/v2/tags", "get")], "I-REJECT-VALID", ["VALID_REJECTED"],
    "group is optional. Use an original 2xx witness without group; default/SUT rejection oracle includes 400.",
    "GET /api/v2/tags without group against fresh identical seed state.", True)

add("swagger-petstore", "petstore-drop-validation", "DROP_VALIDATION", PC + "controller/OrderController.java",
    "if (order == null) {", "if (false) {", [("/store/order", "post")], "I-CRASH", ["SERVER_ERROR"],
    "Removing the explicit empty-order guard lets null reach OrderData.addOrder. Framework request validation may reject first: verify handler reachability before treating survival as an attribution miss.",
    "Empty order request; compare the original 400 with a mutant stack, and report framework-preempted if the handler is never invoked.")
add("swagger-petstore", "petstore-wrong-status", "WRONG_STATUS", PC + "controller/OrderController.java",
    "public ResponseContext getInventory(final RequestContext request) {\n        return new ResponseContext()",
    "public ResponseContext getInventory(final RequestContext request) {\n        return new ResponseContext().status(418)",
    [("/store/inventory", "get")], "I-RESP-CONTRACT", [],
    "default is declared without a schema. Thus 418 does not trigger UNDOCUMENTED_STATUS or RESPONSE_SCHEMA under this spec. A status-semantic negative control, not a conformance kill.",
    "GET /api/v3/store/inventory; record raw 200-to-418 delta without inventing an oracle failure.")
add("swagger-petstore", "petstore-drop-null", "DROP_NULL_CHECK", PC + "data/PetData.java",
    "if (null != pet.getTags()) {", "if (true) {", [("/pet/findByTags", "get")], "I-CRASH", ["SERVER_ERROR"],
    "Needs a stored pet with null tags; default seeded lists may be non-null. State setup and Jackson null handling must be verified. Any propagated faults outside this operation need manual review.",
    "Create a valid named pet with photoUrls and tags:null (if accepted by intended contract), then findByTags; otherwise reject the witness as spec-invalid.")
add("swagger-petstore", "petstore-response-field", "RESP_FIELD", PC + "model/Pet.java",
    "public String getName() {",
    "@com.fasterxml.jackson.annotation.JsonProperty(access = com.fasterxml.jackson.annotation.JsonProperty.Access.WRITE_ONLY)\n    public String getName() {",
    [("/pet/{petId}", "get"), ("/pet/findByStatus", "get"), ("/pet/findByTags", "get")],
    "I-RESP-CONTRACT", ["RESPONSE_SCHEMA"],
    "Pet.name is required. Force Accept:application/json and a nonempty successful Pet result. Verify Inflector/Jackson honors WRITE_ONLY; XML is outside this witness. Input setters remain present.",
    "GET a seeded pet that returned JSON 200/name in the control; repeat identical request against the mutant.", True)
add("swagger-petstore", "petstore-reject-valid", "REJECT_VALID", PC + "controller/PetController.java",
    "public ResponseContext getPetById(final RequestContext request, final Long petId) {",
    'public ResponseContext getPetById(final RequestContext request, final Long petId) {\n        if (petId != null && petId.longValue() > 0L) { throw new javax.ws.rs.BadRequestException("E5 rejects positive pet IDs"); }',
    [("/pet/{petId}", "get")], "I-REJECT-VALID", ["VALID_REJECTED"],
    "Use a positive seeded ID with a control 200 and JSON Accept; request-side int64 format coverage must not be confused with a valid resource witness.",
    "Replay the control's successful GET /api/v3/pet/<positive ID> as an actual HTTP request to both SUTs.", True)

add("market", "market-drop-validation", "DROP_VALIDATION", MR + "CustomerRestController.java",
    "public UserDTO createCustomer(@RequestBody @Valid UserDTO user) {",
    "public UserDTO createCustomer(@RequestBody UserDTO user) {", [("/register", "post")],
    "I-ACCEPT-INVALID", ["INVALID_ACCEPTED", "SERVER_ERROR"],
    "DTO validation is removed, but domain/service validation and persistence may reject independently. Need an original 4xx and mutant 2xx for a spec-invalid witness, or a new causal 5xx classified I-CRASH instead.",
    "Use a fresh unique email and an invalid required request field; check remaining validators and the unchanged original schema first.")
before = '''public Collection<ProductDTO> getProducts() {
		return productService.findAll().stream()
			.sorted(Comparator.comparing(Product::getId))
			.map(productAssembler::toModel)
			.peek(this::addSelfLink)
			.collect(Collectors.toList());
	}'''
after = before.replace("public Collection<ProductDTO>", "public org.springframework.http.ResponseEntity<Collection<ProductDTO>>").replace("return productService.findAll()", "return org.springframework.http.ResponseEntity.status(418).body(productService.findAll()").replace(".collect(Collectors.toList());", ".collect(Collectors.toList()));")
add("market", "market-wrong-status", "WRONG_STATUS", MR + "ProductsRestController.java", before, after,
    [("/products", "get")], "I-RESP-CONTRACT", ["UNDOCUMENTED_STATUS"],
    "GET products documents 200/401/403/404 without default. Existing response-schema gaps remain baseline defects; only injected 418 is the expected new signal. Verify HATEOAS method-link generation compiles with ResponseEntity return type.",
    "GET /products with the same runtime user fixture and JSON Accept.", True)
add("market", "market-drop-null", "DROP_NULL_CHECK", MR + "ProductsRestController.java",
    ".orElseThrow(() -> new UnknownEntityException(ProductDTO.class, productId));", ".get();",
    [("/products/{productId}", "get")], "I-CRASH", ["SERVER_ERROR"],
    "Absent Optional now throws NoSuchElementException rather than mapped UnknownEntityException/404. Verify the missing-ID control and the stack; successful resources retain the map chain.",
    "Use a control request with 404 for a spec-valid missing product ID; repeat in the mutant.", True)
add("market", "market-response-field", "RESP_FIELD", MC + "dto/ProductDTO.java",
    "public Double getPrice() {",
    "@com.fasterxml.jackson.annotation.JsonProperty(access = com.fasterxml.jackson.annotation.JsonProperty.Access.WRITE_ONLY)\n\tpublic Double getPrice() {",
    [("/products", "get"), ("/products/{productId}", "get")], "I-RESP-CONTRACT", ["RESPONSE_SCHEMA"],
    "price is required in ProductDTO. Select nonempty JSON product responses and inspect required-price messages separately from existing _links schema failures.",
    "Reuse successful product listing/detail requests with non-null prices in the control.", True)
add("market", "market-reject-valid", "REJECT_VALID", MR + "ProductsRestController.java",
    "public ProductDTO getProduct(@PathVariable long productId) {",
    'public ProductDTO getProduct(@PathVariable long productId) {\n\t\tif (productId > 0L) { throw new market.exception.CustomNotValidException("Error.Validation.Parameter", "ProductDTO", "productId"); }',
    [("/products/{productId}", "get")], "I-REJECT-VALID", ["UNDOCUMENTED_STATUS", "VALID_REJECTED"],
    "The existing CustomNotValidException mapper returns 406. UNDOCUMENTED_STATUS should appear; VALID_REJECTED additionally needs the code-justified market SUT oracle (400,406,422). Generic 400/422 will not recognize 406 as rejection.",
    "Use an existing positive product ID; check control 200 and the 406 handler outcome; report default and market-SUT oracles separately.")

add("cwa-verification", "cwa-drop-validation", "DROP_VALIDATION", CW + "controller/ExternalTokenController.java",
    "@RequestBody @Valid RegistrationTokenRequest request,", "@RequestBody RegistrationTokenRequest request,",
    [("/version/v1/registrationToken", "post")], "I-CRASH", ["SERVER_ERROR", "INVALID_ACCEPTED"],
    "An empty object bypasses bean validation and reaches switch(null), causing 500. Other invalid GUID inputs can be stored locally. The readiness probe uses a different DTO/controller and remains unchanged.",
    "POST {} JSON to registrationToken; original bean validation should return 400 and the mutant should reach a null keyType switch.")
add("cwa-verification", "cwa-wrong-status", "WRONG_STATUS", CW + "controller/ExternalTokenController.java",
    "deferredResult.setResult(responseEntity);", "deferredResult.setResult(ResponseEntity.status(418).body(responseEntity.getBody()));",
    [("/version/v1/registrationToken", "post")], "I-RESP-CONTRACT", ["UNDOCUMENTED_STATUS"],
    "GUID registration branch only; 418 is undocumented and needs no missing test-result backend. A duplicate GUID would change 400 too, so prefer a fresh valid GUID/control 201 witness.",
    "POST a fresh valid GUID registration request against clean control and mutant states.", True)
before = '''.orElseGet(() -> {
        log.info("The Tan is invalid.");
        throw new VerificationServerException(HttpStatus.NOT_FOUND, "No Tan found or Tan is invalid");
      });'''
add("cwa-verification", "cwa-drop-null", "DROP_NULL_CHECK", CW + "controller/InternalTanController.java", before, ".get();",
    [("/version/v1/tan/verify", "post")], "I-CRASH", ["SERVER_ERROR"],
    "Valid-format but absent TAN reaches Optional.get and 500 instead of the control 404. Neither downstream test-result service nor successful TAN generation is needed. Empty-body readiness still fails binding before this code.",
    "POST a valid-format UUID v4 TAN absent from the fresh DB; compare control 404 and mutant stack.", True)
add("cwa-verification", "cwa-response-field", "RESP_FIELD", CW + "model/RegistrationToken.java",
    "private String registrationToken;",
    "@com.fasterxml.jackson.annotation.JsonProperty(access = com.fasterxml.jackson.annotation.JsonProperty.Access.WRITE_ONLY)\n  private String registrationToken;",
    [("/version/v1/registrationToken", "post")], "I-RESP-CONTRACT", ["RESPONSE_SCHEMA"],
    "RegistrationToken.registrationToken is required. WRITE_ONLY is intended to retain input binding for /tan and /testresult; verify Lombok/Jackson merged-property behavior and retain any additional observed effects for review.",
    "Generate a token with a fresh valid GUID; expect required-registrationToken failure in its JSON response.", True)
add("cwa-verification", "cwa-reject-valid", "REJECT_VALID", CW + "controller/ExternalTokenController.java",
    "switch (keyType) {",
    'if (keyType == app.coronawarn.verification.model.RegistrationTokenKeyType.GUID) { throw new app.coronawarn.verification.exception.VerificationServerException(HttpStatus.BAD_REQUEST, "E5 rejects valid GUID registration"); }\n    switch (keyType) {',
    [("/version/v1/registrationToken", "post")], "I-REJECT-VALID", ["VALID_REJECTED"],
    "Fresh valid GUID would produce control 201; the new guard returns 400 through the explicit VerificationServerException handler. Use a clean DB and no fake header.",
    "Fresh 64-hex hashed GUID with keyType GUID; establish a control 201 witness first.")

for site in sites:
    if site["site_id"].startswith("cwa-"):
        site["pilot"] = site["site_id"] in {"cwa-drop-validation", "cwa-drop-null"}

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "sites.json").write_text(json.dumps({"format": "codemut-sites-v1", "roots": ROOTS, "sites": sites}, indent=2) + "\n")

exposure = {"selection": "Latest lexically sorted complete seed-1 baseline present at T19 inspection; diagnostic and incomplete runs excluded.", "runs": {}, "operations": []}
for sut in ROOTS:
    candidates = []
    for p in (BASE / "08_experiments/E1_pilot/runs" / sut).glob("*/run.json"):
        meta = json.loads(p.read_text())
        if meta.get("complete") and meta.get("mode") == "baseline" and meta.get("seed") == 1:
            candidates.append((p.parent, meta))
    run, meta = sorted(candidates, key=lambda x: str(x[0]))[-1]
    log = run / "exchanges.jsonl"
    exposure["runs"][sut] = {"run_dir": str(run.relative_to(BASE)), "run_metadata_sha256": hashlib.sha256((run / "run.json").read_bytes()).hexdigest(), "exchanges_sha256": hashlib.sha256(log.read_bytes()).hexdigest(), "seed": 1, "complete": True, "base_path": meta["base_path"]}
    spec = json.loads((EMB / "openapi-swagger" / f"{sut}.json").read_text())
    # Compile route templates directly, avoiding imports of framework/SUT code.
    patterns = []
    for p, item in sorted(spec["paths"].items(), key=lambda item: (item[0].count("{"), -len(item[0]))):
        chunks = re.split(r"(\{[^{}]+\})", p)
        pattern = "^" + re.escape(meta["base_path"].rstrip("/")) + "".join("[^/]+" if c.startswith("{") else re.escape(c) for c in chunks) + "/?$"
        for m in item:
            if m in {"get", "post", "put", "delete", "patch", "options", "head", "trace"}:
                patterns.append((p, m, re.compile(pattern)))
    rows = {}
    for line, raw in enumerate(log.read_bytes().split(b"\n"), 1):
        if not raw.strip(): continue
        record = json.loads(raw); req = record.get("request", {}); resp = record.get("response") or {}
        for p, m, pattern in patterns:
            if req.get("method", "").lower() == m and pattern.fullmatch(req.get("path", "")):
                key = (p, m); row = rows.setdefault(key, {"evidence_id": f"{sut}:{m.upper()} {p}", "sut": sut, "path": p, "method": m, "requests": 0, "statuses": {}, "first_exchange": line, "first_2xx_exchange": None, "first_nonempty_2xx_exchange": None, "example_response_fields": [], "missing_query_2xx": {}})
                status = str(resp.get("status")); row["requests"] += 1; row["statuses"][status] = row["statuses"].get(status, 0) + 1
                if status.startswith("2"):
                    if row["first_2xx_exchange"] is None: row["first_2xx_exchange"] = line
                    try:
                        body = json.loads(resp.get("body", {}).get("text", ""))
                    except (ValueError, TypeError):
                        body = None
                    if isinstance(body, (list, dict)) and body and row["first_nonempty_2xx_exchange"] is None:
                        row["first_nonempty_2xx_exchange"] = line
                        example = body[0] if isinstance(body, list) else body
                        row["example_response_fields"] = sorted(example) if isinstance(example, dict) else []
                    for name in ("name", "group"):
                        if name not in req.get("query", {}): row["missing_query_2xx"].setdefault(name, line)
                break
    exposure["operations"].extend(rows[k] for k in sorted(rows))
(OUT / "exposure.json").write_text(json.dumps(exposure, indent=2) + "\n")
print("Reviewed sites:", len(sites), "Exposure rows:", len(exposure["operations"]))
