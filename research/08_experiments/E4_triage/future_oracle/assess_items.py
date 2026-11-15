#!/usr/bin/env python3
"""Materialize the manually reviewed T41 assessments; this is not a classifier.

Direction choices below are explicit review decisions, independent of the comparison
function. Evidence extraction/search is automated; semantic attribution is manual.
"""
import collections
import csv
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t41_miner", HERE / "mine_history.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

P = "src/main/java/io/swagger/petstore/"
C = "src/main/java/app/coronawarn/verification/"
R = "market-rest/src/main/java/market/"
D = "market-core/src/main/java/market/dto/"
PET_FIX = "9fb97b14d3c9d15d99aa8e3dbe323284cceb6bee"
CWA_FIX = "40bd3a829f42e50a1dd764b4fa657a427bf32ef6"
CWA_MIGRATION = "e8046d3a2a04475b95b8bf57d324ab8f8b0b4971"
MAPPING = {"spec_changed_to_match_code": {"SPEC", "SPEC_PARTIAL"}, "code_changed_to_match_spec": {"IMPL"}, "both_changed": {"BOTH"}}
UNCHECKABLE = {"P002", "P003", "P004", "P007", "P008", "P009", "P010", "P020", "P023", "P024", "P025", "P028", "P029", "P030", "P040", "P041"}
TRANSPORT = {"P037", "P039"}
PROBES = {"P001", "C001", "M001"}

