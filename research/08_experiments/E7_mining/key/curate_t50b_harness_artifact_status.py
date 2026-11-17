import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
for suffix,operation,handler in [
 ('Summary','GET /registry/{registry_ref}/artifact/{artifact}/summary','get_artifacts_summary.go'),
 ('Details','GET /registry/{registry_ref}/artifact/{artifact}/version/{version}/details','get_artifact_detail.go'),
 ('File','GET /registry/{registry_ref}/artifact/{artifact}/version/{version}/file/{file_name}','get_artifact_file.go'),
 ('Files','GET /registry/{registry_ref}/artifact/{artifact}/version/{version}/files','get_artifact_files.go')]:
 R['accept']('harness',52,operation,
  'a missing requested resource is reported as HTTP 404',
  'a missing image lookup is translated to a resource-not-found error but the handler returns a typed HTTP 500 response',
  'IMPL','openapi','response.artifact_not_found_status',
  contract=[('registry/app/api/openapi/api.yaml',r'operationId: GetArtifact'+suffix+r'\b|description: The specified resource was not found')],
  implementation=[('registry/app/api/controller/metadata/'+handler,r'GetByNameAndType|GetArtifact'+suffix+r'500JSONResponse'),
   ('registry/app/store/database/image.go',r'func \(i ImageDao\) GetByNameAndType|Failed to get image'),
   ('store/database/util.go',r'case errors.Is\(err, sql.ErrNoRows\)|translatedError = store.ErrResourceNotFound'),
   ('registry/app/api/openapi/contracts/artifact/services.gen.go',r'func \(response GetArtifact'+suffix+r'500JSONResponse\)')])
print('Accepted items and exclusions:',R['finish_accept']('Artifact operations declare 404 for missing resources, but missing image lookups return typed 500 responses; the patch adds explicit not-found mappings.'))
