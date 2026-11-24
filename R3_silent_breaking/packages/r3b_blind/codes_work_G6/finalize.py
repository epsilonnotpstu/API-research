import csv, sys, os
base = sys.argv[1]
hdr = ['item_id','changed_behaviour','affected_operation','contract_operation','op_locator','contract_specified','spec_quote','confidence','rationale']
rows = {}
with open(os.path.join(base,'codes_work_G6','rows.csv'), newline='') as f:
    for r in csv.reader(f):
        assert len(r) == 9
        assert r[0] not in rows, r[0]
        rows[r[0]] = r
order = [r['item_id'] for r in csv.DictReader(open(os.path.join(base,'items.csv'), newline=''))]
assert set(order) == set(rows), set(order) ^ set(rows)
for i in order:
    r = rows[i]
    assert r[3] in ('PRESENT','ABSENT','NO_CONTRACT','UNCLEAR')
    assert r[5] in ('SPECIFIED','UNSPECIFIED','UNCLEAR')
    assert (r[3]=='PRESENT') == bool(r[4]), i
    assert (r[5]=='SPECIFIED') == bool(r[6]), i
    assert len(r[6].split()) <= 25 and len(r[8].split()) <= 30, (i, len(r[8].split()))
    if r[4]:
        fn, ln = r[4][len('contract/'):].rsplit(':',1)
        lines = open(os.path.join(base,i,'contract',fn), encoding='utf-8', errors='replace').read().splitlines()
        print(i, lines[int(ln)-1].strip()[:90])
    if r[6]:
        txt = open(os.path.join(base,i,'contract',r[4][len('contract/'):].rsplit(':',1)[0]), encoding='utf-8').read()
        assert r[6] in txt, i
with open(os.path.join(base,'codes_G6.csv'),'w',newline='') as f:
    w = csv.writer(f)
    w.writerow(hdr)
    for i in order: w.writerow(rows[i])
print('written', len(order))
