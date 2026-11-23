from pathlib import Path
import re,sys
for spec in sys.argv[1:]:
 ident,pattern=spec.split(':',1);d=Path(ident);print('\n===',ident,pattern,'===')
 for p in sorted((d/'contract').iterdir()):
  if p.name=='INDEX.md': continue
  ls=p.read_text().splitlines(); matches=[]
  for i,l in enumerate(ls,1):
   if re.match(r'^\s{0,8}[\"\']?/',l) and re.search(pattern,l,re.I):matches.append((i,l.strip()))
  sec=[(i,l.strip()) for i,l in enumerate(ls,1) if re.search(r'^[ ]{0,4}[\"]?(security|securityDefinitions|securitySchemes)[\"]?\s*:',l)]
  print(p.name,len(ls),'matches',matches[:18], 'SEC', sec[:8])
