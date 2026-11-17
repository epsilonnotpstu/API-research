# Blind change review: what does each commit do to the HTTP API?

You are a blind coder. Work only inside this package directory. Your coder ID is the `YOUR_ID` given in the prompt.

## What you get
`items.csv` lists the items. Each item is one source-code commit to a REST service, in its own folder `<item_id>/`:
- `item.md`: repository name, language and the touched files.
- `diff.patch`: the commit's changes to production source files.
- `before/` and `after/`: the full touched files before and after the commit.
- `contract/`: the service's OpenAPI/Swagger contract as it was **before** the commit (possibly projected to the relevant operations).

The commit did not change the contract document. You do not get the commit message, the author, the date, or anything that happened later.

## What to decide, per item
1. **`observable_change`:** YES, NO or UNCLEAR.
   - Answer **YES** if there is at least one HTTP request to some operation of this service whose observable outcome differs after the commit. Observable outcomes are:
     - status code;
     - response headers or media type;
     - response body content or shape;
     - whether an input is accepted or rejected;
     - an effect visible through the API, such as stored data later returned, or authorization.
   - Answer **NO** for changes that do not alter what any client can observe:
     - refactoring, renaming of internals, logging, metrics, comments;
     - performance changes with identical results;
     - code reached by no HTTP operation.
   - Answer **UNCLEAR** only if the provided files do not let you decide.
2. **If YES, fill in these fields** (otherwise write NA):
   - **`change_kind`:** the single primary kind:
     - `STATUS_OR_ERROR_MAPPING`: different status code, or a different error or exception mapping.
     - `INPUT_STRICTER`: some previously accepted input is now rejected or treated as invalid.
     - `INPUT_LOOSER`: some previously rejected input is now accepted.
     - `DEFAULT_OR_OPTIONALITY`: a different default value, or a parameter or field changes between required and optional.
     - `RESPONSE_CONTENT`: same structure, different values (for example a computation, filter, or format of a value).
     - `RESPONSE_SHAPE`: fields added, removed or renamed, or a type or nesting change in the response.
     - `HEADER_OR_MEDIA_TYPE`: response headers, content type, or encoding.
     - `AUTHZ_OR_AUTH`: who may call the operation, or how authentication behaves.
     - `SIDE_EFFECT_OR_STATE`: what the request changes in stored state (visible through later calls).
     - `ORDERING_PAGINATION_LIMITS`: order, page size, limits or truncation.
     - `OTHER`.
   - **`client_impact`:**
     - BREAKING: a client that worked correctly against the old behaviour can now fail or misbehave. Examples: a request is newly rejected; a field it read is missing or has another type; a status code it relied on changed; a value's meaning changed.
     - COMPATIBLE: existing correct clients keep working. Examples: new optional fields; previously failing requests now succeed; fixes of crashes that clients could not have relied on.
     - UNCLEAR.
   - **`contract_specified`:**
     - SPECIFIED: the **before** contract explicitly states the behaviour that changed, such as that status, that field, that constraint or that default.
     - UNSPECIFIED: the contract is silent about it.
3. **`confidence`:** 1 = guess, 2 = probable, 3 = certain from the code.
4. **`locators`:** `file:line` in `after/` or `diff.patch`, plus the contract location if SPECIFIED.
5. **`rationale`:** at most 40 words, neutral, describing the behaviour before and after.

Judge only what the code does. Do not judge whether the change is a good idea.

## Output
- `codes_<YOUR_ID>.csv` with the header `item_id,observable_change,change_kind,client_impact,contract_specified,confidence,locators,rationale`. Include one row per item, in `items.csv` order.
- `codes_report_<YOUR_ID>.md`: a short report covering hard cases and any item you could not open.

## Rules
- Read nothing outside this directory, except the one file `../../../research/09_collab/PROTOCOL.md` if it exists.
- Do not use git history, the network, or other packages.
- Do not execute any item code. Your own read-only helper scripts (`python3 -I -B`) are fine; keep them under `codes_work_<YOUR_ID>/`.
- Every search command must name explicit paths inside this directory.
- Never copy secrets or personal names into your outputs.
