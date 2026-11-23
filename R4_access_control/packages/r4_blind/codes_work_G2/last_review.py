from pathlib import Path
p=Path('codes_work_G2/decisions.txt');out=[]
for line in p.read_text().splitlines():
 r=line.split('|');n=int(r[0])
 if n==97:r[2]='UNCLEAR'
 if n==127:r[-1]="Authenticated CalDAV users could submit multiget REPORT hrefs with arbitrary task UIDs without verifying each returned task belonged to the project named in its href."
 if n==130:r[3]='SERVICE_LOGIC';r[-2]='163'
 if n==133:r=['133','UNCLEAR','10','The advisory describes scope widening, but the supplied before-version already rejects differing object and template metadata; the patch replaces rejection with normalization, leaving the described exploit unestablished.']
 out.append('|'.join(r))
p.write_text('\n'.join(out)+'\n')
p=Path('codes_work_G2/build.py');s=p.read_text().replace('112,125,126,128','112,125,126,127,128').replace('98,100,101','97,98,100,101');p.write_text(s)
p=Path('codes_report_G2.md');s=p.read_text().replace('103 YES, 32 NO, and 3 UNCLEAR','102 YES, 32 NO, and 4 UNCLEAR').replace('The three unresolved','The four unresolved')
s=s.replace('- **A100:**', '- **A133:** The before-version already rejects differing object and template metadata. The patch replaces that rejection with metadata normalization; the advertised scope-widening exploit is not established by this before/after pair.\n- **A100:**')
s=s.replace(' **A133** preserves trusted scope metadata during rotation; the defect is caller-controlled scope widening, not a broken encryption primitive.','')
s=s.replace('A078 and A101 leave', 'A078, A097, and A101 leave')
s=s.replace('- **A051, A060, A071, A138:**', '- **A127:** The before-version already checks the project for single-resource GET. The remaining supplied change checks multiget REPORT hrefs; the coding describes that narrower supported path.\n- **A051, A060, A071, A138:**')
p.write_text(s)
