"""Build the R3 replication archive into a NEW directory. Read-only on the repository and the upstream clones; nothing upstream is executed.
Run: /usr/bin/python3 -I -B build_archive_r3.py --out "/run/media/afridi/Shared Data/R3_replication/<name>" [--rev HEAD] [--anonymize]
Layout:
  R3_silent_breaking/                      git archive of <rev> (plan, mining scripts + frozen pool/sample hashes + key, packages metadata
                                           and blind codes, collab tasks/reports/scripts, paper sources) -- no __pycache__
  R3_silent_breaking/packages/<pkg>/Bnnn/  the gitignored item excerpts, copied byte for byte (the package TREE freezes verify on them)
  R3_silent_breaking/packages/<pkg>/UPSTREAM_LICENSES/Bnnn.txt
                                           the upstream licence in force at the item's parent commit (kept OUTSIDE B* so the TREE hashes hold)
  LICENSES/item_licences.csv, SCAN_REPORT.txt, MANIFEST.sha256, README.md (+ ANONYMIZATION.md with --anonymize)
Exits non-zero if an item has no licence at its parent, a licence is restrictive/unknown, or a scan finds a secret or (anonymised) identity string.
Secret / anonymisation helpers are shared with the R1 builder (research/10_paper/reproduce/build_archive.py)."""
import argparse, csv, hashlib, io, json, shutil, subprocess, sys, tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
R3 = HERE.parents[1]; REPO = R3.parent
sys.path.insert(0, str(REPO / 'research/10_paper/reproduce')); sys.path.insert(0, str(REPO / 'research/10_paper'))
from build_archive import STUDY_ID, anonymize, classify, git_dir, secret_hit, show  # noqa: E402
from licence_at_parent import NAMES as R1_NAMES  # noqa: E402

