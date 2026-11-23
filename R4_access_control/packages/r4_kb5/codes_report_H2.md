# H2 report (kb5)
All 16 items opened.
Hard cases:
- A080: diff.patch (OAuth redirect validation) does not match the advisory (unauthenticated like endpoint); coded from advisory and contract; fix_location OTHER.
- A072: blockchain transaction handlers, only loosely an HTTP service; coded YES with confidence 1.
- A068, A069, A078: contract truncated or operation not identifiable; contract_operation UNCLEAR.
- A070, A071, A078: classified as function-level (revoked/missing permission); confidence 2.
- A067, A073, A076, A077, A079: not HTTP access-control flaws (NO).
