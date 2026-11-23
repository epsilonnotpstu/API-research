# H2 report, kb7 (16 items)
All items opened. Hard cases:
- A099: legacy WebRTC path judged not an HTTP operation (NO).
- A107, A111, A110: judged NO (controller/library/runtime, not HTTP-request access decision); A107 is borderline.
- A103: diff touches only a test helper; fix location and kind inferred from advisory (low confidence).
- A098, A101, A112: contract truncated at 3000 lines; operation not visible, so contract_operation UNCLEAR.
- A109: operation appears only in an x-identrail route-authorization list, not in paths; coded ABSENT.
- A112: diff shows only a query-parameter auth tweak, not the main fix.
