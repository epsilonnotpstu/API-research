import argparse
import re
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('paths', nargs='+')
p.add_argument('--pattern')
p.add_argument('--before', type=int, default=8)
p.add_argument('--after', type=int, default=30)
p.add_argument('--start', type=int, default=1)
p.add_argument('--end', type=int, default=1000000)
a = p.parse_args()
for name in a.paths:
    path = Path(name)
    assert re.match(r'^W\d\d/(contract|impl)/', name), name
    lines = path.read_text().splitlines()
    selected = set()
    if a.pattern:
        for i, line in enumerate(lines):
            if re.search(a.pattern, line):
                selected.update(range(max(a.start-1, i-a.before), min(len(lines), a.end, i+a.after+1)))
    else:
        selected.update(range(a.start-1, min(len(lines), a.end)))
    print('\nFILE', name)
    prev = -2
    for i in sorted(selected):
        if i != prev+1:
            print('...')
        line = lines[i]
        if (re.search(r'(?i)(@author|copyright|created by|maintainer|contributors?|mailto:|[\w.+-]+@[\w.-]+\.[a-z]{2,})', line)
            or re.search(r'(?i)(password|secret|api[_-]?key|access[_-]?token|private[_-]?key)\s*[=:]\s*[\x22\x27][^\x22\x27]+', line)
            or re.search(r'-----BEGIN .*PRIVATE KEY', line)):
            line = '[REDACTED attribution or credential-looking line]'
        print(f'{i+1}: {line}')
        prev = i
