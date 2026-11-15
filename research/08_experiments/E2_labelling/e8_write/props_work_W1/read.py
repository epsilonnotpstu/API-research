import pathlib, re, sys, json

def safe(s):
    if re.search(r'@author|copyright|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', s, re.I):
        return '[REDACTED attribution/contact]'
    if re.search(r'(password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\"\'][^\"\']+[\"\']', s, re.I):
        return '[REDACTED credential-looking assignment]'
    return s

mode, path, *args = sys.argv[1:]
p = pathlib.Path(path)
assert re.match(r'^X\d\d/(contract|impl)(/|$)', path), path
if mode == 'list':
    for f in sorted(p.rglob('*')):
        if f.is_file(): print(f)
elif mode == 'read':
    lines = p.read_text().splitlines()
    lo, hi = map(int, args) if args else (1, len(lines))
    print(path)
    for n in range(lo, min(hi,len(lines))+1): print(f'{n}: {safe(lines[n-1])}')
elif mode == 'search':
    regex = re.compile(args[0], re.I)
    context = int(args[1]) if len(args)>1 else 3
    for f in sorted(p.rglob('*')) if p.is_dir() else [p]:
        if not f.is_file(): continue
        lines = f.read_text().splitlines()
        indices = set()
        for i, s in enumerate(lines):
            if regex.search(s): indices.update(range(max(0,i-context),min(len(lines),i+context+1)))
        if indices:
            print(f)
            last=-2
            for i in sorted(indices):
                if i>last+1: print('...')
                print(f'{i+1}: {safe(lines[i])}')
                last=i
elif mode == 'json':
    obj = json.loads(p.read_text())
    for key in args[0].split('|'): obj=obj[key]
    print(path+'#'+args[0])
    for s in json.dumps(obj,indent=2).splitlines(): print(safe(s))
