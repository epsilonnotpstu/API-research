import argparse,pathlib,re
p=argparse.ArgumentParser(); p.add_argument('paths',nargs='+'); p.add_argument('-p',default=''); p.add_argument('-c',type=int,default=3); p.add_argument('-f',default=''); p.add_argument('-r',default=''); a=p.parse_args()
for base in a.paths:
 assert re.match(r'^X\d+/(contract|impl)(/|$)',base)
 paths=[pathlib.Path(base)] if pathlib.Path(base).is_file() else sorted(pathlib.Path(base).rglob('*'))
 for path in paths:
  if not path.is_file() or a.f and not re.search(a.f,str(path)): continue
  lines=path.read_text(errors='replace').splitlines(); selected=set()
  if a.r:
   for span in a.r.split(','):
    z=span.split(':'); lo=int(z[0]); hi=int(z[-1]); selected.update(range(lo-1,min(hi,len(lines))))
  else:
   for i,l in enumerate(lines):
    if re.search(a.p,l,re.I): selected.update(range(max(0,i-a.c),min(len(lines),i+a.c+1)))
  if selected:
   print('\n'+str(path))
   for i in sorted(selected):
    l=lines[i]
    if re.search(r'@author|copyright|maintainer|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?:password|secret|api[_-]?key|access[_-]?token)\s*[=:]\s*[\"\x27][^\"\x27]+',l,re.I): l='[REDACTED]'
    print(f'{i+1}: {l}')
