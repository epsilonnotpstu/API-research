#!/usr/bin/python3
"""Build only the frozen R3 sample, with no manual candidate inspection."""
from collections import Counter
from datetime import datetime
import csv
import hashlib
import hmac
import io
import json
from pathlib import Path
import re
import posixpath
import runpy
import secrets
import sys
import tempfile
import traceback

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
OUT=BASE/'packages/r3_blind'
KEY=HERE/'key'
P=runpy.run_path(str(HERE/'t53_pool.py'))
S=runpy.run_path(str(HERE/'t53_sample.py'))
V=runpy.run_path(str(HERE/'t53_privacy.py'))
C=runpy.run_path(str(HERE/'t53_contracts.py'))
JVM_NAMES='OpenApi OpenAPI Operation Operations Api ApiOperation ApiResponse ApiResponses ApiModel ApiModelProperty ApiParam ApiImplicitParam ApiImplicitParams ApiIgnore ApiResponses Schema ArraySchema Parameter Parameters RequestBody Content ExampleObject Examples ExternalDocumentation Tag Tags SecurityRequirement SecurityRequirements SecurityScheme SecuritySchemes OAuthFlow OAuthFlows OAuthScope Hidden RouterOperation RouterOperations Path GET POST PUT DELETE PATCH HEAD OPTIONS TRACE Produces Consumes PathParam QueryParam HeaderParam CookieParam FormParam MatrixParam DefaultValue BeanParam Context Encoded ApplicationPath RequestMapping GetMapping PostMapping PutMapping DeleteMapping PatchMapping RestController Controller ResponseBody ResponseStatus ResponseEntityExceptionHandler ExceptionHandler ControllerAdvice RestControllerAdvice RequestParam PathVariable RequestHeader CookieValue RequestPart ModelAttribute CrossOrigin HttpExchange GetExchange PostExchange PutExchange DeleteExchange PatchExchange Valid Validated NotNull Null NotEmpty NotBlank Size Min Max DecimalMin DecimalMax Positive PositiveOrZero Negative NegativeOrZero Digits Pattern Email Past PastOrPresent Future FutureOrPresent AssertTrue AssertFalse Length Range URL CreditCardNumber ISBN Currency DurationMin DurationMax JsonProperty JsonIgnore JsonIgnoreProperties JsonInclude JsonFormat JsonAlias JsonValue JsonCreator JsonAnyGetter JsonAnySetter JsonGetter JsonSetter JsonUnwrapped JsonTypeInfo JsonSubTypes JsonSerialize JsonDeserialize JsonView JsonPropertyOrder'.split()
JVM_PATTERN=r'@(?:[A-Za-z_$][\w$]*\.)*(?:'+'|'.join(JVM_NAMES)+r')\b'
GO_PATTERN=r'//\s*(?:@(?:Router|Param|Success|Failure|Accept|Produce|Security)\b|swagger:)'
PATTERNS=dict(jvm_names=JVM_NAMES,jvm_pattern=JVM_PATTERN,go_pattern=GO_PATTERN,go_flags=['IGNORECASE'],
              scope='added/removed delivered hunk lines only; fully-qualified JVM names accepted')
KEY_COLUMNS='item_id repo commit parent language date n_files changed_lines annotation_touched spec_updated_90d contract_mapping_mode'.split()

def csv_bytes(columns,rows):
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,columns,lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return stream.getvalue().encode()

def shuffled(sample,salt):
    return sorted(sample,key=lambda r:(hmac.new(salt.encode(),(r['repo']+'\0'+r['sha']).encode(),hashlib.sha256).digest(),r['repo'].encode(),r['sha']))

def annotation_touched(patch):
    for line in patch.decode('utf-8','strict').splitlines():
        if line.startswith(('+++','---')) or not line.startswith(('+','-')):continue
        if re.search(JVM_PATTERN,line[1:]) or re.search(GO_PATTERN,line[1:],re.I):return True
    return False

