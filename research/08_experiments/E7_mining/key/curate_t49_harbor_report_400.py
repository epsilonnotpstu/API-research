from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
R['accept']('harbor',166,'GET /projects/{project_name}/repositories/{repository_name}/artifacts/{reference}/scan/{report_id}/log',
 'the documented responses are 200, 401, 403, 404 and 500 with no 400 response',
 'return HTTP 400 for an invalid report UUID through the task lookup and error mapper',
 'SPEC','openapi','response_status.scan-log-invalid-uuid',
 [('api/v2.0/swagger.yaml',r'^  /projects/.*scan/\{report_id\}/log:|operationId: getReportLog')],
 [('src/server/v2.0/handler/scan.go',r'GetReportLog\(|GetScanLog\(ctx, a, params.ReportID'),('src/controller/scan/base_controller.go',r'func .*GetScanLog|func .*listScanTasks|ListScanTasksByReportUUID'),('src/pkg/task/task.go',r'm.dao.ListScanTasksByReportUUID'),('src/pkg/task/dao/task.go',r'invalid UUID'),('src/lib/http/error.go',r'errors.BadRequestCode:.*http.StatusBadRequest')],
 helpers=['src/server/v2.0/handler/base.go'])
print('Accepted/capped:',R['finish_accept']('Parent scan-log responses omit 400; invalid report UUID reaches BadRequestError and HTTP 400 mapping; patch documents that response.'))
