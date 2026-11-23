#!/usr/bin/python3
"""Build blinded R4 packages. Only source blobs/diffs, never commit metadata."""
from collections import Counter
import csv
import hashlib
import hmac
import io
from pathlib import Path, PurePosixPath
import re
import secrets
import shutil
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r4_common import (ROOT, PipelineError, cli, diff, git, is_source_path,
                       read_json, refuse_existing, repo_cache, sha256_file,
                       verify_hashes, write_json)

# Read-only reuse of the R3 privacy implementation; no dependency on R4's
# independent comparison implementation or any coder/scorer material.
sys.path.insert(0, str(ROOT.parent / 'R3_silent_breaking/mining'))
import t53_privacy as privacy

URL = re.compile(r'https?://[^\s<>\"\x27\[\]]+', re.I)
CREDIT = re.compile(r'\b(?:credits?|thanks|reported\s+by|discovered\s+by|found\s+by)\b', re.I)
SECRET_PREFIX = re.compile(
    r'(?<![\w])(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|'
    r'xox[baprs]-[A-Za-z0-9-]{10,}|(?:AKIA|ASIA)[A-Z0-9]{16}|'
    r'sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{30,}|'
    r'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,})(?![\w])')
KEY_COLUMNS = ('item_id ghsa_ids repo ecosystem language fix_sha parent_sha cwes severity '
               'published_at fix_lines fix_touches_contract fix_touches_annotation '
               'fix_silent test_in_fix n_contract_docs').split()


def redact(text, counts=None, item=False):
    """Redact values, logging only kind counts. Preserve source line counts."""
    counts = counts if counts is not None else Counter()

    def substitute(pattern, replacement, text, kind):
        text, n = pattern.subn(replacement, text)
        counts[kind] += n
        return text

    if item:
        def link(match):
            value = match[0]
            if (any(s in value.lower() for s in ('/commit/', '/pull/', '/compare/', '/releases/'))
                    or re.search(r'(?:GHSA-[\w-]+|CVE-\d{4}-\d+)', value, re.I)):
                counts['link'] += 1
                return '[LINK]'
            return value
        text = URL.sub(link, text)
        lines = []
        for line in text.splitlines(keepends=True):
            if CREDIT.search(line):
                counts['credit'] += 1
                lines.append('[CREDIT REDACTED]' + ('\n' if line.endswith('\n') else ''))
            else:
                lines.append(line)
        text = ''.join(lines)
    text = substitute(SECRET_PREFIX, '[REDACTED]', text, 'credential_prefix')
    # R3 interprets a leading '-' as a diff marker. A raw PEM header also
    # starts with '-', so handle full blocks before passing text to R3.
    lines, in_key = [], False
    for line in text.splitlines(keepends=True):
        if privacy.KEY_HEADER.search(line):
            in_key = True
            counts['private_key_block'] += 1
        ending = in_key and '-----END ' in line
        if in_key:
            prefix = line[:1] if line[:1] in {'+', '-'} else ''
            lines.append(prefix + '[REDACTED]' + ('\n' if line.endswith('\n') else ''))
        else:
            lines.append(line)
        if ending:
            in_key = False
    text = ''.join(lines)
    # The same privacy rules as R3, with occurrence counts before replacement.
    for kind, pattern in [('email', privacy.EMAIL), ('attribution', privacy.ATTRIBUTION),
                          ('auth', privacy.AUTH), ('private_key', privacy.KEY_HEADER),
                          ('credential_assignment', privacy.ASSIGNMENT),
                          ('credential_unquoted', privacy.UNQUOTED),
                          ('credential_query', privacy.QUERY), ('url_auth', privacy.URL_AUTH),
                          ('quoted_encoded', privacy.QUOTED_ENCODED),
                          ('encoded', privacy.ENCODED), ('hex', privacy.HEX),
                          ('date', privacy.DATE), ('text_date', privacy.TEXT_DATE),
                          ('source_hosting', privacy.HOSTING)]:
        counts[kind] += len(pattern.findall(text))
    text = privacy.redact(text.encode('utf-8')).decode('utf-8')
    # Confirm value-redaction has removed the explicitly required findings.
    if privacy.EMAIL.search(text) or SECRET_PREFIX.search(text):
        raise PipelineError('PRIVACY_SCAN_FAILED')
    return text


