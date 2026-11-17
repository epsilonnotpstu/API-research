import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('nifi',16,'POST /parameter-contexts/{contextId}/update-requests',
 'updating a parameter context requires read permission for current and newly inherited parameter contexts',
 'the update authorization callback checks the context, affected components and service references without checking inherited-context read permission',
 'IMPL','jvm_annotations','authorization.inherited_context',confidence=2,
 contract=[('web/api/ParameterContextResource.java',r'Read - for any new inherited parameter context')],
 implementation=[('web/api/ParameterContextResource.java',r'validateControllerServiceReferences\(requestEntity, lookup, parameterContext, user\)|private void authorizeReadWriteParameterContext|public Response submitParameterContextUpdate')])
print('Accepted items and exclusions:',R['finish_accept']('Asynchronous update annotations require inherited-context read permissions, but the parent authorization callback lacks those checks; the patch adds them.'))
