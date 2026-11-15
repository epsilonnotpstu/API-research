"""Record F2's manual adjudications and validate their local evidence locators."""
import collections
import csv
import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = list(csv.DictReader((ROOT/'items.csv').open()))
SPECS = {p:json.loads((ROOT/p/'spec.json').read_text()) for p in ['K01','K02','K03','K04']}
ALIASES = {
 'media':'K01/source/api/src/main/java/se/devscout/scoutapi/resource/MediaFileResource.java',
 'category':'K01/source/api/src/main/java/se/devscout/scoutapi/resource/v1/CategoryResource.java',
 'tag':'K01/source/api/src/main/java/se/devscout/scoutapi/resource/TagResource.java',
 'tagmodel':'K01/source/data-access/src/main/java/se/devscout/scoutapi/model/Tag.java',
 'tagdao':'K01/source/data-access/src/main/java/se/devscout/scoutapi/dao/TagDao.java',
 'systemmessage':'K01/source/api/src/main/java/se/devscout/scoutapi/resource/SystemMessageResource.java',
 'system':'K01/source/api/src/main/java/se/devscout/scoutapi/resource/SystemResource.java',
 'activity':'K01/source/api/src/main/java/se/devscout/scoutapi/resource/ActivityResourceV2.java',
 'activitymodel':'K01/source/data-access/src/main/java/se/devscout/scoutapi/model/ActivityProperties.java',
 'app':'K01/source/api/src/main/java/se/devscout/scoutapi/ScoutAPIApplication.java',
 'abstract':'K01/source/api/src/main/java/se/devscout/scoutapi/resource/AbstractResource.java',
 'user':'K01/source/api/src/main/java/se/devscout/scoutapi/resource/UserResource.java',
 'usermodel':'K01/source/data-access/src/main/java/se/devscout/scoutapi/model/User.java',
 'mediatest':'K01/source/api/src/test/java/se/devscout/scoutapi/MediaFilesIntegrationTest.java',
 'systemtest':'K01/source/api/src/test/java/se/devscout/scoutapi/SystemIntegrationTest.java',
 'tagtest':'K01/source/api/src/test/java/se/devscout/scoutapi/TagsIntegrationTest.java',
 'usertest':'K01/source/api/src/test/java/se/devscout/scoutapi/UsersIntegrationTest.java',
 'integration':'K01/source/api/src/test/java/se/devscout/scoutapi/IntegrationTest.java',
 'cart':'K02/source/market-rest/src/main/java/market/rest/CartRestController.java',
 'contacts':'K02/source/market-rest/src/main/java/market/rest/ContactsRestController.java',
 'customer':'K02/source/market-rest/src/main/java/market/rest/CustomerRestController.java',
 'orders':'K02/source/market-rest/src/main/java/market/rest/OrdersRestController.java',
 'products':'K02/source/market-rest/src/main/java/market/rest/ProductsRestController.java',
 'resthandler':'K02/source/market-rest/src/main/java/market/rest/exception/RestExceptionHandler.java',
 'webhandler':'K02/source/market-web/src/main/java/market/controller/SpringExceptionHandler.java',
 'restdoc':'K02/source/market-web/src/main/resources/templates/rest.html',
 'legacydoc':'K02/source/README_RU.md',
 'marketreadme':'K02/source/README.adoc',
 'contactdto':'K02/source/market-core/src/main/java/market/dto/ContactsDTO.java',
 'cartdto':'K02/source/market-core/src/main/java/market/dto/CartDTO.java',
 'productdto':'K02/source/market-core/src/main/java/market/dto/ProductDTO.java',
 'userdto':'K02/source/market-core/src/main/java/market/dto/UserDTO.java',
 'carttest':'K02/source/market-core/src/test/java/market/service/CartServiceTest.java',
 'architecture':'K03/source/docs/architecture-overview.md',
 'externaltan':'K03/source/src/main/java/app/coronawarn/verification/controller/ExternalTanController.java',
 'externaltoken':'K03/source/src/main/java/app/coronawarn/verification/controller/ExternalTokenController.java',
 'teststate':'K03/source/src/main/java/app/coronawarn/verification/controller/ExternalTestStateController.java',
 'internaltan':'K03/source/src/main/java/app/coronawarn/verification/controller/InternalTanController.java',
 'verificationhandler':'K03/source/src/main/java/app/coronawarn/verification/controller/VerificationExceptionHandler.java',
 'registration':'K03/source/src/main/java/app/coronawarn/verification/model/RegistrationTokenRequest.java',
 'registrationvalidator':'K03/source/src/main/java/app/coronawarn/verification/validator/RegistrationTokenRequestValidator.java',
 'externaltest':'K03/source/src/test/java/app/coronawarn/verification/VerificationApplicationExternalTest.java',
 'internaltest':'K03/source/src/test/java/app/coronawarn/verification/VerificationApplicationInternalTest.java',
 'testutils':'K03/source/src/test/java/app/coronawarn/verification/TestUtils.java',
 'pet':'K04/source/src/main/java/io/swagger/petstore/controller/PetController.java',
 'petmodel':'K04/source/src/main/java/io/swagger/petstore/model/Pet.java',
 'categorymodel':'K04/source/src/main/java/io/swagger/petstore/model/Category.java',
 'petuser':'K04/source/src/main/java/io/swagger/petstore/controller/UserController.java',
 'petusermodel':'K04/source/src/main/java/io/swagger/petstore/model/User.java',
 'userdata':'K04/source/src/main/java/io/swagger/petstore/data/UserData.java',
 'petorder':'K04/source/src/main/java/io/swagger/petstore/controller/OrderController.java',
 'petordermodel':'K04/source/src/main/java/io/swagger/petstore/model/Order.java',
 'pettest':'K04/source/src/test/java/ip/swagger/petstore/PetStoreTest.java',
 'petreadme':'K04/source/README.md',
 'inflector':'K04/source/inflector.yaml',
 'checker':'../../tools/conformance.py',
}

def loc(alias, line):
    return ALIASES[alias]+':'+str(line)

def pointer_escape(s):return s.replace('~','~0').replace('/','~1')

def operation_pointer(item):
    return '/paths/'+pointer_escape(item['template'])+'/'+item['method'].lower()

