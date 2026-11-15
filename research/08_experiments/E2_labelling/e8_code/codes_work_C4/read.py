import pathlib, re, sys

pattern = re.compile(sys.argv[1], re.I)
context = int(sys.argv[2])
for arg in sys.argv[3:]:
    root = pathlib.Path(arg)
    assert re.match(r'^X\d+/(impl|contract)(/|$)', arg)
    files = [root] if root.is_file() else sorted(root.rglob('*'))
    for path in files:
        if not path.is_file():
            continue
        lines = path.read_text(errors='replace').splitlines()
        if sys.argv[1].startswith('@L'):
            start, end = map(int, sys.argv[1][2:].split('-'))
            hits = list(range(start-1, min(end, len(lines))))
        else:
            hits = [i for i, line in enumerate(lines) if pattern.search(line)]
        if not hits:
            continue
        indices = set()
        for i in hits:
            indices.update(range(max(0, i-context), min(len(lines), i+context+1)))
        print('\n' + str(path))
        last = -2
        for i in sorted(indices):
            if i != last + 1:
                print('...')
            line = lines[i]
            if re.search(r'@author|copyright|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?:password|api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*[\"\x27][^\"\x27]+', line, re.I):
                line = '[REDACTED attribution/credential-looking line]'
            print(f'{i+1}: {line}')
            last = i
