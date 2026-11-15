"""Author the T36 reviews and freeze decisions BEFORE the final-label join.

The judgments below are manually authored after source, hit-context and fallback
review. This script does not read final labels, old labels, or adjudication labels.
"""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
DEST=ROOT/'08_experiments/E2_labelling/pilot_v06'
CODEBOOK='08_experiments/R1_triage_codebook.md'
PROCEDURE='08_experiments/E2_labelling/proposals/CODEBOOK_11_4_PROPOSAL.md'
rows=json.loads((OUT/'working_evidence.json').read_text())
byid={r['item_id']:r for r in rows}
S=byid['B005']['source_root']+'/'
P=byid['P013']['source_root']+'/'
C=byid['C002']['source_root']+'/'
M=byid['M002']['source_root']+'/'
SC='api/src/main/java/se/devscout/scoutapi/'
ST='api/src/test/java/se/devscout/scoutapi/'
SD='data-access/src/main/java/se/devscout/scoutapi/'
PC='src/main/java/io/swagger/petstore/'
CC='src/main/java/app/coronawarn/verification/'
CT='src/test/java/app/coronawarn/verification/'

def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def checklist(a,b,c,ar,br,cr):
 return {
  'a_expected_behavior':{'passes':a,'reason':ar},
  'b_target_scenario':{'passes':b,'reason':br},
  'c_separate_basis':{'passes':c,'reason':cr},
  'd_applicable_revision':{'passes':True,'reason':'Run metadata records EMB 915859080da033fc36feae54bab3ad4a7b04e872, also current shallow checkout; reviewed files are hashed in protected_before.json.'},
  'e_contrary_evidence_reviewed':{'passes':True,'reason':'All raw hits and directed tests/docs/local-history fallback reviewed; contrary or adjacent-branch candidates retained with dispositions.'}}

def manual(locator,category,reason,disposition='context',direction='none',
           expected=True,linked=True,separate=False,extra=None):
 d={'locator':locator,'category':category,'disposition':disposition,'reason':reason,
    'direction':direction,'independence_checklist':checklist(expected,linked,separate,
     reason,'Target constraint/scenario linkage reviewed: '+reason,
     'Independent source or adopted adjudication precedent.' if separate else 'Implementation/context or unverified normative provenance; not an independent vote.')}
 if extra:d.update(extra)
 return d

def dec(l1,l2,reason,review='none_found',both=True,confidence=2,manuals=None,
        messages=None,flag='',root='',exception=''):
 return {'L1':l1,'L2':l2,'confidence':confidence,'both_candidate':both,
  'rationale':reason,'intent_review_verdict':review,'adjudication_flag':flag,
  'root_cause_id':root,'manual_additions':manuals or [],'message_decisions':messages or [],
  'documented_exception':exception,'coverage_gap_unresolved':False,
  'coverage_decision':'All relevant local source/tests/docs/config and available local history reviewed. Binary UI assets/build output are irrelevant. Shallow history limits upstream intent knowledge; no missing local candidate patch remains.'}

D={}
status_ids=['B068','B005','B037','B042','B017']
for ident in status_ids:
 r=byid[ident]
 D[ident]=dec('SPEC','S-STATUS',
  '⚠️ Adopted §11.3 framework-wide 400/404 precedent applies to this binding-error status; success/auth test hits concern different scenarios. This does not establish the input schema policy.',
  review='supports_impl_behavior',both=False,
  root='SCOUT_FRAMEWORK_STATUS',exception='Existing explicit adjudication precedent: codebook §11.3, not a new same-class policy decision.',
  manuals=[manual(CODEBOOK+':277-280','E-CONSIST',
   'Existing §11.3 specifically preserves Scout 400/404 as framework-wide policy; source routes and observed binding-error responses are version matched.',
   'accept','supports_impl_behavior',separate=True,extra={'basis':'adopted_precedent','new_independent_discovery':False}),
   manual(S+SC+'resource/SystemMessageResource.java:73-98','HANDLER','Separate system-message POST/PUT resource consumes DTOs; framework binding precedes method body.'),
   manual(S+SC+'resource/ActivityResourceV2.java:167-186','HANDLER','Activity PUT/PATCH delegates to shared resource after framework binding; no success assertion proves the observed error scenario.'),
   manual(S+ST+'IntegrationTest.java:44-57','HANDLER','Helper expands relative paths to /api/<version>/; default version v1, explicit version v2.')],
  messages=[{'constraint':r['kind']+':'+r['status'],'L1':'SPEC','exchange_lines':r['exchange_lines'],
    'basis':CODEBOOK+':277-280'}])

