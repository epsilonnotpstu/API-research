import csv
import json
import pathlib
import re
from collections import Counter

rows = json.loads(pathlib.Path('codes_work_C1/decisions.json').read_text())
items = list(csv.DictReader(open('items.csv')))
assert len(rows) == len(items) == 70

def locator(item, side, entry):
    if '#' in entry:
        suffix, pointer = entry.split('#', 1)
        line = None
    else:
        suffix, line = entry.rsplit(':', 1)
        line = int(line)
        pointer = None
    base = pathlib.Path(item) / side
    matches = [p for p in base.rglob('*') if p.is_file() and str(p).endswith('/' + suffix)]
    assert len(matches) == 1, (item, side, entry, matches)
    path = matches[0]
    content = path.read_text()
    if line is not None:
        assert 1 <= line <= len(content.splitlines()), (path, line)
        return f'{path}{":" if side == "impl" else "#"}{line}'
    node = json.loads(content)
    for key in pointer.lstrip('/').split('/'):
        key = key.replace('~1', '/').replace('~0', '~')
        node = node[int(key)] if isinstance(node, list) else node[key]
    return f'{path}#{pointer}'

output=[]
for raw, item in zip(rows, items):
    n, kind, specificity, confidence, impl, contract, rationale = raw
    item_id=f'X{n:02}'
    assert item_id == item['item_id']
    assert kind in {'DELIBERATE', 'ACCIDENTAL', 'UNCLEAR'}
    assert specificity in {'SPECIFIC', 'GENERIC', 'UNCLEAR'}
    assert confidence in {1, 2, 3}
    assert len(rationale.split()) <= 40, (item_id, len(rationale.split()))
    assert '\n' not in rationale
    output.append(dict(item_id=item_id, divergence_kind=kind,
                       contract_specificity=specificity, confidence=confidence,
                       impl_locators=';'.join(locator(item_id, 'impl', e) for e in impl.split(';')),
                       contract_locators=';'.join(locator(item_id, 'contract', e) for e in contract.split(';')),
                       rationale=rationale))

with open('codes_C1.csv','w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['item_id','divergence_kind','contract_specificity','confidence',
                                      'impl_locators','contract_locators','rationale'])
    writer.writeheader()
    writer.writerows(output)
print(json.dumps({'rows':len(output),
                  'divergence_kind':dict(Counter(x['divergence_kind'] for x in output)),
                  'contract_specificity':dict(Counter(x['contract_specificity'] for x in output)),
                  'confidence':dict(Counter(x['confidence'] for x in output)),
                  'max_rationale_words':max(len(x['rationale'].split()) for x in output)},ensure_ascii=False))
