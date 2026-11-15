"""Check T37 outputs for fixed auth values in memory, emitting counts only."""
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = Path(__file__).resolve().parent
needles, roles = set(), set()
for path in (ROOT / '08_experiments/_external/emb/auth').glob('*.yaml'):
    document = yaml.safe_load(path.read_text()) or {}
    for role in document.get('auth', []):
        roles.add(role.get('name', ''))
        for header in role.get('fixedHeaders', []):
            value = header.get('value', '')
            if value:
                needles.add(value)
                needles.add(value.split(' ', 1)[-1])
needles -= roles
outputs = [p for p in SCRATCH.rglob('*') if p.is_file()] + [ROOT / '09_collab/reports/T37_report.md']
hits = [str(p.relative_to(ROOT)) for p in outputs if any(n.encode() in p.read_bytes() for n in needles if n)]
result = {'files_scanned': len(outputs), 'credential_match_files': hits, 'passed': not hits, 'values_withheld': True}
(SCRATCH / 'artifact_scan.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'files_scanned': len(outputs), 'match_count': len(hits), 'passed': not hits}))
raise SystemExit(bool(hits))