DATA = {}
def row(n,l1,l2,proposed,conf,both,verdict,refs,rationale,types='E-CODE-INTENT',flag='none'):
    DATA[n]={'L1':l1,'L2':l2,'proposed_L2':proposed,'confidence':conf,'both_candidate':both,
        'intent_review_verdict':verdict,'refs':refs,'rationale':rationale,'evidence_types':types,
        'adjudication_flag':flag}

row(1,'UNDECIDABLE','NA','S-STATUS',2,True,'none_found',[('media',291)],
    'Unknown-property JSON yields undocumented 400. The binding response and handler show behavior, but no independent test or documentation establishes this error-status policy.')
row(2,'IMPL','I-CRASH','',3,True,'not_applicable',[('customer',52),('resthandler',37),('userdto',10)],
    'Parsing schema-permitted _links:[] produces 500. The catch-all handler turns client input into server failure; the incompatible links structure also qualifies as a spec defect under §10.6.','E-CODE-INTENT;E-CONV')
row(3,'SPEC','S-REQ-STRICT','',2,False,'supports_impl_behavior',[('cart',87),('restdoc',133),('restdoc',135),('carttest',229),('carttest',232)],
    'The documented clear-cart operation and linked service test need only the authenticated customer. The handler has no name query input; the recorded request succeeds without it.','E-CODE-INTENT;E-DOC;E-TEST')
row(4,'SPEC','S-REQ-STRICT','',2,False,'supports_impl_behavior',[('category',43),('abstract',55),('usertest',82),('usertest',86)],
    'The shared attrs filter accepts comma-separated names. An independent integration test successfully sends id,identities through that filter, contradicting a one-character maximum.','E-CODE-INTENT;E-TEST;E-CROSS')
row(5,'IMPL','I-CRASH','',3,True,'not_applicable',[('category',60),('tag',61),('tagmodel',37),('tagmodel',41)],
    'Empty category creation violates persistent NOT NULL group/name requirements and escapes as 500. The request schema omits those required fields; §10.6 supports the additional spec-defect flag.','E-CODE-INTENT;E-CONV')
row(6,'UNDECIDABLE','NA','S-REQ-LOOSE',2,True,'none_found',[('pet',99),('pettest',3),('petreadme',8)],
    'The missing-name guard returns 400 although name is optional in the contract. No scenario-specific test or independent documentation resolves whether the guard or optionality is wrong.')
row(7,'UNDECIDABLE','NA','S-REQ-STRICT',2,True,'none_found',[('category',33),('tagdao',40)],
    'The group filter accepts the longer string, but neither the shared implementation nor unrelated group fixtures independently establishes the intended query-length policy.')
row(8,'UNDECIDABLE','NA','S-REQ-STRICT',2,True,'none_found',[('pet',213),('pet',220),('petmodel',83)],
    'Update accepts an absent status and stores the supplied pet. No independent evidence establishes whether the tightened request required list or the permissive update is intended.')
row(9,'IMPL','I-CRASH','',3,False,'not_applicable',[('systemmessage',100),('systemmessage',102)],
    'Updating nonexistent id 0 dereferences the absent stored message and returns 500. The matching log identifies the null dereference; §10.6 classifies missing-resource crashes as implementation faults.','E-CODE-INTENT;E-CONV')
row(10,'SPEC','S-METHOD','',3,False,'supports_impl_behavior',[('media',233),('mediatest',165),('mediatest',167),('integration',57)],
    'Independent media CRUD tests exercise GET by id using the resolved API prefix. Its omission from the contract is established even though this representative oversized id returns 404.','E-CODE-INTENT;E-TEST')
row(11,'IMPL','I-CRASH','',3,True,'supports_impl_behavior',[('cart',75),('resthandler',37),('restdoc',126),('restdoc',128)],
    'PUT cart is independently documented but absent from the contract. Its _links parse error becomes 500; the primary attribution follows the server-error rule, with the omitted operation flagged separately.','E-CODE-INTENT;E-DOC;E-CONV')
row(12,'UNDECIDABLE','NA','S-RESP-MISSING',2,True,'none_found',[('pet',199),('pet',196),('petmodel',83)],
    'The form create response omits required status. Handler echoing and a nullable model explain the omission, but no independent evidence determines the response-field obligation.')
row(13,'IMPL','I-CRASH','',3,True,'not_applicable',[('category',60),('tag',61),('tagmodel',37),('tagmodel',41)],
    'The same empty category request fails on persistent NOT NULL fields and returns 500. The schema also permits omission of those fields; apply §10.6 with primary IMPL.','E-CODE-INTENT;E-CONV')
row(14,'UNDECIDABLE','NA','S-REQ-STRICT',2,True,'none_found',[('pet',205),('pet',220),('categorymodel',36)],
    'Category name Dogs exceeds the request maximum and is accepted. Model setters and the contract example are insufficient independent evidence of the intended length constraint.')
row(15,'SPEC','S-RESP-MISSING','',2,False,'supports_impl_behavior',[('contacts',59),('cart',125),('products',64),('contactdto',13),('cartdto',12)],
    'Independent controller classes attach named relations to the shared RepresentationModel DTO family. This corroborates a dynamic HAL relation policy that the closed empty-only _links schema incorrectly forbids.','E-CODE-INTENT;E-CONSIST')
row(16,'IMPL','I-CRASH','',3,True,'supports_impl_behavior',[('media',258),('media',260),('mediatest',133),('mediatest',134)],
    'Download tests independently establish the omitted route. The nonexistent media id then causes a logged null dereference and 500; both defects are evidenced, with primary IMPL.','E-CODE-INTENT;E-TEST;E-CONV')
row(17,'SPEC','S-METHOD','',3,False,'supports_impl_behavior',[('system',25),('systemtest',34),('systemtest',36),('integration',57)],
    'The resolved GET ping test explicitly expects 204, matching the handler and exchange. The contract omits this independently tested operation.','E-CODE-INTENT;E-TEST')
row(18,'SPEC','S-STATUS','',2,False,'supports_impl_behavior',[('cart',113),('resthandler',74),('webhandler',67),('restdoc',143),('restdoc',146)],
    'The payment documentation specifies 406 for invalid card input, corroborated by validation handlers in separate classes. Success-branch 201 evidence does not contradict this observed validation branch.','E-CODE-INTENT;E-DOC;E-CONSIST')
