"""Replay the project oracle for T16; retain locators without credential values."""
import bisect
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / '08_experiments/tools'))
import conformance

RUNS = {
 'swagger-petstore': '08_experiments/E1_pilot/runs/swagger-petstore/20261114T021748Z_batch_1701236_baseline_NONE_p0_s1',
 'market': '08_experiments/E1_pilot/runs/market/20261114T023303Z_batch_1724645_baseline_NONE_p0_s1',
}

def fingerprint(raw):
    value = raw
    for _ in range(3):
        if isinstance(value, list):
            return json.dumps(value,ensure_ascii=False,separators=(',',':'))
        value = json.loads(value)
    raise ValueError('fingerprint did not decode to an array')

def structure(value, depth=0):
    if depth > 3:
        return type(value).__name__
    if isinstance(value,dict):
        return {k:structure(v,depth+1) for k,v in value.items() if len(k)<50 and k.isascii()}
    if isinstance(value,list):
        return [structure(v,depth+1) for v in value[:3]]
    return type(value).__name__

def public_error(text):
    # Record only fixed API error text and validator metadata, never user values.
    fixed = ['No status provided','No tags provided','No Name provided','No name provided',
             'No Pet provided','No petId provided','No User provided','No Username provided',
             'No username provided','No Order provided','No file uploaded','Pet not found','User not found']
    for phrase in fixed:
        if phrase in text:
            return phrase
    try:
        value=json.loads(text)
    except ValueError:
        return 'non-JSON error body'
    if isinstance(value,dict):
        return {'keys':list(value), 'field_error_names':sorted(set(re.findall(r'"field"\s*:\s*"([A-Za-z_][A-Za-z0-9_.]*)"',text)))}
    return type(value).__name__

def spec_index(source):
    newline=[-1]+[m.start() for m in re.finditer('\n',source)]
    decoder=json.JSONDecoder(); loc={}
    def scan(pos,pointer):
        while source[pos].isspace():pos+=1
        loc[pointer]=bisect.bisect_left(newline,pos)
        if source[pos] not in '{[':return decoder.raw_decode(source,pos)[1]
        obj=source[pos]=='{';pos+=1;n=0
        while True:
            while source[pos].isspace() or source[pos]==',':pos+=1
            if source[pos] in '}]':return pos+1
            if obj:
                key,pos=decoder.raw_decode(source,pos)
                while source[pos].isspace() or source[pos]==':':pos+=1
                key=key.replace('~','~0').replace('/','~1')
            else:key=str(n)
            pos=scan(pos,pointer+'/'+key);n+=1
    scan(0,'');return loc

def main():
    for sut,run_rel in RUNS.items():
        run=ROOT/run_rel
        spec_data=json.loads((run/'spec.original.json').read_text())
        oracle=conformance.Spec(spec_data)
        items=list(csv.DictReader((ROOT/f'08_experiments/E2_labelling/{sut}_baseline_s1_blind.csv').open()))
        by_fp={fingerprint(i['fingerprint']):i['item_id'] for i in items}
        matches={i['item_id']:[] for i in items}; unknown=collections.Counter(); meta={}
        all_violations=[]
        for n,raw in enumerate((run/'exchanges.jsonl').open(),1):
            x=json.loads(raw);req,resp=x['request'],x['response']
            template,pp=oracle.match(req['path'],req['method'],req.get('origin'))
            op,params=oracle.operation(template,req['method']) if template else (None,[])
            problems=conformance.request_problems(oracle,params,op,x,pp) if op else []
            rb=req.get('body',{});text=rb.get('text','')
            try:body=json.loads(text) if text else None
            except ValueError:body=None
            response_text=resp.get('body',{}).get('text','')
            meta[str(n)]={'method':req['method'],'template':template,'status':resp['status'],
                         'timestamp':x.get('ts'),
                         'query_names':list(req.get('query',{})),
                         'content_type':req.get('headers',{}).get('content-type',''),
                         'response_content_type':resp.get('headers',{}).get('content-type',''),
                         'body_size':rb.get('size'), 'body_truncated':rb.get('truncated'),
                         'body_decode_error':rb.get('decode_error'),'body_shape':structure(body),
                         'response_sha256':hashlib.sha256(response_text.encode()).hexdigest(),
                         'response_size':resp.get('body',{}).get('size'),
                         'response_error':public_error(response_text) if int(resp['status'])>=400 else None,
                         'request_problems':[{'pointer':p,'keyword':i.get('keyword')} for p,m,i in problems],
                         'request_uncheckable':getattr(problems,'uncheckable',[])}
            for v in conformance.check(oracle,x):
                iid=by_fp.get(v['fingerprint'])
                if iid:matches[iid].append(n)
                else:unknown[v['fingerprint']]+=1
                all_violations.append({'item_id':iid,'exchange_line':n,'kind':v['kind'],'pointer':v['pointer']})
        mapped=[]
        for item in items:
            iid=item['item_id'];assert len(matches[iid])==int(item['occurrences']),(sut,iid,len(matches[iid]),item['occurrences'])
            mapped.append({'item_id':iid,'exchange_lines':matches[iid]})
        assert not unknown,(sut,unknown)
        for name,value in [('exchange_map',mapped),('exchange_meta',meta),('diagnostics',all_violations),
                           ('spec_locations',spec_index((run/'spec.original.json').read_text()))]:
            (OUT/f'{sut}_{name}.json').write_text(json.dumps(value,indent=2,ensure_ascii=True)+'\n')
        summary={'sut':sut,'run':run_rel,'exchanges':n,'items':len(items),'diagnostic_occurrences':len(all_violations),
                 'exact_occurrence_counts':True,'unmatched_fingerprints':dict(unknown),
                 'fingerprint_outer_JSON_string_normalized':True,
                 'oracle_version':spec_data.get('openapi',spec_data.get('swagger')),'base':oracle.base}
        (OUT/f'{sut}_replay_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(json.dumps(summary))
        for item,mapped_item in zip(items,mapped):
            sample=meta[str(mapped_item['exchange_lines'][0])]
            print(item['item_id'],item['kind'],item['status'],'n',len(mapped_item['exchange_lines']),
                  'ex',mapped_item['exchange_lines'][:3], 'type',sample['content_type'],
                  'error',sample['response_error'])

if __name__=='__main__':main()