for ident,resource in [('B012','resource/ActivityResourceV2.java:178-186'),
 ('B043','resource/SystemMessageResource.java:73-78'),
 ('B091','resource/v1/CategoryResource.java:76-83'),
 ('B032','resource/MediaFileResource.java:99-109'),
 ('B027','resource/MediaFileResource.java:286-300')]:
 D[ident]=dec('UNDECIDABLE','',
  '⚠️ Open request schema accepts undeclared keys; strict JSON binding rejects them. Framework status policy does not independently establish whether this input should be accepted. Apply §10.2 and §11.1–11.2.',
  root='SCOUT_OPEN_SCHEMA_BINDING',manuals=[
   manual(S+SC+resource,'HANDLER','DTO binding explains the observed rejection but supplies no independent intent for forbidding additional properties.'),
   manual(CODEBOOK+':221-223','RULE','§10.2 prescribes abstention for open schema versus strict binding without independent intent.')],
  messages=[{'constraint':'open-schema additional-property acceptance versus binding rejection','L1':'UNDECIDABLE',
   'exchange_lines':byid[ident]['exchange_lines'],'basis':CODEBOOK+':221-223'}])

D['P043']=dec('UNDECIDABLE','',
 '⚠️ Missing body is rejected by one controller guard; no independent requirement was found. The other exchange exceeds int32 userStatus. UNDECIDABLE+TEST has no supported SPEC component; conservatively abstain.',
 root='PETSTORE_USER_OPTIONAL_BODY',manuals=[
  manual(P+PC+'controller/UserController.java:139-149','HANDLER','Missing User guard explains 34 exchanges, but code-only intent is insufficient under §11.2.'),
  manual(P+'src/test/java/ip/swagger/petstore/PetStoreTest.java:1-5','E-TEST','Only an empty test class; no independent assertion exists.','reject',expected=False,linked=False),
  manual(P+PC+'model/User.java:15-35','HANDLER','User fields bind Java numeric values; historic request checker omitted int32 bounds.'),
  manual(CODEBOOK+':235-239','RULE','Numeric-format checker gap is a TEST component, not evidence of SPEC intent.')],
 messages=[{'constraint':'optional request body rejected when absent','L1':'UNDECIDABLE','exchange_lines':[n for n in byid['P043']['exchange_lines'] if n!=1358],'count':34},
 {'constraint':'historic int32 userStatus request-validation gap','L1':'TEST','exchange_lines':[1358],'count':1}],
 exception='Aggregation gap: UNDECIDABLE+TEST conservatively UNDECIDABLE; no SPEC evidence to justify SPEC_PARTIAL.')

D['P021']=dec('UNDECIDABLE','',
 '⚠️ Missing upload body is rejected by one code guard; no independent required-body policy was found. Two requests exceed petId int64. Remaining intent is unresolved; no supported SPEC component.',
 root='PETSTORE_UPLOAD_OPTIONAL_BODY',manuals=[
  manual(P+PC+'controller/PetController.java:149-165','HANDLER','File-null rejection is one disputed guard, not independent intent.'),
  manual(P+'src/test/java/ip/swagger/petstore/PetStoreTest.java:1-5','E-TEST','Empty test class; no missing-file assertion.','reject',expected=False,linked=False)],
 messages=[{'constraint':'optional upload body rejected when absent','L1':'UNDECIDABLE','count':60},
  {'constraint':'historic path petId int64 overflow checker gap','L1':'TEST','count':2,'exchange_lines':[577,578]}],
 exception='UNDECIDABLE+TEST conservatively UNDECIDABLE; SPEC_PARTIAL requires a supported SPEC component.')