def language(item):
    counts = Counter(PurePosixPath(p).suffix for p in item['source_files'])
    if not counts:
        raise PipelineError('NO_SOURCE_FILES')
    # Stable lexical tie break; the majority rule does not specify ties.
    extension = min(counts, key=lambda ext: (-counts[ext], ext))
    return {'.java': 'Java', '.kt': 'Kotlin', '.go': 'Go'}[extension]


def shuffled(sample, salt):
    return sorted(sample, key=lambda item: (hmac.new(salt, item['ghsa_id'].encode('utf-8'),
                                                     hashlib.sha256).digest(), item['ghsa_id']))


def csv_text(columns, records):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\n')
    writer.writeheader()
    writer.writerows(records)
    return stream.getvalue()


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text.replace('\r\n', '\n').replace('\r', '\n'))


def item_text(item, advisories):
    sections = [f"# {item['repo'].split('/')[-1]}", f'Language: {language(item)}',
                'CWEs: ' + ', '.join(item['cwes'])]
    for identifier in item['ghsa_ids']:
        advisory = advisories[identifier]
        sections.extend([advisory.get('summary') or '', advisory.get('description') or ''])
    sections.extend(['Touched source files:', *('- ' + p for p in item['source_files'])])
    return '\n\n'.join(sections) + '\n'


def contract_sizes(cache, parent, paths):
    if not paths:
        return []
    entries = git(cache, 'ls-tree', '-r', '-l', '-z', parent, '--', *paths).split('\0')
    result = []
    for entry in entries:
        if not entry:
            continue
        metadata, path = entry.split('\t', 1)
        mode, kind, oid, size = metadata.split()
        if path in paths and kind == 'blob':
            result.append((path, int(size)))
    if {p for p, size in result} != set(paths):
        raise PipelineError('CONTRACT_NOT_A_BLOB')
    return sorted(result, key=lambda pair: (-pair[1], pair[0]))


def flattened(path, counts):
    name = redact(path.replace('/', '__'), counts)
    if name in {'', '.', '..'} or '/' in name or '\0' in name:
        raise PipelineError('INVALID_FLATTENED_PATH')
    return name


def build_item(folder, item, advisories, root=ROOT):
    counts, notes = Counter(), Counter()
    cache = repo_cache(root, item['repo'])
    parent, fix = item['parent_sha'], item['fix_sha']
    folder.mkdir(parents=True)
    write_text(folder / 'item.md', redact(item_text(item, advisories), counts, item=True))
    write_text(folder / 'diff.patch', redact(diff(cache, parent, fix, item['source_files']), counts))
    for stage in ('before', 'after', 'contract'):
        (folder / stage).mkdir()
    # Rank changed files (not lines of context) by total additions+deletions.
    changes = sorted(item['source_changes'],
                     key=lambda c: (-(c['added'] + c['deleted']), c['new_path'], c['old_path']))
    chosen = changes[:20]
    notes['source_files_omitted'] = max(0, len(changes) - len(chosen))
    trees = {sha: set(git(cache, 'ls-tree', '-r', '--name-only', '-z', sha).split('\0'))
             for sha in (parent, fix)}
    written = {'before': set(), 'after': set(), 'contract': {'INDEX.md'}}
    for change in chosen:
        for stage, sha, key in (('before', parent, 'old_path'), ('after', fix, 'new_path')):
            path = change[key]
            if not is_source_path(path) or path not in trees[sha]:
                notes[stage + '_absent'] += 1
                continue
            name = flattened(path, counts)
            if name in written[stage]:
                raise PipelineError('FLATTENED_PATH_COLLISION')
            written[stage].add(name)
            raw = git(cache, 'show', sha + ':' + path)
            write_text(folder / stage / name, redact(raw, counts))
    contracts = contract_sizes(cache, parent, item['contract_paths'])
    index = ['# Parent contract documents', '', 'Path | Bytes | Included', '--- | ---: | ---']
    for i, (path, size) in enumerate(contracts):
        index.append(f'{path} | {size} | {"yes" if i < 3 else "no"}')
        if i < 3:
            name = flattened(path, counts)
            if name in written['contract']:
                raise PipelineError('FLATTENED_PATH_COLLISION')
            written['contract'].add(name)
            raw = git(cache, 'show', parent + ':' + path)
            lines = raw.splitlines(keepends=True)
            if len(lines) > 3000:
                notes['contract_truncated'] += 1
            write_text(folder / 'contract' / name, redact(''.join(lines[:3000]), counts))
    write_text(folder / 'contract/INDEX.md', redact('\n'.join(index) + '\n', counts))
    return {'notes': dict(notes), 'scan_counts': {k: n for k, n in counts.items() if n}}


