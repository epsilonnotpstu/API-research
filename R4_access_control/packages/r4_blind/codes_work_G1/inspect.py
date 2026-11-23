from pathlib import Path
import sys

for n in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
    base = Path(f'A{n:03}')
    print(f'\n===== {base} =====')
    text = (base / 'item.md').read_text()
    print(text[:int(sys.argv[3]) if len(sys.argv) > 3 else 2400])
    lines = (base / 'diff.patch').read_text().splitlines()
    print('--- DIFF ---')
    if len(lines) <= 180:
        for i, line in enumerate(lines, 1):
            print(f'{i}: {line}')
    else:
        selected = [(i, line) for i, line in enumerate(lines, 1) if line.startswith(('diff ', '@@', '+'))]
        for i, line in selected[:100]:
            print(f'{i}: {line}')
        print(f'[Long diff: {len(lines)} lines; showing first 100 selected lines]')