D['P019']=dec('UNDECIDABLE','',
 '⚠️ Optional name is rejected by a single explicit guard; README is incidental and the test class is empty. Three petId overflows are TEST. Independent required-name intent remains absent.',
 root='PETSTORE_OPTIONAL_NAME',manuals=[
  manual(P+PC+'controller/PetController.java:91-117','HANDLER','Query name is nullable in supplied spec but code checks null; this is precisely the disputed guard.'),
  manual(P+'README.md:1-6','E-DOC','README identifies sample/version and does not require name.','reject',expected=False,linked=False),
  manual(P+'src/test/java/ip/swagger/petstore/PetStoreTest.java:1-5','E-TEST','Empty test class; no missing-name assertion.','reject',expected=False,linked=False)],
 messages=[{'constraint':'optional query name rejected when absent','L1':'UNDECIDABLE','count':63},
  {'constraint':'historic petId int64 overflow checker gap','L1':'TEST','count':3,'exchange_lines':[396,427,428]}],
 exception='UNDECIDABLE+TEST conservatively UNDECIDABLE; absence of independent intent cannot support SPEC_PARTIAL.')

D['C002']=dec('SPEC_PARTIAL','S-REQ-LOOSE',
 '⚠️ Independent missing-key/keyType tests support rejection, while saved schema has no required list. Seven invalid-control-header requests are TEST under §10.3. SPEC+TEST aggregates to SPEC_PARTIAL (§10.4).',
 review='supports_impl_behavior',both=False,root='CWA_MISSING_REQUIRED_KEYS',manuals=[
  manual(C+CT+'VerificationApplicationExternalTest.java:530-558','E-TEST',
   'Tests explicitly send null keyType or key and assert 400; they exercise the same missing-input validation policy as {}.',
   'accept','supports_impl_behavior',separate=True,extra={'tool_miss':True,'new_independent_discovery':True}),
  manual(C+CT+'TestUtils.java:51-53','HANDLER','Constants establish /version/v1/registrationToken; tests use secure requests.'),
  manual(C+CC+'model/RegistrationTokenRequest.java:41-60','HANDLER','@NotNull on key and keyType corroborates the tests; annotations alone would not suffice.'),
  manual(C+'docs/architecture-overview.md:180-194','E-DOC','Independent design document shows request key/keyType, but does not alone prove requiredness.','context',separate=True),
  manual(CODEBOOK+':224-226','RULE','Invalid HTTP control characters in seven cwa-fake headers are TEST, not input-policy evidence.')],
 messages=[{'constraint':'missing key/keyType rejection','L1':'SPEC','count':62},
  {'constraint':'invalid HTTP header control character','L1':'TEST','count':7}],
 exception='Raw conflicting is success 201 versus distinct error branches and generated annotation echoes; scenario filtering plus missed independent tests resolves required-input policy.')

D['C005']=dec('UNDECIDABLE','',
 '⚠️ Missing 404 body is the actual constraint. Tests and architecture prose establish 404, not an empty body. Bodyless methods in one exception-handler class need Claude’s provisional same-class policy review.',
 root='CWA_ERROR_BODY',flag='same_class_policy',manuals=[
  manual(C+CT+'VerificationApplicationInternalTest.java:156-170','E-TEST','Unknown TAN test asserts 404 but never asserts empty response body.','context',linked=False,separate=True),
  manual(C+CT+'TestUtils.java:51-53','HANDLER','Constants resolve the tested route to /version/v1/tan/verify.'),
  manual(C+'docs/architecture-overview.md:243-253','E-DOC','Design document specifies invalid-TAN 404 but has no response-body obligation.','context',linked=False,separate=True),
  manual(C+CC+'controller/VerificationExceptionHandler.java:64-95','E-CONSIST',
   'Binding, validation and verification handlers produce bodyless responses in one class; new same-class policy admissibility requires Claude provisional decision (§12.1 Q3), then supervisor review.',
   'unresolved',expected=True,separate=None),
  manual(C+CC+'controller/InternalTanController.java:103-122','HANDLER','The success branch also builds an empty response; its scenario differs from invalid-TAN 404.')],
 messages=[{'constraint':'documented 404 object body absent','L1':'UNDECIDABLE','count':100}],
 exception='Status-only search cannot resolve response-body intent. All raw status candidates are context or generated/branch-mismatched evidence; no label inferred from them.')

