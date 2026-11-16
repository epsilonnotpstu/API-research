"""Private CORS request body processing evidence; first three spec operations fill cap."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
for operation,x in [
 ('POST /consumers/{groupid}','the JSON request body supplies consumer name and supported configuration options'),
 ('POST /consumers/{groupid}/instances/{name}/positions/beginning','the JSON request body supplies the topic partitions to seek to their beginning'),
 ('POST /consumers/{groupid}/instances/{name}/positions/end','the JSON request body supplies the topic partitions to seek to their end')]:
 R['accept']('strimzi-kafka-bridge',45,operation,x,
  'install a CORS global handler without a body handler when CORS is enabled, leaving those JSON request-body values unprocessed',
  'IMPL','spec_file','request_body.cors_body_handler_missing',
  [('src/main/resources/openapi.json',r'"'+operation.split(' ',1)[1].replace('{',r'\{').replace('}',r'\}')+r'"|requestBody|Consumer|partitions')],
  [('http/HttpBridge.java',r'isCorsEnabled|rootHandler\(getCorsHandler|routerBuilder.createRouter|routingContext.body\(\)|getString\("format"'),
   ('http/HttpSinkBridgeEndpoint.java',r'bodyAsJson.getString\("name"|bodyAsJson.getJsonArray\("partitions"|routingContext.body\(\)')],confidence=2)
R['decide']('strimzi-kafka-bridge',45,'ACCEPT','Three request-body operations lose body processing under the parent CORS global handler; the patch adds the required handler, filling the repository cap.')
print('New accepted items:',len(R['accepted']()))
