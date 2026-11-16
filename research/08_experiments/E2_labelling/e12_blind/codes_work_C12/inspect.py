import re
import sys
from pathlib import Path

line_range = re.fullmatch(r'@([0-9]+):([0-9]+)', sys.argv[1])
pattern = re.compile(sys.argv[1], re.I)
context = int(sys.argv[2])
for arg in sys.argv[3:]:
    root = Path(arg)
    if not re.match(r'^U\d{2}/(impl|contract)(/|$)', str(root)):
        raise SystemExit('Explicit item source path required')
    paths = [root] if root.is_file() else sorted(p for p in root.rglob('*') if p.is_file())
    for path in paths:
        lines = path.read_text().splitlines()
        indexes = set(range(int(line_range[1])-1, min(len(lines), int(line_range[2])))) if line_range else set()
        for i, line in enumerate(lines):
            if pattern.search(line):
                indexes.update(range(max(0, i-context), min(len(lines), i+context+1)))
        if not indexes:
            continue
        print('\nFILE', path)
        previous = -2
        for i in sorted(indexes):
            if i != previous + 1:
                print('...')
            line = lines[i]
            if re.search(r'@author|copyright|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?:password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\x22\x27][^\x22\x27]+', line, re.I):
                line = '[REDACTED: credential-looking content or personal attribution]'
            print(f'{i+1}: {line}')
            previous = i
