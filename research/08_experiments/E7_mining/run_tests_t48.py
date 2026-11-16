#!/usr/bin/python3
"""Run old tests against an isolated reconstruction, never old blind packages."""
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAB = ROOT / '08_experiments/E2_labelling'


def read_boundary(event, args):
    if event not in {'open', 'os.listdir', 'os.scandir'} or not args:
        return
    value = args[0]
    if not isinstance(value, (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(value)).absolute()
    try:
        relative = path.relative_to(LAB)
    except ValueError:
        return
    # All old labelling packages are off limits, including directory listings.
    if not relative.parts or relative.parts[0] != 'e10_blind':
        raise AssertionError('Test attempted access outside the new blind package')


def main():
    sys.addaudithook(read_boundary)
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    old_count = 0
    for name in ['test_build.py', 'test_pool2.py', 'test_review2.py']:
        module = runpy.run_path(str(HERE / name))
        tests = unittest.TestSuite(loader.loadTestsFromTestCase(value) for value in module.values()
                                  if isinstance(value, type) and issubclass(value, unittest.TestCase))
        old_count += tests.countTestCases()
        suite.addTests(tests)
    old_module = runpy.run_path(str(HERE / 'test_t47.py'))
    builder = old_module['B']
    salt = (HERE / 'key/e8b_shuffle_salt.txt').read_text().strip()
    rebuilt = builder['reconstruct'](salt)
    with tempfile.TemporaryDirectory(prefix='.t48-old-tests-', dir=HERE) as folder:
        output = Path(folder) / 'reconstructed-prior-package'
        output.mkdir()
        for relative, data in rebuilt[0].items():
            path = output / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        builder['OUT'] = output
        tests = unittest.TestSuite(loader.loadTestsFromTestCase(value) for value in old_module.values()
                                  if isinstance(value, type) and issubclass(value, unittest.TestCase))
        old_count += tests.countTestCases()
        suite.addTests(tests)
        module = runpy.run_path(str(HERE / 'test_t48.py'))
        tests = unittest.TestSuite(loader.loadTestsFromTestCase(value) for value in module.values()
                                  if isinstance(value, type) and issubclass(value, unittest.TestCase))
        new_count = tests.countTestCases()
        suite.addTests(tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = dict(earlier_tests=old_count, T48_tests=new_count, tests_run=result.testsRun,
                   failures=len(result.failures), errors=len(result.errors), passed=result.wasSuccessful(),
                   old_package_access_blocked=True, old_T47_tests_use_isolated_reconstruction=True)
    path = ROOT / '09_collab/logs/T48_scratch/test_summary.json'
    with path.open('x') as stream:
        json.dump(summary, stream, indent=2)
        stream.write('\n')
    print(json.dumps(summary))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
