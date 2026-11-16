from pathlib import Path
import runpy,re,json
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'));B=runpy.run_path(str(Path(__file__).parents[1]/'build.py'))
n=R['next_row']();R['require_current'](n);R['record_preview'](n,'parent common-error handler and operation linkage inspection')
git=R['M']['git'];rev=n['parent_commit'];text=git('harbor','show',rev+':api/v2.0/swagger.yaml').decode();lines,nodes=B['yaml_nodes'](text)
paths=git('harbor','ls-tree','-r','--name-only',rev).decode().splitlines()
functions={}
for path in paths:
 if not re.match(r'^src/server/v2.0/handler/[^/]+\.go$',path) or path.endswith('_test.go'):continue
 source=git('harbor','show',rev+':'+path).decode()
 starts=list(re.finditer(r'^func \([^)]*\) (\w+)\(',source,re.M))
 for i,m in enumerate(starts):
  body=source[m.start():starts[i+1].start() if i+1<len(starts) else len(source)]
  if '.SendError(ctx, err)' in body:functions.setdefault(m[1],[]).append(path)
def reaches_errors(ptr,seen=None):
 seen=set() if seen is None else seen
 if ptr in seen:return False
 seen.add(ptr)
 if ptr==('definitions','Errors'):return True
 if ptr not in nodes:return False
 a,b=nodes[ptr]
 for ref in B['references'](''.join(lines[a:b]).encode()):
  if ref.startswith('#/') and reaches_errors(B['pointer_parts'](ref[1:]),seen):return True
 return False
valid=[]
for ptr,(a,b) in nodes.items():
 if len(ptr)!=3 or ptr[0]!='paths' or ptr[2] not in {'get','post','put','patch','delete'}:continue
 body=''.join(lines[a:b]);m=re.search(r'operationId:\s*(\w+)',body)
 if not m or not reaches_errors(ptr):continue
 name=next((name for name in functions if name.lower()==m[1].lower()),None)
 if not name or len(functions[name])!=1:continue
 op=ptr[2].upper()+' '+ptr[1];handler=functions[name][0]
 valid.append(dict(operation=op,operation_id=m[1],function=name,handler=handler))
for v in valid:
 R['accept']('harbor',178,v['operation'],
  'documented error responses use a top-level Errors array',
  'send an object containing an errors array through the shared error responder',
  'SPEC','openapi','response_shape.shared-error-envelope',
  [('api/v2.0/swagger.yaml',r'^    Errors:|^  Errors:|operationId: '+re.escape(v['operation_id'])+r'\b')],
  [(v['handler'],r'func .*\) '+re.escape(v['function'])+r'\(|SendError\(ctx, err\)'),('src/server/v2.0/handler/base.go',r'lib_http.SendError|return NewErrResponder'),('src/lib/http/error.go',r'errors.NewErrs\(err\).Error'),('src/lib/errors/errors.go',r'json:"errors,omitempty"')])
R['private_json'](R['KEY']/'t49_error_envelope_operation_audit.json',dict(verified_operations=valid,selection='ascending UTF-8 operation bytes only'))
print('Verified operations:',len(valid))
print('Accepted/capped:',R['finish_accept']('Parent shared Errors schema is an array; linked handlers serialize an object containing errors; patch corrects that common response shape.'))
