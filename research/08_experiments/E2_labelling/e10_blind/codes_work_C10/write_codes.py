from pathlib import Path
import csv

rows=[]
def loc(item, side, name, line):
    base=Path(item)/side
    matches=list(base.rglob(name))
    assert len(matches)==1, (item,side,name,matches)
    p=matches[0]
    assert 1 <= line <= len(p.read_text().splitlines())
    return f'{p}{":" if side=="impl" else "#"}{line}'
def add(n,kind,specificity,confidence,impl,contract,rationale):
    item=f'V{n:02d}'
    assert len(rationale.split())<=40, (item,len(rationale.split()))
    rows.append(dict(item_id=item,divergence_kind=kind,contract_specificity=specificity,confidence=confidence,
        impl_locators=';'.join(loc(item,'impl',name,line) for name,line in impl),
        contract_locators=';'.join(loc(item,'contract',name,line) for name,line in contract),rationale=rationale))

add(1,'ACCIDENTAL','SPECIFIC',2,
 [('HttpBinaryMessageConverter.java',48),('HttpBinaryMessageConverter.java',51),('HttpSourceBridgeEndpoint.java',140)],
 [('openapi.json',2257),('openapi.json',2276),('openapi.json',1165)],
 '⚠️ missing textual-node validation lets asText coercion reach base64 decoding; no branch targets object/array acceptance. Contract explicitly describes binary strings and an invalid-record 422 response.')
add(2,'DELIBERATE','GENERIC',3,
 [('KapuaMethod.java',101),('KapuaMethod.java',144),('DeviceEventImpl.java',196),('DeviceEvent.java',152),('DeviceEvents.java',195)],
 [('deviceEvent.yaml',44),('deviceEvent-scopeId-deviceId-deviceEventId.yaml',31)],
 'SUBMIT is explicitly declared and preserved by normalizeAction, then exposed as action. The supplied contract only declares action as string; the proposition’s claimed six-value enum is absent.')
add(3,'ACCIDENTAL','SPECIFIC',3,
 [('handler.go',161),('handler.go',216),('handler.go',262)],
 [('api.json',420),('api.json',422)],
 'The manual query lookup omits the documented preview prefix, although its annotation retains it. This inconsistent parameter name leaves the preview filter unused; the contract explicitly describes similarity search.')
add(4,'ACCIDENTAL','SPECIFIC',2,
 [('strategy_recovery_admin.go',145),('strategy_recovery_admin.go',157),('strategy_recovery_admin.go',160),('strategy_recovery_admin.go',165)],
 [('api.json',7),('api.json',9)],
 '⚠️ ParseDuration accepts fractional segments, while decoding lacks the dedicated pattern check. The error text still expects integer-unit syntax, supporting omitted validation rather than a targeted fractional-duration policy.')
add(5,'DELIBERATE','SPECIFIC',3,
 [('DataMessagesJson.java',209),('DataMessagesJson.java',217),('DataMessagesJson.java',219)],
 [('dataMessage-scopeId-datastoreMessageId.yaml',25),('dataMessage-scopeId-datastoreMessageId.yaml',30)],
 'The JSON handler explicitly constructs and returns one JsonDatastoreMessage. The operation explicitly assigns dataMessageListResult to its 200 JSON response, despite describing a single requested message.')
add(6,'DELIBERATE','SPECIFIC',3,
 [('TppBankingApiPisInfoController.java',74),('Xs2aGetPaymentStatusEntrypoint.java',53),('GlobalConst.java',53)],
 [('tpp_banking_api_pis.yml',90),('tpp_banking_api_pis.yml',96)],
 'The outgoing status call explicitly supplies PAYMENT_PRODUCT_SEPA, documented in code as the default product; the request builder never forwards paymentProduct. The operation requires the PaymentProduct path parameter with enumerated alternatives.')
add(7,'DELIBERATE','GENERIC',3,
 [('DeviceEvents.java',77),('KapuaMethod.java',101),('KapuaMethod.java',144),('DeviceEventImpl.java',196),('DeviceEvent.java',152)],
 [('deviceEvent.yaml',44),('deviceEvent-scopeId-deviceId.yaml',52)],
 'SUBMIT is a declared model value preserved by the explicit normalization default and exposed as action. The contract’s shared deviceEvent schema says string only; the claimed enum restriction is absent.')
add(8,'ACCIDENTAL','SPECIFIC',3,
 [('HttpSinkBridgeEndpoint.java',375),('HttpSinkBridgeEndpoint.java',404),('SinkBridgeEndpoint.java',185)],
 [('openapi.json',335)],
 'The 409 guard checks only simultaneous body fields; subscription proceeds without an existing-assignment check. This is omitted state validation. The operation explicitly promises mutual exclusivity with partitions.')
