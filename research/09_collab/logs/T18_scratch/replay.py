"""T18 local replay and safe request metadata; no external execution."""
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
RUN = ROOT / '08_experiments/E1_pilot/runs/cwa-verification/20261114T084828Z_batch_118863_baseline_NONE_p0_s1'
SOURCE = ROOT / '08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server/src/main/java/app/coronawarn/verification'
ORIGIN = 'http://sut-cwa-verification:8080'
def normalize(value):
    while isinstance(value,str): value=json.loads(value)
    return json.dumps(value,ensure_ascii=False,separators=(',',':'))
def save(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=True)+'\n')
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
    data=json.loads((RUN/'spec.original.json').read_text())
    oracle=conformance.Spec(data,deploy_origin=ORIGIN)
    items=list(csv.DictReader((ROOT/'08_experiments/E2_labelling/cwa-verification_baseline_s1_blind.csv').open()))
    lookup={normalize(i['fingerprint']):i['item_id'] for i in items}
    matches={i['item_id']:[] for i in items}; meta={}; unknown=[]; all_d=[]
    for n,raw in enumerate((RUN/'exchanges.jsonl').open(),1):
        x=json.loads(raw); req=x['request']; resp=x['response']
        template,pp=oracle.match(req['path'],req['method'],req.get('origin'))
        op,params=oracle.operation(template,req['method']) if template else (None,[])
        problems=conformance.request_problems(oracle,params,op,x,pp) if op else []
        text=req.get('body',{}).get('text','')
        try: body=json.loads(text) if text else None
        except ValueError: body=None
        fields={k:{'type':type(v).__name__,'length':len(v) if isinstance(v,(str,list,dict)) else None} for k,v in (body.items() if isinstance(body,dict) else []) if k in ['registrationToken','responsePadding','key','keyType','keyDob','tan']}
        # Only validator metadata is retained, never token/GUID/header values.
        if isinstance(body,dict):
            if 'keyType' in body: fields['keyType']['enum_member']=body['keyType'] if body['keyType'] in ['GUID','TELETAN'] else 'other'
            for field in ['registrationToken','tan']:
                if isinstance(body.get(field),str): fields[field]['uuid_v4_pattern']=bool(re.fullmatch(r'[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}',body[field]))
        ds=conformance.check(oracle,x)
        for d in ds:
            iid=lookup.get(d['fingerprint'])
            if not iid:unknown.append(d['fingerprint'])
            else:matches[iid].append(n)
            all_d.append({'exchange_line':n,'item_id':iid,'kind':d['kind']})
        meta[str(n)]={'method':req['method'],'template':template,'status':resp['status'],'request_body_present':bool(text),'request_fields':fields,'body_is_object':isinstance(body,dict),'request_unknown_field_count':len(set(body)-set(fields)) if isinstance(body,dict) else 0,'request_issues':[{'pointer':p,'keyword':identity.get('keyword')} for p,m,identity in problems],'uncheckable':getattr(problems,'uncheckable',[]),'response_body_size':resp.get('body',{}).get('size'),'response_body_present':bool(resp.get('body',{}).get('text','')),'response_capture_incomplete':bool(resp.get('body',{}).get('truncated') or resp.get('body',{}).get('decode_error')),'cwa_fake':req.get('headers',{}).get('cwa-fake') if req.get('headers',{}).get('cwa-fake') in ['0','1'] else None,'diagnostic_items':[lookup.get(d['fingerprint']) for d in ds]}
    for i in items:assert len(matches[i['item_id']])==int(i['occurrences'])
    assert not unknown
    save('exchange_map.json',matches);save('exchange_meta.json',meta);save('diagnostics.json',all_d)
    save('spec_locations.json',spec_index((RUN/'spec.original.json').read_text()))
    summary={'status':'PASS','exchanges':n,'items':len(items),'diagnostic_occurrences':len(all_d),'exact_counts':True,'unmatched_fingerprints':unknown,'deploy_origin':ORIGIN,'generator_spec_identical':data==json.loads((RUN/'generator-input.json').read_text()),'per_item':{k:len(v) for k,v in matches.items()}}
    save('replay_summary.json',summary);print(json.dumps(summary))
    for iid,lines in matches.items():
        groups=collections.Counter(json.dumps({k:meta[str(i)][k] for k in ['request_body_present','request_fields','request_unknown_field_count','cwa_fake']},sort_keys=True) for i in lines)
        print(iid,'samples',lines[:5],'groups',len(groups))
        for signature,count in groups.most_common(12): print(count,signature)
    for pointer,line in spec_index((RUN/'spec.original.json').read_text()).items():
        if '/schemas/' in pointer and pointer.count('/')<=3:print('SCHEMA',pointer,line)
if __name__=='__main__':main()
