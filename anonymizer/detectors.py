import re

PATTERNS = {
    "personnummer": re.compile(
        r"\b(\d{6}[-+]\d{4}|\d{8}[-+]\d{4}|\d{10}|\d{12})\b"
    ),
    "email": re.compile(
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
    ),
    "phone": re.compile(
        r"\b(\+46[\s\-]?|0)[\d\s\-]{7,12}\b"
    ),
    "ip_address": re.compile(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    ),
    "ipv6": re.compile(
        r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"
    ),
}


def find_matches(text):
    """Return list of (start, end, entity_type, matched_text) sorted by position."""
    matches = []
    for entity_type, pattern in PATTERNS.items():
        for m in pattern.finditer(text):
            matches.append((m.start(), m.end(), entity_type, m.group()))
    matches.sort(key=lambda x: x[0])
    return _remove_overlaps(matches)


def _remove_overlaps(matches):
    result = []
    last_end = -1
    for match in matches:
        start, end, entity_type, text = match
        if start >= last_end:
            result.append(match)
            last_end = end
    return result
