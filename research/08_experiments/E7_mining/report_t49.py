#!/usr/bin/python3
"""Write the aggregate Bengali report after every required audit passes."""
import csv
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KEY = HERE / 'key'
SCRATCH = ROOT / '09_collab/logs/T49_scratch'


def main():
    runpy.run_path(str(HERE / 'review_t49.py'))['guard']()
    summary = json.loads((HERE / 'summary_t49.json').read_text())
    verification = json.loads((HERE / 'verification_t49.json').read_text())
    audit = json.loads((SCRATCH / 'final_audit.json').read_text())
    tests = json.loads(sorted(SCRATCH.glob('test_summary_*.json'))[-1].read_text())
    assert tests['passed'] and tests['failures'] == tests['errors'] == 0
    assert all(verification['checks'].values()) and audit['changed_existing_files'] == 0
    with (HERE / 'yield_t49.csv').open() as stream:
        yields = list(csv.DictReader(stream))
    package = verification['summary']
    cross, refs = audit['cross_item_audit'], audit['reference_audit']
    counts = summary['reason_code_counts']
    table = '\n'.join('| {repo} | {previous_last_rank} | {reviewed_T49} | {last_reviewed_rank} | {accepted_previous} | {accepted_T49} | {accepted_combined} | {stopped} |'.format(**r) for r in yields)
    reasons = '\n'.join(f'| {code} | {counts.get(code, 0)} |' for code in sorted(counts))
    code_counts = summary['T49_direction_counts']
    all_counts = summary['combined_new_direction_counts']
    text = f'''# T49 — frozen pool2 continuation ও পৃথক U-package

Evidence paths: নিচে সংক্ষিপ্ত script/JSON/CSV নাম এবং `key/`-এর ভিত্তি `08_experiments/E7_mining/`; `final_audit.json` ও test summaries-এর ভিত্তি `09_collab/logs/T49_scratch/`। `E2_labelling/`-এর ভিত্তি `08_experiments/`। Function name, JSON field ও CSV repo row দিয়ে সংশ্লিষ্ট evidence চিহ্নিত করা হয়েছে।

T49 সম্পন্ন: **{summary['reviewed']} candidates**-এর final decision থেকে **{summary['accepted_candidates']} accepted candidates / {summary['accepted_T49']} items** পাওয়া গেছে। 40-এর আগে থামার কারণ: প্রতিটি eligible repo capped অথবা exhausted। Frozen pool2-তে 34 repo / 12,637 candidates আছে; এই continuation-এ ছয় repo-তে নতুন review হয়েছে। শেষে সব repo মিলিয়ে 14 capped এবং 20 exhausted। Evidence: `08_experiments/E7_mining/summary_t49.json` (`reviewed`, `accepted_candidates`, `accepted_T49`, `stopping_reason`); `08_experiments/E7_mining/yield_t49.csv` (repo rows)।

`yield_t48.csv:last_reviewed_rank + 1` থেকে একই repo order-এ rank অনুযায়ী review হয়েছে; নতুন rank limit বা retrieval চালানো হয়নি। Combined T45–T49 cap 10। প্রতিটি accepted candidate-এর সব প্রতিষ্ঠিত operation-এর `METHOD path` UTF-8/plain byte order-এ সাজিয়ে প্রথম দুইটি রাখা হয়েছে; repo-তে কম slot থাকলে সেই prefix আরও ছোট হতো। Selection function direction, confidence বা অন্য item property পড়ে না। প্রতিটি candidate-এর final decision পরবর্তী candidate খোলার আগে লেখা হয়েছে। ⚠️ এটি static parent contract/implementation ও resolving patch comparison; runtime execution হয়নি। Evidence: `09_collab/tasks/T49.md` requirements 1–4; `08_experiments/E7_mining/review_t49.py:plan`, `select_operations`, `require_current`; `finalize_t49.py:audit`।

নিচে সব repo দেখানো হয়েছে; `reviewed_T49` শূন্য হলে পূর্বের cap বা exhaustion-এর কারণে নতুন review হয়নি। প্রতিটি row-এর সরাসরি evidence `08_experiments/E7_mining/yield_t49.csv:repo`।

| Repo | T48 শেষ rank | T49 reviewed | শেষ rank | আগের items | T49 items | Combined | Stop |
|---|---:|---:|---:|---:|---:|---:|---|
{table}

Accepted candidates-এর মধ্যে 12টি থেকে একটি করে এবং 12টি থেকে দুইটি করে item রাখা হয়েছে। Cap-এর আগে valid operations-এর histogram: 12 candidates × 1, 6 × 2, 2 × 3, 2 × 4, 1 × 6, 1 × 37 = 81 operations। অতিরিক্ত **{summary['FIX_CAP_exclusions']} operations**-এ `review_status=accepted_capped`, `reason_code=FIX_CAP`; `REPO_CAP` exclusions {summary['REPO_CAP_exclusions']}। Candidate final rows 949 এবং cap-exclusion rows 45—মোট 994 rows private decision CSV-তে আছে। Evidence: `summary_t49.json:items_per_accepted_candidate`, `valid_operations_per_accepted_candidate`, `FIX_CAP_exclusions`; `key/review_decisions_t49.csv:review_status,reason_code`; `finalize_t49.py:audit`।

Candidate-level `reason_code` distribution নিচে; `ACCEPT` candidates গণনা করে, items নয়। Cap exclusions আলাদাভাবে উপরে দেওয়া হয়েছে। Evidence: `summary_t49.json:reason_code_counts,review_status_counts`; candidate statuses: accepted 24, rejected 818, deferred 107।

| reason_code | Candidates |
|---|---:|
{reasons}

Direction শুধু aggregate হিসেবে: T49 **SPEC {code_counts.get('SPEC', 0)}, IMPL {code_counts.get('IMPL', 0)}, BOTH {code_counts.get('BOTH', 0)}**। T45–T49 নতুন set মিলিয়ে 162 items: SPEC {all_counts.get('SPEC', 0)}, IMPL {all_counts.get('IMPL', 0)}, BOTH {all_counts.get('BOTH', 0)}। Direction target বা balancing করা হয়নি। Evidence: `summary_t49.json:T49_direction_counts,combined_new_direction_counts`; cap selection-এর regression tests `test_t49.py:CapRegressionTests`। Per-item direction, fix identifiers ও ID mapping কেবল `key/`-তে রাখা হয়েছে।

পৃথক package `08_experiments/E2_labelling/e12_blind/`-এ শুধু **U01–U36** আছে। `items.csv`-এর চারটি column `item_id,repo,operation,proposition`; propositions private accepted rows থেকে verbatim। প্রত্যেক item-এর `contract/` ও `impl/` আছে; README-এর bytes T48 builder-এর README-এর সমান। Fresh salt এবং mapping কেবল `key/e12_shuffle_salt.txt`, `key/e12_shuffle_mapping.csv`-তে। নতুন `key/e12_key.csv`-এর columns `e10_key.csv`-এর সমান; `key/accepted_full_t49.csv`-এর columns `accepted_full_t48.csv`-এর সমান এবং `candidate_id` আছে; সব নতুন row-এ `set=new`, `source_task=T49`। Evidence: `build_t49.py:prepare,full_bytes,publish`; `test_t49.py:ContinuationTests`।

Package size **{package['files']} files / {package['bytes']:,} bytes ({package['bytes'] / 1024 / 1024:.2f} MiB)**: contract {package['contract_files']}, implementation {package['implementation_files']}, table ও README 2 files। বড় spec-এর operation/reference projection {package['projected_files']} files; privacy/history/metadata redaction হয়েছে {package['redacted_files']} files-এ। Implementation files সর্বোচ্চ আটটি/item; own parent locator files retained। কিছু generated spec path-এ API mount prefix expanded থাকায় একটিমাত্র literal suffix match পাওয়া গেলে সেই পূর্ণ spec path-এর operation project করা হয়েছে; ambiguous match reject হয়। Parent source phrase পরে commit subject হিসেবে ব্যবহৃত থাকলে phrase-টিও redacted; leakage scanner শিথিল করা হয়নি। Evidence: `verification_t49.json:summary,checks`; `build_t49.py:project_yaml,prepare`; `test_t49.py:SyntheticSeparationTests`।

Cross-item check exploratory 25 + T45–T48 126 + T49 36 = **187 items** জুড়ে হয়েছে। নতুন package-এ flagged items {package['cross_item_flagged']}, excluded path incidents {package['excluded_cross_files']}, retained own-locator overlap incidents {package['retained_cross_locators']}। Actual manifests-এর independent audit-এ মোট pair incidents {cross['pair_incidents']}, U-তে incoming {cross['incoming_to_U']}, U থেকে prior package-এ incidents {cross['U_to_prior']}; অতিরিক্ত prior-item flags {cross['additional_prior_flagged_items']}। পুরোনো key না বদলে পূর্ণ side audit private `key/e12_cross_item_all.json`-এ আছে। Evidence: `verification_t49.json:summary`; `09_collab/logs/T49_scratch/final_audit.json:cross_item_audit`; `cross_audit_t49.py:main`।

Local contract file reference incidents {refs['local_file_reference_incidents']}; mandatory cross-item exclusions-এর ফলে {refs['affected_items']} items-এ {refs['missing_reference_incidents']} references-এর target অনুপস্থিত। প্রতিটি missing target excluded cross-item path-এর মধ্যে পড়ে। Remote reference incidents {refs['remote_reference_incidents']}। ⚠️ ফলে ওই excerpt closures সম্পূর্ণ self-contained নয়; blind reading-এ এই সীমাবদ্ধতা বিবেচ্য। Evidence: `key/e12_reference_audit.json:missing_references`; `final_audit.json:reference_audit`; `test_t49.py:test_all_generation_cross_flags_and_reference_exclusions`।

সব **{tests['tests_run']} tests pass**: earlier tests {tests['earlier_tests']} + T49 tests {tests['T49_tests']}; failures 0, errors 0। পুরোনো package tests T47/T48-এর isolated reconstruction-এ চলে; test process-এর audit hook অন্য labelling package-এ open/list/scandir আটকায়। Synthetic Git fixtures কেবল নিজেদের test directories-এ; upstream bare clones read-only। Independent reconstruction-এ delivered bytes, key, full CSV, mapping ও build log মিলে গেছে। Parent provenance, own-child exclusion, message/history scan, forbidden words, privacy, cross-item exclusion, verbatim propositions ও আট-file cap checks pass। Evidence: `09_collab/logs/T49_scratch/{sorted(SCRATCH.glob('test_summary_*.json'))[-1].name}`; `verification_t49.json:checks`; `run_tests_t49.py:read_boundary`; raw diagnostics private `key/e12_test_run_*.txt`।

Task শুরুর **8,853 existing key files** এবং ছয়টি recorded freeze/continuation input—মোট **8,859 files**—before/after SHA-256-এ byte-identical; changed files 0। `freeze2.json`-এর pool/source/code hashes-ও actual files-এর সঙ্গে মেলে। Old keys ও frozen pool2 বদলানো হয়নি; অন্য blind packages বা board পড়া হয়নি। Old keys পড়া হয়েছে authorized preservation/build/dedup কাজে। Board-এর কাজ কেবল task শেষে একটিমাত্র completion Log append (`>>`); board row edit করা হয়নি। Evidence: `key/preservation_t49_start.json`, `key/preservation_t49_after.json`; `final_audit.json:existing_files_checked,changed_existing_files,board_read`; `09_collab/logs/T49_scratch/completion.json`; `finalize_t49.py:audit`; `09_collab/tasks/T49.md` board override।

Preview ledger: **2,473 events / 949 candidates**; outside-final-prefix 0, without-final-decision 0, lookahead-before-prior-decision 0। Chronological sequence এবং final-prefix membership pass। 726 candidates conservative static triage-এর মাধ্যমে final হয়েছে; বাকি 223-এ অতিরিক্ত model patch review হয়েছে। Accepted candidates-এ exact parent locators ও resolving patch evidence private আছে। Stop-এর পরে পরের candidate evidence access Git read বা preview write-এর আগেই reject হয়। Evidence: `summary_t49.json:preview_record,conservative_static_triage,additional_model_patch_reviews`; `key/t49_previews/`; `finalize_t49.py:validate_previews`; `test_t49.py:test_real_preview_ledger_and_stopped_guard`।

একটি early legacy patch preview-তে credential-সদৃশ encoded literal দেখা গিয়েছিল। Display filter-এ long encoded quoted literals এবং credential assignments suppression যোগ হয়েছে; synthetic regression pass। Value এখানে পুনরাবৃত্তি করা হয়নি। অতিরিক্ত exact/decoded/escaped variant scan-এ delivered {audit['preview_privacy_incident']['delivered_files_scanned']} files-এর কোনোটিতে observed value পাওয়া যায়নি ({audit['preview_privacy_incident']['scanned_variants']} variants checked)। এই incident-এর কারণে preview privacy-কে ত্রুটিহীন বলা যায় না। Evidence: `key/e12_preview_privacy_incident_audit.json`; `final_audit.json:preview_privacy_incident`; `review_t49.py:display`; `test_t49.py:test_preview_display_suppresses_encoded_and_credential_literals`।

⚠️ Threats: correction-cue retrieval ও historical availability selection bias তৈরি করে; frozen pool বা byte-order cap direction না পড়লেও repo caps এবং method/path ordering sample composition বদলায়। 726 rule-triaged candidates পূর্ণ manual parent comparison পায়নি; deferred 107-এর মধ্যে missing/ambiguous contracts এবং বড় patches আছে। Generated external models অনুপস্থিত থাকলে acceptance করা হয়নি। Accepted conclusions static framework dispatch, validation, serialization ও persistence inference; কোনো runtime reproduction বা external-code execution হয়নি। একই candidate-এর একাধিক operation এবং shared helpers স্বাধীন observations নয়; per-fix cap দুই হলেও clustering রয়ে গেছে। Cross-item own-locator exceptions এবং missing references blind readers-কে প্রভাবিত করতে পারে। Privacy/metadata redaction source readability কমাতে পারে। Aggregate directions এই selected corpus-এর ফল; population prevalence বা independent-fix rate হিসেবে ব্যবহারযোগ্য নয়। Evidence: `summary_t49.json`; `verification_t49.json`; `key/e12_cross_item_all.json`; `key/e12_reference_audit.json`; `final_audit.json`; `09_collab/tasks/T49.md` constraints।

Required deliverables: `key/e12_key.csv`, `key/accepted_full_t49.csv`, `key/review_decisions_t49.csv`, `yield_t49.csv`, `E2_labelling/e12_blind/`, T49 scripts/tests, preservation/verification audits এবং এই report। কোনো blocker বাকি নেই; ভবিষ্যৎ runtime validation বা blind labelling এই task-এর বাইরে। Evidence: উল্লিখিত artifacts এবং passing test/audit records।
'''
    # Per-item source identifiers never enter the report.
    for row in runpy.run_path(str(HERE / 'review_t49.py'))['accepted']():
        assert row['fix_commit'] not in text and row['parent_commit'] not in text
    with (ROOT / '09_collab/reports/T49_report.md').open('x') as stream:
        stream.write(text)
    print('Bengali T49 report written; aggregate directions only.')


if __name__ == '__main__':
    main()
