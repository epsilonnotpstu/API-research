"""R4 mining pipeline, Claude's implementation (primary; R4_DEVIATIONS D1). Implements R4_PLAN.md §3, §4, §6. Stdlib only.
Run from R4_access_control/:  /usr/bin/python3 -I -B mining/claude/r4p.py {collect|resolve|pool|sample|build|all}
Outputs (mining/): advisories.json, resolved.json, pool.json, pool_inventory.json, pool_freeze.json, sample.json, sample_freeze.json,
key/r4_key.csv, key/r4_build_log.json, key/r4_shuffle_salt.txt; packages/r4_blind/, packages/r4_kb*/.
Prints counts only; never prints advisory text, diffs or contract content."""
import collections, csv, hashlib, hmac, json, os, random, re, secrets, shutil, subprocess, sys, time
from pathlib import Path

B = Path(__file__).resolve().parents[2]; M = B / 'mining'; C = M / 'cache'; G = C / 'git'; P = B / 'packages'
R3M = B.parent / 'R3_silent_breaking' / 'mining'
sys.path.insert(0, str(R3M))
import t53_privacy as PRIV  # noqa: E402  (read-only reuse of R3 redaction)

ECOS = ('maven', 'go')
CWES = '284,285,639,862,863,915,269,266,425,566,708,306'
EXCL = {'test', 'tests', 'testdata', 'example', 'examples', 'sample', 'samples', 'fixture', 'fixtures', 'vendor', 'node_modules',
        'third_party', 'e2e', 'mock', 'mocks'}
CONTRACT_RX = re.compile(r'(^|/)[^/]*(openapi|swagger)[^/]*\.(ya?ml|json)$', re.I)  # plan §3.1: file name contains openapi/swagger (F4/M05)
COMMIT_RX = re.compile(r'^https://github\.com/([^/]+)/([^/]+)/commit/([0-9a-fA-F]{7,40})')
PAT = json.load(open(R3M / 'annotation_patterns.json'))
JVM_RX = re.compile(PAT['jvm_pattern']); GO_RX = re.compile(PAT['go_pattern'], re.I)
MAX_LINES = 2000; CAP_REPO = 4; CAP_ALL = 160; BATCH = 16; MAX_FILES = 20; CONTRACT_DOCS = 3; CONTRACT_LINES = 3000
ENV = {**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'LC_ALL': 'C'}


# ---------- helpers
def jdump(obj, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + '\n', encoding='utf-8')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(cmd, tries=3, check=True, binary=False, timeout=600):
    for t in range(tries):
        r = subprocess.run(cmd, capture_output=True, env=ENV, timeout=timeout)
        if r.returncode == 0: return r.stdout if binary else r.stdout.decode('utf-8', 'replace')
        if t < tries - 1: time.sleep(2 * (t + 1))
    if check: raise RuntimeError(f'command failed: {cmd[:4]} ... rc={r.returncode}')
    return None


def segs(path):
    return [s.lower() for s in path.split('/')[:-1]]


def is_contract_path(p):
    return bool(CONTRACT_RX.search(p)) and not (set(segs(p)) & EXCL)


def is_test_path(p):
    lp = p.lower(); name = p.rsplit('/', 1)[-1]
    return ('src/test/' in lp or name.endswith('_test.go') or bool(set(segs(p)) & {'test', 'tests'})
            or re.search(r'(Test|Tests|IT)\.(java|kt)$', name) is not None)


def is_source_path(p):
    return (p.endswith(('.java', '.kt', '.go')) and not (set(segs(p)) & EXCL) and 'src/test/' not in p.lower() and not p.endswith('_test.go')
            and not is_test_path(p))


def annotation_lines(diff):
    """Added/removed lines inside hunks (F4/M12: hunk-state parsing; whole fix diff is passed in)."""
    n, hunk = 0, False
    for line in diff.splitlines():
        if line.startswith('diff --git '): hunk = False; continue
        if line.startswith('@@'): hunk = True; continue
        if hunk and line[:1] in ('+', '-') and (JVM_RX.search(line[1:]) or GO_RX.search(line[1:])): n += 1
    return n


TOKEN_RX = re.compile(r'(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{16,}|(?:AKIA|ASIA)[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|sk_live_[0-9A-Za-z]{16,}'
                      r'|AIza[0-9A-Za-z_-]{35}|glpat-[A-Za-z0-9_-]{20}')
