"""Index physical log lines; do not write request URLs, credentials, or messages."""
import collections
import json
import re
from urllib.parse import parse_qs,urlsplit
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay import OUT,ROOT,RUNS

def request_key(method,path,query,status):
    return (method,path,tuple(sorted((k,tuple(v)) for k,v in query.items())),int(status))

def main():
    for sut,rel in RUNS.items():
        run=ROOT/rel;xs=[json.loads(s) for s in (run/'exchanges.jsonl').open()]
        lines=(run/'compose.log').read_bytes().decode().split('\n')
        queues=collections.defaultdict(collections.deque);count=0
        for n,line in enumerate(lines,1):
            m=re.search(r'"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS) (\S+) HTTP/[12](?:\.[01])?" (\d{3}) ',line)
            if m and line.startswith('sut-'):
                url=urlsplit(m[2]);queues[request_key(m[1],url.path,parse_qs(url.query,keep_blank_values=True),m[3])].append(n);count+=1
        mapping={}
        for n,x in enumerate(xs,1):
            r=x['request'];key=request_key(r['method'],r['path'],r.get('query',{}),x['response']['status'])
            if queues[key]:mapping[str(n)]={'access_line':queues[key].popleft()}
        if sut=='market':
            error_queues=collections.defaultdict(collections.deque)
            warn_queues=collections.defaultdict(collections.deque)
            for n,line in enumerate(lines,1):
                if line.startswith('sut-market-1') and 'WARN' in line and 'RestExceptionHandler' in line:
                    path=re.search(r'uri=([^,\s\'"}]+)',line)
                    if path:warn_queues[path[1]].append(n)
                if not line.startswith('sut-market-1') or 'ERROR' not in line:continue
                block=[]
                for j in range(n-1,min(n+12,len(lines))):
                    if lines[j].startswith('sut-market-1'):block.append(lines[j])
                combined='\n'.join(block)
                path=re.search(r'uri=([^,\s\'"}]+)',combined)
                if not path:continue
                if '_links' in combined:category='HAL_links_binding'
                elif 'quantity' in combined:category='quantity_int32_overflow'
                elif 'NumberFormatException' in combined:category='path_int64_overflow'
                else:raise AssertionError(('unclassified market log',n))
                frames=[]
                for j in range(n,min(n+35,len(lines))):
                    m=re.search(r'\bat ([\w.$]+)\(([^()]*)\)',lines[j])
                    if m:frames.append({'line':j+1,'symbol':m[1],'source':m[2]})
                error_queues[(path[1],category)].append({'error_line':n,'frames':frames[:6]})
            for n,x in enumerate(xs,1):
                if x['response']['status'] in (401,404,406) and warn_queues[x['request']['path']]:
                    mapping.setdefault(str(n),{})['validation_or_notfound_line']=warn_queues[x['request']['path']].popleft()
                if x['response']['status']!=500:continue
                msg=json.loads(x['response']['body']['text'])['message']
                category='HAL_links_binding' if '_links' in msg else ('quantity_int32_overflow' if 'quantity' in msg else 'path_int64_overflow')
                key=(x['request']['path'],category)
                assert error_queues[key],(n,category)
                mapping.setdefault(str(n),{}).update(error_queues[key].popleft())
            assert sum(map(len,error_queues.values()))==0
        else:
            # Mitmproxy's URI display is truncated. Its own ordered request/response
            # stream can still locate a representative complete URI per operation.
            pending=None; pairs=[]; prefix_pairs=[]
            for n,line in enumerate(lines,1):
                if not line.startswith('mitmproxy-1'):continue
                m=re.search(r'\| [^ ]+:\d+: (GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD) (http://\S+)',line)
                if m:
                    url=urlsplit(m[2]);pending=(m[1],url.path,parse_qs(url.query,keep_blank_values=True),n,'\u2026' in m[2])
                m=re.search(r'\|\s+<< (\d{3})\b',line)
                if m and pending:
                    method,path,query,start,truncated=pending
                    prefix_pairs.append((method,path,int(m[1]),start,n,truncated))
                    if not truncated:pairs.append((request_key(method,path,query,m[1]),start,n))
                    pending=None
            proxy=collections.defaultdict(collections.deque)
            for key,a,b in pairs:proxy[key].append((a,b))
            for n,x in enumerate(xs,1):
                r=x['request'];key=request_key(r['method'],r['path'],r.get('query',{}),x['response']['status'])
                if proxy[key]:
                    a,b=proxy[key].popleft();mapping.setdefault(str(n),{}).update({'proxy_request_line':a,'proxy_response_line':b})
            for n,x in enumerate(xs,1):
                if str(n) in mapping:continue
                r=x['request'];candidates=[]
                for method,path,status,a,b,truncated in prefix_pairs:
                    if method!=r['method'] or status!=x['response']['status']:continue
                    prefix=path.split('\u2026',1)[0]
                    if r['path']==path or (truncated and r['path'].startswith(prefix)):
                        candidates.append((len(prefix),a,b))
                if candidates:
                    _,a,b=max(candidates,key=lambda v:v[0])
                    mapping[str(n)]={'prefix_corroboration_request_line':a,'prefix_corroboration_response_line':b,
                                     'scope':'operation/status and displayed URI prefix; not an exact exchange join'}
        (OUT/f'{sut}_log_locations.json').write_text(json.dumps(mapping,indent=2)+'\n')
        print(json.dumps({'sut':sut,'access_lines':count,'mapped_exchanges':len(mapping),
                          'error_joins':sum('error_line' in r for r in mapping.values())}))

if __name__=='__main__':main()
