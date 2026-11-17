import runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50b.py'))
R['accept']('dependency-track',4,'GET /api/v1/finding/project/{uuid}',
 'the endpoint returns all project findings with a total-number-of-findings header',
 'the body excludes suppressed findings while its total count includes them',
 'IMPL','jvm_annotations','filter.suppressed_findings_total',
 contract=[('resources/v1/FindingResource.java',r'Returns a list of all findings|total number of findings')],
 implementation=[('resources/v1/FindingResource.java',r'getVulnerabilityCount\(project, true\)|qm.getFindings\(project\)'),('persistence/QueryManager.java',r'public long getVulnerabilityCount|if \(! includeSuppressed\)|analysis == null \|\| !analysis.isSuppressed')],
 route=[('src/main/webapp/WEB-INF/web.xml',r'<url-pattern>/api/\*</url-pattern>')])
print('Accepted items and exclusions:',R['finish_accept']('The all-findings contract and total-count header include suppressed entries while the parent body filters them; the patch includes them.'))
