# Blind review report — G2

Reviewed all 136 items in `items.csv` order. The CSV records 64 YES, 51 NO, and 21 UNCLEAR decisions. Among YES decisions, 35 are BREAKING and 29 COMPATIBLE. All item patches opened successfully; no item was skipped.

The review used only this package's supplied patches, source snapshots, and contracts. No item code was executed, and no network or history was consulted. Read-only helpers are in `codes_work_G2/`.

Hard cases retained as UNCLEAR:

| Items | Evidence limitation |
| --- | --- |
| B007, B025 | Startup path normalization and web-context startup policy change, but the provided files do not establish a different completed HTTP outcome. |
| B013, B019, B028, B078, B088, B108 | Changed validation, transaction, storage, authorization, mapping, or registry behavior depends on missing or redacted implementations. |
| B022, B048, B106, B110, B127, B133 | Internal data or helper behavior changes, but supplied callers do not establish the HTTP effect. |
| B063, B065, B091 | The supplied source contains inconsistent before declarations or unresolved after merge markers, preventing a reliable comparison of running behavior. |
| B090 | The validation annotation namespace changes; the active validation provider is not supplied. |
| B107, B114, B116 | A resolver replacement, asynchronous service dependency, or removed transaction boundary depends on implementation details not included. |

Concurrency changes were not automatically treated as refactoring. B002 prevents a stale permission overwrite; B120 changes consumer cleanup under concurrent mutation; B123 serializes stored submodel mutations. Their API-visible permissions or state can differ. B130's gated debug allocation preserves response inclusion, and its salt substitution uses the documented preformatted identifier, so it is NO with confidence 2.

New standalone types or uninvoked helpers were not assumed to change HTTP behavior (for example B030, B053, B064, B097, B126, B135). Changes confined to email or business-event output were also distinguished from HTTP outcomes (B038, B044, B055). B111 is YES because it explicitly registers a new HTTP servlet, beyond changing internal metric collection.

Contract judgments concern only the supplied before documents. Twenty-nine contract folders contain no files; other folders sometimes contain only metadata, unrelated examples, or projections without the relevant operation. These do not establish specified behavior. SPECIFIED decisions cite the relevant response field, compatibility override description, or documented error status in addition to source evidence.

Validation checked the CSV header, complete ordered coverage, enum values, NA rules, rationale lengths of at most 40 words, and existence and line bounds of every locator. No service tests were run because executing item code is prohibited.
