#!/usr/bin/python3
"""Build bounded, parent-state excerpts. Never execute upstream content."""
import argparse
from collections import Counter
import csv
import hashlib
import hmac
import io
import json
import posixpath
from pathlib import Path
import re
import runpy
import secrets
import tempfile

HERE=Path(__file__).resolve().parent
M=runpy.run_path(str(HERE/'mine.py')); O=M['OLD']; Git=O['Git']; require=O['require']
ROOT=HERE.parents[1]
OUT=ROOT/'08_experiments/E2_labelling/e7_blind'
KEY=HERE/'key'
FORBIDDEN=re.compile(r'\b(?:fix|fixed|commit|later|changed|mined|repair|direction|E6|E7|T42|T43|T45|T46)\b',re.I)
KEY_COLUMNS='item_id set repo stars fix_commit parent_commit date operation truth_direction confidence contract_kind mismatch_type fix_family cross_item_flag source_task'.split()
ITEM_COLUMNS='item_id repo operation proposition'.split()
LIMIT=300*1024
ATTRIBUTION_HEADING=re.compile(r'^\s*(?://|/\*|\*|#)\s*(?:authors?|contributors?)\s*:',re.I)

def sha(b):return hashlib.sha256(b).hexdigest()
def jb(v):return (json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
def cb(columns,rows):return O['csv_bytes'](columns,rows)
def absent(paths):O['assert_absent'](paths)

def sanitize(raw,path,needles):
    data=O['redact'](raw,needles).decode()
    # Preserve JSON syntax and physical line numbering, including escaped strings.
    try:
        value=json.loads(data)
    except ValueError:value=None
    if isinstance(value,(dict,list)):
        def walk(v):
            if isinstance(v,str) and re.search(r'(?i)licensed to|signed-off-by|co-authored-by|@author\b',v):
                return {v}
            if isinstance(v,dict):return set().union(*(walk(x) for x in v.values()),set())
            if isinstance(v,list):return set().union(*(walk(x) for x in v),set())
            return set()
        contact=value.get('info',{}).get('contact',{}) if isinstance(value,dict) and isinstance(value.get('info'),dict) else {}
        contact_values={s for s in contact.values() if isinstance(s,str)} if isinstance(contact,dict) else set()
        for s in sorted(walk(value)|contact_values,key=lambda s:-len(s)):
            for spelling in {json.dumps(s),json.dumps(s,ensure_ascii=False)}:data=data.replace(spelling,'"<redacted>"')
    else:
        lines=[];credits=False;info=False;contact_indent=None
        for line in data.splitlines(keepends=True):
            if path.endswith(('.yaml','.yml')):
                indent=len(line)-len(line.lstrip(' '))
                if re.match(r'^info:\s*$',line):info=True
                elif line.strip() and not line.lstrip().startswith('#') and indent==0:info=False;contact_indent=None
                if info and re.match(r'^\s+contact:\s*',line):
                    contact_indent=indent
                    if re.search(r'contact:\s*\{',line):line=line.split('contact:',1)[0]+'contact: {}'+ ('\n' if line.endswith('\n') else '')
                elif contact_indent is not None and line.strip() and indent<=contact_indent:contact_indent=None
                if contact_indent is not None and indent>contact_indent and re.match(r'^\s+(?:name|email|url):',line):
                    line=line.split(':',1)[0]+': "<redacted>"'+ ('\n' if line.endswith('\n') else '')
            if ATTRIBUTION_HEADING.search(line):credits=True
            elif credits and ('*/' in line or not re.match(r'^\s*(?:\*|//|#)',line)):
                credits=False
            if credits:
                line=('// [REDACTED attribution]' if path.endswith(('.java','.kt','.go')) else '# [REDACTED attribution]')+ ('\n' if line.endswith('\n') else '')
            if re.search(r'(?i)licensed to|signed-off-by|co-authored-by|SPDX-FileCopyrightText',line):
                line=('// [REDACTED attribution]' if path.endswith(('.java','.kt','.go')) else '# [REDACTED attribution]')+ ('\n' if line.endswith('\n') else '')
            if path.endswith(('.yaml','.yml')) and line.startswith('// [REDACTED attribution]'):line='#'+line[2:]
            lines.append(line)
        data=''.join(lines)
    data=re.sub(r'\b\d{4}-\d{2}-\d{2}(?:[T ][0-9:.+Z-]+)?\b','<redacted>',data)
    data=re.sub(r'\b[a-fA-F0-9]{40}(?:[a-fA-F0-9]{24})?\b','<redacted>',data)
    require(len(data.splitlines())==len(raw.decode().splitlines()),'Redaction changed line count')
    result=data.encode()
    require(not O['privacy_findings'](result,needles),'Privacy scan failed (values suppressed)')
    require(not re.search(r'(?i)signed-off-by|co-authored-by|@author\b|SPDX-FileCopyrightText',data),'Attribution scan failed')
    require(not any(ATTRIBUTION_HEADING.search(line) for line in data.splitlines()),'Attribution heading scan failed')
    require(not re.search(r'\b\d{4}-\d{2}-\d{2}\b|\b[0-9a-f]{40,64}\b',data,re.I),'History literal scan failed')
    if isinstance(value,(dict,list)):json.loads(result)
    return result

def locators(row):
    check=json.loads(row['proposition_check']);roles={}
    for role in ['contract','implementation','route']:
        roles[role]=set()
        for loc in check.get(role,[]):
            rev,path,line=loc.rsplit(':',2)
            require(rev==row['parent_commit'] and line.isdigit(),'Non-parent or malformed locator')
            O['safe_path'](path);roles[role].add(path)
    require(roles['contract'] and roles['implementation'],'Missing parent locators')
    return roles

def yaml_nodes(text):
    """Index block-mapping nodes without evaluating YAML tags or constructors.

    Only complete original YAML nodes are copied. Unsupported layout is refused.
    No scalar or third-party YAML code is evaluated.
    """
    lines=text.splitlines(keepends=True); stack=[];nodes={}
    pattern=re.compile(r'^( *)([^\s#][^:]*?):(?:\s|$)')
    for i,line in enumerate(lines):
        match=pattern.match(line)
        if not match or match[2].startswith('- '):continue
        indent=len(match[1]);key=match[2].strip().strip('"\'')
        while stack and stack[-1][0]>=indent:
            _,ptr,start=stack.pop();nodes[ptr]=(start,i)
        ptr=(*(stack[-1][1] if stack else ()),key)
        stack.append((indent,ptr,i))
    while stack:
        _,ptr,start=stack.pop();nodes[ptr]=(start,len(lines))
    return lines,nodes

def pointer_parts(fragment):
    return tuple(x.replace('~1','/').replace('~0','~') for x in fragment.lstrip('/').split('/')) if fragment else ()

def references(data):
    # JSON is preferred; YAML block/flow $ref scalar spellings are bounded data.
    try:
        obj=json.loads(data)
    except ValueError:
        return re.findall(r'\$ref\s*:\s*[\'\"]?([^\s\'\",}]+)',data.decode())
    out=[]
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get('$ref'),str):out.append(v['$ref'])
            for c in v.values():walk(c)
        elif isinstance(v,list):
            for c in v:walk(c)
    walk(obj);return out

