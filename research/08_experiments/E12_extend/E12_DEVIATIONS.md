# E12 deviations (recorded before any score was seen)

**D1: scorer CSV field limit (2026-11-17 00:33, Claude).** This was the first scoring run, after the output freeze (`e12_outputs_freeze.sha256`, 16 files). The frozen `score_e12.py` (sha256 f229283f…) crashed while loading `E7_mining/key/accepted_full_t49.csv`, because Python's csv module stops at fields over 128 KiB (`_csv.Error: field larger than field limit (131072)`). The crash came before any analysis line was printed, so no result was seen.

The fix is one added line, `csv.field_size_limit(sys.maxsize)`, placed after the imports. There is no logic change. The new sha256 is faff3972…, and the self-test `test_score_e12.py` still passes. The scorer was then run once. The original is preserved in git history (commit 07bfbef).
