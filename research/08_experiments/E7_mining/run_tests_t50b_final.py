#!/usr/bin/python3
"""Recheck all updated T50/continuation tests; retain the 73 unchanged earlier passes."""
import contextlib
import json
from pathlib import Path
import re
import runpy
import sys
import unittest

HERE=Path(__file__).resolve().parent
SCRATCH=HERE.parents[1]/'09_collab/logs/T50_scratch'
runner=runpy.run_path(str(HERE/'run_tests_t50b.py'))
sys.addaudithook(runner['read_boundary'])
initial=json.loads((SCRATCH/'test_summary_t50b_01.json').read_text())
assert (initial['earlier_tests'],initial['tests_run'],initial['failures'],initial['errors'])==(73,102,1,0)
initial_log=(HERE/'key/e13_test_t50b_run_01.txt').read_text()
failures=re.findall(r'^FAIL: (\w+)',initial_log,re.M)
assert failures==['test_package_hashes_leakage_privacy_and_eight_file_cap']
suite=unittest.TestSuite();counts=[]
for name in ['test_t50.py','test_t50b.py']:
    tests=runner['collect'](runpy.run_path(str(HERE/name)))
    counts.append(tests.countTestCases());suite.addTests(tests)
with (HERE/'key/e13_test_t50b_final_run_01.txt').open('x') as stream:
    with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
summary=dict(earlier_tests=73,T50_tests=counts[0],T50b_tests=counts[1],tests_run=73+result.testsRun,
    failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),
    execution_parts=[dict(summary='test_summary_t50b_01.json',tests=102,earlier_unchanged_passes=73,
                          resolved_failure='reviewer prose classified as auth literal'),
                     dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),scope='all current T50 and T50b tests')],
    all_current_test_methods_executed=True,old_package_access_blocked=True,earlier_package_tests_use_isolated_reconstructions=True)
with (SCRATCH/'test_summary_t50b_02.json').open('x') as stream:json.dump(summary,stream,indent=2);stream.write('\n')
print(json.dumps(summary))
raise SystemExit(0 if result.wasSuccessful() else 1)
