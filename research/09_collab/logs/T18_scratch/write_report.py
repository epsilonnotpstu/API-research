"""Write the short Bengali T18 report from frozen-scope local evidence."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from replay import ROOT, RUN, SOURCE


def cite(path, line):
    rel = str(path.relative_to(ROOT))
    return f'`{rel}:{line}`'


def main():
    spec = RUN / 'spec.original.json'
    logs = RUN / 'compose.log'
    raw = RUN / 'exchanges.jsonl'
    scratch = ROOT / '09_collab/logs/T18_scratch'
    labels = ROOT / '08_experiments/E2_labelling/cwa-verification_baseline_s1_labels_codex.csv'
    roots = ROOT / '08_experiments/E2_labelling/cwa-verification_root_causes_codex.csv'
    checker = ROOT / '08_experiments/tools/conformance.py'
    book = ROOT / '08_experiments/R1_triage_codebook.md'
    report = f'''T18 — cwa-verification blind labeller B (codebook v0.4)

দুটি CSV-তে C001–C006-এর primary label ও সাতটি root-cause family লেখা হয়েছে। ফল: TEST ৪, SPEC ১, SPEC_PARTIAL ১; সব confidence ৩ এবং `both_candidate=false`। Strict scoring: TEST ৪ / SPEC ১ / UNDECIDABLE ১; lenient: TEST ৪ / SPEC ২। Labeller নিজে BOTH দেয়নি। Evidence: {cite(labels, 2)}, {cite(labels, 3)}, {cite(labels, 4)}, {cite(labels, 5)}, {cite(labels, 6)}, {cite(labels, 7)}; {cite(roots, 2)}; aggregation ও notation: {cite(book, 218)}, {cite(book, 229)}।

পদ্ধতি: saved original spec-এর বিরুদ্ধে নিজের checker replay-তে `--deploy-origin http://sut-cwa-verification:8080` ব্যবহার করেছি; spec-এর localhost authority অপরিবর্তিত। Blind fingerprint-এর বাইরের JSON string খুলে তুলনা করলে ৪৩০ captured exchange-এ ছয়টি exact fingerprint, ৪৩০ diagnostic occurrence এবং প্রত্যেক blind count মেলে; unmatched শূন্য। Original ও generator spec structurally identical। Evidence: {cite(checker, 182)}, {cite(checker, 443)}, {cite(spec, 13)}, {cite(scratch / 'replay_summary.json', 1)}।

| Item | Primary L1 / L2 | Occurrences | সিদ্ধান্ত |
|---|---|---:|---|
| C001 | TEST / proposed T-PROBE | ১ | null-byte capability probe |
| C002 | SPEC_PARTIAL / S-REQ-LOOSE | ৬৯ | ৬২ SPEC + ৭ TEST |
| C003 | TEST / proposed T-ORACLE-STATE | ৮০ | session না থাকা generated token |
| C004 | TEST / proposed T-ORACLE-COVERAGE | ১০০ | object-shaped Authorization header checker-এর আওতার বাইরে |
| C005 | SPEC / S-RESP-MISSING | ১০০ | ইচ্ছাকৃত empty 404-এ ভুল object-body schema |
| C006 | TEST / proposed T-ORACLE-STATE | ৮০ | session না থাকা generated token |

টেবিলের occurrence evidence: {cite(scratch / 'replay_summary.json', 10)}; occurrence-ভিত্তিক label: {cite(scratch / 'case_labels.json', 1)}। মোট message attribution TEST ২৬৮, SPEC ১৬২; এগুলো independent bug-এর সংখ্যা নয় ({cite(scratch / 'case_summary.json', 4)})।

⚠️ C002-এর ৬২টি application rejection-এ অন্তত একটি explicit validation constraint schema-তে নেই: `key` অনুপস্থিত ৩৩টি, `keyType` ৪৪টি, GUID pattern ১১টি, keyDob pattern ১৬টি, TELETAN alphabet ২টি; counts overlap করে। Source-এ @NotNull, @Pattern এবং conditional validator আছে; schema-তে required key/keyType ও সংশ্লিষ্ট patterns নেই। অঘোষিত property আছে বলেই এই attribution দেওয়া হয়নি। বাকি সাতটিতে header control codepoint ২৫ অথবা ১৪ এবং HTML 400 আছে—এগুলো সত্যিই invalid HTTP, container-এর বৈধ-input policy ambiguity নয়। ফলে §10.4 অনুযায়ী SPEC_PARTIAL। Evidence: {cite(spec, 314)}; {cite(SOURCE / 'model/RegistrationTokenRequest.java', 47)}, {cite(SOURCE / 'model/RegistrationTokenRequest.java', 53)}, {cite(SOURCE / 'model/RegistrationTokenRequest.java', 59)}; {cite(SOURCE / 'validator/RegistrationTokenRequestValidator.java', 60)}, {cite(SOURCE / 'service/HashingService.java', 37)}, {cite(SOURCE / 'service/TanService.java', 82)}; {cite(raw, 164)}, {cite(raw, 188)}; {cite(scratch / 'case_summary.json', 8)}; {cite(book, 226)}, {cite(book, 229)}।

⚠️ C003/C006-এর token-গুলো UUID pattern মেনে চললেও persistent session থাকার প্রমাণ নেই; দুই operation-এর ৮০টি করে log সরাসরি missing-session rejection দেখায়। Source সেই অবস্থায় deliberate 400 দেয়, backend result call-এর আগে। Captured traffic-এ কোনো registrationToken creation সফল হয়নি; TAN/testresult requests teleTAN creation-এরও আগে হয়েছে। অতএব `VALID_REJECTED` এখানে state না বোঝা oracle-এর false positive—IMPL বা ENV নয়। Evidence: {cite(raw, 2)}, {cite(raw, 82)}; {cite(spec, 57)}, {cite(spec, 105)}; {cite(logs, 250)}, {cite(logs, 532)}; {cite(SOURCE / 'controller/ExternalTanController.java', 108)}, {cite(SOURCE / 'controller/ExternalTanController.java', 154)}, {cite(SOURCE / 'controller/ExternalTestStateController.java', 102)}, {cite(SOURCE / 'controller/ExternalTestStateController.java', 149)}; {cite(scratch / 'case_summary.json', 31)}।

⚠️ C004-এর ১০০টি response 201; checker object/ref header-কে স্পষ্টভাবে uncheckable করে। Unit হলো coverage diagnostic, header model-এর আদর্শ serialization নির্ধারণ নয়। C005-এর ১০০টি 404-এ capture সম্পূর্ণ কিন্তু body খালি; controller ও ResponseEntity<Void> handler সেটিই ইচ্ছাকৃতভাবে করে। তাই C005-এর response content schema সরানোই repair; আলাদা code defect-এর প্রমাণ নেই, BOTH candidate নয়। Evidence: {cite(checker, 327)}, {cite(spec, 170)}, {cite(logs, 1398)}; {cite(raw, 331)}, {cite(spec, 232)}, {cite(SOURCE / 'controller/InternalTanController.java', 120)}, {cite(SOURCE / 'controller/VerificationExceptionHandler.java', 93)}। C001-এর probe header ও GET / → 400 evidence: {cite(raw, 1)}, {cite(logs, 382)}।

Root CSV-তে RC01 probe, RC02 missing required fields, RC03 omitted conditional patterns, RC04 invalid HTTP, RC05 state oracle, RC06 header coverage এবং RC07 unwanted response-body schema আলাদা; C002 একাধিক root বহন করে। Fix sites কেবল spec/test। Evidence: {cite(roots, 2)}, {cite(roots, 3)}, {cite(roots, 4)}, {cite(roots, 5)}, {cite(roots, 6)}, {cite(roots, 7)}, {cite(roots, 8)}। নতুন proposed `T-ORACLE-STATE` মানে schema-valid input থেকেই business-state validity ধরে নেওয়া। `T-ORACLE-COVERAGE`-এর body-only উদাহরণকে এখানে unsupported parameter serialization পর্যন্ত বিস্তৃত করার প্রস্তাব; `T-PROBE` ও mixed C002-এর leaf `T-GEN-INVALID-HTTP` §10.5-এর pending নাম। কোনো নতুন L2-কে অনুমোদিত ধরে নেওয়া হয়নি ({cite(checker, 327)}, {cite(checker, 438)}, {cite(book, 233)}; {cite(scratch / 'case_labels.json', 1)})।

সীমা ও খোলা প্রশ্ন: blinding বজায় রেখে labels_A এবং pilot_results-এর RESULTS report খোলা হয়নি; বাধ্যতামূলক board log পড়া হয়েছে, label evidence হিসেবে ব্যবহৃত হয়নি। কোনো external code/SUT চালানো হয়নি; task-এর নিষিদ্ধ harness/tools write করা হয়নি; own Python ও read-only replay ব্যবহৃত হয়েছে (scope: `09_collab/tasks/T18.md:13`, `09_collab/tasks/T18.md:32`; execution record: {cite(scratch / 'validation.json', 1)})। Log-এ ৭১টি UnicodeEncodeError আছে; তাই এই ফল কেবল captured ৪৩০ exchange-এর, সম্পূর্ণ emitted traffic-এর নয়। Log corroboration operation/category-ভিত্তিক; unique request identity join নয়। দুটি firewall exception-কে সাতটি raw invalid-header case-এর সঙ্গে জোর করে join করিনি ({cite(logs, 439)}, {cite(logs, 966)}, {cite(logs, 1248)}; {cite(scratch / 'log_locations.json', 1)})। Missing cwa-testresult-server-এর জন্য এই ছয় fingerprint-এ ENV evidence পাওয়া যায়নি; source/log-এ observed rejection backend call-এর আগেই হয় ({cite(SOURCE / 'controller/ExternalTanController.java', 118)}, {cite(SOURCE / 'controller/ExternalTanController.java', 154)}, {cite(SOURCE / 'controller/ExternalTestStateController.java', 111)}, {cite(SOURCE / 'controller/ExternalTestStateController.java', 149)}; {cite(scratch / 'log_locations.json', 1)})। Supervisor-এর খোলা সিদ্ধান্ত: proposed state-oracle L2 ও parameter-coverage scope-এর নাম গ্রহণ করবেন কি না; successful stateful workflow-এর failure এই baseline থেকে নির্ণয় করা যায় না ({cite(scratch / 'case_summary.json', 31)})।

যাচাই: exact item/count coverage, ৪৩০ case aggregation, reciprocal root membership, সব evidence locator, ≤৩০-word rationale ও unchanged input hashes PASS। পূর্ণ audit: {cite(scratch / 'validation.json', 1)}; deliverable freeze ও SHA-256: {cite(scratch / 'freeze.json', 1)}।
'''
    report = report.replace('case_summary.json:31', 'case_summary.json:28')
    (ROOT / '09_collab/reports/T18_report.md').write_text(report)


if __name__ == '__main__':
    main()