# Each tuple: concrete proposition, HEAD state, exact source marker(s).
REVIEW = {
    "P005": ("POST /pet 200 response can omit required photoUrls after form creation sets its initialized list to null.", "PetData.createPet still calls setPhotoUrls(urls); Pet.photoUrls remains required in the YAML.", [(P+"data/PetData.java", "pet.setPhotoUrls(urls);"), (P+"model/Pet.java", "getPhotoUrls()")]),
    "P006": ("POST /pet returns 500 for JSON Pet with omitted optional id and some non-JSON submissions; nullable id reaches primitive/state comparisons (inferred cause).", "Pet.id remains optional and its primitive-long getId() still unboxes the nullable field; non-JSON throwing sites remain unresolved.", [(P+"model/Pet.java", "public long getId()"), (P+"data/PetData.java", "pets.get(i).getId() == pet.getId()")]),
    "P011": ("PUT /pet 200 response can omit required photoUrls after form creation supplies null URLs.", "The form overload, null URL assignment and required response field persist.", [(P+"controller/PetController.java", "public ResponseContext updatePet(final RequestContext request, final Long"), (P+"data/PetData.java", "pet.setPhotoUrls(urls);")]),
    "P012": ("PUT /pet returns 500 when optional Pet.id is absent; lookup unboxes the nullable id, while the contract does not require id.", "updatePet still passes pet.getId() to primitive-long getPetById; id is still optional in YAML.", [(P+"controller/PetController.java", "getPetById(pet.getId())"), (P+"data/PetData.java", "getPetById(final long")]),
    "P013": ("GET /pet/findByStatus 200 contains a stored Pet missing required photoUrls.", "The photoUrls factory/storage path and required Pet.photoUrls schema persist; making status required does not repair this response field.", [(P+"data/PetData.java", "pet.setPhotoUrls(urls);"), (P+"controller/PetController.java", "final List<Pet> petByStatus")]),
    "P014": ("GET /pet/findByStatus without status is schema-valid (optional, default available) but returns 400 No status provided.", "YAML now requires status; default available remains; the existing null guard still returns 400.", [(P+"controller/PetController.java", "if (status == null)")]),
    "P015": ("GET /pet/findByTags returns 400 for omitted/empty tags although tags is optional and its array has no minItems.", "YAML now requires tags; no minItems was added; null/empty-list guard remains.", [(P+"controller/PetController.java", "if (tags == null || tags.size() == 0)")]),
    "P018": ("POST /pet/{petId} accepts arbitrary query status and returns a Pet outside the response enum available/pending/sold; request status has no enum.", "updatePetWithForm still stores arbitrary status; request enum remains absent and Pet response enum remains.", [(P+"controller/PetController.java", "existingPet.setStatus(status);")]),
    "P019": ("POST /pet/{petId} rejects omitted optional name with 400 (63/66); three int64-overflow witnesses are checker false positives.", "Optional query name and the explicit name-null 400 guard persist; int64 format persists.", [(P+"controller/PetController.java", "if (name == null)")]),
    "P021": ("POST /pet/{petId}/uploadImage rejects missing optional request body/file with 400 (60/62); two numeric-id witnesses are checker false positives.", "The octet-stream request body remains optional and file-null guard remains; int64 format persists.", [(P+"controller/PetController.java", "if (file == null)")]),
    "P026": ("POST /store/order form submissions return 500; optional wrapper fields reach primitive createOrder parameters (inferred throwing site).", "Order form overload still forwards nullable wrappers into primitive-long/int/boolean factory parameters.", [(P+"controller/OrderController.java", "OrderData.createOrder(id, petId, quantity"), (P+"data/OrderData.java", "public static Order createOrder(final long")]),
    "P027": ("POST /store/order with no body is schema-valid because requestBody is optional but returns 400 No Order provided.", "requestBody remains optional; placeOrder still rejects a null Order with 400.", [(P+"controller/OrderController.java", "if (order == null)")]),
    "P031": ("POST /user returns 500 after an empty/nameless user enters shared storage; username is optional and equality dereferences it (inferred per-request cause).", "User.username remains optional; addUser still dereferences stored usernames without a null guard.", [(P+"data/UserData.java", "users.get(i).getUsername().equals(user.getUsername())")]),
    "P032": ("POST /user with absent optional request body returns 400 No User provided.", "requestBody remains optional; createUser still returns 400 for a null User.", [(P+"controller/UserController.java", "public ResponseContext createUser(final RequestContext request, final User user)")]),
    "P033": ("POST /user/createWithList returns 500 on shared users with missing optional username; username equality lacks null safety (inferred per-request cause).", "Optional username, list insertion and null-unsafe addUser comparisons persist.", [(P+"controller/UserController.java", "public ResponseContext createUsersWithListInput"), (P+"data/UserData.java", "users.get(i).getUsername().equals(user.getUsername())")]),
    "P034": ("POST /user/createWithList accepts an optional array body with no minItems in the schema, but rejects absent/empty lists with 400.", "The optional array still has no minItems; createUsersWithListInput still rejects null/empty arrays.", [(P+"controller/UserController.java", "public ResponseContext createUsersWithListInput")]),
    "P035": ("GET /user/login 200 advertises application/json string but sends an unquoted Logged in user session string, causing RESPONSE_PARSE.", "The handler still returns a raw session string through Util.getMediaType; JSON string response schema remains.", [(P+"controller/UserController.java", '.entity("Logged in user session: "')]),
    "P036": ("DELETE /user/{username} returns 500 when stored optional username is null and deletion calls equals on it (inferred per-request cause).", "User.username remains optional and deleteUser still dereferences it in removeIf.", [(P+"data/UserData.java", "users.removeIf(user -> user.getUsername().equals(username))")]),
    "P038": ("GET /user/{username} returns 500 when lookup traverses a stored null username and calls equals (inferred per-request cause).", "User.username remains optional and findUserByName still calls getUsername().equals(username).",
              [(P+"data/UserData.java", "if (user.getUsername().equals(username))")]),
    "P042": ("PUT /user/{username} returns 500 on shared storage containing missing optional username; lookup/update equality is null-unsafe (inferred per-request cause).", "Optional User.username and null-unsafe lookup/add/delete paths persist.", [(P+"controller/UserController.java", "public ResponseContext updateUser"), (P+"data/UserData.java", "if (user.getUsername().equals(username))")]),
    "P043": ("PUT /user/{username} rejects an absent optional User body with 400 (34/36); two remaining witnesses have unresolved validity.", "requestBody remains optional and updateUser still rejects a null User.", [(P+"controller/UserController.java", "public ResponseContext updateUser")]),
    "C002": ("POST /version/v1/registrationToken returns 400 for bodies allowed by stale spec: missing key/keyType and omitted key/keyDob validation constraints; seven witnesses also have illegal header controls.", "Checked-in api-docs now requires key/keyType and constrains keyDob; existing NotNull/Pattern annotations and handler rejection policy remain; conditional key constraints remain absent.", [(C+"model/RegistrationTokenRequest.java", "@NotNull"), (C+"model/RegistrationTokenRequest.java", "@Pattern(regexp"), (C+"validator/RegistrationTokenRequestValidator.java", "if (key == null || keyType == null)")]),
    "C005": ("POST /version/v1/tan/verify 404 is deliberately bodyless but the deployed generated spec requires an object response body (*/*).",
              "HEAD api-docs still declares an object for 404; VerificationExceptionHandler still returns ResponseEntity.status(...).build(). Other responses/headers were refreshed and Java imports migrated.", [(C+"controller/InternalTanController.java", '@ApiResponse(responseCode = "404"'), (C+"controller/VerificationExceptionHandler.java", "return ResponseEntity.status(exception.getHttpStatus()).build();")]),
}


