#!/usr/bin/env python3
"""Independent structural, provenance and material-conclusion checks for T41."""
import ast
import base64
import collections
import csv
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("t41_miner", HERE / "mine_history.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
CHECKS = []


def check(condition, label):
    assert condition, label
    CHECKS.append(label)


def rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def strip_java_imports_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"(?m)^import .*?;\s*", "", text)
    return re.sub(r"\s+", "", text)


def main():
    anchors = json.loads((HERE / "anchors.json").read_text())
    output = rows(HERE / "future_oracle.csv")
    final = {r["item_id"]: r for r in rows(m.LABELS / "final_labels_baseline_s1.csv") if r["sut"] in m.SUTS}
    check(len(output) == 62 and {r["item_id"] for r in output} == set(final), "exact 62 baseline IDs, no duplicates or scout rows")
    check(list(output[0]) == ["item_id", "sut", "proposition", "anchor_commit", "fix_direction", "evidence_locators", "commit_dates", "confidence (1–3)", "notes"], "exact requested CSV columns")
    directions = collections.Counter(r["fix_direction"] for r in output)
    check(directions == {"spec_changed_to_match_code": 3, "unchanged_at_head": 31, "changed_unrelated": 1, "unclear": 27}, "all direction counts independently recounted")
    histories = {}
    for sut, a in anchors.items():
        repo = m.ROOT / a["upstream_clone"]
        check(m.git(repo, "rev-list", "-1", "HEAD").decode().strip() == a["head"], sut + " frozen HEAD")
        scores = [r for r in rows(HERE / "anchor_scores.csv") if r["sut"] == sut]
        best = max(int(r["matches"]) for r in scores if r["reachable_from_head"] == "True")
        check(a["matches"] == best == sum(r["state"] == "exact" for r in a["per_file"]), sut + " chosen score is the HEAD-ancestor maximum")
        check(best == a["global_best_matches"], sut + " HEAD-line maximum also equals all-ref maximum")
        check(a["fraction"] >= .8 and a["denominator"] == len(a["per_file"]), sut + " denominator and anchor threshold")
        for r in a["per_file"]:
            data = (m.ROOT / a["emb_source"] / r["path"]).read_bytes()
            check(m.blob(data) == r["emb_blob"], sut + " EMB blob " + r["path"])
            if r["upstream_blob"]:
                upstream = m.git(repo, "show", a["commit"] + ":" + r["upstream_path"])
                check(m.blob(upstream) == r["upstream_blob"], sut + " upstream blob " + r["upstream_path"])
        descendants = set(m.git(repo, "rev-list", "--all", "--ancestry-path=" + a["commit"], "^" + a["commit"]).decode().splitlines())
        histories[sut] = json.loads((HERE / (sut + "_all_descendant_history.json")).read_text())
        check(descendants == set(a["all_ref_post_anchor_descendants"]) == {h["commit"] for h in histories[sut]}, sut + " all-ref descendant coverage")
        check(set(a["post_anchor_reachable_commits"]) <= descendants, sut + " default post-anchor commits all descendants")
        check(all(len(h["message"]) <= 160 for h in histories[sut]), sut + " commit excerpts <=160 characters")
        for h in histories[sut]:
            actual = m.git(repo, "diff", "--name-only", h["parent"], h["commit"]).decode().splitlines()
            check(actual == h["files"], sut + " complete touched-file set " + h["commit"])
        if sut in {"swagger-petstore", "market"}:
            before = {p: oid for p, oid in m.tree(repo, a["commit"]).items() if p.endswith(".java")}
            after = {p: oid for p, oid in m.tree(repo, a["head"]).items() if p.endswith(".java")}
            check(before == after, sut + " complete upstream Java tree unchanged between anchor and HEAD")
            check(not any(any(p.endswith('.java') for p in h['files']) for h in histories[sut]), sut + " no Java touch in any-ref descendants")
    # Every actual SHA:path:line locator is checked against the original Git blob.
    for r in output:
        sut = r["sut"]
        a = anchors[sut]
        check(r["anchor_commit"] == a["commit"] and r["confidence (1–3)"] in {"1", "2", "3"}, r["item_id"] + " anchor/confidence")
        check("HEAD " + a["head"] in r["notes"], r["item_id"] + " explicit HEAD state")
        locs = re.findall(r"([a-f0-9]{40}):([^;:\n]+):(\d+)", r["evidence_locators"])
        check(bool(locs), r["item_id"] + " has a full-SHA source locator")
        for commit, path, n in locs:
            lines = m.git(m.ROOT / a["upstream_clone"], "show", commit + ":" + path).decode().splitlines()
            check(0 < int(n) <= len(lines), r["item_id"] + " valid Git locator " + commit + ":" + path + ":" + n)
    pet = anchors["swagger-petstore"]
    repo = m.ROOT / pet["upstream_clone"]
    docpath = "src/main/resources/openapi.yaml"
    before = m.git(repo, "show", pet["commit"] + ":" + docpath).decode().splitlines()
    after = m.git(repo, "show", pet["head"] + ":" + docpath).decode().splitlines()
    reverted = list(after)
    for n in [131, 173]:
        check(before[n-1].strip() == "required: false" and after[n-1].strip() == "required: true", "petstore exact target predicate at line " + str(n))
        reverted[n-1] = before[n-1]
    # Restore only the info version, then compare the ENTIRE document apart from trailing whitespace.
    version = next(n for n, v in enumerate(before) if v.startswith("  version:"))
    reverted[version] = before[version]
    check([v.rstrip() for v in before] == [v.rstrip() for v in reverted], "petstore whole YAML differs only by two required flags/version/trailing whitespace")
    cwa = anchors["cwa-verification"]
    repo = m.ROOT / cwa["upstream_clone"]
    old = json.loads(m.git(repo, "show", cwa["commit"] + ":api-docs.json"))
    new = json.loads(m.git(repo, "show", cwa["head"] + ":api-docs.json"))
    old_schema = old['components']['schemas']['RegistrationTokenRequest']
    new_schema = new['components']['schemas']['RegistrationTokenRequest']
    check('required' not in old_schema and new_schema['required'] == ['key','keyType'], "C002 actual JSON required-fields delta")
    check('pattern' not in old_schema['properties']['keyDob'] and new_schema['properties']['keyDob']['pattern'] == '^[XxA-Fa-f0-9]([A-Fa-f0-9]{63})$', "C002 actual JSON pattern delta")
    check(old['paths']['/version/v1/tan/verify']['post']['responses']['404'] == new['paths']['/version/v1/tan/verify']['post']['responses']['404'], "C005 exact 404 object unchanged, despite broad spec refresh")
    path = 'src/main/java/app/coronawarn/verification/model/RegistrationTokenRequest.java'
    oldjava = m.git(repo,'show',cwa['commit']+':'+path).decode()
    newjava = m.git(repo,'show',cwa['head']+':'+path).decode()
    check(strip_java_imports_comments(oldjava) == strip_java_imports_comments(newjava), "C002 entire model/annotations unchanged except imports/license")
    cwa_fix = next(h for h in histories['cwa-verification'] if h['commit'] == '40bd3a829f42e50a1dd764b4fa657a427bf32ef6')
    check(cwa_fix['files'] == ['api-docs.json'], "C002 fixing commit changes spec only")
    pet_fix = next(h for h in histories['swagger-petstore'] if h['commit'] == '9fb97b14d3c9d15d99aa8e3dbe323284cceb6bee')
    check(pet_fix['files'] == [docpath], "P014/P015 fixing commit changes spec only")
    witness = {r['item_id']:r for r in json.loads((HERE/'candidate_witnesses.json').read_text())}
    check(witness['P014']['counts'] == {'parameter_absent':1}, "P014 omitted query covers 1/1")
    check(witness['P015']['counts'] == {'parameter_absent':2,'parameter_present':3}, "P015 partial cluster 2/5")
    check(sum(w['present_values_all_empty'] for w in witness['P015']['witnesses']) == 3, "P015 other three query serializations contain only empty values")
    check(witness['C002']['counts']['new_spec_rejects_without_illegal_headers'] == 54 and len(witness['C002']['witnesses']) == 69, "C002 partial coverage 54/69 transport-clean")
    compare = rows(HERE/'agreement.csv')
    check(len(compare)==3 and sum(r['agreement']=='True' for r in compare)==2 and [r['item_id'] for r in compare if r['agreement']=='False']==['P014'], "agreement 2/3, sole disagreement P014")
    check(all(r['run_spec_semantic_equal'] for r in json.loads((HERE/'spec_provenance.json').read_text()).values()), "all three baseline run specs equal supplied deployed JSON")
    check(json.loads((HERE/'spec_provenance.json').read_text())['cwa-verification']['byte_identical'], "CWA deployed spec exact upstream anchor blob")
    protected = json.loads((m.SCRATCH/'protected_hashes.json').read_text())
    drift = [path for path,digest in protected.items() if m.sha((m.ROOT/path).read_bytes()) != digest]
    check(not drift, "all protected input hashes unchanged")
    for p in HERE.glob('*.py'):
        ast.parse(p.read_text(), filename=str(p))
        check(True, 'own script syntax '+p.name)
    # Read demo auth fixture only inside the scanner; never emit any secret value.
    fixture = m.EMB/'auth/market-auth.yaml'
    secret_tokens = set(re.findall(rb'\bBasic\s+([A-Za-z0-9+/=]{8,})', fixture.read_bytes()))
    check(bool(secret_tokens), "market fixture credential loaded only for silent output scanning")
    secret_values = set(secret_tokens)
    for token in secret_tokens:
        try:
            secret_values.add(base64.b64decode(token, validate=True))
        except ValueError:
            pass
    report = m.ROOT/'09_collab/reports/T41_report.md'
    scan = [p for p in HERE.rglob('*') if p.is_file()] + [report]
    hits = []
    for p in scan:
        if p.name == 'verification.json':
            continue
        data = p.read_bytes()
        if any(value in data for value in secret_values if len(value)>=8):
            hits.append(str(p.relative_to(m.ROOT)))
        if re.search(rb'(?i)\b(?:Basic|Bearer)\s+[A-Za-z0-9+/=._~-]{12,}', data):
            hits.append(str(p.relative_to(m.ROOT)))
    check(not hits, "all deliverables credential-output scan clean; no matched values emitted")
    forbidden = ['e4_blind/', 'e5_blind', 'E4_triage/e4_key.csv', 'E5_codemut/blind_key']
    for p in HERE.rglob('*'):
        if p.is_file() and p.suffix in {'.json','.csv','.diff','.txt'}:
            check(not any(x in p.read_text() for x in forbidden), 'evidence has no forbidden-input provenance '+str(p.relative_to(HERE)))
    result = {'status':'PASS','checks':len(CHECKS),'protected_input_files':len(protected),'protected_input_drift':drift,'checked_csv_items':len(output),'credential_scan_files':len(scan),'credential_scan_hits':0,'checks_detail':CHECKS}
    m.dump(HERE/'verification.json',result)
    manifest = {str(p.relative_to(m.ROOT)):m.sha(p.read_bytes()) for p in sorted(HERE.rglob('*')) if p.is_file()}
    manifest[str(report.relative_to(m.ROOT))] = m.sha(report.read_bytes())
    m.dump(m.SCRATCH/'artifact_manifest.json',manifest)
    print(json.dumps({k:v for k,v in result.items() if k!='checks_detail'},indent=2))


if __name__=='__main__':
    main()
