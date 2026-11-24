from pathlib import Path
import sys,json,re
for arg in sys.argv[1:]:
 n,_,term=arg.partition(':'); n,_,fn=n.partition('@'); d=Path('C'+n.zfill(3))/'contract'
 print('\n===',d,'filter',term,'===')
 files=[f for f in sorted(d.iterdir()) if not fn or fn in f.name]
 # Prefer JSON equivalents to avoid duplicate large results.
 if any(f.suffix=='.json' and f.stat().st_size>1000 for f in files) and n not in ('8','38'): files=[f for f in files if f.suffix not in ('.yml','.yaml')]
 for f in files:
  if f.suffix not in ('.json','.yaml','.yml'):continue
  s=f.read_text(); lines=s.splitlines()
  if f.suffix=='.json':
   try: doc=json.loads(s)
   except Exception as e: print(f.name,'PARSE ERROR',str(e)[:120]);continue
   if not isinstance(doc,dict) or not ('swagger' in doc or 'openapi' in doc):continue
   paths=doc.get('paths',{}) or {}
   if not paths: continue
   for path,entry in paths.items():
    if term and not re.search(term,path,re.I):continue
    loc=next((i for i,l in enumerate(lines,1) if re.match(r'\s*'+re.escape(json.dumps(path))+r'\s*:',l)), '?')
    if not isinstance(entry,dict):continue
    print(f.name+':'+str(loc),path,'BASE',doc.get('basePath',doc.get('servers','')))
    defs=doc.get('securityDefinitions',doc.get('components',{}).get('securitySchemes',{}))
    for m,op in entry.items():
     if m not in {'get','put','post','delete','patch','head','options','trace'} or not isinstance(op,dict):continue
     sec=op.get('security',doc.get('security','NONE'))
     print(m.upper(),'SEC',sec,'DEFINED',list(defs),'INFO',op.get('summary',''),op.get('description',''))
     if False:print('DETAIL',json.dumps(op,ensure_ascii=False)[:7000])
  else:
   found=False
   for i,l in enumerate(lines):
    mt=re.match(r'^(\s*)[\"\']?(/.*?)[\"\']?:\s*$',l)
    if not mt:continue
    found=True;path=mt[2]
    if term and not re.search(term,path,re.I):continue
    end=i+1
    while end<len(lines) and (not lines[end].strip() or len(lines[end])-len(lines[end].lstrip())>len(mt[1])):end+=1
    print(f.name+':'+str(i+1),path)
    if False:
     print('\n'.join(str(j+1)+':'+lines[j] for j in range(i,min(end,i+210))))
    else:print('\n'.join(str(j+1)+':'+lines[j] for j in range(i+1,end) if re.match(r'^\s+(get|put|post|delete|patch|security|summary|description):',lines[j])))
   if not found:print(f.name,'NO PATHS')
