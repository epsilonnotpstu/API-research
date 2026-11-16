import pathlib
import re
import sys


def safe(line):
    if re.search(r'@author|copyright|created by|written by|\bTODO\b|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', line, re.I):
        return '[REDACTED attribution/contact]'
    if re.search(r'(?:password|passwd|api[_-]?key|client[_-]?secret|private[_-]?key)\s*[=:]\s*[\"\x27][^\"\x27]+', line, re.I):
        return '[REDACTED credential-looking line]'
    return line


root = pathlib.Path(sys.argv[1])
assert root.parts[0].startswith('W') and '..' not in root.parts
range_match = re.fullmatch(r'lines:(\d+)-(\d+)', sys.argv[2])
pattern = re.compile(sys.argv[2], re.I)
context = int(sys.argv[3]) if len(sys.argv) > 3 else 3
files = sorted(root.rglob('*')) if root.is_dir() else [root]
for path in files:
    if not path.is_file():
        continue
    lines = path.read_text().splitlines()
    chosen = set()
    for i, line in enumerate(lines):
        if range_match:
            if int(range_match[1]) <= i+1 <= int(range_match[2]):
                chosen.add(i)
        elif pattern.search(line):
            chosen.update(range(max(0, i-context), min(len(lines), i+context+1)))
    if chosen:
        print('\n' + str(path))
        previous = -2
        for i in sorted(chosen):
            if i != previous + 1:
                print('...')
            print(f'{i+1}: {safe(lines[i])}')
            previous = i
