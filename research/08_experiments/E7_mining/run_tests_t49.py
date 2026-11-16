#!/usr/bin/python3
"""Run all earlier tests on reconstructions; deny access to older blind packages."""
import contextlib
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
    if not relative.parts or relative.parts[0] != 'e12_blind':
        raise AssertionError('Test attempted access outside the new blind package')


def collect(module):
    loader = unittest.TestLoader()
    return unittest.TestSuite(loader.loadTestsFromTestCase(value) for value in module.values()
                              if isinstance(value, type) and issubclass(value, unittest.TestCase))


def main():
    sys.addaudithook(read_boundary)
    suite = unittest.TestSuite()
    old_count = 0
    for name in ['test_build.py', 'test_pool2.py', 'test_review2.py']:
        tests = collect(runpy.run_path(str(HERE / name)))
        old_count += tests.countTestCases()
        suite.addTests(tests)
    with tempfile.TemporaryDirectory(prefix='.t49-old-tests-', dir=HERE) as folder:
        for task, package, salt_name in [('t47', 'e8b_blind', 'e8b_shuffle_salt.txt'),
                                         ('t48', 'e10_blind', 'e10_shuffle_salt.txt')]:
            module = runpy.run_path(str(HERE / ('test_' + task + '.py')))
            builder = module['B']
            rebuilt = builder['reconstruct']((HERE / 'key' / salt_name).read_text().strip())
            output = Path(folder) / package
            output.mkdir()
            for relative, data in rebuilt[0].items():
                path = output / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            builder['OUT'] = output
            tests = collect(module)
            old_count += tests.countTestCases()
            suite.addTests(tests)
        module = runpy.run_path(str(HERE / 'test_t49.py'))
        tests = collect(module)
        new_count = tests.countTestCases()
        suite.addTests(tests)
        # Any diagnostic containing private identifiers stays inside key/.
        number = len(list((HERE / 'key').glob('e12_test_run_*.txt'))) + 1
        with (HERE / 'key' / f'e12_test_run_{number:02}.txt').open('x') as stream:
            with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    summary = dict(earlier_tests=old_count, T49_tests=new_count, tests_run=result.testsRun,
                   failures=len(result.failures), errors=len(result.errors), passed=result.wasSuccessful(),
                   old_package_access_blocked=True, earlier_package_tests_use_isolated_reconstructions=True)
    path = ROOT / '09_collab/logs/T49_scratch' / f'test_summary_{number:02}.json'
    with path.open('x') as stream:
        json.dump(summary, stream, indent=2)
        stream.write('\n')
    print(json.dumps(summary))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