row(19,'SPEC','S-REQ-STRICT','',2,False,'supports_impl_behavior',[('orders',40),('restdoc',195),('restdoc',197)],
    'The independent REST interface documents listing the authenticated customer’s orders without a name query input. The controller uses only Principal; the added required name constraint rejects the observed intended call.','E-CODE-INTENT;E-DOC')
row(20,'SPEC','S-REQ-STRICT','',2,False,'supports_impl_behavior',[('cart',87),('restdoc',133),('restdoc',135),('carttest',229)],
    'The documented clear-cart interface does not consume a name filter, and the linked service clears by authenticated customer alone. The arbitrary query-name maximum therefore overconstrains this operation.','E-CODE-INTENT;E-DOC;E-TEST')
row(21,'IMPL','I-CRASH','',3,False,'not_applicable',[('orders',53),('resthandler',37)],
    'The unbounded integer schema permits this id, but Java long conversion fails into the generic 500 handler. R1 establishes I-CRASH; independent evidence does not establish the intended numeric bound.','E-CODE-INTENT;E-CONV')
row(22,'UNDECIDABLE','NA','S-RESP-MISSING',2,True,'none_found',[('petuser',34),('petuser',44),('petusermodel',62)],
    'Creating an empty user returns no lastName despite the response required list. Echoing a nullable field explains the behavior but does not establish the intended field-presence obligation.')
row(23,'UNDECIDABLE','NA','S-METHOD',2,True,'none_found',[('petorder',34),('petorder',37),('pettest',3),('petreadme',8)],
    'Inventory responds successfully and has a matching handler, but no independent test or operation-specific documentation establishes whether the route belongs in the public contract.')
row(24,'UNDECIDABLE','NA','S-RESP-MISSING',2,True,'none_found',[('activity',113),('activitymodel',286),('app',226)],
    'The revision omits time_max after empty creation. Retrieved success assertions do not assert this field or scenario; nullable model and serialization policy alone cannot settle the response obligation.')
row(25,'IMPL','I-CRASH','',3,False,'not_applicable',[('media',293),('media',295)],
    'Updating nonexistent media id 0 dereferences a null stored entity. The matching log and 500 establish I-CRASH; missing-resource handling is the implementation’s responsibility.','E-CODE-INTENT;E-CONV')
row(26,'IMPL','I-CRASH','',3,False,'not_applicable',[('petuser',166),('petuser',169),('userdata',55)],
    'The documented form update produces a non-gateway 500. The overloaded update and user lookup provide source context, but the precise exception is not established by the available log.','E-CODE-INTENT;E-CONV')
row(27,'UNDECIDABLE','NA','S-RESP-MISSING',2,True,'none_found',[('activity',113),('activitymodel',262),('app',226)],
    'The properties object omits participants_min after empty creation. Tests asserting successful activity operations do not establish this field’s required presence; serialization behavior alone is insufficient.')
row(28,'UNDECIDABLE','NA','S-REQ-LOOSE',2,True,'none_found',[('tag',81),('tagtest',56),('tagtest',82)],
    'The open request schema permits these extra JSON properties, while binding rejects them. Retrieved normal CRUD tests do not exercise unknown properties; §10.2 leaves the binding policy undecidable.')
row(29,'SPEC','S-METHOD','',3,False,'supports_impl_behavior',[('externaltan',51),('externaltan',96),('externaltest',200),('externaltest',205),('testutils',51),('architecture',204)],
    'The architecture guide and resolved integration test independently define POST tan, including 400 for an unknown registration token. Its missing contract operation is a specification defect.','E-CODE-INTENT;E-DOC;E-TEST')
row(30,'SPEC','S-METHOD','',2,False,'supports_impl_behavior',[('cart',38),('cart',61),('contacts',59),('restdoc',121),('restdoc',123)],
    'The independent cart interface describes GET cart, and another controller links clients to the current cart controller. These corroborate the implemented route omitted from the specification.','E-CODE-INTENT;E-DOC;E-CONSIST')
row(31,'SPEC','S-RESP-MISSING','',3,False,'supports_impl_behavior',[('products',37),('products',46),('restdoc',35),('restdoc',37)],
    'The independent products-list example explicitly uses links arrays, matching the collection response. The closed response schema forbids that documented property.','E-CODE-INTENT;E-DOC')
row(32,'UNDECIDABLE','NA','S-REQ-LOOSE',2,True,'none_found',[('petuser',72),('petuser',88),('pettest',3)],
    'The list and array methods both reject empty arrays within one class. Without independent evidence, their repetition raises the same-class-policy ambiguity rather than proving the missing minItems constraint.','E-CODE-INTENT','same_class_policy')
row(33,'UNDECIDABLE','NA','S-METHOD',2,True,'none_found',[('pet',149),('pet',163),('pettest',3),('inflector',1)],
    'The missing-pet upload response matches the upload handler, but only handler/configuration context supports the route. No independent evidence settles whether its omission from the public contract is erroneous.')
row(34,'TEST','NA','T-ORACLE-COVERAGE',3,False,'not_applicable',[('petorder',71),('checker',307),('checker',313),('checker',467)],
    'This item reports unsupported form-body validation, a checker capability gap. The observed 500 is a separate implementation-error component; it does not make the checker’s unsupported-encoding message an API-contract defect.','E-AUX;E-CODE-INTENT')
row(35,'UNDECIDABLE','NA','S-RESP-MISSING',2,True,'none_found',[('pet',58),('pet',68),('petmodel',65),('petmodel',69)],
    'The result includes a stored pet lacking photoUrls. Neither the empty test class nor generic documentation establishes whether creation/storage or the required response-field policy is wrong.')
row(36,'UNDECIDABLE','NA','S-RESP-MISSING',2,True,'none_found',[('petorder',58),('petorder',68),('petordermodel',81)],
    'The XML-created order is returned without shipDate. The handler echoes a nullable model field, but no independent evidence establishes whether the server should supply it or the response requirement is excessive.')
row(37,'TEST','NA','T-FIXTURE-STATE',3,False,'supports_impl_behavior',[('teststate',149),('externaltest',772),('externaltest',779),('architecture',175)],
    'The request contains an unregistered token. An external-profile test and the use-case guide explicitly require 400 for this state; schema validity alone does not promise a successful lookup.','E-CODE-INTENT;E-TEST;E-DOC')
