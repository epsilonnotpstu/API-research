"""Private binary-record input representation evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
for suffix in ['', '/partitions/{partitionid}']:
 R['accept']('strimzi-kafka-bridge',44,'POST /topics/{topicname}'+suffix,
  'binary record keys and values use base64-encoded strings and invalid records return 422',
  'coerce object or array keys and values through JsonNode.asText before base64 decoding, admitting empty-byte records instead of rejecting their representation',
  'IMPL','spec_file','request_validation.binary_record_nonstring_representation',
  [('src/main/resources/openapi.json',r'"/topics/\{topicname\}'+suffix.replace('{',r'\{').replace('}',r'\}')+r'"|base64-encoded binary|The record.*not valid')],
  [('converter/HttpBinaryMessageConverter.java',r'Base64.getDecoder\(\).decode\(json.get\("(?:key|value)"\).asText\(\)\)'),
   ('http/HttpSourceBridgeEndpoint.java',r'catch \(Exception e\)|UNPROCESSABLE_ENTITY|toKafkaRecord')],confidence=2)
R['decide']('strimzi-kafka-bridge',44,'ACCEPT','Both producer operations require valid binary representations, but parent conversion coerces objects to empty strings; the patch rejects non-text nodes before base64 decoding.')
print('New accepted items:',len(R['accepted']()))
