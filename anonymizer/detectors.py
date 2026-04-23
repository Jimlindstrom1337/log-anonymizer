import re

# MAC addresses are detected only to prevent other patterns from matching them.
# They are never anonymized.
_MAC_PATTERN = re.compile(
    r"\b([0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}\b"
)

PATTERNS = {
    "personnummer": re.compile(
        r"\b(?:19|20)\d{6}(?:[-+]\d{4}|\d{4})\b"
    ),
    "email": re.compile(
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
    ),
    "phone": re.compile(
        r"\+46\d{8,10}(?=\b|@)"
        r"|(?<!\w)0[\d\s\-]{7,12}\b"
        r"|(?<=:)u\d{7,12}(?=[@:\s/])"
    ),
    "ip_address": re.compile(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    ),
    "ipv6": re.compile(
        r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"
    ),
    "unique_id": re.compile(
        r"(?<=LID:)[A-Za-z0-9_\-]+"
        r"|(?<=Call-ID: )[A-Za-z0-9_\-]+"
        r"|(?<=X-Tvx-Lid: )[A-Za-z0-9_\-]+"
    ),
}


def find_matches(text):
    """Return list of (start, end, entity_type, matched_text) sorted by position."""
    mac_ranges = [(m.start(), m.end()) for m in _MAC_PATTERN.finditer(text)]

    matches = []
    for entity_type, pattern in PATTERNS.items():
        for m in pattern.finditer(text):
            if _overlaps_mac(m.start(), m.end(), mac_ranges):
                continue
            if entity_type == "email" and re.search(r'@sip\b', m.group(), re.IGNORECASE):
                continue
            matches.append((m.start(), m.end(), entity_type, m.group()))
    matches.sort(key=lambda x: x[0])
    return _remove_overlaps(matches)


def _overlaps_mac(start, end, mac_ranges):
    return any(mac_start <= start < mac_end or mac_start < end <= mac_end
               for mac_start, mac_end in mac_ranges)


def _remove_overlaps(matches):
    result = []
    last_end = -1
    for match in matches:
        start, end, entity_type, text = match
        if start >= last_end:
            result.append(match)
            last_end = end
    return result
