"""mitmproxy addon: log full request/response exchanges as JSON Lines for R1 triage.

Drop-in alternative to EMB's dockerfiles/addons/minlog.py (which records only
status, path and method). Mount it into the mitmproxy container and pass
`-s /addons/mitm_fulllog.py`. Output: $MITM_LOG_DIR/$MITM_FULLLOG_FILE (default
exchanges.jsonl). Bodies are truncated at MAX_BODY bytes; secrets in the
Authorization/Cookie headers are redacted.
"""
import base64
import json
import os
import time

from mitmproxy import http

LOG_DIR = os.getenv('MITM_LOG_DIR', '/logs')
LOG_FILE = os.path.join(LOG_DIR, os.getenv('MITM_FULLLOG_FILE', 'exchanges.jsonl'))
MAX_BODY = int(os.getenv('MITM_MAX_BODY', '65536'))
REDACT = {'authorization', 'cookie', 'set-cookie', 'x-api-key'}
os.makedirs(LOG_DIR, exist_ok=True)


def _body(message):
    raw = message.get_content(strict=False) or b''
    text = raw[:MAX_BODY].decode('utf-8', 'replace')
    try:
        raw[:MAX_BODY].decode('utf-8', 'strict')
        decode_error = False
    except UnicodeDecodeError:
        decode_error = True
    return {'text': text, 'truncated': len(raw) > MAX_BODY, 'size': len(raw),
            'base64': base64.b64encode(raw[:MAX_BODY]).decode('ascii'), 'decode_error': decode_error}


def _headers(headers):
    return {k.lower(): ('<redacted>' if k.lower() in REDACT else v) for k, v in headers.items()}


def response(flow: http.HTTPFlow):
    req, resp = flow.request, flow.response
    record = {
        'ts': time.time(),
        'request': {'method': req.method, 'path': req.path.split('?', 1)[0],
                    'origin': f'{req.scheme}://{req.host}:{req.port}',
                    'query': {k: req.query.get_all(k) for k in req.query.keys()},
                    'headers': _headers(req.headers), 'body': _body(req)},
        'response': {'status': resp.status_code, 'headers': _headers(resp.headers), 'body': _body(resp)},
    }
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
