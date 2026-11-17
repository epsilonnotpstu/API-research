import runpy
R=runpy.run_path('08_experiments/E7_mining/review_t50b.py')
base='rest/admin-v2/'
for method,path,api,handler in [
 ('PATCH','/admin/api/v2/realms/{name}/clients/{id}','ClientApi.java','DefaultClientApi.java'),
 ('POST','/admin/api/v2/realms/{name}/clients','ClientsApi.java','DefaultClientsApi.java'),
 ('PUT','/admin/api/v2/realms/{name}/clients/{id}','ClientApi.java','DefaultClientApi.java')]:
 R['accept']('keycloak',41,method+' '+path,
  'displayName, appUrl and appRedirectUrls carry the client name, application homepage and redirect URLs',
  'the DTO-to-model mapper has no mappings from those renamed fields to name, baseUrl and redirectUris, so submitted values are not transferred',
  'IMPL','jvm_annotation','request.client_aliased_field_mapping',confidence=2,
  contract=[(base+'api/src/main/java/org/keycloak/representations/admin/v2/ClientRepresentation.java',r'Human readable name|application.s homepage|URLs that the browser'),
   (base+'rest/src/main/java/org/keycloak/admin/api/client/'+api,r'@'+method),
   (base+'rest/src/main/java/org/keycloak/admin/api/AdminRootV2.java',r'@Path'),
   (base+'rest/src/main/java/org/keycloak/admin/api/AdminApi.java',r'@Path'),
   (base+'rest/src/main/java/org/keycloak/admin/api/realm/RealmsApi.java',r'@Path'),
   (base+'rest/src/main/java/org/keycloak/admin/api/realm/RealmApi.java',r'@Path')],
  implementation=[(base+'api/src/main/java/org/keycloak/models/mapper/MapStructClientModelMapper.java',r'void toModel|target = "displayName"|target = "appUrl"|target = "appRedirectUrls"'),
   (base+'api/src/main/java/org/keycloak/models/mapper/MapStructModelMapper.java',r'Mappers.getMapper'),
   (base+'api/src/main/java/org/keycloak/services/client/DefaultClientService.java',r'mapper.toModel|new MapStructModelMapper'),
   ('server-spi/src/main/java/org/keycloak/models/ClientModel.java',r'void setName|void setBaseUrl|void setRedirectUris'),
   (base+'rest/src/main/java/org/keycloak/admin/api/client/'+handler,r'clientService.createOrUpdate')])
print('Accepted items and exclusions:',R['finish_accept']('Client DTO fields describe stored identity and URLs, but reverse mapper omits their renamed bindings; the patch supplies explicit DTO-to-model mappings.'))
