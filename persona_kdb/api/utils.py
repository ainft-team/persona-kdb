from datetime import datetime, timedelta

ISO_8601 = '%Y-%m-%dT%H:%M:%S.%fZ'
CHAR_MAP = {
    '!': '%21',
    '#': '%23',
    '$': '%24',
    '&': '%26',
    "'": '%27',
    '(': '%28',
    ')': '%29',
    '*': '%2A',
    '+': '%2B',
    ',': '%2C',
    '.' : '%2E',
    '/': '%2F',
    ':': '%3A',
    ';': '%3B',
    '=': '%3D',
    '?': '%3F',
    '@': '%40',
    '[': '%5B',
    ']': '%5D',
    '<': '%3C',
    '>': '%3E',
    '%': '%25',
    '{': '%7B',
    '}': '%7D',
    '|': '%7C',
    '\\': '%5C',
    '^': '%5E',
    '~': '%7E',
    '`': '%60',
    ' ': '%20'
}

def now(format=ISO_8601, offset_hours=0):
    time = datetime.utcnow() + timedelta(hours=offset_hours)
    if format is None:
        return time.timestamp()
    else:
        return time.strftime(format)

def encode_query(query: str):
    for char, encoded in CHAR_MAP.items():
        query = query.replace(char, encoded)
    return query

def decode_query(query: str) -> str:
    for char, encoded in CHAR_MAP.items():
        query = query.replace(encoded, char)
    return query