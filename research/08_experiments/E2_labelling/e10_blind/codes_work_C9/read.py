"""Read-only, redacted inspection of explicitly named item paths."""
import argparse
import json
import re
from pathlib import Path


def redact(line):
    if re.search(r'(?i)@author|copyright|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|-----BEGIN .*KEY', line):
        return '[REDACTED attribution/credential-looking line]'
    if re.search(r'(?i)(?:password|secret|api[_-]?key|access[_-]?token)\s*[=:]\s*[\"\x27][^\"\x27]+[\"\x27]', line):
        return '[REDACTED credential-looking line]'
    return line


p = argparse.ArgumentParser()
p.add_argument('paths', nargs='+')
p.add_argument('--match')
p.add_argument('--context', type=int, default=3)
p.add_argument('--lines')
p.add_argument('--pointer')
a = p.parse_args()
for name in a.paths:
    path = Path(name)
    assert re.match(r'^V\d\d/(impl|contract)(/|$)', name), name
    files = sorted(f for f in path.rglob('*') if f.is_file()) if path.is_dir() else [path]
    for f in files:
        raw = f.read_text()
        if a.pointer is not None:
            obj = json.loads(raw)
            for key in a.pointer.lstrip('/').split('/'):
                key = key.replace('~1', '/').replace('~0', '~')
                obj = obj[int(key)] if isinstance(obj, list) else obj[key]
            print(str(f) + '#' + a.pointer)
            for line in json.dumps(obj, indent=2).splitlines():
                print(redact(line))
            continue
        lines = raw.splitlines()
        selected = set()
        if a.lines:
            for span in a.lines.split(','):
                bounds = [int(x) for x in span.split(':')]
                start, end = (bounds[0], bounds[-1])
                selected.update(range(max(0, start-1), min(len(lines), end)))
        elif a.match:
            for i, line in enumerate(lines):
                if re.search(a.match, line):
                    selected.update(range(max(0, i-a.context), min(len(lines), i+a.context+1)))
        else:
            selected.update(range(len(lines)))
        if selected:
            print('\n' + str(f))
            last = -2
            for i in sorted(selected):
                if i > last+1:
                    print('...')
                print(f'{i+1}: {redact(lines[i])}')
                last = i
