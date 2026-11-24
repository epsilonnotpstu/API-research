"""Build the R3 replication archive into a NEW directory. Read-only on the repository and the upstream clones; nothing upstream is executed.
Run: /usr/bin/python3 -I -B build_archive_r4.py --out "/run/media/afridi/Shared Data/R4_replication/<name>" [--rev HEAD] [--anonymize]
Layout:
  R4_access_control/                      git archive of <rev> (plan, mining scripts + frozen pool/sample hashes + key, packages metadata
                                           and blind codes, collab tasks/reports/scripts, paper sources) -- no __pycache__
  R4_access_control/packages/<pkg>/Annn/  the gitignored item excerpts, copied byte for byte (the package TREE freezes verify on them)
  R4_access_control/packages/<pkg>/UPSTREAM_LICENSES/Annn.txt
                                           the upstream licence in force at the item's parent commit (kept OUTSIDE A* so the TREE hashes hold)
  LICENSES/item_licences.csv, SCAN_REPORT.txt, MANIFEST.sha256, README.md (+ ANONYMIZATION.md with --anonymize)
Exits non-zero if an item has no licence at its parent, a licence is restrictive/unknown, or a scan finds a secret or (anonymised) identity string.
Secret / anonymisation helpers are shared with the R1 builder (research/10_paper/reproduce/build_archive.py)."""
import argparse, csv, hashlib, io, json, re, shutil, subprocess, sys, tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
R3 = HERE.parents[1]; REPO = R3.parent; R4G = R3 / 'mining/cache/git'
sys.path.insert(0, str(REPO / 'research/10_paper/reproduce')); sys.path.insert(0, str(REPO / 'research/10_paper'))
from build_archive import STUDY_ID, anonymize, classify, git_dir, secret_hit, show  # noqa: E402
from licence_at_parent import NAMES as R1_NAMES  # noqa: E402

NAMES = R1_NAMES + ('license.txt', 'License.txt', 'LICENSE.rst', 'LICENSING.markdown')
EXTRA_RULES = [('server side public license', 'RESTRICTIVE'), ('non-commercial license', 'RESTRICTIVE'), ('lesser general public license', 'LGPL'), ('the postgresql license', 'PostgreSQL')]


def classify4(text, name):
    head = text[:4000].decode('utf-8', 'replace').lower()
    for pat, lab in EXTRA_RULES:
        if pat in head: return lab
    c = classify(text)
    if c == 'UNKNOWN' and 'all rights reserved' in head: return 'RESTRICTIVE'   # proprietary EULA
    return c
