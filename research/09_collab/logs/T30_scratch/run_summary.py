"""Call summarise_e5.main unchanged; emit progress without changing outputs."""
import datetime,sys,json
from pathlib import Path
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'08_experiments/E5_codemut'))
import summarise_e5 as summary
identify=summary.analysis_identity
identified=False
def identity():
    global identified
    value=identify()
    if not identified:
        (ROOT/"09_collab/logs/T30_scratch/analysis_identity_initial.json").write_text(json.dumps(value,indent=2)+"\n")
        identified=True
    return value
summary.analysis_identity=identity
original=summary.verify_analysis
counter=0

def progress(directory,*args,**kwargs):
    global counter
    counter+=1
    print(datetime.datetime.now(datetime.timezone.utc).isoformat(),counter,str(directory),flush=True)
    return original(directory,*args,**kwargs)

summary.verify_analysis=progress
sys.exit(summary.main())
