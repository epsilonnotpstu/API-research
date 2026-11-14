# T31 — EvoMaster derecursed generator input

T31 সম্পন্ন: live harness-এ সরাসরি পরিবর্তন করা হয়েছে। সব execution ছিল local harness/নিজস্ব Python checks; Docker, Java, Maven, network বা external project code চালানো হয়নি। Scope: `09_collab/tasks/T31.md`; verification: `09_collab/logs/T31_scratch/{bash_n.txt,static_validate.txt,test_fuzzer_args.txt,sanity.json,freeze.json,verification.json}`। নিচের `E1_pilot/`, `tools/`, `_external/` paths-এর root হলো `08_experiments/`।

## পরিবর্তন

- `EVOMASTER_INPUT=spec|derecursed`, unset/empty হলে `spec`; validated value export হয় `PILOT_EVOMASTER_INPUT` হিসেবে। Invalid value অথবা Schemathesis-এর সঙ্গে non-empty knob হলে value echo না করে exit 2; validation Docker/run-directory creation-এর আগে। Empty knob Schemathesis-এ T28-এর schema-oracles knob-এর মতো accepted। Evidence: `E1_pilot/harness_v2/run_pilot.sh:19–43`; tests `test_fuzzer_args.py:155–195`।
- Schemathesis-এর আগের generator block byte-identical রেখে `build_derecursed_generator_input()` function করা হয়েছে। Baseline original থেকে back edges কাটে; mutated mode original derecurse করে একই fault/severity/seed/only-ops দিয়ে specmut চালায়, তারপর selected operation sets মিলিয়ে generator snapshot লেখে। Schemathesis ও opt-in EvoMaster একই function ব্যবহার করে। Evidence: `run_pilot.sh:220–239,281–298`; `logs/T31_scratch/verification.json:3–4`।
- `derecursed` mode-এ host `generator-input.json` read-only mount হয় container-এর বিদ্যমান `/work/spec.test.json` path-এ; `--schema` argv একই থাকে। Default `spec` mode আগের মতো oracle copy করে এবং আগের mount source রাখে। Evidence: `fuzzer_args.sh:33–41`; `run_pilot.sh:287–307`; `test_fuzzer_args.py:155–174,230–278`। Default full Docker invocation mount-array expansion-এর পর prior invocation-এর সমান: `logs/T31_scratch/verification.json:3`।
- `run.json`-এ EvoMaster-only `evomaster_input`, এবং actual schema bytes-এর `generator_input_sha256` যোগ হয়েছে। Default EvoMaster hash করে `spec.test.json`; derecursed/Schemathesis hash করে `generator-input.json`; preparation-এর আগে অনুপস্থিত file হলে null। Derecursed EvoMaster metadata-তে “generator schema back edges…” ও “equal mutation operation sets…” limitations থাকে; default-এ আগের filtering থাকে। Evidence: `run_metadata.py:35–37,86,98–102`; `test_fuzzer_args.py:439–454`।
- Oracle `spec.test.*` ও analysis script অপরিবর্তিত; synthetic baseline/mutated test-এ oracle bytes সংরক্ষণ যাচাই করা হয়েছে। Evidence: `test_fuzzer_args.py:230–278`; protected `analyse_run.sh` digest: `logs/T31_scratch/freeze.json`।

## Checks ও সংরক্ষণ

৬টি shell script-এ `bash -n` PASS। `/usr/bin/python3 -I -B .../static_validate.py` PASS: derecurse ১৩ tests এবং fuzzer ৩৩ tests। আলাদা `/usr/bin/python3 -I -B .../test_fuzzer_args.py` ৩৩/৩৩ PASS; existing golden argv/source fragments অপরিবর্তিত। Evidence: `logs/T31_scratch/bash_n.txt`, `static_validate.txt`, `test_fuzzer_args.txt`; golden digest ও block equality: `verification.json`।

নতুন tests দুই mode-এর argv/mount/export, invalid-value redaction, Schemathesis rejection, metadata hash/limitations এবং তিন generator settings × baseline/mutated synthetic preparation cover করে। Evidence: `test_fuzzer_args.py:155–195,230–278,439–454`।

`freeze.json`-এ ৩৮টি protected file-এর before/after SHA-256 সমান। এতে untouched harness files/golden/analysis, tools Python files, scout original ও batch only-ops আছে। T29/T30 paths পরিবর্তন করা হয়নি; runs/_external/tools/E5/E2-তে output লেখা হয়নি। Freeze পুরো repository snapshot নয়; তালিকাভুক্ত ৩৮টি file-এর যাচাই। Evidence: `logs/T31_scratch/freeze.json` (`changed=[]`, `all_unchanged=true`), `verification.json:2`।

## Offline scout sanity check

নিজস্ব `derecurse.py` ও `tools/specmut.py` CLI `/usr/bin/python3 -I -B` দিয়ে চালানো হয়েছে। Original: `_external/emb/openapi-swagger/scout-api.json`; pool: `E1_pilot/runs/scout-api/batches/20261114T214527Z_batch_1003519/eligible_loose_s1.json`; mutation flags: `--fault REQUEST_LOOSE --severity 30 --seed 1 --only-ops <pool>`। প্রথমে original derecurse, তারপর original ও derecursed input-এ একই mutation flags। সব output `09_collab/logs/T31_scratch/`-এর মধ্যে। Evidence: `sanity.json`, `derecurse-cuts.json`, `oracle.log`, `generator.log`, `oracle/*.manifest.json`, `generator/*.manifest.json`।

| Input | Bytes | Max nesting depth |
|---|---:|---:|
| Original baseline | 52,607 | 8 |
| Derecursed baseline | 52,690 | 8 |
| Original থেকে mutated oracle | 650,641 | 31 |
| Derecursed থেকে mutated generator | 67,391 | 14 |
| Saved stalled run spec.test.json | 650,641 | 31 |

Depth-এ JSON root container = 1, scalar = 0। দুই recursive back edge কাটা হয়েছে। Generator/oracle উভয়ে একই ১৪টি operations নির্বাচিত করেছে; saved stalled run-এর manifest-এর সঙ্গেও একই। Reproduced oracle ও saved `spec.test.json` byte-identical; SHA-256 `7e835c9c5d95c5209acc05c5a5b02c17a3d02c40d89a3df01e234c5d9c486c8b`। Generator SHA-256 `374a83c743f545e138288ea612aaf483b95166b478a327bf11bdd596f3a4f736`। Evidence: `logs/T31_scratch/sanity.json` (`files`, `operations_equal`, `saved_operations_equal`, `oracle_bytes_equal_saved`, `operations`, `cuts`)।

## সীমাবদ্ধতা ও বাকি যাচাই

⚠️ Size/depth reduction runtime stall সমাধানের প্রমাণ নয়; EvoMaster runtime চালানো হয়নি। Claude-এর baseline + REQUEST_LOOSE smoke run বাকি। Equal selected operations generator/oracle constraints সমান প্রমাণ করে না; metadata limitations-এ এই বিষয় retained। Evidence: `run_metadata.py:75–79,98–102`; offline ফলের scope: `sanity.json`। এই task-এর implementation/checks-এ blocker নেই; runtime ফল এখনও অজানা।
