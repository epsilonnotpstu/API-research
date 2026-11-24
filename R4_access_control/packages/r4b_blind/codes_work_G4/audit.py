import csv, pathlib, re, collections
root=pathlib.Path(__file__).resolve().parent.parent
with (root/'codes_G4.csv').open(newline='') as f:
    rows=list(csv.DictReader(f))
print('Rows:',len(rows))
expected=list(csv.DictReader((root/'items.csv').open()))
print('Order correct:',[r['item_id'] for r in rows]==[r['item_id'] for r in expected])
for r in rows:
    item=r['item_id']
    if None in r or None in r.values(): print(item,'BAD CSV',r)
    if any('TODO' in str(v) for v in r.values()): print(item,'TODO')
    for k in ['rationale','policy_quote']:
        limit=30 if k=='rationale' else 25
        if len(r[k].split())>limit: print(item,k,'too long',len(r[k].split()))
    for k in ['op_locator','sec_locator']:
        value=r[k]
        if not value or value=='TODO': continue
        path,line=value.rsplit(':',1)
        p=root/item/path
        if not p.is_file(): print(item,k,'missing',p)
        else:
            lines=p.read_text().splitlines()
            if not 1<=int(line)<=len(lines): print(item,k,'bad line')
            elif k=='sec_locator' and 'security' not in lines[int(line)-1]: print(item,k,'not security:',lines[int(line)-1])
    if r['policy_in_contract']=='YES' and r['policy_quote']!='TODO':
        quote=r['policy_quote']
        texts=[p.read_text() for p in (root/item/'contract').iterdir() if p.name!='INDEX.md']
        if not any(quote in t or quote in t.replace('\\n','\n') for t in texts): print(item,'QUOTE NOT LITERAL',quote)
print('Contract coverage:',dict(collections.Counter(r['contract_operation'] for r in rows)))
