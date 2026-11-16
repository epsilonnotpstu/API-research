from pathlib import Path
import re,sys
item,pattern=sys.argv[1:3]
context=int(sys.argv[3]) if len(sys.argv)>3 else 3
assert re.fullmatch(r'W\d{2}',item)
rx=re.compile(pattern,re.I)
private=re.compile(r'@author|copyright|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|-----BEGIN .*PRIVATE|(?:password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\x22\x27][^\x22\x27]+',re.I)
for side in ['contract','impl']:
 for p in sorted((Path(item)/side).rglob('*')):
  if not p.is_file(): continue
  lines=p.read_text(errors='replace').splitlines()
  hits=[i for i,s in enumerate(lines) if rx.search(s)]
  visible=set()
  for i in hits: visible.update(range(max(0,i-context),min(len(lines),i+context+1)))
  if visible:
   print('\nFILE',p)
   for i in sorted(visible): print(f'{i+1}: '+('[REDACTED]' if private.search(lines[i]) else lines[i]))