def project_json(raw,path,operation,fragments=()):
    source=json.loads(raw);method,target=operation.split(' ',1)
    selected={'openapi':source['openapi']} if 'openapi' in source else {'swagger':source['swagger']}
    selected['info']=source.get('info',{'title':'Source excerpt','version':'source'})
    selected['x-source-path']=path
    for k in ['servers','basePath','host','schemes','consumes','produces','security']:
        if k in source:selected[k]=source[k]
    def copy_pointer(parts):
        obj=source
        for p in parts:obj=obj[p]
        dest=selected
        for p in parts[:-1]:dest=dest.setdefault(p,{})
        dest[parts[-1]]=obj
    if fragments:
        for frag in fragments:copy_pointer(pointer_parts(frag))
    else:
        candidates=[p for p in source.get('paths',{}) if target==p or target.endswith(p)]
        require(len(candidates)==1,'Cannot identify operation in large JSON contract')
        p=candidates[0];copy_pointer(('paths',p,method.lower()))
        if 'parameters' in source['paths'][p]:copy_pointer(('paths',p,'parameters'))
    seen=set()
    while True:
        refs=set(references(jb(selected)))-seen
        if not refs:break
        for ref in refs:
            seen.add(ref)
            if ref.startswith('#/'):copy_pointer(pointer_parts(ref[1:]))
    return jb(selected)

