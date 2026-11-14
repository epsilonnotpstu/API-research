#!/usr/bin/env python3
"""Labeller A (Claude) for cwa-verification baseline s1 (6 items), codebook v0.4. Not ground truth alone."""
import csv
from collections import Counter
SRC = "../E2_labelling/cwa-verification_baseline_s1_blind.csv"
OUT = "pilot_results/cwa-verification_baseline_s1_labels_A_claude.csv"
J = "src/main/java/app/coronawarn/verification/"
RUN = "runs/cwa-verification/20261114T084828Z_batch_118863_baseline_NONE_p0_s1/exchanges.jsonl"
STATE = lambda loc, why: ("TEST", "", "T-ORACLE-STATEFUL", 3, "E-CODE-INTENT", J + loc, "RC-C2", False, why)
L = {
 "C001": ("TEST", "T-PROBE", "", 3, "E-OBS", RUN + ":1", "RC-C0", False, "Schemathesis capability probe to /"),
 "C002": ("SPEC_PARTIAL", "S-REQ-LOOSE", "", 2, "E-CODE-INTENT+E-OBS", J + "model/RegistrationTokenRequest.java:47-60", "RC-C1", False,
          "56/69 bodies lack key or keyType, which are @NotNull in code but not required in spec; 13/69 have both and are rejected for unresolved reasons"),
 "C003": STATE("controller/ExternalTanController.java:153-154",
               "Pattern-valid but unknown registration token -> explicit 400 'VerificationAppSession not found' (documented 400). Schema validity cannot capture server state"),
 "C004": ("TEST", "", "T-ORACLE-COVERAGE", 2, "E-OBS", "spec.original.json#/paths/~1version~1v1~1tan~1teletan/post/parameters (Authorization header)", "RC-C3", False,
          "Checker cannot evaluate an 'Authorization' header parameter; OAS 3 says such definitions are ignored. [H] spec should use a securityScheme (S-CONFIG)"),
 "C005": ("SPEC", "", "S-RESP-BODY", 3, "E-CODE-INTENT", J + "controller/InternalTanController.java:99,103-122", "RC-C4", False,
          "@ApiResponse(404) declares no content; springdoc emitted a */* object body, but the handler returns 404 without a body"),
 "C006": STATE("controller/ExternalTestStateController.java:149-151",
               "Pattern-valid but unknown registration token -> explicit 400 (documented). Server-state rejection, not a schema contract breach"),
}
cols = ["item_id","L1","L2","proposed_L2","confidence","evidence_types","evidence_locators","root_cause_id","both_candidate","rationale"]
rows = list(csv.DictReader(open(SRC)))
assert set(L) == {r["item_id"] for r in rows}
with open(OUT, "w", newline="") as f:
    w = csv.writer(f); w.writerow(cols)
    for r in rows: w.writerow([r["item_id"], *L[r["item_id"]]])
print(Counter(L[r["item_id"]][0] for r in rows))
