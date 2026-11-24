import pathlib,csv,re,json
root=pathlib.Path(__file__).resolve().parent.parent
for row in csv.DictReader((root/'codes_G4.csv').open()):
    if 'TODO' not in row['sec_locator']: continue
    loc=row['op_locator']
    if loc=='TODO': continue
    rel,num=loc.rsplit(':',1)
    lines=(root/row['item_id']/rel).read_text().splitlines()
    start=int(num)-1
    print(row['item_id'],rel)
    found=0
    for i in range(start,min(len(lines),start+250)):
        if re.search(r'["\x27]?security["\x27]?:',lines[i]):
            print(i+1,' / '.join(lines[i:i+4])); found+=1
            if found>=3: break
    for i,l in enumerate(lines):
        if re.match(r'^\s{0,2}["\x27]?security["\x27]?:',l): print('GLOBAL',i+1,l)
