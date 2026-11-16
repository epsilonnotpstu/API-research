from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
contract=[('openapi/ditto-api-2.yml',r'^    ConnectionType:|^        - mqtt$|^  /connections:|^  .*/connections/\{connectionId\}')]
base=[('connectivity/model/ConnectionType.java',r'MQTT_5\("mqtt-5"\)'),('connectivity/model/ImmutableConnection.java',r'ConnectionType.forName|JsonFields.CONNECTION_TYPE, connectionType.getName')]
for operation,response in [('GET /connections',True),('GET /connections/{connectionId}',True),('POST /connections',False),('PUT /connections/{connectionId}',False)]:
 impl=base+([('commands/query/RetrieveConnectionsResponse.java',r'connection.toJson|return connections;')] if operation=='GET /connections' else [('commands/RetrieveConnectionStrategy.java',r'RetrieveConnectionResponse.of\(entity.toJson')] if operation.startswith('GET') else [('connectivity/model/ConnectivityModelFactory.java',r'ImmutableConnection.fromJson')])
 R['accept']('ditto',193,operation,
  'the connectionType enumeration excludes mqtt-5',
  ('serialize stored connections with connectionType mqtt-5' if response else 'parse mqtt-5 as a supported ConnectionType value'),
  'SPEC','openapi','enum.connection-type-mqtt5',contract,impl,
  route=[('routes/connections/ConnectionsRoute.java',r'GET /connections|POST /connections|PUT /connections|RetrieveConnection.newInstance|RetrieveConnections.newInstance')],
  helpers=['commands/query/RetrieveConnectionResponse.java'] if operation=='GET /connections/{connectionId}' else [],confidence=3)
print('Accepted/capped:',R['finish_accept']('Parent connection enum omits mqtt-5 while routes and model support it; resolving OpenAPI patch adds the value.'))
