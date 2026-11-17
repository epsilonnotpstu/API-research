import sys, pathlib, re
span=re.fullmatch(r'@(\d+):(\d+)',sys.argv[1])
pattern=re.compile(sys.argv[1],re.I) if not span else None
context=int(sys.argv[2])
for arg in sys.argv[3:]:
 p=pathlib.Path(arg)
 assert re.match(r'^Q\d\d/(contract|impl)(/|$)',arg),arg
 files=sorted(p.rglob('*')) if p.is_dir() else [p]
 for f in files:
  if not f.is_file(): continue
  lines=f.read_text().splitlines()
  hits=list(range(int(span[1])-1,min(len(lines),int(span[2])))) if span else [i for i,s in enumerate(lines) if pattern.search(s)]
  keep=set(j for i in hits for j in range(max(0,i-context),min(len(lines),i+context+1)))
  if not keep: continue
  print('\n'+str(f))
  prev=-2
  for i in sorted(keep):
   if i>prev+1: print('...')
   s=lines[i]
   if re.search(r'[a-f0-9]{24,}|authorization:\s*\S+|authelia_session=|[?&]code=|^\s*(?:key|token|secret|code):\s*\S|[A-Za-z0-9_-]{48,}|@author|copyright|[\w.+-]+@[\w.-]+\.[a-z]{2,}|(?:password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\"\x27][^\"\x27]+',s,re.I): s='[REDACTED attribution or credential-looking line]'
   print(f'{i+1}: {s}')
   prev=i
