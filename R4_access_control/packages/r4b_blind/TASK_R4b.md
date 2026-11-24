# Blind contract review: does the API contract describe the vulnerable operation and its access rule?

You are a blind coder. Work only inside this package directory. Your coder ID is the `YOUR_ID` given in the prompt.

## What you get
`items.csv` lists the items. Each item is one published security advisory about an access-control flaw in a REST service, together with the commit that fixed it. Each item has its own folder `<item_id>/`:
- **`item.md`:** repository name, language, CWE ids, the advisory summary and description, and the touched source files.
- **`diff.patch`:** the fix commit's changes to production source files.
- **`before/` and `after/`:** the touched source files before the fix (vulnerable) and after the fix.
- **`contract/`:** **all** OpenAPI/Swagger documents of the repository as they were **before** the fix, in full. `contract/INDEX.md` lists them with line counts. Large documents are complete; search them, for example with `grep -n` on the path.

## What to decide, per item
1. **`operation`:** the vulnerable HTTP operation or operations, as `METHOD /path` with the path as the server exposes it (for example `PUT /api/v1/users/{id}`). Separate several with `;`. Use the advisory, the diff and the route definitions in the code. Write `UNKNOWN` if you cannot determine any.
2. **`contract_operation`:**
   - **PRESENT:** at least one of these operations is described in a `contract/` document. The path may differ only by base path or parameter names, and the method must match.
   - **ABSENT:** documents exist, but none describes the operation.
   - **NO_CONTRACT:** no usable document. This means it is empty, unparseable, or not an API description of this service.
   - **UNCLEAR.**
   - If PRESENT, give **`op_locator`** = `contract/<file>:<line>` of the path entry (the line with the path key).
3. **`contract_security`:** only if PRESENT, otherwise write NA.
   - **DECLARED:** a security requirement applies to that operation, either operation-level `security:` or a global `security:` that is not overridden by an empty list, and it references a defined security scheme. Give **`sec_locator`** = `contract/<file>:<line>`.
   - **NOT_DECLARED.**
   - **UNCLEAR.**
4. **`policy_in_contract`:**
   - **YES:** the contract states, or lets one directly derive, the **specific access rule that was violated**. Examples:
     - "only the owner may…";
     - a role or OAuth scope required for this operation;
     - a property marked `readOnly` that was writable;
     - a statement binding a tenant or organisation parameter to the caller.
     Give **`policy_quote`**: at most 25 words copied verbatim from the contract.
   - **NO:** the contract does not state that rule. A bare security scheme, or a generic "requires authentication", is NO, unless the flaw is that authentication was missing.
   - **UNCLEAR.**
5. **`confidence`:** 1 = guess, 2 = probable, 3 = certain.
6. **`rationale`:** at most 30 words, neutral.

## Output
- **`codes_<YOUR_ID>.csv`.** Header:
  `item_id,operation,contract_operation,op_locator,contract_security,sec_locator,policy_in_contract,policy_quote,confidence,rationale`
  One row per item, in `items.csv` order. Quote fields that contain commas.
- **`codes_report_<YOUR_ID>.md`.** A short report covering hard cases and any item you could not open.

## Rules
- Read nothing outside this directory.
- Do not use git history, the network, or other packages.
- Do not execute item code. Read-only helper scripts (`python3 -I -B`) are fine; keep them under `codes_work_<YOUR_ID>/`.