row(38,'SPEC','S-REQ-STRICT','',2,False,'supports_impl_behavior',[('category',43),('tag',44),('tagdao',44),('tagtest',54),('tagtest',56),('integration',57)],
    'The independent tags-list test omits the count filter and succeeds. Category delegates to that same listing implementation, whose null filter means no threshold; the required query constraint is excessive.','E-CODE-INTENT;E-TEST;E-CROSS')
row(39,'UNDECIDABLE','NA','S-METHOD',2,True,'none_found',[('pet',233),('pet',245),('pettest',3),('petreadme',8)],
    'The tags search response matches the dedicated handler, but the available tests and generic README do not independently establish its public-operation intent.')
row(40,'IMPL','I-CRASH','',3,False,'not_applicable',[('orders',53),('resthandler',37)],
    'The schema declares integer without format or bounds. The enormous id cannot convert to Java long and reaches the generic 500 handler; the non-gateway server failure establishes I-CRASH.','E-CODE-INTENT;E-CONV')
row(41,'IMPL','I-CRASH','',3,False,'not_applicable',[('petuser',61),('petuser',63),('userdata',55)],
    'GET user returns a non-gateway 500 despite a source branch for missing-user 404. The lookup dereferences stored usernames; the exact triggering state is uncertain, but the observed server failure is decisive.','E-CODE-INTENT;E-CONV')
row(42,'UNDECIDABLE','NA','S-REQ-STRICT',2,True,'none_found',[('petuser',103),('petuser',109),('pettest',3)],
    'The login handler ignores absent credentials and returns a session string. No independent test or normative documentation resolves whether permissive sample behavior or the required username contract is intended.')
row(43,'SPEC','S-METHOD','',2,False,'supports_impl_behavior',[('cart',98),('cart',99),('restdoc',138),('restdoc',140),('carttest',214),('carttest',217)],
    'The delivery interface explicitly specifies PUT with included, and a linked service test verifies false changes delivery state. The current controller prefix resolves the route omitted from the contract.','E-CODE-INTENT;E-DOC;E-TEST')
row(44,'SPEC','S-STATUS','',3,False,'supports_impl_behavior',[('customer',52),('resthandler',74),('webhandler',67),('restdoc',55),('restdoc',57),('restdoc',166)],
    'The current registration guide explicitly promises 406 for validation failures, corroborated by independent validation-handler classes. The empty-object validation response is missing from the documented statuses.','E-CODE-INTENT;E-DOC;E-CONSIST')
row(45,'SPEC','S-RESP-MISSING','',3,False,'supports_impl_behavior',[('products',37),('products',46),('restdoc',35),('restdoc',37)],
    'The independently documented products-list representation uses links arrays rather than _links objects. Requiring _links in each collection item contradicts that example and the matching observed representation.','E-CODE-INTENT;E-DOC')
row(46,'UNDECIDABLE','NA','S-RESP-MISSING',2,True,'none_found',[('internaltan',122),('verificationhandler',93),('verificationhandler',95),('architecture',251)],
    'The unknown-TAN branch returns an empty 404 while its response schema requires an object. Retrieved 404 statements establish status only; they do not independently establish whether an error body is required.')
row(47,'SPEC','S-REQ-LOOSE','',2,False,'supports_impl_behavior',[('registration',47),('registration',59),('registrationvalidator',60),('externaltest',540),('externaltest',558),('architecture',184),('architecture',186)],
    'The documented request needs key and keyType; independent null-value tests expect 400. ⚠️ Omission reaches the same null-field validation branch, so the contract’s absent required list is too loose.','E-CODE-INTENT;E-DOC;E-TEST')
row(48,'UNDECIDABLE','NA','S-RESP-MISSING',2,True,'none_found',[('user',59),('usermodel',141),('app',226),('usertest',114)],
    'The created user omits email_address under non-null serialization. Name-only success tests do not assert email absence or presence; no independent evidence settles the tightened response-field obligation.')
row(49,'IMPL','I-CRASH','',3,True,'not_applicable',[('contacts',50),('contactdto',13),('resthandler',37)],
    'The request schema permits _links:[] but parsing fails and the catch-all handler returns 500. Under §10.6 the incompatible links structure and conversion into server failure justify the additional spec-defect flag.','E-CODE-INTENT;E-CONV')
row(50,'TEST','NA','T-ORACLE-COVERAGE',3,False,'not_applicable',[('internaltan',143),('checker',359),('checker',360),('checker',467)],
    'The checker explicitly cannot validate object-valued header serialization. This item measures oracle coverage; successful teleTAN generation or unrelated status assertions do not establish header-schema conformance.','E-AUX;E-CODE-INTENT')

# These operations have neither a retained operationId nor a source route
# annotation. The missing runtime OpenAPI routing file leaves a real gap.
for n in [23,33,39]:
    DATA[n].update(L1='DEFERRED',confidence=1,both_candidate=False,
        intent_review_verdict='not_applicable',
        rationale='The operation is absent from the contract and a plausible handler exists, but its runtime route mapping is unavailable. The tool aborts before retrieval; manual inspection cannot resolve the route, requiring deferral under §11.4.')
for n in [3,4,15,19,20,30,38,43]:
    DATA[n]['rationale']='⚠️ '+DATA[n]['rationale']

SPECIAL_POINTERS = {
 1:'/responses/400',2:'/parameters/0/schema/properties/_links/type',
 3:'/parameters/0/required',4:'/parameters/3/maxLength',5:'/parameters/0/schema',
 6:'/parameters/1/required',7:'/parameters/0/maxLength',
 8:'/requestBody/content/application~1json/schema/required',9:'/parameters/1/schema',
 12:'/responses/200/content/application~1json/schema/required',13:'/parameters/0/schema',
 14:'/requestBody/content/application~1json/schema/properties/category/properties/name/maxLength',
 15:'/responses/200/schema/properties/_links/additionalProperties',18:'/responses/406',
 19:'/parameters/0/required',20:'/parameters/0/maxLength',21:'/responses/500',
 22:'/responses/200/content/application~1json/schema/required',
 24:'/responses/200/schema/properties/properties_revisions/items/required',
 25:'/parameters/1/schema',26:'/requestBody/content/application~1x-www-form-urlencoded',
 27:'/responses/200/schema/properties/properties/required',28:'/parameters/1/schema',
 31:'/responses/200/schema/items/additionalProperties',
 32:'/requestBody/content/application~1json/schema/minItems',
 34:'/requestBody/content/application~1x-www-form-urlencoded',
 35:'/responses/200/content/application~1json/schema/items',
 36:'/responses/200/content/application~1json/schema/required',
 37:'/requestBody/content/application~1json/schema',38:'/parameters/2/required',
 40:'/parameters/1/type',41:'/responses/404',42:'/parameters/0/required',44:'/responses/406',
 45:'/responses/200/schema/items/required',46:'/responses/404/content/*~1*/schema',
 47:'/requestBody/content/application~1json/schema',48:'/responses/200/schema/required',
 49:'/parameters/0/schema',50:'/parameters/0/schema',
}