add(9,'ACCIDENTAL','SPECIFIC',2,
 [('IdsResourceImpl.java',89),('AbstractResourceImpl.java',72),('AbstractResourceImpl.java',83),('AbstractResourceImpl.java',131)],
 [('openapi.json',4581),('openapi.json',611),('openapi.json',638)],
 '⚠️ the URL template omits /content despite comments targeting content URLs. The contract describes registry-valid rewritten references and identifies the generated destination as version metadata; the content suffix omission explains Y.')
add(10,'DELIBERATE','SPECIFIC',3,
 [('TppBankingApiPisInfoController.java',48),('Xs2aGetPaymentInfoEntrypoint.java',53),('GlobalConst.java',53)],
 [('tpp_banking_api_pis.yml',63),('tpp_banking_api_pis.yml',96)],
 'The information call explicitly supplies the documented default PAYMENT_PRODUCT_SEPA constant; its request builder drops paymentProduct. The GET operation requires the PaymentProduct path parameter and lists alternative products.')
add(11,'DELIBERATE','SPECIFIC',3,
 [('TppBankSearchController.java',42),('TppBankSearchController.java',44)],
 [('tpp_banking_api_bank_search.yml',45),('tpp_banking_api_bank_search.yml',83)],
 'An explicit banks.isEmpty branch constructs a bodyless NOT_FOUND response. The operation explicitly declares a 200 bank-search result; it does not separately specify empty-result behavior.')
add(12,'ACCIDENTAL','SPECIFIC',2,
 [('strategy_recovery.go',155),('strategy_recovery.go',163),('strategy_recovery.go',165),('strategy_recovery.go',170)],
 [('api.json',7),('api.json',9)],
 '⚠️ compound and fractional acceptance follows ParseDuration without enforcing the single-segment pattern. Error text still expects integer-unit syntax, supporting omitted validation. The request schema explicitly anchors exactly one segment.')
add(13,'DELIBERATE','GENERIC',3,
 [('SubscriptionsExceptionMapper.java',42),('DefaultExceptionMapper.java',65)],
 [('openapi.yaml',316),('openapi.yaml',1251),('openapi.yaml',1904)],
 'Exception mappers explicitly place a single Error in the response entity. The required errors array comes from the shared Errors envelope through the reusable default ErrorResponse, rather than an operation-specific error-shape statement.')
add(14,'ACCIDENTAL','SPECIFIC',3,
 [('AuthSessionService.java',84),('GlobalExceptionHandler.java',143)],
 [('security-openapi.yaml',280)],
 'An unknown session throws IllegalArgumentException; no matching 404 mapping exists in the supplied advice, so the catch-all returns 500. The dedicated Session not found 404 response is explicit; the mismatch is exception classification.')
add(15,'DELIBERATE','GENERIC',3,
 [('ContractsExceptionMapper.java',44),('DefaultExceptionMapper.java',65)],
 [('openapi.yaml',119),('openapi.yaml',1251),('openapi.yaml',1904)],
 'The mappers explicitly serialize new Error as the response entity. Contract wrapping in a required errors array is inherited from the shared default ErrorResponse and Errors schema.')
add(16,'DELIBERATE','GENERIC',3,
 [('strategy_login.go',188),('handler.go',219),('attributes.go',87)],
 [('api.json',718)],
 'Identifier-first population explicitly assigns username webauthn to the input autocomplete attribute. The six-value restriction is inherited from the shared generated uiNodeInputAttributes schema rather than a native-login-specific requirement.')
add(17,'DELIBERATE','GENERIC',3,
 [('SubscriptionsExceptionMapper.java',42),('DefaultExceptionMapper.java',65)],
 [('openapi.yaml',339),('openapi.yaml',1251),('openapi.yaml',1904)],
 'Mapped exceptions explicitly use one Error entity. The errors-array obligation is supplied by the common Errors schema referenced through this operation’s reusable default ErrorResponse.')
add(18,'DELIBERATE','GENERIC',3,
 [('DeviceKeystore.java',39),('DeviceKeystoreImpl.java',37),('DeviceManagementKeystores.java',69)],
 [('deviceKeystore.yaml',18),('deviceKeystore-scopeId-deviceId.yaml',31)],
 'The model explicitly annotates its identifier as id and returns getId. Contract name comes from the referenced shared deviceKeystore schema and its examples, without an operation-specific naming statement.')
add(19,'ACCIDENTAL','SPECIFIC',2,
 [('HttpBridge.java',168),('HttpBridge.java',286),('HttpSinkBridgeEndpoint.java',95),('HttpSinkBridgeEndpoint.java',120)],
 [('openapi.json',14),('openapi.json',17)],
 '⚠️ CORS installs a root handler without a body handler; downstream code expects parsed JSON. Body loss follows an unaddressed framework default, not an explicit discard policy. RouterBuilder internals are absent; contract body semantics are explicit.')
