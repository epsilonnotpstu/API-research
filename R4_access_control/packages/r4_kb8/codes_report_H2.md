# H2 report (kb8)
All 16 items opened and coded; no item unreadable.
Hard cases:
- A114: CoAP header injection, not HTTP access control (NO).
- A117: OAuth consent scope expansion; coded OTHER. The contract lists /oauth2/authorize as removed (410), so PRESENT is weak.
- A118: advisory is stale permission cache; the diff bundles many unrelated hardening changes. Contract truncated, token operation not seen (ABSENT).
- A119: gRPC stream interface; contract has REST only, observable_via_http coded YES at confidence 2.
- A125: Kubernetes contract truncated at 3000 lines, security block not visible (UNCLEAR).
- A126, A128: caller identity before the fix is inferred from the fix and advisory; confidence 2.
