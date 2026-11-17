import argparse
import pathlib
import re

p = argparse.ArgumentParser()
p.add_argument('paths', nargs='+')
p.add_argument('--pattern', default=None)
p.add_argument('--context', type=int, default=5)
p.add_argument('--lines', default=None)
a = p.parse_args()
for path in a.paths:
    root = pathlib.Path(path)
    assert re.match(r'^Q[0-9]{2}/(impl|contract)(/|$)', path), path
    files = [root] if root.is_file() else sorted(f for f in root.rglob('*') if f.is_file())
    for f in files:
        lines = f.read_text().splitlines()
        keep = set()
        if a.lines:
            for span in a.lines.split(','):
                bounds = [int(n) for n in span.split('-')]
                keep.update(range(bounds[0]-1, bounds[-1]))
        elif a.pattern:
            for i, line in enumerate(lines):
                if re.search(a.pattern, line, re.I):
                    keep.update(range(max(0, i-a.context), min(len(lines), i+a.context+1)))
        else:
            keep.update(range(len(lines)))
        if not keep:
            continue
        print('\n' + str(f))
        last = -2
        for i in sorted(keep):
            if i >= len(lines):
                continue
            if i != last+1:
                print('...')
            line = lines[i]
            if re.search(r'@author\b|copyright|(?:FIXME|TODO):\s*[A-Z][a-z]+:|[\w.+-]+@[\w.-]+\.[a-z]{2,}|BEGIN .*PRIVATE KEY|authelia_(at|rt)_|[A-Za-z0-9_-]{45,}\.[A-Za-z0-9_.-]{20,}', line, re.I) or re.search(r'(password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[\"\x27][^\"\x27]+[\"\x27]', line, re.I):
                line = '[REDACTED attribution or credential-looking line]'
            print(f'{i+1}: {line[:650]}')
            last = i
