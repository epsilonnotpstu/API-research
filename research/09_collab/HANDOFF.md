# 🚩 RESUME POINT — 2026-11-14 (বিদ্যুৎ বিভ্রাটের কারণে বিরতি)

**অবস্থা:** কোনো process, Docker container বা Codex task চলছে না। সব শেষ বা পরিষ্কারভাবে থামানো হয়েছে।

## ✅ সম্পন্ন (এই session)
| কাজ | Owner | ফল |
|---|---|---|
| Batch 2 (scout-api) | Claude | `08_experiments/E1_pilot/pilot_results/BATCH2_RESULTS.md` |
| Labeller A: 99টি fingerprint | Claude | `pilot_results/batch2_baseline_s1_labels_code.csv` |
| T13 v0.3 re-labelling | Codex | গৃহীত; κ 0.75 (`E2_labelling/comparison_triage_codex_v03.csv`) |
| T14 harness_v2 | Codex | গৃহীত; তিন SUT-এ runtime-এ কাজ করে |
| T15 blind labeller B | Codex | গৃহীত; A–B κ 0.70 (`E2_labelling/batch2_AB_agreement.md`) |
| Adjudication: 18টি open-schema item | Supervisor | UNDECIDABLE |
| Petstore batch | Claude | `pilot_results/PETSTORE_RESULTS.md` |
| Market batch | Claude | `pilot_results/MARKET_RESULTS.md` (তিন SUT-এর তুলনাসহ) |
| specmut `--only-ops` + `tools/eligible_ops.py` (editable 2xx schema শর্তসহ) | Claude | `tools/test_only_ops.py` 5/5; specmut 144/144; pipeline PASS |
| harness_v2: `ORACLE_POOL`, `FAULTS`, docker-pull fallback | Claude | `bash -n` OK |

## ⏸️ মাঝপথে থামানো (প্রথমে এটা আবার চালাতে হবে)
**Scout-api RESPONSE_ORACLE pool batch.** উদ্দেশ্য: seed-নির্ভরতা (scout: 90/0/0) কমে কিনা দেখা।
- থামানো run: `runs/scout-api/20261114T025723Z_batch_1771572_*` (harness exit 130, অসম্পূর্ণ)।
- তার আগের বাতিল run: `20261114T025044Z_batch_1756007_*` (DNS ত্রুটি; পুরোনো pool)।
- দুটোই diagnostic; analysis-এ ব্যবহার করা যাবে না।

পুনরায় চালানোর command (বিদ্যুৎ ও internet ফিরলে, আনুমানিক 15 মিনিট):
```bash
cd "/home/afridi/Documents/API research/research/08_experiments/E1_pilot/harness_v2"
FAULTS=RESPONSE_ORACLE ORACLE_POOL=baseline SCHEMA_CHECKS=response_headers_conformance BUDGET_SECONDS=300 \
  ./run_batch.sh scout-api 1 2 3 > ../scout_oraclepool3.console.log 2>&1
```
তারপর: তিন seed-এর replay/fresh NEW তুলনা করা Batch 2-এর 90/0/0-এর সাথে → `MARKET_RESULTS.md` §4-এর পয়েন্ট 4 হালনাগাদ।

## ⏭️ পরের কাজ (ক্রমানুসারে)
1. **Supervisor:** `08_experiments/E2_labelling/batch2_adjudication.csv`-এ BOTH-এর 12টি item (B015, B016, B079, B080, B020, B044, B045, B054, B055, B084, B087, B088) → `supervisor_L1/L2/note`।
2. **Claude:** উপরের scout pool batch পুনরায় চালানো ও analysis।
3. **Claude + Codex:** petstore ও market baseline-এর labelling, A/B protocol-এ।
   - Codex task file (T16, T17) এখনো লেখা হয়নি।
   - Blind sheet scout-এর মতো বানাতে হবে।
4. **Market-এর 406 status:** exception handler দেখে IMPL/BOTH নিশ্চিত করা।
5. **REQUEST_LOOSE metric:** NEW-এর বদলে VANISHED; analysis script-এ যোগ করা।
6. **cwa-verification build (JDK 11)** → চতুর্থ SUT।
7. **পরের ধাপ:** JaCoCo coverage report; code-mutation দিক (E5)।

## নিয়ম মনে রাখা
- Labeller A = Claude, B = Codex (blind); adjudication supervisor-এর।
- Codex শুধু `-s workspace-write`।
- Auth header কখনো print করা যাবে না।
- Batch চলাকালে `tools/` edit করা যাবে না।
