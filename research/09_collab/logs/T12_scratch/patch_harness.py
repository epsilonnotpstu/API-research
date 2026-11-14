"""Apply T12 step 1b's bounded authentication and timeout harness fixes."""
from pathlib import Path
import sys

h = Path(sys.argv[1] if len(sys.argv) > 1 else '08_experiments/E1_pilot/harness')
p = h / 'run_pilot.sh'
s = p.read_text()
needle = 'BASE_PATH=${BASE_PATH:-/api}\n'
replacement = '''BASE_PATH=${BASE_PATH:-/api}
REQUEST_TIMEOUT_MS=${REQUEST_TIMEOUT_MS:-10000}
export PILOT_REQUEST_TIMEOUT_MS="$REQUEST_TIMEOUT_MS" PILOT_HYPOTHESIS_PHASES=explicit,generate
[[ $REQUEST_TIMEOUT_MS =~ ^[1-9][0-9]*$ ]] || { echo 'Invalid REQUEST_TIMEOUT_MS' >&2; exit 2; }
# Load the benchmark fixture at runtime; never persist its credential in provenance.
if [[ ${AUTH_HEADER+x} ]]; then
    export PILOT_AUTH_ROLE=${AUTH_ROLE:-custom}
else
    AUTH_HEADER=$(/usr/bin/python3 -I -B - "$EMB_DIR/auth/scout-api-auth.yaml" <<'AUTH_PY'
import sys, yaml
from pathlib import Path
config = yaml.safe_load(Path(sys.argv[1]).read_text())
role = next(item for item in config['auth'] if item['name'] == 'administrator')
header = next(item for item in role['fixedHeaders'] if item['name'].lower() == 'authorization')
print(header['name'] + ': ' + header['value'])
AUTH_PY
    )
    export PILOT_AUTH_ROLE=administrator
fi
[[ $AUTH_HEADER == *:* && $AUTH_HEADER != *$'\\n'* && $AUTH_HEADER != *$'\\r'* ]] || { echo 'Invalid AUTH_HEADER' >&2; exit 2; }
# Only the redactor receives this host-side environment value; Docker receives -H.
export PILOT_AUTH_REDACT="$AUTH_HEADER"
'''
assert needle in s
s = s.replace(needle, replacement)
s = s.replace('"${compose[@]}" logs --no-color >"$run_dir/compose.log" 2>&1', '"${compose[@]}" logs --no-color 2>&1 | /usr/bin/python3 -I -B "$HERE/redact_auth.py" >"$run_dir/compose.log"')
s = s.replace('    metadata "$rc"', '    /usr/bin/python3 -I -B "$HERE/redact_auth.py" "$run_dir"\n    if (($? != 0)); then echo \'Credential redaction failed\' >&2; rc=1; fi\n    metadata "$rc"')
s = s.replace('for flag in --checks --hypothesis-seed --hypothesis-max-examples --junit-xml --cassette-path --base-url; do', 'for flag in --checks --hypothesis-seed --hypothesis-max-examples --junit-xml --cassette-path --base-url --request-timeout --hypothesis-phases --header --sanitize-output; do')
s = s.replace('    --junit-xml /work/schemathesis.junit.xml --cassette-path /work/schemathesis-cassette.yaml)', '    --junit-xml /work/schemathesis.junit.xml --cassette-path /work/schemathesis-cassette.yaml \\\n    --request-timeout "$REQUEST_TIMEOUT_MS" --hypothesis-phases "$PILOT_HYPOTHESIS_PHASES" --sanitize-output true)')
s = s.replace('metadata pending\nset +e\ntimeout', 'printf \'%s\\n\' -H \'<redacted>\' >>"$run_dir/schemathesis-argv.txt"\nschema_cmd+=(-H "$AUTH_HEADER")\nmetadata pending\nset +e\ntimeout')
s = s.replace('"$SCHEMA_IMAGE" "${schema_cmd[@]}" >"$run_dir/schemathesis.log" 2>&1\nschema_rc=$?', '"$SCHEMA_IMAGE" "${schema_cmd[@]}" 2>&1 | /usr/bin/python3 -I -B "$HERE/redact_auth.py" >"$run_dir/schemathesis.log"\npilot_pipeline_rc=("${PIPESTATUS[@]}")\nschema_rc=${pilot_pipeline_rc[0]}\n((pilot_pipeline_rc[1] == 0)) || { echo \'Output redaction failed\' >&2; exit 1; }')
p.write_text(s)
(h / 'redact_auth.py').write_text(Path('09_collab/logs/T12_scratch/redact_auth.py.pending').read_text())
p = h / 'run_metadata.py'; s = p.read_text()
s = s.replace("'auth': 'none (pilot assumption)',", "'auth': os.environ.get('PILOT_AUTH_ROLE', 'none (pilot assumption)'),\n        'request_timeout_ms': int(os.environ.get('PILOT_REQUEST_TIMEOUT_MS', '10000')),\n        'hypothesis_phases': os.environ.get('PILOT_HYPOTHESIS_PHASES', 'explicit,generate'),")
p.write_text(s)
p = h / 'analyse_run.sh'; s = p.read_text()
s = s.replace("'max_examples', 'budget_seconds', 'seed', 'schemathesis_image', 'logger_max_body'):", "'max_examples', 'budget_seconds', 'seed', 'schemathesis_image', 'logger_max_body',\n            'request_timeout_ms', 'hypothesis_phases'):")
p.write_text(s)
