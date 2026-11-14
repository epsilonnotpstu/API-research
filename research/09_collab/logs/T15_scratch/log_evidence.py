"""Join HTTP error IDs to saved stack traces without executing the SUT."""
import collections
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RUN = ROOT / '08_experiments/E1_pilot/runs/scout-api/20261113T202103Z_baseline_NONE_p0_s1_1642810'
# Count physical LF-delimited lines, matching rg/nl; generated Unicode/control
# characters in logged request data must not create artificial line numbers.
logs = (RUN / 'compose.log').read_bytes().decode('utf-8').split('\n')
starts = {}
for n, line in enumerate(logs, 1):
    match = re.search(r'Error handling a request: ([0-9a-f]+)', line)
    if match:
        starts[match[1]] = n
records = []
for item in json.loads((OUT / 'exchange_map.json').read_text()):
    errors = []
    grouped = collections.defaultdict(list)
    for sample in item['response_signatures']:
        match = re.search(r'logged \(ID ([0-9a-f]+)\)', sample['response_error'].get('message', ''))
        if not match:
            continue
        start = starts[match[1]]
        stack = []
        for n in range(start, min(start + 130, len(logs))):
            line = logs[n]
            if 'sut-scout-api-1' not in line:
                continue
            if ' | ! ' not in line:
                break
            stack.append((n + 1, line.split(' | ! ', 1)[1]))
        exceptions = [(n, line) for n, line in stack if not line.startswith('at ') and not line.startswith('...')]
        frames = [(n, line) for n, line in stack if 'at se.devscout.' in line]
        key = ' / '.join([e[1] for e in exceptions[:2]] + [f[1] for f in frames[:2]])
        grouped[key].append(sample['line'])
        errors.append({'exchange_line': sample['line'], 'log_line': start,
                       'exceptions': exceptions, 'project_frames': frames})
    if errors:
        records.append({'item_id': item['item_id'], 'errors': errors,
                        'groups': [{'signature': sig, 'count': len(lines), 'exchange_lines': lines}
                                   for sig, lines in grouped.items()]})
(OUT / 'log_map.json').write_text(json.dumps(records, indent=2, ensure_ascii=True) + '\n')
for item in records:
    print(item['item_id'], 'error IDs', len(item['errors']), 'types', len(item['groups']))
    for g in item['groups']:
        e = next(e for e in item['errors'] if e['exchange_line'] == g['exchange_lines'][0])
        print(' ',g['count'],'EX',e['exchange_line'],'LOG',e['log_line'],ascii(g['signature'])[:450])
