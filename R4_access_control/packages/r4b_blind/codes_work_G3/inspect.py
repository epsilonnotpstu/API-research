from pathlib import Path
import sys
for n in sys.argv[1:]:
 d=Path('C'+n.zfill(3)); s=(d/'item.md').read_text()
 print('\n===',d,'===\n',s if len(s)<7000 else s[:6000]+'\n[LONG ADVISORY: remainder available]\n'+s[s.find('## Touched'):])
 s=(d/'diff.patch').read_text()
 if len(s)>7000:
  s='\n'.join(l for l in s.splitlines() if l.startswith(('diff ','@@','+')))
  if len(s)>7000:s=s[:7000]+'\n[LONG DIFF: remainder available]'
 print('--- DIFF ---\n',s)
