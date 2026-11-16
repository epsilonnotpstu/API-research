#!/usr/bin/python3
"""Inventory local references after mandatory cross-item file exclusions."""
import argparse
import json
from pathlib import Path
import posixpath
import re
import runpy

HERE = Path(__file__).resolve().parent
B = runpy.run_path(str(HERE / 'build_t48.py'))


def audit():
    output = B['OUT']
    missing = []
    local = remote = 0
    for path in output.rglob('*'):
        if not path.is_file() or len(path.relative_to(output).parts) < 3 or path.relative_to(output).parts[1] != 'contract':
            continue
        for ref in B['B']['references'](path.read_bytes()):
            filename = ref.partition('#')[0]
            if not filename:
                continue
            if re.match(r'^[a-zA-Z][\w+.-]*:', filename):
                remote += 1
                continue
            local += 1
            target = Path(posixpath.normpath(str(path.parent / filename)))
            if not target.is_file():
                missing.append(dict(source=str(path.relative_to(output)), reference=ref,
                                    target=str(target.relative_to(output))))
    # Sorting makes the audit independent of filesystem enumeration order.
    missing.sort(key=lambda row: (row['source'], row['reference'], row['target']))
    return dict(local_file_reference_incidents=local, remote_reference_incidents=remote,
                missing_reference_incidents=len(missing), affected_items=len({r['source'].split('/')[0] for r in missing}),
                missing_references=missing)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    result = audit()
    path = HERE / 'key/e10_reference_audit.json'
    if args.verify:
        existing = json.loads(path.read_text())
        existing['missing_references'].sort(key=lambda row: (row['source'], row['reference'], row['target']))
        assert result == existing
    else:
        B['R']['private_json'](path, result)
    print(json.dumps({k: v for k, v in result.items() if k != 'missing_references'}))


if __name__ == '__main__':
    main()