D['P039']=dec('UNDECIDABLE','',
 '⚠️ Percent-encoded backslash reaches Tomcat URI rejection before the controller; no invalid HTTP control-character witness is present. Open path schema versus container security policy stays UNDECIDABLE (§10.3).',
 both=False,root='TOMCAT_BACKSLASH_POLICY',manuals=[
  manual(P+PC+'controller/UserController.java:54-65','HANDLER','The controller is not reached by this URI-rejection branch.'),
  manual(CODEBOOK+':224-226','RULE','Adopted container-security versus open-schema abstention rule applies; no inference that controller guard caused this response.')],
 messages=[{'constraint':'container rejection of encoded backslash','L1':'UNDECIDABLE','count':2}],
 exception='Raw none_found does not automatically set both_candidate: this is a known container-policy ambiguity, not a deliberate disputed local code line.')

for ident,source,logline in [('B066',S+SD+'dao/ActivityDao.java:156-167',162687),
 ('B023',S+SC+'resource/MediaFileResource.java:291-299',63865),
 ('B071',S+SD+'dao/ActivityDao.java:216-223',168301)]:
 D[ident]=dec('IMPL','I-CRASH',
  '⚠️ Saved non-gateway 500 and source/log null dereference establish primary IMPL under R1. Missing resource state does not establish a separate SPEC defect (§10.6).',
  review='not_applicable',both=False,confidence=3,root='SCOUT_MISSING_RESOURCE_CRASH',
  manuals=[manual(source,'HANDLER','Null resource is dereferenced on update/delete.'),
   manual(str(Path(byid[ident]['spec']).with_name('compose.log'))+':'+str(logline),'E-LOG','Saved exception and project frame corroborate the 500; external code was not executed.')],
  messages=[{'constraint':'non-gateway server error','L1':'IMPL','count':int(byid[ident]['occurrences'])}],
  exception='§11.4.1 search exemption: R1 / §9.3 determines primary non-gateway 5xx without intent inference.')

D['P035']=dec('IMPL','I-RESP-CONTRACT',
 'Documented JSON response contains unquoted login text; syntax failure determines IMPL under §9.3 and §10.7. Body contents are withheld because they resemble session material.',
 review='not_applicable',both=False,confidence=3,root='PETSTORE_LOGIN_JSON',manuals=[
  manual(P+PC+'controller/UserController.java:103-109','HANDLER','Controller returns a plain string; saved response JSON parsing fails. No session values copied.'),
  manual(CODEBOOK+':191-192','RULE','Malformed documented JSON is a deterministic implementation-contract failure.')],
 messages=[{'constraint':'malformed documented JSON','L1':'IMPL','count':2}],
 exception='§11.4.1 malformed documented JSON exemption; §10.7 says one-side repair is IMPL rather than BOTH.')

for ident,model,resource,logline in [
 ('B040','SystemMessage','resource/SystemMessageResource.java:73-78',109066),
 ('B094','Tag','resource/v1/CategoryResource.java:55-60',230659)]:
 D[ident]=dec('IMPL','I-CRASH',
  '⚠️ R1 determines primary IMPL. Optional create body and omitted NOT NULL fields cause saved crashes; §10.6 supports a separate SPEC candidate. Final BOTH requires adjudication (§10.1).',
  confidence=3,root='SCOUT_CREATE_REQUIREDNESS',manuals=[
   manual(S+SC+resource,'HANDLER','Create delegates a potentially null entity to persistence.'),
   manual(S+SD+'model/'+model+'.java:35-45','HANDLER','Persistent non-null fields are omitted from saved schema required lists; treated via adopted §10.6, not annotation-only intent.'),
   manual(str(Path(byid[ident]['spec']).with_name('compose.log'))+':'+str(logline),'E-LOG','Saved SQL NOT NULL violation is observed evidence.'),
   manual(CODEBOOK+':241-247','RULE','§10.6 optional create body or missing NOT NULL persistent field is a BOTH candidate; labeller keeps primary IMPL.')],
  messages=[{'constraint':'non-gateway 500','L1':'IMPL'},
   {'constraint':'optional create body/NOT NULL field omission','L1':'SPEC_candidate','authority':CODEBOOK+':241-247'}],
  exception='Raw none_found cannot erase deterministic primary R1 or the established §10.6 dual-defect candidate rule.')

