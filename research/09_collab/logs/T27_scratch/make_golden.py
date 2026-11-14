"""Capture synthetic golden argv from the original, unmodified shell statements."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
LIVE = ROOT / '08_experiments/E1_pilot/harness_v2'
STAGE = Path(__file__).resolve().parent / 'staged/harness_v2'
source = (LIVE / 'run_pilot.sh').read_text()
begin = source.index('schema_cmd=(run ')
end = source.index('# mount the run directory', begin)
builder = source[begin:end]
begin = source.index('schema_cmd[1]=')
end = source.index('metadata pending\nset +e', begin)
recorder = source[begin:end]
cases = []
for name, updates in (
    ('default-scout', {}),
    ('default-explicit', {'FUZZER': 'schemathesis'}),
    ('root-custom-checks', {'BASE_PATH': '/', 'SCHEMA_CHECKS': 'not_a_server_error', 'seed': '0'}),
    ('petstore-positive-auth', {'BASE_PATH': '/api/v3', 'DATA_GEN': 'positive', 'AUTH_HEADER': 'X-Test: synthetic-t27'}),
    ('negative', {'DATA_GEN': 'negative'}),
    ('all-custom-timeout', {'DATA_GEN': 'all', 'REQUEST_TIMEOUT_MS': '123', 'MAX_EXAMPLES': '5'}),
):
    values = {'PATH': os.environ['PATH'], 'BASE_PATH': '/api', 'SCHEMA_CHECKS': 'all', 'seed': '7',
              'MAX_EXAMPLES': '100', 'REQUEST_TIMEOUT_MS': '10000', 'PILOT_HYPOTHESIS_PHASES': 'explicit,generate',
              'AUTH_HEADER': '', 'test_spec': '/synthetic/spec.test.json'}
    values.update(updates)
    with tempfile.TemporaryDirectory(prefix='t27-golden-') as directory:
        values['run_dir'] = directory
        result = subprocess.run(['bash', '-euc', builder + recorder + '\nprintf "%s\\0" "${schema_cmd[@]}"'],
                                env=values, capture_output=True, check=True)
        argv = result.stdout.decode().removesuffix('\0').split('\0')
        recorded = (Path(directory) / 'schemathesis-argv.txt').read_text().splitlines()
    cases.append({'name': name, 'environment': updates, 'argv': argv, 'recorded': recorded})

fragments = {}
for name, start, end in (
    ('default-docker-argv', 'timeout --signal=INT --kill-after=20 "${budget}s" docker run', '>"$run_dir/schemathesis.log"'),
    ('default-image-and-help', '# A registry/DNS outage', '\ndone'),
    ('readiness-and-quarantine', '# Probe through the proxy', 'phase=generation'),
    ('cleanup-and-coverage', 'finish() {', '    metadata "$rc"'),
    ('mutation-candidate-pool', '    # Optional candidate pool', 'cp "$test_spec"'),
    ('default-derecursion', '# mount the run directory', 'schema_cmd[1]='),
    ('default-exit-semantics', '# Exit 1 includes test failures;', '\nesac'),
):
    begin = source.index(start)
    stop = source.index(end, begin)
    fragments[name] = {'start': start, 'end': end, 'sha256': hashlib.sha256(source[begin:stop].encode()).hexdigest()}
(STAGE / 'fuzzer-golden.json').write_text(json.dumps({
    'source': 'E1_pilot/harness_v2/run_pilot.sh',
    'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
    'cases': cases, 'preserved_fragments': fragments,
}, indent=2) + '\n')

p = STAGE / 'static_validate.py'
s = p.read_text().replace('T14/T17 static validation', 'T14/T17/T27 static validation')
s = s.replace('T14/T17 validation:', 'T14/T17/T27 validation:')
s = s.replace('    for marker in (\'SCHEMA_CHECKS\'', '    fuzzer_args = (HERE / "fuzzer_args.sh").read_text()\n    for marker in (\'SCHEMA_CHECKS\'')
s = s.replace('        assert marker in run, marker', '        assert marker in run + fuzzer_args, marker')
needle = '    print("PASS ALL STATIC CHECKS AND PERMITTED UNIT TESTS", flush=True)'
assert s.count(needle) == 1
s = s.replace(needle, '''    print("BEGIN FUZZER ARGV/ROUTING/REDACTION/PROVENANCE UNIT TESTS", flush=True)
    subprocess.run(["/usr/bin/python3", "-I", "-B", str(HERE / "test_fuzzer_args.py")],
                   check=True, stderr=subprocess.STDOUT)
''' + needle)
s = s.replace('Compose, Java, Schemathesis, SUTs, ', 'Compose, Java, Schemathesis, EvoMaster, SUTs, ')
p.write_text(s)