EXTRA_ID = [b'epsilonnotpstu']          # repository owner name (identity) -- must not appear in the anonymised copy
EXCLUDE_PARTS = ('__pycache__',)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--rev', default='HEAD'); ap.add_argument('--anonymize', action='store_true')
    a = ap.parse_args(); out = Path(a.out)
    if out.exists(): sys.exit(f'refuse: {out} exists')
    out.mkdir(parents=True); problems = []
    tar = subprocess.run(['git', '-C', str(REPO), 'archive', '--format=tar', a.rev, 'R4_access_control'], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        members = [m for m in t.getmembers() if not any(x in m.name for x in EXCLUDE_PARTS) and not m.name.endswith('.pyc')]
        t.extractall(out, members=members, filter='data')
    crlf = 0
    for m in members:
        if not m.isfile(): continue
        a_, w_ = out / m.name, REPO / m.name
        if w_.is_file():
            wb, ab = w_.read_bytes(), a_.read_bytes()
            if wb != ab and wb.replace(b'\r\n', b'\n') == ab: a_.write_bytes(wb); crlf += 1   # freezes hash working-tree bytes
    # public advisory text: PoC example tokens (Authorization headers, AWS example keys, PEM blocks) redacted in the archive copy;
    # the original is re-downloadable from GitHub and its sha256 is recorded in mining/pool_freeze.json
    adv = out / 'R4_access_control/mining/advisories.json'
    if adv.is_file():
        t = adv.read_text(encoding='utf-8')
        t = re.sub(r'([Aa]uthorization: *(?:Bearer|Basic) +)[A-Za-z0-9+/=._-]{8,}', r'\1[REDACTED]', t)
        t = re.sub(r'(?:AKIA|ASIA)[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|glpat-[A-Za-z0-9_-]{20}', '[REDACTED]', t)
        t = re.sub(r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----', '[REDACTED PEM]', t, flags=re.S)
        adv.write_text(t, encoding='utf-8')
    key = {r['item_id']: r for r in csv.DictReader(open(R3 / 'mining/key/r4_key.csv', newline='', encoding='utf-8'))}
    kb4b = R3 / 'mining/key/r4b_key.csv'                     # R4b follow-up items C### -> R4 item -> repo/parent
    if kb4b.is_file():
        for r in csv.DictReader(open(kb4b, newline='', encoding='utf-8')): key[r['r4b_id']] = key[r['r4_id']]
    lic, cache, withheld = {}, {}, set()
    for pkg in sorted(p for p in (R3 / 'packages').iterdir() if p.is_dir()):
        for it in sorted(p for p in pkg.iterdir() if p.is_dir() and p.name[:1] in ('A', 'C') and p.name[1:].isdigit()):
            dst = out / 'R4_access_control/packages' / pkg.name / it.name
            r = key.get(it.name)
            if not r: problems.append(f'no key row for {pkg.name}/{it.name}'); continue
            rk = (r['repo'], r['parent_sha'])
            if rk not in cache:
                o_, r_ = r['repo'].split('/'); gd = R4G / f'{o_}__{r_}.git'; gd = gd if gd.is_dir() else None; found = None
                for n in (NAMES if gd else ()):
                    b = show(gd, r['parent_sha'], n)
                    if b: found = (n, b); break
                cache[rk] = (found, show(gd, r['parent_sha'], 'NOTICE') if gd else None, gd is not None)
            found, notice, have = cache[rk]
            if not found: problems.append(f'no licence at parent: {pkg.name}/{it.name} ({r["repo"]}; clone {"found" if have else "MISSING"})'); continue
            name, text = found; cls = classify4(text, name)
            if name == 'LICENSING.markdown':                     # Liferay dual licence: ship the LGPL text alongside
                lg = show(gd, r['parent_sha'], 'LICENSES/LGPL-2.1-or-later.txt')
                if lg: text += b'\n\n----- LICENSES/LGPL-2.1-or-later.txt -----\n' + lg
            if cls == 'UNKNOWN': problems.append(f'{pkg.name}/{it.name}: licence class UNKNOWN ({r["repo"]})')
            if cls == 'RESTRICTIVE':
                # withhold upstream excerpts; keep item.md (advisory text, GitHub Advisory Database, CC-BY-4.0) and record original hashes
                dst.mkdir(parents=True)
                shutil.copy2(it / 'item.md', dst / 'item.md')
                with open(dst.parent / 'WITHHELD.sha256', 'a') as wf:
                    for f in sorted((x for x in it.rglob('*') if x.is_file() and x.name != 'item.md'), key=lambda x: x.relative_to(it.parent).as_posix().encode()):
                        wf.write(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(it.parent).as_posix()}\n')
                withheld.add(it.name)
            else:
                shutil.copytree(it, dst)
            ld = dst.parent / 'UPSTREAM_LICENSES'; ld.mkdir(exist_ok=True)
            (ld / f'{it.name}.txt').write_bytes(f'Upstream: {r["repo"]} at parent commit {r["parent_sha"]} (file {name}); licence class: {cls}\n\n'.encode() + text
                                                + ((b'\n\n----- NOTICE -----\n' + notice) if notice else b''))
            row = lic.setdefault(it.name, {'item_id': it.name, 'packages': [], 'repo': r['repo'], 'parent_commit': r['parent_sha'], 'licence_file': name, 'licence_class': cls})
            row['packages'].append(pkg.name)
    (out / 'LICENSES').mkdir()
    with open(out / 'LICENSES/item_licences.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['item_id', 'packages', 'repo', 'parent_commit', 'licence_file', 'licence_class'], lineterminator='\n'); w.writeheader()
        for r in sorted(lic.values(), key=lambda r: r['item_id']): w.writerow({**r, 'packages': ';'.join(r['packages'])})
    ch = []
    if a.anonymize:
        ch = anonymize(out)
        for p in sorted(out.rglob('*')):       # owner name (e.g. a git remote URL in a log line)
            if p.is_file():
                b = p.read_bytes(); n = b
                for s in EXTRA_ID: n = n.replace(s, b'anonymous-owner')
                if n != b: p.write_bytes(n); ch.append(str(p.relative_to(out)))
        (out / 'ANONYMIZATION.md').write_text(
            '# Anonymised review copy\n\nLocal path, user-name and repository-owner strings were replaced by placeholders (<REPO_ROOT>, <DATA_ROOT>, <HOME>, <TMP>, '
            '<PROJECT>, anonymous, anonymous-owner). Files changed (their freeze entries, if any, verify only in the de-anonymised archive):\n\n'
            + '\n'.join('- ' + c for c in sorted(set(ch))) + '\n')
    hits, idhits, nfiles = [], [], 0
    for p in sorted(out.rglob('*')):
        if not p.is_file(): continue
        nfiles += 1; b = p.read_bytes(); t = b.decode('utf-8', 'replace')
        if secret_hit(t): hits.append(str(p.relative_to(out)))
        if STUDY_ID.search(t) or any(s in b for s in EXTRA_ID): idhits.append(str(p.relative_to(out)))
    classes = {c: sum(r['licence_class'] == c for r in lic.values()) for c in sorted({r['licence_class'] for r in lic.values()})}
    rep = [f'files scanned: {nfiles}', f'CRLF working-tree restorations: {crlf}', f'items with licence: {len(lic)} (R4 {sum(i.startswith("A") for i in lic)}, R4b {sum(i.startswith("C") for i in lic)})', f'items with upstream excerpts withheld (restrictive licence): {sorted(withheld)}',
           f'secret-pattern files: {len(hits)}', *[f'  {h}' for h in hits],
           f'author-identity files: {len(idhits)}' + ('' if a.anonymize else ' (expected in the de-anonymised archive)'), *([f'  {h}' for h in idhits] if a.anonymize else []),
           'licence classes: ' + json.dumps(classes), f'problems: {len(problems)}', *[f'  {p}' for p in problems]]
    (out / 'SCAN_REPORT.txt').write_text('\n'.join(rep) + '\n')
    (out / 'README.md').write_text(README)
    with open(out / 'MANIFEST.sha256', 'w') as m:
        for p in sorted(out.rglob('*')):
            if p.is_file() and p.name != 'MANIFEST.sha256': m.write(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out)}\n')
    print('\n'.join(rep))
    sys.exit(1 if hits or problems or (a.anonymize and idhits) else 0)


README = """# Replication archive: real access-control vulnerabilities vs contract-driven black-box testing (R4)

## Layout
- **`R4_access_control/plan/`.** It contains:
  - the frozen plan `R4_PLAN.md`;
  - the scorer `score_r4.py` and its self-test `test_score_r4.py`;
  - the coder task `TASK_R4.md`;
  - the deviations: D1 (two independent pipelines), F1–F4 (mechanical fixes before coding), P1 (resume);
  - the audit, the results and the scorer output;
  - the three freezes;
  - `R4_DEVIATIONS_at_package_freeze.md`, the deviations file as frozen with the packages. The live file has P1 appended.
- **`R4_access_control/mining/`.** It contains:
  - `claude/r4p.py`, the primary pipeline;
  - `r4_*.py` with `test_r4.py`, Codex's independent implementation (56 tests);
  - `advisories.json`, the normalised GitHub advisories;
  - `resolved.json`, `pool.json`, `pool_inventory.json` and `pool_freeze.json`;
  - `sample.json` and `sample_freeze.json`;
  - the key `mining/key/r4_key.csv`, which maps each item to its advisory ids, repository, fix and parent commit, and the mechanical measures;
  - the build log.
- **`R4_access_control/packages/`.**
  - `r4_blind` was coded by G1 and G2 (GPT family).
  - `r4_kb1` to `r4_kb9` hold the same items in batches, coded by H1 and H2 (Claude family).
  - Each item folder `Annn/` holds `item.md` (the advisory, redacted), `diff.patch`, `before/`, `after/` and `contract/`.
  - The upstream licence at the vulnerable (parent) commit is in `UPSTREAM_LICENSES/Annn.txt`, outside `A*`, so the TREE hashes hold.
- **`R4_access_control/collab/`.** Task specifications (T56b, T57, T58), the reports, the D1 comparison, and the coder-launch and audit scripts.
- **`R4_access_control/paper/`.** The paper (Markdown, LaTeX via `latex/md2ieee.py`), the figure script and data, and `reproduce/`.
- **Top level.** `LICENSES/item_licences.csv`, `SCAN_REPORT.txt` and `MANIFEST.sha256`.

## Reproducing every number
From `R4_access_control/`, run:

    bash paper/reproduce/reproduce_r4.sh

The script does three things:
1. It verifies the plan, package and output freezes. Package TREE hashes use a byte-order sort (`LC_ALL=C`).
2. It re-runs the frozen scorer on a scratch copy of the key and the codes, and compares the result with `plan/r4_score_output.txt` and `plan/r4_scores.csv` byte for byte.
3. It runs the scorer self-test.

It needs Python 3.11+ (standard library only), bash and GNU coreutils.

## Re-mining
The mining needs network access, `gh` and git. Run `mining/claude/r4p.py collect|resolve|pool|sample|build`. The advisory database changes over time, so compare the result with `mining/pool_freeze.json`.

## Licences
Upstream excerpts remain under their upstream licences, as listed per item. Study code and data written by the authors fall under the repository licence.

## Advisory text
`mining/advisories.json` is GitHub Advisory Database content (CC-BY-4.0). In this archive copy, example credentials from the advisories' own proofs of concept are replaced by `[REDACTED]`: Authorization header values, AWS example keys and PEM blocks. The original file can be re-downloaded from GitHub, and its sha256 is in `mining/pool_freeze.json`.

## Not included
- the git caches of the upstream repositories;
- raw agent transcripts.
"""

if __name__ == '__main__':
    main()
