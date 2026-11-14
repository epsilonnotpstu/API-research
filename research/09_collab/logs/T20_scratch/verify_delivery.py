"""Final static/protected-boundary audit; executes no harness or external code."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

root=Path.cwd(); e=root / '08_experiments/E5_codemut'; scratch=root / '09_collab/logs/T20_scratch'
sys.path.insert(0,str(e))
import summarise_e5 as summary
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
protected=json.loads((scratch / 'protected_before.json').read_text())
changed=[name for name,digest in protected.items() if sha(root / name) != digest]
expected_update='08_experiments/E5_codemut/COORDINATOR_NOTES.md'
assert set(changed) <= {expected_update},changed
external_updates={name:{'before_sha256':protected[name],'current_sha256':sha(root / name),
                        'evidence':'COORDINATOR_NOTES.md Build results and COLLAB_BOARD.md Claude T19 build-results log'} for name in changed}
parsed=[]
for p in list(e.glob('*.py'))+[Path(__file__)]:
    ast.parse(p.read_text(),filename=str(p)); parsed.append(str(p.relative_to(root)))
shell=[]
for name in ('run_pair.sh','analyse_pair.sh'):
    p=e / name
    result=subprocess.run(['bash','-n',str(p)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert p.stat().st_mode & 0o111
    shell.append(name)
blocks=re.findall(r'^```bash\n(.*?)^```',(e / 'PIPELINE.md').read_text(),re.M|re.S)
plan=scratch / 'guide-commands.sh'; plan.write_text('\n'.join(blocks))
result=subprocess.run(['bash','-n',str(plan)],capture_output=True,text=True)
assert result.returncode==0,result.stderr
citations=0
for p in (e / 'PIPELINE.md',root / '09_collab/reports/T20_report.md'):
    for match in re.finditer(r'`([A-Za-z0-9_./-]+\.(?:py|sh|md|json|csv|txt)):(\d+(?:[–-]\d+)?(?:,\d+(?:[–-]\d+)?)*)`',p.read_text()):
        target=root / match[1] if match[1].startswith(('08_experiments/','09_collab/')) else e / match[1]
        assert target.is_file(),(p,target)
        size=len(target.read_bytes().split(b'\n'))
        assert all(1<=int(n)<=size for n in re.findall(r'\d+',match[2])),(p,target,match[2],size)
        citations+=1
with (e / 'e5_summary.csv').open(newline='') as stream:
    reader=csv.DictReader(stream); assert reader.fieldnames==summary.FIELDS; rows=list(reader)
assert len(rows)==0
assert not list(e.glob('.test-*')) and not list(scratch.glob('synthetic-*'))
text=(scratch / 'tests.txt').read_text()
assert re.search(r'Ran 74 tests in .*\n\nOK\n',text)
bundle=json.loads((scratch / 'built_pair_readonly_check.json').read_text()); assert bundle['status']=='PASS'
result={'status':'PASS','python_ast':parsed,'shell_syntax':shell,'guide_bash_blocks':len(blocks),
        'file_line_citations_checked':citations,'synthetic_tests':{'total':74,'new_pipeline':52,'existing_codemut':22},
        'protected_files':{'count':len(protected),'unchanged_count':len(protected)-len(changed),'changed':changed,'coordinator_updates':external_updates,'scope':'harness_v2/tools regular nonhidden/noncache files plus coordinator build_pair.sh and COORDINATOR_NOTES.md'},
        'readonly_completed_build_checks':len(bundle['checks']),
        'summary':{'rows':len(rows),'status':'NO_RUNS','header_fields':len(summary.FIELDS)},
        'execution':{'own_python_tests_and_tools':'synthetic evidence only; plus read-only completed build inspection',
                     'docker_java_maven_harness_sut':'not_run','work_writes':'none','runs_writes':'none'}}
(scratch / 'static_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
