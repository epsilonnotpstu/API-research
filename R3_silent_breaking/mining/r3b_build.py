"""Build R3b packages (plan/R3b_PLAN.md): the 60 R3 items with GPT final observable_change=YES; item.md/diff/before/after copied
byte-for-byte from packages/r3_blind/<B id>; contract/ = ALL parent-commit files matching the R4 §3.1 file-name rule, untruncated
(e-mail, authorization-header and token redaction only). Read-only git on the bare clones; refuses to overwrite.
Run from R3_silent_breaking/: /usr/bin/python3 -I -B mining/r3b_build.py"""
import csv, hashlib, hmac, json, re, secrets, shutil, subprocess, sys
from pathlib import Path

B = Path(__file__).resolve().parents[1]; M = B / 'mining'; P = B / 'packages'
UP = Path('/run/media/afridi/Shared Data/api_research_upstream')
sys.path.insert(0, str(B / 'plan')); sys.path.insert(0, str(B.parent / 'R4_access_control/mining/claude'))
from score_r3 import load_codes, final  # noqa: E402
import r4p  # noqa: E402  (is_contract_path, scrub, flat)

AUTH_RX = re.compile(r'([Aa]uthorization: *(?:Bearer|Basic) +)[A-Za-z0-9+/=._-]{8,}')
EMAIL = re.compile(r'(?<![\w.+-])[\w.+-]{1,80}@[\w.-]{1,253}\.[A-Za-z]{2,24}')
BATCH = 15


def git(repo, *a):
    r = subprocess.run(['git', '--git-dir', str(UP / f'{repo}.git'), *a], capture_output=True)
    if r.returncode != 0: raise RuntimeError(f'git failed for {repo}: {a[:2]}')
    return r.stdout


def main():
    out = P / 'r3b_blind'
    if out.exists(): sys.exit('refuse: packages/r3b_blind exists')
    G1, G2 = load_codes([P / 'r3_blind/codes_G1.csv']), load_codes([P / 'r3_blind/codes_G2.csv'])
    r3ids = sorted(i for i in G1 if final(G1[i], G2[i])['observable_change'] == 'YES')
    key3 = {r['item_id']: r for r in csv.DictReader(open(M / 'key/r3_key.csv'))}
    salt_f = M / 'key/r3b_shuffle_salt.txt'
    if salt_f.exists(): sys.exit('refuse: r3b salt exists')
    salt_f.write_text(secrets.token_hex(32) + '\n'); salt = bytes.fromhex(salt_f.read_text().strip())
    order = sorted(r3ids, key=lambda i: hmac.new(salt, i.encode(), hashlib.sha256).hexdigest())
    out.mkdir(parents=True); keyrows, log = [], {}
    for n, bid in enumerate(order, 1):
        did = f'D{n:03d}'; k = key3[bid]; src = P / 'r3_blind' / bid; d = out / did; d.mkdir()
        for name in ('diff.patch', 'before', 'after'):
            s = src / name
            if s.is_dir(): shutil.copytree(s, d / name)
            elif s.is_file(): shutil.copy2(s, d / name)
        (d / 'item.md').write_bytes((src / 'item.md').read_bytes().replace(bid.encode(), did.encode()))
        tree = git(k['repo'], 'ls-tree', '-r', '--name-only', k['parent']).decode('utf-8', 'replace').splitlines()
        docs = sorted(p for p in tree if r4p.is_contract_path(p))
        (d / 'contract').mkdir(); idx = ['# Contract documents at the parent commit (complete, untruncated)', '', '| file | lines |', '|---|---|']
        for p in docs:
            t = git(k['repo'], 'show', f'{k["parent"]}:{p}').decode('utf-8', 'replace').replace('\r\n', '\n')
            t = AUTH_RX.sub(r'\1[REDACTED]', EMAIL.sub('[REDACTED]', r4p.scrub(t)))
            for sha in (k['commit'], k['parent']): t = t.replace(sha, '[REDACTED]')
            (d / 'contract' / r4p.flat(p)).write_text(t); idx.append(f'| `{r4p.flat(p)}` | {t.count(chr(10))} |')
        if not docs: idx.append('\nNo checked-in contract document exists at the parent commit.')
        (d / 'contract' / 'INDEX.md').write_text('\n'.join(idx) + '\n')
        log[did] = {'contract_docs': len(docs)}
        keyrows.append({'r3b_id': did, 'r3_id': bid, 'repo': k['repo'], 'language': k['language']})
    task = (B / 'plan/TASK_R3b.md').read_bytes()
    def items_csv(path, rows):
        with open(path, 'w', newline='') as f:
            w = csv.writer(f, lineterminator='\n'); w.writerow(['item_id', 'language'])
            for r in rows: w.writerow([r['r3b_id'], r['language']])
    items_csv(out / 'items.csv', keyrows); (out / 'TASK_R3b.md').write_bytes(task)
    with open(M / 'key/r3b_key.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(keyrows[0]), lineterminator='\n'); w.writeheader(); w.writerows(keyrows)
    (M / 'key/r3b_build_log.json').write_text(json.dumps(log, indent=1, sort_keys=True) + '\n')
    for j in range(0, len(keyrows), BATCH):
        kb = P / f'r3b_kb{j // BATCH + 1}'; kb.mkdir()
        for r in keyrows[j:j + BATCH]: shutil.copytree(out / r['r3b_id'], kb / r['r3b_id'])
        items_csv(kb / 'items.csv', keyrows[j:j + BATCH]); (kb / 'TASK_R3b.md').write_bytes(task)
    print(f'r3b build: {len(keyrows)} items, {-(-len(keyrows) // BATCH)} batches; items without contract: {sum(v["contract_docs"] == 0 for v in log.values())}; '
          f'docs {sum(v["contract_docs"] for v in log.values())}')


if __name__ == '__main__':
    main()
