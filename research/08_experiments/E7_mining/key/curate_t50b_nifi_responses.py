import runpy,re
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py');n=R['next_row']();_,patch=R['evidence'](n)
ref_type=re.search(r'^\+\s*response = (ControllerService\w+Entity)\.class',patch,re.M)[1]
ops=[]
for root,file in [('controller-services','ControllerServiceResource.java'),('processors','ProcessorResource.java'),('reporting-tasks','ReportingTaskResource.java')]:
 for method,suffix in [('GET','state'),('POST','state/clear-requests')]:
  ops.append((method+' /'+root+'/{id}/'+suffix,file,'ComponentStateDTO','ComponentStateEntity',r'final ComponentStateEntity entity = new ComponentStateEntity'))
ops += [
 ('GET /controller-services/{id}/references','ControllerServiceResource.java','ControllerServiceEntity',ref_type,'final '+ref_type+' entity ='),
 ('DELETE /flowfile-queues/{id}/listing-requests/{listing-request-id}','FlowFileQueueResource.java','DropRequestEntity','ListingRequestEntity',r'final ListingRequestEntity entity = new ListingRequestEntity'),
 ('GET /flow/remote-process-groups/{id}/status','FlowResource.java','ProcessorStatusEntity','RemoteProcessGroupStatusEntity',r'final RemoteProcessGroupStatusEntity entity = serviceFacade.getRemoteProcessGroupStatus'),
 ('GET /process-groups/{id}/process-groups','ProcessGroupResource.java','ProcessorsEntity','ProcessGroupsEntity',r'final ProcessGroupsEntity entity = new ProcessGroupsEntity'),
 ('POST /process-groups/{id}/snippet-instance','ProcessGroupResource.java','FlowSnippetEntity','FlowEntity',r'final FlowEntity flowEntity =')]
for op,file,old,new,pattern in ops:
 R['accept']('nifi',23,op,
  'the successful response is documented using '+old,
  'the resource returns the structurally different '+new+' envelope',
  'SPEC','jvm_annotations','schema.resource_response_type',
  contract=[('web/api/'+file,r'response = '+old+r'.class')],
  implementation=[('web/api/'+file,pattern)],
  helpers=['entity/'+new+'.java'])
print('Accepted items and exclusions:',R['finish_accept']('Eleven parent resource response annotations declare DTOs or unrelated envelopes; implementations return distinct entity wrappers, and the patch corrects the declarations.'))