PEM_RX = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(?:-----END [A-Z ]*PRIVATE KEY-----|\Z)', re.S)


def scrub(text):
    """F4/M15-M16: known token prefixes and raw PEM private-key blocks (line count preserved)."""
    text = TOKEN_RX.sub('[REDACTED]', text)
    return PEM_RX.sub(lambda m: '\n'.join('[REDACTED]' for _ in m.group(0).split('\n')), text)


def gitdir(owner, repo):
    return G / f'{owner}__{repo}.git'


def git(gd, *a, **k):
    return run(['git', '--git-dir', str(gd), *a], **k)


def ensure_repo(owner, repo):
    gd = gitdir(owner, repo)
    if not gd.exists():
        run(['git', 'init', '-q', '--bare', str(gd)]); git(gd, 'remote', 'add', 'origin', f'https://github.com/{owner}/{repo}.git')
    return gd


def have_commit(gd, sha):
    return subprocess.run(['git', '--git-dir', str(gd), 'cat-file', '-e', f'{sha}^{{commit}}'], capture_output=True, env=ENV).returncode == 0


# ---------- stages
def collect():
    advs = []
    for eco in ECOS:
        raw = C / f'advisories_{eco}.json'
        if not raw.exists():
            out = run(['gh', 'api', '--paginate', f'/advisories?ecosystem={eco}&type=reviewed&cwes={CWES}&per_page=100'], timeout=1800)
            pages = '[' + out.strip().replace('][', '],[') + ']'
            data = [a for page in json.loads(pages) for a in page]
            jdump(data, raw)
        for a in json.load(open(raw)):
            advs.append({'ghsa_id': a['ghsa_id'], 'cve_id': a.get('cve_id'), 'ecosystem': eco,
                         'cwes': sorted(c['cwe_id'] for c in (a.get('cwes') or [])), 'severity': a.get('severity'),
                         'published_at': a.get('published_at'), 'withdrawn_at': a.get('withdrawn_at'), 'summary': a.get('summary') or '',
                         'description': a.get('description') or '', 'references': list(a.get('references') or []),
                         'source_code_location': a.get('source_code_location') or '',
                         'packages': sorted({(v.get('package') or {}).get('name', '') for v in (a.get('vulnerabilities') or [])})})
    by = {}
    for a in advs:                       # an advisory listed in both ecosystems: keep the first (maven), record both
        if a['ghsa_id'] in by: by[a['ghsa_id']]['ecosystem'] += ';' + a['ecosystem']
        else: by[a['ghsa_id']] = a
    advs = sorted(by.values(), key=lambda a: a['ghsa_id'])
    jdump(advs, M / 'advisories.json')
    print(f'collect: {len(advs)} advisories ({collections.Counter(a["ecosystem"] for a in advs)}); withdrawn {sum(bool(a["withdrawn_at"]) for a in advs)}')


def candidates(a):
    src = a['source_code_location'].rstrip('/').lower()
    own, other = [], []
    for ref in a['references']:
        m = COMMIT_RX.match(ref.strip())
        if not m: continue
        o, r, s = m.group(1), m.group(2), m.group(3).lower()
        r = r[:-4] if r.endswith('.git') else r
        (own if f'https://github.com/{o}/{r}'.lower() == src else other).append((o, r, s))
    seen, out = set(), []
    for c in own + other:
        if c not in seen: seen.add(c); out.append(c)
    return out


