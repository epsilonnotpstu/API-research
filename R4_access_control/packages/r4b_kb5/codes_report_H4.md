# H4 report (kb5)
All 17 items opened. No boundary incident.
Hard cases:
- C070: exact system route not in provided files; operation given as wildcard, low confidence.
- C071: openapi documents have no paths (NO_CONTRACT).
- C077: no HTTP operation (RBAC configuration flaw); UNCLEAR.
- C078: contract is a Go-template; path key is templated, treated as PRESENT with moderate confidence.
- C073: several operations in the advisory; refs dump/restore chosen as documented ones.
- C083: bypass applies to all protected endpoints; representative operation chosen; policy YES because flaw is missing authentication.
