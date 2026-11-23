# H2 report (kb1)
All 16 items opened. Hard cases:
- A002: password-reset code returned in response; coded NO (reset-flow logic).
- A006: SCIM externalId collision; only a DB migration shown, endpoint unknown; UNCLEAR.
- A005: access-rule matching case bug in forward-auth; coded YES/OTHER, contract is a Go template so security UNCLEAR.
- A004: org claims leaked when feature disabled; PROPERTY_LEVEL is a judgment call (confidence 2).
- A009: contract path mapping to the touched resources is approximate.
- A007: blockchain precompile, not HTTP; NO.