def project_yaml(raw,path,operation,fragments=()):
    lines,nodes=yaml_nodes(raw.decode());method,target=operation.split(' ',1)
    selected=set()
    if fragments:
        selected.update(pointer_parts(f) for f in fragments)
    else:
        candidates=[ptr for ptr in nodes if len(ptr)==3 and ptr[0]=='paths' and ptr[2]==method.lower() and (target==ptr[1] or target.endswith(ptr[1]))]
        require(len(candidates)==1,'Cannot identify operation in large YAML contract')
        selected.add(candidates[0])
        parameter=('paths',candidates[0][1],'parameters')
        if parameter in nodes:selected.add(parameter)
    for key in ['openapi','swagger','info','servers','basePath','host','schemes','consumes','produces','security']:
        if (key,) in nodes:selected.add((key,))
    def block(ptr):
        require(ptr in nodes,'Missing local YAML reference target')
        a,b=nodes[ptr];return ''.join(lines[a:b])
    seen=set()
    while True:
        refs=set(references(''.join(block(p) for p in selected).encode()))-seen
        if not refs:break
        for ref in refs:
            seen.add(ref)
            if ref.startswith('#/'):selected.add(pointer_parts(ref[1:]))
    # Reconstruct ancestors and retain whole mapping nodes verbatim.
    selected={p for p in selected if not any(p[:i] in selected for i in range(1,len(p)))}
    trie={}
    for ptr in selected:
        d=trie
        for p in ptr:d=d.setdefault(p,{})
    def emit(d,prefix=(),depth=0):
        out=[]
        for key,child in sorted(d.items(),key=lambda kv:nodes.get(prefix+(kv[0],),(10**9,))[0]):
            ptr=prefix+(key,)
            if ptr in selected:
                text=block(ptr);indent=len(text)-len(text.lstrip(' '))
                out.extend(' '*depth+line[indent:] if line.strip() else line for line in text.splitlines(keepends=True))
            else:
                out.append(' '*depth+json.dumps(key)+':\n');out.extend(emit(child,ptr,depth+2))
        return out
    return ('# Source path: '+path+'\n'+''.join(emit(trie))).encode()

def contract_files(row,git,initial):
    tree=git.tree(row['parent_commit']);files={};remote=set();pending=[(p,()) for p in sorted(initial)];wanted={};processed={}
    while pending:
        path,fragments=pending.pop(0)
        state=wanted.setdefault(path,set())
        state.update(fragments)
        signature=tuple(sorted(state))
        if path in processed and processed[path]==signature:continue
        processed[path]=signature
        fragments=() if path in initial else signature
        require(path in tree,'Missing local contract file')
        entry=tree[path];require(entry.mode=='100644' or entry.mode=='100755','Non-regular contract')
        raw=git.blobs([entry])[entry.oid]
        if len(raw)>LIMIT and path.endswith(('.json','.yaml','.yml')):
            data=project_json(raw,path,row['operation'],fragments) if path.endswith('.json') else project_yaml(raw,path,row['operation'],fragments)
        else:data=raw
        files[path]={'raw':raw,'excerpt':data,'projection':data!=raw}
        targets={}
        for ref in references(data):
            filename,_,fragment=ref.partition('#')
            if not filename:continue
            if re.match(r'^[a-zA-Z][\w+.-]*:',filename):remote.add(ref);continue
            other=posixpath.normpath(posixpath.join(posixpath.dirname(path),filename));O['safe_path'](other)
            targets.setdefault(other,[]).append(fragment)
        pending.extend((p,tuple(fs)) for p,fs in sorted(targets.items()))
    return files,sorted(remote)

def helper_selection(git,parent,required,manual=()):
    tree=git.tree(parent);selected=set(required)|set(manual)
    require(len(selected)<=8,'More than eight required implementation files')
    require(selected<=tree.keys(),'Missing implementation evidence')
    candidates=[]
    for path in sorted(required):
        e=tree[path];text=git.blobs([e])[e.oid].decode('utf-8')
        for name in set(re.findall(r'\b([A-Z]\w*(?:Helper|Validator|Guard|Mapper|Utils|Util|Converter|Constants))\b',text)):
            matches=[p for p in tree if p.endswith('/'+name+'.java') and not M['SKIP'].search(p)]
            if len(matches)==1 and matches[0] not in selected:candidates.append(matches[0])
    for path in sorted(set(candidates)):
        if len(selected)<8:selected.add(path)
    return selected,sorted(set(candidates)-selected)