def updated_90d(row,history):
    stamp=int(datetime.fromisoformat(row['date']).timestamp())
    position=history['positions'][row['sha']]
    return any(d['position']>position and stamp<d['timestamp']<=stamp+90*86400 for d in history['document_updates'])

def strip_patch(raw):
    lines=[];in_hunk=False
    for line in raw.decode('utf-8','strict').splitlines(keepends=True):
        if line.startswith('diff --git '):
            in_hunk=False
            lines.append(line)
        elif line.startswith(('--- ','+++ ')):
            lines.append(line)
        elif line.startswith('@@ '):
            in_hunk=True;lines.append(line)
        elif in_hunk and line[:1] in {'+','-',' ','\\'}:
            lines.append(line)
    return ''.join(lines).encode()

def context_for_repo(git,rows):
    messages=set();identifiers=set();shas=set()
    for row in rows:
        # Full message is inspected only by redaction machinery after both freezes.
        raw=git.run('show','-s','--format=%B',row['sha']).decode('utf-8','replace')
        lines,ids=V['message_needles'](raw)
        messages.update(lines);identifiers.update(ids)
        for oid in (row['sha'],row['parent']):
            if oid:shas.update([oid,oid[:7]])
    return dict(messages=sorted(messages,key=lambda s:(-len(s),s)),identifiers=sorted(identifiers),shas=sorted(shas))

def redact_fix(raw,**context):
    """F6 (Claude): apply redaction to a fixpoint (at most 5 passes). Redaction output can itself match another rule
    (observed only in projected JSON contracts); iterating only ever redacts more, and is identical for idempotent input."""
    data=V['redact'](raw,**context)
    for _ in range(4):
        again=V['redact'](data,**context)
        if again==data:break
        data=again
    if V['redact'](data,**context)!=data:
        # F6c: still no fixpoint -> replace every line that redaction would still change by a whole-line marker.
        out=[]
        for line in data.splitlines(keepends=True):
            body=line.rstrip(b'\r\n');end=line[len(body):]
            out.append(b'[REDACTED]'+end if V['redact'](body,**context)!=body else line)
        data=b''.join(out)
    return data

