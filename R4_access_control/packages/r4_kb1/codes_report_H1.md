# H1 report (kb1)
All 16 items opened. Hard cases (low confidence):
- A002: judged NO (password-reset code returned in response; reset-flow logic).
- A004: feature-disabled enforcement; classed FUNCTION_LEVEL at confidence 1, borderline NO/UNCLEAR.
- A005: domain-case rule mismatch in forwarded-auth; kind OTHER, confidence 1.
- A006: SCIM uid collision; fix is a DB migration only; kind OTHER, confidence 1.
- A007: EVM precompile; HTTP reachability only via JSON-RPC, contract operation ABSENT.
Contract_security for items whose contract has no security block was coded NOT_DECLARED.
