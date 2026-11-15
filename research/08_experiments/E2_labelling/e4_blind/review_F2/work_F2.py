"""F2 local evidence inspection and search runner; never imports package code."""
import csv
import datetime
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def redact(line):
    # Preserve semantic token identifiers; suppress credential-bearing literals.
    if re.search(r'(?i)authorization|password|secret|api.?key|Bearer|Basic\s+', line):
        return '[REDACTED credential-looking line]'
    return line

def show(path, start, end):
    p = ROOT / path
    assert p.is_relative_to(ROOT) and p.parts[len(ROOT.parts)] in {'K01','K02','K03','K04'}
    print(path)
    for n, line in enumerate(p.open(), 1):
        if start <= n <= end:
            print(f'{n}: {redact(line.rstrip())}')

FIELDS = {3:'name',4:'attrs',6:'name',7:'group',8:'status',12:'status',14:'name',15:'Shopping cart',19:'name',20:'name',22:'lastName',24:'time_max',27:'participants_min',28:'unknown',31:'links',32:'users',35:'photoUrls',36:'shipDate',37:'registrationToken',38:'min_activities_count',42:'username',45:'_links',46:'body',47:'key',48:'email_address',50:'Authorization'}
SCENARIOS = {
1:'unknown JSON properties produce 400, which is absent from documented statuses',
2:'_links empty array in registration JSON produces parse-error 500',
3:'missing query name is accepted when clearing the cart',
4:'attrs exceeds maxLength=1 and is accepted',
5:'empty category JSON crashes; assess missing persistent key as well',
6:'absent optional name on form update produces 400',
7:'group exceeds maxLength=1 and is accepted',
8:'pet update JSON omits status and is accepted',
9:'update nonexistent system message with empty JSON produces 500',
10:'GET media file exists in implementation but method is absent from specification',
11:'PUT cart method absent from specification and _links array produces 500',
12:'POST pet form response omits schema-required status',
13:'empty category JSON crashes; assess missing persistent key as well',
14:'pet category name Dogs exceeds request maxLength=1 and is accepted',
15:'contacts HAL response includes Shopping cart relation forbidden by closed schema',
16:'GET file method absent from specification; nonexistent media id produces 500',
17:'GET ping returns 204 but operation is absent from specification',
18:'missing credit-card number produces undocumented validation 406',
19:'missing query name is accepted for listing orders',
20:'query name longer than one character accepted when clearing cart',
21:'out-of-range order id produces undocumented conversion-error 500',
22:'empty user create response omits schema-required lastName',
23:'GET inventory returns 200 but operation absent from specification',
24:'empty activity create response revision omits schema-required time_max',
25:'update nonexistent media file id with empty JSON produces 500',
26:'form-encoded user update produces 500',
27:'empty activity create response properties omit required participants_min',
28:'open tag request schema accepts unknown properties but JSON binding rejects them',
29:'POST tan operation absent from specification and unknown registration token returns 400',
30:'GET cart returns 200 but operation absent from specification',
31:'products response includes links property forbidden by closed schema',
32:'empty user array accepted by schema but rejected with 400',
33:'POST uploadImage absent from specification and missing pet returns 404',
34:'form-encoded order cannot be checked by checker; observed 500 is separate component',
35:'findByStatus response includes a persisted pet without required photoUrls',
36:'order response omits required shipDate when request omits it',
37:'unknown registration token is schema-valid but returns 400',
38:'missing required min_activities_count query parameter accepted',
39:'GET findByTags returns 200 but operation absent from specification',
40:'out-of-range order id produces conversion-error 500',
41:'nonexistent username GET produces 500',
42:'login omits required username and returns 200',
43:'PUT delivery returns 200 but operation absent from specification',
44:'empty registration JSON yields undocumented validation 406',
45:'products response uses links and omits schema-required _links',
46:'unknown TAN verify returns 404 without schema-documented object body',
47:'empty registration request is schema-valid but rejected with 400',
48:'created user lacking email returns response without schema-required email_address',
49:'contacts _links empty array produces parse-error 500',
50:'checker cannot validate object-valued Authorization header serialization',
}
DETERMINISTIC = {2,5,9,13,21,25,26,34,40,41,49,50}

