from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
R['accept']('ditto',188,'PATCH /things/{thingId}/features',
 'a required featureId path parameter accompanies the collection operation',
 'route the collection operation at path end using thingId and the features body without extracting featureId',
 'SPEC','openapi','request_parameter.extraneous-feature-id',
 [('openapi/ditto-api-2.yml',r"FeatureIdPathPathParam|'/things/\{thingId\}/features'"),('sources/parameters/featureIdPathPathParam.yml',r'name: featureId|required: true')],
 [('endpoints/routes/things/FeaturesRoute.java',r'PATCH /features$|MergeThing.withFeatures|pathEndOrSingleSlash')],
 route=[('endpoints/routes/things/ThingsRoute.java',r'featuresRoute|FeaturesRoute|PATH_FEATURES')])
print('Accepted/capped:',R['finish_accept']('Collection PATCH requires featureId in parent OpenAPI; parent route extracts none; patch removes the extraneous parameter.'))
