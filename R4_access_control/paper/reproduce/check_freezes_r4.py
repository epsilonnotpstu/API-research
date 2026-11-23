"""Verify the three R4 freezes: plan (before mining), packages (before any coder; TREE lines hash a package's A* item folders with
byte-order sort, LC_ALL=C), outputs (before scoring). Missing files count as failures.
Append-only exception: plan/R4_DEVIATIONS.md grew after the package freeze (P1 appended). Its frozen version is kept verbatim as
plan/R4_DEVIATIONS_at_package_freeze.md; the entry is EXPLAINED if that copy matches the frozen hash AND the live file starts with it.
In an anonymised archive, files listed in ../ANONYMIZATION.md are EXPLAINED as well.
Run from anywhere: /usr/bin/python3 -I -B check_freezes_r4.py"""
import hashlib, sys
from pathlib import Path

B = Path(__file__).resolve().parents[2]
FREEZES = ['plan/r4_plan_freeze.sha256', 'plan/r4_packages_freeze.sha256', 'plan/r4_outputs_freeze.sha256']
APPEND_ONLY = {'plan/R4_DEVIATIONS.md': 'plan/R4_DEVIATIONS_at_package_freeze.md'}


def tree(d):
    """= (cd d && find A* -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum), in Python (byte-order sort).
    Files of restrictively licensed items are withheld from the archive; their original hashes are in d/WITHHELD.sha256
    and enter the listing exactly as the missing files would."""
    rows = {f.relative_to(d).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in d.glob('A*/**/*') if f.is_file()}
    w = d / 'WITHHELD.sha256'
    if w.is_file():
        for line in w.read_text().splitlines():
            h, p = line.split('  ', 1)
            if p in rows: return None          # a withheld file must really be absent
            rows[p] = h
    listing = ''.join(f'{rows[p]}  {p}\n' for p in sorted(rows, key=lambda x: x.encode()))
    return hashlib.sha256(listing.encode()).hexdigest()


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
