# Blind vulnerability review: what would a black-box API tester need to expose this flaw?

You are a blind coder. Work only inside this package directory. Your coder ID is the `YOUR_ID` given in the prompt.

## What you get
`items.csv` lists the items. Each item is one published security advisory for a REST service, together with the source-code commit that fixed it. Each item has its own folder `<item_id>/`:
- **`item.md`:** the repository name, language, CWE ids, the advisory summary and description (links and reporter credits removed), and the touched source files.
- **`diff.patch`:** the fix commit's changes to production source files.
- **`before/` and `after/`:** the touched source files before the fix (vulnerable) and after the fix.
- **`contract/`:** the service's OpenAPI/Swagger documents as they were **before** the fix. Large documents are truncated to 3,000 lines. `contract/INDEX.md` lists all contract files of the repository with their sizes.

You do not get the commit message, the author, dates, or later history.

## What to decide, per item
1. **`ac_relevant`:** YES, NO or UNCLEAR.
   - **YES** if the vulnerability is an **access-control flaw reachable through an HTTP operation of this service**. That means a wrong decision about one of:
     - who may perform which operation;
     - on which object;
     - on which properties of it;
     - whether the operation requires authentication at all.
   - **NO** for:
     - cryptography, token or signature validation, password-reset or login-flow logic;
     - session fixation, CSRF;
     - SSRF, injection, path traversal used to read files, DoS;
     - flaws only in a client library or CLI;
     - flaws not reachable through this service's HTTP API.
   - **UNCLEAR** only if the material does not let you decide.
2. **If YES, fill in the fields below** (otherwise write NA in each):
   - **`ac_kind`:** the single primary kind:
     - `OBJECT_LEVEL`: a principal can read or act on **another principal's object** of a type it may otherwise access (BOLA/IDOR).
     - `FUNCTION_LEVEL`: a principal can invoke an **operation reserved for another role or privilege** (BFLA, privilege escalation through an endpoint).
     - `PROPERTY_LEVEL`: a principal can **read or write properties** of an object beyond its rights (mass assignment, excessive data exposure of fields).
     - `MISSING_AUTHENTICATION`: the operation can be called **without any credentials** although it should require them.
     - `TENANT_ISOLATION`: a principal can cross an **organisation, tenant, realm, project or namespace boundary**.
     - `OTHER`.
   - **`principals_needed`:** the **minimal black-box test setup** in which a tester sending HTTP requests could observe the violation:
     - `NONE`: one anonymous request (no credentials) suffices.
     - `ONE`: a single authenticated principal suffices, for example one user who can grant itself a role or set a forbidden property.
     - `TWO_SAME_ROLE`: two principals of the same role are needed, for example user B reads user A's object.
     - `TWO_ROLES`: principals of two different privilege levels or roles are needed, for example a viewer calls an admin-only operation and must be compared with an admin.
     - `UNCLEAR`.
   - **`observable_via_http`:**
     - YES: the violation shows in HTTP responses, either the status or body of the offending call, or a later call that reveals the effect.
     - NO: it is visible only through side channels such as logs, the database or e-mail.
     - UNCLEAR.
   - **`contract_operation`:**
     - PRESENT: the vulnerable HTTP operation (path and method) is described in the `contract/` documents.
     - ABSENT: there are contract documents, but not for this operation.
     - NO_CONTRACT: no usable contract document was provided.
     - UNCLEAR.
   - **`contract_security`:** only if `contract_operation` is PRESENT, otherwise NA.
     - DECLARED: the contract declares a security requirement that applies to that operation, at operation level or globally (`security:` with a defined security scheme).
     - NOT_DECLARED.
     - UNCLEAR.
   - **`policy_in_contract`:**
     - YES: the contract states, or lets one directly derive, the **specific access rule that was violated**. Examples: "only the owner may…", a role or OAuth scope required for this operation, a property marked `readOnly` that was writable, a tenant parameter whose binding to the caller is stated.
     - NO: the contract does not state the rule. A bare security scheme without the rule counts as NO.
     - UNCLEAR.
   - **`fix_location`:** where the fix mainly acts:
     - `HANDLER`: a controller or route handler method;
     - `MIDDLEWARE_FILTER`: a filter, interceptor, security configuration, route-level guard or permission annotation;
     - `SERVICE_LOGIC`;
     - `DATA_QUERY`: scoping a query or repository lookup by owner or tenant;
     - `MODEL_BINDING`: allow-listing or ignoring DTO fields;
     - `OTHER`.
3. **`confidence`:** 1 = guess, 2 = probable, 3 = certain from the material.
4. **`locators`:** `file:line` in `diff.patch` or `after/`, plus the contract location if relevant.
5. **`rationale`:** at most 40 words, neutral. State who could do what before the fix.

Judge only from the provided material. Do not judge the advisory's severity score.

## Output
- **`codes_<YOUR_ID>.csv`:**
  - header: `item_id,ac_relevant,ac_kind,principals_needed,observable_via_http,contract_operation,contract_security,policy_in_contract,fix_location,confidence,locators,rationale`;
  - one row per item, in `items.csv` order;
  - quote any field that contains commas.
- **`codes_report_<YOUR_ID>.md`:** a short report covering hard cases and any item you could not open.

## Rules
- Read nothing outside this directory.
- Do not use git history, the network, or other packages.
- Do not execute any item code. Your own read-only helper scripts (`python3 -I -B`) are fine; keep them under `codes_work_<YOUR_ID>/`.
