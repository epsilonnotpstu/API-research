#!/usr/bin/python3
"""Mechanical routes and bounded OpenAPI projections; no semantic judgement."""
from copy import deepcopy
import json
import posixpath
import re
from urllib.parse import unquote
import yaml

METHODS = {'get','post','put','delete','patch','head','options','trace'}
LIMIT = 2000

class ContractError(Exception):
    pass

def load(raw):
    try:
        obj = json.loads(raw)
    except (ValueError, UnicodeError):
        try:
            obj = yaml.safe_load(raw)
        except Exception:
            raise ContractError('Unsupported contract syntax; contents suppressed') from None
    if not isinstance(obj, (dict, list)):
        raise ContractError('Non-container contract; contents suppressed')
    def normalize(value):
        if isinstance(value,dict):return {str(k):normalize(v) for k,v in value.items()}
        if isinstance(value,list):return [normalize(v) for v in value]
        if value is None or isinstance(value,(str,int,float,bool)):return value
        return str(value)
    return normalize(obj)

def encoded(obj):
    # JSON is valid YAML 1.2. The repository-relative filename is preserved.
    return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()

def references(obj):
    out = []
    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get('$ref'), str):
                out.append(value['$ref'])
            for child in value.values():walk(child)
        elif isinstance(value, list):
            for child in value:walk(child)
    walk(obj)
    return out

def parts(fragment):
    return tuple(unquote(s).replace('~1','/').replace('~0','~') for s in fragment.lstrip('/').split('/')) if fragment else ()

def at(obj, pointer):
    for key in pointer:
        try:obj = obj[int(key)] if isinstance(obj,list) else obj[key]
        except (KeyError, IndexError, ValueError, TypeError):
            raise ContractError('Missing reference target; contents suppressed') from None
    return obj

def insert(dest, source, pointer):
    # A pointer into a sequence retains that sequence as one complete node.
    cursor=source
    for i,key in enumerate(pointer):
        if isinstance(cursor,list):
            pointer=pointer[:i]
            break
        cursor=cursor[key]
    if not pointer:
        return deepcopy(source)
    cursor = dest
    for key in pointer[:-1]:
        cursor = cursor.setdefault(key, {})
    cursor[pointer[-1]] = deepcopy(at(source, pointer))
    return dest

def canonical(path):
    path = path.split('?',1)[0]
    path = re.sub(r'\{[^}]+\}|:[A-Za-z_]\w*|<[^>]+>', '{}', path)
    return '/' + '/'.join(p for p in path.split('/') if p)

def annotation_tokens(text):
    result = []
    for match in re.finditer(r'@([\w.]+)\b', text):
        start = match.end()
        while start < len(text) and text[start].isspace():start += 1
        end = start
        args = ''
        if start < len(text) and text[start] == '(':
            depth = 0; quote = None; escaped = False
            for end in range(start, len(text)):
                c = text[end]
                if quote:
                    if escaped:escaped = False
                    elif c == '\\':escaped = True
                    elif c == quote:quote = None
                elif c in {'\"', "'"}:quote = c
                elif c == '(':depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:break
            else:continue
            args = text[start+1:end];end += 1
        result.append((match.start(), end, match[1].split('.')[-1], args))
    return result

def values(args):
    # Only value/path arguments are routes; media types/names are never paths.
    named = re.search(r'\b(?:value|path)\s*=\s*(\{[^}]*\}|\[[^]]*\]|\"[^\"]*\")', args)
    subject = named[1] if named else args.split(',',1)[0] if not re.match(r'\s*\w+\s*=',args) else ''
    result = re.findall(r'\"([^\"]*)\"',subject)
    return [v for v in result if not v or v.startswith('/')] or ['']

def routes(sources):
    result = set()
    spring = {'GetMapping':'get','PostMapping':'post','PutMapping':'put','DeleteMapping':'delete','PatchMapping':'patch',
              'GetExchange':'get','PostExchange':'post','PutExchange':'put','DeleteExchange':'delete','PatchExchange':'patch'}
    for path, raw in sources:
        text = raw.decode('utf-8','replace')
        if path.endswith('.go'):
            for match in re.finditer(r'(?im)^\s*//\s*@Router\s+(\S+)\s+\[(\w+)\]',text):
                if match[2].lower() in METHODS:result.add((match[2].lower(),canonical(match[1])))
            for match in re.finditer(r'(?im)^\s*//\s*swagger:route\s+(\w+)\s+(\S+)',text):
                if match[1].lower() in METHODS:result.add((match[1].lower(),canonical(match[2])))
            for match in re.finditer(r'\.(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|Get|Post|Put|Delete|Patch|Head|Options)\s*\(\s*\"([^\"]*)\"',text):
                result.add((match[1].lower(),canonical(match[2])))
            for match in re.finditer(r'\.(?:Handle|HandleFunc)\s*\(\s*\"([^\"]*)\"[^\n;]*?\.Methods\s*\(\s*\"([A-Z]+)\"',text):
                if match[2].lower() in METHODS:result.add((match[2].lower(),canonical(match[1])))
            continue
        tokens = annotation_tokens(text)
        declaration = re.search(r'\b(?:class|interface|object)\s+\w+',text)
        boundary = declaration.start() if declaration else 0
        prefixes = ['']
        for start,end,name,args in tokens:
            if start < boundary and name in {'Path','RequestMapping'}:
                prefixes = values(args)
        for i,(start,end,name,args) in enumerate(tokens):
            if start < boundary:continue
            if name in spring or name == 'RequestMapping':
                methods = [spring[name]] if name in spring else [m.lower() for m in re.findall(r'RequestMethod\.(\w+)',args)]
                for method in methods:
                    if method not in METHODS:continue
                    for prefix in prefixes:
                        for value in values(args):result.add((method,canonical(prefix+'/'+value)))
            if name.lower() in METHODS and name.upper() == name:
                # Contiguous annotation groups only: do not cross method bodies.
                group = [tokens[i]]
                j=i-1
                while j>=0 and not text[tokens[j][1]:group[0][0]].strip():
                    group.insert(0,tokens[j]);j-=1
                j=i+1
                while j<len(tokens) and not text[group[-1][1]:tokens[j][0]].strip():
                    group.append(tokens[j]);j+=1
                segments = [v for _,_,n,a in group if n=='Path' for v in values(a)] or ['']
                for prefix in prefixes:
                    for segment in segments:result.add((name.lower(),canonical(prefix+'/'+segment)))
    return result