def build_item(row,item_id,git,history,context):
    files={};sources=[]
    for path in row['files']:
        if not P['safe_path'](path):raise ValueError('Unsafe package path')
        for role,revision in [('before',row['parent']),('after',row['sha'])]:
            raw=git.blob(revision,path)
            if raw is None:continue
            if b'\0' in raw:raise ValueError('Binary behaviour source')
            raw.decode('utf-8','strict')
            sources.append((path,raw))
            files[role+'/'+path]=redact_fix(raw,**context)
    patch=git.run('diff','--no-ext-diff','--no-textconv','--no-color','--find-renames=50%',
                  row['parent'] or P['EMPTY'],row['sha'],'--',*row['files'])
    files['diff.patch']=redact_fix(strip_patch(patch),**context)
    try:
        mapped=C['routes'](sources)
        roots=history['roots'][row['parent'] or 'ROOT']
        contracts,modes,remote=C['build'](roots,lambda path:git.blob(row['parent'],path),mapped)
        for path,raw in contracts.items():
            if not P['safe_path'](path):raise ValueError('Unsafe contract path')
            data=redact_fix(raw,**context)
            # F6b: a projection whose redaction has no fixpoint goes to the raw fallback instead of failing the item.
            if V['redact'](data,**context)!=data:raise C['ContractError']('Projected contract redaction has no fixpoint')
            # JSON representation under an original YAML filename is valid YAML 1.2.
            json.loads(data)
            files['contract/'+path]=data
        # Redaction must not silently leave a local contract reference unresolved.
        delivered_contracts={p.removeprefix('contract/'):json.loads(v) for p,v in files.items() if p.startswith('contract/')}
        for path,obj in delivered_contracts.items():
            for reference in C['references'](obj):
                filename,_,fragment=reference.partition('#')
                if re.match(r'^[\w+.-]+:',filename):continue
                target=posixpath.normpath(posixpath.join(posixpath.dirname(path),filename)) if filename else path
                if target not in delivered_contracts:raise C['ContractError']('Redacted contract has a missing local reference')
                C['at'](delivered_contracts[target],C['parts'](fragment))
    except (C['ContractError'], json.JSONDecodeError) as error:
        # F3 (Claude, D1): projection is context, not an inclusion criterion. Deliver the parent's root
        # contract document(s) as redacted plain text, first 2,000 lines in path byte order; never drop the item.
        for path in [p for p in files if p.startswith('contract/')]:del files[path]
        roots=history['roots'][row['parent'] or 'ROOT'];total=0
        for path in sorted(roots,key=lambda p:p.encode()):
            if not P['safe_path'](path):raise ValueError('Unsafe contract path')
            raw=git.blob(row['parent'],path)
            if raw is None or total>=2000:continue
            text=redact_fix(raw,**context).decode('utf-8','replace').splitlines(keepends=True)[:2000-total]
            # F6d: re-redact the truncated prefix (a JSON document's prefix is no longer JSON, so other rules apply)
            files['contract/'+path]=redact_fix(''.join(text).encode(),**context);total+=len(text)
        modes=[dict(path='*',mode='raw_fallback',operations=0,reason=type(error).__name__)];remote=0
    files['item.md']=('Repository: '+row['repo']+'\nLanguage: '+row['language']+'\nFiles:\n'+''.join('- '+p+'\n' for p in row['files'])).encode()
    files['item.md']=redact_fix(files['item.md'],**context)
    for data in files.values():
        if V['findings'](data,**context):raise ValueError('Delivered privacy/leakage finding; values suppressed')
    mode='no_checked_in_document' if not modes else ';'.join(sorted({m['mode'] for m in modes}))
    key=dict(item_id=item_id,repo=row['repo'],commit=row['sha'],parent=row['parent'] or '',language=row['language'],
             date=row['date'],n_files=len(row['files']),changed_lines=row['changed_lines'],
             annotation_touched=str(annotation_touched(files['diff.patch'])).lower(),
             spec_updated_90d=str(updated_90d(row,history)).lower(),contract_mapping_mode=mode)
    audit=dict(item_id=item_id,contract_mapping=modes,remote_references=remote,
               files={p:dict(sha256=P['sha'](data),bytes=len(data)) for p,data in sorted(files.items())})
    return files,key,audit

def path_flag(path,context):
    """F4 (revised): content rules (e.g. ENCODED, which matches any long '/'-joined token) do not apply to paths.
    A delivered path is flagged only if a segment contains a sample SHA (>= 7 hex), a ticket-style id, a '#'-number
    id written with '#', an email address, or a distinctive commit-message line."""
    low=path.lower()
    if any(len(v)>=7 and v.lower() in low for v in context['shas']):return True
    if any(m.lower() in low for m in context['messages']):return True
    for seg in path.split('/'):
        if V['EMAIL'].search(seg):return True
        for i in context['identifiers']:
            if i.startswith('#'):
                if i in seg:return True
            elif re.search(r'(?<![A-Za-z0-9])'+re.escape(i)+r'(?![A-Za-z0-9])',seg):return True
    return False

def scan_package(files,contexts):
    findings=Counter()
    for path,data in files.items():
        # F4 (Claude, after T54 review): delivered relative paths are scanned like contents.
        parts=path.split('/');role=parts[0] if len(parts)==1 else parts[1] if parts[1] in ('contract','before','after') else parts[-1]
        if any(path_flag(path,c) for c in contexts.values()):findings['path_metadata:'+role]+=1
        for kind in V['findings'](data):findings[kind]+=1
        for context in contexts.values():
            if V['redact'](data,**context)!=data:findings['sample_metadata']+=1
        # F5 (Claude): VCS headers can only leak through generated files; upstream contract/before/after files are
        # content (e.g. a YAML 'date:' key), and still pass the full privacy findings above.
        upstream_content=len(path.split('/'))>2 and path.split('/')[1] in ('contract','before','after')
        if not upstream_content and re.search(rb'(?im)^(?:index [0-9a-f]|commit [0-9a-f]|Author:|Date:|From [0-9a-f])',data):
            findings['vcs_header']+=1
        if '\r' in data.decode('utf-8','strict'):findings['non_LF']+=1
    return dict(findings)

