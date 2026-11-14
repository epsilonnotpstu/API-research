"""Render the reviewed catalogue with real source locators and read-only exposure rows."""
from pathlib import Path
import json
import re

root = Path("08_experiments/E5_codemut")
catalogue = json.loads((root / "sites.json").read_text())
exposure = json.loads((root / "exposure.json").read_text())
by_operation = {(r["sut"], r["path"], r["method"]): r for r in exposure["operations"]}
lines = ["""# E5 implementation mutation operators — T19

The tool implements five operator families as **reviewed, digest-pinned exact
edits**, not arbitrary Java AST rewriting. Every site is reviewed catalogue
data in `sites.json` (row key `site_id`). All runtime effects below are **[H]**:
no Java compilation, SUT execution or mutation kill was observed in T19.
Synthetic safety tests do not establish real Java compilation
(`test_codemut.py`; `../../09_collab/logs/T19_scratch/tests.txt`, final summary).

## Operator-level expectations

All five inject on the IMPL side. The L1 expectation describes the newly inserted
defect's intended origin; it does not relabel pre-existing SPEC/BOTH/TEST faults.
Codebook: `08_experiments/R1_triage_codebook.md:90–114,228–259`;
current evidence: `08_experiments/E1_pilot/pilot_results/PILOT_SUMMARY.md:39–52,79–112`
and `08_experiments/E2_labelling/FINAL_LABELS.md:18–24`.

| Operator | Expected L1 / L2 | [H] conformance signal when exposed | Required distinction |
|---|---|---|---|
| DROP_VALIDATION | IMPL / I-ACCEPT-INVALID; I-CRASH if it instead crashes | INVALID_ACCEPTED for spec-invalid → 2xx; SERVER_ERROR for a causal 5xx | Revalidate the actual request with the unchanged spec; binding, service or persistence validation can still reject it. |
| WRONG_STATUS | IMPL / I-RESP-CONTRACT | UNDOCUMENTED_STATUS, only without applicable exact/range/default response | A schema-free default can make the mutation invisible; do not pick 503 and then misinterpret ENV policy. These sites use 418. |
| DROP_NULL_CHECK | IMPL / I-CRASH | SERVER_ERROR | Require an absence/null witness that reaches the removed guard. Existing crashes on the same path are not new ground truth. |
| RESP_FIELD | IMPL / I-RESP-CONTRACT | RESPONSE_SCHEMA for a missing required field | Dropping an optional field is usually invisible. WRITE_ONLY targets serialization while retaining setters/input binding; verify framework behavior at runtime. |
| REJECT_VALID | IMPL / I-REJECT-VALID | VALID_REJECTED, optionally UNDOCUMENTED_STATUS | Need a control 2xx for the identical request and equivalent state; spec-valid syntax alone does not prove resource existence or business validity. |

Signal implementation: `08_experiments/tools/conformance.py:399–442`.
Market's 406 rejection convention needs the separately reported SUT oracle
(`08_experiments/R1_triage_codebook.md`, §10.8;
`08_experiments/E1_pilot/harness_v2/suts/market.env`, REJECT_STATUSES_DEFAULT).
No strict-only missing-property policy is invented here.

## Exposure evidence and limits

`exposure.json` records a frozen selection of one **complete seed-1 baseline per
SUT**, its run/exchange hashes, and operation-level status counts. It is read-only
evidence of captured requests, not bytecode/site coverage. These latest baselines
can be from negative-data variants and are **not** matched E5 controls. A new
same-harness control build/run is required. `evidence_id` identifies rows below.
The URI templates are matched to the original spec by method/path; no source or
saved exchange was changed (`../../09_collab/logs/T19_scratch/make_catalogue.py`,
exposure loop; `exposure.json`, `selection` and `runs`).
"""]

