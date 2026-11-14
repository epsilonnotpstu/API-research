"""Property checks for specmut over a folder of real specs (e.g. EMB openapi-swagger/).

Usage: python3 test_specmut.py SPEC_DIR
Checks, for every spec x fault class:
  1. the mutated spec serialises to JSON;
  2. locality: operations not listed in the manifest are byte-identical to the original;
  3. manifest fidelity: every recorded edit's `after` value is present at its pointer
     (or the key is absent when `after` is None);
  4. determinism: the same seed yields the same manifest.
"""
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import specmut


def get(doc, pointer):
    node = doc
    for part in pointer.lstrip('/').split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        if isinstance(node, list):
            node = node[int(part)]
        elif isinstance(node, dict) and part in node:
            node = node[part]
        else:
            raise KeyError(pointer)
    return node


def apply_manifest(base, manifest):
    """Verify every before-value and reconstruct the complete output document."""
    import copy
    doc = copy.deepcopy(base)
    for m in manifest:
        for e in m['edits']:
            if e.get('op') == 'move':
                item = doc['paths'][m['path']]
                assert item[e['before']] == e['value']
                assert e['after'] not in item
                item[e['after']] = item.pop(e['before'])
                continue
            try:
                before = get(doc, e['pointer'])
                exists = True
            except KeyError:
                before, exists = None, False
            assert exists == e['before_exists'], e
            assert before == e['before'], e
            parent_pointer, _, raw_key = e['pointer'].rpartition('/')
            parent = get(doc, parent_pointer)
            key = raw_key.replace('~1', '/').replace('~0', '~')
            if isinstance(parent, list):
                key = int(key)
            if e['after_exists']:
                parent[key] = copy.deepcopy(e['after'])
            else:
                del parent[key]
    return doc


def check(spec_path, fault, severity=30, seed=7):
    base = specmut.load_spec(spec_path)
    mutated, manifest, n_ops = specmut.mutate(base, fault, severity, seed)
    json.dumps(mutated, default=str)
    touched = {(m['path'], m['method']) for m in manifest}
    if fault == 'METHOD_SEM':
        touched |= {(m['path'], e['after']) for m in manifest for e in m['edits']}
    for path, method, op in specmut.operations(base):
        if (path, method) not in touched:
            assert mutated['paths'][path].get(method) == op, f'locality broken at {method} {path}'
    for m in manifest:
        for e in m['edits']:
            if fault == 'METHOD_SEM':
                assert e['after'] in mutated['paths'][m['path']]
                continue
            try:
                value = get(mutated, e['pointer'])
                assert e['after_exists'] and value == e['after'], f'{e["pointer"]}: {value!r} != {e["after"]!r}'
            except KeyError:
                assert not e['after_exists'], f'missing pointer {e["pointer"]}'
    assert apply_manifest(base, manifest) == mutated, 'manifest omits changes'
    again = specmut.mutate(base, fault, severity, seed)
    assert again == (mutated, manifest, n_ops), 'non-deterministic'
    return n_ops, len(manifest), sum(len(m['edits']) for m in manifest)


def main(spec_dir):
    failures, rows = [], []
    for spec_path in sorted(glob.glob(f'{spec_dir}/*.json') + glob.glob(f'{spec_dir}/*.yaml')):
        fmt = 'oas3' if specmut.is_oas3(specmut.load_spec(spec_path)) else 'sw2'
        for fault in specmut.FAULTS:
            try:
                rows.append((Path(spec_path).stem, fmt, fault) + check(spec_path, fault))
            except Exception as exc:  # report and continue
                failures.append((Path(spec_path).stem, fault, repr(exc)[:200]))
    for r in rows:
        print(f'{r[0]:28s} {r[1]:4s} {r[2]:16s} ops={r[3]:4d} mutated={r[4]:3d} edits={r[5]:5d}')
    print(f'\n{len(rows)} passed, {len(failures)} failed')
    for f in failures:
        print('FAIL', *f)
    return 1 if failures or not rows else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
