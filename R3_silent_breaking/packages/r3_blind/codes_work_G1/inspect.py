from pathlib import Path
import sys

mode = sys.argv[1]
if mode == 'search':
    import re
    for arg in sys.argv[2:]:
        directory, pattern = arg.split('=', 1)
        print('\n###', directory, pattern)
        for p in Path(directory).rglob('*'):
            if not p.is_file():
                continue
            lines = p.read_text().splitlines()
            indices = set()
            for n, s in enumerate(lines):
                if re.search(pattern, s, re.I):
                    indices.update(range(max(0, n-3), min(len(lines), n+5)))
            if indices:
                print(p)
            for n in sorted(indices):
                print(f'{n+1}: {lines[n]}')
    sys.exit()
if mode == 'slice':
    pattern, start, end = sys.argv[2:]
    for p in Path('.').glob(pattern):
        print('\n###', p)
        for n, s in enumerate(p.read_text().splitlines(), 1):
            if int(start) <= n <= int(end):
                print(f'{n}: {s}')
    sys.exit()
for arg in sys.argv[2:]:
    p = Path(arg)
    if mode == 'diff':
        print('\n###', p)
        lines = (p / 'diff.patch').read_text().splitlines()
        removed = {s[1:].strip() for s in lines if s.startswith('-')}
        added = {s[1:].strip() for s in lines if s.startswith('+')}
        for n, s in enumerate(lines, 1):
            if s.startswith(('diff ', '@@')) or (s.startswith(('+', '-')) and s[1:].strip() not in (removed & added)):
                print(f'{n}: {s}')
    elif mode == 'files':
        for x in p.rglob('*'):
            if x.is_file():
                print(x)
    elif mode == 'read':
        print('\n###', p)
        for n, s in enumerate(p.read_text().splitlines(), 1):
            print(f'{n}: {s}')
