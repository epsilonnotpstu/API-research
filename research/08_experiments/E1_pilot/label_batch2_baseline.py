#!/usr/bin/env python3
"""Code-informed labels for the 99 Batch-2 baseline (seed 1) violation fingerprints.

Labeller: Claude (single labeller, NOT ground truth by itself; needs a second labeller).
Evidence: scout-api source (EMB, jdk_8_maven/cs/rest/original/scout-api), SUT log, exchanges.
Each rule below cites the source locator that justifies it (E-CODE-INTENT / E-LOG).
"""
import csv, sys
from collections import Counter

SRC = "pilot_results/batch2_baseline_s1_violations_prelim.csv"
OUT = "pilot_results/batch2_baseline_s1_labels_code.csv"
R = "api/src/main/java/se/devscout/scoutapi/resource/"
D = "data-access/src/main/java/se/devscout/scoutapi/"


def label(r):
    k, m, t, st = r["kind"], r["method"], r["template"], r["status"]
    item = t.endswith("{id}") or "{id}/" in t
    if k == "UNDOCUMENTED_OPERATION":
        return ("TEST", "T-PROBE", "E-LOG", "exchanges.jsonl: x-schemathesis-probe request with NUL byte to /api",
                3, "Schemathesis capability probe, rejected by Jetty; not an API operation", "")
    if k == "INVALID_ACCEPTED":
        loc = (R + "UserResource.java:81-84" if "users" in t else R + "v1/FavouritesResourceV1.java:29,46,55")
        return ("SPEC", "S-STRUCT", "E-CODE-INTENT", loc, 3,
                "Spec declares required path parameter id on a path without {id}; comes from a stray @PathParam(\"id\") "
                "on a method whose @Path has no template. Unsatisfiable parameter; checker is correct", "fix site = code annotation")
    if k in ("SERVER_ERROR", "UNDOCUMENTED_STATUS") and st == "500":
        dup = "duplicate view of SERVER_ERROR" if k == "UNDOCUMENTED_STATUS" else ""
        if m == "GET" and t.endswith("/activities"):
            return ("IMPL", "I-CRASH", "E-CODE-INTENT", R + "v1/ActivityResourceV1.java:74-76; " + R + "ActivityResourceV2.java:76-78", 3,
                    "Documented query parameter my_favourites triggers WebApplicationException without status (=500); "
                    "25/26 (v1) and 22/24 (v2) occurrences. Deliberate 'not supported' reported as server error",
                    "spec co-defect [H]: advertises an unsupported parameter -> BOTH candidate")
        if item or "rating" in t or t.endswith("/file"):
            return ("IMPL", "I-CRASH", "E-CODE-INTENT+E-LOG",
                    R + "ActivityResource.java:76,94,102,119,133,144; " + D + "model/ActivityRating.java:90; "
                    + D + "dao/ActivityDao.java:167,219; " + R + "MediaFileResource.java:260",
                    3, "dao.read(id) result used without null check: non-existent id gives NullPointerException / "
                       "'attempt to create delete event with null entity' -> 500 where 404 is intended", dup)
        if t.endswith("/favourites"):
            return ("IMPL", "I-CRASH", "E-CODE-INTENT+E-LOG", R + "v1/FavouritesResourceV1.java:58,66", 3,
                    "Body {} leaves id list null; dereferenced without validation -> NullPointerException", 
                    "spec co-defect [H]: id not marked required")
        return ("IMPL", "I-CRASH", "E-LOG", "compose.log: JdbcSQLException NULL not allowed / NullPointerException in create()", 2,
                "Create with spec-valid minimal body ({} or missing fields) reaches persistence without validation -> 500",
                (dup + "; " if dup else "") + "spec co-defect [H]: no required fields declared -> BOTH candidate")
    if k == "UNDOCUMENTED_STATUS":
        if st == "403":
            return ("SPEC", "S-STATUS", "E-CODE-INTENT", R + "UserResource.java:126", 3,
                    "Explicit FORBIDDEN ('Cannot set authorization level to higher than your own'); spec lists only 200", "")
        if st == "404":
            return ("SPEC", "S-STATUS", "E-OBS", "exchanges.jsonl: id outside int64 range -> JAX-RS path conversion 404", 2,
                    "Framework-level 404 for unconvertible path id; spec lists only 200", "")
        if st == "400":
            return ("SPEC", "S-STATUS", "E-OBS", "exchanges.jsonl: 'Unable to process JSON' (Dropwizard JSON mapper)", 2,
                    "Standard 400 for undeserialisable body; spec lists only 200", "")
    if k == "VALID_REJECTED":
        if m == "GET":
            return ("SPEC", "S-REQ-LOOSE", "E-CODE-INTENT", R + "ActivityResource.java:47-55", 3,
                    "Query parameters declared plain string, but code parses them as comma-separated integers and "
                    "returns an explicit 400 otherwise; spec lacks pattern/array-of-integer typing", "")
        return ("SPEC", "S-REQ-LOOSE", "E-OBS", "exchanges.jsonl: 1054/1131 rejected bodies carry a top-level undeclared property", 2,
                "Server rejects undeclared properties (strict Jackson deserialisation); schemas do not state "
                "additionalProperties:false. Remaining 77 bodies: nested undeclared properties or out-of-range values",
                "intent not explicit in project code (framework default) -> confidence 2")
    return ("UNDECIDABLE", "", "", "", 1, "no rule", "")


rows = list(csv.DictReader(open(SRC, newline="")))
cols = list(rows[0].keys()) + ["L1", "L2", "evidence_type", "evidence_locator", "label_confidence", "rationale", "note"]
c1, c2, chg = Counter(), Counter(), Counter()
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows:
        L = label(r)
        r.update(dict(zip(cols[-7:], L)))
        w.writerow(r)
        c1[L[0]] += 1; c2[(L[0], L[1])] += 1; chg[(r["prelim_L1"], L[0])] += 1
print(len(rows), dict(c1)); print(dict(c2)); print("prelim->final", dict(chg))