add(20,'ACCIDENTAL','SPECIFIC',2,
 [('HttpBridge.java',168),('HttpSinkBridgeEndpoint.java',500),('HttpSinkBridgeEndpoint.java',181)],
 [('openapi.json',166),('openapi.json',169)],
 '⚠️ CORS root-handler setup omits body handling while seek-to-end reads parsed partitions. Any resulting body loss is an unaddressed framework default; RouterBuilder internals are absent. The operation explicitly describes body-supplied partitions.')
add(21,'DELIBERATE','GENERIC',2,
 [('helper.go',8),('manager_http.go',94),('handler.go',128)],
 [('swagger.json',1558),('swagger.json',2762)],
 '⚠️ Bearer extraction explicitly reads the Authorization header. The query location appears to be a generator fallback from the invalid in: authorization annotation; contract token prose elsewhere also specifies the header. Generator implementation is absent.')
add(22,'DELIBERATE','GENERIC',3,
 [('DeviceEvents.java',133),('KapuaMethod.java',101),('KapuaMethod.java',144),('DeviceEventImpl.java',196),('DeviceEvent.java',152)],
 [('deviceEvent.yaml',44),('deviceEvent-scopeId-deviceId-_query.yaml',32)],
 'The model declares SUBMIT and preserves it through the normalization default for serialized action. The referenced contract schema only declares string, so the proposition’s six-value enum restriction is unsupported.')
add(23,'DELIBERATE','GENERIC',3,
 [('ContractsExceptionMapper.java',44),('DefaultExceptionMapper.java',65)],
 [('openapi.yaml',469),('openapi.yaml',1251),('openapi.yaml',1904)],
 'Response entities explicitly contain a single Error in the supplied mappers. The required errors-array envelope comes from the common Errors schema and reusable default ErrorResponse.')
add(24,'DELIBERATE','GENERIC',3,
 [('ContractsExceptionMapper.java',44),('DefaultExceptionMapper.java',65)],
 [('openapi.yaml',195),('openapi.yaml',1251),('openapi.yaml',1904)],
 'The mappers explicitly construct Error response entities. The contract’s envelope requirement is inherited through shared ErrorResponse and Errors definitions rather than dedicated sync-contracts error prose.')
add(25,'DELIBERATE','GENERIC',3,
 [('ContractsExceptionMapper.java',44),('DefaultExceptionMapper.java',65)],
 [('openapi.yaml',30),('openapi.yaml',1251),('openapi.yaml',1904)],
 'A single Error is explicitly selected as the mapped response entity. The errors-array envelope is inherited from the referenced common default response and Errors schema.')
add(26,'DELIBERATE','GENERIC',3,
 [('LoginInfo.java',38),('LoginInfo.java',48),('LoginInfo.java',53),('Authentication.java',165)],
 [('authentication.yaml',54),('authentication.yaml',59),('authentication.yaml',64),('authentication-info.yaml',28)],
 'Explicit XmlElement annotations and singular getters select rolePermission, groupPermission and groupRolePermission. The plural property names come from the referenced shared loginInfo model rather than a dedicated operation naming constraint.')
add(27,'DELIBERATE','GENERIC',3,
 [('strategy_login.go',188),('handler.go',219),('handler.go',698)],
 [('api.json',718)],
 'The identifier-first strategy explicitly sets username webauthn, and flow retrieval serializes the stored flow. The autocomplete restriction comes from the shared generated input-node schema, not a flow-retrieval-specific constraint.')
add(28,'ACCIDENTAL','SPECIFIC',2,
 [('PageableProductsProvider.java',31),('PageableProductsProvider.java',46),('GlobalExceptionHandler.java',20),('ProductExceptionHandler.java',22)],
 [('product-openapi.yaml',95)],
 '⚠️ arbitrary sortAttribute reaches repository sorting without a PropertyReferenceException mapping in either supplied advice. Server-error behavior depends on framework handling. The operation explicitly documents 400 for invalid pagination or sorting.')
add(29,'ACCIDENTAL','SPECIFIC',3,
 [('HttpSinkBridgeEndpoint.java',357),('HttpSinkBridgeEndpoint.java',372),('SinkBridgeEndpoint.java',270)],
 [('openapi.json',548)],
 'Assignment proceeds after reading partitions and checks no existing topic subscription. The omitted state guard explains Y; the assignment operation explicitly declares a 409 for mutually exclusive subscription modes.')
add(30,'ACCIDENTAL','SPECIFIC',3,
 [('handler.go',229),('handler.go',230),('provider_viper.go',370),('provider_viper.go',379)],
 [('api.swagger.json',3082),('api.swagger.json',3175)],
 'ClaimsSupported calls the scope provider and ScopesSupported calls the claim provider, whose defaults confirm the reversal. This is swapped data wiring. Dedicated contract prose distinguishes claim names from OAuth scope values.')
