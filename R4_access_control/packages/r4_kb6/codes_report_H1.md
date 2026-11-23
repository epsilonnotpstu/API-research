# H1 report (kb6, 16 items)
All 16 items opened; none unreadable.
Hard cases:
- A081, A084: contract truncated at 3000 lines and target path not visible; contract_operation set UNCLEAR rather than ABSENT.
- A083, A089: policy_in_contract YES because the contract itself declares authentication for the operation (the violated rule is "authentication required").
- A084: PoC shows one account owning two projects suffices; coded ONE.
- A082, A085, A091, A094, A096: coded NO (token validation, VM builtin, replay window, container networking, login flow).
- A086: filter fix plus object-layer checks; main locus coded MIDDLEWARE_FILTER.
- A095: namespace-scoped read of templates coded TENANT_ISOLATION (alternative: FUNCTION_LEVEL).