LOGS = {5:('K01/r1/compose.log',230674),13:('K01/r1/compose.log',230674),
        9:('K01/r1/compose.log',92852),25:('K01/r1/compose.log',63874),16:('K01/r1/compose.log',84371)}

def checklist(a,b,c,d=True,explanation=''):
    return {'a_explicit_behavior':a,'b_target_scenario_linkage':b,
            'c_independent_basis':c,'d_applicable_revision':d,'e_opposing_evidence_reviewed':True,
            'explanation':explanation}

def manual(category, locator, disposition, proposition, support=None, inference=False):
    accepted=disposition=='accept'
    return {'category':category,'locator':locator,'disposition':disposition,'proposition':proposition,
        'support':support,'inference':inference,
        'checklist':checklist(accepted,accepted,accepted,explanation=proposition)}

MANUAL = collections.defaultdict(list)
def add(n,category,alias,line,disposition,proposition,support=None,inference=False):
    MANUAL[n].append(manual(category,loc(alias,line),disposition,proposition,support,inference))

# Explicit manual additions are separate from lexical hits, including misses.
for n in [3,20]:
    add(n,'E-DOC','restdoc',133,'accept','Whole DELETE cart interface row, lines 133–135, specifies clearing for the authenticated customer without a name filter. Its /cart shorthand is linked to the current customer/cart class mapping, not to an unrelated operation.','supports_impl_behavior',True)
    add(n,'E-TEST','carttest',229,'context','Service test calls clearCart(email), asserts empty at 232; this verifies linked business behavior but is not by itself an HTTP query-parameter assertion.')
    add(n,'HANDLER','cart',38,'context','Class mapping customer/cart and method clearCart at 87 resolve the documentation shorthand; Principal supplies the account identity.')
add(4,'E-TEST','usertest',82,'accept','GET users with attrs=id,identities has HTTP_OK assertion at 86; inherited AbstractResource.okResponse invokes the same toJson filter used by CategoryResource, so the shared attrs length policy is directly linked.','supports_impl_behavior',True)
add(4,'HANDLER','abstract',55,'context','Comma splitting is shared with CategoryResource via TagResource.all and AbstractResource.okResponse at 67–72; this is linkage, not independent intent.')
for n in [5,13]:
    add(n,'HANDLER','tagmodel',37,'context','Group and name have persistent @Basic(optional=false), lines 37–42. Together with the captured NOT NULL failure this invokes deterministic §10.6, not an inference from an absent test.')
for n in [10,16,17]:
    add(n,'HANDLER','integration',57,'context','createRequest helpers at 44–63 add /api/ and default v1, resolving the test route precisely.')
add(10,'E-TEST','mediatest',165,'accept','GET media_files/id asserts HTTP_OK at 167, called by CRUD test at 89–99. This independently establishes route existence, not overflow-id response intent.','supports_impl_behavior')
add(16,'E-TEST','mediatest',133,'accept','Upload/download test GETs media_files/{id}/file, asserts 200 at 134 and downloaded bytes at 137. This proves the omitted operation, while the 500 is separately decisive.','supports_impl_behavior')
add(17,'E-TEST','systemtest',34,'accept','GET system/ping explicitly asserts HTTP_NO_CONTENT at 36, with helper prefix resolved.','supports_impl_behavior')
add(11,'E-DOC','restdoc',126,'accept','Whole PUT cart row, lines 126–130, documents adding a product. Class mapping at CartRestController:38 resolves the /cart shorthand; parse-error 500 is separately evaluated by R1.','supports_impl_behavior',True)
for n in [15]:
    add(n,'E-CONSIST','cart',125,'accept','Separate CartRestController adds named Customer contacts and Proceed to payment relations at 125–126 to CartDTO, a RepresentationModel at CartDTO:12. This independently establishes dynamic relation keys in the shared HAL DTO policy.','supports_impl_behavior',True)
    add(n,'E-CONSIST','products',64,'accept','Separate ProductsRestController attaches an All products relation to ProductDTO, another RepresentationModel. It corroborates dynamic relation keys rather than the closed schema’s empty-only object.','supports_impl_behavior',True)
    add(n,'HANDLER','contactdto',13,'context','ContactsDTO extends the same RepresentationModel family; ContactsRestController:59 supplies the particular Shopping cart relation. Neither the single label nor status 200 is independent evidence by itself.')
for n in [18,44]:
    add(n,'E-CONSIST','resthandler',74,'accept','Active REST MethodArgumentNotValidException handler returns 406; a separate SpringExceptionHandler:67 applies the same validation-status policy. Current REST guide independently corroborates the branch, avoiding reliance on same-class repetition.','supports_impl_behavior')
add(18,'E-DOC','restdoc',146,'accept','Whole payment interface row, lines 143–147, promises 406 for invalid card format or empty cart; @Valid CreditCardDTO at CartRestController:113 links the missing-card-number scenario.','supports_impl_behavior',True)
add(19,'E-DOC','restdoc',195,'accept','Whole GET /customer/orders row at 195–197 is the REST interface, listing orders for the authenticated customer with no name query requirement. The REST handler at OrdersRestController:40 supplies the exact linkage.','supports_impl_behavior',True)
for n in [23,33,39]:
    add(n,'HANDLER','inflector',1,'context','Controller/model package conventions, the uniquely matching handler and observed response permit manual candidate linkage. The runtime swaggerUrl file is absent from the source snapshot; routing is inferred, not independently established intent.')
    add(n,'E-TEST','pettest',3,'reject','The sole packaged test class is empty. Absence of assertions is not evidence that the public route is intended.')
    add(n,'E-DOC','petreadme',8,'reject','README’s complete overview and usage paragraphs are generic sample instructions, without this operation’s public contract.')
