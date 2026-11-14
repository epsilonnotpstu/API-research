#!/usr/bin/env python3
"""Labeller A (Claude) for market baseline s1 (13 items). Not ground truth alone."""
import csv
from collections import Counter
SRC = "../E2_labelling/market_baseline_s1_blind.csv"
OUT = "pilot_results/market_baseline_s1_labels_A_claude.csv"
H = "market-rest/src/main/java/market/rest/exception/RestExceptionHandler.java"
RUN = "runs/market/20261114T023303Z_batch_1724645_baseline_NONE_p0_s1/exchanges.jsonl"
S406 = ("SPEC", "S-STATUS", "", 3, "E-CODE-INTENT", H + ":63-64,73-74", "RC-M2", True,
        "Validation errors deliberately mapped to 406 (@ResponseStatus NOT_ACCEPTABLE); spec omits it. [H] 406 misuses HTTP semantics (400/422 expected) -> BOTH candidate")
LINKS = ("BOTH", "I-CRASH", "S-REQ-TYPE", 2, "E-CODE-INTENT+E-OBS",
         H + ":37-42; spec.original.json#/definitions/*DTOReq/properties/_links; " + RUN + ":211,709,1105", "RC-M1", True,
         "Spec types HAL _links as array (Springfox artifact); spec-valid {\"_links\": []} fails HAL parsing, and the generic handler turns a client error into 500")
L = {
 "M001": ("TEST", "T-PROBE", "", 3, "E-LOG", "Schemathesis probe to /", "RC-M0", False, "Capability probe, not an API call"),
 "M002": LINKS, "M004": LINKS, "M006": LINKS, "M008": LINKS, "M011": LINKS, "M013": LINKS,
 "M003": S406, "M005": S406, "M007": S406, "M012": S406,
 "M009": ("IMPL", "I-CRASH", "", 3, "E-CODE-INTENT+E-OBS", H + ":37-42; " + RUN + ":927,952", "RC-M3", False,
          "orderId beyond int64 (invalid input) raises a conversion error that the generic handler maps to 500 instead of 4xx"),
 "M010": None,
}
L["M010"] = L["M009"]
cols = ["item_id","L1","L2","proposed_L2","confidence","evidence_types","evidence_locators","root_cause_id","both_candidate","rationale"]
rows = list(csv.DictReader(open(SRC)))
assert set(L) == {r["item_id"] for r in rows}
with open(OUT, "w", newline="") as f:
    w = csv.writer(f); w.writerow(cols)
    for r in rows: w.writerow([r["item_id"], *L[r["item_id"]]])
print(Counter(L[r["item_id"]][0] for r in rows))