add(31,'ACCIDENTAL','SPECIFIC',2,
 [('HttpBridge.java',168),('HttpSinkBridgeEndpoint.java',500),('HttpSinkBridgeEndpoint.java',181)],
 [('openapi.json',102),('openapi.json',105)],
 '⚠️ the CORS root handler lacks body handling while seek-to-beginning expects parsed partitions. Resulting body loss is an unaddressed framework default; RouterBuilder internals are absent. The contract explicitly describes the request partitions.')
add(32,'DELIBERATE','GENERIC',3,
 [('SubscriptionsExceptionMapper.java',42),('DefaultExceptionMapper.java',65)],
 [('openapi.yaml',444),('openapi.yaml',1251),('openapi.yaml',1904)],
 'The exception mappers explicitly choose single Error entities. The required errors-array wrapper is inherited from reusable default ErrorResponse and shared Errors schema definitions.')
add(33,'DELIBERATE','GENERIC',3,
 [('strategy_login.go',188),('handler.go',219),('attributes.go',87)],
 [('api.json',723)],
 'Identifier-first login explicitly populates username webauthn as autocomplete. The contract restriction is inherited from a shared generated input-node enum rather than dedicated browser-login behavior prose.')
add(34,'ACCIDENTAL','SPECIFIC',3,
 [('GroupsResourceImpl.java',875),('GroupsResourceImpl.java',968),('AbstractResourceImpl.java',83),('AbstractResourceImpl.java',131)],
 [('openapi.json',4581),('openapi.json',611),('openapi.json',638)],
 'The rewrite template omits /content even though its comment targets content URLs; the destination operation returns VersionMetaData. This missing suffix explains Y. The contract explicitly describes registry-valid reference rewriting.')
add(35,'ACCIDENTAL','SPECIFIC',2,
 [('HttpBinaryMessageConverter.java',48),('HttpBinaryMessageConverter.java',51),('HttpSourceBridgeEndpoint.java',140)],
 [('openapi.json',2257),('openapi.json',2276),('openapi.json',724)],
 '⚠️ asText coerces container nodes before base64 decoding because binary conversion lacks a textual-node guard. Empty-byte acceptance is incidental to that omission. Contract prose describes binary strings and an invalid-record-list 422 response.')
add(36,'DELIBERATE','GENERIC',3,
 [('ContractsExceptionMapper.java',44),('DefaultExceptionMapper.java',65)],
 [('openapi.yaml',98),('openapi.yaml',1251),('openapi.yaml',1904)],
 'The supplied exception mappers explicitly return one Error object. The errors-array envelope follows the reusable default ErrorResponse and common Errors schema, rather than dedicated GET-contracts error-shape prose.')
add(37,'DELIBERATE','SPECIFIC',3,
 [('login.go',29),('login.go',178)],
 [('api.swagger.json',683)],
 'The route registration explicitly uses POST and the generated form explicitly uses POST. The contract declares GET at this exact path, an operation-specific method statement rather than an absent operation or generic default.')
add(38,'DELIBERATE','GENERIC',3,
 [('ContractsExceptionMapper.java',44),('DefaultExceptionMapper.java',65)],
 [('openapi.yaml',259),('openapi.yaml',1251),('openapi.yaml',1904)],
 'Single Error response entities are explicitly constructed by the mappers. The required errors-array wrapper is inherited from the common Errors model through the reusable default ErrorResponse.')
add(39,'ACCIDENTAL','SPECIFIC',3,
 [('ServiceConfigurations.java',86),('ThrowableMapper.java',37),('KapuaEntityNotFoundExceptionMapper.java',39)],
 [('serviceConfiguration-scopeId.yaml',79)],
 'After account lookup, update dereferences account without checking for null or throwing the mapped entity-not-found exception. ThrowableMapper produces the generic 500. The operation explicitly declares 404 entityNotFound.')
add(40,'DELIBERATE','SPECIFIC',3,
 [('InstancesResource.java',215),('InstancesResource.java',218),('InstancesResource.java',220),('TallyInstanceView.java',83)],
 [('rhsm-subscriptions-api-spec.yaml',1703)],
 'An explicit unit-comparison branch selects the first monthly total only for the key’s unit and explicitly writes zero otherwise. The contract dedicates prose to matching measurement positions with meta.measurements.')

with open('items.csv',newline='') as f: expected=[r['item_id'] for r in csv.DictReader(f)]
assert [r['item_id'] for r in rows]==expected
fields=['item_id','divergence_kind','contract_specificity','confidence','impl_locators','contract_locators','rationale']
with open('codes_C10.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
print('Wrote',len(rows),'rows; all locators resolve and rationales contain at most 40 words.')
