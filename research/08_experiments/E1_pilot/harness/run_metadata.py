"""Write atomic, standard-library-only provenance for a pilot (called by run_pilot.sh)."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main():
    (run, emb, sut, source, mode, fault, severity, seed, budget, examples, image,
     project, started, phase, schema_rc, coverage_rc, cleanup_rc, harness_rc,
     health, base_path) = sys.argv[1:]
    run, emb = Path(run), Path(emb)
    commit = subprocess.check_output(['git', '-C', str(emb), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(['git', '-C', str(emb), 'status', '--porcelain'], text=True)
    images = {}
    for path in sorted(run.glob('*-image.json')):
        try:
            inspected = json.loads(path.read_text())[0]
            images[path.stem] = {'id': inspected['Id'], 'repo_digests': inspected.get('RepoDigests', []),
                                'repo_tags': inspected.get('RepoTags', [])}
        except (ValueError, IndexError, KeyError) as error:
            images[path.stem] = {'inspection_error': str(error)}
    files = {p.name: sha(p) for p in sorted(run.iterdir())
             if p.is_file() and p.name != 'run.json' and not p.name.endswith('.tmp')}
    data = {
        'run_id': run.name, 'sut': sut, 'source_spec': source,
        'source_sha256': sha(next(run.glob('spec.original.*'), Path(source))),
        'mode': mode, 'fault': fault, 'severity': int(severity), 'seed': int(seed),
        'budget_seconds': int(budget), 'max_examples': int(examples),
        'schemathesis_image': image, 'compose_project': project,
        'started_at': started, 'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'finished_at': None if harness_rc == 'pending' else datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'phase': phase, 'schemathesis_exit': schema_rc, 'coverage_exit': coverage_rc,
        'cleanup_exit': cleanup_rc, 'harness_exit': harness_rc,
        'complete': harness_rc == '0', 'emb_commit': commit, 'emb_status_porcelain': dirty,
        'health_path': health, 'base_path': base_path, 'auth': os.environ.get('PILOT_AUTH_ROLE', 'none (pilot assumption)'),
        'request_timeout_ms': int(os.environ.get('PILOT_REQUEST_TIMEOUT_MS', '10000')),
        'hypothesis_phases': os.environ.get('PILOT_HYPOTHESIS_PHASES', 'explicit,generate'),
        'logger_max_body': int(os.environ['MITM_MAX_BODY']),
        'host_port': os.environ['HOST_PORT'], 'jacoco_port': os.environ['JACOCO_PORT'],
        'sut_jar_sha256': sha(emb / 'dist' / f'{sut}-sut.jar'),
        'jacoco_agent_sha256': sha(emb / 'dist' / 'jacocoagent.jar'),
        'jacoco_cli_sha256': sha(emb / 'dist' / 'jacococli.jar'),
        'images': images, 'file_sha256': files,
        'tool_sha256': {p.name: sha(p) for p in sorted((emb.parent.parent / 'tools').glob('*.py'))},
        'harness_sha256': {p.name: sha(p) for p in sorted(Path(__file__).parent.iterdir()) if p.is_file() and not p.name.startswith('.')},
        'limitations': ['fresh traffic is observational', 'fixed seed does not guarantee identical traffic',
                         'transport-error and truncation coverage require review',
                         'locally built SUT may have only image ID, no registry digest'],
    }
    tmp = run / 'run.json.tmp'
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    tmp.replace(run / 'run.json')


if __name__ == '__main__':
    main()