D['B098']=dec('IMPL','I-CRASH',
 '⚠️ Missing id list triggers null dereference and 500. Spec also declares a required path id on a template without {id}, and omits body/list requirements. Keep primary IMPL and request BOTH adjudication.',
 confidence=3,root='SCOUT_FAVOURITES_REQUIREDNESS',manuals=[
  manual(S+SC+'resource/v1/FavouritesResourceV1.java:51-90','HANDLER','POST dereferences nullable properties.id; route has no {id} placeholder.'),
  manual(S+ST+'ActivitiesIntegrationTest.java:112-146','E-TEST','Tests cover populated lists and success; they do not assert missing-list rejection.','context',linked=False,separate=True),
  manual(CODEBOOK+':241-247','RULE','Required resource-key/create-input rule supports dual candidate; malformed in:path declaration is a separate structural witness.')],
 messages=[{'constraint':'non-gateway 500','L1':'IMPL'},
  {'constraint':'missing key/body requiredness and path parameter without placeholder','L1':'SPEC_candidate'}],
 exception='R1 primary plus §10.6/structural witness; no success test is misused as null-input intent.')

D['B087']=dec('IMPL','I-CRASH',
 '⚠️ Missing target causes null dereference; another saved branch violates NOT NULL group. Primary IMPL is certain; optional persistent-field branch merits an additional BOTH-candidate review under §10.6.',
 confidence=3,root='SCOUT_CATEGORY_UPDATE',manuals=[
  manual(S+SC+'resource/TagResource.java:81-88','HANDLER','Null persisted target and copying absent fields are separate crash paths.'),
  manual(S+SD+'model/Tag.java:35-45','HANDLER','Persistent name/group constraints corroborate the second branch.'),
  manual(str(Path(byid['B087']['spec']).with_name('compose.log'))+':216715','E-LOG','GRP NOT NULL SQL failure occurs in a distinct captured request; no change to final label is made.')],
 messages=[{'constraint':'non-gateway 500 on absent target','L1':'IMPL'},
  {'constraint':'optional persistent group omitted then SQL NOT NULL crash','L1':'SPEC_candidate','exchange_lines':[4135]}],
 exception='R1 primary is unaffected by none_found; possible second defect is a review signal under §10.6, not a direct BOTH assignment.')

D['P018']=dec('IMPL','I-RESP-CONTRACT',
 '⚠️ Request status has no enum, response Pet.status does; saved response contains the supplied out-of-enum value. Apply the specific internal-inconsistency rule §10.6: primary IMPL, BOTH candidate.',
 confidence=3,root='PETSTORE_STATUS_INCONSISTENCY',manuals=[
  manual(P+PC+'controller/PetController.java:91-121','HANDLER','Unconstrained query status is assigned directly to persisted Pet and returned.'),
  manual(P+PC+'model/Pet.java:83-90','HANDLER','@Schema enum repeats the model contract; it is not independent intent from the same spec generator.'),
  manual(CODEBOOK+':241-247','RULE','§10.6 explicitly covers a request parameter without enum versus model enum with invalid values stored.')],
 messages=[{'constraint':'out-of-enum response status','L1':'IMPL'},
  {'constraint':'request/model enum inconsistency','L1':'SPEC_candidate'}],
 exception='Specific §10.6 adjudication rule, with both spec pointers and saved witness, overrides code-only none_found abstention for the primary decision.')

D['P013']=dec('UNDECIDABLE','',
 '⚠️ One response member lacks required photoUrls. Field default/setter and XML annotations do not independently establish JSON presence intent; tests are empty and local import history is non-normative. Abstain under §11.2.',
 root='PETSTORE_PHOTOURLS_PRESENCE',manuals=[
  manual(P+PC+'model/Pet.java:32-70','HANDLER','Default empty list, public setter and XML annotations are context, not independent JSON requiredness evidence.'),
  manual(P+PC+'data/PetData.java:115-135','HANDLER','Factory may pass a nullable list to setter; this explains state but not intended JSON contract.'),
  manual(P+'src/test/java/ip/swagger/petstore/PetStoreTest.java:1-5','E-TEST','Only an empty test class; no JSON field-presence assertion.','reject',expected=False,linked=False)],
 messages=[{'constraint':'required photoUrls absent at response /6','L1':'UNDECIDABLE','count':1,'exchange_lines':[211]}])

