#!/usr/bin/python3
"""Deterministic value redaction; original values never enter diagnostics."""
import json
import re

REPLACEMENT = '[REDACTED]'
EMAIL = re.compile(r'(?<![\w.+-])[\w.+-]{1,80}@[\w.-]{1,253}\.[A-Za-z]{2,24}')
ATTRIBUTION = re.compile(r'(?i)@author\b|\bcopyright\b|SPDX-File(?:CopyrightText|Contributor)|\b(?:signed|co-authored|reviewed|acked|tested|reported|suggested|approved|contributed)-by\s*:|\b(?:author|committer)\s*:|\b(?:created|written|maintained) by\b|\bthanks to\b|licensed to')
HEADING = re.compile(r'(?i)^\s*(?://|/\*|\*|#)\s*(?:authors?|contributors?|acknowledgements?)\s*:')
SENSITIVE = r'[\w.-]*(?:secret|password|passwd|credential|token|private[_-]?key|api[_-]?key|trustKey|encoding)[\w.-]*'
ASSIGNMENT = re.compile(r'(?i)(\b' + SENSITIVE + r'\b\s*[=:]\s*)([\"\x27])([^\r\n]*?)\2')
UNQUOTED = re.compile(r'(?i)(\b' + SENSITIVE + r'\b\s*:\s*)([^\s\"\x27{},\[\]][^\r\n,}]*?)\s*$')
QUERY = re.compile(r'(?i)([?&](?:' + SENSITIVE + r')=)([^\s&\"\x27<>]+)')
AUTH = re.compile(r'(?i)\b(?:Basic|Bearer)[ \t]+[A-Za-z0-9+/_=-]{8,}')
URL_AUTH = re.compile(r'(https?://)[^\s/<>\"\x27]+@', re.I)
HOSTING = re.compile(r'https?://(?:www\.)?(?:github|gitlab|gitee|bitbucket)\.[^\s\"\x27<>]+', re.I)
QUOTED_ENCODED = re.compile(r'([\"\x27])([A-Za-z0-9+/_=-]{32,})\1')
ENCODED = re.compile(r'(?<![\w.])[A-Za-z0-9+_=/\-]{40,}(?![\w.])')
HEX_BYTES = re.compile(r'(?:0x[0-9a-fA-F]{2}[,\t ]*){8,}')
HEX = re.compile(r'\b[0-9a-f]{7,64}\b', re.I)
DATE = re.compile(r'\b(?:19|20)\d{2}[-/.]\d{1,2}[-/.]\d{1,2}(?:[T ][0-9:.+Z-]+)?\b|\b\d{1,2}[-/]\d{1,2}[-/](?:19|20)\d{2}\b')
TEXT_DATE = re.compile(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+(?:19|20)\d{2}\b', re.I)
KEY_HEADER = re.compile(r'-----BEGIN [A-Z ]*(?:PRIVATE KEY|CERTIFICATE)-----')

def message_needles(message):
    # No message, number, or original value is persisted by this module.
    # F2 (Claude, D1): only distinctive lines (>= 20 chars and >= 3 words) are needles; short generic lines
    # such as 'fix' or '*' would otherwise redact ordinary source tokens. Ids and SHAs are handled separately.
    lines = sorted({s.strip() for s in message.splitlines() if len(s.strip()) >= 20 and len(s.split()) >= 3}, key=lambda s:(-len(s), s))
    ids = sorted(set(re.findall(r'#\d+\b|\b[A-Z][A-Z0-9]+-\d+\b', message)))
    ids += ['#' + number for pair in re.findall(r'/(?:issues|pull|pulls)/(\d+)\b|\b(?:PR|issue)\s*#?(\d+)\b', message, re.I) for number in pair if number]
    return lines, sorted(set(ids))

def redact_text(text, messages=(), identifiers=(), shas=(), structured=False):
    original_lines = len(text.splitlines())
    text = EMAIL.sub(REPLACEMENT, text)
    text = URL_AUTH.sub(lambda m:m[1] + REPLACEMENT + '@', text)
    text = HOSTING.sub(REPLACEMENT, text)
    text = AUTH.sub(REPLACEMENT, text)
    text = QUERY.sub(lambda m:m[1] + REPLACEMENT, text)
    text = QUOTED_ENCODED.sub(lambda m:m[1] + REPLACEMENT + m[1], text)
    text = HEX_BYTES.sub(REPLACEMENT, text)
    text = ENCODED.sub(lambda m:REPLACEMENT if any(c.isdigit() for c in m[0]) or any(c in m[0] for c in '+/=') else m[0], text)
    for value in sorted(set(shas), key=lambda v:(-len(v), v)):
        if value and value.casefold() not in REPLACEMENT.casefold():
            text = re.sub(re.escape(value), REPLACEMENT, text, flags=re.I)
    for value in sorted(set(messages), key=lambda v:(-len(v), v)):
        if value and value.casefold() not in REPLACEMENT.casefold():
            pattern = (r'(?<!\w)' if value[0].isalnum() else '') + re.escape(value) + (r'(?!\w)' if value[-1].isalnum() else '')
            text = re.sub(pattern, REPLACEMENT, text, flags=re.I)
    for value in identifiers:
        if value.startswith('#'):
            number = re.escape(value[1:])
            text = re.sub(r'(?:#|/(?:issues|pull|pulls)/|\b(?:PR|issue)\s*#?)' + number + r'\b', REPLACEMENT, text, flags=re.I)
        else:
            text = re.sub(r'\b' + re.escape(value) + r'\b', REPLACEMENT, text)
    text = HEX.sub(REPLACEMENT, text)
    text = DATE.sub(REPLACEMENT, text)
    text = TEXT_DATE.sub(REPLACEMENT, text)
    lines = []
    credit = False
    key = False
    sensitive_indent = None
    contact_indent = None
    for line in text.splitlines(keepends=True):
        newline = '\n' if line.endswith('\n') else ''
        body = line[:-1] if newline else line
        prefix = body[:1] if body[:1] in {'+', '-', ' '} else ''
        content = body[len(prefix):]
        indent = len(content) - len(content.lstrip())
        if KEY_HEADER.search(content):
            key = True
        if HEADING.search(content) or re.search(r'@author\b', content):
            credit = True
        elif credit and ('*/' in content or not re.match(r'^\s*(?:\*|//|#)', content)):
            credit = False
        if re.match(r'^\s*[\"\x27]?contact[\"\x27]?\s*:', content):
            contact_indent = indent
        elif contact_indent is not None and content.strip() and indent <= contact_indent:
            contact_indent = None
        if re.match(r'^\s*[\"\x27]?' + SENSITIVE + r'[\"\x27]?\s*:\s*$', content, re.I):
            sensitive_indent = indent
        elif sensitive_indent is not None and content.strip() and indent <= sensitive_indent:
            sensitive_indent = None
        if key or credit or ATTRIBUTION.search(content):
            body = prefix + '// ' + REPLACEMENT
        else:
            body = ASSIGNMENT.sub(lambda m:m[1] + m[2] + REPLACEMENT + m[2], body)
            body = UNQUOTED.sub(lambda m:m[1] + REPLACEMENT if m[2] != REPLACEMENT else m[0], body)
            if not structured and re.search(r'(?i)secret|password|passwd|token|credential|private.?key|encoding',content):
                body = re.sub(r'([\"\x27])(?:\\.|(?!\1)[^\\\r\n])*?\1',
                              lambda m:m[0] if m.string[m.end():].lstrip().startswith(':') else m[1]+REPLACEMENT+m[1],body)
            if sensitive_indent is not None and indent > sensitive_indent or contact_indent is not None and indent > contact_indent:
                body = re.sub(r'(^[+ -]*\s*(?:[\"\x27]?(?:example|default|value|name|email|url)[\"\x27]?)\s*:)\s*[^\r\n]+', lambda m:m[1] + ' "' + REPLACEMENT + '"', body)
        if key and '-----END ' in content:
            key = False
        lines.append(body + newline)
    result = ''.join(lines)
    if len(result.splitlines()) != original_lines:
        raise ValueError('Redaction changed line count; contents suppressed')
    return result

def redact(raw, **context):
    text = raw.decode('utf-8', 'strict').replace('\r\n', '\n')
    # Parse JSON as inert data to handle contact and nested sensitive examples.
    try:
        value = json.loads(text)
    except (ValueError, RecursionError):
        value = None
    private = set()
    def walk(obj, sensitive=False, contact=False, mask=False):
        if isinstance(obj, dict):
            for k, v in obj.items():
                direct=bool(re.fullmatch(SENSITIVE,k,re.I))
                walk(v,sensitive or direct,contact or k=='contact',direct or sensitive and k in {'example','examples','default','value','enum'})
        elif isinstance(obj, list):
            for v in obj:
                walk(v, sensitive, contact, mask)
        elif isinstance(obj, str) and (mask or contact or ATTRIBUTION.search(obj)):
            private.add(obj)
    if isinstance(value, (dict, list)):
        walk(value)
        for literal in sorted(private, key=lambda s:(-len(s), s)):
            if literal and literal != REPLACEMENT:
                for spelling in {json.dumps(literal), json.dumps(literal, ensure_ascii=False)}:
                    text = text.replace(spelling, json.dumps(REPLACEMENT))
    return redact_text(text, structured=isinstance(value,(dict,list)), **context).encode()

def findings(raw, **context):
    text = raw.decode('utf-8', 'replace')
    found = []
    for name, pattern in [('email', EMAIL), ('attribution', ATTRIBUTION), ('auth', AUTH),
                          ('quoted_encoded', QUOTED_ENCODED), ('hex', HEX), ('date', DATE),
                          ('text_date', TEXT_DATE), ('private_key', KEY_HEADER), ('source_hosting', HOSTING)]:
        if pattern.search(text):
            found.append(name)
    if redact(raw, **context) != raw:
        found.append('non_idempotent_or_metadata')
    return sorted(set(found))

def display(text):
    # Delivered bytes use value redaction. Interactive previews are stricter.
    safe = redact(text.encode()).decode()
    return '\n'.join(REPLACEMENT if re.search(r'(?i)secret|password|passwd|token|credential|private.?key|encoding', line) else line for line in safe.splitlines())