def freeze_guard():
    S['guard']()
    sample=json.loads((HERE/'sample4.json').read_text())
    freeze=json.loads((HERE/'freeze4_sample.json').read_text())
    assert freeze['before_packaging'] is True
    assert freeze['sample_sha256']==P['sha']((HERE/'sample4.json').read_bytes())
    assert freeze['sampler_sha256']==P['sha']((HERE/'t53_sample.py').read_bytes())
    with (HERE/'heads.tsv').open() as stream:pinned=list(csv.DictReader(stream,delimiter='\t'))
    assert sample==S['select'](json.loads((HERE/'pool4.json').read_text()),[r['repo'] for r in pinned])
    assert P['heads']([P['UPSTREAM']/(r['repo']+'.git') for r in pinned])==pinned
    assert P['sha']((KEY/'document_history.json').read_bytes())==json.loads((HERE/'freeze4.json').read_text())['document_history_sha256']
    return sample

def prepare(sample,salt,directories,document_history,task_bytes):
    # Allocate every ID before building. Failures never shift subsequent IDs.
    order=shuffled(sample,salt)
    files={};keys=[];audits=[];failures=[];contexts={}
    gs={name:P['Git'](path) for name,path in directories.items()}
    try:
        # All sampled metadata needles are scanned against every delivered file.
        for repo,git in gs.items():contexts[repo]=context_for_repo(git,[r for r in sample if r['repo']==repo])
        union=dict(messages=sorted({v for c in contexts.values() for v in c['messages']},key=lambda s:(-len(s),s)),
                   identifiers=sorted({v for c in contexts.values() for v in c['identifiers']}),
                   shas=sorted({v for c in contexts.values() for v in c['shas']}))
        contexts={'all':union}
        items=[]
        for index,row in enumerate(order,1):
            iid=f'B{index:03}'
            try:
                item,key,audit=build_item(row,iid,gs[row['repo']],document_history[row['repo']],union)
                files.update({iid+'/'+path:data for path,data in item.items()})
                keys.append(key);audits.append(audit)
                items.append(dict(item_id=iid,repo=row['repo'],language=row['language'],files=';'.join(row['files'])))
            except Exception as error:
                # Never serialize exception messages or upstream data.
                reason=str(error) if isinstance(error,C['ContractError']) else 'mechanical package build failure; diagnostics suppressed'
                failures.append(dict(item_id=iid,repo=row['repo'],commit=row['sha'],
                                     failure_class=type(error).__name__,reason=reason,no_substitution=True,
                                     frames=[dict(function=f.name,line=f.lineno) for f in traceback.extract_tb(error.__traceback__)]))
        files['items.csv']=V['redact'](csv_bytes(['item_id','repo','language','files'],items),**union)
        files['README.md']=b'# Source packages\n\nitems.csv lists each item, repository, language, and source paths. Each item has item.md and diff.patch, complete source versions under before/ and after/, and checked-in API documents under contract/ when available. Repository paths are preserved. API documents may contain selected operations and their local references or a bounded selection in path order. Source values may be replaced with [REDACTED]. JSON-formatted contract files are also valid YAML 1.2. TASK_R3.md contains the reading instructions.\n'
        # This is the sole authorized plan input. Its bytes are not displayed.
        files['TASK_R3.md']=task_bytes
        findings=scan_package(files,contexts)
        if findings:raise ValueError('Package scan failed; kinds='+json.dumps(findings,sort_keys=True)+'; values suppressed')
        if V['redact'](task_bytes,**union)!=task_bytes:raise ValueError('Byte-identical task copy conflicts with redaction')
        return files,keys,audits,failures
    finally:
        for git in gs.values():git.close()