def dump_csv(path, rows, columns=None):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns or list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def source_locator(sut, commit, path, marker):
    text = (HERE / "source_evidence" / sut / commit / (path + ".txt")).read_text()
    lines = text.splitlines()
    line = next((n for n, v in enumerate(lines, 1) if marker in v), None)
    assert line, (sut, path, marker)
    return commit + ":" + path + ":" + str(line)


def route_code(b):
    if b["sut"] == "swagger-petstore":
        route = b["template"]
        return [P + "controller/" + ("PetController.java" if route.startswith("/pet") else "OrderController.java" if route.startswith("/store") else "UserController.java")]
    if b["sut"] == "market":
        route = b["template"]
        klass = "Cart" if "/cart" in route else "Contacts" if "/contacts" in route else "Orders" if "/orders" in route else "Customer"
        return [R + "rest/" + klass + "RestController.java"]
    mapping = {"C002": "ExternalToken", "C003": "ExternalTan", "C004": "InternalTan", "C005": "InternalTan", "C006": "ExternalTestState"}
    return [C + "controller/" + mapping.get(b["item_id"], "InternalTan") + "Controller.java"]


def market_review(b):
    id, route, method, status = b["item_id"], b["template"], b["method"], b["status"]
    exception = R + "rest/exception/RestExceptionHandler.java"
    markers = [(exception, "@ExceptionHandler(Exception.class)")]
    if id in {"M003", "M005", "M007", "M012"}:
        proposition = f"{method} {route} returns validation 406, omitted from operation responses in the generated Swagger spec."
        state = "The same MethodArgumentNotValidException/CustomNotValidException 406 mappings, route validation annotations and springfox configuration remain; no HEAD spec was regenerated."
        markers = [(exception, "@ExceptionHandler(MethodArgumentNotValidException.class)"), (exception, "@ResponseStatus(HttpStatus.NOT_ACCEPTABLE)")]
    elif id in {"M009", "M010"}:
        proposition = f"GET {route} returns 500 for nonnumeric/out-of-int64 orderId binding; the generic exception handler maps input conversion errors to server errors."
        if id == "M010":
            proposition += " 500 is also undocumented."
        state = "Primitive-long orderId binding and generic 500 mapping remain; no targeted exception mapping or response annotation was added."
        markers += [(R+"rest/OrdersRestController.java", "@PathVariable long orderId")]
    else:
        proposition = f"{method} {route} returns 500 for malformed HAL _links array (advertised as input by the spec)"
        if id in {"M002", "M004"}:
            proposition += " and/or int32 quantity overflow"
        proposition += "; input parse errors reach the generic 500 handler."
        if b["kind"] == "UNDOCUMENTED_STATUS":
            proposition += " 500 is also omitted from operation responses."
        state = "Handler/DTO/RepresentationModel inheritance, generic 500 mapping and springfox configuration are unchanged; the generated HEAD document was not executed/exported."
        dto = "Cart" if "/cart" in route else "Contacts" if "/contacts" in route else "User"
        markers += [(D+dto+"DTO.java", "extends RepresentationModel")]
    return proposition, state, markers