for sut in catalogue["roots"]:
    run = exposure["runs"][sut]
    lines += [f"\n## {sut}\n", f"Source root: `08_experiments/_external/emb/{catalogue['roots'][sut]}/`.\n",
              f"Exposure source: `{run['run_dir']}/exchanges.jsonl`; `run.json` was complete, baseline, seed 1 (`exposure.json`, `runs.{sut}`).\n"]
    for site in [s for s in catalogue["sites"] if s["sut"] == sut]:
        signals = ", ".join(site["expected_conformance_signal"]) or "none guaranteed under the current oracle"
        lines += [f"\n### {site['site_id']} — {site['operator']}\n",
                  f"- Site: `{site['evidence']}`; exact before/after/file digest: `sites.json`, `{site['site_id']}`.\n",
                  f"- [H] Expected: IMPL / {site['expected_L2']}; signal: {signals}.\n",
                  f"- Operations: {', '.join('`' + o['method'].upper() + ' ' + o['path'] + '`' for o in site['operations'])}.\n"]
        spec_path = Path('08_experiments/_external/emb/openapi-swagger') / (sut + '.json')
        spec_text = spec_path.read_text()
        contract = []
        for op in site['operations']:
            needle = json.dumps(op['path']) + ': {'
            assert spec_text.count(needle) == 1
            contract.append(str(spec_path) + ':' + str(spec_text[:spec_text.index(needle)].count('\n') + 1))
        schema_names = {'scout-api': 'RolesView', 'swagger-petstore': 'Pet', 'market': 'ProductDTO', 'cwa-verification': 'RegistrationToken'}
        if site['operator'] == 'RESP_FIELD':
            needle = json.dumps(schema_names[sut]) + ': {'
            contract.append(str(spec_path) + ':' + str(spec_text[:spec_text.index(needle)].count('\n') + 1))
        lines += ['- Original contract evidence (operation/response schema): ' + ', '.join('`' + x + '`' for x in contract) + '.\n']
        for op in site["operations"]:
            row = by_operation.get((sut, op["path"], op["method"]))
            if row:
                lines += [f"- Captured exposure: {row['requests']} requests, statuses `{json.dumps(row['statuses'], sort_keys=True)}`; "
                          f"first 2xx line `{row['first_2xx_exchange']}`, first nonempty JSON 2xx line `{row['first_nonempty_2xx_exchange']}` "
                          f"(`exposure.json`, `{row['evidence_id']}`; `{run['run_dir']}/exchanges.jsonl:{row['first_exchange']}`).\n"]
            else:
                lines += [f"- No matching captured request in the selected baseline for {op['method'].upper()} {op['path']} "
                          f"(`exposure.json`, `runs.{sut}` and `operations`).\n"]
        lines += [f"- Conditions/limitations: {site['conditions']}\n", f"- Witness plan: {site['witness_plan']}\n"]

lines += ["""
## First E5 batch: ten proposed mutants (2–3 per SUT)

All choices remain [H] pending compilation, controlled HTTP witnesses and source/
image verification. Exact site IDs below can be passed to `codemut.py --site`.
The subset is also `pilot=true` in `sites.json`.

| SUT | First sites | Why these before the alternatives |
|---|---|---|
| scout-api | scout-wrong-status; scout-drop-null; scout-reject-valid | roles had a captured 200; tags had 95 captured 200s, including absent optional query inputs. Expect distinct status/crash/rejection effects; repeat the same-state witnesses to separate existing faults (`exposure.json`, scout rows). |
| swagger-petstore | petstore-response-field; petstore-reject-valid | A nonempty JSON findByStatus response carries required name. getPetById is reached, but this selected negative-data control has no 200 there: establish a clean seeded-pet 200 before calling a later 400 a reject-valid kill (`exposure.json`, pet rows). |
| market | market-wrong-status; market-drop-null; market-response-field | The listing has a nonempty 200 with price, while product detail has 44 captured 404s. These avoid inventing a valid registration fixture and permit status, absence and field witnesses (`exposure.json`, market rows). |
| cwa-verification | cwa-drop-validation; cwa-drop-null | Registration binding and absent-TAN verification are reached with 400/404. Neither requires the missing test-result server or a successful token response. Registration's selected baseline has zero 2xx, so defer its wrong-status/response-field proposals until a manual GUID-control 201 witness exists (`exposure.json`, cwa rows). |

For field mutants, force JSON and nonempty response objects. For crash mutants,
save the new stack site as well as status. For every mutant, retain invalid or
unexposed candidates in the selection ledger; do not exclude survivors after
looking at attribution outcomes. Compile-invalid, equivalent/oracle-blind,
unexposed, killed and flaky are separate outcomes. The injected site is code-side
ground truth; causal exposure and the observed L1/L2 still require independent
review (`sites.json`, each site's `conditions`; codebook §5 and §10).
"""]
(root / "OPERATORS.md").write_text("".join(lines))
