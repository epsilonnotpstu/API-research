from pathlib import Path
import re,sys
for n in range(int(sys.argv[1]),int(sys.argv[2])+1):
 d=Path(f'A{n:03}');print('\n===',d,'===')
 for p in sorted((d/'contract').iterdir()):
  if p.name=='INDEX.md':continue
  ls=p.read_text().splitlines(); paths=[]; sec=[]
  for i,l in enumerate(ls,1):
   if re.match(r'^\s{0,8}[\"\']?/[a-zA-Z{]',l):paths.append(f'{i}:{l.strip()}')
   if re.search(r'\b(security|securityDefinitions|securitySchemes)\b',l):sec.append(f'{i}:{l.strip()}')
  print(p.name,'lines',len(ls),'PATHS', ' | '.join(paths)[:3500], 'SEC', ' | '.join(sec)[:600])
