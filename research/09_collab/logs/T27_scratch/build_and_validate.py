"""Produce a patch, apply it to a temporary harness copy, and run offline checks."""
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = Path(__file__).resolve().parent
EXP = ROOT / '08_experiments'
LIVE = EXP / 'E1_pilot/harness_v2'
STAGE = SCRATCH / 'staged/harness_v2'
PROPOSAL = LIVE / 'proposals'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


changed = []
base = {}
for candidate in sorted(STAGE.rglob('*')):
    if not candidate.is_file():
        continue
    relative = candidate.relative_to(STAGE)
    original = LIVE / relative
    if original.is_file() and original.read_bytes() == candidate.read_bytes():
        continue
    label = 'E1_pilot/harness_v2/' + relative.as_posix()
    if original.is_file():
        base[label] = sha(original)
    changed.append(label)

patch = []
for label in changed:
    relative = Path(label).relative_to('E1_pilot/harness_v2')
    original, candidate = LIVE / relative, STAGE / relative
    patch.append(f'diff --git a/{label} b/{label}\n')
    if not original.exists():
        patch.append('new file mode ' + ('100755' if candidate.stat().st_mode & 0o111 else '100644') + '\n')
    patch.extend(difflib.unified_diff(
        original.read_text().splitlines(keepends=True) if original.exists() else [],
        candidate.read_text().splitlines(keepends=True),
        fromfile='a/' + label if original.exists() else '/dev/null', tofile='b/' + label))
diff_path = PROPOSAL / 'harness.evomaster.proposed.diff'
diff_path.write_text(''.join(patch))
(PROPOSAL / 'harness.evomaster.base-sha256.json').write_text(json.dumps(base, indent=2) + '\n')

temp_root = Path(tempfile.mkdtemp(prefix='T27-patch-validation-', dir='/tmp'))
temp_exp = temp_root / 'research/08_experiments'
temp_harness = temp_exp / 'E1_pilot/harness_v2'
shutil.copytree(LIVE, temp_harness, ignore=shutil.ignore_patterns('.run.lock', '__pycache__'))
# Static validators only read these existing source/spec/JAR files. They never execute them.
(temp_exp / '_external').mkdir(parents=True)
(temp_exp / '_external/emb').symlink_to(EXP / '_external/emb', target_is_directory=True)
(temp_exp / 'E1_pilot/harness').symlink_to(EXP / 'E1_pilot/harness', target_is_directory=True)
result = subprocess.run(['patch', '--batch', '--fuzz=0', '-p1', '-i', str(diff_path.resolve())],
                        cwd=temp_exp, capture_output=True, text=True)
(SCRATCH / 'patch-apply.txt').write_text(result.stdout + result.stderr)
assert result.returncode == 0, result.stdout + result.stderr
for label in changed:
    relative = Path(label).relative_to('E1_pilot/harness_v2')
    assert (temp_harness / relative).read_bytes() == (STAGE / relative).read_bytes(), label
static = subprocess.run(['/usr/bin/python3', '-I', '-B', str(temp_harness / 'static_validate.py')],
                        cwd=temp_exp, capture_output=True, text=True)
(SCRATCH / 'static-tests.txt').write_text(static.stdout + static.stderr)
shells = []
for file in sorted(temp_harness.glob('*.sh')):
    result = subprocess.run(['bash', '-n', str(file)], capture_output=True, text=True)
    shells.append({'file': file.name, 'exit': result.returncode, 'stderr': result.stderr})
initial = json.loads((SCRATCH / 'initial-harness-sha256.json').read_text())
unchanged = {name: (LIVE / name).is_file() and sha(LIVE / name) == expected for name, expected in initial.items()}
validation = {'temp_root': str(temp_root), 'changed_files': changed, 'patch_sha256': sha(diff_path),
              'static_validate_exit': static.returncode, 'shell_checks': shells,
              'original_harness_unchanged': unchanged, 'applied_files_match_stage': True,
              'external_code_executed': False, 'network_used': False}
(SCRATCH / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
print(json.dumps({'temp_root': str(temp_root), 'static_validate_exit': static.returncode,
                  'original_files': len(unchanged), 'unchanged': all(unchanged.values()),
                  'changed_files': changed}, indent=2))
if static.returncode:
    print(static.stdout[-10000:])
    print(static.stderr[-10000:])
assert static.returncode == 0
assert all(item['exit'] == 0 for item in shells)
assert all(unchanged.values())
