"""Build the R1 replication archive (tiers A + B of REPLICATION_PACKAGE_PLAN.md) into a NEW directory.
Read-only on the repository and the upstream clones; nothing upstream is executed.
Run: /usr/bin/python3 -I -B build_archive.py --out "/run/media/afridi/Shared Data/R1_replication/<name>"
Layout:
  repo/        git archive of HEAD: research/08_experiments, 09_collab (PROTOCOL, tasks, reports, committed logs), 10_paper, RESEARCH_STATE.md
  items/<pkg>/ the gitignored item excerpt folders of every blind package, each with UPSTREAM-LICENSE.txt (+ NOTICE.txt if any)
  LICENSES/item_licences.csv   item_id, package(s), repo, parent commit, licence file, licence class
  SCAN_REPORT.txt, MANIFEST.sha256, README.md
Exits non-zero if an item has no licence at its parent, a licence is restrictive, or a scan finds a secret pattern."""
import argparse, csv, hashlib, io, json, os, re, shutil, subprocess, sys, tarfile
from pathlib import Path
csv.field_size_limit(sys.maxsize)

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]; REPO = RESEARCH.parent; X = RESEARCH / '08_experiments'; E = X / 'E2_labelling'; K = X / 'E7_mining/key'
UP = Path('/run/media/afridi/Shared Data/api_research_upstream'); EXT = X / '_external/upstream'
sys.path.insert(0, str(RESEARCH / '10_paper'))
from licence_at_parent import NAMES, RULES  # noqa: E402

PKGS = ['e6_blind', 'e7_blind', 'e8_write', 'e8_code', 'e8b_write', 'e8b_blind', 'e9_m1', 'e10_blind', 'e12_blind', 'e13_blind']
ITEM = re.compile(r'^[KXWVUQ]\d{2,3}$')
TIER_A = ['research/08_experiments', 'research/09_collab/PROTOCOL.md', 'research/09_collab/tasks', 'research/09_collab/reports',
          'research/09_collab/logs', 'research/09_collab/human_check', 'research/10_paper', 'research/RESEARCH_STATE.md']
ICED_NOTE = ('NOTE: this excerpt comes from an earlier version of the project that was released under the licence above '
             '(checked at the parent commit). The project\'s current licence is different and restrictive; it does not apply to this excerpt.\n')
SECRET = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----\s*\n[A-Za-z0-9+/=]{40,}|ghp_[A-Za-z0-9]{20}|AKIA[0-9A-Z]{16}')
AUTH = re.compile(r'[Aa]uthorization: *(?:Bearer|Basic) +([A-Za-z0-9+/=._-]{20,})')
# sha256 of known synthetic test tokens (E1 harness tests); the values themselves are never stored here
SYNTHETIC = {'944a6ad5f20da2203adf726cece7b369cd6725de077e29a3ede769c30f4d151d'}


# sha256 of the first 15 characters of a known benchmark demo credential (the value itself is never stored)
KNOWN_PREFIX = {'dd2eaf50560d39c2b280f9ca7671b8000b8d582afcc913f88df2028dc16cd31d'}
B64 = re.compile(r'[A-Za-z0-9+/]{15,}={0,2}')


def secret_hit(t):
    if SECRET.search(t): return True
    if any(hashlib.sha256(m.group(0)[:15].encode()).hexdigest() in KNOWN_PREFIX for m in B64.finditer(t)): return True
    return any(hashlib.sha256(m.group(1).encode()).hexdigest() not in SYNTHETIC for m in AUTH.finditer(t))


STUDY_ID = re.compile(r'(?i)afridi')


def git_dir(repo):
    for p in (UP / f'{repo}.git', EXT / repo / '.git', EXT / repo, EXT / f'{repo}.git'):
        if p.exists() and subprocess.run(['git', '--git-dir', str(p), 'rev-parse', '--git-dir'], capture_output=True).returncode == 0:
            return p
    return None