for ident,model in [('M002','CartItemDTOReq'),('M013','UserDTOReq')]:
 manuals=[manual(M+'market-rest/src/main/java/market/rest/exception/RestExceptionHandler.java:37-42','HANDLER','Generic exception mapper returns 500 for HAL JSON parse errors.'),
  manual(M+'market-core/src/main/java/market/dto/'+('CartItemDTO.java:10-20' if ident=='M002' else 'UserDTO.java:8-29'),'HANDLER','DTO inherits RepresentationModel; saved request schema describes _links as an array, and captured array input raises Expected relation name.'),
  manual(CODEBOOK+':241-247','RULE','Adopted §10.6 explicitly covers market _links shape disagreement converted to 5xx; primary IMPL and dual candidate.')]
 review='none_found'
 if ident=='M013':
  manuals.append(manual(M+'market-web/src/main/resources/templates/rest.html:52-60','E-DOC',
   'Registration guide assigns 406 to validation failures after data binding; its example is an invalid name. The observed case fails HAL parsing before validation. Do not infer that this paragraph specifies the HAL parser branch.',
   'context',linked=False,separate=True,extra={'new_independent_discovery':False,'tool_miss':False,
   'scope_caveat':'No specific HAL _links type or parse-failure status obligation.'}))
 D[ident]=dec('IMPL','I-CRASH',
  '⚠️ Saved array _links produces HAL parse failure and generic 500. R1 determines primary IMPL; §10.6 supplies the separate schema-shape candidate. Success docs/UI tests do not establish parse-error intent.',
  review=review,confidence=3,root='MARKET_HAL_LINKS',manuals=manuals,
  messages=[{'constraint':'HAL parse failure mapped to 500','L1':'IMPL'},
   {'constraint':'array _links schema versus HAL representation','L1':'SPEC_candidate'}],
  exception='R1 primary and explicit market-_links §10.6 rule apply. '+(
   'Registration 406 validation prose is context for a later branch, not independent proof about HAL parse failures; no third-behavior intent is accepted for this scenario.' if ident=='M013' else
   'Raw supports_spec success examples are rejected for the parse-error scenario; reviewed none_found does not erase the deterministic primary.'))

assert set(D)==set(byid)

