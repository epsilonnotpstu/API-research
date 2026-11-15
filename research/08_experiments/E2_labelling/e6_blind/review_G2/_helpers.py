import sys, re, subprocess, json, datetime
from pathlib import Path

def safe(s):
    out=[]
    for l in s.splitlines():
        if re.search(r"(?i)(TEST_[A-Z_]*(?:TOKEN|TAN)|contact|\[REDACTED email\]|clientSecret|@author|copyright|\bwritten by\b|\bauthorization\b|\bpassword\b|\bpasswd\b|\bsecret[_-]?key\b|\baccess[_-]?token\b|\bbearer\s+|\bbasic\s+[A-Za-z0-9+/=]{8,}|[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",l):
            m=re.match(r"^(.*?:[0-9]+:|[0-9]+:)",l)
            out.append((m.group(0) if m else "")+"[REDACTED credential-looking or attribution line]")
        else: out.append(l)
    return "\n".join(out)

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

a=sys.argv[1:]
if a[0]=="read":
    path=Path(a[1]); lines=path.read_text().splitlines()
    ranges=a[2:] or ["1:"+str(len(lines))]
    for r in ranges:
        lo,hi=map(int,r.split(":")); print(str(path)+":"+r)
        print(safe("\n".join(str(i)+":"+lines[i-1] for i in range(lo,min(hi,len(lines))+1))))
elif a[0]=="scan":
    r=subprocess.run(["rg","-n","-i","--",a[1],*a[2:]],capture_output=True,text=True)
    print(safe(r.stdout)); print("rg_exit="+str(r.returncode))
elif a[0]=="files":
    r=subprocess.run(["rg","--files",*a[1:]],capture_output=True,text=True); print(safe(r.stdout))
elif a[0]=="search":
    item,spec,method,path,status,field,scenario,reason=a[1:]
    target={"side":"request" if scenario.startswith("request:") else "response", "method":method,"path_template":path,"scenario":scenario,"observed_status":None if status=="-" else int(status),"field":None if field=="-" else field}
    review={"item_id":item,"labeller":"G2","target_proposition":target,"mandatory_search":{"required":True,"reason":reason},"start_time":now(),"end_time":None,"hits":[],"manual_additions":[],"decision":None,"history_scope":"unavailable"}
    review_path=Path("review_G2")/(item+".json"); review_path.write_text(json.dumps(review,indent=2)+"\n")
    cmd=["/usr/bin/python3","-I","-B","../../tools/intent_evidence.py",item+"/source",spec,"--method",method,"--path",path,"--json"]
    if status!="-":cmd += ["--status",status]
    if field!="-":cmd += ["--field",field]
    r=subprocess.run(cmd,capture_output=True,text=True)
    Path("search_G2",item+".json").write_text(r.stdout)
    Path("search_G2",item+".stderr").write_text(r.stderr)
    Path("search_G2",item+".exitcode").write_text(str(r.returncode)+"\n")
    print("exit_code="+str(r.returncode))
    try:
        data=json.loads(r.stdout)
        print(safe(json.dumps({k:v for k,v in data.items() if k!="hits"},indent=2)))
        for i,h in enumerate(data.get("hits",[])):
            print(safe(json.dumps({"index":i,"category":h.get("category"),"location":h.get("location"),"snippet":h.get("snippet"),"support":h.get("support")},ensure_ascii=False)))
    except Exception: print(safe(r.stdout))
    print(safe(r.stderr))

elif a[0]=="finish":
    item=a[1]; cfg=json.load(sys.stdin); rp=Path("review_G2",item+".json"); rv=json.loads(rp.read_text()); raw_text=Path("search_G2",item+".json").read_text(); raw=json.loads(raw_text) if raw_text.strip() else {"independent_evidence":"NA","hits":[]}
    def checklist(accepted,reason):
        return {"a_expected_behavior_explicit":{"satisfied":accepted,"reason":reason if not accepted else "Explicit assertion or normative statement for the target behavior."},"b_target_scenario_linked":{"satisfied":accepted,"reason":reason if not accepted else "Operation, method, scenario and branch resolved in manual review."},"c_independent_basis":{"satisfied":accepted,"reason":reason if not accepted else "Separate test assertion or normative source; not the questioned handler/spec."},"d_applicable_revision":{"satisfied":True,"reason":"Supplied package snapshot; no history or external revision substituted."},"e_counterevidence_reviewed":{"satisfied":True,"reason":cfg["counterevidence"]}}
    for i,h in enumerate(raw.get("hits",[])):
        o=cfg.get("hit_overrides",{}).get(str(i),{}); disp=o.get("disposition","context"); reason=o.get("reason",cfg["default_hit_reason"])
        rv["hits"].append({"index":i,"category":h.get("category"),"locator":item+"/source/"+h.get("location",""),"disposition":disp,"reason":reason,"checklist":checklist(disp=="accept",reason),"support":o.get("support","neither")})
    for m in cfg.get("manual_additions",[]):
        m.setdefault("disposition","context"); m["checklist"]=checklist(m["disposition"]=="accept",m["reason"])
        rv["manual_additions"].append(m)
    rv["handler_review"]=cfg["handler_review"]; rv["retrieval_completion"]=cfg["retrieval_completion"]; rv["decision"]=cfg["decision"];rv["end_time"]=now()
    rv["intent_search_verdict"]=raw.get("independent_evidence","NA");rv["intent_search_status"]=cfg.get("intent_search_status","complete")
    rv["review_order"]=["HANDLER","E-TEST","E-DOC","E-CONSIST","E-HISTORY"]
    rp.write_text(json.dumps(rv,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"item_id":item,**cfg["decision"]},ensure_ascii=False))
