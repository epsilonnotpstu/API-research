from pathlib import Path
import re,sys
item,side,name,start,end=sys.argv[1:]
assert re.fullmatch(r'W\d{2}',item) and side in ('contract','impl')
private=re.compile(r'@author|copyright|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|-----BEGIN .*PRIVATE|(?:password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\x22\x27][^\x22\x27]+',re.I)
for p in sorted((Path(item)/side).rglob(name)):
 if not p.is_file(): continue
 print('\nFILE',p)
 for i,s in enumerate(p.read_text(errors='replace').splitlines(),1):
  if int(start)<=i<=int(end): print(f'{i}: '+('[REDACTED]' if private.search(s) else s))
