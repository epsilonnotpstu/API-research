"""Redact the runtime benchmark credential from streaming and saved artifacts."""
import os
from pathlib import Path
import sys


def secrets():
    header = os.environ.get('PILOT_AUTH_REDACT', '')
    value = header.partition(':')[2].strip()
    token = value.split(' ', 1)[-1]
    return sorted({s for s in (header, value, token) if s}, key=len, reverse=True)


def clean(data, needles):
    for needle in needles:
        data = data.replace(needle.encode(), b'<redacted>')
    return data


def main():
    needles = secrets()
    if len(sys.argv) == 1:
        for line in sys.stdin.buffer:
            sys.stdout.buffer.write(clean(line, needles))
            sys.stdout.buffer.flush()
        return
    directory = Path(sys.argv[1])
    for path in directory.rglob('*'):
        # Public role identifiers in provenance/configuration are not credentials.
        # Metadata contains role/source/digests only; config contains no header value.
        if not path.is_file() or path.suffix == '.exec' or path.name in {'sut-config.env', 'run.json'}:
            continue
        data = path.read_bytes()
        redacted = clean(data, needles)
        if redacted != data:
            path.write_bytes(redacted)


if __name__ == '__main__':
    main()
