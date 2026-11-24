import sys, pathlib, re, json

root = pathlib.Path(__file__).resolve().parent.parent
mode, item, *args = sys.argv[1:]
base = root / item
if mode == 'brief':
    source=(base / 'item.md').read_text()
    print(source.split('## Touched source files')[0][:2000])
    changes=(base / 'diff.patch').read_text().splitlines()
    kept=[l for l in changes if l.startswith(('diff --git','@@','+','-')) and not l.startswith(('+++','---')) and not re.match(r'^[+-]\s*(//|\*|import |$)',l)]
    for l in kept[:65]: print(l)
    if len(kept)>65: print(f'[{len(kept)-65} further changed lines]')
    files=sorted(p.name for p in (base / 'contract').iterdir() if p.name!='INDEX.md')
    print('CONTRACT FILES',len(files),', '.join(files[:5]))
elif mode == 'item':
    print((base / 'item.md').read_text())
    print((base / 'diff.patch').read_text())
    print((base / 'contract/INDEX.md').read_text())
elif mode == 'find':
    pat = re.compile(args[0], re.I)
    context = int(args[1]) if len(args) > 1 else 0
    for p in sorted((base / 'contract').iterdir()):
        if p.name == 'INDEX.md': continue
        lines = p.read_text().splitlines()
        selected = set()
        for i,l in enumerate(lines):
            if pat.search(l): selected.update(range(max(0,i-context), min(len(lines),i+context+1)))
        for i in sorted(selected): print(f'{item}/contract/{p.name}:{i+1}: {lines[i]}')
elif mode == 'json':
    pat = re.compile(args[0], re.I)
    for p in sorted((base / 'contract').iterdir()):
        if p.suffix != '.json': continue
        try: doc=json.loads(p.read_text())
        except (ValueError, UnicodeError): continue
        if not isinstance(doc,dict) or not ('swagger' in doc or 'openapi' in doc): continue
        if not any(pat.search(path) for path in doc.get('paths',{})): continue
        print(f'FILE {item}/contract/{p.name} base={doc.get("basePath",doc.get("servers"))} globalSecurity={doc.get("security")} schemes={list((doc.get("securityDefinitions",doc.get("components",{}).get("securitySchemes")) or {}).keys())}')
        lines=p.read_text().splitlines()
        for path,methods in doc.get('paths',{}).items():
            if not pat.search(path): continue
            loc=next((i+1 for i,l in enumerate(lines) if json.dumps(path) + ':' in l),'?')
            print(f'PATH {loc}: {path}')
            for method,op in methods.items():
                if method not in ['get','post','put','patch','delete','head','options']: continue
                print(method.upper(),json.dumps({k:v for k,v in op.items() if k in ['summary','description','security','operationId']}))
elif mode == 'paths':
    pat=re.compile(args[0],re.I)
    for p in sorted((base/'contract').iterdir()):
        if p.suffix not in ['.yaml','.yml']: continue
        lines=p.read_text().splitlines()
        hits=[i for i,l in enumerate(lines) if re.match(r'^\s*[?]?\s*[\"\']?/',l) and pat.search(l)]
        for i in hits:
            print(f'{item}/contract/{p.name}:{i+1}: {lines[i]}')
            indent=len(lines[i])-len(lines[i].lstrip())
            for j in range(i+1,min(len(lines),i+350)):
                l=lines[j]
                if l.strip() and len(l)-len(l.lstrip())<=indent: break
                if re.search(r'\b(get|post|put|patch|delete|security|summary|description):|^\s*- (\w.*Auth|[Bb]earer|[Oo][Aa]uth|jwt|admin|Read|Write|Delete)',l):
                    print(f'{j+1}: {l}')
elif mode == 'slice':
    p=base / args[0]
    start,end=map(int,args[1:3])
    for i,l in enumerate(p.read_text().splitlines(),1):
        if start<=i<=end: print(f'{item}/{args[0]}:{i}: {l}')
