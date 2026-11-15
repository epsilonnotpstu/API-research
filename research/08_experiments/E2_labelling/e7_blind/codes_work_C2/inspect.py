import sys
import re
from pathlib import Path

def safe(line):
    if re.search(r'@author|copyright|SPDX-FileCopyrightText|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', line, re.I):
        return '[personal attribution redacted]'
    if re.search(r'(?:password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\"\'][^\"\']+[\"\']|-----BEGIN .*PRIVATE KEY|(?:AKIA|ASIA)[A-Z0-9]{16}', line, re.I):
        return '[credential-looking line redacted]'
    return line

for spec in sys.argv[1:]:
    root, name, rest = spec.split('|', 2)
    pattern, context = rest.rsplit('|', 1)
    assert re.fullmatch(r'X\d{2}/(?:impl|contract)', root)
    context = int(context)
    for path in sorted(Path(root).rglob(name)):
        if not path.is_file():
            continue
        lines = path.read_text().splitlines()
        hits = [i for i, line in enumerate(lines) if re.search(pattern, line)]
        if not hits:
            continue
        print(str(path))
        selected = set()
        for i in hits:
            selected.update(range(max(0, i-context), min(len(lines), i+context+1)))
        last = -2
        for i in sorted(selected):
            if i != last+1:
                print('...')
            print(f'{i+1}: {safe(lines[i])}')
            last = i
