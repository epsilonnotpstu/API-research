import runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50b.py'))
R['accept']('nifi',7,'GET /flow/cluster/summary',
 'the successful JSON response is documented as ControllerStatusEntity with controllerStatus',
 'the resource serializes ClusteSummaryEntity containing clusterSummary',
 'SPEC','jvm_annotations','schema.cluster_summary_entity',
 contract=[('web/api/FlowResource.java',r'response = ControllerStatusEntity.class'),('entity/ControllerStatusEntity.java',r'getControllerStatus')],
 implementation=[('web/api/FlowResource.java',r'final ClusteSummaryEntity entity = new ClusteSummaryEntity|entity.setClusterSummary'),('entity/ClusteSummaryEntity.java',r'getClusterSummary')])
print('Accepted items and exclusions:',R['finish_accept']('The parent cluster-summary annotation declares controller status, while the JSON-producing resource constructs a cluster-summary entity.'))
