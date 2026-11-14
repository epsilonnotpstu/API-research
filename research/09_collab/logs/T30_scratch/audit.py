import csv,hashlib,json,subprocess
from pathlib import Path
ROOT=Path.cwd(); E5=ROOT/'08_experiments/E5_codemut'; OUT=ROOT/'09_collab/logs/T30_scratch'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files():
    paths=set((ROOT/'08_experiments/tools').glob('*.py'))
    paths.update(p for p in (ROOT/'08_experiments/E1_pilot/harness_v2').rglob('*') if p.is_file())
    for ledger in E5.glob('work/*/*runs.tsv'):
        for row in csv.DictReader(ledger.open(),delimiter='\t'):
            run=Path(row['run_dir'])
            if run.is_dir():paths.update(p for p in run.iterdir() if p.is_file())
    paths.update(p for p in E5.glob('work/*/*analysis-s*/*') if p.is_file())
    return {str(p):sha(p) for p in sorted(paths)}
def validations():return {str(p):{'sha256':sha(p),'status':json.loads(p.read_text())['status']} for p in sorted(E5.glob('work/*/*pair-validation-s*.json'))}
if __name__=='__main__':
    before=OUT/'before.json'
    if not before.exists():
        (OUT/'summary_before.csv').write_bytes((E5/'e5_summary.csv').read_bytes())
        (OUT/'summary_HEAD.csv').write_bytes(subprocess.check_output(['git','show','HEAD:./08_experiments/E5_codemut/e5_summary.csv']))
        before.write_text(json.dumps({'protected':files(),'validations':validations()},indent=2)+'\n')
    else:
        old=json.loads(before.read_text());new={'protected':files(),'validations':validations()}
        (OUT/'after.json').write_text(json.dumps(new,indent=2)+'\n')
        print(json.dumps({'protected_count':len(old['protected']),'protected_changed':[p for p,h in old['protected'].items() if new['protected'].get(p)!=h], 'validation_count':len(old['validations']), 'validations_changed':[p for p,h in old['validations'].items() if new['validations'].get(p)!=h]},indent=2))
