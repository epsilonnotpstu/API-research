import argparse,pathlib,re
p=argparse.ArgumentParser();p.add_argument('path');p.add_argument('pattern');p.add_argument('-c',type=int,default=5);p.add_argument('--file',default='');p.add_argument('--lines',default='');a=p.parse_args()
root=pathlib.Path(a.path)
assert re.match(r'^U\d{2}/(impl|contract)(/|$)',str(root))
files=[root] if root.is_file() else sorted(root.rglob('*'))
for f in files:
 if not f.is_file() or (a.file and a.file not in str(f)):continue
 lines=f.read_text(errors='replace').splitlines(); selected=set()
 if a.lines:
  for span in a.lines.split(','):
   lo,hi=map(int,span.split('-'));selected.update(range(lo-1,min(hi,len(lines))))
 for i,s in enumerate(lines):
  if re.search(a.pattern,s,re.I):selected.update(range(max(0,i-a.c),min(len(lines),i+a.c+1)))
 if not selected:continue
 print('\nFILE',f)
 last=-2
 for i in sorted(selected):
  if i!=last+1:print('...')
  s=lines[i]
  if re.search(r'copyright|@author|\bAuthor:|[\w.+-]+@[\w.-]+\.[a-z]{2,}|\b(?:password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\"\x27][^\"\x27]+',s,re.I):s='[REDACTED attribution or credential-looking line]'
  print(f'{i+1}: {s}');last=i
