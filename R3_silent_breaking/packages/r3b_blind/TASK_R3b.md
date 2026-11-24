# Blind contract review: does the API contract specify the behaviour that a commit changed?

You are a blind coder. Work only inside this package directory. Your coder ID is the `YOUR_ID` given in the prompt.

## What you get
`items.csv` lists the items. Each item is one commit to a REST service that changed production source code. Each item has its own folder `<item_id>/`:
- **`item.md`:** the repository name, language and touched files.
- **`diff.patch`:** the commit's changes.
- **`before/` and `after/`:** the touched files before and after the commit.
- **`contract/`:** **all** OpenAPI/Swagger documents of the repository as they were **before** the commit, complete. `contract/INDEX.md` lists them with line counts. Large documents are complete; search them, for example with `grep -n` on the path or field names.

## What to decide, per item
1. **`changed_behaviour`:** one neutral sentence on the HTTP-observable behaviour that changed, such as a status, a field, a validation rule, a default or a side effect. Write `NONE` if you find no observable change.
2. **`affected_operation`:** the affected HTTP operation or operations, as `METHOD /path`. Separate several with `;`. Write `UNKNOWN` if you cannot determine any.
3. **`contract_operation`:**
   - PRESENT: an affected operation is described in `contract/`. Give **`op_locator`** = `contract/<file>:<line>` of its path entry.
   - ABSENT: documents exist, but none describes the operation.
   - NO_CONTRACT: no usable document.
   - UNCLEAR.
4. **`contract_specified`:**
   - **SPECIFIED:** the contract explicitly states the behaviour that changed. Examples: the status code in question, the field in question, the constraint (pattern, min, max, required), the default value, or a description sentence stating the behaviour. Give **`spec_quote`**: at most 25 words copied verbatim from the contract.
   - **UNSPECIFIED:** the contract is silent about that behaviour, even if the operation itself is described.
   - **UNCLEAR.**
5. **`confidence`:** 1 = guess, 2 = probable, 3 = certain.
6. **`rationale`:** at most 30 words.

## Output
- **`codes_<YOUR_ID>.csv`.** Header:
  `item_id,changed_behaviour,affected_operation,contract_operation,op_locator,contract_specified,spec_quote,confidence,rationale`
  One row per item, in `items.csv` order. Quote fields that contain commas.
- **`codes_report_<YOUR_ID>.md`.** A short report covering hard cases.

## Rules
- Read nothing outside this directory.
- Do not use git, the network, or other packages.
- Do not execute item code. Read-only helper scripts (`python3 -I -B`) are fine; keep them under `codes_work_<YOUR_ID>/`.
