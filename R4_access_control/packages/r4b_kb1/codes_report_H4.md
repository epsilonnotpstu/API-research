# H4 report (kb1)
All 17 items opened. Hard cases:
- C001: contract has no paths (base file only), coded NO_CONTRACT.
- C005, C009, C011, C014: contracts describe other APIs or only management endpoints; coded ABSENT. C005 could also be read as NO_CONTRACT (boards plugin API).
- C007: flaw is in proxy rule matching, no REST operation; UNKNOWN/UNCLEAR.
- C008: export documented as GET, advisory says POST; PRESENT via import (v1.10 file used).
- C010: flaw is missing authentication; contract declares security and 401, coded policy YES (confidence 2).
- C015: advisory names no endpoint; representative operation chosen.
- C009 and C005 operation paths inferred from product knowledge, not verified in item files.
