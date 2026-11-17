import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
R['accept']('tyk',37,'GET /tyk/keys',
 'the successful response is an array of key identifiers',
 'the successful response is a JSON object containing a keys array',
 'SPEC','openapi','response.key_list_envelope',
 contract=[('swagger.yml',r'operationId: listKeys|Returns an array of Key IDs')],
 implementation=[('gateway/api.go',r'APIKeys \[\]string `json:"keys"`|sessionsObj := apiAllKeys\{fixedSessions\}|obj, code = gw.handleGetAllKeys\(filter\)|func doJSONWrite')],
 route=[('gateway/server.go',r'r.HandleFunc\("/keys", gw.keyHandler\)')])
print('Accepted items and exclusions:',R['finish_accept']('Key-list schema declares an array, but the handler serializes an object containing keys; the patch references the existing envelope schema.'))
