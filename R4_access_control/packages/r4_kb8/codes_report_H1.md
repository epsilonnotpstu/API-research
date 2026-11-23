# H1 report (kb8)
All 16 items opened. Hard cases:
- A117: OAuth prompt=none consent bypass coded NO (authorization-flow logic), confidence 2.
- A119: gRPC stream, not REST; coded YES TENANT_ISOLATION, observable UNCLEAR, contract ABSENT.
- A118: bundled diff; coded from advisory (stale permission cache); contract truncated, operation UNCLEAR.
- A128, A126: unclear whether anonymous callers were affected; confidence 2.
- A113: kind TENANT_ISOLATION vs FUNCTION_LEVEL ambiguous.
