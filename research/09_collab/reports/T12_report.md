# T12 — scout-api pilot batch

**Task update:** initial read-এর পরে T12 §1b যোগ হয়েছে (task file mtime 21:56:36 local)। চলমান unauthenticated সাত-run series diagnostic হিসেবে রাখা হচ্ছে; পরের ধাপ administrator auth, request timeout ও shrinking-disable harness fixes, নতুন smoke এবং revised batch (`09_collab/logs/T12_scratch/task_updated_snapshot.md:22-30`; `09_collab/COLLAB_BOARD.md`, T12 Log update)।

**অবস্থা: চলমান; mutation batch চলছে।** T11 DONE এবং pilot lock free—দুটো শর্ত 480.02 seconds অপেক্ষার পর পূরণ হয়েছে। তিন baseline সম্পন্ন হয়েছে, কিন্তু সব incomplete: seed1 exit124, seed2 exit124, seed3 exit137। Exchanges যথাক্রমে 106/123/124; original-spec operation hit 2/49, 3/49, 3/49 (`09_collab/logs/T12_scratch/gate.jsonl`, elapsed_seconds=480.02; `08_experiments/E1_pilot/pilot_results/runs.csv`, baseline seed rows)।

## প্রস্তুতি

Protocol, T12 task, harness README, T5/T10 report এবং codebook §5/§9 পড়া হয়েছে। Execution wrapper ও local analysis script অনুমোদিত scratch path-এ লেখা হয়েছে; external execution কেবল task-এর তিন reviewed harness script-এর মাধ্যমে হবে (`09_collab/logs/T12_scratch/batch.py:1`; `09_collab/logs/T12_scratch/summarize.py:1`; `09_collab/tasks/T12.md:4-12`)।

পরিকল্পিত settings: `MAX_EXAMPLES=100 HEALTH_PATH=/admin/healthcheck BASE_PATH=/api`; baseline seeds 1/2/3, এরপর চার mutation class-এর severity 30, seed 1; প্রতিটি generation budget 600 seconds। প্রতিটি mutated run-এর পরে `analyse_run.sh --mode both` চলবে। Incomplete run comparison আলাদা partial audit হিসেবে চিহ্নিত হবে; harness-এর completeness/provenance gate পরিবর্তন করা হবে না (`09_collab/tasks/T12.md:30-37`; `08_experiments/E1_pilot/harness/analyse_run.sh:10-35`; `09_collab/logs/T12_scratch/batch.py:1`)।

## ফলাফল ও সীমা

এখন baseline-গুলির partial audit পাওয়া যাচ্ছে; full batch result এখনও প্রস্তুত নয় (`08_experiments/E1_pilot/pilot_results/runs.csv`, baseline seed rows)। Default/strict policy, baseline variability এবং replay/fresh locality আলাদা CSV-তে সংরক্ষণের script প্রস্তুত (`09_collab/logs/T12_scratch/summarize.py:1`)।

JaCoCo execution-data dump reviewed harness-এর অন্তর্ভুক্ত; standalone `java ... report` ও external extraction command task-এর exact external-execution allowlist-এ নেই। তাই line-coverage calculation skip করার পরিকল্পনা; dump size/exit report হবে (`09_collab/tasks/T12.md:4-12,39-44`; `08_experiments/E1_pilot/harness/run_pilot.sh:58-66`)।
