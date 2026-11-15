#!/usr/bin/python3
"""Manual screen sign-off and individual code assignments after frozen review."""
import json,re
from pathlib import Path
H=Path(__file__).resolve().parents[1];K=H/'key'
inv=json.loads((H/'pool2_inventory.json').read_text())
signs={r['repo']:min(60,r['pool2']) for r in inv}
signs.update({'cwms-data-api':50,'strimzi-kafka-bridge':32,'tiltaksgjennomforing-api':0})
# Codes are applied to individual draft rows; each retains its own actual path,
# title and differing source delta. No range-level reason is published.
assignments={
'Iced-Latte':{
 'REFACTOR_OR_RENAME':'2,4,6,9,10,13,14,15,16,18,22,23,25,26,29,30,32,33,34,35,45,46,47,51',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'53,54,55',
 'GENERATED_OR_DOCS_ONLY_CHURN':'8,57', 'TOO_LARGE_TO_ESTABLISH':'5,59',
 'NOT_CONTRACT_RELATED':'24,56,60'},
'OpenLineage':{'GENERATED_OR_DOCS_ONLY_CHURN':'1,2,3'},
'apicurio-registry':{
 'REFACTOR_OR_RENAME':'7,11,18,25,26,34,37,48,54',
 'GENERATED_OR_DOCS_ONLY_CHURN':'13,19,23,58,59',
 'NEW_FEATURE_OR_ENDPOINT':'8,40,42', 'TOO_LARGE_TO_ESTABLISH':'17,30,44,47',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'35,38,45',
 'NOT_CONTRACT_RELATED':'4,5,10,16,21,24,28,32,41,43,51,52,56,57'},
'basyx-java-server-sdk':{
 'NOT_CONTRACT_RELATED':'3,6,11,12,13,14,15,19',
 'REFACTOR_OR_RENAME':'8,16',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'18,20',
 'NEW_FEATURE_OR_ENDPOINT':'17,21'},
'catwatch':{'NEW_FEATURE_OR_ENDPOINT':'3','REFACTOR_OR_RENAME':'4'},
'cwms-data-api':{
 'REFACTOR_OR_RENAME':'2,5,7,8,10,11,13,14,16,18,22,24,25,27,30,38,39,40,42,43,47',
 'GENERATED_OR_DOCS_ONLY_CHURN':'1,45,49',
 'NEW_FEATURE_OR_ENDPOINT':'4,9',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'23,32,44',
 'TOO_LARGE_TO_ESTABLISH':'6,12,15,37'},
'ditto':{
 'REFACTOR_OR_RENAME':'1,6,8,10,13,15,17,19,21,27,32,35,37,39,46,47,48,51,54,55,56,57,59,60',
 'GENERATED_OR_DOCS_ONLY_CHURN':'4,25,43,49',
 'NEW_FEATURE_OR_ENDPOINT':'34',
 'NOT_CONTRACT_RELATED':'2,3,9,11,12,16,20,26,28,29,30,31,33,36,38,41,42,44,50,52,53'},
'dockstore':{
 'REFACTOR_OR_RENAME':'4,7,8,12,13,14,16,19,27,28,29,31,35,37,38,42,48,50,52,53,54,57',
 'GENERATED_OR_DOCS_ONLY_CHURN':'5,20,24,33',
 'NEW_FEATURE_OR_ENDPOINT':'21,30,32,45,49,58',
 'TOO_LARGE_TO_ESTABLISH':'25,56',
 'NOT_CONTRACT_RELATED':'2,10,11,17,18,23,39,43,47,60'},
'eudi-srv-verifier-endpoint':{'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'1,2,3'},
'fineract':{
 'NOT_CONTRACT_RELATED':'1,2,3,5,6,7,8,10,11,13,14,15,17,18,20,21,23,24,25,26,34,35,37,39,40,41,42,45,48,49,50,53,54,56,59,60',
 'REFACTOR_OR_RENAME':'9,19,22,28,29,31,38,47,51,52',
 'GENERATED_OR_DOCS_ONLY_CHURN':'30,33,55,57,58'},
'genome-nexus':{'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'1,2,4','GENERATED_OR_DOCS_ONLY_CHURN':'3'},
'gravitee-api-management':{
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'4,5,14,17,22,25,26,45,50',
 'REFACTOR_OR_RENAME':'1,6,15,20,28,36,37,47,51,55,60',
 'NOT_CONTRACT_RELATED':'2,3,7,8,9,10,11,12,13,16,21,23,24,27,29,30,31,32,33,34,35,38,39,40,41,42,43,44,46,48,49,52,53,54,56,57,58,59'},
'harbor':{
 'NOT_CONTRACT_RELATED':'1,2,3,5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,26,28,29,30,31,32,33,35,36,37,38,39,40,41,42,44,45,47,48,50,52,53,54,56,58,59,60',
 'REFACTOR_OR_RENAME':'27',
 'GENERATED_OR_DOCS_ONLY_CHURN':'25,34,49,51,55,57',
 'NEW_FEATURE_OR_ENDPOINT':'46'},
'hivemq-edge':{
 'REFACTOR_OR_RENAME':'3,4,6,9,13,18,22,23,25,27,29,31,34,35,38,42,43,48,49,54,58,60',
 'GENERATED_OR_DOCS_ONLY_CHURN':'2,5,12,24,26,30,32,40,50,56',
 'NEW_FEATURE_OR_ENDPOINT':'7,16,20,41',
 'TOO_LARGE_TO_ESTABLISH':'44,53',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'19,28,37,39,46,55,57',
 'NOT_CONTRACT_RELATED':'1,10,11,21,36,45,47,52'},
'hydra':{
 'REFACTOR_OR_RENAME':'4,5,10,12,16,21,27,28,29,39,41,43,44,45,48,50,51,52,56,58',
 'GENERATED_OR_DOCS_ONLY_CHURN':'7,8,9,13,15,22,31,34,38,46,54',
 'NEW_FEATURE_OR_ENDPOINT':'24,36,37',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'3,18,20,25,26,47,53,55,60',
 'NOT_CONTRACT_RELATED':'1,2,6,11,14,17,19,23,30,32,33,40,42,49,57,59'},
'kapua':{
 'NOT_CONTRACT_RELATED':'1,2,3,4,5,6,11,12,13,19,21,23,25,27,35,38,39,42,43,44,47,50,51,53,54,55,56,57,59,60',
 'GENERATED_OR_DOCS_ONLY_CHURN':'7,9,15,16,17,18,24,30,31,34,37,41,46,48,49,52,58',
 'NEW_FEATURE_OR_ENDPOINT':'14,22',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'40'},
'kratos':{
 'REFACTOR_OR_RENAME':'3,4,5,10,12,17,18,22,23,24,27,32,34,39,40,43,49,50,59',
 'GENERATED_OR_DOCS_ONLY_CHURN':'2,7,9,28,33,36,38,41,44,48,56',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'11,14,15,19,21,26,29,30,31,35,37,42,45,46,47,52,53,54,55,57,58,60',
 'NEW_FEATURE_OR_ENDPOINT':'1,6,25'},
'microcks':{
 'GENERATED_OR_DOCS_ONLY_CHURN':'2,4,12,14,15,18,19,24,40,45,55',
 'REFACTOR_OR_RENAME':'3,6,7,9,11,21,23,33,36,38,47,49,50,57',
 'NEW_FEATURE_OR_ENDPOINT':'1,28,35,37,46,58,59',
 'NOT_CONTRACT_RELATED':'5,8,10,13,16,20,22,26,31,32,34,39,41,42,43,44,48,51,52,53,54,56,60'},
'nessie':{
 'REFACTOR_OR_RENAME':'1,6,8,9,10,12,13,17,19,21,22,25,26,28,29,32,34,37,38,41,45,48,50,52,53,54,55,56,57,58,59,60',
 'GENERATED_OR_DOCS_ONLY_CHURN':'2,3,11,18,23,24,27,30,39,43,44,46,49',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'4,5,15,20,35,36',
 'NOT_CONTRACT_RELATED':'14,31,33,42'},
'ohsome-api':{'REFACTOR_OR_RENAME':'2,4,5,8,9,11,14,16','NOT_CONTRACT_RELATED':'1,3,6,7,10,12,13,15,17,18,19'},
'open-banking-gateway':{
 'REFACTOR_OR_RENAME':'1,3,4,5,6,8,9,10,11,14,19,21,23,24,25,29,30,32,33,35,36,38,41,43,44,46,47,48,49,50,52,54,56,57,58,59',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'7,12,13,15,16,17,18,22,26,27,28,37,39,40,42,45,51,53,55,60',
 'NOT_CONTRACT_RELATED':'2,20,31,34'},
'pay-publicapi':{
 'REFACTOR_OR_RENAME':'1,3,4,7,8,9,10,11,12,13,17,18,20,21,23,24,26,30,31,34,38,40,42,46,47',
 'GENERATED_OR_DOCS_ONLY_CHURN':'2,5,16,19,27,28,33,39',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'6,22,29,35,36,37,43,44,45',
 'NOT_CONTRACT_RELATED':'14,25'},
'polaris':{
 'NOT_CONTRACT_RELATED':'1,3,4,5,6,7,8,9,12,13,15,16,26,36',
 'REFACTOR_OR_RENAME':'10,19,27',
 'GENERATED_OR_DOCS_ONLY_CHURN':'2,11,17,20,21,22,23,24,25,28,29,30,31,35',
 'NEW_FEATURE_OR_ENDPOINT':'32,34,37','BOTH_CHANGED_TO_NEW_BEHAVIOUR':'18,33'},
'quartz-manager':{'REFACTOR_OR_RENAME':'1,2,4,5,6,8,9','NOT_CONTRACT_RELATED':'3,7'},
'rhsm-subscriptions':{
 'REFACTOR_OR_RENAME':'3,4,5,7,8,11,14,16,21,22,23,24,27,30,34,35,37,38,39,41,42,43,45,47,48,54,56,57,58,60',
 'GENERATED_OR_DOCS_ONLY_CHURN':'25,31,49,50,51',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'2,15',
 'NOT_CONTRACT_RELATED':'1,6,9,12,17,18,19,20,26,28,29,32,33,36,40,46,52,55'},
'service-api':{
 'REFACTOR_OR_RENAME':'1,9,10,11,15,18,24,26,28,32,33,35,37,38,42,44,48,49,52,53,54,57,58,59',
 'NOT_CONTRACT_RELATED':'2,3,4,5,6,8,12,13,14,16,17,19,20,21,22,25,27,29,30,31,36,39,40,41,43,45,46,47,50,51,55,56,60',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'23,34'},
'sldt-digital-twin-registry':{'NEW_FEATURE_OR_ENDPOINT':'1,3,4,8','REFACTOR_OR_RENAME':'9','GENERATED_OR_DOCS_ONLY_CHURN':'6,7'},
'strimzi-kafka-bridge':{
 'NOT_CONTRACT_RELATED':'1,3,6,7,8,10,11,14,16,22,23,25,30',
 'REFACTOR_OR_RENAME':'4,9,12,17,18,21,24,28,29',
 'GENERATED_OR_DOCS_ONLY_CHURN':'5,15,20,31',
 'BOTH_CHANGED_TO_NEW_BEHAVIOUR':'19,26,27'},
}
overrides={}
for repo,codes in assignments.items():
 for code,span in codes.items():
  for rank in map(int,span.split(',')):
   assert str(rank) not in overrides.setdefault(repo,{})
   overrides[repo][str(rank)]={'reason_code':code}
# Exact-parent investigations that did not satisfy the acceptance gate.
notes={
('Iced-Latte',11):('NO_PARENT_MISMATCH','Removing bearer security conflicts with parent refresh/logout handlers, which still extract bearer credentials.'),
('Iced-Latte',19):('NO_PARENT_MISMATCH','Payment documentation changes both verb and location; its replacement root path does not match the unchanged controller prefix.'),
('Iced-Latte',42):('NO_PARENT_MISMATCH','Adds password length limits; no parent implementation enforcing the proposed maximum was established.'),
('Iced-Latte',50):('NO_PARENT_MISMATCH','Adds password validation, but the parent reset-password schema also lacks the proposed constraints.'),
('apicurio-registry',15):('NO_PARENT_MISMATCH','Corrects the modifiedOn mapper; the inspected parent version-metadata schema lacks the claimed modifiedOn response property.'),
('apicurio-registry',19):('GENERATED_OR_DOCS_ONLY_CHURN','Reorders media-type/schema pairs without changing either pair; parent JSON and ZIP response meanings already agree.'),
('apicurio-registry',49):('NO_PARENT_MISMATCH','Introduces substring filtering; the parent well-known name parameters do not explicitly promise substring matching.'),
('basyx-java-server-sdk',20):('BOTH_CHANGED_TO_NEW_BEHAVIOUR','Adds encoded cursors to interfaces and controllers; the parent cursor contract describes an opaque server identifier.'),
('gravitee-api-management',19):('OTHER','Duplicate role-deletion response-body proposition already admitted in the T45 set.'),
('hivemq-edge',8):('NO_PARENT_MISMATCH','Renames data-hub headers to If-Match, but the corresponding parent endpoint implementation is unavailable in this clone.'),
('hivemq-edge',51):('NO_PARENT_MISMATCH','Renames specification routes; the concrete parent route interfaces are generated outside the tracked tree.'),
('hivemq-edge',57):('BOTH_CHANGED_TO_NEW_BEHAVIOUR','Changes tagName to name in the model; the parent DomainTag schema also specifies tagName.'),
('kapua',28):('NO_PARENT_MISMATCH','Documents metric restrictions, but the parent helper permits existence predicates without metricType in one branch.'),
('kapua',32):('NO_PARENT_MISMATCH','Removes required permission fields; a complete parent serialization path omitting those fields was not established.'),
('microcks',27):('NO_PARENT_MISMATCH','Adds missing-job 404 responses, but the latest checked-in parent job contract documents only successful responses for these operations.'),
('microcks',29):('NO_PARENT_MISMATCH','Moves mainArtifact to query documentation; Spring RequestParam also accepts multipart form fields, so the prior mismatch is unproved.'),
('nessie',7):('NO_PARENT_MISMATCH','Adds Boolean aliases; checked-in parent material does not independently establish the disputed generated request property names.'),
('service-api',7):('NO_PARENT_MISMATCH','Corrects JSON Patch paths, but the matching parent API contract lives in an unavailable generated API dependency.'),
('strimzi-kafka-bridge',19):('NO_PARENT_MISMATCH','Changes subscription success to 204; the parent OpenAPI document specifies 200, matching the previous response.'),
}
for (repo,rank),(code,reason) in notes.items():
 assert len(reason.split())<=25,(repo,rank)
 overrides.setdefault(repo,{})[str(rank)]={'reason_code':code,'reason':reason}
(K/'review2_signoff.json').write_text(json.dumps(signs,indent=2)+'\n')
(K/'review2_overrides.json').write_text(json.dumps(overrides,indent=2)+'\n')
print('Individual ranked screens signed off; exact-parent deferrals recorded separately.')