def raw_review(ident,i,h):
 r=byid[ident];cat=h['category'];loc=r['source_root']+'/'+h['location']
 a,b,c=True,True,False;disp='context';direction='none'
 reason='Implementation route/DTO/return is context only and cannot be its own independent intent evidence.'
 if cat=='E-TEST':
  c=True;b=False;disp='reject'
  if ident=='B068' or (ident in {'B005','B017','B012'} and h['line']!=216):
   reason='Full test/helper context shows a different operation, method, version, or success branch; not this binding-error scenario. The 146 assertion is GET favourites, not the queried PUT/POST/PATCH.'
  elif ident in {'B005','B017','B012'}:
   reason='Helper is a successful PUT/PATCH with valid fixture; it does not assert behavior for undeclared JSON keys or the observed 400 branch.'
  elif ident=='B037':
   reason='Test covers low-authority 403 on valid DTO; observed case is admin-context JSON binding 400, before application auth. Adjacent POST/DELETE assertions are also different methods.'
  elif ident=='B098':
   disp='context';reason='POST populated-list and GET success assertions establish normal operation only; they do not require omitted id list/body or establish missing-input behavior.'
  elif ident=='M002':
   reason='Other-module UI GET /customer/new renders a view. No REST cart-controller/parse-error linkage; never independent for this item.'
 elif cat=='E-DOC':
  if ident in {'C005','C002'}:
   c=False;b=False
   reason=('Handler Javadoc/@ApiResponse is generated-contract or disputed-handler context with no separate normative provenance. '+
     ('200/404 branches do not assert the questioned empty 404 body.' if ident=='C005' else
      '201 success and duplicate/unknown-key 400 branches do not independently require missing key/keyType.'))
  elif ident in {'P019','P018'}:
   a=False;b=False;c=True;disp='reject';reason='README line identifies sample/branch; incidental words do not assert missing-name policy or permitted status values.'
  elif ident=='M002':
   c=True;b=False
   if h['file'].endswith('CartRestController.java'):
    c=False;reason='Handler-adjacent success Javadoc has no independent provenance and says nothing about HAL parsing failure.'
   elif h['file']=='README.adoc':
    a=False;disp='reject';reason='Feature list says cart is persisted; it gives no status, field-shape or parse-error policy.'
   elif h['line'] in {193,78}:
    disp='reject';reason='Full documentation row is cart payment/order success 201, not cart PUT or HAL parse rejection; proximity and translated copies add no evidence.'
   else:
    disp='context';reason='Cart-add success 200 prose is applicable only to valid add-item requests. It does not decide array _links parsing; README/template are duplicated descriptions.'
  elif ident=='M013':
   if h['file'].endswith('CustomerRestController.java'):
    c=False;b=False;reason='Handler registration-success Javadoc repeats implementation context; no separate normative provenance or HAL parse-error statement.'
   elif h['line'] in {57,60,166}:
    c=True;b=False;disp='context'
    reason='Full registration paragraph/table describes 406 for validation errors and exemplifies invalid name after binding. The actual case fails HAL parsing before validation; no branch linkage establishes this as parse-error intent. Repeated descriptions add no independent votes.'
   else:
    c=True;b=False;disp='context';reason='Registration route/input/success text is adjacent context. 200 success differs from current annotated 201, but neither is the observed format-error branch; sensitive example line is not quoted.'
 elif cat=='E-CONSIST':
  c=True;b=False;disp='context'
  reason='Full classes show distinct bad-request branches. Generic validation mapper is useful context, but other token/key-type errors do not independently specify missing key/keyType or prove the saved model requiredness.'
 elif cat=='E-HISTORY':
  a=False;b=False;c=False;disp='reject'
  reason='Full local message and file patch are a shallow EMB merge/import (entire file added), not a behavior-specific developer fix. No upstream intent direction can be inferred.'
 d={'hit_index':i,'raw_hit_locator':'09_collab/logs/T36_scratch/search/'+ident+'.json:$.hits['+str(i)+']',
  'source_locator':loc,'category':cat,'disposition':disp,'reason':reason,
  'direction':direction,'tool_independent_hypothesis':h.get('independent',False),
  'tool_support':h.get('support',[]),'independence_checklist':checklist(a,b,c,
   'Explicit assertion/proposition exists in context.' if a else 'No target expected-behavior proposition.',
   reason,'Separate test/doc basis, subject to scenario gate.' if c else 'Questioned code/spec, generated echo, or import history; not independent.'),
  'source_file_sha256':sha(r['source_root']+'/'+h['file'])}
 # All source windows were read beyond the 160-character tool snippet.
 d['reviewed_context_locator']=r['source_root']+'/'+h['file']+':'+str(max(1,h['line']-12))+'-'+str(min(len((ROOT/r['source_root']/h['file']).read_text().splitlines()),h['line']+12))
 if cat=='E-HISTORY':
  d['patch_locator']='09_collab/logs/T36_scratch/fallback/patch_'+ident+'.txt:1'
 return d