for n in [6,8,12,14,22,24,27,28,32,35,36,42,46,48]:
    if n in [6,8,12,14,22,32,35,36,42]:
        add(n,'E-TEST','pettest',3,'reject','Empty test class has no scenario assertion; no independent intent is inferred from that absence.')
        add(n,'E-DOC','petreadme',8,'reject','Whole README overview and usage instructions do not specify this field, constraint or rejection scenario.')
for n in [24,27]:
    add(n,'HANDLER','app',226,'context','Global NON_NULL serialization explains omission but is not independent confirmation of the target response obligation.')
    add(n,'E-TEST','integration',71,'reject','Helper creates fixture-backed activities and asserts success only; it does not assert omission/presence of the target field after an empty request.')
add(28,'E-TEST','tagtest',54,'reject','Resolved helper is GET v2/tags; the other nearby helpers create/read/delete normal tag fixtures. None tests PUT with unknown JSON properties.')
add(29,'E-TEST','externaltest',200,'accept','Unknown-token TAN test deletes the app-session repository at 199, sends POST /tan with prefix and asserts 400 at 205. TestUtils:51 resolves /version/v1.','supports_impl_behavior')
add(29,'E-DOC','architecture',204,'accept','Whole Create TAN use case, lines 200–222, defines POST /tan and unknown registration-token 400. Class mapping ExternalTanController:51 supplies /version/v1.','supports_impl_behavior')
add(30,'E-DOC','restdoc',121,'accept','Whole GET cart row at 121–123 defines returning the cart. Current class mapping and independent ContactsRestController link resolve the short documented route.','supports_impl_behavior',True)
add(30,'E-CONSIST','contacts',59,'accept','A separate contacts controller publishes a link to CartRestController, corroborating the public cart resource independently of its GET handler.','supports_impl_behavior',True)
for n in [31,45]:
    add(n,'E-DOC','restdoc',37,'accept','Read the complete products-list paragraph and full example, lines 35–37: collection items use a links array and do not use _links. Adjacent individual-product example at 40 uses _links and is a different representation.','supports_impl_behavior')
    add(n,'E-DOC','marketreadme',128,'context','README_RU is explicitly a legacy 2014 description. It is not treated as decisive revision evidence; the bundled current REST guide separately confirms the collection representation.')
add(32,'E-CONSIST','petuser',72,'unresolved','Array and list empty-array guards at 72 and 88 are in the same class. Independence is ambiguous under §11.4; same_class_policy is requested, and neither guard is counted as accepted intent.')
for n in [34,50]:
    add(n,'E-AUX','checker',467,'context','REQUEST_UNCHECKABLE is emitted from problems.uncheckable separately from status and response checks. Attribution is to the stated checker message, not to every issue in the representative exchange.')
add(34,'E-AUX','checker',313,'context','parse_body supports JSON and text; application/x-www-form-urlencoded falls through to unsupported body encoding. Deterministic oracle-coverage decision.')
add(50,'E-AUX','checker',359,'context','Object-valued header schema is explicitly added to unsupported parameter serialization. This does not assert that the parameter is valid or invalid.')
add(37,'E-TEST','externaltest',779,'accept','External-profile test deletes app sessions, then posts a registration token to /version/v1/testresult and explicitly expects 400. The representative uses the same unknown-session branch.','supports_impl_behavior')
add(37,'E-DOC','architecture',175,'accept','Whole Get Test Result use case, lines 168–178, explicitly requires 400 if RegistrationToken does not exist. This is a state precondition, not a JSON-schema missing-field requirement.','supports_impl_behavior')
add(37,'E-TEST','internaltest',325,'reject','Unknown-token 404 belongs to the internal-profile test-state controller. It does not conflict with the external-profile branch exercised by this exchange.')
add(38,'E-TEST','tagtest',54,'accept','Tags-list test sends GET v2/tags without min_activities_count and asserts 200 at 56. CategoryResource:43 directly delegates to that TagResource implementation and TagDao:44 explicitly handles null as no threshold. Cross-version linkage is explicit.','supports_impl_behavior',True)
add(43,'E-DOC','restdoc',138,'accept','Whole row at 138–140 specifies PUT /cart/delivery?included={boolean}. Current class prefix customer/cart and DELIVERY constant resolve the operation; the guide specifies the same false-value scenario.','supports_impl_behavior',True)
add(43,'E-TEST','carttest',214,'context','Linked service test sets included=false and asserts delivery is false at 217. This corroborates business behavior, while the guide supplies the HTTP method and parameter contract.')
add(46,'E-DOC','architecture',251,'reject','Whole Verify TAN use case at 243–254 requires 404 for an absent TAN but does not specify error-body presence or absence. Status-only support cannot settle the target proposition.')
add(46,'HANDLER','verificationhandler',95,'context','ResponseEntity<Void>.build() explains the empty response but belongs to the implementation being evaluated.')
add(46,'E-TEST','internaltest',325,'reject','This is a testresult status assertion, not a TAN-verification body assertion. Directed review of TAN-related tests found no empty-404-body assertion.')
add(47,'E-TEST','externaltest',540,'accept','Null-keyType test asserts 400; the null keyType maps to the same validator condition as an omitted property on the no-argument DTO, whose fields have no defaults. This is a branch-equivalence inference, not a claim that null and omitted are identical JSON.','supports_impl_behavior',True)
add(47,'E-TEST','externaltest',558,'accept','Null-key test asserts 400; omitted key also becomes null on the DTO and reaches RegistrationTokenRequestValidator:60. Confidence is reduced for this explicit mapping inference.','supports_impl_behavior',True)
add(47,'E-DOC','architecture',184,'accept','Whole registration-token use case at 180–198 specifies creation from a hashed GUID or teleTAN and shows key plus keyType as its input. It independently supports the required data obligation.','supports_impl_behavior')
add(47,'HANDLER','testutils',51,'context','PREFIX_API_VERSION=/version/v1 and REGISTRATION_TOKEN_URI=/registrationToken resolve both test requests. TestUtils:122–123 serializes the model without executing any package code during this review.')
add(48,'E-TEST','usertest',114,'reject','Name-only creation success is tested, but the assertions concern id/name/identities, not the presence or absence of serialized email_address.')

