from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).parents[1]/'review_t49.py'))
contract=[('openapi/ditto-api-2.yml',r'^    ConnectionStatus:|^    ConnectivityStatus:|^    Connection:|^    NewConnection:'),('schemas/connections/newConnection.yml',r'connectionStatus:|connectionStatus.yml'),('schemas/connections/connectionStatus.yml',r'^type: object')]
for op in ['GET /connections','GET /connections/{connectionId}','POST /connections','PUT /connections/{connectionId}']:
 response=op.startswith('GET')
 impl=[('connectivity/model/ImmutableConnection.java',r'getConnectionStatusOrThrow|ConnectivityStatus.forName|JsonFields.CONNECTION_STATUS, connectionStatus.getName')]
 if op=='GET /connections':impl+=[('commands/query/RetrieveConnectionsResponse.java',r'connection.toJson|return connections;')]
 elif response:impl+=[('commands/RetrieveConnectionStrategy.java',r'RetrieveConnectionResponse.of\(entity.toJson')]
 else:impl+=[('connectivity/model/ConnectivityModelFactory.java',r'ImmutableConnection.fromJson')]
 R['accept']('ditto',317,op,
  'connectionStatus is an object through the ConnectionStatus schema reference',
  'serialize connectionStatus as a string enum' if response else 'parse connectionStatus as a string enum using ConnectivityStatus.forName',
  'SPEC','openapi','schema.connection-status-object-versus-string',contract,impl,
  route=[('routes/connections/ConnectionsRoute.java',r'GET /connections|POST /connections|PUT /connections|connectionFromJson')],
  helpers=['commands/query/RetrieveConnectionResponse.java'] if op=='GET /connections/{connectionId}' else [])
print('Accepted/capped:',R['finish_accept']('Parent connectionStatus schema resolves to an object; model reads and writes string enums; patch selects ConnectivityStatus.'))
