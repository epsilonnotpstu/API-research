#!/usr/bin/env python3
"""Labeller A (Claude) for swagger-petstore baseline s1 (43 items). Not ground truth alone."""
import csv
from collections import Counter
SRC = "../E2_labelling/swagger-petstore_baseline_s1_blind.csv"
OUT = "pilot_results/swagger-petstore_baseline_s1_labels_A_claude.csv"
C = "src/main/java/io/swagger/petstore/"
RUN = "runs/swagger-petstore/20261114T021748Z_batch_1701236_baseline_NONE_p0_s1/exchanges.jsonl"
# item_id -> (L1, L2, proposed_L2, conf, evidence_types, locators, root_cause, both, rationale)
U = ("TEST", "", "T-ORACLE-COVERAGE", 3, "E-OBS", "tools/conformance.py REQUEST_UNCHECKABLE", "RC-A1", False,
     "Checker cannot validate XML/form request bodies; the 500/400 outcomes themselves are labelled under their own items")
PET500 = ("IMPL", "I-CRASH", "", 3, "E-CODE-INTENT+E-OBS", C + "model/Pet.java:29,37-38; " + C + "data/PetData.java:103; " + C + "controller/PetController.java:213",
          "RC-A2", True, "Pet.id is Long but getId() returns long: body without id (spec-optional) unboxes null -> NPE; 132/132 500s lack id, all 200s have id")
USER500 = ("IMPL", "I-CRASH", "", 3, "E-CODE-INTENT+E-OBS", C + "data/UserData.java:53-56,63-66; " + RUN + ":952",
           "RC-A3", True, "POST /user {} stores a user with null username (#952); every later lookup/insert calls getUsername().equals -> NPE. Stateful: cause is in POST /user")
LOOSE = lambda loc, why: ("SPEC", "S-REQ-LOOSE", "", 3, "E-CODE-INTENT", C + loc, "RC-A4", False, why)
L = {
 "P001": ("TEST", "T-PROBE", "", 3, "E-LOG", "compose.log: x-schemathesis-probe-null header rejected by Tomcat", "RC-A0", False, "Schemathesis capability probe, not an API call"),
 "P005": ("IMPL", "I-RESP-CONTRACT", "", 3, "E-OBS+E-CODE-INTENT", RUN + ":105,146,147; " + C + "controller/PetController.java:199-203", "RC-A5", False,
          "Form-encoded create without photoUrls (required in Pet) is accepted and echoed; response violates required photoUrls"),
 "P011": None, "P013": None,
 "P006": PET500, "P012": PET500,
 "P014": ("IMPL", "I-REJECT-VALID", "", 3, "E-CODE-INTENT", C + "controller/PetController.java:50-56", "RC-A6", False,
          "Spec declares status optional with default 'available'; code rejects missing status instead of applying the documented default"),
 "P015": LOOSE("controller/PetController.java:233-239", "tags optional in spec; code explicitly rejects missing tags with 400"),
 "P016": ("TEST", "", "T-ORACLE-FORMAT", 2, "E-OBS", RUN + " (path ids > 2^63)", "RC-A7", False,
          "Path id exceeds int64 declared by format; request is spec-invalid but checker does not enforce int64 range"),
 "P017": None,
 "P018": ("SPEC", "S-REQ-LOOSE", "", 2, "E-OBS", RUN + ":408-409", "RC-A8", True,
          "updatePetWithForm 'status' query has no enum while Pet.status is an enum; arbitrary status stored and returned. Code also does not validate"),
 "P019": LOOSE("controller/PetController.java:100-104", "63/66: name optional in spec, code requires it ('No Name provided'); 3/66 are int64-overflow ids"),
 "P020": ("TEST", "", "T-ORACLE-COVERAGE", 3, "E-OBS", "tools/conformance.py: request body capture incomplete/undecodable", "RC-A1", False, "octet-stream body not decodable by checker"),
 "P021": LOOSE("controller/PetController.java:157-159", "60/62: requestBody not required in spec, code rejects empty upload ('No file uploaded')"),
 "P022": ("TEST", "", "T-GEN-INVALID-HTTP", 2, "E-OBS", RUN + ":624 (api_key header = 0x03)", "RC-A9", False,
          "Generator sent a control character in a header; Tomcat rejects at HTTP level before the API"),
 "P026": ("IMPL", "I-CRASH", "", 2, "E-OBS", RUN + " (50/50 order 500s are form-urlencoded)", "RC-A10", False,
          "Form-encoded order creation crashes (JSON/XML never 500); no stack trace (NOP logger) -> confidence 2"),
 "P027": LOOSE("controller/OrderController.java:59-63", "requestBody not required in spec; code rejects absent order"),
 "P031": USER500, "P033": USER500, "P036": USER500, "P038": USER500, "P042": USER500,
 "P032": LOOSE("controller/UserController.java:35-39", "requestBody not required in spec; code rejects absent user"),
 "P034": LOOSE("controller/UserController.java:88-92", "Array schema has no minItems; code rejects empty list"),
 "P035": ("IMPL", "I-RESP-CONTRACT", "", 3, "E-OBS", RUN + " (GET /user/login: content-type application/json, body plain text)", "RC-A11", True,
          "Declares application/json but returns unquoted text; malformed JSON body -> IMPL (§9.3). [H] spec may have intended text/plain"),
 "P037": ("UNDECIDABLE", "", "", 1, "E-OBS", RUN + " (Tomcat HTML 400 for encoded backslash in username)", "RC-A12", False,
          "Servlet-container default rejects %5C; spec leaves username open. Policy-ambiguous like the T15 open-schema decision"),
 "P039": None,
 "P043": LOOSE("controller/UserController.java:146-149", "34/36: requestBody not required in spec; code rejects absent user"),
}
L["P011"] = L["P005"]; L["P013"] = L["P005"]; L["P017"] = L["P016"]; L["P039"] = L["P037"]
for i in ["P002","P003","P004","P007","P008","P009","P010","P023","P024","P025","P028","P029","P030","P040","P041"]:
    L[i] = U
cols = ["item_id","L1","L2","proposed_L2","confidence","evidence_types","evidence_locators","root_cause_id","both_candidate","rationale"]
rows = list(csv.DictReader(open(SRC)))
assert set(L) == {r["item_id"] for r in rows}, set(r["item_id"] for r in rows) ^ set(L)
with open(OUT, "w", newline="") as f:
    w = csv.writer(f); w.writerow(cols)
    for r in rows: w.writerow([r["item_id"], *L[r["item_id"]]])
print(Counter(L[r["item_id"]][0] for r in rows), "BOTH", sum(L[r["item_id"]][7] for r in rows))
