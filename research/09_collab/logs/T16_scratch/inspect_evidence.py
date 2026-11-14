"""Summarize saved failures without revealing request or credential values."""
import collections
import csv
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay import OUT, ROOT, RUNS

def char_flags(value):
    return {'length':len(value),'control':bool(re.search(r'[\x00-\x1f\x7f]',value)),
            'non_ascii':not value.isascii(), 'percent_control':bool(re.search(r'%(?:0[0-9a-f]|1[0-9a-f]|7f)',value,re.I))}

def main():
    for sut,run_rel in RUNS.items():
        run=ROOT/run_rel; xs=[json.loads(s) for s in (run/'exchanges.jsonl').open()]
        lines=(run/'compose.log').read_bytes().decode('utf-8').split('\n')
        items=list(csv.DictReader((ROOT/f'08_experiments/E2_labelling/{sut}_baseline_s1_blind.csv').open()))
        maps={i['item_id']:i for i in json.loads((OUT/f'{sut}_exchange_map.json').read_text())}
        if sut=='swagger-petstore':
            # Only exception class names and source frames, never messages/values.
            exceptions=[]
            for n,line in enumerate(lines,1):
                m=re.search(r'(?:(?:Caused by:|Causing:)\s*)?((?:[A-Za-z_$][\w$]*\.)+[\w$]*(?:Exception|Error))\b',line)
                if m and ' at ' not in line:
                    frames=[]
                    for j in range(n,min(n+100,len(lines))):
                        f=re.search(r'at ((?:io\.swagger\.|org\.glassfish\.|com\.fasterxml\.)[\w.$]+)\(([^()]*)\)',lines[j])
                        if f:frames.append({'line':j+1,'symbol':f[1],'source':f[2]})
                        if j>n and re.search(r'\| (?:WARN|ERROR|INFO)\s',lines[j]):break
                    exceptions.append({'line':n,'class':m[1],'frames':frames[:8]})
            (OUT/f'{sut}_log_exceptions.json').write_text(json.dumps(exceptions,indent=2)+'\n')
            grouped=collections.defaultdict(list)
            for error in exceptions:
                key=(error['class'],tuple((f['symbol'],f['source']) for f in error['frames'][:2]))
                grouped[key].append(error['line'])
            print('PET LOG GROUPS')
            for key,ns in grouped.items():print(len(ns),ns[:3],key)
        else:
            exceptions=[]
            for n,line in enumerate(lines,1):
                match=re.search(r'((?:org\.|java\.|com\.|market\.)[\w.$]*(?:Exception|Error))\b',line)
                if match and ' at ' not in line:
                    frames=[]
                    for j in range(n,min(n+100,len(lines))):
                        f=re.search(r'at (market\.[\w.$]+)\(([^()]*)\)',lines[j])
                        if f:frames.append({'line':j+1,'symbol':f[1],'source':f[2]})
                        if j>n and re.match(r'^sut-.*\| \d{4}-\d\d-\d\dT',lines[j]):break
                    exceptions.append({'line':n,'class':match[1],'frames':frames})
            (OUT/f'{sut}_log_exceptions.json').write_text(json.dumps(exceptions,indent=2)+'\n')
            grouped=collections.defaultdict(list)
            for error in exceptions:grouped[(error['class'],tuple((f['symbol'],f['source']) for f in error['frames'][:2]))].append(error['line'])
            print('MARKET LOG GROUPS')
            for key,ns in grouped.items():print(len(ns),ns[:3],key)
        print('VALID_REJECTED/500 REQUEST SHAPES',sut)
        records=[]
        for item in items:
            if item['kind'] not in ('VALID_REJECTED','SERVER_ERROR','RESPONSE_SCHEMA','RESPONSE_PARSE') and not(item['status']=='406'):continue
            groups=collections.defaultdict(list)
            for n in maps[item['item_id']]['exchange_lines']:
                x=xs[n-1]; req=x['request'];resp=x['response'];text=resp['body']['text']
                try:value=json.loads(text)
                except ValueError:value=None
                message=value.get('message','') if isinstance(value,dict) else text
                # Record diagnostic categories, not error contents or credentials.
                name=next((k for k in ['No Name provided','No User provided','No Order provided','No status provided','No tags provided','No file uploaded','No User provided'] if k in message),None)
                reason=re.search(r'(?:reason:|<title>)([^<\n]+)',message)
                if reason:
                    reason=reason[1]
                    name=next((k for k in ['Bad URI','Bad Message','Bad Request','Illegal character','Bad query','Bad path','Bad header'] if k.lower() in reason.lower()),'HTTP parser rejection')
                exceptions=re.findall(r'(?:[A-Za-z_$][\w$]*\.)+[\w$]*(?:Exception|Error)',message)
                if exceptions:name=';'.join(sorted(set(exceptions)))
                if not name:name='JSON generic error' if isinstance(value,dict) else 'non-JSON response'
                groups[name].append(n)
            print(item['item_id'],[(k,len(v),v[:4]) for k,v in groups.items()])
            records.append({'item_id':item['item_id'],'groups':[{'category':k,'count':len(v),'exchange_lines':v} for k,v in groups.items()]})
        (OUT/f'{sut}_response_groups.json').write_text(json.dumps(records,indent=2)+'\n')

if __name__=='__main__':main()
