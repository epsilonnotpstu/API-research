import csv, json, pathlib, re

root = pathlib.Path('.')
items = list(csv.DictReader((root/'items.csv').open(newline='')))
notes = list(csv.reader((root/'props_work_W1/notes.tsv').open(), delimiter='\t'))
assert len(notes) == len(items) == 70
assert [n[0] for n in notes] == [i['item_id'] for i in items]
banned = re.compile(r'\b(deliberate|deliberately|accidental|accidentally|intentional|intentionally|oversight|forgot|bug|wrong|correct|incorrect|should|mistake)\b', re.I)

def locator(item, side, short):
    if not short: return ''
    result = []
    for loc in short.split(';'):
        loc = loc.strip()
        if '#' in loc:
            suffix, pointer = loc.split('#', 1)
            line = None
        else:
            suffix, num = loc.rsplit(':', 1)
            line = int(num)
        candidates = [p for p in (root/item/side).rglob('*') if p.is_file() and str(p).endswith('/'+suffix)]
        assert len(candidates) == 1, (item, side, loc, candidates)
        p = candidates[0]
        content = p.read_text()
        if line is not None:
            lines = content.splitlines()
            assert 1 <= line <= len(lines), (p, line)
            assert lines[line-1].strip(), (p, line, 'blank locator')
            result.append(f'{p}{"#" if side == "contract" else ":"}{line}')
        else:
            obj = json.loads(content)
            for key in pointer.lstrip('/').split('/'):
                key = key.replace('~1', '/').replace('~0', '~')
                obj = obj[int(key)] if isinstance(obj, list) else obj[key]
            result.append(f'{p}#{pointer}')
    return ';'.join(result)

rows = []
for item, note in zip(items, notes):
    item_id, prop, contract, impl, confidence = note
    if prop != 'NONE':
        before, after = prop.split('; implementation ', 1)
        verb, rest = after.split(' ', 1)
        base = {'requires':'require', 'accepts':'accept', 'returns':'return',
                'serializes':'serialize', 'also':'also', 'calls':'call', 'throws':'throw',
                'passes':'pass', 'binds':'bind', 'bypasses':'bypass', 'replaces':'replace',
                'reads':'read', 'substitutes':'substitute', 'dereferences':'dereference',
                'appends':'append', 'emits':'emit', 'streams':'stream', 'represents':'represent',
                'exposes':'expose', 'ignores':'ignore', 'registers':'register', 'sends':'send',
                'unconditionally':'unconditionally', 'maps':'map', 'completes':'complete',
                'deserializes':'deserialize', 'places':'place', 'generates':'generate',
                'parses':'parse', 'defaults':'default', 'validates':'validate', 'writes':'write',
                'ends':'end', 'rejects':'reject', 'treats':'treat'}
        if verb == 'also':
            rest = rest.replace('accepts ', 'accept ', 1)
        if verb == 'unconditionally':
            rest = rest.replace('parses ', 'parse ', 1)
        for finite, infinitive in [('forwards','forward'), ('throws','throw'), ('returns','return'),
                                   ('dereferences','dereference'), ('saves','save'), ('applies','apply')]:
            rest = re.sub(r'\b(and|but never) '+finite+r'\b', r'\1 '+infinitive, rest)
        prop = before+'; implementation does '+base[verb]+' '+rest
        prop = f'{item["operation"]}: {prop}'
        assert len(prop.split()) <= 45, (item_id, len(prop.split()))
        assert prop.count('; implementation does ') == 1
        assert not banned.search(prop), (item_id, prop)
        assert contract and impl
    else:
        assert not contract and not impl
    assert confidence in ('1', '2', '3')
    rows.append(dict(item_id=item_id, proposition=prop,
                     contract_locators=locator(item_id, 'contract', contract),
                     impl_locators=locator(item_id, 'impl', impl), confidence=confidence))

output = root/'props_W1.csv'
with output.open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['item_id', 'proposition', 'contract_locators', 'impl_locators', 'confidence'])
    writer.writeheader()
    writer.writerows(rows)
assert list(csv.DictReader(output.open(newline=''))) == rows
audit = dict(item_count=len(rows), discrepancy_count=sum(r['proposition']!='NONE' for r in rows),
             none_items=[r['item_id'] for r in rows if r['proposition']=='NONE'],
             confidence_counts={str(i):sum(r['confidence']==str(i) for r in rows) for i in (1,2,3)},
             max_proposition_words=max(len(r['proposition'].split()) for r in rows),
             checks=['row count and order', 'exact CSV columns', 'CSV round trip', 'word limit',
                     'proposition form', 'excluded vocabulary', 'locator file existence',
                     'locator nonempty source lines', 'JSON pointer resolution', 'confidence values',
                     'empty NONE locators'])
audit['none_item_files'] = {
    r['item_id']: {side: [str(p) for p in sorted((root/r['item_id']/side).rglob('*')) if p.is_file()]
                   for side in ('contract', 'impl')}
    for r in rows if r['proposition'] == 'NONE'
}
(root/'props_work_W1/audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit, indent=2))
