"""Reuse the smoke's immutable image instead of rebuilding project-labelled images."""
from pathlib import Path

h = Path('08_experiments/E1_pilot/harness')
p = h / 'compose.override.scout-api.yaml'
s = p.read_text().replace('  sut-scout-api:\n    build:', '  sut-scout-api:\n    image: ${PILOT_SUT_IMAGE:-r1-scout-api-pilot}\n    build:')
p.write_text(s)
p = h / 'run_pilot.sh'; s = p.read_text()
s = s.replace('export PILOT_UID=$(id -u) PILOT_GID=$(id -g)', 'export PILOT_UID=$(id -u) PILOT_GID=$(id -g)\nexport PILOT_SUT_IMAGE=${PILOT_SUT_IMAGE:-}\nif [[ -n $PILOT_SUT_IMAGE ]]; then\n    [[ $PILOT_SUT_IMAGE =~ ^sha256:[[:xdigit:]]{64}$ ]] || { echo \'PILOT_SUT_IMAGE must be an immutable local image ID\' >&2; exit 2; }\nfi')
s = s.replace('"${compose[@]}" up -d --build >"$run_dir/compose-up.log" 2>&1', 'if [[ -n $PILOT_SUT_IMAGE ]]; then\n    "${compose[@]}" up -d --no-build >"$run_dir/compose-up.log" 2>&1\nelse\n    "${compose[@]}" up -d --build >"$run_dir/compose-up.log" 2>&1\nfi')
p.write_text(s)
