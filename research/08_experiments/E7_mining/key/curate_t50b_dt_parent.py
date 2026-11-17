import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('dependency-track',11,'POST /v1/project',
 'omitting parent or setting it to null leaves the existing parent unchanged',
 'the update persistence path removes the existing parent when parent is null',
 'SPEC','jvm_annotations','update.parent_null',
 contract=[('v1/ProjectResource.java',r'to leave the parent unchanged')],
 implementation=[('v1/ProjectResource.java',r'return qm.updateProject\(jsonProject, true\)'),('persistence/ProjectQueryManager.java',r'project.setParent\(null\)')])
print('Accepted items and exclusions:',R['finish_accept']('Parent omission is documented as preserving hierarchy, but the resource passes null to persistence, which clears the parent.'))
