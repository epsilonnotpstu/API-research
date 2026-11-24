"""Verify the three R3 freezes: plan (before mining), packages (before any coder; TREE lines hash a package's item folders),
outputs (before scoring). Missing files count as failures. Run from anywhere: /usr/bin/python3 -I -B check_freezes_r3.py"""
import hashlib, os, subprocess, sys
from pathlib import Path

B = Path(__file__).resolve().parents[2]
FREEZES = ['plan/r3_plan_freeze.sha256', 'plan/r3_packages_freeze.sha256', 'plan/r3_outputs_freeze.sha256',
           'plan/r3b_plan_freeze.sha256', 'plan/r3b_packages_freeze.sha256', 'plan/r3b_outputs_freeze.sha256']
PENDING_OK = {'plan/r3b_outputs_freeze.sha256'}   # R3b GPT coders pending (P-R3b-1) until scored


def tree(d, letter='B'):
    """= (cd d && find B* -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum), exactly as r3_freeze_packages.sh ran it.
    NOTE: the freeze was made under LANG=en_US.UTF-8, and `sort -z` collates by locale (not byte order), so the same locale
    is forced here; under LC_ALL=C the TREE hashes differ although no file differs."""
    cmd = f'find {letter}* -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum'
    loc = 'en_US.UTF-8' if letter == 'B' else 'C'   # R3 trees were frozen under en_US.UTF-8, R3b trees under C
    r = subprocess.run(['bash', '-c', cmd], cwd=d, capture_output=True, text=True, env={**os.environ, 'LC_ALL': loc})
    n = sum(1 for p in d.glob(letter + '*/**/*') if p.is_file())
    return (r.stdout.split()[0] if r.returncode == 0 and r.stdout else None), n


def anonymised():
    """Files listed in ../ANONYMIZATION.md (anonymised review copy only): their hashes are expected to differ."""
    f = B.parent / 'ANONYMIZATION.md'
    if not f.is_file(): return set()
    return {l[2:].strip().removeprefix('R3_silent_breaking/') for l in f.read_text().splitlines() if l.startswith('- ')}


def main():
    bad = 0; anon = anonymised()
    for fr in FREEZES:
        ok = n = 0
        if not (B / fr).is_file():
            if fr in PENDING_OK: print(f'PENDING {fr}: R3b not yet scored (P-R3b-1)'); continue
            bad += 1; print(f'FAIL missing {fr}'); continue
        for line in (B / fr).read_text().splitlines():
            h, p = line.split('  ', 1); n += 1
            if p.startswith('TREE:'):
                letter = p[-2]; d = B / p[5:-3]; got, k = tree(d, letter) if d.is_dir() else (None, 0)
                good = got == h and k > 0
            else:
                f = B / p; good = f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest() == h
            if good: ok += 1
            elif p in anon: ok += 1; print(f'EXPLAINED {fr}: {p} (path placeholders in the anonymised copy; verifies in the de-anonymised archive)')
            else: bad += 1; print(f'FAIL {fr}: {p}')
        print(f'{"OK  " if ok == n else "FAIL"} {fr}: {ok}/{n}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
