"""Verify the three R4 freezes: plan (before mining), packages (before any coder; TREE lines hash a package's A* item folders with
byte-order sort, LC_ALL=C), outputs (before scoring). Missing files count as failures.
Append-only exception: plan/R4_DEVIATIONS.md grew after the package freeze (P1 appended). Its frozen version is kept verbatim as
plan/R4_DEVIATIONS_at_package_freeze.md; the entry is EXPLAINED if that copy matches the frozen hash AND the live file starts with it.
In an anonymised archive, files listed in ../ANONYMIZATION.md are EXPLAINED as well.
Run from anywhere: /usr/bin/python3 -I -B check_freezes_r4.py"""
import hashlib, os, subprocess, sys
from pathlib import Path

B = Path(__file__).resolve().parents[2]
FREEZES = ['plan/r4_plan_freeze.sha256', 'plan/r4_packages_freeze.sha256', 'plan/r4_outputs_freeze.sha256']
APPEND_ONLY = {'plan/R4_DEVIATIONS.md': 'plan/R4_DEVIATIONS_at_package_freeze.md'}


def tree(d):
    r = subprocess.run(['bash', '-c', 'find A* -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum'], cwd=d, capture_output=True,
                       text=True, env={**os.environ, 'LC_ALL': 'C'})
    return r.stdout.split()[0] if r.returncode == 0 and r.stdout else None


def anonymised():
    f = B.parent / 'ANONYMIZATION.md'
    if not f.is_file(): return set()
    return {l[2:].strip().removeprefix('R4_access_control/') for l in f.read_text().splitlines() if l.startswith('- ')}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    bad = 0; anon = anonymised()
    for fr in FREEZES:
        ok = n = 0
        for line in (B / fr).read_text().splitlines():
            h, p = line.split('  ', 1); n += 1
            if p.startswith('TREE:'):
                d = B / p[5:].removesuffix('/A*'); good = d.is_dir() and tree(d) == h
            else:
                f = B / p; good = f.is_file() and sha(f) == h
            if good: ok += 1; continue
            if p in APPEND_ONLY:
                c = B / APPEND_ONLY[p]; live = (B / p).read_bytes() if (B / p).is_file() else b''
                if c.is_file() and sha(c) == h and live.startswith(c.read_bytes()):
                    ok += 1; print(f'EXPLAINED {fr}: {p} (append-only; frozen version = {APPEND_ONLY[p]})'); continue
            if p in anon: ok += 1; print(f'EXPLAINED {fr}: {p} (path placeholders in the anonymised copy)'); continue
            bad += 1; print(f'FAIL {fr}: {p}')
        print(f'{"OK  " if ok == n else "FAIL"} {fr}: {ok}/{n}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
