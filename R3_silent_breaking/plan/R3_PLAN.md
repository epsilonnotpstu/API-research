# R3 pre-registration: silent behavioural changes in REST APIs
Claude (supervisor-delegated), 2026-11-17. Draft v1.

**Freeze order:**
1. This plan, the scorer and its self-test are frozen in `r3_plan_freeze.sha256` before mining (T53).
2. The candidate pool is frozen by the miner before sampling.
3. The packages are frozen before any coder runs.
4. The outputs are frozen before scoring.

Novelty check: `../notes/NOVELTY.md`.

## Motivation
Spec-diff tools (oasdiff, openapi-diff, AutoGuard) can only report changes that appear in an OpenAPI document. If a service changes what an operation does, for example a status code, input validation, a default value or response content, without changing its contract, consumers are not warned. We measure how often this happens in real REST service histories, what kinds of change it involves, how many would break clients, and how many would stay invisible even to a contract generated from the code.

## Research questions
- **RQ1 (prevalence).** Of the commits that change operation-implementing production code without touching the checked-in contract document, what share change the observable behaviour of an API operation? What share do so in a client-breaking way?
- **RQ2 (kinds).** What kinds of observable change are they, using a closed taxonomy?
- **RQ3 (visibility).** What share of the breaking silent changes would a contract *generated from code* also miss? That is, the change edits no contract-annotation line or swagger comment annotation.
- **RQ4 (documentation lag, descriptive).** How often is the checked-in contract for the affected operation updated within 90 days after the change?

## Corpus and sampling (T53, Codex miner, hypothesis-blind)
**Repositories.** The 54 bare clones in `/run/media/afridi/Shared Data/api_research_upstream/` (the R1 corpus: 34 T45–T49 repositories and 20 T50 repositories). All are Java/Kotlin/Go REST services with a checked-in OpenAPI/Swagger document.

**Window.** Non-merge commits on the default branch, committed from 2023-01-01 up to the recorded HEAD.

**Candidate commit.** A commit is a candidate when all of the following hold:
1. It modifies at least one production behaviour-path file. The T46 definition is used: Java/Kotlin/Go server sources (handlers, controllers, resources, routes, DTOs, models, validators, serializers, error mapping), excluding tests, examples, generated, vendored and build files.
2. It does **not** modify any checked-in OpenAPI/Swagger document. The T46 document definition is used, including `$ref`-reached files.
3. It is codeable: at most 400 changed lines across behaviour-path files, at most 8 behaviour-path files, and no file only reformatted or renamed.
4. It is not authored by a bot: dependabot, renovate, or a `[bot]` suffix. The check uses the author field only, read in a scratch process, and the author is never recorded.

**Pool and sample:**
- The pool (`pool4.json`) is frozen with its hash before any candidate is opened.
- **Sample:** 3 candidates per repository, drawn uniformly with seed `20261117` from that repository's pool. A repository with fewer than 3 candidates contributes all of them.
- That is at most 162 commits. Each commit is a cluster; repositories are the higher-level cluster.

**No reading before freezing.** The miner opens no sampled commit before the pool and sample are frozen. After freezing, it builds the packages without judging behaviour.

## Packages (blind)
Each item is one commit, with ID `Bnnn`, shuffled with a salt stored only in `key/`. It contains:
- `diff.patch`: the commit's diff restricted to the behaviour-path files;
- `before/` and `after/`: the full parent and child versions of those files, at most 8 files;
- `contract/`: the parent's checked-in OpenAPI document, projected to the operations whose path or handler appears in the touched files, plus `$ref` closure. If no operation can be mapped mechanically, the whole document is projected to at most 2,000 lines;
- `item.md`: repository name and file list.

**Withheld from coders:**
- the commit message;
- the author and date;
- issue or PR references;
- later history.

Leakage, privacy and display filters are as in T49/T50.

