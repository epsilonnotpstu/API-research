import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('dependency-track',28,'POST /v1/user/login',
 'login consumes multipart/form-data',
 'the resource reads login fields using JAX-RS FormParam binding for application/x-www-form-urlencoded data',
 'SPEC','jvm_annotations','request.login_media_type',confidence=2,
 contract=[('v1/UserResource.java',r'@Consumes\(MediaType.MULTIPART_FORM_DATA\)')],
 implementation=[('v1/UserResource.java',r'@FormParam\(')])
print('Accepted items and exclusions:',R['finish_accept']('Login declares multipart input while using standard form-parameter binding; the patch aligns its consumed media type with the existing binding mechanism.'))
