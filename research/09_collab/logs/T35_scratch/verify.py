"""Independent direct-schema recount and read-only/secret checks for T35."""
import base64
import hashlib
import json
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EMB = ROOT/'08_experiments/_external/emb'


def resolved(document, node):
    if isinstance(node,dict):
        if '$ref' in node:
            target = document
            for part in node['$ref'][2:].split('/'):
                target = target[part.replace('~1','/').replace('~0','~')]
            return resolved(document,target)
        return {k:resolved(document,v) for k,v in node.items()}
    if isinstance(node,list):
        return [resolved(document,v) for v in node]
    return node


def main():
    rows=[]
    for seed,expected_fresh,expected_good in [(1,392,81),(3,361,74)]:
        fresh=f'20261114T183929Z_batch_940129_mutated_REQUEST_STRICT_p30_s{seed}'
        base=f'20261114T183929Z_batch_940129_baseline_NONE_p0_s{seed}'
        rp=ROOT/'08_experiments/E1_pilot/runs/market'/fresh
        old=json.loads((rp/'spec.original.json').read_text())
        new=json.loads((rp/'spec.test.json').read_text())
        schema=resolved(old,old['paths']['/customer/contacts']['put']['parameters'][0]['schema'])
        validator=jsonschema.Draft4Validator(schema)
        ns=new['paths']['/customer/contacts']['put']['parameters'][0]['schema']
        assert ns['required']==['_links','address','phone']
        assert ns['properties']['phone']['maxLength']==1
        for run in (fresh,base):
            violations,good=[],[]
            with (ROOT/'08_experiments/E1_pilot/runs/market'/run/'exchanges.jsonl').open() as f:
                for n,line in enumerate(f,1):
                    ex=json.loads(line)
                    q=ex['request']
                    if q['method']!='PUT' or q['path']!='/customer/contacts':
                        continue
                    try:
                        body=json.loads(q['body']['text'])
                    except (ValueError,KeyError):
                        continue
                    if not isinstance(body,dict) or not validator.is_valid(body):
                        continue
                    if len(body.get('phone',''))>1 or len(body.get('address',''))>1:
                        violations.append(n)
                        if 200<=ex['response']['status']<300:
                            assert '_links' not in body
                            good.append(n)
                        if run==fresh:
                            assert isinstance(body['_links'],list)
                            assert next(iter(body))=='_links'
                            assert ex['response']['status']==500
                            text=ex['response']['body']['text']
                            assert all(v in text for v in ('Expected relation name','com.fasterxml.jackson.databind.JsonMappingException','market.dto.ContactsDTO','_links'))
            if run==fresh:
                assert len(violations)==expected_fresh and not good
            else:
                assert len(good)==expected_good
            rows.append({'run':run,'direct_body_length_violations':len(violations),
                         'accepted_length_violations':len(good),'first_violation_line':violations[0]})
    hashes=json.loads((OUT/'protected_sha256.json').read_text())
    mismatches=[p for p,digest in hashes.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=digest]
    assert not mismatches
    # Search output files for fixture header values, encoded tokens, and decoded components.
    # Values are only held in memory and are never written or printed.
    fixture=yaml.safe_load((EMB/'auth/market-auth.yaml').read_text())
    secrets=set()
    for role in fixture['auth']:
        for h in role.get('fixedHeaders',[]):
            v=h.get('value','')
            if not isinstance(v,str) or not v:
                continue
            secrets.add(v)
            if v.lower().startswith('basic '):
                token=v.split(' ',1)[1]
                secrets.add(token)
                decoded=base64.b64decode(token).decode()
                secrets.add(decoded)
                secrets.update(s for s in decoded.split(':') if len(s)>=6)
    targets=[p for p in OUT.iterdir() if p.is_file()]+[ROOT/'09_collab/reports/T35_report.md']
    secret_hits=[]
    for p in targets:
        if p.exists() and any(v in p.read_text() for v in secrets):
            secret_hits.append(str(p.relative_to(ROOT)))
    assert not secret_hits
    result={'independent_recount':rows,'protected_files_checked':len(hashes),
            'protected_hash_mismatches':mismatches,'secret_scan_files':sum(p.exists() for p in targets),
            'secret_scan_hit_files':secret_hits,'execution':'offline Python only; no Java/class execution',
            'total_exchanges':sum(x['total'] for x in json.loads((OUT/'traffic_summary.json').read_text()))}
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
