import sys, pathlib, re
root=pathlib.Path(sys.argv[1])
assert re.fullmatch(r'W\d+/(contract|impl)', str(root))
pat=re.compile(sys.argv[2],re.I)
context=int(sys.argv[3]) if len(sys.argv)>3 else 5
for p in sorted(root.rglob('*')):
    if not p.is_file(): continue
    if len(sys.argv)>4 and sys.argv[4] not in str(p): continue
    lines=p.read_text().splitlines()
    hits=[i for i,s in enumerate(lines) if pat.search(s)]
    indexes=sorted({j for i in hits for j in range(max(0,i-context),min(len(lines),i+context+1))})
    if not indexes: continue
    print('\nFILE',p)
    prev=-2
    for j in indexes:
        if j>prev+1: print('...')
        s=lines[j]
        if re.search(r'@author|copyright|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?:password|secret|api[_-]?key|credential)\s*[:=]\s*[\x22\x27]?[^\s,;]+',s,re.I): s='[REDACTED attribution/credential-looking line]'
        print(f'{j+1}: {s}')
        prev=j