def show(gd, rev, path):
    r = subprocess.run(['git', '--git-dir', str(gd), 'show', f'{rev}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def classify(text):
    head = text[:4000].decode('utf-8', 'replace').lower()
    for pat, lab in RULES:
        if pat.lower() in head: return lab
    return 'UNKNOWN'


def item_sources():
    """item_id -> (repo, parent)"""
    src = {}
    for f in ('e7_key.csv', 'e8b_key.csv', 'e10_key.csv', 'e12_key.csv', 'e13_key.csv'):
        for r in csv.DictReader(open(K / f, newline='')):
            src[r['item_id']] = (r['repo'].split('/')[-1], r['parent_commit'])
    for it in json.load(open(X / 'E6_realfix/e6_build_log.json'))['items']:
        src.setdefault(it['item_id'], (it['repo'].split('/')[-1], it['parent_commit']))
    return src


ANON = [(re.compile(r'/tmp/claude-\d+/[^\s"\'`)<>]*'), '<TMP>'), (re.compile(r'/home/afridi/Documents/API research'), '<REPO_ROOT>'),
        (re.compile(r'/run/media/afridi/Shared Data'), '<DATA_ROOT>'), (re.compile(r'/home/afridi'), '<HOME>'),
        (re.compile(r'-home-afridi-[A-Za-z0-9-]*'), '<PROJECT>'), (re.compile(r'(?i)afridi'), 'anonymous')]


def anonymize(root):
    changed = []
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        b = p.read_bytes()
        try: t = b.decode('utf-8')
        except UnicodeDecodeError: continue
        n = t
        for rx, rep in ANON: n = rx.sub(rep, n)
        if n != t: p.write_text(n, encoding='utf-8'); changed.append(str(p.relative_to(root)))
    return changed


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--rev', default='HEAD'); ap.add_argument('--anonymize', action='store_true'); a = ap.parse_args()
    out = Path(a.out)
    if out.exists(): sys.exit(f'refuse: {out} exists')
    out.mkdir(parents=True)
    problems = []
    # tier A
    tar = subprocess.run(['git', '-C', str(REPO), 'archive', '--format=tar', a.rev, *TIER_A], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        members = [m for m in t.getmembers() if '__pycache__' not in m.name and not m.name.endswith('.pyc')]
        t.extractall(out / 'repo', members=members, filter='data')
    crlf = 0
    for m in members:
        if not m.isfile(): continue
        a_ = out / 'repo' / m.name; w_ = REPO / m.name
        if w_.is_file():
            wb, ab = w_.read_bytes(), a_.read_bytes()
            if wb != ab and wb.replace(b'\r\n', b'\n') == ab:
                a_.write_bytes(wb); crlf += 1     # freezes hash the working-tree bytes (Codex CSVs use CRLF)
    # tier B
    src = item_sources(); licrows = {}; cache = {}
    for pkg in PKGS:
        d = E / pkg
        for it in sorted(p.name for p in d.iterdir() if p.is_dir() and ITEM.match(p.name)):
            dst = out / 'items' / pkg / it
            shutil.copytree(d / it, dst)
            if it not in src: problems.append(f'no source for {pkg}/{it}'); continue
            repo, parent = src[it]
            if (repo, parent) not in cache:
                gd = git_dir(repo); found = None
                if gd:
                    for n in NAMES:
                        b = show(gd, parent, n)
                        if b: found = (n, b); break
                notice = show(gd, parent, 'NOTICE') if gd else None
                cache[(repo, parent)] = (found, notice, gd is not None)
            found, notice, have = cache[(repo, parent)]
            if not found:
                problems.append(f'no licence at parent for {pkg}/{it} ({repo}, clone {"found" if have else "MISSING"})'); continue
            name, text = found; cls = classify(text)
            if cls in ('RESTRICTIVE', 'UNKNOWN'): problems.append(f'{pkg}/{it}: licence class {cls} ({repo})')
            (dst / 'UPSTREAM-LICENSE.txt').write_bytes(
                f'Upstream: {repo} at parent commit {parent} (file {name}); licence class: {cls}\n'.encode()
                + (ICED_NOTE.encode() if repo == 'Iced-Latte' else b'') + b'\n' + text)
            if notice: (dst / 'UPSTREAM-NOTICE.txt').write_bytes(notice)
            r = licrows.setdefault(it, {'item_id': it, 'packages': [], 'repo': repo, 'parent_commit': parent, 'licence_file': name, 'licence_class': cls})
            r['packages'].append(pkg)
    (out / 'LICENSES').mkdir()
    with open(out / 'LICENSES/item_licences.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['item_id', 'packages', 'repo', 'parent_commit', 'licence_file', 'licence_class'], lineterminator='\n'); w.writeheader()
        for r in sorted(licrows.values(), key=lambda r: r['item_id']): w.writerow({**r, 'packages': ';'.join(r['packages'])})
    if a.anonymize:
        ch = anonymize(out)
        (out / 'ANONYMIZATION.md').write_text(
            '# Anonymised review copy\n\nLocal path and user-name strings were replaced by placeholders (<REPO_ROOT>, <DATA_ROOT>, <HOME>, <TMP>, <PROJECT>, anonymous) '
            f'in {len(ch)} text files. Scorers, keys, codes and labels are unaffected. Three frozen task files contain such paths '
            '(research/09_collab/tasks/T48.md, T49.md, T50.md), so their entries in the E10/E12/E13 plan freezes do not verify in this copy; '
            'the de-anonymised archive released after review verifies them. Files changed:\n\n' + '\n'.join('- ' + c for c in ch) + '\n')
    # scans (counts and paths only; never the matched text)
    hits, idhits, nfiles = [], [], 0
    for p in sorted(out.rglob('*')):
        if not p.is_file(): continue
        nfiles += 1; t = p.read_bytes().decode('utf-8', 'replace')
        if secret_hit(t): hits.append(str(p.relative_to(out)))
        if STUDY_ID.search(t): idhits.append(str(p.relative_to(out)))
    rep = [f'files scanned: {nfiles}', f'secret-pattern files: {len(hits)}', *[f'  {h}' for h in hits],
           f'author-identity files: {len(idhits)}' + ('' if a.anonymize else ' (expected in the de-anonymised archive)'), *([f'  {h}' for h in idhits] if a.anonymize else []), 'licence classes: ' + json.dumps(
               {c: sum(r['licence_class'] == c for r in licrows.values()) for c in sorted({r['licence_class'] for r in licrows.values()})}),
           f'problems: {len(problems)}', *[f'  {p}' for p in problems]]
    (out / 'SCAN_REPORT.txt').write_text('\n'.join(rep) + '\n')
    (out / 'README.md').write_text(README)
    with open(out / 'MANIFEST.sha256', 'w') as m:
        for p in sorted(out.rglob('*')):
            if p.is_file() and p.name != 'MANIFEST.sha256':
                m.write(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out)}\n')
    print('\n'.join(rep))
    sys.exit(1 if hits or problems or (a.anonymize and idhits) else 0)


README = """# Replication archive: "Spec or Bug? Predicting Which Side Developers Repair When a REST API and Its Contract Disagree"

## Layout
- `repo/`: the study repository at the release tag.
  - `research/08_experiments/`: plans, amendments, deviations, results, scorers and self-tests, keys, blind codes and labels, freezes, and the mining and build scripts.
  - `research/09_collab/`: task specifications, reports and committed run logs.
  - `research/10_paper/`: the paper sources, figures and licence review.
- `items/<package>/<item>/`: the upstream source excerpts each blind role saw.
  - Every item folder carries `UPSTREAM-LICENSE.txt`: the licence in force at the item's parent commit, with the source commit named. Some also carry `UPSTREAM-NOTICE.txt`.
  - Excerpts are unmodified, except that privacy and credential redactions are marked `[REDACTED]`.
- `LICENSES/item_licences.csv`: the licence per item.
- `SCAN_REPORT.txt`: the secret and identity scan run at build time.
- `MANIFEST.sha256`: a hash of every file.

## Re-scoring all reported numbers
Copy `items/<package>/*` back into `repo/research/08_experiments/E2_labelling/<package>/`. The scorers do not need them; only re-coding does.

Then, from `repo/research/`, run:

    bash 10_paper/reproduce/reproduce_scores.sh

This re-runs every frozen scorer (E6–E13) on a scratch copy and compares each output with the committed one byte for byte.

    /usr/bin/python3 -I -B 10_paper/reproduce/check_freezes.py

This verifies every pre-registration and package freeze. Two post-freeze changes are documented: E12 deviation D1, and E7 amendment A3 appended.

## Re-coding with another model
Use the package folders unchanged, with their `TASK_*.md` files, and the scorers in the matching experiment folder. The keys (`research/08_experiments/E7_mining/key/`) hold the repair directions. Keep them away from coders.

## Licences
Excerpts remain under their upstream licences: Apache-2.0, MIT, EPL-2.0, MPL-2.0, GPL-3.0, AGPL-3.0 or CC BY-NC 4.0, as listed per item. Items under CC BY-NC 4.0 are for non-commercial research use only. Study code and data written by the authors: see the repository licence.

## Not included
- Upstream clones: re-clone them from the repositories named in the keys, using the recorded commits.
- Large derived candidate pools: their hashes are in the `freeze*.json` files, and they rebuild deterministically from the mining scripts.
- Raw agent transcripts that echo upstream patches or attribution.
"""

if __name__ == '__main__':
    main()
