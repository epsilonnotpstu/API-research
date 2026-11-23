from pathlib import Path
p=Path('codes_work_G2/decisions.txt'); lines=p.read_text().splitlines(); out=[]
for line in lines:
 row=line.split('|');n=int(row[0])
 if n==39:
  row[-1]="A collaborator's inherited write grant could override explicit read-only access on a child project; the fix restores nearer grants while retaining inherited administrator privileges."
 if n==24:row[-2]='192'
 if n==54:row[-2]='1189'
 if n==64:row[-2]='157'
 if n==98:row[-2]='162'
 if n==109:row[-2]='285'
 out.append('|'.join(row))
p.write_text('\n'.join(out)+'\n')
p=Path('codes_work_G2/build.py');s=p.read_text();s=s.replace('5,6,20,28,36,42','5,6,20,28,36,39,42');start=s.index('for r in rows:\n loc=');s=s[:start];p.write_text(s)
