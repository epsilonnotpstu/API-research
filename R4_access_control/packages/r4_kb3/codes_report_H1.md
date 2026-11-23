# H1 report (kb3)
Opened all 16 items; none failed.
Hard cases:
- A033: advisory (address IDOR) does not match diff (POST check on a change-tracking command); coded from advisory, confidence 1.
- A038: workflow-submit path is beyond the 3000-line truncation; contract_operation UNCLEAR.
- A036: accept-answer path is redacted in contract; treated as present with ApiKeyAuth.
- A045: token-exchange cross-org flaw coded NO under the token-validation exclusion; arguably tenant isolation.
- A047: gRPC path; observable_via_http UNCLEAR.
- A034/A046: A034 is DNS-rebinding on unauthenticated MCP listener (coded missing authentication); A046 fix only rate-limits, endpoint stays anonymous.
- A048: signature validation, NO.
