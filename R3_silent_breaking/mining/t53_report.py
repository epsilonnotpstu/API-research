#!/usr/bin/python3
"""Independent delivered-byte/reference audit and aggregate Bengali report."""
from collections import Counter
import csv
import io
import json
from pathlib import Path
import posixpath
import re
import runpy

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
B=runpy.run_path(str(HERE/'t53_build.py'))
P=B['P'];C=B['C'];V=B['V']

def audit():
    sample=B['freeze_guard']()
    out=BASE/'packages/r3_blind'
    files={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()}
    log=json.loads((HERE/'key/r3_build_log.json').read_text())
    assert {p:P['sha'](data) for p,data in files.items()}==log['package_hashes']
    assert all(P['sha']((HERE/name).read_bytes())==value for name,value in log['build_code_hashes'].items())
    assert files['TASK_R3.md']==(BASE/'plan/TASK_R3.md').read_bytes()
    findings=Counter()
    for data in files.values():
        findings.update(V['findings'](data))
    assert not findings
    contracts={p:json.loads(data) for p,data in files.items() if '/contract/' in p}
    local=0;remote=0
    for path,obj in contracts.items():
        for ref in C['references'](obj):
            filename,_,fragment=ref.partition('#')
            if re.match(r'^[\w+.-]+:',filename):remote+=1;continue
            target=posixpath.normpath(posixpath.join(posixpath.dirname(path),filename)) if filename else path
            assert target in contracts
            C['at'](contracts[target],C['parts'](fragment));local+=1
    with (HERE/'key/r3_key.csv').open() as stream:keys=list(csv.DictReader(stream))
    with (HERE/'heads.tsv').open() as stream:heads=list(csv.DictReader(stream,delimiter='\t'))
    inventory=json.loads((HERE/'pool4_inventory.json').read_text())
    failures=json.loads((HERE/'key/r3_build_failures.json').read_text())
    tests=json.loads((BASE/'collab/logs/T53_scratch/test_summary.json').read_text())
    assert tests['failures']==tests['errors']==0 and not tests['synthetic_only']
    summary=dict(log['summary'],repositories=len(heads),pool=sum(r['pool'] for r in inventory),
        bot_exclusions=sum(r['bot_exclusions'] for r in inventory),
        before_files=sum('/before/' in p for p in files),after_files=sum('/after/' in p for p in files),
        contract_files=len(contracts),redacted_files=sum(b'[REDACTED]' in data for data in files.values()),
        local_reference_incidents=local,remote_reference_incidents=remote,missing_local_references=0,
        tests=tests['tests'],test_failures=0,test_errors=0,
        privacy_findings=dict(findings),package_sha256=P['sha'](P['jb'](log['package_hashes'])),
        sampled_repositories=len({r['repo'] for r in sample}),
        no_document_items=sum(r['contract_mapping_mode']=='no_checked_in_document' for r in keys),
        manual_commit_judgements=0,candidate_patch_displays=0,substitutions=0,
        network_used=False,upstream_execution=False,board_read=False,forbidden_study_material_read=False)
    (HERE/'verification_t53.json').write_bytes(P['jb'](summary))
    return summary,inventory,sample,keys,failures,tests

