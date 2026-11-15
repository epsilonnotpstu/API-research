#!/usr/bin/python3
"""Second inventory pass: parse root JSON keys and record historical Java surfaces."""
import json
from pathlib import Path
import re
import runpy
m=runpy.run_path(str(Path(__file__).with_name('mine.py')))
ROOT=m['ROOT'];git=m['git'];blob=m['blob']
inventory=json.loads((ROOT/'inventory.json').read_text())
pool=json.loads((ROOT/'candidate_pool.json').read_text())
result=[]
for r in inventory:
    paths=git(r['repo'],'ls-tree','-r','--name-only',r['head']).decode().splitlines()
    specs=[]
    for path in paths:
        if not path.endswith(('.json','.yaml','.yml')):continue
        content=blob(r['repo'],r['head'],path)
        root_key=None;line=None
        if path.endswith('.json'):
            try:
                value=json.loads(content)
                if isinstance(value,dict):root_key=next((k for k in ('openapi','swagger') if k in value),None)
                if root_key:line=next(i for i,l in enumerate(content.splitlines(),1) if '"'+root_key+'"' in l)
            except (ValueError,StopIteration):pass
        else:
            hit=re.search(r'^(openapi|swagger)\s*:',content,re.M)
            if hit:root_key=hit.group(1);line=content[:hit.start()].count('\n')+1
        if root_key:
            role='service_contract'
            if r['repo']=='microcks' and not path.startswith('api/microcks-openapi-'):role='fixture_or_imported_example'
            specs.append({'path':path,'root_key':root_key,'line':line,'role':role})
    historical=[]
    for row in pool:
        if row['repo']!=r['repo'] or not (ROOT/'review_evidence'/(row['candidate_id']+'.diff')).exists():continue
        for c in row['changes']:
            path=c[-1]
            if path.endswith(('.java','.kt')) and re.search('ontroller|esource|odel|xception|alidat',path):
                historical.append({'candidate_id':row['candidate_id'],'fix_commit':row['fix_commit'],'path':path})
    result.append({'repo':r['repo'],'head':r['head'],'spec_files':specs,'swagger_annotation_files':r['annotation_files'],'behaviour_annotation_files':r['behaviour_files'],'behaviour_path_files':r.get('behaviour_path_files',[]),'python_generated_surfaces':r.get('python_generated_surfaces',[]),'generator_references':r['generator_references'],'reviewed_historical_surfaces':historical,'stars':'unavailable_offline_no_network','popularity_evidence':r['popularity_evidence']})
m['dump']('surface_audit.json',result)
print(json.dumps([{'repo':r['repo'],'specs':len(r['spec_files']),'service_specs':sum(s['role']=='service_contract' for s in r['spec_files']),'annotation_files':len(r['swagger_annotation_files']),'python_generated_files':len(r['python_generated_surfaces'])} for r in result],indent=2))
