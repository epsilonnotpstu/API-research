"""Execute only the authorized reviewed harness, retaining each outcome."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from progress import update

ROOT = Path.cwd()
SCRATCH = ROOT / '09_collab/logs/T12_scratch'
RUNS = ROOT / '08_experiments/E1_pilot/runs/scout-api'
HARNESS = ROOT / '08_experiments/E1_pilot/harness'
SPEC = ROOT / '08_experiments/_external/emb/openapi-swagger/scout-api.json'
ENV = dict(os.environ, MAX_EXAMPLES='100', HEALTH_PATH='/admin/healthcheck', BASE_PATH='/api', PYTHONDONTWRITEBYTECODE='1')
TOOLS = ROOT / '08_experiments/tools'
SNAPSHOT = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in TOOLS.glob('*.py')}
(SCRATCH / 'batch_tool_sha256.json').write_text(json.dumps(SNAPSHOT, indent=2) + '\n')


def check_tools():
    current = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in TOOLS.glob('*.py')}
    if current != SNAPSHOT:
        raise RuntimeError('Tools changed during batch; refusing incompatible collection')


def record(value):
    with (SCRATCH / 'batch_events.jsonl').open('a') as output:
        output.write(json.dumps(value) + '\n')
    print(json.dumps(value), flush=True)


def run(mode, fault, seed):
    check_tools()
    before = set(RUNS.iterdir())
    log = SCRATCH / f'{mode}_{fault}_s{seed}.log'
    command = [str(HARNESS / 'run_pilot.sh'), 'scout-api', str(SPEC), mode, fault, '0' if mode == 'baseline' else '30', str(seed), '600']
    start = time.monotonic()
    with log.open('w') as output:
        result = subprocess.run(command, env=ENV, stdout=output, stderr=subprocess.STDOUT)
    new = sorted(set(RUNS.iterdir()) - before)
    if len(new) != 1:
        record({'stage': 'run', 'command': command, 'exit': result.returncode, 'run_candidates': [str(p) for p in new], 'log': str(log.relative_to(ROOT))})
        return None
    directory = new[0]
    meta = json.loads((directory / 'run.json').read_text())
    value = {'stage': 'run', 'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'run_id': directory.name, 'mode': mode, 'fault': fault, 'seed': seed, 'elapsed_seconds': round(time.monotonic() - start, 3), 'exit': result.returncode, 'complete': meta['complete'], 'schemathesis_exit': meta['schemathesis_exit'], 'log': str(log.relative_to(ROOT))}
    record(value)
    update('IN PROGRESS (batch)', f"{directory.name}: harness exit {result.returncode}, Schemathesis exit {meta['schemathesis_exit']}, complete={meta['complete']}; evidence: logs/T12_scratch/batch_events.jsonl, E1_pilot/runs/scout-api/{directory.name}/run.json.")
    check_tools()
    return directory


if __name__ == '__main__':
    with (SCRATCH / 'prepare_dist.log').open('w') as output:
        prepared = subprocess.run([str(HARNESS / 'prepare_dist.sh'), 'scout-api'], env=ENV, stdout=output, stderr=subprocess.STDOUT)
    record({'stage': 'prepare_dist', 'exit': prepared.returncode, 'log': '09_collab/logs/T12_scratch/prepare_dist.log'})
    if prepared.returncode:
        raise SystemExit(prepared.returncode)
    baseline = None
    for seed in (1, 2, 3):
        directory = run('baseline', 'NONE', seed)
        if seed == 1:
            baseline = directory
    for fault in ('REQUEST_LOOSE', 'REQUEST_STRICT', 'RESPONSE_ORACLE', 'METHOD_SEM'):
        directory = run('mutated', fault, 1)
        if directory is not None and baseline is not None:
            log = SCRATCH / f'analyse_{fault}.log'
            with log.open('w') as output:
                result = subprocess.run([str(HARNESS / 'analyse_run.sh'), str(directory), str(baseline), '--mode', 'both'], env=ENV, stdout=output, stderr=subprocess.STDOUT)
            record({'stage': 'analysis', 'fault': fault, 'run_id': directory.name, 'baseline_id': baseline.name, 'exit': result.returncode, 'log': str(log.relative_to(ROOT))})
    check_tools()
    record({'stage': 'batch_finished', 'tools_unchanged': True})
    update('IN PROGRESS (analysis)', 'Seven planned conditions attempted; outcomes and analysis exits: logs/T12_scratch/batch_events.jsonl. Tools unchanged against logs/T12_scratch/batch_tool_sha256.json. Statistical summaries/report next.')
