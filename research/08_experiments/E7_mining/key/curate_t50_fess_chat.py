import runpy
from pathlib import Path
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t50.py'))
for operation,handler,opid in [('POST /api/v2/chat','ChatHandler.java','chatV2'),('POST /api/v2/chat/stream','ChatStreamHandler.java','chatStreamV2')]:
 R['accept']('fess',2,operation,
  'message is a required string with no stated maximum length',
  'messages above the configured character limit return 400, with a default limit of 4000',
  'SPEC','openapi','validation.chat_message_length',
  contract=[('src/main/config/openapi/v2/openapi-user.yaml',r'operationId: '+opid),('src/main/config/openapi/v2/openapi-user.yaml',r'message: \{ type: string \}')],
  implementation=[('api/v2/handlers/'+handler,r'getMaxMessageLength|MessageTooLongException'),('api/v2/handlers/ChatRequestBody.java',r'message.length\(\) > maxMessageLength'),('helper/ChatApiHelper.java',r'getSystemProperty\("rag.chat.message.max.length"')],
  helpers=['src/main/java/org/codelibs/fess/api/v2/V2EnvelopeWriter.java','src/main/java/org/codelibs/fess/api/v2/V2ErrorCode.java'])
R['private_json'](R['KEY']/'t50_fess_chat_scope.json',dict(other_edits='Removed response possibilities and SSE examples are not separately accepted: complete path absence and all event providers were not established.'))
print('Accepted items and exclusions:',R['finish_accept']('Both chat handlers enforce a configured message limit absent from the parent request schema; the patch documents that limit.'))