def resolve():
    advs = json.load(open(M / 'advisories.json')); res = {}
    for i, a in enumerate(advs):
        if a['withdrawn_at']: res[a['ghsa_id']] = {'reason': 'WITHDRAWN'}; continue
        cands = candidates(a); rec = None; err = False
        for o, r, s in cands:
            try:
                if len(s) < 40:
                    full = run(['gh', 'api', f'repos/{o}/{r}/commits/{s}', '--jq', '.sha'], check=False)
                    if not full or not re.fullmatch(r'[0-9a-f]{40}', full.strip()): continue
                    s = full.strip()
                gd = ensure_repo(o, r)
                if not have_commit(gd, s):
                    if git(gd, '-c', 'protocol.version=2', 'fetch', '-q', '--depth=2', '--filter=blob:none', 'origin', s, check=False, tries=3) is None:
                        err = True; continue
                parent = git(gd, 'rev-parse', '-q', '--verify', f'{s}^1^{{commit}}', check=False, tries=1)
                if not parent:   # F1: the fix may be present only as a shallow boundary of another fetch -> re-fetch it with depth 2
                    git(gd, '-c', 'protocol.version=2', 'fetch', '-q', '--depth=2', '--filter=blob:none', 'origin', s, check=False, tries=3)
                    parent = git(gd, 'rev-parse', '-q', '--verify', f'{s}^1^{{commit}}', check=False, tries=1)
                if not parent: rec = {'reason': 'NO_PARENT', 'repo': f'{o}/{r}', 'fix_sha': s}; break
                rec = {'repo': f'{o}/{r}', 'fix_sha': s, 'parent_sha': parent.strip()}; break
            except (RuntimeError, subprocess.TimeoutExpired):
                err = True
        res[a['ghsa_id']] = rec or {'reason': 'FETCH_ERROR' if err else 'NO_COMMIT'}
        if (i + 1) % 100 == 0: print(f'  resolve {i + 1}/{len(advs)}', flush=True)
    jdump(res, M / 'resolved.json')
    print('resolve:', dict(collections.Counter(v.get('reason', 'RESOLVED') for v in res.values())))


def numstat(gd, parent, fix):
    """F4/M07: default rename detection (-M), NUL-separated. Returns dicts: a, d, path (new), old, status."""
    ns = git(gd, 'diff', '-M', '-z', '--numstat', '--no-ext-diff', '--no-textconv', parent, fix).split('\0')
    st = git(gd, 'diff', '-M', '-z', '--name-status', '--no-ext-diff', parent, fix).split('\0')
    status = {}
    i = 0
    while i < len(st) - 1:
        code = st[i]
        if not code: i += 1; continue
        if code[0] in 'RC': status[st[i + 2]] = code[0]; i += 3
        else: status[st[i + 1]] = code[0]; i += 2
    rows, i = [], 0
    while i < len(ns) - 1:
        rec = ns[i]
        if not rec: i += 1; continue
        a, d, p = rec.split('\t', 2)
        if p == '': old, new = ns[i + 1], ns[i + 2]; i += 3
        else: old = new = p; i += 1
        rows.append({'a': 0 if a == '-' else int(a), 'd': 0 if d == '-' else int(d), 'path': new, 'old': old, 'status': status.get(new, 'M')})
    return rows