def prepare(rows,repos,salt,needles=()):
    require(rows and len({r['item_id'] for r in rows})==len(rows),'Duplicate or empty source IDs')
    rows=sorted(rows,key=lambda r:(hmac.new(salt.encode(),r['item_id'].encode(),hashlib.sha256).digest(),r['item_id']))
    gs={repo:Git(repos[repo]) for repo in sorted({r['repo'] for r in rows})}
    items=[]
    for n,row in enumerate(rows,1):
        git=gs[row['repo']];parent=row['parent_commit'];child=row['fix_commit']
        require(git.run('rev-parse',child+'^').decode().strip()==parent,'Not the recorded direct parent')
        roles=locators(row);protected=set().union(*roles.values())
        contracts,remote=contract_files(row,git,roles['contract'])
        # An annotated file serving both roles must also appear under impl/.
        impl_required=roles['implementation']|(roles['route']-set(contracts))
        impl,omitted_helpers=helper_selection(git,parent,impl_required,row.get('helper_paths',()))
        files={};raw_files={};tree=git.tree(parent)
        for p,d in contracts.items():
            files['contract/'+p]=d['excerpt'];raw_files[p]=d['raw']
        for p in impl:
            e=tree[p];require(e.kind=='blob' and e.mode in {'100644','100755'},'Non-regular implementation')
            raw=git.blobs([e])[e.oid];raw.decode('utf-8');require(b'\0' not in raw,'Binary implementation')
            files['impl/'+p]=raw;raw_files[p]=raw
        items.append(dict(id=f'X{n:02}',row=row,files=files,raw_files=raw_files,protected=protected,contracts=contracts,impl=impl,omitted_helpers=omitted_helpers,remote_refs=remote,changed_paths=git.changed(parent,child),cross_item_flag=False))
    pairs=[]
    for a in items:
        for b in items:
            if a is b or a['row']['repo']!=b['row']['repo']:continue
            git=gs[a['row']['repo']]
            if not git.ancestor(a['row']['fix_commit'],b['row']['parent_commit']):continue
            overlap=set(a['changed_paths'])&b['raw_files'].keys()
            if not overlap:continue
            b['cross_item_flag']=True
            removable=overlap-b['protected']
            for p in removable:
                b['files'].pop('impl/'+p,None);b['files'].pop('contract/'+p,None);b['raw_files'].pop(p)
            pairs.append(dict(earlier=a['id'],later=b['id'],paths=sorted(overlap),excluded=sorted(removable),retained_own_locators=sorted(overlap&b['protected'])))
    delivered={};keys=[];manifest=[];details=[]
    for item in items:
        row=item['row'];git=gs[row['repo']];parent=row['parent_commit'];child=row['fix_commit']
        childtree=git.tree(child);parenttree=git.tree(parent)
        entries=[childtree[p] for p in item['changed_paths'] if p in childtree and childtree[p].kind=='blob' and (p not in parenttree or childtree[p].oid!=parenttree[p].oid)]
        forbidden={sha(b) for b in git.blobs(entries).values()}
        file_log={}
        for relative,raw_excerpt in sorted(item['files'].items()):
            role,p=relative.split('/',1)
            require(not re.search(r'change.?log|release.?notes',p,re.I),'History document selected')
            data=sanitize(raw_excerpt,p,needles)
            if role=='contract' and item['contracts'][p]['projection'] and p.endswith(('.yaml','.yml')):
                _,nodes=yaml_nodes(data.decode())
                require(all(pointer_parts(ref[1:]) in nodes for ref in references(data) if ref.startswith('#/')),'Projected YAML has an unresolved component')
            require(sha(item['raw_files'][p]) not in forbidden and sha(data) not in forbidden,'Non-parent child content detected')
            require(item['raw_files'][p]==git.blobs([parenttree[p]])[parenttree[p].oid],'Parent provenance failure')
            related=[r for r in rows if r['repo']==row['repo']]
            require(not O['reference_hits'](data,related,O['is_doc'](p)),'Future metadata reference in source (content suppressed)')
            require(not any(r.get('message_excerpt') and r['message_excerpt'].casefold() in data.decode().casefold() for r in related),'Message in package')
            delivered[item['id']+'/'+relative]=data
            file_log[relative]=dict(parent_oid=parenttree[p].oid,parent_sha256=sha(item['raw_files'][p]),excerpt_sha256=sha(raw_excerpt),delivered_sha256=sha(data),bytes=len(data),redacted=data!=raw_excerpt,projection=role=='contract' and item['contracts'][p]['projection'])
        require(sum(p.startswith('impl/') for p in file_log)<=8,'Implementation cap exceeded')
        require(all('impl/'+p in file_log for p in locators(row)['implementation']),'Missing implementation locator under impl/')
        require(item['protected']<=item['raw_files'].keys(),'Own locator removed')
        key=dict(row,item_id=item['id'],cross_item_flag=str(item['cross_item_flag']).lower());keys.append(key)
        manifest.append({k:key[k] for k in ITEM_COLUMNS})
        details.append(dict(item_id=item['id'],source_item=row['item_id'],repo=row['repo'],fix_commit=child,parent_commit=parent,files=file_log,protected=sorted(item['protected']),omitted_helpers=item['omitted_helpers'],remote_refs=item['remote_refs'],cross_item_flag=item['cross_item_flag']))
    delivered['items.csv']=cb(ITEM_COLUMNS,manifest)
    require(not FORBIDDEN.search(delivered['items.csv'].decode()),'Forbidden word in items.csv')
    delivered['README.md']=b'# Source reading excerpts\n\nEach table row identifies an independent proposition. The contract and implementation directories preserve repository paths. Source files are complete except for privacy redactions; large specification documents contain the selected operation and its local reference closure. Line positions in complete files are retained. Excerpts have no VCS history. Read each row independently.\n'
    for iid,r in zip([x['item_id'] for x in manifest],rows):
        actual=next(x for x in manifest if x['item_id']==iid)
        require(actual['proposition']==r['proposition'],'Non-verbatim proposition')
    for p,data in delivered.items():require(not O['privacy_findings'](data,needles),'Delivered privacy failure')
    log=dict(items=details,cross_item_pairs=pairs,package_hashes={p:sha(d) for p,d in sorted(delivered.items())},summary=dict(items=len(items),files=len(delivered),bytes=sum(map(len,delivered.values())),implementation_files=sum('/impl/' in p for p in delivered),contract_files=sum('/contract/' in p for p in delivered),cross_item_flagged=sum(i['cross_item_flag'] for i in items),excluded_cross_files=sum(len(p['excluded']) for p in pairs),retained_cross_locators=sum(len(p['retained_own_locators']) for p in pairs),projected_files=sum(f['projection'] for d in details for f in d['files'].values()),redacted_files=sum(f['redacted'] for d in details for f in d['files'].values())),assertions=dict(parent_provenance=True,whole_implementation_files=True,own_child_content=True,message_scan=True,cross_item_exclusion_with_locator_exception=True,privacy_and_auth_fixture_values=True,history_literals=True,verbatim_propositions=True,forbidden_words=True,implementation_cap=True))
    return delivered,cb(KEY_COLUMNS,keys),log,keys

