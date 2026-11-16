from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
for method,path,model,constructor in [
 ('POST','/p2p/preheat/instances','InstanceCreatedResp','NewCreateInstanceCreated'),
 ('DELETE','/p2p/preheat/instances/{preheat_instance_name}','InstanceDeletedResp','NewDeleteInstanceOK'),
 ('PUT','/p2p/preheat/instances/{preheat_instance_name}','InstanceUpdateResp','NewUpdateInstanceOK')]:
 R['accept']('harbor',162,method+' '+path,
  'the success response contains the '+model+' JSON object',
  'return a success responder without setting a response payload',
  'SPEC','openapi','response_body.preheat-instance-success',
  [('api/v2.0/swagger.yaml',r'#/definitions/'+model)],
  [('src/server/v2.0/handler/preheat.go',r'return operation.'+constructor+r'\(\)')],confidence=2)
print('Accepted/capped:',R['finish_accept']('Preheat instance success schemas require objects while handlers set no payload; patch removes those body schemas.'))
