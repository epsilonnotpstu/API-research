# Blind proposition-only reading (control)

**Supervisor authorization:** this task overrides the general instruction in `research/AGENTS.md` / `09_collab/PROTOCOL.md` to read `COLLAB_BOARD.md` or coordinator task files. Do not read the board or any coordinator task files. Read only `../../../09_collab/PROTOCOL.md` and this task file.

## What you are given
Only `items.csv` in this directory. Each row has a proposition of the form `"<METHOD> <path>: contract says <X>; implementation does <Y>"`. There are **no source files**. Code each item **from the proposition text alone**, using your general knowledge of the named framework or language where it helps. Do not try to locate the source anywhere else.

## What you code (two fields per item)

### 1. `divergence_kind`
This concerns the implementation behaviour Y in the proposition. The question: **is Y produced by project code that evidently targets Y?**
- **DELIBERATE:** Y is produced by project code that evidently targets Y. For example:
  - an explicit guard, validation or required flag;
  - explicit status or response construction;
  - an explicit serialization, naming or type choice;
  - an explicit branch handling the case;
  - a declared route or handler;
  - a data-model choice of field type or name.
- **ACCIDENTAL:** Y is a side effect of an omission or oversight. For example:
  - an unhandled exception, null dereference or unboxing;
  - a missing branch or missing default handling;
  - a header or content type that is not set;
  - a framework default the code does not address;
  - an ordering error (for example, parsing before a guard);
  - a wrong variable or cache reuse.
- **UNCLEAR:** the given artifacts do not allow a decision.

### 2. `contract_specificity`
This concerns the contract statement X in the proposition.
- **SPECIFIC:** the contract makes an explicit, dedicated statement about this behaviour. For example: prose description, an explicit default, an explicit status or media type, or an operation-specific constraint.
- **GENERIC:** X comes from boilerplate, generator defaults, an inherited or shared schema, or silence. For example: an operation that is not declared, `required` that is absent, or a type default of a schema.
- **UNCLEAR.**

Use UNCLEAR only when the text gives no basis at all; otherwise give your best judgement with a low confidence.

## Output
Write `codes_<YOUR_ID>.csv` with these columns, one row per item, in `items.csv` order:
`item_id, divergence_kind, contract_specificity, confidence, rationale`
- `confidence`: 1, 2 or 3. `rationale`: at most 30 words.

Also write `codes_report_<YOUR_ID>.md` (Bengali; technical terms in English): method, difficult items, limitations.

## Rules
- Your first command must be `cat TASK_CODE.md`.
- Do not open, list or search anything outside this directory except `../../../09_collab/PROTOCOL.md`. No network.
- Write outputs only in this directory. Do not judge which artifact is right or wrong.
- YOUR_ID is supplied at launch.
