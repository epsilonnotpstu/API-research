# H2 report (kb3)
All 16 items opened and coded.
Hard cases:
- A033: diff (POST-method check in a comment resource command) does not match the IDOR advisory; coded from advisory, confidence 1.
- A034: DNS-rebinding on a separate MCP SSE listener; coded as missing authentication, borderline with CSRF-style NO.
- A038: contract truncated before workflow submit path; contract_operation UNCLEAR.
- A042, A047: not plain REST operations (admission webhook, gRPC); A042 coded YES, A047 coded NO.
- A046: fix is rate limiting only; coded NO.
- A036: fix changes a reputation-threshold config; kind FUNCTION_LEVEL is a judgment call.
