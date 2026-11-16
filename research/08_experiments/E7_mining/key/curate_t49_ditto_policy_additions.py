from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
R['accept']('ditto',270,'PUT /policies/{policyId}/entries/{label}',
 'the PolicyEntry request permits allowedImportAdditions to specify permitted imported additions',
 'reconstruct the submitted entry from subjects, resources and importable while omitting allowedImportAdditions',
 'IMPL','openapi','request_body.policy-entry-allowed-import-additions',
 [('openapi/ditto-api-2.yml',r'^        allowedImportAdditions:|^  .*/policies/\{policyId\}/entries/\{label\}'),('sources/schemas/policies/policyEntry.yml',r'allowedImportAdditions:')],
 [('routes/policies/PolicyEntriesRoute.java',r'createPolicyEntryForPut|newPolicyEntry\(Label.of\(labelString\)')],
 helpers=['policies/model/PoliciesModelFactory.java','policies/model/ImmutablePolicyEntry.java'])
print('Accepted/capped:',R['finish_accept']('Parent PolicyEntry schema permits allowedImportAdditions; PUT handler drops it during reconstruction; patch uses the complete JSON parser.'))