def main(root=ROOT):
    root = Path(root)
    mining, packages = root / 'mining', root / 'packages'
    blind = packages / 'r4_blind'
    refuse_existing(blind, mining / 'key/r4_key.csv', mining / 'key/r4_build_log.json',
                    mining / 'key/r4_shuffle_salt.txt')
    # This only checks names; it never opens or inspects an existing package.
    if packages.exists() and any(packages.glob('r4_kb*')):
        raise PipelineError('OUTPUT_EXISTS')
    pool_freeze = read_json(mining / 'pool_freeze.json')
    sample_freeze = read_json(mining / 'sample_freeze.json')
    verify_hashes(mining, pool_freeze['sha256'])
    verify_hashes(mining, sample_freeze['sha256'])
    if sha256_file(mining / 'pool_freeze.json') != sample_freeze['pool_freeze_sha256']:
        raise PipelineError('POOL_FREEZE_HASH_MISMATCH')
    sample = read_json(mining / 'sample.json')
    pool = {i['ghsa_id']: i for i in read_json(mining / 'pool.json')}
    if len({i['ghsa_id'] for i in sample}) != len(sample) or any(
            pool.get(i['ghsa_id']) != i for i in sample):
        raise PipelineError('INVALID_SAMPLE_MEMBERSHIP')
    salt = secrets.token_bytes(32)
    key_dir = mining / 'key'
    key_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    key_dir.chmod(0o700)
    write_text(key_dir / 'r4_shuffle_salt.txt', salt.hex() + '\n')
    (key_dir / 'r4_shuffle_salt.txt').chmod(0o600)
    advisories = {}
    for a in read_json(mining / 'advisories.json'):
        advisories.setdefault(a['ghsa_id'], a)
    blind.mkdir(parents=True)
    # The excluded task text is copied as opaque bytes, never opened for analysis.
    shutil.copyfile(root / 'plan/TASK_R4.md', blind / 'TASK_R4.md')
    rows, key_rows, log = [], [], {}
    for number, item in enumerate(shuffled(sample, salt), 1):
        identifier = f'A{number:03d}'
        log[identifier] = build_item(blind / identifier, item, advisories, root)
        rows.append({'item_id': identifier,
                     'repo_short_name': redact(item['repo'].split('/')[-1]),
                     'language': language(item)})
        key_rows.append({k: (identifier if k == 'item_id' else
                             ';'.join(item[k]) if k in {'ghsa_ids', 'cwes'} else
                             language(item) if k == 'language' else item[k]) for k in KEY_COLUMNS})
    write_text(blind / 'items.csv', csv_text(['item_id', 'repo_short_name', 'language'], rows))
    for start in range(0, len(rows), 16):
        batch = packages / f'r4_kb{start // 16 + 1}'
        batch.mkdir()
        shutil.copyfile(root / 'plan/TASK_R4.md', batch / 'TASK_R4.md')
        batch_rows = rows[start:start + 16]
        write_text(batch / 'items.csv', csv_text(['item_id', 'repo_short_name', 'language'], batch_rows))
        for row in batch_rows:
            shutil.copytree(blind / row['item_id'], batch / row['item_id'])
    write_text(key_dir / 'r4_key.csv', csv_text(KEY_COLUMNS, key_rows))
    write_json(key_dir / 'r4_build_log.json', log)
    print('items=' + str(len(rows)) + ' batches=' + str((len(rows) + 15) // 16))


if __name__ == '__main__':
    cli(main)