def main():
    s,inventory,sample,keys,failures,tests=audit()
    sampled=Counter(r['repo'] for r in sample);delivered=Counter(r['repo'] for r in keys)
    lines=['# T53 — R3 pool4, frozen sample ও blind packages','',
        f'কাজ সম্পন্ন: ৫৪টি bare clone-এর pinned HEAD থেকে **{s["pool"]:,} candidates**; frozen deterministic sample **{s["sampled"]} commits**, delivered **{s["delivered"]} items**, mechanical build failures **{s["build_failures"]}**। কোনো commit judgement, resampling বা substitution হয়নি। Evidence: `mining/heads.tsv`, `mining/pool4.json`, `mining/pool4_inventory.json`, `mining/freeze4.json`, `mining/sample4.json`, `mining/freeze4_sample.json`, `mining/verification_t53.json`। এই report-এর সংক্ষিপ্ত paths-এর ভিত্তি `R3_silent_breaking/`।','',
        'HEAD-এর first-parent chain-এ non-merge candidates নেওয়া হয়েছে; committer timestamp ≥ 2023-01-01T00:00:00Z। Non-monotonic dates-এর জন্য সব history metadata traverse করে Python-এ timestamp filter হয়েছে। T46 production-path regex ও T50 exclusions পুনর্ব্যবহার হয়েছে; migration/build exclusions স্পষ্টভাবে যোগ করা হয়েছে। Top-level OpenAPI/Swagger key detection সব blob type-এ হয়েছে; parent-এর local `$ref` closure এবং parent/child roots document exclusion নির্ধারণ করেছে। Bot name/email scratch process-এর memory-তে পরীক্ষা হয়েছে; upstream attribution কোনো output/log-এ লেখা হয়নি। Bot counts সব non-merge window commits-এর, behaviour eligibility-র আগেই গণনা। Evidence: `mining/t53_pool.py:behaviour,is_openapi,roots_and_closure,history,discover`; `collab/logs/T53_scratch/bot_scan.py`।','',
        'প্রতি behaviour file-এ whitespace-insensitive `-w --ignore-blank-lines` emptiness check হয়েছে; formatting-only ও zero-numstat rename-only files count থেকে বাদ গেছে। বাকি files ≤৮ এবং added+deleted lines ≤৪০০। Modified rename-এর দুটো production path থাকলে দুটোই আট-path limit-এ গণনা হয়েছে। Contract-document rename/mode-only change-ও conservative document-change screen-এ পড়ে। Pool freeze-এর আগে patch বা message চাওয়া হয়নি; document detection-এর source bytes judgement ছাড়াই machine-এ পরীক্ষা হয়েছে। Evidence: `mining/t53_pool.py:Git.nonwhite,discover`; `mining/freeze4.json:rules`; `mining/test_t53.py:SyntheticTests`।','',
        'Pool, code bundle, pinned heads, inventory ও document-history hashes freeze-এ আছে। Repo byte order-এ sorted SHAs থেকে ঠিক `random.Random("20261117:" + repo).sample(shas, min(3, len(shas)))` প্রয়োগ করা হয়েছে। Sample hash লেখা হয়েছে package construction-এর আগে। নতুন salt শুধু `mining/key/r3_shuffle_salt.txt`-তে; HMAC-SHA256 order-এ B-IDs বরাদ্দ হয়েছে build-এর আগে। Failed item-এর ID বজায় থাকে; অন্য commit দিয়ে পূরণ করা হয় না। Evidence: `mining/t53_sample.py:select,guard`; `mining/t53_build.py:shuffled,prepare`; `mining/freeze4_sample.json`; `mining/key/r3_key.csv`; `mining/key/r3_build_failures.json`।','',
        'নিচে প্রতি repo-র pool, frozen sample, delivered items ও bot exclusions আছে। Row evidence: `mining/pool4_inventory.json:repo`, `mining/sample4.json:repo`, `mining/key/r3_key.csv:repo`।','',
        '| Repo | Pool4 | Sample | Delivered | Bot exclusions |','|---|---:|---:|---:|---:|']
    for row in inventory:
        repo=row['repo'];lines.append(f'| {repo} | {row["pool"]} | {sampled[repo]} | {delivered[repo]} | {row["bot_exclusions"]} |')
    lines+=['',f'সর্বমোট bot exclusions **{s["bot_exclusions"]:,}**। কোনো bot identity বা author/email list রাখা হয়নি। Mechanical build failures **{len(failures)}**; নিচে history identifier ছাড়া failure record দেওয়া হলো। Evidence: `mining/pool4_inventory.json:bot_exclusions`; `mining/key/r3_build_failures.json`।','']
    if failures:
        lines+=['| Item | Repo | Failure class | Mechanical reason |','|---|---|---|---|']
        for f in failures:lines.append(f'| {f["item_id"]} | {f["repo"]} | {f["failure_class"]} | {f["reason"]} |')
    else:lines+=['Build failure নেই।']
    lines+=['',
        f'Package `packages/r3_blind/`: **{s["delivered"]} items / {s["files"]:,} files / {s["bytes"]:,} bytes ({s["bytes"]/1048576:.2f} MiB)**। Before files {s["before_files"]}, after files {s["after_files"]}, contract files {s["contract_files"]}; `{s["redacted_files"]}` files-এ redaction marker আছে। `items.csv` LF এবং চারটি নির্ধারিত column-এ; item.md-তে শুধু repo/language/paths। Patches-এ file headers ও hunks আছে; index/history headers নেই। Added/deleted source-এর শুধু বিদ্যমান side থাকে। Parent-এ checked-in document না থাকা items {s["no_document_items"]}। Evidence: `mining/key/r3_build_log.json`; `mining/verification_t53.json`; `mining/test_t53.py:ActualArtifactTests`।','',
        'Route strings, Spring/JAX-RS annotations ও Go swagger comments থেকে mechanical mapping হয়েছে; mapped parent operations এবং transitive local `$ref` closure দেওয়া হয়েছে। Mapping না হলে whole document; বড় হলে path-byte-order operation prefix ও সম্পূর্ণ closure দিয়ে প্রতি document সর্বোচ্চ ২,০০০ canonical JSON lines রাখা হয়েছে। প্রথম complete operation-ও bound-এ না ধরলে mechanical failure; partial node বা metadata-only substitute দেওয়া হয়নি। Mapped closure-তে এই fallback cap প্রযোজ্য নয়। JSON-formatted files তাদের মূল path/extension-এ আছে এবং YAML 1.2-তেও valid। Mode ও details শুধু private key/build log-এ; aggregate modes নিচে। Evidence: `mining/t53_contracts.py:routes,matched_operations,closure,build`; `mining/key/r3_key.csv:contract_mapping_mode`।','',
        '| Contract mapping mode | Items |','|---|---:|']
    for mode,count in sorted(s['mapping_modes'].items()):lines.append(f'| {mode} | {count} |')
    lines+=['',
        f'Aggregate `annotation_touched=true`: **{s["annotation_touched"]}**; aggregate `spec_updated_90d=true`: **{s["spec_updated_90d"]}**। Per-item values শুধু `mining/key/`-তে। Exact JVM names/regex ও Go regex `mining/annotation_patterns.json`-এ আছে; annotation scan শুধু delivered added/removed hunk lines-এ। ৯০ দিনের flag একই first-parent chain-এর পরবর্তী commits, merge-সহ, date interval `(commit date, commit date + 90 days]`-এ parent/child root বা parent-reference change পরীক্ষা করে; HEAD-এর বাইরে যায় না। Evidence: `mining/t53_build.py:annotation_touched,updated_90d`; `mining/key/document_history.json`; `mining/key/r3_key.csv`।','',
        f'Privacy/history scans pass: email, attribution, credentials, authentication literals, encoded literals, dates, full/short commit ও parent identifiers, complete message lines এবং message-derived PR/issue references পরীক্ষা হয়েছে। Redaction `[REDACTED]`; raw values বা exception diagnostics লেখা/দেখানো হয়নি। কোনো candidate patch interactive display হয়নি। Local reference incidents **{s["local_reference_incidents"]}**, missing targets/pointers **০**, remote references **{s["remote_reference_incidents"]}**; remote URL fetch হয়নি। `TASK_R3.md` byte-identical copy pass; source task-এর content display হয়নি। Evidence: `mining/t53_privacy.py`; `mining/t53_build.py:context_for_repo,build_item,scan_package`; `mining/t53_report.py:audit`; `mining/verification_t53.json`।','',
        f'**{tests["tests"]} tests pass**, failures/errors **০/০**, `/usr/bin/python3 -I -B`-এ। পুরো ৫৪-repo pool পুনর্নির্মাণ করে pool/inventory/document-history hashes তুলনা হয়েছে; sample ও salt-based shuffle replay, synthetic candidate/bot rules, privacy/leakage, annotation/90-day boundary, package separation/overwrite refusal এবং exact package/key reconstruction পরীক্ষা হয়েছে। Synthetic Git identities nonpersonal placeholders; temporary bare repos test শেষে মুছে গেছে। Test diagnostics-এ source values suppress করা হয়েছে। Evidence: `mining/test_t53.py`; `collab/logs/T53_scratch/test_summary.json`।','',
        'Pre-freeze প্রথম traversal memory-bound object-reader failure-এ থেমেছিল; freeze বা sample তখন হয়নি। Bounded blob batches দিয়ে পুনরায় build হয়েছে। Synthetic checks-এ ধরা implementation errors-ও freeze-এর আগে ঠিক হয়েছে; কোনো candidate বিচার বা sample selection দিয়ে correction করা হয়নি। Initial/final synthetic summaries ও pool progress scratch-এ আছে; final full replay frozen hashes মেলায়। Evidence: `collab/logs/T53_scratch/`; `mining/t53_pool.py:Git.classify`; `mining/test_t53.py:test_full_pool_rebuild_and_hash`।','',
        '⚠️ Threats: curated bare clones, first-parent-only history, fixed time window, lexical production-path rules ও size cap population coverage সীমিত করে। Static path filtering server behaviour নিশ্চিত করে না; utility/business logic miss হতে পারে। Per-repo সর্বোচ্চ তিনটির sample commit-uniform within repo হলেও pooled commits-এর uniform sample নয়; shared history/files স্বাধীন observation নয়। Root parsing ও local lexical `$ref` detection atypical syntax miss করতে পারে; remote references resolve করা হয়নি। Evidence: `mining/freeze4.json:rules`; `mining/t53_pool.py`; `mining/t53_contracts.py`।','',
        '⚠️ Route mapping syntax-based: class prefix, mount suffix ও template normalization runtime routing নিশ্চিত করে না; helper/DTO-only edits-এ mapping নাও পাওয়া যায়। Fallback byte-order projection সংশ্লিষ্ট operation বাদ দিতে পারে, আর complete sources সব dependencies দেয় না। Canonical JSON serialization, YAML scalar normalization ও privacy redaction source/document readability বা details বদলাতে পারে। Lexical privacy/leakage scans সব semantic hint বা ব্যক্তিগত attribution শনাক্ত করার নিশ্চয়তা নয়। Build failures sample-এর অংশ রয়ে গেছে; delivered subset-এ availability bias থাকতে পারে। Evidence: `mining/t53_contracts.py`; `mining/t53_privacy.py`; `mining/key/r3_build_failures.json`।','',
        '⚠️ `annotation_touched` lexical annotation presence, runtime contract impact নয়। `spec_updated_90d` একই repo-তে কোনো checked-in document change বোঝায়; sampled behaviour-এর সঙ্গে সম্পর্ক প্রতিষ্ঠা করে না। HEAD-এর কাছে ৯০ দিনের observation অসম্পূর্ণ হতে পারে; non-monotonic committer dates temporal interpretation দুর্বল করে। কোনো label, coder output বা judgement field তৈরি হয়নি। কাজ সম্পূর্ণ offline; upstream-এ read-only Git, কোনো checkout/network/upstream-content execution নয়; research/ বা নিষিদ্ধ study materials/board modify/read করা হয়নি। Evidence: `mining/t53_build.py`; `mining/verification_t53.json`; `mining/test_t53.py`।','']
    (BASE/'collab/reports/T53_report.md').write_text('\n'.join(lines))
    print(json.dumps({k:s[k] for k in ['repositories','pool','sampled','delivered','build_failures','files','bytes','tests','local_reference_incidents','remote_reference_incidents']}))

if __name__=='__main__':main()
