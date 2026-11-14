"""Prepare the review-only T27 source tree; never edit the live harness."""
from pathlib import Path

HERE = Path(__file__).resolve().parent / 'staged/harness_v2'


def replace_once(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new, 1)


p = HERE / 'run_pilot.sh'
s = p.read_text()
marker = 'for tool in docker curl java timeout flock git sha256sum grep /usr/bin/python3; do'
s = replace_once(s, marker, '''# Select/validate the fuzzer before any Docker command or run-directory creation.
export PILOT_FUZZER=${FUZZER:-schemathesis}
case $PILOT_FUZZER in
    schemathesis) ;;
    evomaster)
        /usr/bin/python3 -I -B "$HERE/evomaster_guard.py" options "$mode" "$seed" "$budget" "${DATA_GEN:-}" "${ONLY_OPS:-}"
        ;;
    *) echo 'Invalid FUZZER: use schemathesis or evomaster' >&2; exit 2;;
esac
source "$HERE/fuzzer_args.sh"
''' + marker)
s = replace_once(s, 'SCHEMA_IMAGE=schemathesis/schemathesis:3.39.16', '''SCHEMA_IMAGE=schemathesis/schemathesis:3.39.16
if [[ $PILOT_FUZZER == evomaster ]]; then
    export PILOT_EVOMASTER_IMAGE=webfuzzing/evomaster@sha256:de1f4387e809a309a4c61517f3340c3d0b733b78bbb86d0e3ebd217d343515ab
    export PILOT_EVOMASTER_VERSION=6.2.0
    # Keep schema-image.json / schemathesis_image as compatibility aliases for analysis.
    SCHEMA_IMAGE=$PILOT_EVOMASTER_IMAGE
fi''')
old = '    echo "Run: $run_dir; harness exit=$rc; Schemathesis exit=$schema_rc; coverage exit=$coverage_rc"'
s = replace_once(s, old, '''    if [[ $PILOT_FUZZER == evomaster ]]; then
        echo "Run: $run_dir; harness exit=$rc; EvoMaster exit=$schema_rc; coverage exit=$coverage_rc"
    else
''' + old + '''
    fi''')
start = s.index('# A registry/DNS outage')
end = s.index('phase=startup', start)
original_preflight = s[start:end]
s = s[:start] + '''if [[ $PILOT_FUZZER == evomaster ]]; then
    /usr/bin/python3 -I -B "$HERE/evomaster_guard.py" schema "$run_dir/spec.test.json" "$BASE_PATH"
    # The supervisor already pulled this immutable image. Never pull or run help here.
    docker image inspect "$SCHEMA_IMAGE" >"$run_dir/schema-image.json"
    cp "$run_dir/schema-image.json" "$run_dir/evomaster-image.json"
else
''' + original_preflight + '''fi
''' + s[end:]
start = s.index('schema_cmd=(run ')
end = s.index('# mount the run directory', start)
s = s[:start] + '''if [[ $PILOT_FUZZER == schemathesis ]]; then
build_schemathesis_argv
''' + s[end:]
start = s.index('printf \'%s\\n\' "${schema_cmd[@]}" >"$run_dir/schemathesis-argv.txt"')
end = s.index('metadata pending\nset +e', start)
s = s[:start] + '''record_fuzzer_argv "$run_dir/schemathesis-argv.txt" -H
else
    # Compatibility snapshot required by analyse_run.sh; no de-recursion for EvoMaster.
    cp "$run_dir/spec.test.json" "$run_dir/generator-input.json"
    mkdir "$run_dir/evomaster"
    build_evomaster_argv
    record_fuzzer_argv "$run_dir/evomaster-argv.txt" --header0
fi
''' + s[end:]
start = s.index('timeout --signal=INT --kill-after=20 "${budget}s" docker run')
end = s.index('pilot_pipeline_rc=', start)
default_execution = s[start:end]
s = s[:start] + '''if [[ $PILOT_FUZZER == evomaster ]]; then
    # maxTime bounds search; allow startup and generated-test/statistics serialization.
    # A watchdog timeout is still incomplete, exactly as on the default path.
    timeout --signal=INT --kill-after=20 "$((budget + 120))s" docker run --rm --name "$generator" \\
        --user "$PILOT_UID:$PILOT_GID" --workdir /work/evomaster --network "${project}_default" \\
        -v "$run_dir:/work" -v "$run_dir/spec.test.json:/work/spec.test.json:ro" \\
        "$SCHEMA_IMAGE" "${schema_cmd[@]}" 2>&1 | /usr/bin/python3 -I -B "$HERE/redact_auth.py" >"$run_dir/evomaster.log"
    pilot_pipeline_rc=("${PIPESTATUS[@]}")
else
''' + default_execution + '''    pilot_pipeline_rc=("${PIPESTATUS[@]}")
fi
''' + s[end:]
# Capture PIPESTATUS immediately inside each branch; a completed 'if' loses it.
s = replace_once(s, 'fi\npilot_pipeline_rc=("${PIPESTATUS[@]}")\nschema_rc=', 'fi\nschema_rc=')
start = s.index('# Exit 1 includes test failures;')
end = s.index('phase=complete', start)
default_completion = s[start:end]
s = s[:start] + '''if [[ $PILOT_FUZZER == evomaster ]]; then
    case $schema_rc in
        0|1) /usr/bin/python3 -I -B "$HERE/evomaster_guard.py" outputs "$run_dir/evomaster" ;;
        124|137) echo 'Generation budget expired; partial run retained, do not treat as complete' >&2; exit "$schema_rc";;
        *) echo "EvoMaster execution failed ($schema_rc)" >&2; exit "$schema_rc";;
    esac
else
''' + default_completion + '''fi
''' + s[end:]
p.write_text(s)

p = HERE / 'run_metadata.py'
s = p.read_text()
s = replace_once(s, "    data = {", "    fuzzer = os.environ.get('PILOT_FUZZER', 'schemathesis')\n    data = {")
s = replace_once(s, "        'run_id': run.name, 'sut': sut, 'source_spec': source,", "        'fuzzer': fuzzer,\n        'run_id': run.name, 'sut': sut, 'source_spec': source,")
s = replace_once(s, "    tmp = run / 'run.json.tmp'", '''    if fuzzer == 'evomaster':
        # Legacy image key identifies the selected generator for unchanged analysis.
        # Do not claim that Schemathesis ran in an EvoMaster collection.
        data['schemathesis_exit'] = 'not_started'
        data.update({
            'evomaster_image': os.environ['PILOT_EVOMASTER_IMAGE'],
            'evomaster_version': os.environ['PILOT_EVOMASTER_VERSION'],
            'evomaster_exit': schema_rc,
            'evomaster_argv_file': 'evomaster-argv.txt',
            'evomaster_argv': ((run / 'evomaster-argv.txt').read_text().splitlines()
                               if (run / 'evomaster-argv.txt').is_file() else []),
            'evomaster_watchdog_seconds': int(budget) + 120,
        })
        data['file_sha256'].update({str(p.relative_to(run)): sha(p)
                                   for p in sorted((run / 'evomaster').rglob('*')) if p.is_file()})
        data['limitations'] = [line for line in data['limitations']
                               if not line.startswith(('generator schema back edges',
                                                       'equal mutation operation sets'))]
        data['limitations'].append('EvoMaster uses spec.test unchanged; schema path checked against base_path')
    tmp = run / 'run.json.tmp' ''')
p.write_text(s)

p = HERE / 'fuzzer_args.sh'
s = p.read_text().replace('# Pure argv builders.', 'set -euo pipefail\n# Pure argv builders.')
p.write_text(s)
p.chmod(0o755)