def package_hash(hashes):
    return sha(jb(hashes))

def publish(files,key_bytes,log,output=OUT,key_dir=KEY,replace=False):
    output=Path(output);key_dir=Path(key_dir)
    destinations=[output,key_dir/'e7_key.csv',key_dir/'build_log.json']
    if not replace:absent(destinations)
    if replace:
        require(output.is_dir(),'Replacement requires an existing package')
        previous={p.relative_to(output).as_posix():sha(p.read_bytes()) for p in output.rglob('*') if p.is_file()}
        prior_log=json.loads((key_dir/'build_log.json').read_text()) if (key_dir/'build_log.json').exists() else {}
        log['replacement_history']=prior_log.get('replacement_history',[])+[dict(explicit_replace=True,old_package_sha256=package_hash(previous),old_files=len(previous),old_build_log_sha256=sha((key_dir/'build_log.json').read_bytes()) if (key_dir/'build_log.json').exists() else None,new_package_sha256=package_hash(log['package_hashes']))]
    with tempfile.TemporaryDirectory(prefix='.build-stage-',dir=HERE) as temporary:
        stage=Path(temporary)/'package';stage.mkdir()
        for rel,data in sorted(files.items()):
            O['safe_path'](rel);p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        require({p.relative_to(stage).as_posix():sha(p.read_bytes()) for p in stage.rglob('*') if p.is_file()}==log['package_hashes'],'Staged hashes differ')
        if replace:
            backup=Path(temporary)/'previous-package';output.rename(backup)
            try:stage.rename(output)
            except BaseException:
                backup.rename(output);raise
            (key_dir/'e7_key.csv').write_bytes(key_bytes)
            (key_dir/'build_log.json').write_bytes(jb(log))
        else:
            absent(destinations);output.mkdir()
            for child in stage.iterdir():child.rename(output/child.name)
            with (key_dir/'e7_key.csv').open('xb') as f:f.write(key_bytes)
            with (key_dir/'build_log.json').open('xb') as f:f.write(jb(log))