def hit_review(n,item,h,index):
    cat=h['category']; f=h['file']; line=h['line']
    result={'index':index,'category':cat,'locator':item['package']+'/source/'+f+':'+str(line)}
    if cat=='HANDLER':
        result.update(disposition='context',reason='Matched implementation behavior/routing only; no independent intent. Any other-module handler match is not treated as target evidence.',checklist=checklist(bool(h.get('statuses') or h.get('route') or h.get('field')),not ('market-web/' in f),False))
    elif cat=='E-DOC' and (f.endswith('.java') or f.endswith('.kt')):
        result.update(disposition='context',reason='Handler Javadoc/API annotation repeats implementation or generated-spec context; no distinct normative basis for this target obligation.',checklist=checklist(False,True,False))
    elif cat=='E-TEST':
        if n==37 and f.endswith('VerificationApplicationExternalTest.java') and line==779:
            result.update(disposition='accept',reason='Same external-profile operation and unknown app-session branch; resolves prefix and repository-empty fixture; expects 400.',support='supports_impl_behavior',checklist=checklist(True,True,True))
        else:
            reason='Assertion is another method/branch, status-only, or lacks the target field/constraint obligation; not decisive for this target proposition.'
            if f.startswith('market-web/'):
                reason='Different MVC module/controller (HTML/admin/customer view), without REST-handler linkage for this proposition. Similar paths, names and status numbers are insufficient.'
            if n in [24,27]:reason='Resolved activity/rating/list/update or fixture-create helper does not assert this field after empty activity creation; success status alone is irrelevant to presence obligation.'
            if n==28:reason='Resolved normal GET/create/delete tag helpers do not exercise unknown properties on the PUT binding-error branch.'
            if n==37 and f.endswith('VerificationApplicationInternalTest.java'):reason='Internal profile/controller or its success branch; representative uses external-profile unknown-session branch. No unresolved conflict remains after profile filtering.'
            result.update(disposition='reject',reason=reason,checklist=checklist(False,False,bool(h.get('independent')),not (n==37 and 'InternalTest' in f)))
    elif cat=='E-DOC':
        accept=False; reason='Incidental field/number, neighboring operation or success branch; no explicit target scenario obligation.'
        if n in [31,45] and f=='market-web/src/main/resources/templates/rest.html' and line==37:
            accept=True;reason='Full products-list example explicitly uses links arrays instead of _links. The adjacent individual-product example is a distinct representation.'
        if n==19 and f=='market-web/src/main/resources/templates/rest.html' and line in [195,197]:
            accept=True;reason='Current REST interface row for GET /customer/orders specifies listing for the authenticated customer without a name query argument; current REST handler supplies exact linkage.'
        if n==44 and f=='market-web/src/main/resources/templates/rest.html' and line in [57,166]:
            accept=True;reason='Complete registration paragraph/interface row explicitly specifies validation-error 406 for this operation.'
        if n==37 and f=='docs/architecture-overview.md' and line==175:
            accept=True;reason='Get Test Result use-case step explicitly requires HTTP 400 for an unregistered token; exact state branch.'
        if n==47 and f=='docs/architecture-overview.md' and line==186:
            accept=True;reason='Read complete registration-token use case: normative request includes key and keyType and requires one source value to generate a token; absent required-list is inconsistent.'
        if f=='README_RU.md':reason='Explicitly legacy documentation per README.adoc:128; neighboring examples/statuses do not establish this exact current target. Current rest.html is reviewed separately.'
        if f=='README.md' and item['package']=='K04':reason='Entire README paragraph is generic sample/build/deployment documentation, not the target route/constraint/response-field obligation.'
        if 'underscore-min.map' in f:reason='Bundled third-party source map containing incidental names, not API normative documentation.'
        if n==46:reason='Body word or status in unrelated prose, threat table, or target status statement; no independent obligation concerning an empty 404 body.'
        result.update(disposition='accept' if accept else 'reject',reason=reason,checklist=checklist(accept,accept,True,not(f=='README_RU.md')))
        if accept:result['support']='supports_impl_behavior'
    elif cat=='E-CONSIST':
        accept=n in [18,44] and (f.endswith('/RestExceptionHandler.java') or f.endswith('/SpringExceptionHandler.java'))
        result.update(disposition='accept' if accept else 'reject',reason='Separate classes consistently implement validation 406, corroborated by target-scenario prose.' if accept else 'Different status/error operation or success case; does not independently establish the target field/header obligation.',checklist=checklist(accept,accept,True))
        if accept:result['support']='supports_impl_behavior'
    else:
        result.update(disposition='reject',reason='No usable local history is supplied; no independent target evidence.',checklist=checklist(False,False,False,False))
    return result

def spec_locator(n,item):
    base=operation_pointer(item)
    return item['package']+'/spec.json#'+base+SPECIAL_POINTERS.get(n,'')

def decode_pointer(document,pointer):
    node=document
    for key in pointer.lstrip('/').split('/'):
        key=key.replace('~1','/').replace('~0','~')
        node=node[int(key)] if isinstance(node,list) else node[key]
    return node