def scope_for(b, markers):
    sut = b["sut"]
    spec_paths = ["src/main/resources/openapi.yaml"] if sut == "swagger-petstore" else ["api-docs.json"] if sut == "cwa-verification" else []
    code = set(route_code(b) + [p for p, _ in markers])
    if sut == "swagger-petstore":
        route = b["template"]
        name = "Pet" if route.startswith("/pet") else "Order" if route.startswith("/store") else "User"
        code |= {P+"model/"+name+".java", P+"data/"+name+"Data.java", P+"utils/Util.java"}
        config = ["pom.xml", "inflector.yaml"]
    elif sut == "cwa-verification":
        code |= {C+"controller/VerificationExceptionHandler.java", C+"config/RequestSizeLimitFilter.java", C+"service/AppSessionService.java", C+"service/TanService.java"}
        if b["item_id"] == "C002":
            code |= {C+"model/RegistrationTokenRequest.java", C+"validator/RegistrationTokenRequestValidator.java", C+"service/HashingService.java"}
        if b["item_id"] in {"C003", "C006"}:
            code |= {C+"model/RegistrationToken.java", C+"repository/VerificationAppSessionRepository.java"}
        if b["item_id"] == "C004":
            code.add(C+"model/AuthorizationToken.java")
        if b["item_id"] == "C005":
            code.add(C+"model/Tan.java")
        config = ["pom.xml"]
    else:
        code |= {R+"rest/exception/RestExceptionHandler.java", R+"RestConfig.java"}
        route = b['template']
        dtos = ['Cart', 'CartItem'] if '/cart' in route else ['Contacts'] if '/contacts' in route else ['Order'] if '/orders' in route else ['User']
        if route.endswith('/pay'):
            dtos.append('CreditCard')
        code |= {D+name+'DTO.java' for name in dtos}
        config = ["pom.xml", "market-core/pom.xml", "market-rest/pom.xml"]
    return {"spec_artifact_paths": spec_paths, "source_paths": sorted(code), "configuration_paths": config}