def operations(obj):
    if not isinstance(obj,dict) or not isinstance(obj.get('paths',{}),dict):return []
    return [(method,path) for path,entry in obj.get('paths',{}).items() if isinstance(entry,dict)
            for method in entry if method in METHODS]

def matched_operations(obj, mapped):
    result = set()
    ops = operations(obj)
    for method, route in mapped:
        direct = [(m,p) for m,p in ops if m==method and canonical(p)==route]
        if direct:result.update(direct);continue
        suffix = [(m,p) for m,p in ops if m==method and (canonical(p).endswith(route) or route.endswith(canonical(p)))]
        if len(suffix)==1:result.update(suffix)
    return sorted(result,key=lambda x:(x[1].encode(),x[0].encode()))

def projected_root(source, selected):
    result = {k:deepcopy(v) for k,v in source.items() if k in {
        'openapi','swagger','info','servers','host','basePath','schemes','consumes','produces','security','securityDefinitions'}}
    if isinstance(source.get('components'),dict) and 'securitySchemes' in source['components']:
        result['components']={'securitySchemes':deepcopy(source['components']['securitySchemes'])}
    result['paths'] = {}
    for method,path in selected:
        entry = source['paths'][path]
        dest = result['paths'].setdefault(path,{})
        for key in ['parameters','servers','$ref']:
            if key in entry:dest[key]=deepcopy(entry[key])
        dest[method]=deepcopy(entry[method])
    return result

def closure(root_path, initial, get):
    source = {root_path:get(root_path)}
    output = {root_path:initial}
    pending = [root_path]
    seen = set()
    external = 0
    while pending:
        path = pending.pop(0)
        for ref in references(output[path]):
            if (path,ref) in seen:continue
            seen.add((path,ref))
            filename,_,fragment = ref.partition('#')
            if re.match(r'^[\w+.-]+:',filename):
                external += 1;continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(path),unquote(filename))) if filename else path
            if target.startswith('../') or target.startswith('/') or '\\' in target:
                raise ContractError('Reference leaves contract tree')
            if target not in source:source[target]=get(target)
            # Empty fragment means the complete external document.
            pointer = parts(fragment)
            existing = output.get(target,{})
            if pointer:
                value = at(source[target],pointer)
                try:already = at(existing,pointer)==value
                except ContractError:already=False
                if already:continue
                output[target]=insert(existing,source[target],pointer)
            else:
                output[target]=deepcopy(source[target])
            pending.append(target)
    return output, external

def build(root_paths, blob, mapped):
    cache = {}
    def get(path):
        if path not in cache:
            raw = blob(path)
            if raw is None:raise ContractError('Missing local contract reference')
            cache[path]=load(raw)
        return cache[path]
    output = {}
    modes = []
    remote = 0
    bounded_targets = set()
    mapped_targets = set()
    for path in sorted(root_paths,key=lambda p:p.encode()):
        source=get(path)
        if not isinstance(source,dict):raise ContractError('Non-mapping root contract')
        selected=matched_operations(source,mapped)
        if selected:
            files,count=closure(path,projected_root(source,selected),get)
            mode='mapped_operations'
        else:
            files,count=closure(path,deepcopy(source),get)
            mode='whole_document'
            if any(len(encoded(v).splitlines())>LIMIT for v in files.values()):
                selected=[]
                for op in sorted(operations(source),key=lambda x:(x[1].encode(),x[0].encode())):
                    trial,trial_count=closure(path,projected_root(source,selected+[op]),get)
                    if all(len(encoded(v).splitlines())<=LIMIT for v in trial.values()):
                        selected.append(op);files,count=trial,trial_count
                    else:
                        # Byte-order prefix, independent of operation contents.
                        break
                if not selected:
                    raise ContractError('No complete operation closure fits the fallback line bound')
                mode='bounded_document_prefix'
        if mode!='mapped_operations' and any(len(encoded(v).splitlines())>LIMIT for v in files.values()):
            raise ContractError('Contract reference closure exceeds line bound')
        if mode=='mapped_operations':mapped_targets.update(files)
        else:bounded_targets.update(files)
        remote += count
        modes.append(dict(path=path,mode=mode,operations=len(selected)))
        for target,obj in files.items():
            if target in output:
                # Unite projections of shared fragments; never lose ref closure.
                def merge(a,b):
                    if isinstance(a,dict) and isinstance(b,dict):
                        result=deepcopy(a)
                        for k,v in b.items():result[k]=merge(result[k],v) if k in result else deepcopy(v)
                        return result
                    return deepcopy(b)
                output[target]=merge(output[target],obj)
            else:output[target]=obj
    if any(len(encoded(output[p]).splitlines())>LIMIT for p in bounded_targets-mapped_targets):
        raise ContractError('Combined contract projection exceeds line bound')
    return {p:encoded(v) for p,v in output.items()}, modes, remote
