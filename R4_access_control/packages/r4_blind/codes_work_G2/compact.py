from pathlib import Path
import sys
for n in range(int(sys.argv[1]),int(sys.argv[2])+1):
 d=Path(f'A{n:03}'); print('\n===',d,'===')
 s=(d/'item.md').read_text(); print(s[:1900])
 ls=(d/'diff.patch').read_text().splitlines(); out=[]; skip=False
 for i,l in enumerate(ls,1):
  if l.startswith('diff --git'): skip=any(x in l for x in ['.gen.go','generated/'])
  if not skip and (l.startswith(('+','-','@@','diff --git')) and not l.startswith(('+++','---'))):out.append(f'{i}: {l}')
 print('\n'.join(out[:40]));
 if len(out)>40:print('MORE CHANGES:',len(out)-40)
 print('CONTRACT FILES:', ', '.join(str(p) for p in (d/'contract').rglob('*') if p.is_file() and p.name!='INDEX.md'))
