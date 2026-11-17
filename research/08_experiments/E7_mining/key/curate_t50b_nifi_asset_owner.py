import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
root='nifi-framework-bundle/nifi-framework/nifi-web/nifi-web-api/src/main/java/org/apache/nifi/web/'
R['accept']('nifi',46,'DELETE /parameter-contexts/{contextId}/assets/{assetId}',
 'the operation deletes an asset from the given parameter context',
 'verification checks references in the given context but deletion uses the asset ID alone without verifying its owner context',
 'IMPL','jvm_annotation','request.asset_owner_scope',confidence=2,
 contract=[(root+'api/ParameterContextResource.java',r'summary = "Deletes an Asset from the given Parameter Context"|@Path\("\{contextId\}/assets/\{assetId\}"\)')],
 implementation=[(root+'StandardNiFiServiceFacade.java',r'public void verifyDeleteAsset|public AssetEntity deleteAsset|assetManager.deleteAsset\(assetId\)'),(root+'api/ParameterContextResource.java',r'serviceFacade.deleteAsset\(parameterContextId, assetId\)|serviceFacade.verifyDeleteAsset\(parameterContextId, assetId\)')])
print('Accepted items and exclusions:',R['finish_accept']('Asset deletion promises the given context but does not verify asset ownership; the patch rejects assets owned by a different context.'))