def run_search(a,b):
    items=list(csv.DictReader((ROOT/'items.csv').open()))
    out=ROOT/'search_F2'; out.mkdir(exist_ok=True)
    for item in items[a-1:b]:
        iid=item['item_id']; number=int(iid[1:]); field=FIELDS.get(number)
        target={'side':'request' if item['kind'] in {'INVALID_ACCEPTED','VALID_REJECTED','REQUEST_UNCHECKABLE'} else 'response',
                'method':item['method'],'path_template':item['template'],'scenario':SCENARIOS[number],
                'observed_status':int(item['status']),'field':field,
                'direction':'Determine whether the observed behavior or the specification obligation is intended; assess only the stated item component.'}
        review={'item_id':iid,'start_time':stamp(),'target_proposition':target,
                'mandatory_search':{'required':number not in DETERMINISTIC,
                'reason':'Codebook 11.4.1: intent-dependent attribution, undecidable candidate, or missing-operation intent.' if number not in DETERMINISTIC else 'Deterministic non-gateway 500 or checker-coverage rule; search performed voluntarily to check additional spec component.'},
                'history_scope':'unavailable','hits':[],'manual_additions':[],'decision':None,'end_time':None}
        (ROOT/'review_F2'/f'{iid}.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
        cmd=['/usr/bin/python3','-I','-B',str(ROOT/'../../tools/intent_evidence.py'),str(ROOT/item['package']/'source'),str(ROOT/item['package']/'spec.json'),'--method',item['method'],'--path',item['template'],'--status',item['status']]
        if field:cmd+=['--field',field]
        cmd+=['--json']
        begin=stamp()
        p=subprocess.run(cmd,capture_output=True,timeout=35)
        (out/f'{iid}.json').write_bytes(p.stdout)
        (out/f'{iid}.stderr').write_bytes(p.stderr)
        (out/f'{iid}.exitcode').write_text(str(p.returncode)+'\n')
        review['search_run']={'command':cmd,'start_time':begin,'end_time':stamp(),'exit_code':p.returncode}
        (ROOT/'review_F2'/f'{iid}.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
        try:
            data=json.loads(p.stdout)
            print(iid,p.returncode,data['independent_evidence'],len(data['hits']),data['scan']['complete'],flush=True)
        except json.JSONDecodeError:
            print(iid,p.returncode,'no JSON; manual coverage required',flush=True)

if __name__=='__main__':
    if sys.argv[1]=='show':show(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]))
    elif sys.argv[1]=='search':run_search(int(sys.argv[2]),int(sys.argv[3]))
    elif sys.argv[1]=='hits':
        for name in sys.argv[2:]:
            d=json.loads((ROOT/'search_F2'/f'{name}.json').read_text())
            print(name,d['independent_evidence'],d['warnings'])
            for i,h in enumerate(d['hits']):
                print(i,json.dumps({k:v for k,v in h.items() if k not in {'snippet'}},ensure_ascii=True))
    elif sys.argv[1]=='scan':
        pattern=re.compile(sys.argv[2],re.I)
        for relative in sys.argv[3:]:
            base=ROOT/relative
            for p in sorted(base.rglob('*') if base.is_dir() else [base]):
                if not p.is_file() or p.is_symlink() or p.stat().st_size>2000000:continue
                try: lines=list(p.open())
                except (UnicodeError,OSError):continue
                for n,line in enumerate(lines,1):
                    if pattern.search(line): print(str(p.relative_to(ROOT))+':'+str(n)+': '+redact(line.rstrip())[:600])
    elif sys.argv[1]=='inventory':
        unique={}
        for name in sys.argv[2:]:
            try:d=json.loads((ROOT/'search_F2'/f'{name}.json').read_text())
            except json.JSONDecodeError:continue
            print(name,d['independent_evidence'],len(d['hits']))
            for i,h in enumerate(d['hits']):
                key=(h['category'],h['file'],h['line'])
                unique.setdefault(key,[]).append((name,i,h))
        for key,entries in unique.items():
            h=entries[0][2]
            print(' '.join(n+':'+str(i) for n,i,_ in entries),key,'values='+str(h.get('asserted_values',h.get('statuses',[]))), 'field='+str(h.get('field')), 'behavior='+str(h.get('field_behavior')))
            print(redact(h.get('snippet',''))[:450].replace('\n',' | '))
