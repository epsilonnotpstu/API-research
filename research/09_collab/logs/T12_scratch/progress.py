"""Update only T12's status cell and append an evidence-bearing board log."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import sys


def update(status, message):
    path = Path('09_collab/COLLAB_BOARD.md')
    lines = path.read_text().splitlines()
    for index, line in enumerate(lines):
        if line.startswith('| T12 |'):
            cells = line.split('|')
            cells[5] = f' {status} '
            lines[index] = '|'.join(cells)
            break
    else:
        raise RuntimeError('T12 row missing')
    stamp = datetime.now(ZoneInfo('Asia/Dhaka')).strftime('%Y-%m-%d %H:%M')
    lines.append(f'- {stamp} | Codex | T12 | {message}')
    path.write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    update(*sys.argv[1:])
