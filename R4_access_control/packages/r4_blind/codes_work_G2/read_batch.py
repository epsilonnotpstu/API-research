from pathlib import Path
import sys
start,end=map(int,sys.argv[1:3])
for n in range(start,end+1):
 d=Path(f'A{n:03}')
 print('\n===',d,'===')
 print((d/'item.md').read_text())
 lines=(d/'diff.patch').read_text().splitlines()
 filtered=[]; skip=False
 for i,line in enumerate(lines,1):
  if line.startswith('diff --git'):
   skip=any(x in line for x in ['.gen.go','openapi.gen','client.gen','server.gen','generated/','oapi-codegen','client.gen','zz_generated'])
  if not skip: filtered.append(f'{i}: {line}')
 if len(filtered)>220:
  print('\n'.join(filtered[:220]));print('DIFF REMAINDER',len(filtered)-220)
 else: print('\n'.join(filtered))
 print((d/'contract/INDEX.md').read_text())
