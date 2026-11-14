"""Run existing review suite with its temp directories confined to T26 scratch."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = Path(__file__).resolve().parent
original = tempfile.TemporaryDirectory


def temporary(*args, **kwargs):
    if 'dir' in kwargs:
        kwargs['dir'] = SCRATCH
    return original(*args, **kwargs)


output = io.StringIO()
rc = 0
start = time.monotonic()
with patch.object(tempfile, 'TemporaryDirectory', side_effect=temporary), \
        contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
    sys.argv = [str(ROOT / '08_experiments/tools/test_review_fixes.py')]
    try:
        runpy.run_path(sys.argv[0], run_name='__main__')
    except SystemExit as exc:
        rc = int(exc.code or 0)
(SCRATCH / 'review_fixes_tests.txt').write_text(output.getvalue())
result = {'suite': 'review_fixes', 'returncode': rc,
          'seconds': round(time.monotonic() - start, 4),
          'temporary_directory_override': 'T10_scratch -> T26_scratch (no source edits)',
          'tail': output.getvalue().splitlines()[-6:]}
(SCRATCH / 'review_fixes_summary.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
sys.exit(rc)
