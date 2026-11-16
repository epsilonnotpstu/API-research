import csv, json, re
from collections import Counter
from pathlib import Path

fields=['item_id','divergence_kind','contract_specificity','confidence','impl_locators','contract_locators','rationale']
with open('items.csv',newline='') as f:
    expected=[r['item_id'] for r in csv.DictReader(f)]
with open('codes_C5.csv',newline='') as f:
    reader=csv.DictReader(f)
    assert reader.fieldnames==fields
    rows=list(reader)
assert [r['item_id'] for r in rows]==expected
assert len(set(expected))==len(expected)
for row in rows:
    item=row['item_id']
    assert row['divergence_kind'] in {'DELIBERATE','ACCIDENTAL','UNCLEAR'}
    assert row['contract_specificity'] in {'SPECIFIC','GENERIC','UNCLEAR'}
    assert row['confidence'] in {'1','2','3'}
    assert 0<len(row['rationale'].split())<=40
    for field,part,sep in [('impl_locators','impl',':'),('contract_locators','contract','#')]:
        assert row[field]
        for locator in row[field].split(';'):
            path,anchor=locator.rsplit(sep,1)
            assert path.startswith(item+'/'+part+'/'),(item,locator)
            assert '..' not in Path(path).parts
            p=Path(path)
            assert p.is_file(),locator
            if anchor.isdigit():
                assert 1<=int(anchor)<=len(p.read_text().splitlines()),locator
            else:
                assert part=='contract' and anchor.startswith('/'),locator
                value=json.loads(p.read_text())
                for key in anchor[1:].split('/'):
                    key=key.replace('~1','/').replace('~0','~')
                    value=value[int(key)] if isinstance(value,list) else value[key]
    assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',row['rationale'])
report=Path('codes_report_C5.md').read_text()
assert all(word in report for word in ['পদ্ধতি','সীমাবদ্ধতা','Boundary incidents','W10'])
assert re.search(r'[\u0980-\u09ff]',report)
print('PASS: schema, 37-item order, labels, confidence, <=40-word rationales, same-item paths, line bounds, JSON pointers, Bengali report.')
print('divergence_kind:',dict(Counter(r['divergence_kind'] for r in rows)))
print('contract_specificity:',dict(Counter(r['contract_specificity'] for r in rows)))
print('confidence:',dict(Counter(r['confidence'] for r in rows)))
