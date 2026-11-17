import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('fess',31,'GET /api/v1/suggest-words',
 'suggestion metadata fields are named took, total and num, with item field values under field',
 'the JSON writer emits query_time, record_count and page_size, with item values under labels',
 'SPEC','openapi','response.suggestion_field_names',
 contract=[('src/main/config/openapi/openapi-user.yaml',r'^  /suggest-words:')],
 implementation=[('api/json/SearchApiManager.java',r'query_time.*suggestResponse|record_count.*suggestResponse|page_size.*suggestResponse|labels')])
print('Accepted items and exclusions:',R['finish_accept']('The parent suggestion schema names four response fields differently from the JSON writer; the patch aligns the document with existing serialization.'))
