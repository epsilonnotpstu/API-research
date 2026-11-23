from pathlib import Path
p=Path('codes_work_G2/decisions.txt')
rows={int(l.split('|')[0]):l.split('|') for l in p.read_text().splitlines()}
locs={4:313,14:177,20:21,24:192,29:239,51:80,54:1190,58:75,64:157,65:101,86:219,98:163,104:161,106:125,109:286,131:172,136:589}
for n,v in locs.items():rows[n][-2]=str(v)
rows[6][2]='TWO_ROLES'
rows[54][3]='SERVICE_LOGIC'
rows[78][2]='UNCLEAR'
rows[101][2]='UNCLEAR'
rows[121][2]='TWO_SAME_ROLE'
rows[121][-1]="A non-admin could update another user's account, including changing its password, by naming that user in an update request."
rows[100]=['100','UNCLEAR','66','The advisory does not identify a denied caller or operation, and the patch adds a service interface without showing policy enforcement; the specific access violation is unclear.']
rows[133]=['133','PROPERTY_LEVEL','NONE','SERVICE_LOGIC','12',"A rotate caller could set untrusted template scope annotations and receive a victim's sealed secret re-encrypted with cluster-wide scope, enabling retargeting."]
rows[53][-1]="Authenticated users could access sensitive file metadata by filename UUID without checking that the file belonged to the board and team they could access."
p.write_text('\n'.join('|'.join(rows[n]) for n in sorted(rows))+'\n')
p=Path('codes_work_G2/contracts.txt')
ls=p.read_text().splitlines();ls=[l for l in ls if not l.startswith('100|')]
ls.append('133|PRESENT|NOT_DECLARED|NO|docs__developer__swagger.yml:43')
p.write_text('\n'.join(ls)+'\n')
