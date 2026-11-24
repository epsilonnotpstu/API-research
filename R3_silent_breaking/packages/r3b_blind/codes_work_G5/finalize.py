import csv, os
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
order = [r['item_id'] for r in csv.DictReader(open(os.path.join(base,'items.csv')))]
rows = {r[0]: r for r in csv.reader(open(os.path.join(base,'codes_work_G5','rows.csv')))}
assert set(rows) == set(order) and len(rows) == 60, (len(rows))
hdr = "item_id,changed_behaviour,affected_operation,contract_operation,op_locator,contract_specified,spec_quote,confidence,rationale".split(',')
for i in order:
    r = rows[i]
    assert r[3] in ('PRESENT','ABSENT','NO_CONTRACT','UNCLEAR'), r
    assert r[5] in ('SPECIFIED','UNSPECIFIED','UNCLEAR'), r
    if r[3] == 'PRESENT':
        f, ln = r[4].rsplit(':',1)
        line = open(os.path.join(base,i,f)).read().split('\n')[int(ln)-1]
        print(i, 'LOC', line.strip()[:90])
    else:
        assert r[4] == '', r
    if r[5] == 'SPECIFIED':
        assert len(r[6].split()) <= 25
        txt = open(os.path.join(base,i,r[4].rsplit(':',1)[0])).read()
        assert r[6] in txt, ('quote missing', i)
    if len(r[8].split()) > 30: print('LONG RATIONALE', i, len(r[8].split()))
with open(os.path.join(base,'codes_G5.csv'),'w',newline='') as fo:
    w = csv.writer(fo); w.writerow(hdr)
    for i in order: w.writerow(rows[i])
print('written', len(order))
