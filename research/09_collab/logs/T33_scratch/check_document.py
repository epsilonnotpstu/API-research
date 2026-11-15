"""Validate T33 draft citation bounds, search artifacts and protected-file hashes."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = Path(__file__).resolve().parent
PROPOSAL = ROOT / '08_experiments/E2_labelling/proposals/CODEBOOK_11_4_PROPOSAL.md'
ALIASES = {
    'S': '08_experiments/_external/emb/jdk_8_maven/cs/rest/original/scout-api',
    'M': '08_experiments/_external/emb/jdk_11_maven/cs/rest-gui/market',
    'P': '08_experiments/_external/emb/jdk_8_maven/cs/rest/original/swagger-petstore',
    'C': '08_experiments/_external/emb/jdk_11_maven/cs/rest/cwa-verification-server',
}
text = PROPOSAL.read_text()
checked, errors = [], []
for token in re.findall(r'`([^`\n]+)`', text):
    match = re.match(r'((?:08_experiments|09_collab|S|M|P|C)/[^:#]+)(?::([\d,–-]+)|[:#].*)?$', token)
    if not match or '…' in token:
        continue
    name = match[1]
    if name.split('/')[0] in ALIASES:
        alias, relative = name.split('/', 1)
        name = ALIASES[alias] + '/' + relative
    assert 'e5_blind' not in name and 'blind_key' not in name, name
    path = ROOT / name
    if not path.exists():
        errors.append({'token': token, 'error': 'missing file'})
        continue
    if match[2]:
        count = len(path.read_text().splitlines())
        numbers = list(map(int, re.findall(r'\d+', match[2])))
        if not all(1 <= number <= count for number in numbers):
            errors.append({'token': token, 'error': 'line out of bounds', 'lines': count})
    checked.append(token)
before = json.loads((SCRATCH / 'protected_before.json').read_text())
after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in before}
runs = json.loads((SCRATCH / 'search_summary.json').read_text())
checks = {
    'proposal_is_draft': 'DRAFT / NOT ADOPTED' in text,
    'subsections': len(re.findall(r'^## 11\.4\.', text, re.M)) == 7,
    'supervisor_questions': len(re.findall(r'^\d\. ', text.split('## 11.4.7')[1], re.M)) == 7,
    'searches': len(runs),
    'all_exit_zero': all(run['returncode'] == 0 for run in runs),
    'all_hit_locators_verified': all(run['locators_verified'] for run in runs),
    'total_hit_locators': sum(sum(run['hit_counts'].values()) for run in runs),
    'citation_tokens_checked': len(checked),
    'citation_errors': errors,
    'protected_files': len(before),
    'protected_unchanged': before == after,
    'tool_sha256': after['08_experiments/tools/intent_evidence.py'],
    'forbidden_cited_paths': False,
}
(SCRATCH / 'document_verification.json').write_text(json.dumps(checks, indent=2, ensure_ascii=False) + '\n')
print(json.dumps(checks, indent=2, ensure_ascii=False))
assert not errors and before == after
assert checks['subsections'] and checks['supervisor_questions'] and checks['proposal_is_draft']
