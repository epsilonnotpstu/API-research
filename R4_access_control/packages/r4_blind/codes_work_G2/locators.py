from pathlib import Path
p=Path('codes_work_G2/decisions.txt');out=[]
for l in p.read_text().splitlines():
 r=l.split('|');n=int(r[0])
 if n in {54,58,98,109,131}:r[-2]=str({54:1193,58:93,98:312,109:154,131:171}[n])
 out.append('|'.join(r))
p.write_text('\n'.join(out)+'\n')
