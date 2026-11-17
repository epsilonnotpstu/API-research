import runpy,json
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50b.py'))
ops=[('PUT','/segments/{segmentID}','putSegment','PutSegment'),('DELETE','/segments/{segmentID}','deleteSegment','DeleteSegment'),('PUT','/segments/{segmentID}/constraints/{constraintID}','putConstraint','PutConstraint'),('DELETE','/segments/{segmentID}/constraints/{constraintID}','deleteConstraint','DeleteConstraint'),('PUT','/segments/{segmentID}/distributions','putDistributions','PutDistributions')]
for method,suffix,opid,name in ops:
 row=R['accept']('flagr',8,method+' /api/v1/flags/{flagID}'+suffix,
  'the mutation is nested under a required flagID path parameter',
  'child records are selected or deleted without constraining their membership to that flag',
  'IMPL','openapi','scope.flag_child_membership',contract=[('docs/api_docs/bundle.yaml',r'operationId: '+opid)],
  implementation=[('pkg/handler/crud.go',r'func .*\) '+name+r'\(|^func commitFlagMutation')],confidence=2)
 path=R['KEY']/'t50_valid'/row['candidate_id']/(row['item_id']+'.json')
 row['inference_notes']='⚠️ Required parent membership inferred from the nested operation path and required flagID; SQL lacks that scope; no runtime execution.'
 path.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
print('Accepted items and exclusions:',R['finish_accept']('Five nested flag mutations do not constrain child membership; existing paths require the parent flag identifier and the patch adds ownership checks.'))