def pool():
    if (M / 'pool_freeze.json').exists(): sys.exit('refuse: pool_freeze.json exists')
    advs = {a['ghsa_id']: a for a in json.load(open(M / 'advisories.json'))}; res = json.load(open(M / 'resolved.json'))
    reasons = collections.Counter(); elig = {}
    for gid in sorted(res):
        r = res[gid]
        if 'reason' in r: reasons[r['reason']] += 1; continue
        o, rp = r['repo'].split('/'); gd = gitdir(o, rp)
        tree = git(gd, 'ls-tree', '-r', '--name-only', r['parent_sha']).splitlines()
        contracts = sorted(p for p in tree if is_contract_path(p))
        if not contracts: reasons['NO_CONTRACT_AT_PARENT'] += 1; continue
        ns = numstat(gd, r['parent_sha'], r['fix_sha'])
        src = [x for x in ns if is_source_path(x['path'])]
        if not src: reasons['NO_SOURCE_CHANGE'] += 1; continue
        lines = sum(x['a'] + x['d'] for x in src)
        if lines > MAX_LINES: reasons['TOO_LARGE'] += 1; continue
        key = (r['repo'].lower(), r['fix_sha'])
        if key in elig:
            elig[key]['ghsa_ids'] = sorted(elig[key]['ghsa_ids'] + [gid]); reasons['DEDUP_MERGED'] += 1; continue
        diff = git(gd, 'diff', '-M', '--no-ext-diff', '--no-textconv', r['parent_sha'], r['fix_sha'])   # whole fix diff (M12)
        ext = collections.Counter(x['path'].rsplit('.', 1)[-1] for x in src).most_common()
        lang = {'java': 'Java', 'kt': 'Kotlin', 'go': 'Go'}[sorted(ext, key=lambda e: (-e[1], e[0]))[0][0]]
        elig[key] = {'ghsa_ids': [gid], 'repo': r['repo'], 'fix_sha': r['fix_sha'], 'parent_sha': r['parent_sha'],
                     'ecosystem': advs[gid]['ecosystem'], 'language': lang, 'fix_lines': lines, 'n_source_files': len(src),
                     'source_files': [x['path'] for x in src], 'contract_paths': contracts,
                     'fix_touches_contract': any(is_contract_path(x['path']) or is_contract_path(x['old']) for x in ns),
                     'fix_touches_annotation': annotation_lines(diff) > 0,
                     'test_in_fix': any(x['status'] in 'AMRT' and is_test_path(x['path']) for x in ns)}
    items = sorted(elig.values(), key=lambda x: x['ghsa_ids'][0])
    for it in items:
        it['fix_silent'] = not (it['fix_touches_contract'] or it['fix_touches_annotation'])
        it['item_key'] = it['ghsa_ids'][0]
    jdump(items, M / 'pool.json')
    inv = {'n_advisories': len(advs), 'n_eligible_items': len(items), 'exclusions': dict(sorted(reasons.items())),
           'by_ecosystem': dict(collections.Counter(i['ecosystem'] for i in items)),
           'by_repo': dict(sorted(collections.Counter(i['repo'] for i in items).items()))}
    jdump(inv, M / 'pool_inventory.json')
    jdump({'query': {'ecosystems': ECOS, 'type': 'reviewed', 'cwes': CWES}, 'created': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
           'sha256': {f: sha256(M / f) for f in ('advisories.json', 'resolved.json', 'pool.json', 'pool_inventory.json')}},
          M / 'pool_freeze.json')
    print(f'pool: {len(items)} eligible items from {len(inv["by_repo"])} repos; exclusions {inv["exclusions"]}; by eco {inv["by_ecosystem"]}')


def sample():
    if (M / 'sample_freeze.json').exists(): sys.exit('refuse: sample_freeze.json exists')
    items = json.load(open(M / 'pool.json')); ids = {i['item_key']: i for i in items}
    if len(items) <= CAP_ALL: chosen = sorted(ids)
    else:
        by = collections.defaultdict(list)
        for i in items: by[i['repo']].append(i['item_key'])
        chosen = []
        for repo in sorted(by):
            ks = sorted(by[repo]); chosen += random.Random('r4:' + repo).sample(ks, min(CAP_REPO, len(ks)))
        chosen = sorted(chosen)
        if len(chosen) > CAP_ALL: chosen = sorted(random.Random('r4-sample-20261123').sample(chosen, CAP_ALL))
    jdump([ids[k] for k in chosen], M / 'sample.json')
    jdump({'pool_freeze_sha256': sha256(M / 'pool_freeze.json'), 'sample_sha256': sha256(M / 'sample.json'), 'n': len(chosen),
           'repos': len({ids[k]['repo'] for k in chosen})}, M / 'sample_freeze.json')
    print(f'sample: {len(chosen)} items from {len({ids[k]["repo"] for k in chosen})} repos')


LINK_RX = re.compile(r'https?://\S*(?:/commit/|/pull/|/compare/|/releases/|/advisories/|GHSA-|CVE-)\S*', re.I)
CREDIT_RX = re.compile(r'(?i)\b(credits?|thanks?|thank you|acknowledg\w*|contributors?|reporters?|(?:reported|discovered|found|identified|disclosed)\s+(?:by|this|and reported)|researchers? who|authorship|(?:fix|patch|commit|fixes|patches)\s+(?:was\s+)?(?:by|from)|sign-off)\b')
HANDLE_RX = re.compile(r'(?<![\w.@/])@[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})\b')


def clean_advisory(t):
    """F2: a line naming credit/thanks/reporters is redacted, and so is every following line up to the next Markdown heading
    (credit sections list names on later lines); GitHub @handles on such lines and in such sections are covered by the same rule."""
    t = LINK_RX.sub('[LINK]', t or '')
    t = PRIV.EMAIL.sub('[REDACTED]', t)
    out, in_credit = [], False
    for l in t.replace('\r\n', '\n').split('\n'):
        if l.lstrip().startswith('#'):
            in_credit = bool(CREDIT_RX.search(l))
            out.append('[CREDIT REDACTED]' if in_credit else l); continue
        if CREDIT_RX.search(l): in_credit = True
        out.append('[CREDIT REDACTED]' if (in_credit and l.strip()) else l)
        if in_credit and not l.strip() and out[-2:-1] != ['[CREDIT REDACTED]']: pass
    return '\n'.join(out)


