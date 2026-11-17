#!/usr/bin/python3
"""Bengali aggregate report; no item direction or source history identifiers."""
import csv
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SCRATCH=ROOT/'09_collab/logs/T50_scratch'

def main():
    summary=json.loads((HERE/'summary_t50.json').read_text())
    verification=json.loads((HERE/'verification_t50.json').read_text())
    audit=json.loads((SCRATCH/'final_audit.json').read_text())
    tests=json.loads(sorted(SCRATCH.glob('test_summary_*.json'))[-1].read_text())
    incident=json.loads((SCRATCH/'incident_privacy_scan.json').read_text())
    assert tests['passed'] and tests['failures']==tests['errors']==0
    with (HERE/'yield_t50.csv').open() as f:yields=list(csv.DictReader(f))
    text='''# T50 — নতুন repository, frozen pool3 এবং পৃথক Q-package

নিচের সংক্ষিপ্ত script/JSON/CSV ও `key/` path-এর ভিত্তি `08_experiments/E7_mining/`; scratch audit/test path-এর ভিত্তি `09_collab/logs/T50_scratch/`। Function, JSON field ও repo-named CSV row সরাসরি evidence locator।

T50-তে ২০টি নতুন bare clone-এর সব পাওয়া গেছে। **১২,৮৩২ candidates-এর pool3 review-এর আগে freeze** হয়েছে। নির্বাচনের `selected.tsv:clone_name` order-এ দুইটি পূর্ণ round-robin round শেষে **৪০ candidates / ৫ accepted candidates / ৮ items**। **৬০-item target পূরণ হয়নি**। অনুমোদিত budget stopping rule ব্যবহার করে দ্বিতীয় round-এর শেষ candidate-এর final decision-এর পরে থামা হয়েছে; pool exhausted বা target reached দাবি করা হচ্ছে না। Evidence: `pool3_inventory.json` (repo records); `freeze3.json:before_review`; `summary_t50.json:reviewed,accepted_candidates,accepted_items,completed_round,stopping_reason`; `key/t50_stop.json`।

Retrieval T46 pool2-এর content-verified OpenAPI/root/local-ref/JVM annotation এবং production Java/Kotlin/Go behaviour filters পুনর্ব্যবহার করে। শুধু checked-in document-এর সঙ্গে থাকা Go `// @Router` ও `// swagger:route` source যোগ হয়েছে; সব repo-তে একই rule। Correction cue AND (contract OR behaviour) condition এবং `10 × cue_strength + operation_path_bit` score অপরিবর্তিত; direction bonus নেই। Repo-র ভিতরে score descending, SHA ascending। Repo selection read-only; ৩৪টি পুরোনো repo থেকে pool3 candidate নেওয়া হয়নি। Evidence: `mine3.py:classify,discover,main`; `mine2.py:excluded,production,reachable`; `mine.py:rank_candidate`; `t50_repo_selection/selected.tsv`; `test_t50.py:Pool3Tests`।

প্রতি candidate-এর final decision পরের candidate খোলার আগে লেখা হয়েছে। Acceptance-এ existing operation, neutral proposition, exact parent locators, resolving patch, confidence ও family evidence আছে; IMPL-এ parent contract সমর্থন আবশ্যক। Dedup সব T45–T49 ও ২৫ exploratory item-এর repo–operation–family identity-র সঙ্গে হয়েছে। Item selection direction বা অন্য বৈশিষ্ট্যের ভিত্তিতে করা হয়নি। Evidence: `review_t50.py:require_current,record_preview,accept,finish_accept`; `finalize_t50.py:audit`; `key/accepted_full_t50.csv:proposition_check,evidence,inference_notes`; `key/review_decisions_t50.csv`।

Per-repo ফল নিচে। প্রতিটি row-এর evidence `yield_t50.csv:repo`; accepted candidates ও accepted items আলাদা column। সব repo-র শেষ rank ২, কোনো repo ১০-item cap-এ পৌঁছায়নি; সব row-এর stop reason `budget after complete round`।

| Repo | Pool3 | Reviewed | Accepted candidates | Items |
|---|---:|---:|---:|---:|
'''
    for r in yields:text+=f"| {r['repo']} | {r['pool3']} | {r['reviewed']} | {r['accepted_candidates']} | {r['items']} |\n"
    text+='''
Accepted candidates-এর মধ্যে দুইটি থেকে একটি করে এবং তিনটি থেকে দুইটি করে item রাখা হয়েছে। Cap-এর আগে প্রতিষ্ঠিত operation histogram: ২ candidates × ১, ১ × ২, ১ × ৪, ১ × ১০ = ১৮ operations। Plain UTF-8/byte order-এ `METHOD path` সাজিয়ে প্রতি candidate-এর প্রথম দুইটি রাখা হয়েছে। **FIX_CAP exclusions ১০**, REPO_CAP exclusions ০। অতিরিক্ত operation rows-এ `review_status=accepted_capped`, `reason_code=FIX_CAP`; candidate final rows ৪০ ও exclusion rows ১০ মিলিয়ে private decision table-এ ৫০ rows। কিছু patch-এর অন্যান্য edits-এর parent mismatch প্রতিষ্ঠিত হয়নি; সেগুলো accepted operation হিসেবে গণনা করা হয়নি। Evidence: `summary_t50.json:items_per_accepted_candidate,valid_operations_per_candidate,FIX_CAP_exclusions,REPO_CAP_exclusions`; `review_t50.py:select_operations`; `key/t50_fess_scope.json`, `key/t50_fess_chat_scope.json`; `key/review_decisions_t50.csv`।

**LICENCE rejections ০**। প্রতিটি accepted candidate-এর parent revision-এর root licence file read-only `git show` দিয়ে পড়া, hash ও class record হয়েছে; প্রতিটি accepted item-এর `licence_at_parent` আছে। Restrictive/source-available/non-commercial software grant অথবা অজানা licence acceptance আটকে `OTHER` এবং `LICENCE:` reason লেখে। একটি trademark clause-এ commercial ও non-commercial দুই ধরনের product-এর উল্লেখ থাকায় initial lexical check false positive দিয়েছিল; software grant-এর context পড়ে acceptance-এর আগেই classifier সংশোধিত হয়েছে। সেই initial record private audit-এ অক্ষত আছে। ⚠️ এটি static licence classification; legal বা runtime validation করা হয়নি। Evidence: `review_t50.py:licence_class,parent_licence,licence_gate`; `key/t50_licences/`; `key/e13_licence_classifier_correction.json`; `key/accepted_full_t50.csv:licence_at_parent`; `test_t50.py:ReviewTests`।

Candidate-level reason_code distribution নিচে; ACCEPT candidate গোনে, item নয়। Cap-exclusion count উপরে আলাদা। Evidence: `summary_t50.json:reason_code_counts,review_status_counts`; `key/review_decisions_t50.csv`।

| reason_code | Candidates |
|---|---:|
'''
    for code,count in sorted(summary['reason_code_counts'].items()):text+=f'| {code} | {count} |\n'
    text+='''
Final statuses: accepted ৫, rejected ২৫, deferred ১০। **Aggregate direction: SPEC ৭, IMPL ১, BOTH ০**। Per-item direction, source identifiers, operation-to-source mapping এবং shuffle salt কেবল `key/`-তে আছে। Aggregate counts এই নির্বাচিত sample-এর ফল। Evidence: `summary_t50.json:aggregate_directions,review_status_counts`; `key/e13_key.csv`; `key/e13_shuffle_mapping.csv`; `key/e13_shuffle_salt.txt`।

পৃথক package `08_experiments/E2_labelling/e13_blind/`-এ শুধু **Q01–Q08**। `items.csv`-এর columns `item_id,repo,operation,proposition`, LF endings এবং verbatim propositions যাচাই হয়েছে। প্রত্যেক item-এর `contract/` ও `impl/` আছে; README T49 builder-এর একই bytes। Package path থাকলে overwrite প্রত্যাখ্যান করে; অন্য package তৈরি বা পরিবর্তন করা হয়নি। New key-এর columns `e12_key.csv`-এর সমান; full table-এর columns `accepted_full_t49.csv`-এর সঙ্গে শুধু `licence_at_parent` যোগ করে। Evidence: `build_t50.py:prepare,full_bytes,publish`; `test_t50.py:PackageTests,SyntheticPackageTests`।

Package **৫২ files / ১,১৬১,০০২ bytes (প্রায় ১.১১ MiB)**: contract ৮, implementation ৪২, table ও README ২। বড় generated contract-এর operation ও transitive local `$ref` closure-এ projected files ২; redacted source files ৩৬। প্রতি item-এ implementation সর্বোচ্চ আট files; নিজস্ব parent locator files রাখা হয়েছে। Whole implementation, parent provenance, child-content exclusion, message/history-literal scans, forbidden words এবং privacy checks pass। Evidence: `verification_t50.json:summary,checks`; `key/e13_build_log.json:items,assertions`; `test_t50.py:test_package_hashes_leakage_privacy_and_eight_file_cap`।

Cross-item ancestry/path check **১৯৫ items** জুড়ে: পুরোনো ১৮৭ ও নতুন ৮। নতুন selected repo এবং পুরোনো item repo-র overlap ০; নতুন items-এর মধ্যেও check হয়েছে। Flagged new items ২, optional exclusion incidents ০, retained own-locator overlap incidents ৪। পুরোনো flags/keys বদলানো হয়নি। Delivered contracts-এ missing local-file references ০, remote-file references ০; দুইটি projected document-এর internal closure builder যাচাই করেছে। Evidence: `key/e13_cross_item_audit.json`; `key/e13_build_log.json:cross_item_pairs`; `key/e13_reference_audit.json`; `final_audit.json:reference_audit,cross_item_all_items`; `build.py:prepare,contract_files`।

'''
    text+=f"সব **{tests['tests_run']} tests pass**: earlier {tests['earlier_tests']} + T50 {tests['T50_tests']}; failures/errors ০। প্রথম full suite-এ ৯২টি এবং পরে নতুন দুটি supplemental test চলেছে; সব বর্তমান test method covered। পুরোনো package tests isolated reconstruction-এ চলেছে; audit hook অন্য labelling packages open/list/scandir করতে দেয়নি। Production Q-package সরাসরি disk থেকে এবং পুনর্নির্মিত bytes-এর সঙ্গে পরীক্ষা হয়েছে। Pool3 frozen source থেকে পুরো pool/rank mapping deterministically পুনর্গঠিত হয়েছে; একটি selected repo-র full discovery দুবার replay করে frozen records-এর সঙ্গে মেলানো হয়েছে। Q-shuffle input-order independent, নতুন salt, cap, licence gate, preview filter ও overwrite refusal tests pass। Evidence: `test_summary_01.json`, `test_summary_02.json:execution_parts,all_current_test_methods_executed`; `run_tests_t50.py:read_boundary,main`; `test_t50.py`; raw diagnostics কেবল `key/e13_test_run_*.txt`; `verification_t50.json:checks.exact_disk_reconstruction`।\n\n"
    text+='''Task শুরুর **১৪,১৫৮ existing key/pool/freeze files** before/after SHA-256-এ byte-identical; changed ০। Pool3 এবং নতুন freeze-এর recorded hashes-ও মেলে। Existing key বা পুরোনো pool/freeze পুনর্লিখন হয়নি; selection files read-only ছিল। Evidence: `key/preservation_t50_start.json`, `key/preservation_t50_after.json`; `final_audit.json:existing_files_checked,changed_existing_files`; `review_t50.py:guard`; `freeze3.json`।

Preview ledger: **২০৮ events / ৪০ candidates**; outside-final-prefix ০, without-final-decision ০, lookahead-before-prior-decision ০। Chronological order এবং সম্পূর্ণ round boundary যাচাই হয়েছে। একটি current-candidate test-path probe-তে credential-সদৃশ fixture value দেখা গিয়েছিল; value এখানে পুনরাবৃত্তি করা হয়নি। Filter এখন sensitive keyword-সম্বলিত পুরো line, long encoded literal ও credential assignment suppress করে; source probes test paths বাদ দেয়। এই incident-এর কারণে preview privacy-কে ত্রুটিহীন বলা যায় না। Evidence: `summary_t50.json:preview_record`; `key/t50_previews/`; `key/e13_preview_privacy_incident.json`; `review_t50.py:display,probe`; `peek_t50.py`; `test_t50.py:test_display_suppresses_encoded_literals_and_credential_assignments`।

'''
    text+=f"Observed fixture value-এর exact/encoded **{incident['variants_checked']} variants** দিয়ে delivered {incident['files_checked']} files scan-এ occurrences **০**। T44 auth fixtures ও value variants, attribution, credential assignments এবং candidate reasons-ও পরীক্ষা হয়েছে। Evidence: `incident_privacy_scan.json`; `final_audit.json:privacy_scan_passed,preview_privacy_incident`; `verification_t50.json:auth_fixtures,auth_value_variants`; `audit_t50.py`; `test_t50.py:PackageTests`।\n\n"
    text+='''⚠️ Threats: মাত্র দুই round-এর prefix reviewed; ১২,৭৯২ candidates unreviewed। Budget stop এবং correction-cue/path selection থেকে corpus completeness বা population prevalence বোঝা যায় না। Repo selection, available history, lexical cue strength ও byte-order cap sample composition প্রভাবিত করে। Conservative deferrals false negatives রাখতে পারে; absent generated DTO/schema বা external writer source-এর কারণে mismatch প্রতিষ্ঠিত না-হওয়া correctness-এর প্রমাণ নয়। Parent contracts-এর omitted response বা limit interpretation, framework dispatch/validation/serialization static inference; accepted evidence-এ confidence এবং inference notes আছে। Upstream build, traffic reproduction বা generation pipeline execute করা হয়নি। Evidence: `summary_t50.json`; `yield_t50.csv`; `key/accepted_full_t50.csv:confidence,inference_notes`; `key/review_decisions_t50.csv`; `mine3.py`।

⚠️ একই candidate-এর একাধিক operation এবং shared source files স্বাধীন observation নয়। Per-fix cap দুই হলেও clustering আছে; own-locator cross-item exceptions blind reading প্রভাবিত করতে পারে। Eight-file cap সম্পূর্ণ runtime context নিশ্চিত করে না। Large-document projections line numbers বদলায়; whole files-এ privacy redaction readability কমাতে পারে। Lexical scans সব personal attribution, semantic hint বা credential শনাক্ত করার নিশ্চয়তা দেয় না; preview incident এই সীমাবদ্ধতার বাস্তব উদাহরণ। Licence detector-এর lexical false positive context review দিয়ে সংশোধন করতে হয়েছে। Evidence: `key/e13_build_log.json`; `key/e13_cross_item_audit.json`; `key/e13_preview_privacy_incident.json`; `key/e13_licence_classifier_correction.json`; `test_t50.py`।

সব কাজ offline। Upstream bare clones-এ read-only `git --git-dir`; network, checkout, upstream execution বা dependency install হয়নি। নিজস্ব Python ও artificial bare-repo tests চালানো হয়েছে। নিষিদ্ধ analysis/label files, অন্য blind packages এবং board পড়া হয়নি। শেষে শুধু একটি Log line `>>` দিয়ে append করা হয়েছে। পরবর্তী continuation থাকলে প্রত্যেক repo-র প্রথম unreviewed pool3 rank ৩; এই task-এর Q-package পৃথক ও frozen review records সংরক্ষিত। Evidence: `mine.py:git`; `run_tests_t50.py`; `final_audit.json:network_used,upstream_execution,board_read`; `completion.json`; `yield_t50.csv:last_reviewed_rank`।
'''
    path=ROOT/'09_collab/reports/T50_report.md'
    with path.open('x') as f:f.write(text)
    print('Bengali T50 report written; aggregate-only output.')

if __name__=='__main__':main()
