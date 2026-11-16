#!/usr/bin/python3
"""Render the Bengali report from audited aggregate records, without item keys."""
import csv
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    summary = json.loads((HERE / 'summary_t48.json').read_text())
    checks = json.loads((HERE / 'checks_t48.json').read_text())
    assert summary['accepted_T48'] == 40 and checks['tests']['passed']
    yields = list(csv.DictReader(io.StringIO((HERE / 'yield_t48.csv').read_text())))
    table = '\n'.join('| ' + ' | '.join([r['repo'], r['reviewed_phase1'], r['reviewed_phase2'],
                       r['reviewed_T48'], r['accepted_T48'], r['accepted_previous'], r['accepted_combined'],
                       r['previous_last_rank'] + ' → ' + r['last_reviewed_rank'], str(i)]) + ' |'
                       for i, r in enumerate(yields, 2))
    codes = ['ACCEPT', 'NOT_CONTRACT_RELATED', 'NEW_FEATURE_OR_ENDPOINT', 'REFACTOR_OR_RENAME',
             'GENERATED_OR_DOCS_ONLY_CHURN', 'BOTH_CHANGED_TO_NEW_BEHAVIOUR', 'NO_PARENT_MISMATCH',
             'TEST_OR_CLIENT_ONLY', 'TOO_LARGE_TO_ESTABLISH', 'OTHER']
    reasons = '\n'.join(f"| {code} | {summary['reason_code_counts'].get(code, 0)} |" for code in codes)
    report = f'''# T48 — Frozen pool2 continuation ও পৃথক V package

T48-এ **490টি candidate-এর final decision থেকে 40টি নতুন item** গৃহীত হয়েছে; accepted candidate **21টি**। T45–T47-এর 86টি মিলিয়ে নতুন corpus এখন **126টি item**। শুধু T48-এর জন্য **V01–V40** package তৈরি হয়েছে। Evidence: `08_experiments/E7_mining/summary_t48.json` (`reviewed`, `accepted_T48`, `accepted_candidates`, `accepted_combined_new`); `08_experiments/E7_mining/verification_t48.json` (`summary.items`)। নিচের সংক্ষিপ্ত mining path-গুলোর base `08_experiments/E7_mining/`।

pool2 পুনরায় freeze করা হয়নি। Task-start baseline-এর **6,169টি existing key file**, এবং মোট **6,175টি baseline file**-এর SHA-256 final comparison-এ একই আছে। এর মধ্যে `e7_key.csv`, `e8b_key.csv`, `corpus_key.csv`, `accepted_full.csv`, `accepted_full_t47.csv`, frozen source, `pool2.json`, `freeze2.json`, `mine2.py`, আগের pool/freeze ও `yield_t47.csv` অন্তর্ভুক্ত। Freeze record-এর pool/source/code hash-ও মিলেছে। Evidence: `key/preservation_t48_start.json`; `key/preservation_t48_final.json` (`unchanged`, `existing_key_files`, `total_baseline_files`, `hashes`); `test_t48.py::ContinuationTests.test_all_existing_key_and_freeze_bytes_preserved`; `checks_t48.json`।

Review-এর প্রথম pass-এ `yield_t47.csv`-এর order-এ শুধু `T47 target reached` repo-গুলি নেওয়া হয়েছে, সর্বোচ্চ rank 150 পর্যন্ত। দ্বিতীয় pass-এ একই repo order-এ বাকি eligible rank সর্বোচ্চ 250 পর্যন্ত নির্ধারিত ছিল। প্রতিটি repo তার প্রথম unreviewed rank থেকে এগিয়েছে; আগের pass-এর rank দ্বিতীয়বার নেওয়া হয়নি। T45–T48 মিলিয়ে প্রতি repo-তে cap 10। First pass-এ **441 candidate / 36 item**, second pass-এ **49 candidate / 4 item** হয়েছে। Evidence: `review_t48.py::plan`, `review_t48.py::next_row`; `finalize_t48.py::audit`; `summary_t48.json` (`phase1_reviewed`, `phase2_reviewed`, `phase1_accepted`, `phase2_accepted`)।

Acceptance gate আগের মতো: existing operation, exact parent contract ও implementation locators, resolving patch, evidence, confidence, contract kind, mismatch/family এবং neutral proposition। IMPL acceptance-এ parent contract-এ প্রত্যাশিত আচরণ আগে থেকেই প্রতিষ্ঠিত। Proposition-এর রূপ `<METHOD> <path>: contract says <X>; implementation does <Y>`; package-এ verbatim আছে। Dedup identity repo + operation + fix family; exploratory 25 এবং সব T45–T47 item-এর সঙ্গে তুলনা হয়েছে। Direction বা অন্য property-এর quota/balancing ব্যবহার করা হয়নি। Evidence: `review_t48.py::accept`; `finalize_t48.py::audit`; `key/accepted_full_t48.csv`; `verification_t48.json` (`checks.verbatim_propositions`)।

প্রতিটি candidate-এর নিজস্ব `review_status`, `reason_code`, specific reason (1–25 words), sanitized patch path/hash এবং review-depth record আছে। **268টি conservative scripted scope-triage record**, এবং বাকি **222টি candidate-এর অতিরিক্ত model patch review** আছে। Script প্রতিবার শুধু current candidate-এর patch খুলে final decision দেওয়ার পরে পরেরটিতে গেছে; ambiguous screen-এ থেমেছে। Accepted candidate-গুলিতে exact parent evidence ও resolving patch যাচাই করা হয়েছে। সব 490টি candidate-এর সমান গভীর manual parent comparison হয়েছে—এমন দাবি করা হচ্ছে না। Evidence: `triage_t48.py`; `review_t48.py::decide`; `key/t48_triage/`; `key/review_decisions_t48.csv` (490 data row, `review_depth`); `summary_t48.json` (`conservative_static_triage`, `additional_model_patch_reviews`)।

Per-repo table-এ reviewed হলো T48 candidate count; accepted হলো T48 item count। পূর্বের accepted কেবল T45–T47। শেষের column `yield_t48.csv`-এর line number।

| Repo | Pass 1 reviewed | Pass 2 reviewed | T48 reviewed | T48 accepted | পূর্বের accepted | Combined | Pool2 rank: পূর্বে → শেষে | CSV line |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{table}

**Stopping reason:** দ্বিতীয় pass-এ apicurio-registry rank **155**-এর সম্পূর্ণ final decision-এর পরে T48 count **40**, অর্থাৎ ≥40। ওই repo একই সঙ্গে combined cap 10-এ পৌঁছেছে। এর পরে আর কোনো candidate patch preview বা review হয়নি। Second pass-এ Iced-Latte-র 44টি এবং apicurio-registry-র 5টি candidate নেওয়া হয়েছে। Table-এর zero-review row ও target-এ থেমে থাকা repo-গুলি zero-yield evidence নয়। Evidence: `summary_t48.json` (`stopping_reason`, `final_repo`, `final_rank`, `preview_record`); `yield_t48.csv:3`, `yield_t48.csv:6`; `finalize_t48.py::audit`।

Reason-code distribution candidate-level; ACCEPT-এর 21 candidate থেকে 40 item এসেছে। Evidence: `summary_t48.json` (`reason_code_counts`, `review_status_counts`)।

| reason_code | Candidates |
|---|---:|
{reasons}

Status totals: **accepted 21, rejected 363, deferred 106**। `NO_PARENT_MISMATCH` মানে bounded review-এ parent discrepancy প্রতিষ্ঠিত হয়নি; deferred বা rejected screen-কে negative ground truth হিসেবে ব্যবহার করা যাবে না। Evidence: `review_t48.py::decide`; `key/review_decisions_t48.csv` (`review_status`, `reason`, `review_depth`); `summary_t48.json` (`review_status_counts`)।

কেবল aggregate direction counts নিচে আছে। Evidence: `summary_t48.json` (`T48_direction_counts`, `combined_new_direction_counts`)।

| Set | SPEC | IMPL | BOTH | Total |
|---|---:|---:|---:|---:|
| T48 new | 21 | 19 | 0 | 40 |
| T45 + T46 + T47 + T48 new | 70 | 55 | 1 | 126 |

নতুন output `08_experiments/E2_labelling/e10_blind/`-এ শুধু V01–V40, চার-column `items.csv` (`item_id,repo,operation,proposition`), প্রতি item-এর `contract/`, `impl/`, এবং README আছে। Private output: `key/e10_key.csv` (e8b key-এর একই schema, `set=new`, `source_task=T48`), `key/accepted_full_t48.csv`, `key/review_decisions_t48.csv`। নতুন HMAC shuffle salt ও source-to-V mapping শুধু `key/e10_shuffle_salt.txt` ও `key/e10_shuffle_mapping.csv`-তে আছে; salt আগের দুই salt থেকে আলাদা। Publisher existing destination/key file পেলে overwrite প্রত্যাখ্যান করে। পুরোনো blind package খোলা বা পরিবর্তন করা হয়নি; coordinator-এর m1/m1f copies তৈরি করা হয়নি। Evidence: `build_t48.py::v_order`, `build_t48.py::prepare`, `build_t48.py::publish`; `test_t48.py::ContinuationTests.test_real_package_contains_only_V_rows_and_separate_roles`; `test_t48.py::ContinuationTests.test_private_salt_and_mapping_deterministic_and_not_delivered`; `checks_t48.json` (`old_blind_packages_read`, `existing_package_replacement`); `09_collab/logs/T48_scratch/completion.json`।

Package size **40 item, 1,606 file, 7,606,198 bytes**: **1,420 contract file**, **184 implementation file**, table ও README। Role count directory-এর দ্বিতীয় path component থেকে হিসাব করা হয়েছে; implementation namespace-এ `contract` শব্দ থাকলে double count হয় না। **1,547টি source file** privacy/history redaction পেয়েছে, projected contract file **6টি**। Implementation whole parent file; প্রতি item-এ সর্বোচ্চ **8টি**, suggested helper omission **0**। Required locator সব আছে। Published disk bytes, key, full evidence ও mapping reconstruction-এর সঙ্গে হুবহু মিলেছে। Evidence: `verification_t48.json` (`summary`, `checks`); `key/e10_build_log.json` (`items.files`, `items.protected`, `package_hashes`); `checks_t48.json` (`omitted_helper_occurrences`, `maximum_implementation_files`); `build_t48.py::prepare`।

Cross-item build check-এ exploratory 25 + T45–T47 new 86 + T48 new 40, মোট **151টি item** ছিল। নতুন package-এর **18টি item flagged**; **39টি own-locator overlap incidence** retained, **3টি optional overlapping contract file occurrence** excluded। Actual manifests-এর independent all-pairs audit-এ **105 pair incidence / 51 flagged item**, যার **36 pair incidence** নতুন V destination-এ এবং **12 incidence** V source থেকে পুরোনো destination-এ। V source-এর প্রভাবে **5টি পুরোনো item**-এ overlap আছে; এদের মধ্যে **1টি** frozen key-র flags-এর বাইরে। সব নতুন relationship নতুন private audit-এ রাখা হয়েছে; আগের key বা flag বদলানো হয়নি। Evidence: `verification_t48.json` (`summary`); `key/e10_build_log.json` (`cross_item_pairs`); `key/e10_cross_item_all.json` (`all_pairs`, `newly_affected_prior_items`, `additional_prior_flags`, `summary`); `cross_audit_t48.py::main`।

⚠️ **Reference limitation:** cross-item exclusion-এর পরে **3টি item-এ 143টি local file-reference occurrence unresolved**। সব missing target ঠিক ওই **3টি excluded optional contract file occurrence**; কোনো required locator বাদ যায়নি। মোট local file-reference occurrence **16,479**, remote reference **0**। তাই delivered contract directories-কে সম্পূর্ণ standalone reference-closed specification বলা যাবে না। Large-spec projection-এর নিজস্ব local fragment check পাস করলেও mandatory cross-item exclusion সম্পূর্ণ closure সীমিত করেছে; পরের reader-কে source excerpts হিসেবেই এগুলো ব্যবহার করতে হবে। Evidence: `key/e10_reference_audit.json` (`missing_reference_incidents`, `affected_items`, `missing_references`); `reference_audit_t48.py::audit`; `test_t48.py::ContinuationTests.test_reference_exclusions_are_recorded_and_limited_to_cross_item_paths`; `checks_t48.json` (`unresolved_reference_targets_equal_mandatory_cross_item_exclusions`)।

**Preview record:** **1,364টি sequential event**, **490টি unique candidate**। Final prefix-এর বাইরে **0**, final decision ছাড়া **0**, prior final decision-এর আগে lookahead **0**। Ledger-এর candidate ordinal, event sequence, `final_decisions_before`, repo/rank এবং evidence set একসঙ্গে যাচাই হয়েছে। Current candidate ছাড়া evidence/probe access guard প্রত্যাখ্যান করে; target পূরণ হওয়ার পরে ভবিষ্যৎ patch খোলার চেষ্টাও কোনো Git read বা preview/evidence write-এর আগে ব্যর্থ হয়েছে। Tests-এ unknown candidate, আগের decision-এর আগে lookahead, completed candidate পুনরায় খোলা এবং unlogged evidence-এর corrupted synthetic ledger প্রত্যাখ্যাত হয়েছে। Evidence: `summary_t48.json` (`preview_record`); `key/t48_previews/`; `review_t48.py::require_current`, `review_t48.py::record_preview`; `finalize_t48.py::validate_previews`; `test_t48.py::PreviewRegressionTests`; `test_t48.py::ContinuationTests.test_real_preview_ledger_has_no_lookahead_or_undecided_evidence`।

**52টি test পাস**: আগের **36টি**, নতুন **16টি**, failure/error **0**। আগের T47 package tests unchanged test definitions দিয়েই isolated reconstruction-এর উপর চালানো হয়েছে; private old manifest-এর hashes-এর সঙ্গে তার bytes মিলেছে। Filesystem audit hook পুরোনো labelling package access block করেছে। ফলে এই run পুরোনো package-এর disk contents পুনরায় পরীক্ষা করেনি; বরং আগের tests-এর logic, frozen private manifests, এবং reconstructed source bytes যাচাই করেছে। New production package সরাসরি disk থেকে পরীক্ষা হয়েছে। Evidence: `09_collab/logs/T48_scratch/test_results.txt`; `09_collab/logs/T48_scratch/test_summary.json`; `run_tests_t48.py::read_boundary`, `run_tests_t48.py::main`; `test_t48.py`।

Parent provenance, whole implementation, corresponding child-content exclusion, message/history-literal scans, verbatim proposition, forbidden words, eight-file cap, package separation এবং fresh salt checks পাস। T44 privacy scans-এ **15টি auth fixture / 54টি value variant** দিয়ে package এবং সব candidate reason পরীক্ষা হয়েছে। Display filter-এ history/date/attribution এবং credential-key patterns চাপা হয়েছে; upstream code execute করা হয়নি। Evidence: `verification_t48.json` (`checks`, `auth_fixtures`, `auth_value_variants`); `test_t48.py::ContinuationTests.test_package_hashes_role_counts_privacy_and_leakage_assertions`; `review_t48.py::display`; `build.py::sanitize`, `build.py::prepare`।

⚠️ Threats: frozen correction-cue/path retrieval, rank bounds, cap এবং acceptance threshold coverage সীমিত করে। Conservative scope triage false negatives রাখতে পারে; বড়/ambiguous patch-এর parent mismatch প্রতিষ্ঠিত না-হওয়া defect না-থাকার প্রমাণ নয়। Framework annotation/validation, route wiring, serializer ও exception behaviour-এর কিছু conclusion static inference; confidence ও inference notes private evidence-এ আছে, runtime request করা হয়নি। Evidence: `triage_t48.py`; `key/accepted_full_t48.csv` (`confidence`, `inference_notes`, `proposition_check`); `key/review_decisions_t48.csv`; `yield_t48.csv`।

⚠️ 40টি item এসেছে 21টি candidate থেকে; shared error envelope-এর একটি candidate-এ একাধিক operation আছে। এগুলো স্বাধীন observation নয়। Cross-item own-locator exception, frozen prior flags, shared files এবং unresolved optional references reading context ও independence সীমিত করে। Eight-file cap required locator রাখলেও পূর্ণ runtime dependency context নিশ্চিত করে না। Lexical privacy/leakage checks সব personal name, semantic hint বা secret-এর অনুপস্থিতির নিশ্চয়তা নয়। Evidence: `summary_t48.json` (`accepted_candidates`); `key/e10_build_log.json`; `key/e10_cross_item_all.json`; `key/e10_reference_audit.json`; `verification_t48.json` (`checks`)।

কাজ offline: upstream bare clone-এ শুধু read-only `git --git-dir` access; network, upstream checkout/build/execution বা dependency install ব্যবহার হয়নি। নিজস্ব Python ও synthetic bare-repo tests চলেছে। Board পড়া হয়নি; শেষে একটিমাত্র Log line `>>` দিয়ে append করা হয়েছে। কোনও বাস্তব item-এর direction বা fix identifier report/package-এ নেই। Open question: mandatory cross-item exclusion-এ হারানো optional reference context পরের blind reading-এ যথেষ্ট কি না—এটি পরবর্তী reader assessment-এর বিষয়; T48 package বা frozen key এখানে বদলানো হয়নি। Evidence: `mine.py::git`; `build.py::prepare`; `build_t48.py::publish`; `09_collab/logs/T48_scratch/completion.json`; `09_collab/tasks/T48.md`।
'''
    with (ROOT / '09_collab/reports/T48_report.md').open('x') as stream:
        stream.write(report)


if __name__ == '__main__':
    main()
