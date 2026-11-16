import argparse
import re
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('paths', nargs='+')
p.add_argument('--pattern', default='')
p.add_argument('--context', type=int, default=4)
p.add_argument('--lines', default='')
a = p.parse_args()
for target in a.paths:
    root = Path(target)
    assert re.match(r'^W\d\d/(contract|impl)(/|$)', target)
    files = [root] if root.is_file() else sorted(f for f in root.rglob('*') if f.is_file())
    for f in files:
        lines = f.read_text().splitlines()
        selected = set()
        if a.lines:
            lo, hi = map(int, a.lines.split(':'))
            selected.update(range(max(0, lo-1), min(len(lines), hi)))
        else:
            for i, line in enumerate(lines):
                if re.search(a.pattern, line, re.I):
                    selected.update(range(max(0, i-a.context), min(len(lines), i+a.context+1)))
        if not selected:
            continue
        print('\nFILE', f)
        last = -2
        for i in sorted(selected):
            if i != last+1:
                print('...')
            line = lines[i]
            if re.search(r'@author|copyright|mailto:|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|password|secret|credential|api[_-]?key|private[_ -]?key|access[_-]?token|bearer\s+[A-Za-z0-9]', line, re.I):
                line = '[REDACTED sensitive or personal attribution line]'
            print(f'{i+1}: {line}')
            last = i
