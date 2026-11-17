import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('dependency-track',33,'POST /v1/bom',
 'uploaded bill-of-material documents are CycloneDX or SPDX',
 'the upload dispatches ScanUploadEvent to dependency-check scan processing instead of the BOM processor',
 'IMPL','jvm_annotations','upload.bom_event_dispatch',
 contract=[('v1/BomResource.java',r'Expects CycloneDX or SPDX')],
 implementation=[('v1/BomResource.java',r'new ScanUploadEvent\(project.getUuid\(\), content\)'),('tasks/ScanUploadProcessingTask.java',r'DependencyCheckParser|instanceof ScanUploadEvent'),('tasks/BomUploadProcessingTask.java',r'instanceof BomUploadEvent|CycloneDxParser')])
print('Accepted items and exclusions:',R['finish_accept']('Multipart BOM upload promises CycloneDX or SPDX but dispatches the scan-processing event; the patch routes it to the existing BOM processor.'))