def red(raw_bytes, shas):
    raw_bytes = scrub(raw_bytes.decode('utf-8', 'replace').replace('\r\n', '\n')).encode()
    try: return PRIV.redact(raw_bytes, shas=shas)
    except (UnicodeDecodeError, ValueError):
        return PRIV.redact_text(raw_bytes.decode('utf-8', 'replace'), shas=shas).encode()


def flat(p):
    return p.replace('/', '__')


def build():
    out = P / 'r4_blind'
    if out.exists(): sys.exit('refuse: packages/r4_blind exists')
    advs = {a['ghsa_id']: a for a in json.load(open(M / 'advisories.json'))}; items = json.load(open(M / 'sample.json'))
    task = (B / 'plan/TASK_R4.md').read_bytes()
    salt_f = M / 'key/r4_shuffle_salt.txt'
    if not salt_f.exists(): salt_f.parent.mkdir(parents=True, exist_ok=True); salt_f.write_text(secrets.token_hex(32) + '\n')
    salt = bytes.fromhex(salt_f.read_text().strip())
    order = sorted(items, key=lambda it: hmac.new(salt, it['item_key'].encode(), hashlib.sha256).hexdigest())
    out.mkdir(parents=True); log = {}; keyrows = []
    for n, it in enumerate(order, 1):
        iid = f'A{n:03d}'; d = out / iid; d.mkdir(); o, rp = it['repo'].split('/'); gd = gitdir(o, rp); shas = [it['fix_sha'], it['parent_sha']]
        a = advs[it['ghsa_id'] if 'ghsa_id' in it else it['ghsa_ids'][0]]
        cw = sorted({c for g in it['ghsa_ids'] for c in advs[g]['cwes']})
        ns = numstat(gd, it['parent_sha'], it['fix_sha'])
        srcrows = sorted([x for x in ns if is_source_path(x['path'])], key=lambda x: (-(x['a'] + x['d']), x['path']))
        src = [(x['a'] + x['d'], x['path']) for x in srcrows]
        files = srcrows[:MAX_FILES]
        md = [f'# {iid}', '', f'- Repository: {rp}', f'- Language: {it["language"]}', f'- CWE: {", ".join(cw) or "none listed"}', '',
              '## Advisory summary', clean_advisory(a['summary']), '', '## Advisory description', clean_advisory(a['description']), '',
              '## Touched source files (non-test)'] + [f'- `{p}`' for _, p in src]
        if len(it['ghsa_ids']) > 1:
            md += ['', '## Further advisories fixed by the same commit']
            for g in it['ghsa_ids'][1:]: md += ['', f'### Summary', clean_advisory(advs[g]['summary'])]
        (d / 'item.md').write_bytes(PRIV.redact_text(scrub('\n'.join(md) + '\n'), shas=shas).encode())
        paths = sorted({x['path'] for x in srcrows} | {x['old'] for x in srcrows})
        diff = git(gd, 'diff', '-M', '--no-ext-diff', '--no-textconv', it['parent_sha'], it['fix_sha'], '--', *paths, binary=True)
        (d / 'diff.patch').write_bytes(red(diff, shas))
        for side, rev in (('before', it['parent_sha']), ('after', it['fix_sha'])):
            (d / side).mkdir()
            for x in files:
                if (side == 'before' and x['status'] == 'A') or (side == 'after' and x['status'] == 'D'): continue
                p = x['old'] if side == 'before' else x['path']
                b = git(gd, 'show', f'{rev}:{p}', binary=True, check=True, tries=3)      # M18: fail loudly
                (d / side / flat(p)).write_bytes(red(b, shas))
        (d / 'contract').mkdir()
        sizes = []
        for p in it['contract_paths']:
            s = git(gd, 'cat-file', '-s', f'{it["parent_sha"]}:{p}', check=True, tries=3)
            sizes.append((int(s), p))
        sizes.sort(key=lambda x: (-x[0], x[1]))
        idx = ['# Contract documents at the vulnerable version', '', '| path | bytes | provided |', '|---|---|---|']
        top = [p for _, p in sizes[:CONTRACT_DOCS]]
        for s, p in sizes: idx.append(f'| `{p}` | {s} | {"yes" if p in top else "no"} |')
        for p in top:
            b = git(gd, 'show', f'{it["parent_sha"]}:{p}', binary=True, check=True, tries=3)
            lines = b.replace(b'\r\n', b'\n').split(b'\n'); trunc = len(lines) > CONTRACT_LINES
            txt = b'\n'.join(lines[:CONTRACT_LINES]) + (b'\n' if trunc else b'')
            try: txt = PRIV.redact_text(scrub(txt.decode('utf-8', 'replace')), shas=shas, structured=p.endswith('.json')).encode()
            except ValueError: txt = b''
            (d / 'contract' / flat(p)).write_bytes(txt + (b'\n# [TRUNCATED at 3000 lines]\n' if trunc and not p.endswith('.json') else b''))
            if trunc: idx.append(f'\n`{p}` truncated to its first {CONTRACT_LINES} lines.')
        (d / 'contract' / 'INDEX.md').write_text('\n'.join(idx) + '\n')
        found = collections.Counter()
        for f in d.rglob('*'):
            if f.is_file():
                for k in PRIV.findings(f.read_bytes(), shas=shas):
                    if k not in ('hex', 'date', 'non_idempotent_or_metadata', 'attribution'): found[k] += 1
        log[iid] = {'files': len(files), 'source_files_total': len(src), 'contract_docs': len(sizes), 'scan': dict(found)}
        keyrows.append({'item_id': iid, 'ghsa_ids': ';'.join(it['ghsa_ids']), 'repo': it['repo'], 'ecosystem': it['ecosystem'],
                        'language': it['language'], 'fix_sha': it['fix_sha'], 'parent_sha': it['parent_sha'], 'cwes': ';'.join(cw),
                        'severity': a['severity'], 'published_at': a['published_at'], 'fix_lines': it['fix_lines'],
                        'fix_touches_contract': str(it['fix_touches_contract']).lower(), 'fix_touches_annotation': str(it['fix_touches_annotation']).lower(),
                        'fix_silent': str(it['fix_silent']).lower(), 'test_in_fix': str(it['test_in_fix']).lower(), 'n_contract_docs': len(sizes)})
    with open(out / 'items.csv', 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['item_id', 'repo_short_name', 'language'])
        for r in keyrows: w.writerow([r['item_id'], r['repo'].split('/')[1], r['language']])
    (out / 'TASK_R4.md').write_bytes(task)
    with open(M / 'key/r4_key.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(keyrows[0]), lineterminator='\n'); w.writeheader(); w.writerows(keyrows)
    jdump(log, M / 'key/r4_build_log.json')
    ids = [r['item_id'] for r in keyrows]
    for k in range(0, len(ids), BATCH):
        kb = P / f'r4_kb{k // BATCH + 1}'; kb.mkdir()
        for iid in ids[k:k + BATCH]: shutil.copytree(out / iid, kb / iid)
        with open(kb / 'items.csv', 'w', newline='') as f:
            w = csv.writer(f, lineterminator='\n'); w.writerow(['item_id', 'repo_short_name', 'language'])
            for r in keyrows[k:k + BATCH]: w.writerow([r['item_id'], r['repo'].split('/')[1], r['language']])
        (kb / 'TASK_R4.md').write_bytes(task)
    print(f'build: {len(ids)} items, {-(-len(ids) // BATCH)} Claude batches; scan findings (items with any): '
          f'{sum(1 for v in log.values() if v["scan"])}; kinds {dict(sum((collections.Counter(v["scan"]) for v in log.values()), collections.Counter()))}')


if __name__ == '__main__':
    stage = sys.argv[1] if len(sys.argv) > 1 else ''
    steps = {'collect': collect, 'resolve': resolve, 'pool': pool, 'sample': sample, 'build': build}
    if stage == 'all':
        for s in ('collect', 'resolve', 'pool', 'sample'): steps[s]()
    elif stage in steps: steps[stage]()
    else: sys.exit(__doc__)