def main():
 if (OUT/'decisions_frozen.csv').exists():raise SystemExit('Refusing to overwrite frozen decisions')
 decisions=[];review_hashes={}
 for r in rows:
  ident=r['item_id'];d=D[ident];manifest=json.loads((OUT/'search'/(ident+'.manifest.json')).read_text())
  raw=json.loads((OUT/'search'/(ident+'.json')).read_text())
  hits=[raw_review(ident,i,h) for i,h in enumerate(raw.get('hits',[]))]
  provenance=json.loads((ROOT/Path(r['spec']).with_name('run.json')).read_text())
  review={'item_id':ident,'created_utc':now(),'decision_precedes_final_join':True,
   'operation':{'method':r['method'],'template':r['template'],'status':int(r['status'])},
   'target':{'kind':r['kind'],'message':r['message'] or r['kind'],'violation_path':r['pointer'],
    'observed_field_direction':manifest['field_direction'],
    'representative_exchange_locator':manifest['representative_exchange_locator'],
    'all_exchange_lines':r['exchange_lines'],'observed_response_group_count':len(r['response_groups'])},
   'prior_exposure':{'previous_baseline_labelling':'known (T15/T16/T18 same model family/task history)',
    'previous_final_label':'confirmed current read of B005 before sample' if ident=='B005' else 'possible from previous tasks; exact item final label not recalled before decision',
    'stratum_order_leaks_label':True,'T33_worked_example_excluded':True,
    'other_incidents_locator':'09_collab/logs/T36_scratch/incident.json:1'},
   'manifest_locator':'09_collab/logs/T36_scratch/search/'+ident+'.manifest.json:1',
   'search_mandatory':manifest['mandatory'],'search_gate_rule':manifest['gate_rule'],
   'search_order':['HANDLER','E-TEST','E-DOC','E-CONSIST','E-HISTORY'],
   'source_root':r['source_root'],'source_revision':provenance['emb_commit'],
   'source_revision_locator':str(Path(r['spec']).with_name('run.json'))+':$.emb_commit',
   'spec_sha256':manifest['spec_sha256'],'tool_sha256':manifest['tool_sha256'],
   'coverage_inventory_locator':'09_collab/logs/T36_scratch/coverage_inventory.json:$."'+r['sut']+'"',
   'raw_verdict':manifest['raw_verdict'],'hits':hits,'manual_additions':d['manual_additions'],
   'manual_fallback':{'performed':manifest['mandatory'],
    'manifest_locator':'09_collab/logs/T36_scratch/fallback_manifest.json:1',
    'local_history':'Available shallow EMB import only; patches reviewed, not treated as fixes.',
    'docs_scope':'No top-level Scout README/CHANGELOG; only explicit source paths used after discarded scope incident.',
    'new_independent_evidence':any(h.get('new_independent_discovery') for h in d['manual_additions']) or any(h['disposition']=='accept' for h in hits)},
   'reviewed_verdict':d['intent_review_verdict'],'decision':{k:v for k,v in d.items() if k!='manual_additions'},
   'unresolved_hits_do_not_support_decisive_intent':ident=='C005',
   'effort':{'tool_seconds':manifest['elapsed_seconds'],'raw_hit_count':len(hits),
    'manual_addition_count':len(d['manual_additions']),
    'manual_active_seconds':None,'timing_note':'Manual reasoning shared source-family context; per-item active time was not independently instrumented. Do not interpret generation time as review effort.'}}
  target=DEST/'review'/(ident+'.json')
  if target.exists():raise SystemExit('Refusing to overwrite review '+ident)
  target.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
  review_hashes[str(target.relative_to(ROOT))]=sha(str(target.relative_to(ROOT)))
  locs=[manifest['representative_exchange_locator'],manifest['spec_locator']]
  locs += [x['locator'] for x in d['manual_additions']]
  types=['E-OBS']
  for x in d['manual_additions']:
   if x['category']=='HANDLER':types.append('E-CODE-INTENT')
   elif x['disposition']=='accept':types.append(x['category'])
  if any(x['disposition']=='accept' for x in hits):types.append('E-DOC')
  record={k:r[k] for k in ['item_id','sut','method','template','kind','status','pointer','occurrences','message']}
  record.update({k:d[k] for k in ['L1','L2','confidence','both_candidate','rationale','root_cause_id']})
  record['both_candidate']=str(record['both_candidate']).lower()
  record.update({'proposed_L2':'','evidence_types':';'.join(dict.fromkeys(types)),
   'evidence_locators':';'.join(locs),
   'intent_search_status':'complete' if manifest['mandatory'] else 'not_run',
   'intent_search_verdict':manifest['raw_verdict'],'intent_review_verdict':d['intent_review_verdict'],
   'intent_search_locator':'09_collab/logs/T36_scratch/search/'+ident+'.json:1;09_collab/logs/T36_scratch/search/'+ident+'.manifest.json:1',
   'intent_review_locator':str(target.relative_to(ROOT))+':1',
   'adjudication_flag':d['adjudication_flag'] or 'none',
   'prior_exposure':'known_prior_baseline_labelling;possible_prior_final;stratum_order_nonblind'+(';confirmed_B005_final_read' if ident=='B005' else '')})
  decisions.append(record)
 with (OUT/'decisions_frozen.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(decisions[0]));writer.writeheader();writer.writerows(decisions)
 freeze={'frozen_utc':now(),'decisions_sha256':sha(str((OUT/'decisions_frozen.csv').relative_to(ROOT))),
  'review_sha256':review_hashes,'sample_sha256':sha(str((OUT/'sample.json').relative_to(ROOT))),
  'final_labels_joined':False,'final_labels_read_by_this_script':False}
 (OUT/'decision_freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
 print(json.dumps({'frozen_items':len(decisions),'raw_hits_reviewed':sum(len(json.loads((DEST/'review'/(r['item_id']+'.json')).read_text())['hits']) for r in rows),
  'frozen_utc':freeze['frozen_utc']}))

if __name__=='__main__':main()
