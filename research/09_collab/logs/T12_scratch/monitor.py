"""Read local pilot artifacts without issuing Docker commands."""
from pathlib import Path
import collections
import datetime
import json

root = Path('08_experiments/E1_pilot/runs/scout-api')
run = sorted(root.iterdir())[-1]
meta = json.loads((run / 'run.json').read_text())
path = run / 'exchanges.jsonl'
exchanges = []
if path.exists():
    for line in path.read_text().splitlines():
        try:
            exchanges.append(json.loads(line))
        except json.JSONDecodeError:
            pass
response = [e for e in exchanges if e.get('response')]
result = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'run_id': run.name,
          'phase': meta['phase'], 'complete': meta['complete'], 'harness_exit': meta['harness_exit'],
          'exchanges_so_far': len(exchanges),
          'status_so_far': dict(collections.Counter(str(e['response']['status']) for e in response)),
          'method_paths_so_far': len({(e['request']['method'], e['request']['path']) for e in exchanges})}
with Path('09_collab/logs/T12_scratch/monitor.jsonl').open('a') as output:
    output.write(json.dumps(result) + '\n')
print(json.dumps(result))
log = run / 'schemathesis.log'
if log.exists():
    print('\n'.join(log.read_text(errors='replace').splitlines()[-4:]))
