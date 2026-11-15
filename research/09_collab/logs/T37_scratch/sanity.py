"""Offline market STRICT ablation: old selection, saved manifests, raw edit subsets."""
import collections
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import subprocess

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = Path(__file__).resolve().parent
SOURCE = ROOT / '08_experiments/_external/emb/openapi-swagger/market.json'
TOOLS = ROOT / '08_experiments/tools'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


old = load('t37_before', SCRATCH / 'specmut.before.py')
new = load('t37_after', TOOLS / 'specmut.py')
base = json.loads(SOURCE.read_text())


def family(edit):
    key = edit['pointer'].rsplit('/', 1)[1]
    return 'param_required' if key == 'required' and isinstance(edit['after'], bool) else key


def set_edit(doc, edit):
    node = doc
    parts = [p.replace('~1', '/').replace('~0', '~') for p in edit['pointer'][1:].split('/')]
    for part in parts[:-1]:
        node = node[int(part)] if isinstance(node, list) else node[part]
    node[int(parts[-1]) if isinstance(node, list) else parts[-1]] = copy.deepcopy(edit['after'])


result = {'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'fault': 'REQUEST_STRICT', 'severity': 30,
          'selection_note': 'Legacy manifests record mutated operations only. Seed 1 sampled GET /products '
                            'but produced no STRICT edit there; reconstruct the full original sample before comparison.',
          'rows': []}
for seed in (1, 2, 3):
    saved_path = ROOT / f'08_experiments/E1_pilot/runs/market/20261114T183929Z_batch_940129_mutated_REQUEST_STRICT_p30_s{seed}/manifest.json'
    saved = json.loads(saved_path.read_text())
    old_output, old_mutations, total = old.mutate(base, 'REQUEST_STRICT', 30, seed)
    assert old_mutations == saved['mutations']
    assert new.mutate(base, 'REQUEST_STRICT', 30, seed) == (old_output, old_mutations, total)
    candidates = [(p, m) for p, m, _ in old.operations(base)]
    selected = sorted(random.Random(f'{seed}:REQUEST_STRICT').sample(candidates, max(1, round(len(candidates) * .3))))
    assert new.select_operations(base, 'REQUEST_STRICT', 30, seed) == (selected, total)
    saved_ops = sorted((m['path'], m['method']) for m in saved['mutations'])
    legacy_no_edit = sorted(set(selected) - set(saved_ops))
    raw_by_op = {}
    prepared_by_op = {}
    for path, method in selected:
        working = copy.deepcopy(base)
        op = working['paths'][path][method]
        list(old.request_schemas(working, path, method, op))
        prepared_by_op[path, method] = copy.deepcopy(op)
        raw = []
        old.mutate_strict(working, path, method, op, raw)
        raw_by_op[path, method] = raw
    row = {'seed': seed, 'saved_manifest': str(saved_path.relative_to(ROOT)),
           'saved_manifest_sha256': hashlib.sha256(saved_path.read_bytes()).hexdigest(),
           'default_mutations_equal_saved': True, 'selected_operations': selected,
           'saved_mutated_operations': saved_ops, 'legacy_selected_no_edit': legacy_no_edit,
           'literal_sample_equals_saved_mutated_list': selected == saved_ops, 'variants': []}
    for keywords in (['required'], ['maximum', 'maxLength']):
        out = SCRATCH / f'market_s{seed}_{"_".join(keywords)}'
        process = subprocess.run(['/usr/bin/python3', '-I', '-B', str(TOOLS / 'specmut.py'), str(SOURCE),
            '--fault', 'REQUEST_STRICT', '--severity', '30', '--seed', str(seed),
            '--strict-keywords', ','.join(keywords), '--out', str(out)], capture_output=True, check=True)
        manifest_path = next(out.glob('*.manifest.json'))
        meta = json.loads(manifest_path.read_text())
        output = json.loads(Path(str(manifest_path).replace('.manifest.json', '.json')).read_text())
        edited = sorted((m['path'], m['method']) for m in meta['mutations'])
        selected_variant = sorted(edited + [tuple(o) for o in meta['selected_no_edit']])
        assert selected_variant == selected
        assert sorted(set(selected_variant) - set(legacy_no_edit)) == saved_ops
        expected = copy.deepcopy(base)
        expected_raw = []
        for path, method in selected:
            kept = [e for e in raw_by_op[path, method] if family(e) in keywords]
            if kept:
                expected['paths'][path][method] = copy.deepcopy(prepared_by_op[path, method])
                for edit in kept:
                    set_edit(expected, edit)
                expected_raw.extend(kept)
        assert output == expected
        expected_mutations = []
        for m in saved['mutations']:
            if (m['path'], m['method']) in edited:
                edits = old.document_edits(base['paths'][m['path']][m['method']],
                    expected['paths'][m['path']][m['method']], old.ptr('paths', m['path'], m['method']))
                expected_mutations.append({**m, 'edits': edits})
        assert meta['mutations'] == expected_mutations
        variant = {'strict_keywords': meta['strict_keywords'],
                   'selected_operations': selected_variant, 'selection_equals_unablated': True,
                   'full_edit_capable_selection_equals_saved_mutations': True,
                   'mutated_operations': edited, 'selected_no_edit': meta['selected_no_edit'],
                   'semantic_edits': expected_raw,
                   'semantic_edits_by_keyword': dict(collections.Counter(family(e) for e in expected_raw)),
                   'document_edit_count': sum(len(m['edits']) for m in meta['mutations']),
                   'output_equals_independent_old_mutator_edit_subset': True,
                   'manifest_equals_expected_structural_patch': True,
                   'manifest_path': str(manifest_path.relative_to(ROOT)),
                   'stdout': process.stdout.decode().strip()}
        row['variants'].append(variant)
    result['rows'].append(row)
result['all_checks_passed'] = True
(SCRATCH / 'sanity.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'all_checks_passed': True, 'rows': [{
    'seed': r['seed'], 'selected': len(r['selected_operations']), 'saved_mutated': len(r['saved_mutated_operations']),
    'variants': [{'keywords': v['strict_keywords'], 'mutated': len(v['mutated_operations']),
                  'selected_no_edit': len(v['selected_no_edit']), 'semantic_edits': v['semantic_edits_by_keyword']}
                 for v in r['variants']]} for r in result['rows']]}, indent=2))