def publish(result,output=OUT,key_dir=KEY):
    files,keys,audits,failures=result
    if Path(output).exists():raise FileExistsError('Refusing to overwrite package')
    for name in ['r3_key.csv','r3_build_log.json','r3_build_failures.json']:
        if (key_dir/name).exists():raise FileExistsError('Refusing to overwrite key outputs')
    with tempfile.TemporaryDirectory(prefix='.r3-stage-',dir=key_dir) as temporary:
        stage=Path(temporary)/'package';stage.mkdir()
        for iid in [r['item_id'] for r in keys]:
            for role in ['contract','before','after']:(stage/iid/role).mkdir(parents=True)
        for relative,data in files.items():
            if not P['safe_path'](relative):raise ValueError('Unsafe output path')
            path=stage/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
        if output.exists():raise FileExistsError('Refusing to overwrite package')
        stage.rename(output)
    P['exclusive'](key_dir/'r3_key.csv',csv_bytes(KEY_COLUMNS,keys))
    P['exclusive'](key_dir/'r3_build_failures.json',P['jb'](failures))
    P['exclusive'](key_dir/'r3_build_log.json',P['jb'](dict(items=audits,
        build_code_hashes={name:P['sha']((HERE/name).read_bytes()) for name in ['t53_build.py','t53_privacy.py','t53_contracts.py']},
        package_hashes={p:P['sha'](data) for p,data in sorted(files.items())},
        shuffle='HMAC-SHA256(salt, repo + NUL + sha), byte-order tie breakers',
        summary=dict(sampled=len(keys)+len(failures),delivered=len(keys),build_failures=len(failures),
                     files=len(files),bytes=sum(map(len,files.values())),
                     annotation_touched=sum(r['annotation_touched']=='true' for r in keys),
                     spec_updated_90d=sum(r['spec_updated_90d']=='true' for r in keys),
                     mapping_modes=dict(Counter(r['contract_mapping_mode'] for r in keys))),
        checks=dict(privacy=True,metadata_leakage=True,task_byte_identical=True,sample_unchanged=True,
                    no_patch_display=True,network_used=False,upstream_execution=False))))

def main():
    if OUT.exists():raise FileExistsError('Refusing to overwrite package')
    sample=freeze_guard()
    patterns=HERE/'annotation_patterns.json'
    if patterns.exists():assert json.loads(patterns.read_text())==PATTERNS
    else:P['exclusive'](patterns,P['jb'](PATTERNS))
    salt_path=KEY/'r3_shuffle_salt.txt'
    if not salt_path.exists():P['exclusive'](salt_path,(secrets.token_hex(32)+'\n').encode())
    salt=salt_path.read_text().strip()
    history=json.loads((KEY/'document_history.json').read_text())
    task=(BASE/'plan/TASK_R3.md').read_bytes()
    result=prepare(sample,salt,{r['repo']:P['UPSTREAM']/(r['repo']+'.git') for r in sample},history,task)
    if '--preflight' in sys.argv:
        summary=dict(items=len(result[1]),failures=result[3],files=len(result[0]),bytes=sum(map(len,result[0].values())))
        (KEY/'preflight.json').write_bytes(P['jb'](summary))
        print(json.dumps(dict(items=summary['items'],build_failures=len(result[3]),failure_classes=dict(Counter(f['failure_class'] for f in result[3])),files=summary['files'],bytes=summary['bytes'])))
        return
    publish(result)
    print(json.dumps(json.loads((KEY/'r3_build_log.json').read_text())['summary']))

if __name__=='__main__':
    try:main()
    except Exception as error:sys.exit('Package build failed: '+type(error).__name__+('; '+str(error) if str(error).startswith('Package scan failed; kinds=') else '; diagnostics suppressed'))
