"""Index saved spec nodes and proxy request/response lines for review."""
import bisect
import collections
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RUN = ROOT / '08_experiments/E1_pilot/runs/scout-api/20261113T202103Z_baseline_NONE_p0_s1_1642810'
source = (RUN / 'spec.original.json').read_text()
newlines = [-1] + [m.start() for m in re.finditer('\n', source)]
decoder = json.JSONDecoder()
locations = {}

def scan(pos, pointer):
    while source[pos].isspace():
        pos += 1
    locations[pointer] = bisect.bisect_left(newlines, pos)
    token = source[pos]
    if token not in '{[':
        return decoder.raw_decode(source, pos)[1]
    is_object = token == '{'
    pos += 1
    index = 0
    while True:
        while source[pos].isspace() or source[pos] == ',':
            pos += 1
        if source[pos] in '}]':
            return pos + 1
        if is_object:
            key, pos = decoder.raw_decode(source, pos)
            while source[pos].isspace() or source[pos] == ':':
                pos += 1
            key = key.replace('~', '~0').replace('/', '~1')
        else:
            key = str(index)
        pos = scan(pos, pointer + '/' + key)
        index += 1

scan(0, '')
(OUT / 'spec_locations.json').write_text(json.dumps(locations, indent=2) + '\n')

def key(method, path, query):
    return json.dumps([method, path, sorted((k, tuple(v)) for k, v in query.items())], ensure_ascii=True)

proxy = []
access = []
pending = None
log_lines = (RUN / 'compose.log').read_bytes().decode('utf-8').split('\n')
for n, line in enumerate(log_lines, 1):
    access_match = re.search(r'"(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD) (\S+) HTTP/1\.[01]" (\d{3}) ', line)
    if line.startswith('sut-scout-api-1') and access_match:
        url = urlsplit(access_match[2])
        access.append({'key': key(access_match[1], url.path, parse_qs(url.query, keep_blank_values=True)),
                       'status': int(access_match[3]), 'access_log_line': n})
    if not line.startswith('mitmproxy-1'):
        continue
    match = re.search(r'\| [^ ]+:\d+: (GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD) (http://\S+)', line)
    if match:
        url = urlsplit(match[2])
        pending = {'key': key(match[1], url.path, parse_qs(url.query, keep_blank_values=True)),
                   'request_log_line': n}
        continue
    match = re.search(r'\|\s+<< (\d{3})\b', line)
    if match and pending:
        proxy.append({**pending, 'status': int(match[1]), 'response_log_line': n})
        pending = None

queues = collections.defaultdict(collections.deque)
for pair in access:
    queues[(pair['key'], pair['status'])].append(pair)
mapping = {}
missing = []
for n, raw in enumerate((RUN / 'exchanges.jsonl').open(), 1):
    x = json.loads(raw)
    req = x['request']
    k = (key(req['method'], req['path'], req['query']), int(x['response']['status']))
    if queues[k]:
        mapping[str(n)] = queues[k].popleft()
    else:
        missing.append(n)
(OUT / 'request_log_map.json').write_text(json.dumps(mapping, indent=2, ensure_ascii=True) + '\n')
summary = {'proxy_pairs': len(proxy), 'access_lines': len(access), 'matched_exchanges': len(mapping), 'missing_exchanges': missing}
(OUT / 'request_log_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({**summary, 'missing_exchanges': len(missing)}))
