import sys, pathlib, re, json

def safe(line):
    if re.search(r'[A-Za-z0-9_+/=-]{60,}', line):
        return '[REDACTED long encoded/credential-looking value]'
    if re.search(r'TODO\s*:\s*\w+', line, re.I):
        return '[REDACTED possible personal attribution]'
    if re.search(r'@author|copyright|mailto:|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', line, re.I):
        return '[REDACTED attribution/contact]'
    if re.search(r'(password|secret|token|api[_-]?key|credential)\s*[=:]\s*[\"\x27][^\"\x27]{8,}[\"\x27]', line, re.I):
        return '[REDACTED credential-looking line]'
    return line

for q in json.load(sys.stdin):
    base=pathlib.Path(q['path'])
    assert re.match(r'^X\d{2}/(impl|contract)(/|$)',str(base))
    files=[base] if base.is_file() else sorted(p for p in base.rglob('*') if p.is_file())
    for p in files:
        if q.get('file') and q['file'] not in str(p): continue
        lines=p.read_text().splitlines()
        if 'range' in q:
            a,b=q['range']; hits=set(range(a-1,min(b,len(lines))))
        else:
            pat=re.compile(q['pattern'],re.I if q.get('ignorecase') else 0)
            centers=[i for i,s in enumerate(lines) if pat.search(s)]
            if q.get('limit'): centers=centers[:q['limit']]
            c=q.get('context',3)
            hits={j for i in centers for j in range(max(0,i-c),min(len(lines),i+c+1))}
        if hits:
            print('\n'+str(p))
            last=-2
            for i in sorted(hits):
                if i>last+1: print('...')
                print(f'{i+1}: {safe(lines[i])}')
                last=i
