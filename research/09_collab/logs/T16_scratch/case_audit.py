"""Classify observable subcases and join log messages without exposing values."""
import collections
import csv
import json
import re
from urllib.parse import unquote
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay import OUT, ROOT, RUNS

def main():
    for sut,rel in RUNS.items():
        run=ROOT/rel;xs=[json.loads(s) for s in (run/'exchanges.jsonl').open()]
        lines=(run/'compose.log').read_bytes().decode().split('\n')
        items=list(csv.DictReader((ROOT/f'08_experiments/E2_labelling/{sut}_baseline_s1_blind.csv').open()))
        maps={r['item_id']:r for r in json.loads((OUT/f'{sut}_exchange_map.json').read_text())}
        log_locations=json.loads((OUT/f'{sut}_log_locations.json').read_text())
        records=[]
        if sut=='market':
            for item in items:
                groups=collections.defaultdict(list)
                for n in maps[item['item_id']]['exchange_lines']:
                    x=xs[n-1];resp=x['response'];text=resp['body']['text']
                    try:value=json.loads(text)
                    except ValueError:value={}
                    msg=value.get('message',text) if isinstance(value,dict) else str(value)
                    if resp['status']==500:
                        if '_links' in msg:category='HAL_links_binding'
                        elif 'quantity' in msg and ('out of range' in msg or 'InputCoercionException' in msg):category='quantity_int32_overflow'
                        elif 'NumberFormatException' in msg:category='path_int64_overflow'
                        else:raise AssertionError(('unknown market 500',n))
                    elif resp['status']==406:category='explicit_validation_406'
                    else:category='probe'
                    # The log index matches the URI/category queue before recording
                    # line numbers; a generic message prefix would cross operations.
                    loc=log_locations.get(str(n),{})
                    log_matches=[loc[k] for k in ('error_line','validation_or_notfound_line') if k in loc]
                    groups[category].append(n)
                    records.append({'item_id':item['item_id'],'exchange_line':n,'category':category,
                                    'log_lines':log_matches[:6]})
                print(item['item_id'],[(k,len(v),v[:3]) for k,v in groups.items()])
        else:
            for item in items:
                groups=collections.defaultdict(list)
                for n in maps[item['item_id']]['exchange_lines']:
                    x=xs[n-1]; req,resp=x['request'],x['response'];text=resp['body']['text']
                    try:value=json.loads(text)
                    except ValueError:value={}
                    msg=value.get('message',text) if isinstance(value,dict) else str(value)
                    category=None
                    if item['kind']=='VALID_REJECTED':
                        if 'Input error' in msg and 'Long' in msg:
                            segment=req['path'].split('/')[-2 if req['path'].endswith('/uploadImage') else -1]
                            assert re.fullmatch(r'-?\d+',segment) and not -(2**63)<=int(segment)<2**63
                            category='oracle_ignored_int64_range'
                        elif any(s in msg for s in ['No status provided','No tags provided','No Name provided','No file uploaded','No Order provided','No User provided']):
                            category='explicit_required_input_400'
                        elif 'Bad Request' in text and ('<html' in text.lower() or '<!doctype' in text.lower()):
                            category='transport_rejection'
                        elif 'Input error' in msg:
                            body=json.loads(req['body']['text'])
                            # Input validity is already disproved by the declared
                            # int32 format, independently of unknown-field policy.
                            assert isinstance(body.get('userStatus'),int) and not -(2**31)<=body['userStatus']<2**31
                            category='oracle_ignored_int32_range'
                        else:raise AssertionError(('unknown petstore VALID_REJECTED',n))
                    elif item['kind']=='REQUEST_UNCHECKABLE':
                        category='checker_body_coverage'
                    elif item['kind']=='SERVER_ERROR':
                        if item['template']=='/pet':
                            if req['headers'].get('content-type')=='application/json':
                                body=json.loads(req['body']['text']);assert isinstance(body,dict) and 'id' not in body
                                category='inferred_null_pet_id'
                            else:category='unresolved_pet_nonJSON_failure'
                        elif item['template']=='/store/order':category='inferred_form_wrapper_unboxing'
                        else:category='inferred_null_username_state'
                    elif item['kind']=='RESPONSE_SCHEMA':
                        category='status_contract' if item['pointer'].endswith('/enum') else 'missing_photoUrls'
                    elif item['kind']=='RESPONSE_PARSE':category='unquoted_JSON_string'
                    else:category='probe'
                    groups[category].append(n)
                    records.append({'item_id':item['item_id'],'exchange_line':n,'category':category,'log_lines':[]})
                if item['kind']=='VALID_REJECTED':print(item['item_id'],[(k,len(v),v[:3]) for k,v in groups.items()])
        (OUT/f'{sut}_case_audit.json').write_text(json.dumps(records,indent=2)+'\n')

if __name__=='__main__':main()
