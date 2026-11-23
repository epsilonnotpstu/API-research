"""R4 package privacy/blinding audit (run before the package freeze). Counts only; prints item ids and check names, never matched text.
Checks per item of packages/r4_blind: fix/parent SHA (full or 7+ prefix) anywhere; fix-commit author name/e-mail and committer anywhere;
e-mail addresses; GitHub @handles in item.md; credit words left in item.md outside [CREDIT REDACTED]; github/gitlab URLs; secret findings
(R3 t53_privacy). Also: kb batches are byte-identical copies of r4_blind items.
Run from R4_access_control/: /usr/bin/python3 -I -B collab/scripts/r4_package_audit.py"""
import collections, csv, filecmp, re, subprocess, sys
from pathlib import Path

B = Path(__file__).resolve().parents[2]; P = B / 'packages'; G = B / 'mining/cache/git'
sys.path.insert(0, str(B.parent / 'R3_silent_breaking/mining')); sys.path.insert(0, str(B / 'mining/claude'))
import t53_privacy as PRIV  # noqa: E402
from r4p import CREDIT_RX  # noqa: E402

HANDLE = re.compile(r'(?<![\w.@/`])@[A-Za-z0-9][A-Za-z0-9-]{1,38}\b')
JAVA_ANN = re.compile(r'@(Override|RolesAllowed|PreAuthorize|PostAuthorize|Secured|Get|Post|Put|Delete|Path|Valid|Request\w*|Response\w*|Path\w*|Json\w*|\w+Mapping|Deprecated|Transactional|Autowired|Inject|Component|Service|Controller|RestController|sha256|PermitAll|DenyAll)\b')
HOST = re.compile(r'https?://(?:www\.)?(?:github|gitlab)\.com/', re.I)


def main():
    key = {r['item_id']: r for r in csv.DictReader(open(B / 'mining/key/r4_key.csv'))}
    hits = collections.defaultdict(list)
    for iid, k in sorted(key.items()):
        o, r = k['repo'].split('/'); gd = G / f'{o}__{r}.git'
        who = subprocess.run(['git', '--git-dir', str(gd), 'log', '-1', '--format=%an%n%ae%n%cn%n%ce', k['fix_sha']], capture_output=True, text=True).stdout.split('\n')
        who = {w.strip() for w in who if len(w.strip()) >= 5 and w.strip().lower() not in ('github', 'noreply@github.com', 'web-flow')}
        d = P / 'r4_blind' / iid
        for f in d.rglob('*'):
            if not f.is_file(): continue
            t = f.read_text(errors='replace'); rel = f.relative_to(d).as_posix()
            if any(s[:n] in t for s in (k['fix_sha'], k['parent_sha']) for n in (40, 12, 7) if re.search(r'\b' + s[:n] + r'\b', t)): hits['sha'].append(f'{iid}/{rel}')
            if any(w in t for w in who): hits['commit_author'].append(f'{iid}/{rel}')
            if PRIV.EMAIL.search(t): hits['email'].append(f'{iid}/{rel}')
            if HOST.search(t): hits['hosting_url'].append(f'{iid}/{rel}')
            if rel == 'item.md':
                hs = [h for h in HANDLE.findall(t) if not JAVA_ANN.match(h)]
                if hs: hits['handle_item_md'].append(f'{iid} ({len(hs)})')
                if any(CREDIT_RX.search(l) for l in t.splitlines() if 'CREDIT REDACTED' not in l): hits['credit_word_item_md'].append(iid)
            fs = [x for x in PRIV.findings(f.read_bytes()) if x in ('email', 'auth', 'private_key', 'quoted_encoded')]
            if fs: hits['secret_' + '_'.join(fs)].append(f'{iid}/{rel}')
    kb_bad = 0
    for kb in sorted(P.glob('r4_kb*')):
        for d in sorted(x for x in kb.iterdir() if x.is_dir() and x.name.startswith('A')):
            cmp = filecmp.dircmp(d, P / 'r4_blind' / d.name)
            if cmp.diff_files or cmp.left_only or cmp.right_only: kb_bad += 1
    for k_, v in sorted(hits.items()): print(f'{k_}: {len(v)}  e.g. {v[:6]}')
    print(f'items {len(key)}; kb items differing from r4_blind: {kb_bad}; checks with hits: {len(hits)}')


if __name__ == '__main__':
    main()