NAMES = R1_NAMES + ('license.txt', 'License.txt', 'LICENSE.rst')
EXTRA_ID = [b'epsilonnotpstu']          # repository owner name (identity) -- must not appear in the anonymised copy
EXCLUDE_PARTS = ('__pycache__',)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--rev', default='HEAD'); ap.add_argument('--anonymize', action='store_true')
    a = ap.parse_args(); out = Path(a.out)
    if out.exists(): sys.exit(f'refuse: {out} exists')
    out.mkdir(parents=True); problems = []
    tar = subprocess.run(['git', '-C', str(REPO), 'archive', '--format=tar', a.rev, 'R3_silent_breaking'], capture_output=True, check=True).stdout
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
    key = {r['item_id']: r for r in csv.DictReader(open(R3 / 'mining/key/r3_key.csv', newline='', encoding='utf-8'))}
    if (R3 / 'mining/key/r3b_key.csv').is_file():          # R3b follow-up items D### -> R3 item -> repo/parent
        for r in csv.DictReader(open(R3 / 'mining/key/r3b_key.csv', newline='', encoding='utf-8')): key[r['r3b_id']] = key[r['r3_id']]
    lic, cache = {}, {}
    for pkg in sorted(p for p in (R3 / 'packages').iterdir() if p.is_dir()):
        for it in sorted(p for p in pkg.iterdir() if p.is_dir() and p.name[:1] in ('B', 'D') and p.name[1:].isdigit()):
            dst = out / 'R3_silent_breaking/packages' / pkg.name / it.name
            shutil.copytree(it, dst)
            r = key.get(it.name)
            if not r: problems.append(f'no key row for {pkg.name}/{it.name}'); continue
            rk = (r['repo'], r['parent'])
            if rk not in cache:
                gd = git_dir(r['repo']); found = None
                for n in (NAMES if gd else ()):
                    b = show(gd, r['parent'], n)
                    if b: found = (n, b); break
                cache[rk] = (found, show(gd, r['parent'], 'NOTICE') if gd else None, gd is not None)
            found, notice, have = cache[rk]
            if not found: problems.append(f'no licence at parent: {pkg.name}/{it.name} ({r["repo"]}; clone {"found" if have else "MISSING"})'); continue
            name, text = found; cls = classify(text)
            if cls in ('RESTRICTIVE', 'UNKNOWN'): problems.append(f'{pkg.name}/{it.name}: licence class {cls} ({r["repo"]})')
            ld = dst.parent / 'UPSTREAM_LICENSES'; ld.mkdir(exist_ok=True)
            (ld / f'{it.name}.txt').write_bytes(f'Upstream: {r["repo"]} at parent commit {r["parent"]} (file {name}); licence class: {cls}\n\n'.encode() + text
                                                + ((b'\n\n----- NOTICE -----\n' + notice) if notice else b''))
            row = lic.setdefault(it.name, {'item_id': it.name, 'packages': [], 'repo': r['repo'], 'parent_commit': r['parent'], 'licence_file': name, 'licence_class': cls})
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
    rep = [f'files scanned: {nfiles}', f'CRLF working-tree restorations: {crlf}', f'items with licence: {len(lic)} / {len(key)}',
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


README = """# Replication archive: silent behavioural changes in REST services (R3)

## Layout
- `R3_silent_breaking/plan/`: the frozen plan (`R3_PLAN.md`), the scorer and its self-test (`score_r3.py`, `test_score_r3.py`), the coder task (`TASK_R3.md`), deviations, audit, results, scorer output and the three freezes (`r3_plan_freeze.sha256`, `r3_packages_freeze.sha256`, `r3_outputs_freeze.sha256`).
- `R3_silent_breaking/mining/`: pool, sample, package-build, contract-projection and privacy scripts with their tests; the frozen pool inventory and its hashes (`freeze4.json`, `pool4_inventory.json`); the seeded sample (`sample4.json`, `freeze4_sample.json`); the key (`mining/key/r3_key.csv`: item -> repository, commit, parent, mechanical measures) and the build log.
- `R3_silent_breaking/packages/<pkg>/`: the blind packages exactly as coders saw them. `r3_blind` was coded by the two GPT-family coders (G1, G2); `r3_kb1`-`r3_kb10` hold the same items in batches for the two Claude-family coders (H1, H2). Each holds `TASK_R3.md`, `items.csv`, the item folders `Bnnn/` (diff, before/after files, projected contract) and the coders' `codes_*.csv` and reports.
- `R3_silent_breaking/packages/<pkg>/UPSTREAM_LICENSES/Bnnn.txt`: the upstream licence in force at the item's parent commit (it is kept outside `Bnnn/` so that the frozen package hashes still verify).
- `R3_silent_breaking/collab/`: task specifications, review reports and the coder-launch scripts.
- `R3_silent_breaking/paper/`: the paper (Markdown source, LaTeX generated by `latex/md2ieee.py`, the figure script and data) and `reproduce/`.
- `LICENSES/item_licences.csv`, `SCAN_REPORT.txt` (secret and identity scan at build time), `MANIFEST.sha256` (hash of every file).

## Reproducing every reported number
From `R3_silent_breaking/`:

    bash paper/reproduce/reproduce_r3.sh

This (1) verifies the plan, package and output freezes, (2) re-runs the frozen scorer on a scratch copy of the key and the codes and compares its output with `plan/r3_score_output.txt` and `plan/r3_scores.csv` byte for byte, and (3) runs the scorer self-test. Requirements: Python 3.11+ (standard library only), bash, GNU coreutils, and the `en_US.UTF-8` locale: the package TREE hashes were computed with `sort -z`, which collates by locale.

The figure: `/usr/bin/python3 -I -B paper/make_figure.py` (needs matplotlib) reads only `plan/r3_score_output.txt`.
The LaTeX: `/usr/bin/python3 -I -B paper/latex/md2ieee.py`, then `pdflatex main; bibtex main; pdflatex main; pdflatex main` in `paper/latex/` (IEEEtran class included).

## Re-coding with another model
Give a coder one package folder only, with its `TASK_R3.md`; never the key. Score with `plan/score_r3.py --root <copy>`.

## Re-mining
The upstream repositories and the commits are named in `mining/key/r3_key.csv`. Clone them and run the `mining/t53_*.py` scripts in the order documented in their headers; the pool rebuild is checked against the hashes in `mining/freeze4.json`. The full candidate pool (`mining/pool4.json`) and the document-history cache are not shipped (large, derivable).

## Licences
Upstream excerpts remain under their upstream licences (Apache-2.0, MIT, EPL-2.0, MPL-2.0, GPL-3.0, AGPL-3.0), as listed per item. Study code and data written by the authors: see the repository licence.

## Not included
Upstream clones; the full candidate pool; raw agent transcripts (they may echo upstream patches or commit attribution); third-party papers.
"""

if __name__ == '__main__':
    main()