def inputs():
    new=json.loads((KEY/'new_accepted.json').read_text())
    for r in new:r.update(source_task='T45')
    if (KEY/'new_accepted2.json').exists():
        extra=json.loads((KEY/'new_accepted2.json').read_text())
        for r in extra:r.update(source_task='T46')
        new+=extra
    old=list(csv.DictReader((HERE.parent/'E6_realfix/combined_accepted.csv').open()))
    require(len(old)==25,'Exploratory input count differs')
    for r in old:r.update(set='e6_exploratory',helper_paths=[])
    dedup=set()
    for r in old+new:
        k=r['repo'],r['operation'],r['fix_family'];require(k not in dedup,'Duplicate repo/operation/family');dedup.add(k)
        require(r['truth_direction'] in {'SPEC','IMPL','BOTH'},'Invalid recorded direction')
    return new+old

def main():
    p=argparse.ArgumentParser();p.add_argument('--audit-only',action='store_true');p.add_argument('--replace',action='store_true');args=p.parse_args()
    require(not(args.audit_only and args.replace),'Audit and replacement are separate actions')
    if not args.audit_only and not args.replace:absent([OUT,KEY/'e7_key.csv',KEY/'build_log.json',KEY/'accepted_full.csv'])
    salt_path=KEY/'shuffle_salt.txt'
    if args.replace:
        require((KEY/'t45_snapshot/shuffle_salt.txt').exists(),'Prior salt snapshot required')
        salt=secrets.token_hex(32)
        require(salt!=salt_path.read_text().strip(),'New salt must differ')
    elif not salt_path.exists():
        with salt_path.open('x') as f:f.write(secrets.token_hex(32)+'\n')
        salt=salt_path.read_text().strip()
    else:salt=salt_path.read_text().strip()
    rows=inputs();fixtures=sorted(O['AUTH'].glob('*.yaml'));needles=O['fixture_needles'](fixtures)
    files,key,log,full=prepare(rows,M['REPOS'],salt,needles)
    log['auth_fixtures']=len(fixtures);log['auth_value_variants']=len(O['variants'](needles))
    log['input_hashes']={str(p):sha(p.read_bytes()) for p in [Path(__file__),KEY/'new_accepted.json',HERE.parent/'E6_realfix/combined_accepted.csv',salt_path]}
    log['input_hashes'][str(salt_path)]=sha((salt+'\n').encode())
    if (KEY/'new_accepted2.json').exists():log['input_hashes'][str(KEY/'new_accepted2.json')]=sha((KEY/'new_accepted2.json').read_bytes())
    if args.audit_only:
        with (KEY/'build_preflight.json').open('wb') as f:f.write(jb(log))
    else:
        publish(files,key,log,replace=args.replace)
        if args.replace:salt_path.write_text(salt+'\n')
        columns=list(dict.fromkeys(KEY_COLUMNS+[k for r in full for k in r]))
        normalized=[{k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in full]
        with (KEY/'accepted_full.csv').open('wb' if args.replace else 'xb') as f:f.write(cb(columns,normalized))
    print(json.dumps(dict(audit_only=args.audit_only,**log['summary'])))

if __name__=='__main__':main()