**Mechanical fields, computed by the miner and stored in `key/` only:**
- `annotation_touched`: the diff adds or removes a line containing a JVM contract annotation (the T46 list: `@ApiResponse`, `@Operation`, `@Schema`, `@Parameter`, `@ResponseStatus`, `@NotNull`, `@Size`, `@Pattern`, `@Valid`, `@RequestParam(required…)` and the rest of that list) or a Go swagger comment annotation (`// @Router`, `// @Success`, `// @Failure`, `// @Param`, `// swagger:`);
- `spec_updated_90d`: whether any checked-in contract document of the repository changes within 90 days after the commit.
  - This repository-level field is what H-R3-2 uses.
  - It over-counts updates, so H-R3-2 is conservative.
  - A per-operation refinement after coding is descriptive only.

## Coding (blind; 2 GPT coders G1/G2 and 2 Claude coders H1/H2)
**Task file.** `TASK_R3.md`. Coders see only the package. Per item they code:
- **observable_change:** YES, NO or UNCLEAR. Does some HTTP request to some operation get a different observable outcome (status, headers, body content or shape, accepted or rejected input, side effects visible through the API) after the commit than before?
- **change_kind:** for YES items only, one primary kind from:
  - STATUS_OR_ERROR_MAPPING;
  - INPUT_STRICTER;
  - INPUT_LOOSER;
  - DEFAULT_OR_OPTIONALITY;
  - RESPONSE_CONTENT;
  - RESPONSE_SHAPE;
  - HEADER_OR_MEDIA_TYPE;
  - AUTHZ_OR_AUTH;
  - SIDE_EFFECT_OR_STATE;
  - ORDERING_PAGINATION_LIMITS;
  - OTHER.
- **client_impact:** for YES items only. BREAKING means a client that worked against the parent behaviour can fail or misbehave. COMPATIBLE is the alternative, and UNCLEAR is allowed.
- **contract_specified:** for YES items only. SPECIFIED means the parent contract states the affected behaviour, so the change also creates a contract divergence. UNSPECIFIED means it does not.
- confidence 1–3, locators, and a rationale of at most 40 words.

**Final codes.** The GPT final code for a field is the agreed value, and UNCLEAR when the two coders disagree. The Claude final code follows the same rule.
- Primary estimates use the GPT final codes, as in R1.
- The Claude final codes are the cross-family check.

## Hypotheses and estimates
**E-R3-1 (RQ1, estimate).** Share of sampled commits with a YES observable change, and share with a BREAKING change.
- Each share is reported with a Wilson 95% CI, and a repository-cluster bootstrap CI (2,000 resamples, seed 1).
- No threshold.

**H-R3-1 (RQ3, primary).** Among BREAKING items, more than half edit no contract annotation (`annotation_touched = false`), so a code-generated contract diff would also miss them.
- Test: one-sided exact binomial against 0.5, p < .05.
- **INSUFFICIENT** if fewer than 10 BREAKING items.

**H-R3-2 (RQ4, secondary).** Among BREAKING items whose parent contract SPECIFIED the behaviour, fewer than half see a contract update within 90 days.
- Test: one-sided exact binomial against 0.5, p < .05.
- **INSUFFICIENT** if fewer than 8 such items.

**H-R3-3 (reliability).** Cross-family κ, GPT final vs Claude final, on `observable_change` restricted to YES/NO items, is at least 0.6.
- **INSUFFICIENT** if fewer than 30 items.

**Descriptives:**
- the RQ2 kind distribution;
- `client_impact` × kind;
- `contract_specified` × `client_impact`;
- per-language and per-repository results;
- within-family κ for every field;
- leave-one-repository-out for E-R3-1.

## Stop rules and deviations
- Each blind role runs once. Usage-limit interruptions are resumed in the same session.
- The scorer is frozen before mining. A later change is allowed only as a mechanical fix, disclosed in `R3_DEVIATIONS.md` before any score is reported.
- If the pool has fewer than 60 sampled commits, E-R3-1 is still reported. Hypotheses whose minima are not met are INSUFFICIENT.
- A human spot-check of 20 items by the author is planned after scoring. It is reported separately.
