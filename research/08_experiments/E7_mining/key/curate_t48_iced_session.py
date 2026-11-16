"""Private missing-session response status evidence."""
from pathlib import Path
import runpy
R=runpy.run_path(str(Path(__file__).resolve().parents[1]/'review_t48.py'))
R['accept']('Iced-Latte',153,'DELETE /api/v1/auth/sessions/{sessionId}',
 'an unknown session identifier returns 404 Session not found',
 'throw IllegalArgumentException for an unknown identifier, which the global catch-all maps to 500',
 'IMPL','spec_file','response_status.auth_session_missing',
 [('api-specs/security-openapi.yaml',r'/api/v1/auth/sessions/\{sessionId\}:|Session not found')],
 [('security/api/AuthSessionService.java',r'void revokeById|new IllegalArgumentException\("Session not found"\)'),
  ('common/exception/handler/GlobalExceptionHandler.java',r'ExceptionHandler\(Exception.class\)|INTERNAL_SERVER_ERROR|handleUnhandledException')],
 [('security/endpoint/UserSecurityEndpoint.java',r'DeleteMapping\("/sessions/\{sessionId\}"\)|void|revokeSession|authSessionService.revokeById')],confidence=3)
R['decide']('Iced-Latte',153,'ACCEPT','Session revocation documents 404 for an unknown session, while parent IllegalArgumentException reaches the 500 catch-all; the patch adds a specific 404 exception.')
print('New accepted items:',len(R['accepted']()))
