"""Private parent-state message response evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('kapua',78,'GET /{scopeId}/data/messages/{datastoreMessageId}',
 'the 200 JSON response follows the dataMessageListResult collection schema',
 'return one JsonDatastoreMessage for the requested identifier',
 'SPEC','spec_file','response_body.single_message_not_list',
 [('dataMessage-scopeId-datastoreMessageId.yaml',r'dataMessageListResult|application/json|200:'),
  ('dataMessage/dataMessage.yaml',r'dataMessageListResult:|dataMessage:|items:')],
 [('resources/DataMessagesJson.java',r'public JsonDatastoreMessage findJson|new JsonDatastoreMessage|return DATA_MESSAGES.returnNotNullEntity'),
  ('resources/DataMessages.java',r'public DatastoreMessage find|MESSAGE_STORE_SERVICE.find|return returnNotNullEntity'),
  ('JsonDatastoreMessage.java',r'class JsonDatastoreMessage|public JsonDatastoreMessage')],
 [('resources/DataMessagesJson.java',r'@Path\("\{scopeId\}/data/messages"\)|@Path\("\{datastoreMessageId\}"\)')],confidence=3)
R['decide']('kapua',78,'ACCEPT','Message lookup documents a list result, while its parent JSON resource returns one message; the schema reference is corrected to that object.')
print('New accepted items:',len(R['accepted']()))
