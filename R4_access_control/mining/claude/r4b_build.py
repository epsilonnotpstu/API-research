"""Build R4b packages (plan/R4b_PLAN.md): the 102 R4 items with GPT final ac_relevant=YES, with FULL contracts and corrected item.md redaction.
Reuses r4p.py helpers (numstat, scrub, red, clean_advisory, flat, is_contract_path, is_source_path). Refuses to overwrite.
Run from R4_access_control/: /usr/bin/python3 -I -B mining/claude/r4b_build.py"""
import csv, hashlib, hmac, json, re, secrets, shutil, sys
from pathlib import Path

H = Path(__file__).resolve().parent; B = H.parents[1]; M = B / 'mining'; P = B / 'packages'
sys.path.insert(0, str(H)); sys.path.insert(0, str(B / 'plan'))
import r4p  # noqa: E402
from score_r4 import load_codes, final  # noqa: E402

BATCH = 17
AUTH_RX = re.compile(r'([Aa]uthorization: *(?:Bearer|Basic) +)[A-Za-z0-9+/=._-]{8,}')   # R4b-F1: PoC/example tokens


def main():
    out = P / 'r4b_blind'
    if out.exists(): sys.exit('refuse: packages/r4b_blind exists')
    G1, G2 = load_codes([P / 'r4_blind/codes_G1.csv']), load_codes([P / 'r4_blind/codes_G2.csv'])
    r4ids = sorted(i for i in G1 if final(G1[i], G2[i])['ac_relevant'] == 'YES')
    key4 = {r['item_id']: r for r in csv.DictReader(open(M / 'key/r4_key.csv'))}
    advs = {a['ghsa_id']: a for a in json.load(open(M / 'advisories.json'))}
    pool = {it['item_key']: it for it in json.load(open(M / 'sample.json'))}
    salt_f = M / 'key/r4b_shuffle_salt.txt'
    if salt_f.exists(): sys.exit('refuse: r4b salt exists')
    salt_f.write_text(secrets.token_hex(32) + '\n'); salt = bytes.fromhex(salt_f.read_text().strip())
    order = sorted(r4ids, key=lambda i: hmac.new(salt, i.encode(), hashlib.sha256).hexdigest())
    out.mkdir(parents=True); keyrows = []; log = {}
    for n, r4id in enumerate(order, 1):
        cid = f'C{n:03d}'; k = key4[r4id]; ghsas = k['ghsa_ids'].split(';'); it = pool[ghsas[0]]
        o, rp = k['repo'].split('/'); gd = r4p.gitdir(o, rp); shas = [k['fix_sha'], k['parent_sha']]
        d = out / cid; d.mkdir()
        ns = r4p.numstat(gd, k['parent_sha'], k['fix_sha'])
        srcrows = sorted([x for x in ns if r4p.is_source_path(x['path'])], key=lambda x: (-(x['a'] + x['d']), x['path']))
        files = srcrows[:r4p.MAX_FILES]
        a = advs[ghsas[0]]
        md = [f'# {cid}', '', f'- Repository: {rp}', f'- Language: {k["language"]}', f'- CWE: {", ".join(k["cwes"].split(";")) or "none listed"}', '',
              '## Advisory summary', r4p.clean_advisory(a['summary']), '', '## Advisory description', r4p.clean_advisory(a['description']), '',
              '## Touched source files (non-test)'] + [f'- `{x["path"]}`' for x in srcrows]
        for g in ghsas[1:]: md += ['', '## Further advisory fixed by the same commit (summary)', r4p.clean_advisory(advs[g]['summary'])]
        txt = AUTH_RX.sub(r'\1[REDACTED]', r4p.scrub('\n'.join(md) + '\n'))
        for s in shas: txt = txt.replace(s, '[REDACTED]').replace(s[:7], '[REDACTED]')
        (d / 'item.md').write_text(txt)                      # no line-level attribution redaction of advisory text (R4b fix)
        paths = sorted({x['path'] for x in srcrows} | {x['old'] for x in srcrows})
        diff = r4p.git(gd, 'diff', '-M', '--no-ext-diff', '--no-textconv', k['parent_sha'], k['fix_sha'], '--', *paths, binary=True)
        (d / 'diff.patch').write_bytes(r4p.red(diff, shas))
        for side, rev in (('before', k['parent_sha']), ('after', k['fix_sha'])):
            (d / side).mkdir()
            for x in files:
                if (side == 'before' and x['status'] == 'A') or (side == 'after' and x['status'] == 'D'): continue
                p = x['old'] if side == 'before' else x['path']
                (d / side / r4p.flat(p)).write_bytes(r4p.red(r4p.git(gd, 'show', f'{rev}:{p}', binary=True, check=True, tries=3), shas))
        (d / 'contract').mkdir(); idx = ['# Contract documents at the vulnerable version (complete, untruncated)', '', '| file | lines |', '|---|---|']
        for p in it['contract_paths']:
            b = r4p.git(gd, 'show', f'{k["parent_sha"]}:{p}', binary=True, check=True, tries=3)
            t = r4p.scrub(b.decode('utf-8', 'replace').replace('\r\n', '\n'))
            t = AUTH_RX.sub(r'\1[REDACTED]', r4p.PRIV.EMAIL.sub('[REDACTED]', t))
            (d / 'contract' / r4p.flat(p)).write_text(t)
            idx.append(f'| `{r4p.flat(p)}` (repo path `{p}`) | {t.count(chr(10))} |')
        (d / 'contract' / 'INDEX.md').write_text('\n'.join(idx) + '\n')
        log[cid] = {'contract_docs': len(it['contract_paths']), 'contract_lines': sum(1 for f in (d / 'contract').iterdir() for _ in open(f, errors='replace'))}
        keyrows.append({'r4b_id': cid, 'r4_id': r4id, 'repo': k['repo'], 'language': k['language']})
    with open(out / 'items.csv', 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['item_id', 'repo_short_name', 'language'])
        for r in keyrows: w.writerow([r['r4b_id'], r['repo'].split('/')[1], r['language']])
    task = (B / 'plan/TASK_R4b.md').read_bytes(); (out / 'TASK_R4b.md').write_bytes(task)
    with open(M / 'key/r4b_key.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(keyrows[0]), lineterminator='\n'); w.writeheader(); w.writerows(keyrows)
    (M / 'key/r4b_build_log.json').write_text(json.dumps(log, indent=1, sort_keys=True) + '\n')
    ids = [r['r4b_id'] for r in keyrows]
    for j in range(0, len(ids), BATCH):
        kb = P / f'r4b_kb{j // BATCH + 1}'; kb.mkdir()
        for cid in ids[j:j + BATCH]: shutil.copytree(out / cid, kb / cid)
        with open(kb / 'items.csv', 'w', newline='') as f:
            w = csv.writer(f, lineterminator='\n'); w.writerow(['item_id', 'repo_short_name', 'language'])
            for r in keyrows[j:j + BATCH]: w.writerow([r['r4b_id'], r['repo'].split('/')[1], r['language']])
        (kb / 'TASK_R4b.md').write_bytes(task)
    tot = sum(v['contract_lines'] for v in log.values())
    print(f'r4b build: {len(ids)} items, {-(-len(ids) // BATCH)} Claude batches; contract docs {sum(v["contract_docs"] for v in log.values())}, '
          f'total contract lines {tot}, max per item {max(v["contract_lines"] for v in log.values())}')


if __name__ == '__main__':
    main()