def main():
    anchors = json.loads((HERE / "anchors.json").read_text())
    items = json.loads((HERE / "baseline_evidence.json").read_text())
    output, details = [], {}
    for item in items:
        b = item["baseline"]
        id, sut = b["item_id"], b["sut"]
        a = anchors[sut]
        confidence = 2
        direction = "unchanged_at_head"
        note = "⚠️ Static target state only; no upstream code or server was executed. Absence of a matching fix does not establish intended behaviour."
        evidence_commits = []
        if id in REVIEW:
            prop, head_state, markers = REVIEW[id]
        elif sut == "market" and id != "M001":
            prop, head_state, markers = market_review(b)
        elif id in UNCHECKABLE:
            prop = f"{b['method']} {b['template']} response {b['status']}: REQUEST_UNCHECKABLE records inability to validate non-JSON/binary request encoding; it does not assert a SUT spec/code mismatch."
            head_state = "The route and corresponding media types remain in the source spec; this item is a checker-coverage diagnostic, not a developer-fix proposition."
            markers = []
            direction = "unclear"
        elif id in PROBES:
            prop = f"GET {b['template']} 400 is a null-byte capability/setup probe counted as an undocumented operation; no business-operation mismatch proposition."
            head_state = "No corresponding API operation is defined by the anchored source/configuration; container/probe behaviour at HEAD is unverified."
            markers = [("inflector.yaml", "swaggerUrl:")] if sut == "swagger-petstore" else [(R+"RestConfig.java", "new Docket(")] if sut == "market" else [(C+"config/OpenApiConfig.java", "public OpenAPI openApi()")]
            direction = "unclear"
        elif id in {"P016", "P017"}:
            prop = f"{b['method']} /pet/{{petId}} 400 rejects IDs outside int64 although the checker reports them schema-valid; declared int64 and Long binding agree."
            head_state = "The spec still uses integer/int64 and the controller still binds Long; the faulty validity predicate belongs to the local checker."
            markers = [(P+"controller/PetController.java", "final Long petId")]
            direction = "unclear"
        elif id == "P022" or id in TRANSPORT:
            prop = f"{b['method']} {b['template']} 400 is a pre-handler URI/header or percent-encoded-backslash rejection reported schema-valid; application mismatch validity is unresolved."
            head_state = "The corresponding API source remains; EMB uses added Tomcat bootstrap/dependencies while upstream uses Jetty. Exact container-policy behaviour at HEAD is unverified."
            markers = []
            direction = "unclear"
        elif id in {"C003", "C006"}:
            prop = f"POST {b['template']} 400 rejects syntactically valid registration tokens without an existing application session; documented stateful rejection is reported VALID_REJECTED."
            head_state = "Missing-session BAD_REQUEST logic remains in the controller; syntax validity alone does not establish a SUT mismatch."
            markers = [(route_code(b)[0], "getAppSessionByToken")]
            direction = "unclear"
        elif id == "C004":
            prop = "POST /version/v1/tan/teletan returns 201; REQUEST_UNCHECKABLE concerns object-shaped Authorization header serialization, with no observed failure."
            head_state = "The checked-in HEAD spec still references AuthorizationToken for the required header; runtime serialization was not regenerated or tested."
            markers = [(C+"model/AuthorizationToken.java", "public class AuthorizationToken")]
            direction = "unclear"
        else:
            raise AssertionError(id)
        if id in {"P014", "P015"}:
            direction = "spec_changed_to_match_code"
            confidence = 3
            evidence_commits = [PET_FIX]
            note = "Direct targeted required:false -> true spec edit; no handler/DTO/annotation changes after the anchor. "
            if id == "P014":
                note += "Covers the one omitted-status witness. ⚠️ Developer repair choice differs from final IMPL; this does not retroactively invalidate the old default promise. Review only."
            else:
                note += "⚠️ Partial cluster evidence: only 2/5 witnesses omit tags; 3/5 send a present empty value and remain unresolved by required alone; no minItems/allowEmptyValue fix."
        elif id == "C002":
            direction = "spec_changed_to_match_code"
            evidence_commits = [CWA_FIX]
            note = "⚠️ Generated checked-in spec refresh, possibly incidental regeneration: required key/keyType and keyDob pattern now match pre-existing validation. Spec artifact changed; Java annotations=false; matching handler logic=false. Partial cluster evidence: 56/69 missing required, 61/69 rejected by new required/pattern constraints, but 7 also contain illegal headers, leaving 54/69 transport-clean covered witnesses. Conditional key constraints are still not modeled. No evidence the baseline report caused this commit."
        elif id == "C005":
            direction = "changed_unrelated"
            evidence_commits = [CWA_FIX, CWA_MIGRATION]
            note = "⚠️ Regeneration changed other response/header elements, and a later Jakarta migration changed imports. The exact 404 object schema and empty exception response persist. These touches are not directional evidence for this proposition."
        elif direction == "unclear":
            confidence = 1 if id in TRANSPORT else 2
            note = "⚠️ No usable SUT developer direction: checker/probe/business-precondition item, or unverified deployment-specific transport policy. " + note
        # Source locators are actual SHA:path:line references, not heuristic line guesses.
        code_locs = [source_locator(sut, a["head"], p, marker) for p, marker in markers]
        if not code_locs:
            p = route_code(b)[0]
            code_locs = [source_locator(sut, a["head"], p, "public class")]
        scope = scope_for(b, markers)
        histories = json.loads((HERE / (sut + "_all_descendant_history.json")).read_text())
        touched = []
        for h in histories:
            spec_hits = sorted(set(h["files"]) & set(scope["spec_artifact_paths"]))
            code_hits = sorted(set(h["files"]) & set(scope["source_paths"]))
            config_hits = sorted(set(h["files"]) & set(scope["configuration_paths"]))
            if spec_hits or code_hits or config_hits:
                touched.append({**h, "spec_hits": spec_hits, "code_hits": code_hits, "configuration_hits": config_hits, "matching_directional_commit": h["commit"] in evidence_commits and direction in MAPPING})
        witness = re.search(r"(08_experiments/[^;]+/exchanges.jsonl:\d+)", item["codex"]["evidence_locators"]).group(1)
        locs = [witness, "08_experiments/E2_labelling/" + sut + "_adjudication.csv:" + id] + code_locs
        pointer = "/paths/" + b["template"].replace("~", "~0").replace("/", "~1") + "/" + b["method"].lower()
        if id in PROBES:
            pointer = "/paths"
        locs.append(a["deployed_spec"] + "#" + pointer)
        dates = []
        excerpts = []
        for commit in evidence_commits:
            h = next(v for v in histories if v["commit"] == commit)
            dates.append(commit + "=" + h["committer_date"])
            excerpts.append(commit + " " + h["message"])
            if commit == PET_FIX:
                # Both parameter lines have the same numbering at this commit and HEAD.
                line = 131 if id == "P014" else 173
                locs.append(commit + ":src/main/resources/openapi.yaml:" + str(line))
            elif commit == CWA_FIX:
                locs.append(commit + ":api-docs.json:" + ("384" if id == "C002" else "183"))
            else:
                locs.append(h["patch"])
        dates.append("HEAD=" + a["head_committer_date"])
        if excerpts:
            note += " Commit excerpt(s): " + " | ".join(excerpts) + "."
        note += " HEAD " + a["head"] + ": " + head_state
        locs.append("08_experiments/E4_triage/future_oracle/item_history.json:" + id)
        details[id] = {"sut": sut, "proposition": prop, "head_state": head_state, "scope": scope, "post_anchor_touches": touched, "default_head_commit_count_screened": len(a["post_anchor_reachable_commits"]), "all_ref_descendant_count_screened": len(a["all_ref_post_anchor_descendants"]), "source_locators": code_locs, "baseline_witness": witness, "review_status": "manual static review; non-blind to final labels", "fix_direction": direction, "spec_artifact_changed_for_target": direction == "spec_changed_to_match_code", "annotations_changed_for_target": False, "handler_logic_changed_for_target": False, "eligible_direction_comparison": direction in MAPPING}
        output.append({"item_id": id, "sut": sut, "proposition": ("⚠️ " if "inferred" in prop else "") + prop, "anchor_commit": a["commit"], "fix_direction": direction, "evidence_locators": ";".join(locs), "commit_dates": ";".join(dates), "confidence (1–3)": confidence, "notes": note})
    output.sort(key=lambda r: (r["sut"], r["item_id"]))
    assert len({r["item_id"] for r in output}) == len(output) == 62
    dump_csv(HERE / "future_oracle.csv", output)
    m.dump(HERE / "item_history.json", details)
    final = {i["baseline"]["item_id"]: i["baseline"]["final_L1"] for i in items}
    comparison = [{"item_id": r["item_id"], "sut": r["sut"], "fix_direction": r["fix_direction"], "developer_direction_label": "SPEC" if r["fix_direction"] == "spec_changed_to_match_code" else "IMPL" if r["fix_direction"] == "code_changed_to_match_spec" else "BOTH", "final_L1": final[r["item_id"]], "agreement": final[r["item_id"]] in MAPPING[r["fix_direction"]], "partial_cluster": r["item_id"] in {"P015", "C002"}, "confidence": r["confidence (1–3)"]} for r in output if r["fix_direction"] in MAPPING]
    dump_csv(HERE / "agreement.csv", comparison)
    proposals = [{"item_id": r["item_id"], "current_final_L1": r["final_L1"], "developer_direction": r["developer_direction_label"], "proposal": "Review P014 using the targeted upstream spec repair; retain original label until adjudication. Repair choice and original fault attribution can differ, especially because default available remains.", "status": "review_only_no_label_change"} for r in comparison if not r["agreement"]]
    dump_csv(HERE / "review_proposals.csv", proposals)
    summary = {"items": 62, "counts_by_sut": dict(collections.Counter(r["sut"] for r in output)), "directions": dict(collections.Counter(r["fix_direction"] for r in output)), "usable_direction_items": len(comparison), "usable_direction_fraction": len(comparison)/62, "targeted_commits": 2, "agreement": sum(r["agreement"] for r in comparison), "disagreements": [r["item_id"] for r in comparison if not r["agreement"]], "partial_cluster_items": [r["item_id"] for r in comparison if r["partial_cluster"]], "full_cluster_direction_items": [r["item_id"] for r in comparison if not r["partial_cluster"]], "high_confidence_items": [r["item_id"] for r in comparison if r["confidence"] == 3], "final_label_distribution": dict(collections.Counter(final.values())), "excluded_comparison": {"unchanged_at_head": "No observed directional repair", "unclear": "No reliable SUT repair proposition/direction", "changed_unrelated": "Touches do not repair the target mismatch; no direction-label mapping"}}
    m.dump(HERE / "summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
