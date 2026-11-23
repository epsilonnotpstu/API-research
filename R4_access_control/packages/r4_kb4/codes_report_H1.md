# H1 report (kb4)
All 16 items opened. Hard cases:
- A055: gRPC JWT claim validation; coded NO (token validation, non-REST).
- A062: recovery key/state trust issue; coded NO.
- A057 (stale IdP groups) and A058 (step-up authentication level) are borderline; coded YES with confidence 2, kinds OTHER and FUNCTION_LEVEL.
- A063: default privilege threshold; weak AC reading, confidence 1.
- A054: several flaws in one advisory; primary kind taken from S3 gateway copy; operation is not in the OpenAPI contract.
- A050, A052, A054, A058, A059, A063: contracts truncated or lacking the operation, coded ABSENT.
- A051, A060: contract files have no paths, coded NO_CONTRACT.
