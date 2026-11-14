# T20c — ordering ও operation exclusion

দুটি rule implement করা হয়েছে; **৯০/৯০ E5 tests PASS**। Saved runs থেকেই সাতটি completed seed revalidate ও ছয়টি eligible seed-এর দুই oracle-এ **১২টি নতুন analysis COMPLETE** হয়েছে। Docker/Maven/Java/harness/SUT চালানো হয়নি (`09_collab/logs/T20c_scratch/tests.txt`, final summary; `revalidation.json`, pair/seed rows; `analysis_verification.json`, `completed_analyses`)। এখানে scratch basename বলতে `09_collab/logs/T20c_scratch/` বোঝানো হয়েছে।

- `Env` multiset হিসেবে compare হয়: order উপেক্ষিত, multiplicity ও values strict। `Binds`-এ নিজস্ব run-directory placeholder করার পরে set comparison হয়। SUT/proxy দুটোতেই একই rule; changed source/options বা environment multiplicity fail করে (`08_experiments/E5_codemut/validate_pair.py`, `normalized_runtime`; `test_e5_pipeline.py`, `test_environment_multiset_and_bind_set_ignore_order_but_keep_values`, `test_bind_source_or_mount_options_remain_strict`)।
- Identical JUnit error sets আগের মতো PASS। Asymmetric errors-এর exact testcase name original spec-এর operation-এ map হয়; সব differing operation non-mutated হলে `PASS_WITH_EXCLUSION` ও method/path/reason list। কোনো mutated বা unmappable differing operation থাকলে FAIL (`validate_pair.py`, `paired_junit`; `test_e5_pipeline.py`, non-mutated/mutated/unmappable asymmetry tests)।
- Raw violations রাখা হয়; excluded operations দুই role থেকেই attribution-এর আগে বাদ যায়। Summary raw/scoped equality যাচাই করে এবং সব metric/signal count-এ একই exclusion রাখে। CSV-তে `excluded_ops` ও প্রকৃত `validation_status` আছে (`08_experiments/E5_codemut/e5_pipeline.py`, `filter_violations`, `analyse_pair`; `summarise_e5.py`, `verify_analysis`, `metrics`)।

## Saved-seed ফল

| Pair | Revalidation | নতুন complete analyses |
|---|---|---:|
| scout-drop-null | s1/s2/s3 PASS | 6 |
| cwa-drop-null | s1 PASS; s2 PASS_WITH_EXCLUSION | 4 |
| cwa-drop-validation | s1 PASS; s2 FAIL | 2 |

প্রমাণ: `revalidation.json`, তিন pair-এর seed rows; `analysis_verification.json`, `completed_analyses`। CWA-drop-null s2-তে `POST /version/v1/registrationToken` দুই role-এর comparison থেকে বাদ গেছে—প্রতি oracle-এ control 34 ও mutant 35 diagnostics বাদ, raw files অক্ষত (`analysis_verification.json`, cwa-drop-null/seed=2 rows)।

**Task-এর বর্ণনায় একটি গুরুত্বপূর্ণ অমিল আছে:** `cwa-drop-validation`-এর manifest-এ mutated operation নিজেই `POST /version/v1/registrationToken`। তাই s2-এর ওই asymmetric error-কে non-mutated বলা যায় না। Task-এর explicit FAIL rule অনুযায়ী s2 FAIL রাখা হয়েছে; `analyse_pair.sh` s1 শেষ করে s2-তে nonzero exit দিয়ে থেমেছে। CWA pair দুটির s3 ledger-এ attempted নয়; নতুন SUT run করা হয়নি (`08_experiments/E5_codemut/work/cwa-drop-validation_20261114T114829Z/manifest.json`, `operations`; ওই pair-এর `runs.tsv`, `pair-validation-s2.json`; `09_collab/logs/T20c_scratch/analysis-cwa-drop-validation_20261114T114829Z.log:1`; `revalidation.json`, cwa-drop-validation/seed=2)।

Shared spec defect মেরামত করা হয়নি: `keyDob` property schema-তে `required: false` আছে। Exclusion মানে ওই operation-এর comparison বাদ দেওয়া, spec/generator ঠিক হয়ে যাওয়া নয় (`08_experiments/_external/emb/openapi-swagger/cwa-verification.json:320–324`; `validate_pair.py`, `paired_junit`)।

আগের ছয় pair-এর protected analysis files rewrite করা হয়নি। পুরোনো PASS report-এর missing `excluded_ops` শুধু empty exclusion হিসেবে compatible; বাকি validation content মিলতে হয়। চার reviewed E5 policy module-এর পুরোনো hash provenance হিসেবে রাখা হয়, কিন্তু tools/harness/অন্য code hashes strict থাকে এবং attribution hashed violations থেকে recompute হয়। CSV-তে এ ধরনের row `pipeline_snapshot_status=PRIOR_E5_PIPELINE_RECOMPUTED`; নতুন analysis CURRENT (`summarise_e5.py`, `verify_analysis`, `summarise`; `test_e5_pipeline.py`, prior-pipeline positive/negative tests)।

Regenerated CSV-তে **৫০টি row: ৪৪টি COMPLETE (৪২ PASS, ২ PASS_WITH_EXCLUSION), ৬টি error**। আগের ৩২টি COMPLETE row-এর metrics অপরিবর্তিত। ছয় error row হলো mutated-op asymmetry-র দুই oracle এবং CWA pair দুটির unattempted s3-এর চার oracle; তাই summary CLI exit 1 প্রত্যাশিত। Final CSV ফল ও integrity audit `summary_verification.json`-এ; failed/unattempted seeds-এর metrics blank থাকে। সব **১৬৮৯টি snapshotted protected file অপরিবর্তিত**—harness/tools, saved runs এবং অন্য work pair-এর metadata/analysis outputs। কেবল assigned তিন pair-এর validation/analysis outputs এবং অনুমোদিত E5 code/docs/summary লেখা হয়েছে (`09_collab/logs/T20c_scratch/analysis_verification.json`, `protected_files`; `summary_verification.json`; `09_collab/tasks/T20c.md`, Constraints)।

সীমা/open question: mutated-operation asymmetry থাকায় cwa-drop-validation s2 analysis এই policy-তে অগ্রহণযোগ্য। Future paired rerun বা policy revision coordinator/supervisor-এর কাজ; এই task-এ failure আড়াল করা হয়নি। Exclusion-aware signal match এখনও causal kill বা independent IMPL attribution নয় (`pair-validation-s2.json`, উল্লিখিত cwa-drop-validation directory; `08_experiments/E5_codemut/summarise_e5.py`, `causal_kill_status`)।
