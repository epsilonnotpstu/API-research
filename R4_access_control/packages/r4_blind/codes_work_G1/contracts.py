from pathlib import Path
import re
import sys

for arg in sys.argv[1:]:
    item, pattern = arg.split('=', 1)
    print(f'\n=== {item} / {pattern} ===')
    for file in sorted((Path(item) / 'contract').iterdir()):
        if file.suffix not in ('.yaml', '.yml', '.json'):
            continue
        lines = file.read_text().splitlines()
        entries = [(i, m.group(1) or m.group(2) or m.group(3)) for i, line in enumerate(lines) if (m := re.match(r'''^\s{0,10}(?:"(/[^"\n]*)"\s*:\s*\{|'(/[^'\n]*)'\s*:|(/\S*)\s*:)\s*$''', line))]
        print(f'{file}: {len(entries)} paths; {len(lines)} lines')
        for k, (i, path) in enumerate(entries):
            if not re.search(pattern, path, re.I):
                continue
            end = entries[k+1][0] if k+1 < len(entries) else len(lines)
            print(f'  {i+1}: {path}')
            for j in range(i+1, min(end, i+600)):
                if re.search(r'(?i)"?(get|put|post|patch|delete|head|security)"?\s*:', lines[j]):
                    print(f'    {j+1}: {lines[j].strip()}')
        sec = [(i+1, line.strip()) for i, line in enumerate(lines) if re.search(r'"?(security|securityDefinitions|securitySchemes)"?\s*:', line)]
        print('  security markers:', sec[-4:])
