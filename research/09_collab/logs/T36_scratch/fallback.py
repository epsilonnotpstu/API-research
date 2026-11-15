"""Save directed manual-fallback retrievals; outputs are data, never executed."""
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
TARGET=OUT/'fallback'
TARGET.mkdir(exist_ok=True)
rows=json.loads((OUT/'working_evidence.json').read_text())
roots={r['sut']:r['source_root'] for r in rows}
records=[]
def run(name,argv,items):
 if argv[0]=='rg' and len(argv)<5:
  raise ValueError('Refusing rg without an explicit source path')
 p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,errors='replace',check=False)
 # Do not retain secret-bearing source lines even in scratch output.
 out='\n'.join('[sensitive line withheld]' if re.search(
  r'(?i)(?:Basic|Bearer)\s+[A-Za-z0-9+/=]{6,}|(?:password|cookie|credential)[^\n]*[=:][^\n]*["\']',line)
  else line for line in p.stdout.splitlines())+'\n'
 target=TARGET/(name+'.txt');target.write_text(out)
 record={'name':name,'items':items,'argv':argv,'exit_code':p.returncode,
  'stdout_locator':str(target.relative_to(ROOT))+':1',
  'stderr':p.stderr,'stdout_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
  'retrieved_utc':datetime.now(timezone.utc).isoformat()}
 records.append(record)
 print(json.dumps({'name':name,'exit_code':p.returncode,'lines':len(out.splitlines())}))

for sut,root in roots.items():
 ids=[r['item_id'] for r in rows if r['sut']==sut]
 path=Path(root)
 tests=path/('api/src/test' if sut=='scout-api' else 'src/test')
 if sut=='market':tests=path/'market-web/src/test'
 pattern={
  'scout-api':r'HTTP_BAD_REQUEST|HTTP_NOT_FOUND|UnrecognizedProperty|FAIL_ON_UNKNOWN|system_messages|media_files|categories|activities|favourites',
  'swagger-petstore':r'photoUrls|name|status|upload|updateUser|@Test',
  'cwa-verification':r'TAN_VERIFICATION_URI|REGISTRATION_TOKEN_URI|NullKey|isNotFound|isBadRequest|content\(\)\.string',
  'market':r'_links|HAL|CartRestController|CustomerRestController|RestExceptionHandler|406',
 }[sut]
 run(sut+'_tests',['rg','-n',pattern,str(tests)],ids)
 docs=[str(p) for p in path.iterdir() if p.is_file() and p.name.lower().startswith(('readme','changelog'))]
 if sut=='cwa-verification':docs += [str(path/'docs/architecture-overview.md')]
 if sut=='market':docs += [str(path/'market-web/src/main/resources/templates/rest.html')]
 pattern={
  'scout-api':r'400|404|unknown|invalid|validation|JSON|not found',
  'swagger-petstore':r'photoUrls|uploadImage|updatePetWithForm|required|optional|validation|User|name|status',
  'cwa-verification':r'tan/verify|registrationToken|empty|body|keyType|required|validation|400|404',
  'market':r'_links|HAL|/customer/cart|POST /register|406|format|формат|валидац',
 }[sut]
 if docs:
  run(sut+'_docs',['rg','-n',pattern,*docs],ids)
 run(sut+'_history_scope',['git','--no-pager','-C',root,'rev-parse','HEAD','--is-shallow-repository'],ids)
 # Directed pickaxe beyond handler-only tool retrieval: models, serializers,
 # helpers and exception policies relevant to these sampled constraints.
 literals={'scout-api':['400','404','idList'], 'swagger-petstore':['photoUrls','name','status','userStatus'],
  'cwa-verification':['NotNull','handleVerificationServerExceptions','TAN_VERIFICATION_URI'],
  'market':['_links','HAL','HttpMessageNotReadableException']}[sut]
 for j,literal in enumerate(literals):
  run(sut+'_history_'+str(j),['git','--no-pager','-C',root,'log','--no-ext-diff','--no-textconv',
    '--format=%H %s','-S'+literal,'--','.'],ids)

# Review every actual history candidate's full message and file patch.
seen=set()
for r in rows:
 raw=json.loads((OUT/'search'/(r['item_id']+'.json')).read_text())
 for h in raw.get('hits',[]):
  if h['category']!='E-HISTORY':continue
  commit=h['commit'].split()[0];key=(r['source_root'],commit,h['file'])
  if key in seen:continue
  seen.add(key)
  run('patch_'+r['item_id'],['git','--no-pager','-C',r['source_root'],'show','--no-ext-diff',
    '--no-textconv','--format=fuller',commit,'--',h['file']],[r['item_id']])

# Reconstruct all scanner skip reasons without importing or running SUT code.
inventory={}
for sut,root in roots.items():
 skipped=[]
 for directory,dirs,names in os.walk(ROOT/root,followlinks=False):
  rejected=[d for d in dirs if d in {'.git','target','node_modules','.venv','venv','__pycache__','build','dist','.gradle','.idea'} or Path(directory,d).is_symlink()]
  skipped += [{'path':str(Path(directory,d).relative_to(ROOT/root)),'reason':'excluded directory'} for d in rejected]
  dirs[:]=sorted(d for d in dirs if d not in rejected)
  for name in sorted(names):
   p=Path(directory,name);rel=p.relative_to(ROOT/root);suffix=p.suffix.lower()
   eligible=suffix in {'.java','.kt','.py','.js','.ts','.tsx','.jsx','.go','.rb','.cs','.md','.adoc','.txt','.html','.htm','.rst'} or name.lower().startswith('readme') or set(rel.parts[:-1])&{'docs','templates'} or (suffix in {'.yaml','.yml','.json'} and (re.match(r'^(openapi|swagger)',p.stem,re.I) or p.stem=='inflector'))
   if not eligible:continue
   reason=None
   if p.is_symlink():reason='symlink'
   elif p.stat().st_size>2000000:reason='large bundled Swagger UI asset'
   else:
    b=p.read_bytes()
    try:
     b.decode('utf-8-sig')
     if b'\0' in b:reason='binary documentation font/image'
    except UnicodeError:reason='binary documentation font/image'
   if reason:skipped.append({'path':str(rel),'reason':reason})
 inventory[sut]={'source_root':root,'skips':skipped,
  'assessment':'Bundled UI assets, fonts/images and build output are not normative scenario evidence. Source tests/helpers/docs/config are separately reviewed. Remote/upstream history is unavailable under offline scope; local shallow import is not a developer fix.'}
(OUT/'fallback_manifest.json').write_text(json.dumps(records,indent=2)+'\n')
(OUT/'coverage_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