def finalize():
    rows=[]
    for item in ITEMS:
        iid=item['item_id'];n=int(iid[1:]);d=DATA[n]
        reviewfile=ROOT/'review_F2'/f'{iid}.json'
        review=json.loads(reviewfile.read_text())
        rawbytes=(ROOT/'search_F2'/f'{iid}.json').read_bytes()
        code=int((ROOT/'search_F2'/f'{iid}.exitcode').read_text())
        try:raw=json.loads(rawbytes)
        except json.JSONDecodeError:raw=None
        review['target_proposition']['item_kind']=item['kind']
        review['target_proposition']['violation_pointer']=item['pointer']
        review['target_proposition']['spec_obligation']=item['message'] or ('operation must be declared' if item['kind']=='UNDOCUMENTED_OPERATION' else 'document observed status' if item['kind']=='UNDOCUMENTED_STATUS' else 'avoid non-gateway server failure' if item['kind']=='SERVER_ERROR' else 'successful result for schema-valid input')
        review['target_proposition']['inference_note']='Target is this item’s named violation component; additional observed defects are explicitly recorded separately.'
        review['hits']=[hit_review(n,item,h,i) for i,h in enumerate(raw['hits'])] if raw else []
        review['manual_additions']=MANUAL[n]
        if n in [23,33,39]:
            review['manual_additions'].append(manual('HANDLER',loc('inflector',3),'unresolved',
                'swaggerUrl points at webapp/openapi.yaml, which is absent from the supplied source; the deleted operation lacks an operationId in spec.json. The matching method name/response is only a hypothesis for routing. Gap remains; do not convert tool failure into none_found.'))
        review['review_order']=['HANDLER','E-TEST','E-DOC','E-CONSIST','E-HISTORY']
        review['history_scope']='unavailable'
        review['raw_tool_verdict']=raw['independent_evidence'] if raw else 'NA'
        review['tool_coverage']={'exit_code':code,'scan':raw.get('scan') if raw else None,'warnings':raw.get('warnings') if raw else [],
            'stderr_file':'search_F2/'+iid+'.stderr','raw_stdout_file':'search_F2/'+iid+'.json',
            'manual_gap_resolution':'Incomplete: missing-operation precondition failed and source runtime mapping is absent. Candidate handler cannot be conclusively linked to the deleted route.' if n in [23,33,39] else 'Missing-operation tool precondition failed. Manually inspected handler routes, tests and documentation; annotated paths/constants or explicitly resolved helpers close the retrieval gap. No outside routing/history source was opened.' if not raw else 'Raw scan completed. Directed manual fallback reviewed linked helpers/fixtures, full relevant prose, and independent class policy; no relevant unreadable file remained.'}
        if not raw:
            review['manual_coverage']={
                'handler_locators':[loc(a,l) for a,l in d['refs'] if '/src/main/' in ALIASES[a]],
                'test_scope': 'K04/source/src/test/java/ip/swagger/petstore/PetStoreTest.java (empty)' if item['package']=='K04' else 'K01/source/api/src/test/java/se/devscout/scoutapi; IntegrationTest helper' if item['package']=='K01' else 'K03/source/src/test/java/app/coronawarn/verification; TestUtils route constants' if item['package']=='K03' else 'K02/source/market-core/src/test/java; K02/source/market-web/src/test/java (separate MVC module, not counted as REST route assertions)',
                'doc_scope':'K04/source/README.md; K04/source/inflector.yaml (context)' if item['package']=='K04' else 'K01/source/api/src/main/resources/assets/docs/README.md (generic bundled UI documentation)' if item['package']=='K01' else 'K03/source/docs/architecture-overview.md' if item['package']=='K03' else 'K02/source/market-web/src/main/resources/templates/rest.html; K02/source/README.adoc; README_RU.md marked legacy',
                'status':'incomplete; runtime route mapping unavailable' if n in [23,33,39] else 'manually completed; no claim that failed tool returned none_found'}
        evidence=[loc(a,l) for a,l in d['refs']]
        evidence.append(spec_locator(n,item))
        extra_spec={
            2:'/paths/~1register/post/parameters/0/schema/properties/_links/type',
            5:'/definitions/Tag/required',13:'/definitions/Tag/required',
            21:'/paths/~1customer~1orders~1{orderId}/get/parameters/1/type',
            35:'/components/schemas/Pet/required',
            47:'/components/schemas/RegistrationTokenRequest/required',
            49:'/definitions/ContactsDTOReq/properties/_links/type',
        }.get(n)
        if extra_spec:evidence.append(item['package']+'/spec.json#'+extra_spec)
        evidence.append(item['package']+'/r1/exchanges.jsonl:'+str(int(item['example_exchange'])+1))
        if n in LOGS:evidence.append(LOGS[n][0]+':'+str(LOGS[n][1]))
        evidence.extend(['search_F2/'+iid+'.json','review_F2/'+iid+'.json'])
        secondary={2:'S-STRUCT: _links request type conflicts with parser',5:'S-REQ-LOOSE: missing persistent required fields',11:'S-METHOD: independently documented PUT route omitted',13:'S-REQ-LOOSE: missing persistent required fields',16:'S-METHOD: independently tested download route omitted',49:'S-STRUCT: _links request type conflicts with parser'}.get(n)
        review['decision']={k:d[k] for k in ['L1','L2','proposed_L2','confidence','both_candidate','intent_review_verdict','adjudication_flag','rationale']}
        review['decision']['evidence_locators']=evidence
        review['decision']['secondary_defect']=secondary
        review['decision']['intent_verdict_scope']='The independently evidenced public operation only; the observed 500 remains an IMPL fault under R1, and no intent evidence excuses that 500.' if n in [11,16] else 'The stated target component; raw status-only support is never used for a field or serialization obligation.'
        review['decision']['both_candidate_meaning']='Independently evidenced second defect' if secondary else 'Unresolved attribution under §11; not proof that both sides are defective' if d['both_candidate'] else 'No additional both-side candidate established'
        review['decision']['scope_note']='Only REQUEST_UNCHECKABLE is attributed here. A 500 in the exchange remains an implementation fault under R1, separately from this checker-capability message.' if n==34 else 'One item, one named violation; no aggregation with unrelated exchange messages.'
        review['end_time']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        reviewfile.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
        rows.append({'item_id':iid,**{k:d[k] for k in ['L1','L2','proposed_L2','confidence','evidence_types']},
            'evidence_locators':';'.join(evidence),'both_candidate':str(d['both_candidate']).lower(),
            'intent_search_status':'incomplete' if n in [23,33,39] else 'complete','intent_search_verdict':review['raw_tool_verdict'],
            'intent_review_verdict':d['intent_review_verdict'],'adjudication_flag':d['adjudication_flag'],
            'history_scope':'unavailable','rationale':d['rationale']})
    headers='item_id,L1,L2,proposed_L2,confidence,evidence_types,evidence_locators,both_candidate,intent_search_status,intent_search_verdict,intent_review_verdict,adjudication_flag,history_scope,rationale'.split(',')
    with (ROOT/'labels_F2.csv').open('w',newline='') as out:
        w=csv.DictWriter(out,fieldnames=headers);w.writeheader();w.writerows(rows)
    summary={'rows':len(rows),'distribution':dict(collections.Counter(r['L1'] for r in rows)),
        'both_candidate':sum(r['both_candidate']=='true' for r in rows),
        'raw_verdicts':dict(collections.Counter(r['intent_search_verdict'] for r in rows)),
        'exit_codes':dict(collections.Counter(int((ROOT/'search_F2'/f"{r['item_id']}.exitcode").read_text()) for r in rows)),
        'reviewed_hits':sum(len(json.loads((ROOT/'review_F2'/f"{r['item_id']}.json").read_text())['hits']) for r in rows)}
    (ROOT/'review_F2'/'summary_F2.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':finalize()
