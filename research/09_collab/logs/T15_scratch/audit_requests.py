"""Record uncertainty witnesses and generator-only schema cuts, using saved data."""
import collections
import csv
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RUN = ROOT / '08_experiments/E1_pilot/runs/scout-api/20261113T202103Z_baseline_NONE_p0_s1_1642810'
spec = json.loads((RUN / 'spec.original.json').read_text())
generated = json.loads((RUN / 'generator-input.json').read_text())
xs = [json.loads(raw) for raw in (RUN / 'exchanges.jsonl').open()]
items = list(csv.DictReader((ROOT / '08_experiments/E2_labelling/batch2_baseline_s1_blind.csv').open()))
maps = json.loads((OUT / 'exchange_map.json').read_text())

def features(value, schema, pointer=''):
    if '$ref' in schema:
        schema = spec['definitions'][schema['$ref'].rsplit('/', 1)[-1]]
    found = []
    if isinstance(value, dict):
        props = schema.get('properties', {})
        for name, val in value.items():
            if name not in props:
                found.append(('unknown_property', pointer + '/<undocumented>'))
            else:
                found.extend(features(val, props[name], pointer + '/' + name))
    elif isinstance(value, list):
        for val in value:
            found.extend(features(val, schema.get('items', {}), pointer + '/*'))
    elif schema.get('format') in ('int32', 'int64') and isinstance(value, int):
        bits = 32 if schema['format'] == 'int32' else 64
        if not -(2 ** (bits - 1)) <= value < 2 ** (bits - 1):
            found.append(('outside_java_integer_range', pointer))
    elif schema.get('format') == 'date-time' and isinstance(value, str):
        # This is a syntactic comparison to the explicit SimpleDateFormat;
        # it does not execute or emulate the Java parser.
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z', value):
            found.append(('differs_from_configured_date_pattern', pointer))
    return found

records = []
for item, mapped in zip(items, maps):
    if item['kind'] != 'VALID_REJECTED' or item['method'] == 'GET':
        continue
    op = spec['paths'][item['template']][item['method'].lower()]
    schema = next(p['schema'] for p in op['parameters'] if p['in'] == 'body')
    instances = []
    for line in mapped['exchange_lines']:
        value = json.loads(xs[line - 1]['request']['body']['text'])
        instances.append({'exchange_line': line, 'features': features(value, schema)})
    counts = collections.Counter(k for inst in instances for k in set(f[0] for f in inst['features']))
    records.append({'item_id': item['item_id'], 'count': len(instances), 'feature_counts': dict(counts),
                    'instances': instances})
(OUT / 'request_audit.json').write_text(json.dumps(records, indent=2) + '\n')
for row in records:
    print(row['item_id'],row['count'],row['feature_counts'],
          'no_flag_lines',[i['exchange_line'] for i in row['instances'] if not i['features']])

def diffs(a, b, pointer=''):
    if a == b:
        return []
    if isinstance(a, dict) and isinstance(b, dict):
        return [d for k in sorted(a.keys() | b.keys())
                for d in diffs(a.get(k), b.get(k), pointer + '/' + k.replace('~', '~0').replace('/', '~1'))]
    return [pointer]

diff = diffs(spec, generated)
(OUT / 'generator_diff.json').write_text(json.dumps({'changed_leaf_pointers': diff,
    'cuts': json.loads((RUN / 'derecurse-cuts.json').read_text())}, indent=2) + '\n')
print('generator differences', diff)
