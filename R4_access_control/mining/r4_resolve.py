#!/usr/bin/python3
"""API-first fix choice, then depth-two partial fetch into a bare repository."""
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r4_common import (ROOT, CommandError, PipelineError, cli, git, guard_upstream,
                       read_json, repo_cache, run, write_json)

COMMIT = re.compile(r'^https://github\.com/([^/]+)/([^/]+)/commit/([0-9a-fA-F]{7,40})(?=$|[/#?])')
REPOSITORY = re.compile(r'^https://github\.com/([^/]+)/([^/#?]+)')


def candidates(advisory):
    match = REPOSITORY.match(advisory.get('source_code_location') or '')
    source = '/'.join(match.groups()).removesuffix('.git').casefold() if match else None
    found = []
    for url in advisory['references']:
        match = COMMIT.match(url)
        if match:
            owner, repo, sha = match.groups()
            candidate = (owner + '/' + repo.removesuffix('.git'), sha.lower())
            if candidate not in found:
                found.append(candidate)
    return sorted(found, key=lambda c: c[0].casefold() != source)


def prepare_repo(root, repo, origin=None):
    cache = repo_cache(root, repo)
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        run(['git', 'init', '--bare', str(cache)])
        git(cache, 'remote', 'add', 'origin', origin or 'https://github.com/' + repo + '.git')
        git(cache, 'config', 'remote.origin.promisor', 'true')
        git(cache, 'config', 'remote.origin.partialclonefilter', 'blob:none')
    return cache


def fetch(cache, sha):
    git(cache, 'fetch', '--depth=2', '--filter=blob:none', 'origin', sha)


def first_parent(cache, sha):
    try:
        return git(cache, 'rev-parse', '--verify', sha + '^1').strip()
    except CommandError:
        # F1: an overlapping shallow fetch can leave an existing commit at the
        # boundary. Repair before distinguishing that case from a real root.
        fetch(cache, sha)
    try:
        return git(cache, 'rev-parse', '--verify', sha + '^1').strip()
    except CommandError:
        header = git(cache, 'cat-file', '-p', sha).split('\n\n', 1)[0]
        parents = [line[7:] for line in header.splitlines() if line.startswith('parent ')]
        if not parents:
            return None
        parent = parents[0]
        # Reading the raw header works even if another fetch left sha shallow.
        # Verify the actual parent object is present, never call it a root.
        git(cache, 'cat-file', '-e', parent + '^{commit}')
        return parent


def resolve(advisory, root=ROOT):
    for repo, candidate in candidates(advisory):
        try:
            # Plan §3 overrides the task's full-SHA fetch-only shortcut.
            metadata = json.loads(run(['gh', 'api', f'repos/{repo}/commits/{candidate}']))
        except CommandError as error:
            if not error.not_found:
                return {'reason': 'FETCH_ERROR', 'repo': repo}
            continue
        except (ValueError, TypeError):
            return {'reason': 'FETCH_ERROR', 'repo': repo}
        if not isinstance(metadata, dict):
            return {'reason': 'FETCH_ERROR', 'repo': repo}
        sha = metadata.get('sha', '')
        if not isinstance(sha, str):
            return {'reason': 'FETCH_ERROR', 'repo': repo}
        if not re.fullmatch(r'[0-9a-fA-F]{40}', sha):
            return {'reason': 'FETCH_ERROR', 'repo': repo}
        sha = sha.lower()
        # First API resolution fixes the choice, even when its fetch fails.
        try:
            cache = prepare_repo(root, repo)
            fetch(cache, sha)
            parent = first_parent(cache, sha)
        except CommandError:
            return {'reason': 'FETCH_ERROR', 'repo': repo, 'fix_sha': sha}
        if parent is None:
            return {'reason': 'NO_PARENT', 'repo': repo, 'fix_sha': sha}
        return {'repo': repo, 'fix_sha': sha, 'parent_sha': parent}
    return {'reason': 'NO_COMMIT'}


def main(root=ROOT):
    mining = Path(root) / 'mining'
    guard_upstream(root, 'resolved.json')
    results = {}
    for advisory in read_json(mining / 'advisories.json'):
        if advisory['ghsa_id'] not in results:
            results[advisory['ghsa_id']] = resolve(advisory, root)
    write_json(mining / 'resolved.json', results)
    print('resolved=' + str(sum('reason' not in r for r in results.values())) +
          ' excluded=' + str(sum('reason' in r for r in results.values())))


if __name__ == '__main__':
    cli(main)
