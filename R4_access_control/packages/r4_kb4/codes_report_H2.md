# H2 report (kb4)
16 items coded; all opened. No boundary incident.

Hard cases:
- A054: several flaws (S3 copy, ref-type permission conflation); coded as FUNCTION_LEVEL, confidence 2.
- A057: stale IdP group membership; coded YES/OTHER, requires IdP-side change to observe.
- A058: step-up (LoA) enforcement on credential deletion; judged access control (function level), not login-flow logic; confidence 2.
- A063: diff only changes default privilege thresholds; contract truncated at 3000 lines so operation set to UNCLEAR; confidence 1.
- A055, A062: coded NO (JWT validation; recovery key/sealed state trust).
- A051, A060 (NiFi): contract files contain only info/security, no paths, so ABSENT.
- Principals for role-policy cases (A054, A056) set to TWO_ROLES as a comparison against a permitted role is needed.
